"""Judge specification contract."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from aprt_judge.contracts.enums import JudgeType


@dataclass(frozen=True, slots=True)
class JudgeSpec:
    """Configuration boundary for a replaceable judge."""

    judge_id: str
    judge_type: JudgeType
    enabled: bool = True
    weight: float = 1.0
    config: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.judge_id:
            raise ValueError("judge_id is required")
        if self.weight < 0:
            raise ValueError("weight must be non-negative")

        object.__setattr__(self, "config", MappingProxyType(dict(self.config)))
