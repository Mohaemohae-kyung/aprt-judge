"""Shared enums for Judge/QC contracts."""

from enum import Enum


class JudgeType(str, Enum):
    """Known judge families for v0 routing."""

    CANARY = "canary"
    REGEX = "regex"
    CLASSIFIER = "classifier"
    LLM = "llm"


class EvidenceKind(str, Enum):
    """Kinds of evidence that judges can emit."""

    CANARY_MARKER = "canary_marker"
    REGEX_MATCH = "regex_match"
    CLASSIFIER_SIGNAL = "classifier_signal"
    LLM_REVIEW = "llm_review"


class VerificationClass(str, Enum):
    """How strongly an evidence item has been verified."""

    DETECTED = "detected"
    HEURISTIC = "heuristic"
    MODEL_ASSISTED = "model_assisted"
    HUMAN_REVIEWED = "human_reviewed"


class Decision(str, Enum):
    """Final routing decisions produced by DecisionRouter."""

    NO_SIGNAL = "no_signal"
    REVIEW = "review"
    FINDING_CANDIDATE = "finding_candidate"
