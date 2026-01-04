import logging
import os
import time
from fastapi import FastAPI, Response
from app.config import load_settings
from app.db import init_db, fetch_sample

settings = load_settings()

# Ensure logs folder exists
os.makedirs(os.path.dirname(settings.log_path) or ".", exist_ok=True)

logger = logging.getLogger("app_support_lab")
logger.setLevel(logging.INFO)

fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

# Avoid duplicate handlers on reload
if not logger.handlers:
    file_handler = logging.FileHandler(settings.log_path)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

app = FastAPI(title="app-support-lab", version="0.4.0")

# Simple in-memory metrics (good enough for a lab)
METRICS = {
    "requests_total": 0,
    "errors_total": 0,
    "slow_responses_total": 0,
}

@app.on_event("startup")
def startup():
    init_db(settings.db_path)
    logger.info(f"ENV={settings.env} | Startup complete | DB={settings.db_path}")

@app.get("/health")
def health():
    METRICS["requests_total"] += 1
    logger.info(f"ENV={settings.env} | /health | ok")
    return {"status": "ok", "env": settings.env}

@app.get("/api/data")
def api_data():
    METRICS["requests_total"] += 1

    # Incident simulation: DB down
    if settings.simulate_db_down:
        METRICS["errors_total"] += 1
        logger.error(f"ENV={settings.env} | /api/data | 503 | Simulated DB down")
        return Response(content="Database unavailable (simulated)", status_code=503)

    # Incident simulation: Slow response
    if settings.simulate_slow:
        METRICS["slow_responses_total"] += 1
        delay_s = 3
        time.sleep(delay_s)
        logger.warning(f"ENV={settings.env} | /api/data | 200 | Simulated slow response ({delay_s}s)")

    ok, rows, err = fetch_sample(settings.db_path)
    if not ok:
        METRICS["errors_total"] += 1
        logger.error(f"ENV={settings.env} | /api/data | 500 | DB error: {err}")
        return Response(content=f"DB error: {err}", status_code=500)

    logger.info(f"ENV={settings.env} | /api/data | 200 | rows={len(rows)}")
    return {"env": settings.env, "count": len(rows), "data": rows}

@app.get("/metrics")
def metrics():
    METRICS["requests_total"] += 1

    # Prometheus-style plaintext
    content = (
        "# HELP app_requests_total Total HTTP requests\n"
        "# TYPE app_requests_total counter\n"
        f"app_requests_total {METRICS['requests_total']}\n"
        "# HELP app_errors_total Total application errors\n"
        "# TYPE app_errors_total counter\n"
        f"app_errors_total {METRICS['errors_total']}\n"
        "# HELP app_slow_responses_total Total simulated slow responses\n"
        "# TYPE app_slow_responses_total counter\n"
        f"app_slow_responses_total {METRICS['slow_responses_total']}\n"
    )
    return Response(content=content, media_type="text/plain")