from app.services.context_store import JsonFinanceContextStore
from app.tools.finance import FinanceTools


def test_transaction_with_missing_acceptance_escalates():
    tools = FinanceTools(JsonFinanceContextStore())

    result = tools.review_transaction("txn_1007", "acme")

    assert result.decision == "escalate"
    assert result.requires_human_review is True
    assert "Missing customer acceptance evidence." in result.exceptions


def test_transaction_without_acceptance_requirement_can_be_approved():
    tools = FinanceTools(JsonFinanceContextStore())

    result = tools.review_transaction("txn_1012", "acme")

    assert result.decision == "approve"
    assert result.requires_human_review is False
    assert result.exceptions == []


def test_transaction_id_can_be_inferred_from_message():
    tools = FinanceTools(JsonFinanceContextStore())

    assert tools.infer_transaction_id("Please review txn_1007 today") == "txn_1007"
