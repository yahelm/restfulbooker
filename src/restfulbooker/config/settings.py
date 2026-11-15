from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    base_url: HttpUrl = HttpUrl("https://restful-booker.herokuapp.com")
    username: str = "admin"
    password: str = "strong_password"
    request_timeout: int = 5
    healthcheck_timeout: int = 30
