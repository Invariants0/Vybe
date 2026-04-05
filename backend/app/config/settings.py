import os


def _get_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() == "true"


class BaseConfig:
    APP_NAME = os.getenv("APP_NAME", "vybe-shortener")
    FLASK_DEBUG = _get_bool("FLASK_DEBUG")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

    DATABASE_NAME = os.getenv("DATABASE_NAME", "hackathon_db")
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = int(os.getenv("DATABASE_PORT", 5432))
    DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")
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
    REDIS_ENABLED = _get_bool("REDIS_ENABLED")
    REDIS_URL = os.getenv("REDIS_URL", "")
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


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config():
    environment = os.getenv("FLASK_ENV", "development").lower()
    if environment == "production":
        return ProductionConfig
    return DevelopmentConfig
