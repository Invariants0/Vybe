import os


class BaseConfig:
    APP_NAME = os.getenv("APP_NAME", "vybe-shortener")
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
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
    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config():
    environment = os.getenv("FLASK_ENV", "development").lower()
    if environment == "production":
        return ProductionConfig
    return DevelopmentConfig
