from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Axithor Cloud OS"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    database_url: str = Field(alias="DATABASE_URL")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"], alias="BACKEND_CORS_ORIGINS")
    frontend_base_url: str = Field(default="http://localhost:3000", alias="FRONTEND_BASE_URL")
    backend_base_url: str = Field(default="http://localhost:8000", alias="BACKEND_BASE_URL")
    session_secret_key: str = Field(default="change-me", alias="SESSION_SECRET_KEY")
    google_client_id: str = Field(alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(alias="GOOGLE_CLIENT_SECRET")
    google_oauth_redirect_uri: str = Field(alias="GOOGLE_OAUTH_REDIRECT_URI")
    google_drive_redirect_uri: str = Field(default="http://localhost:8000/api/v1/storage/google/callback", alias="GOOGLE_DRIVE_REDIRECT_URI")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    access_token_cookie_name: str = Field(default="axithor_access", alias="ACCESS_TOKEN_COOKIE_NAME")
    refresh_token_cookie_name: str = Field(default="axithor_refresh", alias="REFRESH_TOKEN_COOKIE_NAME")

    # Module 4 — Subdomain routing
    base_domain: str = Field(default="axithor.tech", alias="BASE_DOMAIN")

    # Module 7 — Cloudflare
    cloudflare_api_token: str | None = Field(default=None, alias="CLOUDFLARE_API_TOKEN")
    cloudflare_zone_id: str | None = Field(default=None, alias="CLOUDFLARE_ZONE_ID")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
