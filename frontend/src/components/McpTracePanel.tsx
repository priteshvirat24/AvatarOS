import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Activity, AlertTriangle, CheckCircle2, Database, Loader2, Lock,
  RefreshCw, ShieldAlert, Terminal, Unlock
} from 'lucide-react';

/**
 * MCP Trace Panel.
 *
 * Two data sources, deliberately kept distinct so nothing here overstates itself:
 *
 *  - The live stream (`/ws/mcp-trace`) is an in-process mirror. It is instant, and
 *    it is labelled as not durable.
 *  - "Verify from ClickHouse" re-reads the same calls out of the cluster through
 *    the official mcp-clickhouse server, and shows the SQL that did it. That read
 *    is itself an MCP call, so it appears in the next verification - which is the
 *    whole point of the panel.
 */

interface McpCall {
  call_id: string;
  ts: string;
  trace_id?: string;
  agent_identity: string;
  tool_name: string;
  status: string;
  authorized: boolean | number;
  rows_returned: number;
  latency_ms: number;
  server_identity: string;
  transport: string;
  compiled_sql?: string;
  error?: string;
  persisted_to_clickhouse?: boolean;
}

interface McpStatus {
  provider: string;
  ready: boolean;
  transport: string;
  is_simulated: boolean;
  server_identity: string;
  server_tools?: string[];
  query_tool?: string;
  database?: string;
  last_error?: string | null;
  tools_count?: number;
}

interface VerificationCall {
  call_id: string;
  server_identity: string;
  transport: string;
  latency_ms: number;
  rows_returned: number;
  compiled_sql: string;
}

const isAuthorized = (value: boolean | number) => value === true || value === 1;

/** Merges incoming calls into the held list, newest first, de-duplicated by call_id. */
const mergeCalls = (existing: McpCall[], incoming: McpCall[]): McpCall[] => {
  const seen = new Set<string>();
  const merged: McpCall[] = [];
  for (const call of [...incoming, ...existing]) {
    if (!call?.call_id || seen.has(call.call_id)) continue;
    seen.add(call.call_id);
    merged.push(call);
  }
  return merged.slice(0, 200);
};

const statusStyle = (status: string): { cls: string; icon: React.ReactNode } => {
  switch (status) {
    case 'SUCCESS':
      return { cls: 'badge-emerald', icon: <CheckCircle2 size={11} /> };
    case 'UNAUTHORIZED':
      return { cls: 'badge-rose', icon: <ShieldAlert size={11} /> };
    default:
      return { cls: 'badge-amber', icon: <AlertTriangle size={11} /> };
  }
};

const formatTime = (ts: string) => {
  if (!ts) return '--:--:--';
  const parsed = new Date(ts.includes('T') ? ts : ts.replace(' ', 'T') + 'Z');
  if (Number.isNaN(parsed.getTime())) return ts.slice(11, 23) || ts;
  return parsed.toISOString().slice(11, 23);
};

