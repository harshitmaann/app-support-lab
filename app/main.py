import logging
import os
from fastapi import FastAPI
from app.config import load_settings

settings = load_settings()

# Ensure logs folder exists
os.makedirs(os.path.dirname(settings.log_path) or ".", exist_ok=True)

logger = logging.getLogger("app_support_lab")
logger.setLevel(logging.INFO)

fmt = logging.Formatter("%(asctime)s | %(levelname)s | ENV=%(message)s")

file_handler = logging.FileHandler(settings.log_path)
file_handler.setFormatter(fmt)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(fmt)
logger.addHandler(console_handler)

app = FastAPI(title="app-support-lab", version="0.1.0")

@app.get("/health")
def health():
    logger.info(f"{settings.env} | /health | ok")
    return {"status": "ok", "env": settings.env}