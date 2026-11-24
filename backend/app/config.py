from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SEMICON_", extra="ignore")

    model_endpoint: str = ""
    model_api_token: str = ""
    model_timeout_seconds: float = 180.0


settings = Settings()
