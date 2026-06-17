"""Opt-in OpenRouter smoke test for real Reward LLM calls."""

import asyncio
import os
import unittest

from aprt.clients import APIAgentClient
from aprt.contracts import ExecutionStatus, RewardObservation, RewardSpec
from aprt.reward.aggregation import RewardAggregator
from aprt.reward.judges import HelpfulnessRewardJudge, SafetyRewardJudge
from aprt.reward.services import RewardService


def _smoke_enabled() -> bool:
    return all(
        [
            os.getenv("RUN_OPENROUTER_SMOKE") == "1",
            os.getenv("OPENROUTER_API_KEY"),
            os.getenv("REWARD_LLM_SAFETY_MODEL"),
            os.getenv("REWARD_LLM_HELPFULNESS_MODEL"),
        ]
    )


@unittest.skipUnless(
    _smoke_enabled(),
    "Set RUN_OPENROUTER_SMOKE=1 and OpenRouter reward model env vars to run.",
)
class OpenRouterSmokeTests(unittest.TestCase):
    def test_reward_service_calls_openrouter(self) -> None:
        spec = RewardSpec.from_env()
        service = RewardService(
            SafetyRewardJudge(
                spec.safety_reward_id,
                APIAgentClient.from_env_for_role("safety"),
            ),
            HelpfulnessRewardJudge(
                spec.helpfulness_reward_id,
                APIAgentClient.from_env_for_role("helpfulness"),
            ),
            RewardAggregator(),
        )
        observation = RewardObservation(
            observation_id="obs-openrouter-smoke",
            attack_id="attack-openrouter-smoke",
            attempt_id="attempt-openrouter-smoke",
            reward_input_prompt="synthetic benign reward input placeholder",
            hidden_prompt="synthetic hidden prompt placeholder",
            target_response="synthetic harmless target response placeholder",
            execution_status=ExecutionStatus.SUCCESS,
            reward_spec=spec,
        )

        result = asyncio.run(service.evaluate(observation))

        self.assertEqual(result.status.value, "success")
        self.assertIsNotNone(result.safety_score)
        self.assertIsNotNone(result.helpfulness_score)


if __name__ == "__main__":
    unittest.main()
