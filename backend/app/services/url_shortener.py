from datetime import datetime, timezone

from peewee import DoesNotExist, IntegrityError

from backend.app.config import ConflictError, NotFoundError, ValidationError
from backend.app.models import LinkVisit, ShortURL
from backend.app.utils.codecs import generate_short_code
from backend.app.utils.urls import normalize_url, parse_expiration


class URLShortenerService:
    def __init__(self, config):
        self.config = config

    def create_short_url(self, original_url, custom_alias=None, expires_at=None, creator_ip=None):
        normalized_url = normalize_url(original_url, max_length=self.config["MAX_URL_LENGTH"])
        code = self._get_code(custom_alias)
        expiration = parse_expiration(expires_at)

        try:
            short_url = ShortURL.create(
                code=code,
                original_url=normalized_url,
                expires_at=expiration,
                creator_ip=creator_ip,
            )
        except IntegrityError as exc:
            raise ConflictError("Short code already exists. Retry the request.") from exc
        return self._serialize_short_url(short_url)

    def get_short_url_stats(self, code):
        short_url = self._get_short_url(code)
        return self._serialize_short_url(short_url, include_visit_count=True)

    def get_recent_visits(self, code, limit=25):
        short_url = self._get_short_url(code)
        query = (
            LinkVisit.select()
            .where(LinkVisit.short_url == short_url)
            .order_by(LinkVisit.accessed_at.desc())
            .limit(limit)
        )
        return [
            {
                "id": visit.id,
                "ip_address": visit.ip_address,
                "user_agent": visit.user_agent,
                "referer": visit.referer,
                "accessed_at": visit.accessed_at.isoformat(),
            }
            for visit in query
        ]

    def update_short_url(self, code, is_active=None, expires_at=None):
        short_url = self._get_short_url(code)
        if is_active is not None:
            short_url.is_active = is_active
        if expires_at is not None:
            short_url.expires_at = parse_expiration(expires_at)
        short_url.save()
        return self._serialize_short_url(short_url, include_visit_count=True)

    def deactivate_short_url(self, code):
        short_url = self._get_short_url(code)
        short_url.is_active = False
        short_url.save()

    def resolve_redirect(self, code, ip_address=None, user_agent=None, referer=None):
        short_url = self._get_short_url(code)

        if not short_url.is_active:
            raise NotFoundError("This short link is inactive.")
        if short_url.expires_at and short_url.expires_at <= datetime.now(timezone.utc):
            raise NotFoundError("This short link has expired.")

        (
            ShortURL.update(
                click_count=ShortURL.click_count + 1,
                last_accessed_at=datetime.now(timezone.utc),
            )
            .where(ShortURL.id == short_url.id)
            .execute()
        )
        LinkVisit.create(
            short_url=short_url,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
        )
        return short_url.original_url

    def _get_short_url(self, code):
        try:
            return ShortURL.get(ShortURL.code == code)
        except DoesNotExist as exc:
            raise NotFoundError("Short link was not found.") from exc

    def _get_code(self, custom_alias):
        reserved_codes = {"api", "health", "healthz", "ready", "favicon.ico"}
        if custom_alias:
            code = custom_alias.strip()
            if len(code) > self.config["MAX_CUSTOM_ALIAS_LENGTH"]:
                raise ValidationError(
                    f"custom_alias must be at most {self.config['MAX_CUSTOM_ALIAS_LENGTH']} characters."
                )
            if not code.replace("-", "").replace("_", "").isalnum():
                raise ValidationError("custom_alias may contain only letters, numbers, hyphens, and underscores.")
            if code in reserved_codes:
                raise ValidationError("custom_alias conflicts with a reserved application route.")
            if ShortURL.select().where(ShortURL.code == code).exists():
                raise ConflictError("custom_alias is already in use.")
            return code

        for _ in range(10):
            code = generate_short_code(self.config["DEFAULT_SHORT_CODE_LENGTH"])
            if not ShortURL.select().where(ShortURL.code == code).exists():
                return code
        raise ConflictError("Could not generate a unique short code. Retry the request.")

    def _serialize_short_url(self, short_url, include_visit_count=False):
        payload = {
            "id": short_url.id,
            "code": short_url.code,
            "short_url": f"{self.config['BASE_URL']}/{short_url.code}",
            "original_url": short_url.original_url,
            "is_active": short_url.is_active,
            "click_count": short_url.click_count,
            "created_at": short_url.created_at.isoformat(),
            "updated_at": short_url.updated_at.isoformat(),
            "expires_at": short_url.expires_at.isoformat() if short_url.expires_at else None,
            "last_accessed_at": short_url.last_accessed_at.isoformat() if short_url.last_accessed_at else None,
        }
        if include_visit_count:
            payload["visit_count"] = LinkVisit.select().where(LinkVisit.short_url == short_url).count()
        return payload
