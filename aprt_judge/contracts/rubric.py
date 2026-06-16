"""Success rubric contract."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from aprt_judge.contracts.enums import Decision


@dataclass(frozen=True, slots=True)
class SuccessRubric:
    """Minimal rubric definition for v0 scoring and routing."""

    rubric_id: str
    version: str
    goal: str
    score_weights: Mapping[str, float] = field(default_factory=dict)
    thresholds: Mapping[Decision, float] = field(default_factory=dict)
    decision_caps: Mapping[str, Decision] = field(default_factory=dict)
    enabled_judges: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.rubric_id:
            raise ValueError("rubric_id is required")
        if not self.version:
            raise ValueError("version is required")
        if not self.goal:
            raise ValueError("goal is required")

        for name, weight in self.score_weights.items():
            if weight < 0:
                raise ValueError(f"score weight must be non-negative: {name}")
        for decision, threshold in self.thresholds.items():
            if not isinstance(decision, Decision):
                raise ValueError("threshold keys must be Decision values")
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(f"threshold must be between 0.0 and 1.0: {decision}")

        object.__setattr__(self, "score_weights", MappingProxyType(dict(self.score_weights)))
        object.__setattr__(self, "thresholds", MappingProxyType(dict(self.thresholds)))
        object.__setattr__(self, "decision_caps", MappingProxyType(dict(self.decision_caps)))
        object.__setattr__(self, "enabled_judges", tuple(self.enabled_judges))
