"""
Real Model Context Protocol client session for the official `mcp-clickhouse` server.

This module speaks the actual MCP wire protocol (JSON-RPC over stdio or streamable
HTTP) to the official ClickHouse MCP server published by ClickHouse
(https://github.com/ClickHouse/mcp-clickhouse, PyPI: `mcp-clickhouse`).

There is deliberately no in-process shortcut here: every analytical read performed
by an AVATAROS agent leaves this process, crosses an MCP transport, is executed by
the partner server against a real ClickHouse cluster, and comes back as MCP tool
output. That is what the ClickHouse track requires, and it is what the in-app MCP
Trace panel renders.

The AVATAROS backend is synchronous (FastAPI sync handlers), while the MCP SDK is
async, so a single long-lived asyncio loop is run on a daemon thread. The MCP
session context is held open by a runner task on that loop; callers on other
threads submit work with `run_coroutine_threadsafe`.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.app.config import settings
from backend.app.logging import app_logger


@dataclass
class MCPCallOutcome:
    """Raw outcome of a single MCP `tools/call`, before domain interpretation."""
    ok: bool
    tool_name: str
    latency_ms: float
    columns: List[str] = field(default_factory=list)
    rows: List[List[Any]] = field(default_factory=list)
    raw_text: str = ""
    error: Optional[str] = None

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def dicts(self) -> List[Dict[str, Any]]:
        return [dict(zip(self.columns, r)) for r in self.rows]


def _resolve_server_command() -> str:
    """
    Locates the official `mcp-clickhouse` console script.

    Prefers an explicit setting, then the console script that sits next to the
    running interpreter (the common venv layout), then whatever is on PATH.
    """
    if settings.MCP_SERVER_COMMAND:
        return settings.MCP_SERVER_COMMAND

    # The official server lives in its own virtualenv (see
    # backend/requirements-mcp-server.txt) so its fastmcp/starlette pins cannot
    # collide with the application's FastAPI pins.
    repo_root = os.path.dirname(  # <repo>/
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    for candidate in (
        os.path.join(repo_root, "backend", ".mcp-server-venv", "bin", "mcp-clickhouse"),
        os.path.join(os.path.dirname(sys.executable), "mcp-clickhouse"),
    ):
        if os.path.exists(candidate):
            return candidate

    discovered = shutil.which("mcp-clickhouse")
    return discovered or "mcp-clickhouse"


def build_server_env() -> Dict[str, str]:
    """
    Builds the environment handed to the official server subprocess.

    The connection settings are AVATAROS's own ClickHouse settings translated into
    the variable names `mcp-clickhouse` documents. Write access is never granted:
    the server stays read-only, so an agent cannot mutate telemetry even if it were
    somehow able to smuggle a statement past the template layer.
    """
    url = settings.CLICKHOUSE_URL
    secure = url.startswith("https://")
    hostport = url.replace("https://", "").replace("http://", "")
    host = hostport.split(":")[0].split("/")[0]
    if ":" in hostport.split("/")[0]:
        port = hostport.split("/")[0].split(":")[1]
    else:
        port = "8443" if secure else "8123"

    password = (
        settings.CLICKHOUSE_PASSWORD.get_secret_value()
        if settings.CLICKHOUSE_PASSWORD
        else ""
    )

    env = dict(os.environ)
    env.update({
        "CLICKHOUSE_HOST": host,
        "CLICKHOUSE_PORT": str(port),
        "CLICKHOUSE_USER": settings.CLICKHOUSE_USERNAME,
        "CLICKHOUSE_PASSWORD": password,
        "CLICKHOUSE_DATABASE": settings.CLICKHOUSE_DATABASE,
        "CLICKHOUSE_SECURE": "true" if secure else "false",
        "CLICKHOUSE_VERIFY": "true" if secure else "false",
        "CLICKHOUSE_CONNECT_TIMEOUT": str(int(settings.CLICKHOUSE_CONNECT_TIMEOUT)),
        "CLICKHOUSE_SEND_RECEIVE_TIMEOUT": str(int(settings.CLICKHOUSE_SEND_RECEIVE_TIMEOUT)),
        # Read-only: the partner server is never permitted to mutate state.
        "CLICKHOUSE_ALLOW_WRITE_ACCESS": "false",
        "CLICKHOUSE_ALLOW_DROP": "false",
        "CLICKHOUSE_MCP_SERVER_TRANSPORT": "stdio",
        # Keep the subprocess quiet: the FastMCP banner and INFO chatter go to
        # stderr on every start and would otherwise drown application logs.
        "FASTMCP_SHOW_SERVER_BANNER": "false",
        "FASTMCP_LOG_LEVEL": "WARNING",
    })
    return env


class MCPServerSession:
    """
    Long-lived MCP client session against one MCP server.

    Thread-safe: `call_tool` may be invoked from FastAPI worker threads. The
    session itself lives on a private asyncio loop running in a daemon thread.
    """

    def __init__(self) -> None:
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._session: Any = None
        self._ready = threading.Event()
        self._stop_event: Optional[asyncio.Event] = None
        self._start_lock = threading.Lock()
        self._tools: List[Dict[str, Any]] = []
        self._server_name: str = "unknown"
        self._server_version: str = "unknown"
        self._last_error: Optional[str] = None
        self._started = False

    # ------------------------------------------------------------------ status

    @property
    def ready(self) -> bool:
        return self._ready.is_set() and self._session is not None

    @property
    def server_identity(self) -> str:
        return f"{self._server_name}@{self._server_version}"

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    def tool_names(self) -> List[str]:
        return [t["name"] for t in self._tools]

    def status(self) -> Dict[str, Any]:
        return {
            "ready": self.ready,
            "server_name": self._server_name,
            "server_version": self._server_version,
            "transport": settings.MCP_TRANSPORT,
            "endpoint": (
                settings.MCP_SERVER_URL
                if settings.MCP_TRANSPORT in ("http", "sse")
                else _resolve_server_command()
            ),
            "server_tools": self.tool_names(),
            "read_only": True,
            "last_error": self._last_error,
        }

    # ----------------------------------------------------------------- startup

    def start(self, timeout: float = 30.0) -> bool:
        """Starts the session and blocks until the server has initialized."""
        with self._start_lock:
            if self._started and self.ready:
                return True
            if self._thread is not None and self._thread.is_alive():
                return self._ready.wait(timeout=timeout)

            self._ready.clear()
            self._last_error = None
            self._started = True
            self._thread = threading.Thread(
                target=self._thread_main, name="avataros-mcp-session", daemon=True
            )
            self._thread.start()

        got_ready = self._ready.wait(timeout=timeout)
        if not got_ready and self._last_error is None:
            self._last_error = f"MCP server did not initialize within {timeout}s"
        return self.ready

    def _thread_main(self) -> None:
        try:
            asyncio.run(self._runner())
        except Exception as exc:  # pragma: no cover - defensive
            self._last_error = f"{type(exc).__name__}: {exc}"
            app_logger.log_operation(
                trace_id="system",
                operation="mcp_session_thread_crash",
                status="ERROR",
                agent_task="mcp_session",
                details={"error": self._last_error},
            )
        finally:
            self._session = None
            self._ready.set()  # unblock any waiter; `ready` is still False

    async def _runner(self) -> None:
        from mcp import ClientSession

        self._loop = asyncio.get_running_loop()
        self._stop_event = asyncio.Event()

        transport = settings.MCP_TRANSPORT
        try:
            if transport in ("http", "sse"):
                url = settings.MCP_SERVER_URL
                if not url:
                    raise ValueError("MCP_SERVER_URL is required for http/sse transport")
                if transport == "http":
                    from mcp.client.streamable_http import streamable_http_client

                    async with streamable_http_client(url) as streams:
                        read_stream, write_stream = streams[0], streams[1]
                        await self._serve(ClientSession, read_stream, write_stream)
                else:
                    from mcp.client.sse import sse_client

                    async with sse_client(url) as (read_stream, write_stream):
                        await self._serve(ClientSession, read_stream, write_stream)
            else:
                from mcp import StdioServerParameters
                from mcp.client.stdio import stdio_client

                params = StdioServerParameters(
                    command=_resolve_server_command(),
                    args=[],
                    env=build_server_env(),
                )
                async with stdio_client(params) as (read_stream, write_stream):
                    await self._serve(ClientSession, read_stream, write_stream)
        except Exception as exc:
            self._last_error = f"{type(exc).__name__}: {exc}"
            app_logger.log_operation(
                trace_id="system",
                operation="mcp_session_connect",
                status="ERROR",
                agent_task="mcp_session",
                details={"transport": transport, "error": self._last_error},
            )
            self._session = None
            self._ready.set()

    async def _serve(self, client_session_cls, read_stream, write_stream) -> None:
        async with client_session_cls(read_stream, write_stream) as session:
            init_result = await session.initialize()
            # The MCP SDK renamed wire-model fields between 1.x (camelCase) and
            # 2.x (snake_case); accept either so the client is not pinned to one.
            info = getattr(init_result, "server_info", None) or getattr(
                init_result, "serverInfo", None
            )
            if info is not None:
                self._server_name = getattr(info, "name", "unknown")
                self._server_version = getattr(info, "version", "unknown")

            listed = await session.list_tools()
            self._tools = [
                {
                    "name": t.name,
                    "description": (t.description or "").strip(),
                }
                for t in listed.tools
            ]

            self._session = session
            self._ready.set()

            app_logger.log_operation(
                trace_id="system",
                operation="mcp_session_connect",
                status="CONNECTED",
                agent_task="mcp_session",
                details={
                    "server": self.server_identity,
                    "transport": settings.MCP_TRANSPORT,
                    "server_tools": self.tool_names(),
                },
            )

            assert self._stop_event is not None
            await self._stop_event.wait()

    # ------------------------------------------------------------------- calls

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> MCPCallOutcome:
        """
        Performs a real MCP `tools/call` and normalizes the ClickHouse result.

        Never raises for a server-side failure: the outcome carries `ok=False` and
        the error text, so callers can surface an honest error rather than a
        placeholder value.
        """
        timeout = timeout or settings.MCP_TIMEOUT
        start = time.perf_counter()

        if not self.ready:
            started = self.start(timeout=min(timeout + 10.0, 30.0))
            if not started:
                return MCPCallOutcome(
                    ok=False,
                    tool_name=tool_name,
                    latency_ms=round((time.perf_counter() - start) * 1000, 2),
                    error=self._last_error or "MCP server session is not available",
                )

        try:
            assert self._loop is not None and self._session is not None
            future = asyncio.run_coroutine_threadsafe(
                self._session.call_tool(tool_name, arguments), self._loop
            )
            result = future.result(timeout=timeout)
        except Exception as exc:
            return MCPCallOutcome(
                ok=False,
                tool_name=tool_name,
                latency_ms=round((time.perf_counter() - start) * 1000, 2),
                error=f"{type(exc).__name__}: {exc}",
            )

        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        raw_text = ""
        for chunk in getattr(result, "content", []) or []:
            text = getattr(chunk, "text", None)
            if text:
                raw_text += text

        if getattr(result, "is_error", None) or getattr(result, "isError", None):
            return MCPCallOutcome(
                ok=False,
                tool_name=tool_name,
                latency_ms=latency_ms,
                raw_text=raw_text,
                error=raw_text or "MCP server reported a tool error",
            )

        columns, rows = _parse_clickhouse_payload(raw_text)
        return MCPCallOutcome(
            ok=True,
            tool_name=tool_name,
            latency_ms=latency_ms,
            columns=columns,
            rows=rows,
            raw_text=raw_text,
        )

    def run_query(self, sql: str, timeout: Optional[float] = None) -> MCPCallOutcome:
        """Executes SQL through the partner server's query tool."""
        return self.call_tool(settings.MCP_QUERY_TOOL, {"query": sql}, timeout=timeout)

    def stop(self) -> None:
        if self._loop is not None and self._stop_event is not None:
            try:
                self._loop.call_soon_threadsafe(self._stop_event.set)
            except Exception:
                pass
        self._started = False
        self._session = None
        self._ready.clear()


def _parse_clickhouse_payload(raw_text: str) -> tuple[List[str], List[List[Any]]]:
    """
    Normalizes the official server's result payload.

    `mcp-clickhouse` returns a JSON document shaped `{"columns": [...], "rows": [[...]]}`
    as tool text content. Anything else is returned as a single-column result so the
    caller still sees the real server output rather than an invented shape.
    """
    if not raw_text:
        return [], []
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return ["result"], [[raw_text]]

    if isinstance(payload, dict) and "columns" in payload and "rows" in payload:
        return list(payload["columns"]), [list(r) for r in payload["rows"]]
    if isinstance(payload, list):
        if payload and isinstance(payload[0], dict):
            columns = list(payload[0].keys())
            return columns, [[row.get(c) for c in columns] for row in payload]
        return ["result"], [[item] for item in payload]
    return ["result"], [[raw_text]]


# Process-wide session against the official ClickHouse MCP server.
mcp_server_session = MCPServerSession()
