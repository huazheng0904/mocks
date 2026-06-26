from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from app.agents.finance_agent import FinanceAgentService
from app.api.schemas import ChatRequest
from app.config import Settings
from app.services.context_store import JsonFinanceContextStore
from evals.scorers import EvalCase, EvalResult, score_transaction_review


DEFAULT_CASES_PATH = Path(__file__).parent / "cases" / "transaction_review.jsonl"


def load_cases(path: Path = DEFAULT_CASES_PATH) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            cases.append(EvalCase.model_validate_json(stripped))
        except ValueError as exc:
            raise ValueError(f"Invalid eval case at {path}:{line_number}: {exc}") from exc
    return cases


async def run_cases(cases: list[EvalCase]) -> list[EvalResult]:
    service = FinanceAgentService(
        store=JsonFinanceContextStore(),
        settings=Settings(agent_mode="deterministic", openai_api_key=None),
    )
    results: list[EvalResult] = []
    for case in cases:
        output = await service.chat(
            ChatRequest(
                message=case.message,
                company_id=case.company_id,
                transaction_id=case.transaction_id,
            )
        )
        results.append(score_transaction_review(case, output))
    return results


def print_text_report(results: list[EvalResult]) -> None:
    passed = sum(1 for result in results if result.passed)
    print(f"{passed}/{len(results)} evals passed")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{result.id}: {status} score={result.score:.2f}")
        for reason in result.reasons:
            print(f"  - {reason}")


async def async_main() -> int:
    parser = argparse.ArgumentParser(description="Run finance-agent behavior evals.")
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Path to a JSONL eval case file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON results.",
    )
    args = parser.parse_args()

    results = await run_cases(load_cases(args.cases))
    if args.json:
        print(json.dumps([result.model_dump() for result in results], indent=2))
    else:
        print_text_report(results)
    return 0 if all(result.passed for result in results) else 1


def main() -> None:
    raise SystemExit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()
