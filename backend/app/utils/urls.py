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

    # SSRF Protection: Block internal and private IPv4 ranges
    netloc = parsed.netloc.lower()
    hostname = netloc.split(":")[0]

    # Block literal localhost
    if hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        raise ValidationError("url points to a restricted internal domain.")

    # Basic rudimentary block for private/internal IPv4 address spaces
    if (
        hostname.startswith("10.")
        or hostname.startswith("192.168.")
        or hostname.startswith("169.254.")
    ):
        raise ValidationError("url points to a restricted internal IP address.")
    if hostname.startswith("172."):
        # Check 172.16.0.0 - 172.31.255.255
        try:
            second_octet = int(hostname.split(".")[1])
            if 16 <= second_octet <= 31:
                raise ValidationError("url points to a restricted internal IP address.")
        except (IndexError, ValueError):
            pass

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
