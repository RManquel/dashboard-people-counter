from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://stadium:stadium@localhost:5432/stadium_db"

    # CORS
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:80", "http://localhost"]

    # MQTT (optional)
    mqtt_broker_url: str = ""
    mqtt_port: int = 1883
    mqtt_topic: str = "stadium/gate/events"

    # App
    app_env: str = "development"
    log_level: str = "info"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
