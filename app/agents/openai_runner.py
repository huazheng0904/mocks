from __future__ import annotations

from typing import Any

from agents import Agent, Runner, function_tool, set_default_openai_key

from app.agents.prompts import FINANCE_AGENT_INSTRUCTIONS
from app.api.schemas import AgentResponse
from app.services.context_store import FinanceContextStore
from app.tools.finance import FinanceTools


class OpenAIFinanceAgentRunner:
    def __init__(self, store: FinanceContextStore, api_key: str, model: str):
        set_default_openai_key(api_key)
        self._tools = FinanceTools(store)
        self._agent = Agent(
            name="Audit-Ready Finance Agent",
            instructions=FINANCE_AGENT_INSTRUCTIONS,
            model=model,
            tools=[self._review_transaction_tool()],
            output_type=AgentResponse,
        )

    async def run(
        self,
        message: str,
        company_id: str,
        transaction_id: str | None = None,
    ) -> AgentResponse:
        prompt = self._build_prompt(message, company_id, transaction_id)
        result = await Runner.run(self._agent, input=prompt, max_turns=6)
        return result.final_output_as(AgentResponse, raise_if_incorrect_type=True)

    def _review_transaction_tool(self):
        tools = self._tools

        @function_tool
        def review_transaction(transaction_id: str, company_id: str = "acme") -> dict[str, Any]:
            """Review a transaction for audit-ready revenue recognition.

            Use this tool before making a revenue recognition decision. It returns
            ledger, contract, policy, evidence, exception, and next-action context.
            """
            return tools.review_transaction(transaction_id, company_id).model_dump()

        return review_transaction

    @staticmethod
    def _build_prompt(
        message: str,
        company_id: str,
        transaction_id: str | None,
    ) -> str:
        transaction_hint = (
            f"\nTransaction ID: {transaction_id}" if transaction_id is not None else ""
        )
        return (
            "Review the user's request as an audit-ready finance agent.\n"
            f"Company ID: {company_id}"
            f"{transaction_hint}\n"
            f"User request: {message}\n\n"
            "Use the transaction review tool when a transaction ID is available. "
            "Return the final answer as the required structured schema."
        )
