from fastapi.testclient import TestClient

from agentsec_arena.main import app


client = TestClient(app)


def test_api_round_trip():
    scenarios = client.get("/api/scenarios")
    assert scenarios.status_code == 200
    assert any(item["id"] == "dvwa" for item in scenarios.json())

    created = client.post("/api/runs", json={"scenario_id": "dvwa"})
    assert created.status_code == 201
    run_id = created.json()["run"]["id"]

    attacker = client.post(f"/api/runs/{run_id}/start-attacker")
    assert attacker.status_code == 200
    assert attacker.json()["findings"]

    defender = client.post(f"/api/runs/{run_id}/start-defender")
    assert defender.status_code == 200
    assert defender.json()["score"]["total"] > 0

    report = client.post(f"/api/runs/{run_id}/report")
    assert report.status_code == 201
    assert "AgentSec Arena Report" in report.json()["content"]

