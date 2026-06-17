"""JSON output validation helpers."""

from typing import Any, Mapping

from aprt.utils.errors import InvalidRewardOutputError

REWARD_OUTPUT_KEYS = {"score", "label", "reason"}


def require_json_object(value: Any, source: str) -> Mapping[str, Any]:
    """Return a mapping or raise an invalid-output error."""

    if not isinstance(value, Mapping):
        raise InvalidRewardOutputError(
            f"{source} did not return a strict JSON object",
            code="invalid_json",
        )
    return value


def require_reward_output_schema(payload: Mapping[str, Any], source: str) -> None:
    """Require the strict reward output schema used by Rs/Rh."""

    keys = set(payload)
    missing = REWARD_OUTPUT_KEYS - keys
    if missing:
        first = sorted(missing)[0]
        raise InvalidRewardOutputError(
            f"{source} output is missing {first}",
            code=f"missing_{first}",
        )
    extra = keys - REWARD_OUTPUT_KEYS
    if extra:
        first = sorted(extra)[0]
        raise InvalidRewardOutputError(
            f"{source} output has unexpected key {first}",
            code="unexpected_key",
        )
    if not isinstance(payload["reason"], str):
        raise InvalidRewardOutputError(
            f"{source} reason is not a string",
            code="invalid_reason_type",
        )


def require_score(payload: Mapping[str, Any], source: str) -> float:
    """Extract and validate a numeric score from a JSON object."""

    if "score" not in payload:
        raise InvalidRewardOutputError(f"{source} output is missing score", code="missing_score")
    score = payload["score"]
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise InvalidRewardOutputError(f"{source} score is not numeric", code="invalid_score_type")
    score = float(score)
    if not 0.0 <= score <= 1.0:
        raise InvalidRewardOutputError(f"{source} score is out of range", code="score_out_of_range")
    return score


def require_label(payload: Mapping[str, Any], allowed: set[str], source: str) -> str:
    """Extract a constrained label from a JSON object."""

    if "label" not in payload:
        raise InvalidRewardOutputError(f"{source} output is missing label", code="missing_label")
    label = payload["label"]
    if not isinstance(label, str) or label not in allowed:
        raise InvalidRewardOutputError(f"{source} label is invalid", code="invalid_label")
    return label
