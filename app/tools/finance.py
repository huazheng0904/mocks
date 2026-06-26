from __future__ import annotations

import re

from app.api.schemas import AgentResponse, EvidenceItem
from app.services.context_store import FinanceContextStore


class FinanceTools:
    def __init__(self, store: FinanceContextStore):
        self._store = store

    def infer_transaction_id(self, message: str) -> str | None:
        match = re.search(r"\btxn_[a-zA-Z0-9_]+\b", message)
        return match.group(0) if match else None

    def review_transaction(self, transaction_id: str, company_id: str = "acme") -> AgentResponse:
        transaction = self._store.get_transaction(transaction_id)
        if transaction is None or transaction.company_id != company_id:
            return AgentResponse(
                answer=f"Transaction {transaction_id} was not found for company {company_id}.",
                confidence="high",
                decision="escalate",
                evidence=[],
                exceptions=["Transaction not found."],
                requires_human_review=True,
                next_actions=["Confirm the transaction ID and company scope."],
            )

        contract = self._store.get_contract(transaction.contract_id)
        policy = self._store.get_policy("revenue_recognition")
        transaction_evidence = self._store.list_evidence(transaction.transaction_id)
        contract_evidence = self._store.list_evidence(transaction.contract_id)
        historical_decisions = self._store.list_decisions(transaction.customer_id)

        evidence = [
            EvidenceItem(
                source="ledger",
                detail=(
                    f"{transaction.transaction_id} requests "
                    f"{transaction.requested_accounting_treatment} for "
                    f"{transaction.amount:.2f} {transaction.currency}."
                ),
            )
        ]
        exceptions: list[str] = []
        next_actions: list[str] = []

        if contract is None:
            exceptions.append("Related contract is missing.")
            next_actions.append("Attach or ingest the related customer contract.")
        else:
            evidence.append(
                EvidenceItem(
                    source="contract",
                    detail=(
                        f"{contract.contract_id} obligation: "
                        f"{contract.performance_obligation}."
                    ),
                )
            )

        if policy is None:
            exceptions.append("Revenue recognition policy is missing.")
            next_actions.append("Attach the revenue recognition policy.")
        else:
            evidence.append(EvidenceItem(source="policy", detail=policy.rule))

        available_evidence = [
            item for item in [*transaction_evidence, *contract_evidence] if item.status == "available"
        ]
        for item in available_evidence:
            evidence.append(EvidenceItem(source=item.evidence_type, detail=item.detail))

        if contract and contract.acceptance_required:
            acceptance_id = contract.acceptance_evidence_id
            acceptance_available = any(
                item.evidence_id == acceptance_id and item.status == "available"
                for item in contract_evidence
            )
            if not acceptance_available:
                exceptions.append("Missing customer acceptance evidence.")
                next_actions.append("Request and attach signed customer acceptance evidence.")

        if historical_decisions:
            latest = historical_decisions[-1]
            evidence.append(
                EvidenceItem(
                    source="historical_decision",
                    detail=f"{latest.outcome}: {latest.rationale}",
                )
            )

        if exceptions:
            return AgentResponse(
                answer=(
                    f"Do not approve revenue recognition for {transaction.transaction_id} yet. "
                    "Required audit evidence is incomplete."
                ),
                confidence="high",
                decision="escalate",
                evidence=evidence,
                exceptions=exceptions,
                requires_human_review=True,
                next_actions=next_actions,
            )

        return AgentResponse(
            answer=(
                f"{transaction.transaction_id} is ready for revenue recognition review. "
                "Required policy and acceptance evidence are available."
            ),
            confidence="high",
            decision="approve",
            evidence=evidence,
            exceptions=[],
            requires_human_review=False,
            next_actions=["Attach the generated review summary to the close workpaper."],
        )
