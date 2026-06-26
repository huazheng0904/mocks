from typing import Annotated

from fastapi import APIRouter, Depends

from app.agents.finance_agent import FinanceAgentService
from app.api.schemas import (
    AgentResponse,
    ChatRequest,
    HealthResponse,
    TransactionReviewRequest,
)
from app.services.context_store import JsonFinanceContextStore


router = APIRouter()


def get_agent_service() -> FinanceAgentService:
    return FinanceAgentService(store=JsonFinanceContextStore())


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="finance-agent-service")


@router.post("/agent/chat", response_model=AgentResponse)
async def chat(
    request: ChatRequest,
    agent_service: Annotated[FinanceAgentService, Depends(get_agent_service)],
) -> AgentResponse:
    return await agent_service.chat(request)


@router.post("/agent/review-transaction", response_model=AgentResponse)
async def review_transaction(
    request: TransactionReviewRequest,
    agent_service: Annotated[FinanceAgentService, Depends(get_agent_service)],
) -> AgentResponse:
    return await agent_service.review_transaction(request)
