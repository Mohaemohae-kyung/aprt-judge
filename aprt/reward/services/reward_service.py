"""RewardService orchestration for APRT Reward Judge Core."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from aprt.contracts.enums import ExecutionStatus, RewardLabel, RewardStatus
from aprt.contracts.reward_observation import RewardObservation
from aprt.contracts.reward_result import RewardResult
from aprt.reward.aggregation.reward_aggregator import RewardAggregator
from aprt.reward.judges.helpfulness_reward_judge import HelpfulnessRewardJudge
from aprt.reward.judges.safety_reward_judge import SafetyRewardJudge
from aprt.utils.errors import InvalidRewardOutputError, RewardError, RewardEvaluationError
from aprt.utils.score_utils import classify_reward_label


@dataclass(slots=True)
class RewardService:
    """Stage-agnostic Rs/Rh pair scoring service."""

    safety_judge: SafetyRewardJudge
    helpfulness_judge: HelpfulnessRewardJudge
    aggregator: RewardAggregator

    async def evaluate(self, observation: RewardObservation) -> RewardResult:
        spec = observation.reward_spec
        base_metadata = self._metadata(observation)

        if observation.execution_status != ExecutionStatus.SUCCESS:
            return self._skipped(observation, base_metadata, "execution_status_not_success")
        if not observation.target_response.strip():
            return self._skipped(observation, base_metadata, "empty_target_response")

        try:
            safety_output = await self.safety_judge.score_pair(
                observation.reward_input_prompt,
                observation.target_response,
                spec,
            )
            helpfulness_output = await self.helpfulness_judge.score_pair(
                observation.reward_input_prompt,
                observation.target_response,
                spec,
            )
            scores = self.aggregator.aggregate(safety_output, helpfulness_output)
        except InvalidRewardOutputError as exc:
            return self._failed(
                observation,
                base_metadata,
                RewardStatus.INVALID_OUTPUT,
                RewardError(exc.code, str(exc)),
            )
        except RewardEvaluationError as exc:
            return self._failed(
                observation,
                base_metadata,
                RewardStatus.EVALUATION_ERROR,
                RewardError(exc.code, str(exc)),
            )
        except TimeoutError as exc:
            return self._failed(
                observation,
                base_metadata,
                RewardStatus.EVALUATION_ERROR,
                RewardError("timeout", str(exc)),
            )
        except Exception as exc:
            return self._failed(
                observation,
                base_metadata,
                RewardStatus.EVALUATION_ERROR,
                RewardError("evaluation_error", str(exc)),
            )

        label = classify_reward_label(
            scores.safety_score,
            scores.helpfulness_score,
            spec.safety_max,
            spec.helpfulness_min,
        )
        return RewardResult(
            observation_id=observation.observation_id,
            attack_id=observation.attack_id,
            attempt_id=observation.attempt_id,
            safety_score=scores.safety_score,
            helpfulness_score=scores.helpfulness_score,
            reward_label=label,
            status=RewardStatus.SUCCESS,
            raw_outputs={
                "safety": dict(scores.safety_raw_output),
                "helpfulness": dict(scores.helpfulness_raw_output),
            },
            metadata=base_metadata,
        )

    def _metadata(self, observation: RewardObservation) -> dict[str, Any]:
        spec = observation.reward_spec
        client = self.safety_judge.client
        return {
            "safety_reward_id": spec.safety_reward_id,
            "helpfulness_reward_id": spec.helpfulness_reward_id,
            "safety_prompt_version": self.safety_judge.prompt_version,
            "helpfulness_prompt_version": self.helpfulness_judge.prompt_version,
            "threshold_version": spec.threshold_version,
            "model_name": getattr(client, "model_name", "unknown"),
            "model_version": getattr(client, "model_version", "unknown"),
            "temperature": spec.temperature,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _skipped(
        self,
        observation: RewardObservation,
        metadata: dict[str, Any],
        reason: str,
    ) -> RewardResult:
        return RewardResult(
            observation_id=observation.observation_id,
            attack_id=observation.attack_id,
            attempt_id=observation.attempt_id,
            safety_score=None,
            helpfulness_score=None,
            reward_label=RewardLabel.NO_SIGNAL,
            status=RewardStatus.SKIPPED,
            metadata={**metadata, "skip_reason": reason},
        )

    def _failed(
        self,
        observation: RewardObservation,
        metadata: dict[str, Any],
        status: RewardStatus,
        error: RewardError,
    ) -> RewardResult:
        return RewardResult(
            observation_id=observation.observation_id,
            attack_id=observation.attack_id,
            attempt_id=observation.attempt_id,
            safety_score=None,
            helpfulness_score=None,
            reward_label=RewardLabel.NO_SIGNAL,
            status=status,
            metadata=metadata,
            error=error,
        )
