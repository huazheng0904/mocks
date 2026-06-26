from __future__ import annotations

from app.agents.openai_runner import OpenAIFinanceAgentRunner
from app.api.schemas import AgentResponse, ChatRequest, TransactionReviewRequest
from app.config import Settings, get_settings
from app.services.context_store import FinanceContextStore
from app.tools.finance import FinanceTools


class FinanceAgentService:
    """Thin orchestration boundary around the agent runtime.

    The first foundation keeps transaction review deterministic and testable.
    The OpenAI Agents SDK can be wired here without changing the HTTP or tool
    contracts.
    """

    def __init__(
        self,
        store: FinanceContextStore,
        settings: Settings | None = None,
        openai_runner: OpenAIFinanceAgentRunner | None = None,
    ):
        self._store = store
        self._settings = settings or get_settings()
        self._tools = FinanceTools(store)
        self._openai_runner = openai_runner

    async def chat(self, request: ChatRequest) -> AgentResponse:
        transaction_id = request.transaction_id or self._tools.infer_transaction_id(request.message)
        if self._should_use_openai():
            return await self._get_openai_runner().run(
                message=request.message,
                company_id=request.company_id,
                transaction_id=transaction_id,
            )

        if transaction_id is None:
            return AgentResponse(
                answer="I need a transaction ID before I can perform an audit-ready review.",
                confidence="high",
                decision="escalate",
                evidence=[],
                exceptions=["No transaction ID was provided."],
                requires_human_review=True,
                next_actions=["Provide a transaction_id or mention one in the message."],
            )
        return self._tools.review_transaction(transaction_id, request.company_id)

    async def review_transaction(self, request: TransactionReviewRequest) -> AgentResponse:
        if self._should_use_openai():
            return await self._get_openai_runner().run(
                message=f"Review transaction {request.transaction_id}. Can it be approved?",
                company_id=request.company_id,
                transaction_id=request.transaction_id,
            )
        return self._tools.review_transaction(request.transaction_id, request.company_id)

    def _should_use_openai(self) -> bool:
        return (
            self._settings.agent_mode == "openai"
            and self._settings.openai_api_key is not None
            and self._settings.openai_api_key.strip() != ""
        )

    def _get_openai_runner(self) -> OpenAIFinanceAgentRunner:
        if self._openai_runner is None:
            if self._settings.openai_api_key is None:
                raise RuntimeError("OPENAI_API_KEY is required for AGENT_MODE=openai")
            self._openai_runner = OpenAIFinanceAgentRunner(
                store=self._store,
                api_key=self._settings.openai_api_key,
                model=self._settings.openai_model,
            )
        return self._openai_runner
