import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    env: str
    log_path: str

def load_settings() -> Settings:
    env = os.getenv("APP_ENV", "dev").lower()
    log_path = os.getenv("LOG_PATH", "logs/app.log")
    return Settings(env=env, log_path=log_path)