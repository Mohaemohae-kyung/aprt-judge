"""Unit tests for reward prompt templates."""

import unittest

from aprt.reward.prompts.helpfulness_prompt import (
    HELPFULNESS_PROMPT_VERSION,
    HELPFULNESS_SYSTEM_PROMPT,
    build_helpfulness_user_prompt,
)
from aprt.reward.prompts.safety_prompt import (
    SAFETY_PROMPT_VERSION,
    SAFETY_SYSTEM_PROMPT,
    build_safety_user_prompt,
)


class RewardPromptTests(unittest.TestCase):
    def test_safety_prompt_documents_pair_scoring_and_score_direction(self) -> None:
        self.assertEqual(SAFETY_PROMPT_VERSION, "safety_prompt.v1")
        self.assertIn("pair scoring", SAFETY_SYSTEM_PROMPT)
        self.assertIn("Lower score", SAFETY_SYSTEM_PROMPT)
        self.assertIn("safe, unsafe, uncertain", SAFETY_SYSTEM_PROMPT)
        self.assertIn("reason is for debugging only", SAFETY_SYSTEM_PROMPT)

    def test_helpfulness_prompt_documents_pair_scoring_and_score_direction(self) -> None:
        self.assertEqual(HELPFULNESS_PROMPT_VERSION, "helpfulness_prompt.v1")
        self.assertIn("pair scoring", HELPFULNESS_SYSTEM_PROMPT)
        self.assertIn("Higher scores require semantic relevance", HELPFULNESS_SYSTEM_PROMPT)
        self.assertIn("helpful, unhelpful, uncertain", HELPFULNESS_SYSTEM_PROMPT)
        self.assertIn("reason is for debugging only", HELPFULNESS_SYSTEM_PROMPT)

    def test_user_prompts_include_only_pair_fields(self) -> None:
        safety_prompt = build_safety_user_prompt("synthetic prompt", "synthetic response")
        helpfulness_prompt = build_helpfulness_user_prompt("synthetic prompt", "synthetic response")

        self.assertIn("[reward_input_prompt]", safety_prompt)
        self.assertIn("[target_response]", safety_prompt)
        self.assertIn("[reward_input_prompt]", helpfulness_prompt)
        self.assertIn("[target_response]", helpfulness_prompt)
        self.assertNotIn("hidden_prompt", safety_prompt)
        self.assertNotIn("hidden_prompt", helpfulness_prompt)


if __name__ == "__main__":
    unittest.main()
