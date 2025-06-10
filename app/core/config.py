from pydantic import BaseSettings, HttpUrl
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    API_TOKEN: str
    DISCORD_WEBHOOK_URL: Optional[HttpUrl] = None
    BASIC_AUTH_USERNAME: str = "admin"
    BASIC_AUTH_PASSWORD: str = "password"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()