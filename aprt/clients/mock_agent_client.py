"""Mock AgentClient for deterministic reward judge tests."""

from collections.abc import Iterable
from typing import Any

from aprt.clients.agent_client import AgentClient


class MockAgentClient(AgentClient):
    """Queue-backed mock client.

    Each call consumes one queued response. If no response is queued, a safe and
    helpful default is returned.
    """

    model_name = "mock-reward-llm"
    model_version = "test"

    def __init__(self, responses: Iterable[dict[str, Any] | Exception] | None = None) -> None:
        self._responses = list(responses or [])
        self.calls: list[dict[str, Any]] = []

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        timeout_sec: float,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "temperature": temperature,
                "timeout_sec": timeout_sec,
            }
        )

        if self._responses:
            response = self._responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response

        if "helpfulness" in system_prompt.lower():
            return {"score": 0.8, "label": "helpful", "reason": "mock default"}
        return {"score": 0.8, "label": "safe", "reason": "mock default"}
