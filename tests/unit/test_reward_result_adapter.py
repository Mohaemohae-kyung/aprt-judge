"""Unit tests for RewardResult adapter payloads."""

import unittest

from aprt.adapters import (
    reward_result_to_external_dict,
    reward_result_to_judge_result_like,
    reward_results_to_external_dicts,
)
from aprt.contracts import RewardLabel, RewardResult, RewardStatus
from aprt.utils.errors import RewardError


FORBIDDEN_DERIVED_KEYS = {
    "eligible_for_training",
    "selection_signal",
    "Djb",
    "Dhid",
    "AER",
}


def reward_result(error: RewardError | None = None) -> RewardResult:
    return RewardResult(
        observation_id="obs-1",
        attack_id="attack-1",
        attempt_id="attempt-1",
        safety_score=0.18 if error is None else None,
        helpfulness_score=0.79 if error is None else None,
        reward_label=RewardLabel.UNSAFE_HELPFUL if error is None else RewardLabel.NO_SIGNAL,
        status=RewardStatus.SUCCESS if error is None else RewardStatus.INVALID_OUTPUT,
        raw_outputs={"safety": {"score": 0.18}, "helpfulness": {"score": 0.79}},
        metadata={"threshold_version": "thresholds.test.v0"},
        error=error,
    )


class RewardResultAdapterTests(unittest.TestCase):
    def test_external_dict_preserves_reward_fields_without_downstream_signals(self) -> None:
        payload = reward_result_to_external_dict(reward_result())

        self.assertEqual(payload["observation_id"], "obs-1")
        self.assertEqual(payload["attack_id"], "attack-1")
        self.assertEqual(payload["attempt_id"], "attempt-1")
        self.assertEqual(payload["safety_score"], 0.18)
        self.assertEqual(payload["helpfulness_score"], 0.79)
        self.assertEqual(payload["reward_label"], "unsafe_helpful")
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["metadata"]["threshold_version"], "thresholds.test.v0")
        self.assertTrue(FORBIDDEN_DERIVED_KEYS.isdisjoint(payload))

    def test_external_dict_serializes_error(self) -> None:
        error = RewardError("invalid_output", "score missing", {"judge": "safety"})
        payload = reward_result_to_external_dict(reward_result(error))

        self.assertEqual(payload["reward_label"], "no_signal")
        self.assertEqual(payload["status"], "invalid_output")
        self.assertEqual(payload["error"]["code"], "invalid_output")
        self.assertEqual(payload["error"]["details"]["judge"], "safety")

    def test_judge_result_like_payload_keeps_scores_and_label(self) -> None:
        payload = reward_result_to_judge_result_like(reward_result())

        self.assertEqual(payload["result_type"], "judge_result_like")
        self.assertEqual(payload["scores"], {"safety": 0.18, "helpfulness": 0.79})
        self.assertEqual(payload["reward_label"], "unsafe_helpful")
        self.assertTrue(FORBIDDEN_DERIVED_KEYS.isdisjoint(payload))

    def test_batch_conversion_preserves_order(self) -> None:
        payloads = reward_results_to_external_dicts([reward_result(), reward_result()])

        self.assertEqual([payload["observation_id"] for payload in payloads], ["obs-1", "obs-1"])
        self.assertEqual([payload["reward_label"] for payload in payloads], ["unsafe_helpful", "unsafe_helpful"])


if __name__ == "__main__":
    unittest.main()
