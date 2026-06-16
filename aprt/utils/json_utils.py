"""JSON output validation helpers."""

from typing import Any, Mapping

from aprt.utils.errors import InvalidRewardOutputError


def require_json_object(value: Any, source: str) -> Mapping[str, Any]:
    """Return a mapping or raise an invalid-output error."""

    if not isinstance(value, Mapping):
        raise InvalidRewardOutputError(f"{source} did not return a JSON object")
    return value


def require_score(payload: Mapping[str, Any], source: str) -> float:
    """Extract and validate a numeric score from a JSON object."""

    if "score" not in payload:
        raise InvalidRewardOutputError(f"{source} output is missing score")
    score = payload["score"]
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise InvalidRewardOutputError(f"{source} score is not numeric")
    score = float(score)
    if not 0.0 <= score <= 1.0:
        raise InvalidRewardOutputError(f"{source} score is out of range")
    return score


def require_label(payload: Mapping[str, Any], allowed: set[str], source: str) -> str:
    """Extract a constrained label from a JSON object."""

    if "label" not in payload:
        raise InvalidRewardOutputError(f"{source} output is missing label")
    label = payload["label"]
    if not isinstance(label, str) or label not in allowed:
        raise InvalidRewardOutputError(f"{source} label is invalid")
    return label
