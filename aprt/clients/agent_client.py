"""Agent client interface for LLM JSON completion."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class AgentClient(ABC):
    """Provider-agnostic async JSON completion interface."""

    model_name: ClassVar[str] = "unknown"
    model_version: ClassVar[str] = "unknown"

    @abstractmethod
    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        timeout_sec: float,
    ) -> dict[str, Any]:
        """Return a JSON object from an LLM provider."""
