"""Reward Judge Core error types."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class RewardError:
    """Serializable error payload for RewardResult."""

    code: str
    message: str
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "details", MappingProxyType(dict(self.details)))


class RewardEvaluationError(Exception):
    """Raised when the LLM call itself fails."""

    def __init__(self, message: str, code: str = "evaluation_error") -> None:
        super().__init__(message)
        self.code = code


class InvalidRewardOutputError(Exception):
    """Raised when a reward model returns invalid JSON or invalid scores."""

    def __init__(self, message: str, code: str = "invalid_output") -> None:
        super().__init__(message)
        self.code = code
