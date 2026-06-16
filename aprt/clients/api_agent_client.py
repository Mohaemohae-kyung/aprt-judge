"""Environment-configured API AgentClient skeleton."""

from dataclasses import dataclass
import os
from typing import Any

from aprt.clients.agent_client import AgentClient
from aprt.utils.errors import RewardEvaluationError


@dataclass(slots=True)
class APIAgentClient(AgentClient):
    """Provider extension point for Claude, Gemini, and future reward LLMs."""

    provider: str = "mock"
    model_name: str = "reward-llm"
    timeout_sec: float = 30.0
    max_retries: int = 1
    claude_api_key: str | None = None
    gemini_api_key: str | None = None
    model_version: str = "api"

    @classmethod
    def from_env(cls) -> "APIAgentClient":
        """Create an API client config from environment variables."""

        return cls(
            provider=os.getenv("REWARD_LLM_PROVIDER", "mock"),
            model_name=os.getenv("REWARD_LLM_MODEL", "reward-llm"),
            timeout_sec=float(os.getenv("REWARD_LLM_TIMEOUT_SEC", "30")),
            max_retries=int(os.getenv("REWARD_LLM_MAX_RETRIES", "1")),
            claude_api_key=os.getenv("CLAUDE_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
        )

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        timeout_sec: float,
    ) -> dict[str, Any]:
        """Call a provider SDK once it is wired in.

        The provider-specific SDK integration is intentionally deferred. This
        skeleton preserves the runtime configuration and failure mode.
        """

        raise RewardEvaluationError(
            f"API provider integration is not implemented yet: {self.provider}"
        )
