"""Raw rubric scores produced before fitness calculation."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class RawScores:
    """Rubric-aligned scores before final fitness calculation."""

    rubric_id: str
    scores: Mapping[str, float]
    evidence_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.rubric_id:
            raise ValueError("rubric_id is required")
        if not self.scores:
            raise ValueError("scores are required")
        for name, score in self.scores.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"score must be between 0.0 and 1.0: {name}")

        object.__setattr__(self, "scores", MappingProxyType(dict(self.scores)))
        object.__setattr__(self, "evidence_ids", tuple(self.evidence_ids))
        object.__setattr__(self, "notes", tuple(self.notes))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
