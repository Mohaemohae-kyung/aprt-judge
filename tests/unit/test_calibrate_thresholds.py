"""Unit tests for the threshold calibration helper script."""

import json
import subprocess
import sys
import unittest


class CalibrateThresholdsScriptTests(unittest.TestCase):
    def test_script_outputs_recommended_candidate_without_mutating_defaults(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/calibrate_thresholds.py"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(set(payload), {"recommended_candidate"})
        candidate = payload["recommended_candidate"]
        self.assertEqual(candidate["fixture_type"], "synthetic_smoke")
        self.assertIn("safety_max", candidate)
        self.assertIn("helpfulness_min", candidate)
        self.assertTrue(candidate["human_review_required"])
        self.assertIn("does not mutate RewardSpec defaults", candidate["note"])


if __name__ == "__main__":
    unittest.main()
