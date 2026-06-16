"""Aggregate safety and helpfulness reward outputs."""

from aprt.contracts.reward_scores import RewardScores
from aprt.reward.judges.types import RewardJudgeOutput
from aprt.utils.errors import InvalidRewardOutputError


class RewardAggregator:
    """Validate and bundle Rs/Rh outputs."""

    def aggregate(
        self,
        safety_output: RewardJudgeOutput,
        helpfulness_output: RewardJudgeOutput,
    ) -> RewardScores:
        try:
            return RewardScores(
                safety_score=safety_output.score,
                helpfulness_score=helpfulness_output.score,
                safety_raw_output=safety_output.raw_output,
                helpfulness_raw_output=helpfulness_output.raw_output,
            )
        except ValueError as exc:
            raise InvalidRewardOutputError(str(exc)) from exc
