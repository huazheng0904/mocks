import pytest

from evals.run_evals import load_cases, run_cases


def test_eval_cases_load():
    cases = load_cases()

    assert [case.id for case in cases] == [
        "txn_1007_missing_acceptance",
        "txn_1012_subscription_ready",
        "missing_transaction_escalates",
    ]


@pytest.mark.anyio
async def test_transaction_review_evals_pass():
    results = await run_cases(load_cases())

    assert all(result.passed for result in results)
