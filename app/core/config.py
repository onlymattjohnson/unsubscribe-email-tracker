from typing import Optional

from pydantic import HttpUrl, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    API_TOKEN: str
    DISCORD_WEBHOOK_URL: Optional[HttpUrl] = None
    BASIC_AUTH_USERNAME: str = "admin"
    BASIC_AUTH_PASSWORD: str = "password"
    TEST_DATABASE_URL: Optional[str] = None
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 20
    RATE_LIMIT_AUTH_REQUESTS: int = 100
    RATE_LIMIT_TIMESCALE_SECONDS: int = 60  # 1 minute

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
