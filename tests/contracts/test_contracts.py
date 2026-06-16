"""Tests for minimal Judge/QC contract models."""

import unittest

from aprt_judge.contracts import (
    Decision,
    Evidence,
    EvidenceKind,
    JudgeResult,
    JudgeSpec,
    JudgeType,
    RawScores,
    SuccessRubric,
    VerificationClass,
)


class ContractTests(unittest.TestCase):
    def test_evidence_is_secret_safe_and_immutable(self) -> None:
        evidence = Evidence(
            evidence_id="ev-1",
            kind=EvidenceKind.CANARY_MARKER,
            judge_id="canary.v0",
            detector_mode="pattern",
            confidence=0.7,
            verification_class=VerificationClass.HEURISTIC,
            matched_ref="marker-ref-1",
            locator="response[10:20]",
            redacted_summary="matched seeded marker reference",
            metadata={"span_count": 1},
        )

        self.assertEqual(evidence.confidence, 0.7)
        with self.assertRaises(TypeError):
            evidence.metadata["span_count"] = 2

    def test_evidence_rejects_raw_secret_metadata_keys(self) -> None:
        with self.assertRaises(ValueError):
            Evidence(
                evidence_id="ev-1",
                kind=EvidenceKind.CANARY_MARKER,
                judge_id="canary.v0",
                detector_mode="exact",
                confidence=1.0,
                metadata={"raw_canary": "do-not-store"},
            )

    def test_judge_spec_keeps_judges_replaceable(self) -> None:
        spec = JudgeSpec(
            judge_id="regex.v0",
            judge_type=JudgeType.REGEX,
            config={"patterns": ["safe-ref"]},
        )

        self.assertTrue(spec.enabled)
        self.assertEqual(spec.judge_type, JudgeType.REGEX)

    def test_rubric_scores_and_result_share_rubric_id(self) -> None:
        rubric = SuccessRubric(
            rubric_id="prompt_leakage",
            version="v1",
            goal="Detect prompt leakage signals",
            score_weights={"marker_exposure": 1.0},
            thresholds={Decision.REVIEW: 0.4},
            enabled_judges=("canary.v0", "regex.v0"),
        )
        scores = RawScores(
            rubric_id=rubric.rubric_id,
            scores={"marker_exposure": 0.5},
            evidence_ids=("ev-1",),
        )
        result = JudgeResult(
            result_id="jr-1",
            observation_ref="obs-1",
            rubric_id=rubric.rubric_id,
            decision=Decision.REVIEW,
            fitness=0.5,
            raw_scores=scores,
            reasons=("review threshold reached",),
        )

        self.assertEqual(result.decision, Decision.REVIEW)
        self.assertEqual(result.raw_scores.scores["marker_exposure"], 0.5)

    def test_result_rejects_rubric_mismatch(self) -> None:
        scores = RawScores(rubric_id="rubric-a", scores={"signal": 0.1})

        with self.assertRaises(ValueError):
            JudgeResult(
                result_id="jr-1",
                observation_ref="obs-1",
                rubric_id="rubric-b",
                decision=Decision.NO_SIGNAL,
                fitness=0.0,
                raw_scores=scores,
            )


if __name__ == "__main__":
    unittest.main()
