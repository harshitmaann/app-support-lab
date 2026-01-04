import logging
import os
from fastapi import FastAPI, Response
from app.config import load_settings
from app.db import init_db, fetch_sample

settings = load_settings()

# Ensure logs folder exists
os.makedirs(os.path.dirname(settings.log_path) or ".", exist_ok=True)

logger = logging.getLogger("app_support_lab")
logger.setLevel(logging.INFO)

fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

file_handler = logging.FileHandler(settings.log_path)
file_handler.setFormatter(fmt)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(fmt)
logger.addHandler(console_handler)

app = FastAPI(title="app-support-lab", version="0.2.0")

@app.on_event("startup")
def startup():
    init_db(settings.db_path)
    logger.info(f"ENV={settings.env} | Startup complete | DB={settings.db_path}")

@app.get("/health")
def health():
    logger.info(f"ENV={settings.env} | /health | ok")
    return {"status": "ok", "env": settings.env}

@app.get("/api/data")
def api_data():
    # Incident simulation: DB down
    if settings.simulate_db_down:
        logger.error(f"ENV={settings.env} | /api/data | 503 | Simulated DB down")
        return Response(content="Database unavailable (simulated)", status_code=503)

    ok, rows, err = fetch_sample(settings.db_path)
    if not ok:
        logger.error(f"ENV={settings.env} | /api/data | 500 | DB error: {err}")
        return Response(content=f"DB error: {err}", status_code=500)

    logger.info(f"ENV={settings.env} | /api/data | 200 | rows={len(rows)}")
    return {"env": settings.env, "count": len(rows), "data": rows}