export const McpTracePanel: React.FC = () => {
  const [calls, setCalls] = useState<McpCall[]>([]);
  const [status, setStatus] = useState<McpStatus | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [connection, setConnection] = useState<'connecting' | 'live' | 'closed'>('connecting');

  const [verifying, setVerifying] = useState(false);
  const [verification, setVerification] = useState<VerificationCall | null>(null);
  const [verifiedCalls, setVerifiedCalls] = useState<McpCall[] | null>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    // Close any previous socket first. Without this, a reconnect (or React's
    // double-invoked effects in development) leaves two live subscriptions and
    // every call arrives twice.
    socketRef.current?.close();

    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${proto}://${window.location.host}/ws/mcp-trace`);
    socketRef.current = socket;
    setConnection('connecting');

    socket.onopen = () => setConnection('live');

    socket.onmessage = (event) => {
      if (socketRef.current !== socket) return; // superseded by a newer socket
      try {
        const msg = JSON.parse(event.data);
        if (msg.event === 'snapshot') {
          setStatus(msg.status);
          setCalls(mergeCalls([], msg.calls || []));
        } else if (msg.event === 'mcp_call') {
          // A reconnect replays a snapshot that overlaps what is already held,
          // so merge by call_id rather than blindly prepending.
          setCalls((prev) => mergeCalls(prev, [msg.call]));
        }
      } catch {
        // A malformed frame must not tear down the panel.
      }
    };

    socket.onclose = () => {
      setConnection('closed');
      // Reconnect with a fixed backoff so a restarted backend recovers on its own.
      retryRef.current = window.setTimeout(connect, 3000);
    };

    socket.onerror = () => socket.close();
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (retryRef.current) window.clearTimeout(retryRef.current);
      socketRef.current?.close();
    };
  }, [connect]);

  const runVerification = async () => {
    setVerifying(true);
    setVerifyError(null);
    try {
      const res = await fetch('/api/mcp/trace/verify?limit=25');
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Verification failed (HTTP ${res.status})`);
      }
      const data = await res.json();
      setVerification(data.verification_call);
      setVerifiedCalls(data.calls || []);
    } catch (err) {
      setVerifyError(err instanceof Error ? err.message : 'Verification failed');
      setVerifiedCalls(null);
      setVerification(null);
    } finally {
      setVerifying(false);
    }
  };

  const showing = verifiedCalls ?? calls;
  const durable = verifiedCalls !== null;
  const simulated = status?.is_simulated ?? true;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', height: '100%' }}>

      {/* ---------------- Partner runtime status ---------------- */}
      <div className="glass-panel" style={{ padding: '14px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Database size={17} color="var(--accent-cyan)" />
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: 800, letterSpacing: '0.3px' }}>
                  CLICKHOUSE MCP PARTNER RUNTIME
                </span>
                <span
                  className={`badge-neon ${simulated ? 'badge-amber' : 'badge-emerald'}`}
                  style={{ fontSize: '9px' }}
                >
                  {simulated ? '● DETERMINISTIC FALLBACK (NO SERVER)' : '● OFFICIAL mcp-clickhouse SERVER'}
                </span>
              </div>
              <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                {status
                  ? `${status.server_identity} · transport: ${status.transport} · db: ${status.database ?? 'n/a'} · query tool: ${status.query_tool ?? 'n/a'}`
                  : 'Resolving partner server…'}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span
              className={`badge-neon ${connection === 'live' ? 'badge-primary' : 'badge-amber'}`}
              style={{ fontSize: '9px' }}
            >
              <Activity size={10} /> {connection === 'live' ? 'STREAMING' : connection.toUpperCase()}
            </span>
            <button
              className="btn btn-secondary"
              onClick={runVerification}
              disabled={verifying}
              style={{ padding: '5px 10px', fontSize: '10px' }}
            >
              {verifying ? <Loader2 size={12} className="spin" /> : <RefreshCw size={12} />}
              {verifying ? 'Querying ClickHouse…' : 'Verify from ClickHouse'}
            </button>
          </div>
        </div>

        {status?.last_error && (
          <div
            style={{
              marginTop: '10px', padding: '8px 10px', borderRadius: 'var(--radius-sm)',
              backgroundColor: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)',
              fontSize: '10px', color: 'var(--accent-rose)'
            }}
          >
            Partner server error: {status.last_error}
          </div>
        )}
      </div>

      {/* ---------------- Verification receipt ---------------- */}
      {verifyError && (
        <div
          className="glass-panel"
          style={{ padding: '12px 14px', borderColor: 'rgba(244, 63, 94, 0.35)' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--accent-rose)' }}>
            <AlertTriangle size={13} /> {verifyError}
          </div>
        </div>
      )}

      {verification && (
        <div className="glass-panel" style={{ padding: '12px 14px', borderColor: 'rgba(16, 185, 129, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <CheckCircle2 size={14} color="var(--accent-emerald)" />
            <span style={{ fontSize: '11px', fontWeight: 700 }}>
              Ledger re-read from ClickHouse through the official MCP server
            </span>
            <span className="badge-neon badge-emerald" style={{ fontSize: '9px' }}>
              {verification.rows_returned} ROWS · {verification.latency_ms}ms
            </span>
          </div>
          <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '8px' }}>
            Executed by <strong style={{ color: 'var(--accent-cyan)' }}>{verification.server_identity}</strong> over{' '}
            <strong>{verification.transport}</strong>. This verification is itself an MCP call, so it appears in the
            next read of the ledger below.
          </p>
          <pre
            className="code-font"
            style={{
              fontSize: '9.5px', color: 'var(--text-secondary)', backgroundColor: 'var(--bg-darkest)',
              padding: '10px', borderRadius: 'var(--radius-sm)', overflowX: 'auto', margin: 0,
              maxHeight: '150px'
            }}
          >
            {verification.compiled_sql}
          </pre>
        </div>
      )}

      {/* ---------------- Call list ---------------- */}
      <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <div
          style={{
            padding: '10px 14px', borderBottom: '1px solid var(--border-subtle)',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Terminal size={14} color="var(--primary-light)" />
            <span style={{ fontSize: '12px', fontWeight: 700 }}>MCP TOOL CALL LEDGER</span>
            <span className={`badge-neon ${durable ? 'badge-emerald' : 'badge-amber'}`} style={{ fontSize: '9px' }}>
              {durable ? 'DURABLE · FROM CLICKHOUSE' : 'LIVE MIRROR · IN-PROCESS'}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>{showing.length} calls</span>
            {durable && (
              <button
                className="btn btn-secondary"
                onClick={() => { setVerifiedCalls(null); setVerification(null); }}
                style={{ padding: '3px 8px', fontSize: '9px' }}
              >
                Back to live
              </button>
            )}
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
          {showing.length === 0 ? (
            <div
              style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                height: '100%', padding: '40px 20px', textAlign: 'center', gap: '10px'
              }}
            >
              <Database size={26} color="var(--text-dim)" />
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                No MCP calls recorded yet
              </p>
              <p style={{ fontSize: '10.5px', color: 'var(--text-muted)', maxWidth: '380px', lineHeight: 1.6 }}>
                Run a production, evolve a strategy, or open the governance view. Every partner tool call an agent
                makes will appear here with the SQL it compiled to.
              </p>
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '10.5px' }}>
              <thead>
                <tr style={{ position: 'sticky', top: 0, backgroundColor: 'var(--bg-surface)', zIndex: 1 }}>
                  {['Time', 'Agent identity', 'Tool', 'Auth', 'Status', 'Rows', 'Latency'].map((h) => (
                    <th
                      key={h}
                      style={{
                        textAlign: h === 'Rows' || h === 'Latency' ? 'right' : 'left',
                        padding: '7px 12px', fontSize: '9px', fontWeight: 700, letterSpacing: '0.6px',
                        color: 'var(--text-muted)', textTransform: 'uppercase',
                        borderBottom: '1px solid var(--border-subtle)'
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {showing.map((call) => {
                  const authorized = isAuthorized(call.authorized);
                  const badge = statusStyle(call.status);
                  const isOpen = expandedId === call.call_id;
                  return (
                    <React.Fragment key={call.call_id}>
                      <tr
                        onClick={() => setExpandedId(isOpen ? null : call.call_id)}
                        style={{
                          cursor: 'pointer',
                          borderBottom: '1px solid var(--border-subtle)',
                          backgroundColor: isOpen ? 'var(--bg-surface-elevated)' : 'transparent'
                        }}
                      >
                        <td className="code-font" style={{ padding: '7px 12px', color: 'var(--text-muted)' }}>
                          {formatTime(call.ts)}
                        </td>
                        <td style={{ padding: '7px 12px', fontWeight: 600 }}>{call.agent_identity}</td>
                        <td className="code-font" style={{ padding: '7px 12px', color: 'var(--accent-cyan)' }}>
                          {call.tool_name}
                        </td>
                        <td style={{ padding: '7px 12px' }}>
                          {authorized
                            ? <Unlock size={11} color="var(--accent-emerald)" />
                            : <Lock size={11} color="var(--accent-rose)" />}
                        </td>
                        <td style={{ padding: '7px 12px' }}>
                          <span className={`badge-neon ${badge.cls}`} style={{ fontSize: '8.5px' }}>
                            {badge.icon} {call.status}
                          </span>
                        </td>
                        <td className="code-font" style={{ padding: '7px 12px', textAlign: 'right' }}>
                          {call.rows_returned}
                        </td>
                        <td className="code-font" style={{ padding: '7px 12px', textAlign: 'right', color: 'var(--text-secondary)' }}>
                          {Number(call.latency_ms).toFixed(1)}ms
                        </td>
                      </tr>

                      {isOpen && (
                        <tr>
                          <td colSpan={7} style={{ padding: '0 12px 12px', backgroundColor: 'var(--bg-surface-elevated)' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', paddingTop: '4px' }}>
                              <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', fontSize: '9.5px', color: 'var(--text-muted)' }}>
                                <span>call_id: <span className="code-font" style={{ color: 'var(--text-secondary)' }}>{call.call_id}</span></span>
                                {call.trace_id && <span>trace_id: <span className="code-font" style={{ color: 'var(--text-secondary)' }}>{call.trace_id}</span></span>}
                                <span>server: <span className="code-font" style={{ color: 'var(--accent-cyan)' }}>{call.server_identity}</span></span>
                                <span>transport: <span className="code-font">{call.transport}</span></span>
                              </div>

                              {call.error ? (
                                <div
                                  style={{
                                    padding: '8px 10px', borderRadius: 'var(--radius-sm)', fontSize: '10px',
                                    backgroundColor: 'rgba(244, 63, 94, 0.1)',
                                    border: '1px solid rgba(244, 63, 94, 0.3)', color: 'var(--accent-rose)'
                                  }}
                                >
                                  <strong>{authorized ? 'Execution error' : 'Authorization refused'}:</strong> {call.error}
                                </div>
                              ) : null}

                              {call.compiled_sql ? (
                                <div>
                                  <p style={{ fontSize: '9px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.6px' }}>
                                    SQL executed by the partner server
                                  </p>
                                  <pre
                                    className="code-font"
                                    style={{
                                      fontSize: '9.5px', color: 'var(--text-secondary)',
                                      backgroundColor: 'var(--bg-darkest)', padding: '10px',
                                      borderRadius: 'var(--radius-sm)', overflowX: 'auto', margin: 0
                                    }}
                                  >
                                    {call.compiled_sql}
                                  </pre>
                                </div>
                              ) : (
                                <p style={{ fontSize: '10px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                                  No SQL was compiled — the call was refused before reaching the template layer.
                                </p>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};
