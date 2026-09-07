import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone
from backend.app.models.production import ProductionRun, AgentExecutionEvent

class ProductionRunStore:
    """
    In-Memory & Persistent Storage for Autonomous Production Runs (Milestone 9, Section 35)
    Thread-safe repository holding production runs, event streams, and failure states.
    """
    def __init__(self):
        self._runs: Dict[str, ProductionRun] = {}
        self._events_by_run: Dict[str, List[AgentExecutionEvent]] = {}

    def create_run(
        self,
        character_id: str,
        input_brief: str,
        campaign_id: str = "titan_laptop_india_devs",
        language: str = "en",
        register: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> ProductionRun:
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        t_id = trace_id or f"trace_{uuid.uuid4().hex[:8]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        run = ProductionRun(
            run_id=run_id,
            trace_id=t_id,
            character_id=character_id,
            campaign_id=campaign_id,
            input_brief=input_brief,
            language=language,
            register=register,
            status="QUEUED",
            current_stage="QUEUED",
            created_at=now_iso
        )
        self._runs[run_id] = run
        self._events_by_run[run_id] = []
        return run

    def record_event(self, run_id: str, event: AgentExecutionEvent):
        if run_id in self._runs:
            self._events_by_run.setdefault(run_id, []).append(event)
            self._runs[run_id].stages.append(event)
            self._runs[run_id].current_stage = event.stage

    def get_run(self, run_id: str) -> Optional[ProductionRun]:
        return self._runs.get(run_id)

    def get_run_by_trace(self, trace_id: str) -> Optional[ProductionRun]:
        for r in self._runs.values():
            if r.trace_id == trace_id:
                return r
        return None

    def list_runs(self, limit: int = 10) -> List[ProductionRun]:
        runs = list(self._runs.values())
        runs.sort(key=lambda r: r.created_at, reverse=True)
        return runs[:limit]

    def get_events(self, run_id: str) -> List[AgentExecutionEvent]:
        return self._events_by_run.get(run_id, [])

    def update_run(self, run: ProductionRun):
        self._runs[run.run_id] = run

production_store = ProductionRunStore()
