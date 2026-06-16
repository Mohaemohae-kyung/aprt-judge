"""Evidence emitted by judges."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from aprt_judge.contracts.enums import EvidenceKind, VerificationClass
from aprt_judge.contracts.evidence_contract import DEFAULT_FORBIDDEN_METADATA_KEYS


def _immutable_metadata(metadata: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(metadata))


@dataclass(frozen=True, slots=True)
class Evidence:
    """A secret-safe signal produced by a judge.

    Evidence stores safe references and redacted summaries only. Plaintext
    secrets and raw canary values belong outside this contract.
    """

    evidence_id: str
    kind: EvidenceKind
    judge_id: str
    detector_mode: str
    confidence: float
    verification_class: VerificationClass = VerificationClass.DETECTED
    matched_ref: str | None = None
    locator: str | None = None
    redacted_summary: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("evidence_id is required")
        if not self.judge_id:
            raise ValueError("judge_id is required")
        if not self.detector_mode:
            raise ValueError("detector_mode is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        forbidden = DEFAULT_FORBIDDEN_METADATA_KEYS.intersection(self.metadata)
        if forbidden:
            names = ", ".join(sorted(forbidden))
            raise ValueError(f"metadata contains forbidden raw value keys: {names}")

        object.__setattr__(self, "metadata", _immutable_metadata(self.metadata))
