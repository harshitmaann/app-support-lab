import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    env: str
    log_path: str
    db_path: str
    simulate_db_down: bool
    simulate_slow: bool

def load_settings() -> Settings:
    env = os.getenv("APP_ENV", "dev").lower()
    log_path = os.getenv("LOG_PATH", "logs/app.log")

    default_db = {
        "dev": "app_dev.sqlite3",
        "staging": "app_staging.sqlite3",
        "prod": "app_prod.sqlite3",
    }.get(env, "app_dev.sqlite3")

    db_path = os.getenv("DB_PATH", default_db)
    simulate_db_down = os.getenv("SIMULATE_DB_DOWN", "0") == "1"
    simulate_slow = os.getenv("SIMULATE_SLOW", "0") == "1"

    return Settings(
        env=env,
        log_path=log_path,
        db_path=db_path,
        simulate_db_down=simulate_db_down,
        simulate_slow=simulate_slow,
    )