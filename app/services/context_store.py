from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from app.models.finance import (
    AccountingPolicy,
    AuditEvidence,
    Contract,
    HistoricalDecision,
    LedgerEntry,
)


class FinanceContextStore(Protocol):
    def get_transaction(self, transaction_id: str) -> LedgerEntry | None:
        ...

    def get_contract(self, contract_id: str) -> Contract | None:
        ...

    def get_policy(self, workflow: str) -> AccountingPolicy | None:
        ...

    def list_evidence(self, entity_id: str) -> list[AuditEvidence]:
        ...

    def list_decisions(self, entity_id: str) -> list[HistoricalDecision]:
        ...


class JsonFinanceContextStore:
    def __init__(self, data_dir: Path | None = None):
        self._data_dir = data_dir or Path(__file__).resolve().parents[2] / "data"
        self._transactions = self._load_models("ledger_entries.json", LedgerEntry)
        self._contracts = self._load_models("contracts.json", Contract)
        self._policies = self._load_models("accounting_policies.json", AccountingPolicy)
        self._evidence = self._load_models("audit_evidence.json", AuditEvidence)
        self._decisions = self._load_models("historical_decisions.json", HistoricalDecision)

    def get_transaction(self, transaction_id: str) -> LedgerEntry | None:
        return self._find(self._transactions, "transaction_id", transaction_id)

    def get_contract(self, contract_id: str) -> Contract | None:
        return self._find(self._contracts, "contract_id", contract_id)

    def get_policy(self, workflow: str) -> AccountingPolicy | None:
        return self._find(self._policies, "workflow", workflow)

    def list_evidence(self, entity_id: str) -> list[AuditEvidence]:
        return [item for item in self._evidence if item.entity_id == entity_id]

    def list_decisions(self, entity_id: str) -> list[HistoricalDecision]:
        return [item for item in self._decisions if item.entity_id == entity_id]

    def _load_models(self, filename: str, model_type):
        raw = json.loads((self._data_dir / filename).read_text(encoding="utf-8"))
        return [model_type.model_validate(item) for item in raw]

    @staticmethod
    def _find(items, field_name: str, value: str):
        return next((item for item in items if getattr(item, field_name) == value), None)
