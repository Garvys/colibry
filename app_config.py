from pydantic_settings import BaseSettings
from pathlib import Path


class AppConfig(BaseSettings):
    library_path: Path = Path("/home/garvys/Documents/calibre-dashboard/library")
    debug: bool = True

    class Config:
        env_prefix = "CD_"


APP_CONFIG = AppConfig()
