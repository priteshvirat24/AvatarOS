from backend.app.data.telemetry_store import telemetry_store
from backend.app.agents.evolution import evolution_agent

def test_clickhouse_query_881a():
    res = telemetry_store.run_query_881a()
    assert res["query_id"] == "ch_query_881a"
    assert len(res["rows"]) >= 4
    # Highest retention must be question hook
    assert res["rows"][0]["hook_type"] == "question"
    assert res["rows"][0]["n"] >= 50
    assert res["rows"][0]["meets_sample_floor"] is True

def test_closed_loop_evolution_and_plan_diff():
    evolution_result = evolution_agent.analyze_and_evolve()
    assert evolution_result["status"] == "STRATEGY_EVOLVED"
    assert evolution_result["new_strategy_version"] == 14
    assert evolution_result["proposed_strategy"]["hook_type"] == "question"

    p1 = {"hook_type": "statement", "opening_duration_s": 9.2, "shots": [{"shot": "medium_shot"}]}
    p2 = {"hook_type": "question", "opening_duration_s": 6.8, "shots": [{"shot": "close_up"}]}
    diff = evolution_agent.compute_plan_diff(p1, p2)
    assert diff["hook_type"]["changed"] is True
    assert diff["hook_type"]["run1"] == "statement"
    assert diff["hook_type"]["run2"] == "question"
