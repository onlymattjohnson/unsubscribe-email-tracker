from typing import Optional

from pydantic import HttpUrl, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    API_TOKEN: str
    DISCORD_WEBHOOK_URL: Optional[HttpUrl] = None
    BASIC_AUTH_USERNAME: str = "admin"
    BASIC_AUTH_PASSWORD: str = "password"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()