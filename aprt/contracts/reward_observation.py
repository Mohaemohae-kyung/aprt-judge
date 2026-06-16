"""Input contract for stage-agnostic reward pair scoring."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from aprt.contracts.enums import ExecutionStatus
from aprt.contracts.reward_spec import RewardSpec


@dataclass(frozen=True, slots=True)
class RewardObservation:
    """Observation consumed by RewardService.

    The reward pair is `(reward_input_prompt, target_response)`. `hidden_prompt`
    is trace metadata and is not the direct scoring criterion for Rs/Rh.
    """

    observation_id: str
    attack_id: str
    attempt_id: str | None
    reward_input_prompt: str
    hidden_prompt: str | None
    target_response: str
    execution_status: ExecutionStatus
    reward_spec: RewardSpec = field(default_factory=RewardSpec)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.observation_id:
            raise ValueError("observation_id is required")
        if not self.attack_id:
            raise ValueError("attack_id is required")
        if not isinstance(self.execution_status, ExecutionStatus):
            raise ValueError("execution_status must be an ExecutionStatus")
        if self.execution_status == ExecutionStatus.SUCCESS:
            if not self.reward_input_prompt:
                raise ValueError("reward_input_prompt is required for successful execution")

        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
