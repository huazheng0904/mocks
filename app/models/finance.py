from typing import Literal

from pydantic import BaseModel, Field


class LedgerEntry(BaseModel):
    transaction_id: str
    company_id: str
    customer_id: str
    contract_id: str
    amount: float
    currency: str = "USD"
    transaction_date: str
    requested_accounting_treatment: str


class Contract(BaseModel):
    contract_id: str
    customer_id: str
    performance_obligation: str
    acceptance_required: bool
    acceptance_evidence_id: str | None = None


class AccountingPolicy(BaseModel):
    policy_id: str
    workflow: str
    rule: str
    required_evidence: list[str] = Field(default_factory=list)


class AuditEvidence(BaseModel):
    evidence_id: str
    entity_id: str
    evidence_type: str
    status: Literal["available", "missing", "rejected"]
    detail: str


class HistoricalDecision(BaseModel):
    decision_id: str
    entity_id: str
    outcome: str
    rationale: str
