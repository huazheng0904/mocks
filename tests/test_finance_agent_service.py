import pytest

from app.agents.finance_agent import FinanceAgentService
from app.api.schemas import AgentResponse, ChatRequest, EvidenceItem, TransactionReviewRequest
from app.config import Settings
from app.services.context_store import JsonFinanceContextStore


@pytest.mark.anyio
async def test_service_uses_deterministic_mode_without_api_key():
    service = FinanceAgentService(
        store=JsonFinanceContextStore(),
        settings=Settings(agent_mode="openai", openai_api_key=None),
    )

    result = await service.review_transaction(
        TransactionReviewRequest(transaction_id="txn_1007", company_id="acme")
    )

    assert result.decision == "escalate"
    assert "Missing customer acceptance evidence." in result.exceptions


class FakeOpenAIRunner:
    async def run(self, message: str, company_id: str, transaction_id: str | None = None):
        return AgentResponse(
            answer=f"live path used for {transaction_id}",
            confidence="high",
            decision="approve",
            evidence=[EvidenceItem(source="test", detail=message)],
            exceptions=[],
            requires_human_review=False,
            next_actions=[],
        )


@pytest.mark.anyio
async def test_service_uses_openai_runner_when_enabled_with_key():
    service = FinanceAgentService(
        store=JsonFinanceContextStore(),
        settings=Settings(agent_mode="openai", openai_api_key="test-key"),
        openai_runner=FakeOpenAIRunner(),
    )

    result = await service.chat(
        ChatRequest(message="Review txn_1007", transaction_id="txn_1007")
    )

    assert result.answer == "live path used for txn_1007"
