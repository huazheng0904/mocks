from typing import Literal

from pydantic import BaseModel, Field


Confidence = Literal["low", "medium", "high"]
ReviewDecision = Literal["approve", "reject", "escalate"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    company_id: str = "acme"
    transaction_id: str | None = None


class TransactionReviewRequest(BaseModel):
    transaction_id: str = Field(min_length=1)
    company_id: str = "acme"


class EvidenceItem(BaseModel):
    source: str
    detail: str


class AgentResponse(BaseModel):
    answer: str
    confidence: Confidence
    decision: ReviewDecision
    evidence: list[EvidenceItem]
    exceptions: list[str]
    requires_human_review: bool
    next_actions: list[str]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
