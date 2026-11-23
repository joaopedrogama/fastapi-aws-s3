from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    s3_external_port: str
    s3_access_key: str
    s3_secret_key: str
    s3_endpoint_url: str
    bucket_name: str

    model_config = SettingsConfigDict(env_file="/app/.env")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
