from __future__ import annotations

import json
import unittest

from agent import FakeModel, ModelResponse, ToolCall, run_agent


class AgentLoopTests(unittest.TestCase):
    def test_runs_single_tool_and_returns_final_answer(self) -> None:
        model = FakeModel(
            [
                ModelResponse(
                    tool_calls=[
                        ToolCall(
                            id="call_1",
                            name="get_weather",
                            arguments=json.dumps({"location": "Havana"}),
                        )
                    ]
                ),
                ModelResponse(content="It is sunny and 72F in Havana."),
            ]
        )

        answer = run_agent("What is the weather in Havana?", model)

        self.assertEqual(answer, "It is sunny and 72F in Havana.")
        second_call_messages = model.calls[1]
        self.assertEqual(second_call_messages[-1]["role"], "tool")
        self.assertEqual(second_call_messages[-1]["tool_call_id"], "call_1")
        payload = json.loads(second_call_messages[-1]["content"])
        self.assertEqual(payload["location"], "Havana")

    def test_runs_multiple_tool_calls_before_final_answer(self) -> None:
        model = FakeModel(
            [
                ModelResponse(
                    tool_calls=[
                        ToolCall(
                            id="call_weather",
                            name="get_weather",
                            arguments=json.dumps({"location": "Miami"}),
                        ),
                        ToolCall(
                            id="call_order",
                            name="lookup_order",
                            arguments=json.dumps({"order_id": "ord_123"}),
                        ),
                    ]
                ),
                ModelResponse(content="Miami is sunny, and order ord_123 shipped."),
            ]
        )

        answer = run_agent("Check weather and my order.", model)

        self.assertEqual(answer, "Miami is sunny, and order ord_123 shipped.")
        second_call_messages = model.calls[1]
        tool_messages = [message for message in second_call_messages if message["role"] == "tool"]
        self.assertEqual([message["tool_call_id"] for message in tool_messages], ["call_weather", "call_order"])

    def test_unknown_tool_is_reported_to_model(self) -> None:
        model = FakeModel(
            [
                ModelResponse(
                    tool_calls=[
                        ToolCall(
                            id="call_missing",
                            name="delete_everything",
                            arguments=json.dumps({}),
                        )
                    ]
                ),
                ModelResponse(content="I cannot use that tool."),
            ]
        )

        answer = run_agent("Use a missing tool.", model)

        self.assertEqual(answer, "I cannot use that tool.")
        payload = json.loads(model.calls[1][-1]["content"])
        self.assertIn("unknown tool", payload["error"])

    def test_bad_json_arguments_are_reported_to_model(self) -> None:
        model = FakeModel(
            [
                ModelResponse(
                    tool_calls=[
                        ToolCall(
                            id="call_bad_json",
                            name="get_weather",
                            arguments="{not-json",
                        )
                    ]
                ),
                ModelResponse(content="I could not parse the tool arguments."),
            ]
        )

        answer = run_agent("Call with bad JSON.", model)

        self.assertEqual(answer, "I could not parse the tool arguments.")
        payload = json.loads(model.calls[1][-1]["content"])
        self.assertIn("invalid JSON", payload["error"])


if __name__ == "__main__":
    unittest.main()
