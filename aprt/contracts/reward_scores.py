"""Reward score bundle produced by RewardAggregator."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class RewardScores:
    """Validated Rs/Rh scores.

    `safety_score` is lower when the response is less safe. `helpfulness_score`
    is higher when the response is more helpful.
    """

    safety_score: float
    helpfulness_score: float
    safety_raw_output: Mapping[str, Any] = field(default_factory=dict)
    helpfulness_raw_output: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.safety_score <= 1.0:
            raise ValueError("safety_score must be between 0.0 and 1.0")
        if not 0.0 <= self.helpfulness_score <= 1.0:
            raise ValueError("helpfulness_score must be between 0.0 and 1.0")

        object.__setattr__(
            self, "safety_raw_output", MappingProxyType(dict(self.safety_raw_output))
        )
        object.__setattr__(
            self, "helpfulness_raw_output", MappingProxyType(dict(self.helpfulness_raw_output))
        )
