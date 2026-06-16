"""Output contract for APRT Reward Judge Core."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from aprt.contracts.enums import RewardLabel, RewardStatus
from aprt.utils.errors import RewardError


@dataclass(frozen=True, slots=True)
class RewardResult:
    """Final result returned by RewardService."""

    observation_id: str
    attack_id: str
    attempt_id: str | None
    safety_score: float | None
    helpfulness_score: float | None
    reward_label: RewardLabel
    status: RewardStatus
    raw_outputs: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    error: RewardError | None = None

    def __post_init__(self) -> None:
        if not self.observation_id:
            raise ValueError("observation_id is required")
        if not self.attack_id:
            raise ValueError("attack_id is required")
        if self.safety_score is not None and not 0.0 <= self.safety_score <= 1.0:
            raise ValueError("safety_score must be between 0.0 and 1.0")
        if self.helpfulness_score is not None and not 0.0 <= self.helpfulness_score <= 1.0:
            raise ValueError("helpfulness_score must be between 0.0 and 1.0")

        object.__setattr__(self, "raw_outputs", MappingProxyType(dict(self.raw_outputs)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
