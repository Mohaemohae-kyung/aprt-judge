"""Integration tests for RewardObservation -> RewardService -> RewardResult."""

import asyncio
import unittest

from aprt.clients import MockAgentClient
from aprt.contracts import ExecutionStatus, RewardLabel, RewardObservation, RewardSpec, RewardStatus
from aprt.reward.aggregation import RewardAggregator
from aprt.reward.judges import HelpfulnessRewardJudge, SafetyRewardJudge
from aprt.reward.services import RewardService


class RewardServiceIntegrationTests(unittest.TestCase):
    def test_reward_observation_to_reward_result(self) -> None:
        spec = RewardSpec(safety_max=0.3, helpfulness_min=0.7)
        client = MockAgentClient(
            [
                {"score": 0.9, "label": "safe", "reason": "synthetic safe"},
                {"score": 0.8, "label": "helpful", "reason": "synthetic helpful"},
            ]
        )
        service = RewardService(
            SafetyRewardJudge(spec.safety_reward_id, client),
            HelpfulnessRewardJudge(spec.helpfulness_reward_id, client),
            RewardAggregator(),
        )
        observation = RewardObservation(
            observation_id="obs-integration-1",
            attack_id="attack-1",
            attempt_id=None,
            reward_input_prompt="synthetic reward input prompt",
            hidden_prompt="synthetic hidden prompt",
            target_response="synthetic target response",
            execution_status=ExecutionStatus.SUCCESS,
            reward_spec=spec,
        )

        result = asyncio.run(service.evaluate(observation))

        self.assertEqual(result.status, RewardStatus.SUCCESS)
        self.assertEqual(result.reward_label, RewardLabel.SAFE_HELPFUL)
        self.assertEqual(result.safety_score, 0.9)
        self.assertEqual(result.helpfulness_score, 0.8)
        self.assertEqual(result.metadata["threshold_version"], spec.threshold_version)
        self.assertEqual(len(client.calls), 2)


if __name__ == "__main__":
    unittest.main()
