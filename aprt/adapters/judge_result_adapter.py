"""Adapters from RewardResult to external result payloads.

The Reward Judge Core does not own selector, active learning, or archive
decisions. These adapters only reshape RewardResult so external teams can
consume the scores and label without deriving downstream training signals.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from aprt.contracts import RewardResult
from aprt.utils.errors import RewardError

ADAPTER_SCHEMA_VERSION = "reward_result_adapter.v1"


def _enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


def _error_to_dict(error: RewardError | None) -> dict[str, Any] | None:
    if error is None:
        return None
    return {
        "code": error.code,
        "message": error.message,
        "details": dict(error.details),
    }


def reward_result_to_external_dict(result: RewardResult) -> dict[str, Any]:
    """Convert RewardResult to the canonical external handoff dictionary."""

    return {
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "result_type": "reward_result",
        "observation_id": result.observation_id,
        "attack_id": result.attack_id,
        "attempt_id": result.attempt_id,
        "safety_score": result.safety_score,
        "helpfulness_score": result.helpfulness_score,
        "reward_label": _enum_value(result.reward_label),
        "status": _enum_value(result.status),
        "raw_outputs": dict(result.raw_outputs),
        "metadata": dict(result.metadata),
        "error": _error_to_dict(result.error),
    }


def reward_result_to_judge_result_like(result: RewardResult) -> dict[str, Any]:
    """Convert RewardResult to a minimal legacy JudgeResult-like dictionary."""

    payload = reward_result_to_external_dict(result)
    return {
        "schema_version": "legacy_judge_result_like.v1",
        "result_type": "judge_result_like",
        "observation_id": payload["observation_id"],
        "attack_id": payload["attack_id"],
        "attempt_id": payload["attempt_id"],
        "scores": {
            "safety": payload["safety_score"],
            "helpfulness": payload["helpfulness_score"],
        },
        "reward_label": payload["reward_label"],
        "status": payload["status"],
        "metadata": payload["metadata"],
        "raw_outputs": payload["raw_outputs"],
        "error": payload["error"],
    }


def reward_results_to_external_dicts(results: Iterable[RewardResult]) -> list[dict[str, Any]]:
    """Convert a batch of RewardResult objects for external batch consumers."""

    return [reward_result_to_external_dict(result) for result in results]
