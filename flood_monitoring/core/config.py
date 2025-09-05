"""
Konfiguracja aplikacji
"""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Flood Monitoring System"

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/flood_monitoring"

    IMGW_API_URL: str = "https://danepubliczne.imgw.pl/api/data/hydro/"
    IMGW_WARNINGS_URL:str = "https://danepubliczne.imgw.pl/api/data/warningshydro"

    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
