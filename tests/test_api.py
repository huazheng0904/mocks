from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "finance-agent-service",
    }


def test_review_transaction_endpoint_escalates_missing_acceptance():
    client = TestClient(create_app())

    response = client.post(
        "/agent/review-transaction",
        json={"transaction_id": "txn_1007", "company_id": "acme"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "escalate"
    assert payload["requires_human_review"] is True
    assert "Missing customer acceptance evidence." in payload["exceptions"]
