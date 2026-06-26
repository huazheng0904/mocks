from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.schemas import AgentResponse, ReviewDecision


class EvalCase(BaseModel):
    id: str
    message: str
    company_id: str = "acme"
    transaction_id: str | None = None
    expected_decision: ReviewDecision
    expected_requires_human_review: bool
    required_exceptions: list[str] = Field(default_factory=list)
    required_evidence_sources: list[str] = Field(default_factory=list)
    min_score: float = 1.0


class EvalResult(BaseModel):
    id: str
    passed: bool
    score: float
    reasons: list[str]
    actual_decision: ReviewDecision
    actual_requires_human_review: bool


def score_transaction_review(case: EvalCase, output: AgentResponse) -> EvalResult:
    checks = [
        (
            output.decision == case.expected_decision,
            f"decision expected {case.expected_decision}, got {output.decision}",
        ),
        (
            output.requires_human_review == case.expected_requires_human_review,
            (
                "requires_human_review expected "
                f"{case.expected_requires_human_review}, got {output.requires_human_review}"
            ),
        ),
    ]

    for required_exception in case.required_exceptions:
        checks.append(
            (
                required_exception in output.exceptions,
                f"missing required exception: {required_exception}",
            )
        )

    actual_sources = {item.source for item in output.evidence}
    for required_source in case.required_evidence_sources:
        checks.append(
            (
                required_source in actual_sources,
                f"missing required evidence source: {required_source}",
            )
        )

    passed_checks = [passed for passed, _reason in checks]
    score = sum(1 for passed in passed_checks if passed) / len(passed_checks)
    reasons = [reason for passed, reason in checks if not passed]

    return EvalResult(
        id=case.id,
        passed=score >= case.min_score and not reasons,
        score=score,
        reasons=reasons,
        actual_decision=output.decision,
        actual_requires_human_review=output.requires_human_review,
    )
