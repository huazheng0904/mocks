from fastapi.testclient import TestClient

from app.agents.finance_agent import FinanceAgentService
from app.api.routes import get_agent_service
from app.config import Settings
from app.main import create_app
from app.services.context_store import JsonFinanceContextStore


def create_test_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_agent_service] = lambda: FinanceAgentService(
        store=JsonFinanceContextStore(),
        settings=Settings(agent_mode="deterministic", openai_api_key=None),
    )
    return TestClient(app)


def test_health_endpoint():
    client = create_test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "finance-agent-service",
    }


def test_review_transaction_endpoint_escalates_missing_acceptance():
    client = create_test_client()

    response = client.post(
        "/agent/review-transaction",
        json={"transaction_id": "txn_1007", "company_id": "acme"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "escalate"
    assert payload["requires_human_review"] is True
    assert "Missing customer acceptance evidence." in payload["exceptions"]
