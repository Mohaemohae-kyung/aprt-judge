"""Grid-search APRT reward thresholds on a synthetic/gold fixture file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aprt.utils.score_utils import grid_search_thresholds


def _candidate_range() -> list[float]:
    return [round(index / 10, 2) for index in range(1, 10)]


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("tests/fixtures/reward_gold_set.json"),
        help="Path to reward gold set fixture.",
    )
    args = parser.parse_args()

    best = grid_search_thresholds(
        _load_records(args.fixture),
        safety_candidates=_candidate_range(),
        helpfulness_candidates=_candidate_range(),
    )
    print(
        json.dumps(
            {
                "safety_max": best.safety_max,
                "helpfulness_min": best.helpfulness_min,
                "accuracy": best.accuracy,
                "correct": best.correct,
                "total": best.total,
                "threshold_version": "thresholds.grid_search.synthetic.v0",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
