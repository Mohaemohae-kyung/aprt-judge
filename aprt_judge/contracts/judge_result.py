"""Final Judge/QC result contract."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from aprt_judge.contracts.enums import Decision
from aprt_judge.contracts.evidence import Evidence
from aprt_judge.contracts.raw_scores import RawScores


@dataclass(frozen=True, slots=True)
class JudgeResult:
    """Final output produced by the Judge/QC pipeline."""

    result_id: str
    observation_ref: str
    rubric_id: str
    decision: Decision
    fitness: float
    raw_scores: RawScores
    evidence: tuple[Evidence, ...] = ()
    reasons: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.result_id:
            raise ValueError("result_id is required")
        if not self.observation_ref:
            raise ValueError("observation_ref is required")
        if not self.rubric_id:
            raise ValueError("rubric_id is required")
        if self.raw_scores.rubric_id != self.rubric_id:
            raise ValueError("raw_scores.rubric_id must match result rubric_id")
        if not 0.0 <= self.fitness <= 1.0:
            raise ValueError("fitness must be between 0.0 and 1.0")

        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "reasons", tuple(self.reasons))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
