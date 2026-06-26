from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str


@dataclass
class ModelResponse:
    content: str | None = None
    tool_calls: list[ToolCall] | None = None


def get_weather(location: str) -> dict[str, Any]:
    return {
        "location": location,
        "forecast": "sunny",
        "temperature_f": 72,
    }


def lookup_order(order_id: str) -> dict[str, Any]:
    orders = {
        "ord_123": {"status": "shipped", "total": 42.50},
        "ord_999": {"status": "delayed", "total": 18.00},
    }
    return orders.get(order_id, {"error": "order not found"})


TOOLS: dict[str, Callable[..., dict[str, Any]]] = {
    "get_weather": get_weather,
    "lookup_order": lookup_order,
}


class FakeModel:
    def __init__(self, responses: list[ModelResponse]):
        self._responses = responses
        self.calls: list[list[dict[str, Any]]] = []

    def complete(self, messages: list[dict[str, Any]]) -> ModelResponse:
        self.calls.append(list(messages))
        if not self._responses:
            raise RuntimeError("fake model has no responses left")
        return self._responses.pop(0)


def run_agent(user_message: str, model: FakeModel) -> str:
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]

    response = model.complete(messages)

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        result = TOOLS[tool_call.name](tool_call.arguments)
        messages.append({"role": "tool", "content": str(result)})
        response = model.complete(messages)

    return response.content or ""
