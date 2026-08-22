from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    debug: bool = False

    database_url: str = "postgresql+asyncpg://agrovision:agrovision@localhost:5432/agrovision"

    jwt_secret: str = "change-me-in-.env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    media_root: str = "media"
    max_upload_size_bytes: int = 15 * 1024 * 1024
    max_video_upload_size_bytes: int = 200 * 1024 * 1024

    cors_origins: list[str] = ["http://localhost:5173"]

    # Only consumed by app/seed.py when creating these accounts for the first
    # time; changing this later does not retroactively change existing passwords.
    seed_admin_password: str = "change-me-admin"
    seed_moderator_password: str = "change-me-moderator"
    seed_student_password: str = "change-me-student"

    # Base URL used to build links inside emails (password reset, etc).
    frontend_url: str = "http://localhost:5173"

    # SMTP is optional: when smtp_host is empty, outgoing emails are logged to
    # the backend console instead of sent (dev-friendly default).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "no-reply@agrovision.ru"
    smtp_use_tls: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
