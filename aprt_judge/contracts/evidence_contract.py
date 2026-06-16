"""Evidence validation and policy contract."""

from dataclasses import dataclass, field


DEFAULT_FORBIDDEN_METADATA_KEYS = frozenset(
    {
        "secret",
        "plaintext_secret",
        "raw_secret",
        "canary",
        "raw_canary",
        "canary_value",
        "token",
    }
)


@dataclass(frozen=True, slots=True)
class EvidenceContract:
    """Policy knobs for evidence validation.

    This is intentionally small. Evidence must carry safe references and
    redacted summaries, not raw secrets or raw canary values.
    """

    forbidden_metadata_keys: frozenset[str] = field(
        default_factory=lambda: DEFAULT_FORBIDDEN_METADATA_KEYS
    )
    require_redacted_summary: bool = False
