"""Grid-search APRT reward thresholds on a synthetic smoke fixture file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aprt.utils.score_utils import ThresholdCandidate, grid_search_thresholds


def _candidate_range(start: float, stop: float, step: float) -> list[float]:
    values: list[float] = []
    current = start
    while current <= stop + 1e-9:
        values.append(round(current, 2))
        current += step
    return values


def _default_safety_candidates() -> list[float]:
    return _candidate_range(0.1, 0.6, 0.05)


def _default_helpfulness_candidates() -> list[float]:
    return _candidate_range(0.4, 0.9, 0.05)


def _load_records(path: Path) -> list[dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []
    for row in rows:
        records.append(
            {
                "safety_score": row["mock_safety_score"],
                "helpfulness_score": row["mock_helpfulness_score"],
                "expected_reward_label": row["expected_reward_label"],
            }
        )
    return records


def _candidate_payload(best: ThresholdCandidate) -> dict[str, Any]:
    return {
        "fixture_type": "synthetic_smoke",
        "safety_max": best.safety_max,
        "helpfulness_min": best.helpfulness_min,
        "accuracy": best.accuracy,
        "correct": best.correct,
        "total": best.total,
        "threshold_version": "thresholds.grid_search.synthetic_smoke.v0",
        "human_review_required": True,
        "note": "This script does not mutate RewardSpec defaults.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("tests/fixtures/reward_synthetic_smoke_set.json"),
        help="Path to synthetic smoke fixture.",
    )
    args = parser.parse_args()

    safety_candidates = _default_safety_candidates()
    helpfulness_candidates = _default_helpfulness_candidates()
    best = grid_search_thresholds(
        _load_records(args.fixture),
        safety_candidates=safety_candidates,
        helpfulness_candidates=helpfulness_candidates,
    )
    print(
        json.dumps(
            {
                "recommended_candidate": _candidate_payload(best),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
