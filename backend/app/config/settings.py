import os
from urllib.parse import urlparse


def _get_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() == "true"


def _parse_database_url():
    """Parse DATABASE_URL into individual components. Falls back to individual env vars."""
    database_url = os.getenv("DATABASE_URL", "")
    if database_url:
        parsed = urlparse(database_url)
        return {
            "name": (parsed.path or "/hackathon_db").lstrip("/"),
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 5432,
            "user": parsed.username or "postgres",
            "password": parsed.password or "postgres",
        }
    return {
        "name": os.getenv("DATABASE_NAME", "hackathon_db"),
        "host": os.getenv("DATABASE_HOST", "localhost"),
        "port": int(os.getenv("DATABASE_PORT", 5432)),
        "user": os.getenv("DATABASE_USER", "postgres"),
        "password": os.getenv("DATABASE_PASSWORD", "postgres"),
    }


_db = _parse_database_url()


class BaseConfig:
    APP_NAME = os.getenv("APP_NAME", "vybe-shortener")
    FLASK_DEBUG = _get_bool("FLASK_DEBUG")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

    DATABASE_NAME = _db["name"]
    DATABASE_HOST = _db["host"]
    DATABASE_PORT = int(_db["port"])
    DATABASE_USER = _db["user"]
    DATABASE_PASSWORD = _db["password"]
    DB_MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS", 20))
    DB_STALE_TIMEOUT_SECONDS = int(os.getenv("DB_STALE_TIMEOUT_SECONDS", 300))
    DB_CONNECTION_TIMEOUT_SECONDS = int(os.getenv("DB_CONNECTION_TIMEOUT_SECONDS", 10))

    DEFAULT_SHORT_CODE_LENGTH = int(os.getenv("DEFAULT_SHORT_CODE_LENGTH", 7))
    MAX_CUSTOM_ALIAS_LENGTH = int(os.getenv("MAX_CUSTOM_ALIAS_LENGTH", 32))
    MAX_URL_LENGTH = int(os.getenv("MAX_URL_LENGTH", 2048))
    DEFAULT_REDIRECT_STATUS_CODE = int(os.getenv("DEFAULT_REDIRECT_STATUS_CODE", 302))
    AUTO_CREATE_TABLES = _get_bool("AUTO_CREATE_TABLES")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")
    REDIS_URL = os.getenv("REDIS_URL", "")
    REDIS_ENABLED = _get_bool("REDIS_ENABLED") if not REDIS_URL else True
    REDIS_DEFAULT_TTL_SECONDS = int(os.getenv("REDIS_DEFAULT_TTL_SECONDS", 300))
    REDIS_RETRY_ATTEMPTS = int(os.getenv("REDIS_RETRY_ATTEMPTS", 3))
    REDIS_RETRY_BACKOFF_SECONDS = float(os.getenv("REDIS_RETRY_BACKOFF_SECONDS", 0.05))
    EVENT_LOG_SAMPLE_RATE = float(os.getenv("EVENT_LOG_SAMPLE_RATE", 1.0))
    AUTH_ENABLED = _get_bool("AUTH_ENABLED")
    API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")
    API_AUTH_TOKENS = os.getenv("API_AUTH_TOKENS", "")
    RATE_LIMIT_ENABLED = _get_bool("RATE_LIMIT_ENABLED", "true")
    RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "500 per minute")
    RATE_LIMIT_WRITE = os.getenv("RATE_LIMIT_WRITE", "120 per minute")
    EXPOSE_ERROR_DETAILS = _get_bool("EXPOSE_ERROR_DETAILS")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config():
    environment = os.getenv("FLASK_ENV", "development").lower()
    if environment == "production":
        return ProductionConfig
    return DevelopmentConfig
