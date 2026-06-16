"""Enums for APRT Reward Judge Core."""

from enum import Enum


class ExecutionStatus(str, Enum):
    """Target execution status observed outside the reward judge."""

    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    BLOCKED = "blocked"
    EMPTY_RESPONSE = "empty_response"


class RewardLabel(str, Enum):
    """Final reward quadrant label."""

    SAFE_UNHELPFUL = "safe_unhelpful"
    SAFE_HELPFUL = "safe_helpful"
    UNSAFE_UNHELPFUL = "unsafe_unhelpful"
    UNSAFE_HELPFUL = "unsafe_helpful"
    NO_SIGNAL = "no_signal"


class RewardStatus(str, Enum):
    """Reward evaluation status."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    EVALUATION_ERROR = "evaluation_error"
    INVALID_OUTPUT = "invalid_output"
