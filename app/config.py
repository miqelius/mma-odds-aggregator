
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "MMA Betting Intelligence Hub"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mma_hub.db")
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "super-secure-production-random-key-change-me"
    )
    ADMIN_SETUP_TOKEN: str = os.getenv("ADMIN_SETUP_TOKEN", "secure-bootstrap-token")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
