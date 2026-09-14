"""Secret redaction for diagnostic data."""

import re

REDACTED = "[REDACTED]"

SENSITIVE_FIELD_NAMES = frozenset(
    {
        "access_token",
        "api_key",
        "api_token",
        "authorization",
        "auth_token",
        "bot_token",
        "database_url",
        "github_token",
        "openai_api_key",
        "password",
        "passwd",
        "pwd",
        "secret",
        "telegram_token",
        "token",
    }
)

PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----.*?-----END (?:[A-Z0-9 ]+ )?PRIVATE KEY-----",
    re.DOTALL,
)
DATABASE_URL_PATTERN = re.compile(
    r"(?P<scheme>\b[a-z][a-z0-9+.-]*://)(?P<username>[^:/\s]+):(?P<password>[^@/\s]+)@",
    re.IGNORECASE,
)
AUTHORIZATION_PATTERN = re.compile(
    r"(?P<prefix>\b(?:authorization|proxy-authorization)\s*:\s*(?:bearer|basic)\s+)(?P<secret>[^\s,;]+)",
    re.IGNORECASE,
)
BEARER_PATTERN = re.compile(r"(?P<prefix>\bbearer\s+)(?P<secret>[^\s,;]+)", re.IGNORECASE)
GITHUB_TOKEN_PATTERN = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
)
OPENAI_KEY_PATTERN = re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{8,}\b")
TELEGRAM_TOKEN_PATTERN = re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{20,}\b")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    (?P<name>[a-z0-9_-]*(?:api[_-]?key|api[_-]?token|access[_-]?token|password|passwd|secret|token)[a-z0-9_-]*)
    (?P<before>\s*)(?P<separator>[:=])(?P<after>\s*)
    (?P<quote>[\"']?)(?P<secret>[^\s,;'\"`}]+)(?P=quote)
    """
)


def redact_text(value: str) -> str:
    """Replace supported secrets in a text value."""
    redacted = PRIVATE_KEY_PATTERN.sub(REDACTED, value)
    redacted = DATABASE_URL_PATTERN.sub(_replace_database_url, redacted)
    redacted = AUTHORIZATION_PATTERN.sub(_replace_prefixed_secret, redacted)
    redacted = BEARER_PATTERN.sub(_replace_prefixed_secret, redacted)
    redacted = GITHUB_TOKEN_PATTERN.sub(REDACTED, redacted)
    redacted = OPENAI_KEY_PATTERN.sub(REDACTED, redacted)
    redacted = TELEGRAM_TOKEN_PATTERN.sub(REDACTED, redacted)
    return SECRET_ASSIGNMENT_PATTERN.sub(_replace_secret_assignment, redacted)


def redact_data(value: object) -> object:
    """Recursively redact string values and sensitive mapping fields."""
    if isinstance(value, dict):
        return {
            key: REDACTED if _is_sensitive_field(key) else redact_data(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_data(item) for item in value)
    if isinstance(value, str):
        return redact_text(value)
    return value


def _is_sensitive_field(value: object) -> bool:
    """Return whether a mapping key represents a secret field."""
    return isinstance(value, str) and value.lower().replace("-", "_") in SENSITIVE_FIELD_NAMES


def _replace_database_url(match: re.Match[str]) -> str:
    """Keep database scheme and username while hiding the password."""
    return f"{match.group('scheme')}{match.group('username')}:{REDACTED}@"


def _replace_prefixed_secret(match: re.Match[str]) -> str:
    """Keep an authorization prefix while hiding its credential."""
    return f"{match.group('prefix')}{REDACTED}"


def _replace_secret_assignment(match: re.Match[str]) -> str:
    """Keep a secret field name and separator while hiding its value."""
    return "".join(
        (
            match.group("name"),
            match.group("before"),
            match.group("separator"),
            match.group("after"),
            REDACTED,
        )
    )
