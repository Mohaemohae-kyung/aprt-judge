"""Internal reward judge score type."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class RewardJudgeOutput:
    """Parsed output from a single reward judge."""

    reward_id: str
    score: float
    label: str
    reason: str
    raw_output: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw_output", MappingProxyType(dict(self.raw_output)))
