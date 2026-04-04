from datetime import datetime, timezone
from urllib.parse import urlparse

from backend.app.config import ValidationError


def normalize_url(url, max_length=2048):
    if not isinstance(url, str) or not url.strip():
        raise ValidationError("url is required.")

    candidate = url.strip()
    if len(candidate) > max_length:
        raise ValidationError(f"url must be at most {max_length} characters.")

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("url must start with http:// or https://.")
    if not parsed.netloc:
        raise ValidationError("url must include a valid hostname.")
    return candidate


def parse_expiration(expires_at):
    if expires_at in (None, ""):
        return None

    try:
        normalized = expires_at.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationError("expires_at must be a valid ISO 8601 datetime.") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    if parsed <= datetime.now(timezone.utc):
        raise ValidationError("expires_at must be in the future.")
    return parsed
