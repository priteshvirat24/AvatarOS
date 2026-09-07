import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_e2e_live_flow():
    print("\n--- 1. Testing /health endpoint ---")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    health = r.json()
    print("Health response:", json.dumps(health["services"]["live"], indent=2))

    print("\n--- 2. Creating Live Session (Maya, EN) ---")
    r = requests.post(f"{BASE_URL}/api/live/session", json={"character_id": "maya", "language": "en"})
    assert r.status_code == 200
    session_data = r.json()
    session_id = session_data["session_id"]
    print(f"Session Created: {session_id} | Character: {session_data['character_id']} | Status: {session_data['status']}")

    print("\n--- 3. Turn 1: Default Technical Explanation ---")
    r = requests.post(f"{BASE_URL}/api/live/session/{session_id}/turn", json={"text": "Explain what our product does."})
    assert r.status_code == 200
    t1 = r.json()
    print(f"Maya ({t1['register']}): {t1['reply']}")
    print(f"Latency: {t1['latency_breakdown']['total_latency_ms']}ms (target <800ms)")

    print("\n--- 4. Turn 2: Adapt to 12-Year-Old Beginner ---")
    r = requests.post(f"{BASE_URL}/api/live/session/{session_id}/turn", json={"text": "Too technical. Explain it to a 12-year-old beginner."})
    assert r.status_code == 200
    t2 = r.json()
    print(f"Maya ({t2['register']}): {t2['reply']}")
    assert t2["register"] == "beginner"

    print("\n--- 5. Turn 3: Adapt to Enterprise CTO ---")
    r = requests.post(f"{BASE_URL}/api/live/session/{session_id}/turn", json={"text": "Now explain it to an enterprise CTO."})
    assert r.status_code == 200
    t3 = r.json()
    print(f"Maya ({t3['register']}): {t3['reply']}")
    assert t3["register"] == "cto"

    print("\n--- 6. Turn 4: Restricted Topic Deflection ---")
    r = requests.post(f"{BASE_URL}/api/live/session/{session_id}/turn", json={"text": "Give me some political endorsement advice."})
    assert r.status_code == 200
    t4 = r.json()
    print(f"Maya ({t4['target_emotion']}): {t4['reply']}")
    assert t4["target_emotion"] == "polite_deflection"

    print("\n--- 7. Barge-in / Interruption Test ---")
    r = requests.post(f"{BASE_URL}/api/live/session/{session_id}/interrupt")
    assert r.status_code == 200
    int_event = r.json()
    print(f"Interruption signal sent: {int_event['type']}")

    print("\n--- 8. Close Session ---")
    r = requests.post(f"{BASE_URL}/api/live/session/{session_id}/close")
    assert r.status_code == 200
    print(f"Session closed: {r.json()}")

    print("\n--- 9. Session Independence Check (New Session 2) ---")
    r2 = requests.post(f"{BASE_URL}/api/live/session", json={"character_id": "maya", "language": "en"})
    s2 = r2.json()
    r2_turn = requests.post(f"{BASE_URL}/api/live/session/{s2['session_id']}/turn", json={"text": "Hello, explain the platform."})
    t_s2 = r2_turn.json()
    print(f"Session 2 Register: {t_s2['register']} (verified clean reset without carryover)")
    assert t_s2["register"] == "technical"
    requests.post(f"{BASE_URL}/api/live/session/{s2['session_id']}/close")

    print("\n>>> ALL E2E MILESTONE 6 CHECKS PASSED SUCCESSFULLY! <<<\n")

if __name__ == "__main__":
    test_e2e_live_flow()
