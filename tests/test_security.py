"""Tests for secret redaction."""

import pytest

from repropack.security import REDACTED, redact_data, redact_text


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("API_KEY=example-secret", "API_KEY=[REDACTED]"),
        ("password: correct-horse", "password: [REDACTED]"),
        ("Authorization: Bearer bearer-secret", "Authorization: Bearer [REDACTED]"),
        ("Authorization: Basic c2VjcmV0", "Authorization: Basic [REDACTED]"),
        ("ghp_abcdefghijklmnopqrstuvwxyz1234567890", "[REDACTED]"),
        ("sk-proj-abcdefghijklmnopqrstuvwxyz123456", "[REDACTED]"),
        ("123456789:AAAbbbcccdddeeefffggghhhiiijjjkkk", "[REDACTED]"),
        (
            "postgresql://reporter:correct-horse-battery@db.example.com/repro",
            "postgresql://reporter:[REDACTED]@db.example.com/repro",
        ),
        (
            "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----",
            "[REDACTED]",
        ),
    ],
)
def test_redact_text_replaces_supported_secret_formats(value: str, expected: str) -> None:
    """Supported secret formats are replaced without exposing their values."""
    assert redact_text(value) == expected


def test_redact_text_keeps_safe_text_unchanged() -> None:
    """Ordinary diagnostic text remains useful to the report reader."""
    assert redact_text("branch=main") == "branch=main"


def test_redact_data_uses_sensitive_mapping_keys_and_recurses() -> None:
    """Nested report data is redacted even when a secret is stored as a field value."""
    value = {
        "api_key": "plain-secret",
        "nested": [{"authorization": "Bearer nested-secret"}],
        "safe": "branch=main",
    }

    assert redact_data(value) == {
        "api_key": REDACTED,
        "nested": [{"authorization": REDACTED}],
        "safe": "branch=main",
    }
