from fastapi import APIRouter

from app.agents.finance_agent import FinanceAgentService
from app.api.schemas import (
    AgentResponse,
    ChatRequest,
    HealthResponse,
    TransactionReviewRequest,
)
from app.services.context_store import JsonFinanceContextStore


router = APIRouter()
store = JsonFinanceContextStore()
agent_service = FinanceAgentService(store=store)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="finance-agent-service")


@router.post("/agent/chat", response_model=AgentResponse)
async def chat(request: ChatRequest) -> AgentResponse:
    return await agent_service.chat(request)


@router.post("/agent/review-transaction", response_model=AgentResponse)
async def review_transaction(request: TransactionReviewRequest) -> AgentResponse:
    return await agent_service.review_transaction(request)
