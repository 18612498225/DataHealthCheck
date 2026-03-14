from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Default DB path: backend/app.db
_backend_dir = Path(__file__).resolve().parent.parent
_default_db = _backend_dir / "app.db"


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{_default_db.as_posix()}"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
