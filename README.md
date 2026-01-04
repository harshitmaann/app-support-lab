# app-support-lab

A simulated production **Application Support** environment built with **FastAPI + SQLite**, complete with **logging**, **metrics**, and **monitoring scripts** to practice real-world incident response.

This lab mirrors the day-to-day work of an **Applications Support Specialist**:
- Monitor service health and metrics
- Investigate errors via logs
- Validate endpoints and recover from incidents
- Document troubleshooting and resolution steps

---

## What This Repo Demonstrates (Why it matters for App Support)
✅ Uptime validation (`/health`, `/api/data`)  
✅ Log-based troubleshooting (`logs/app.log`)  
✅ Metrics inspection (`/metrics`)  
✅ Incident simulation (DB down / slow responses via environment flags)  
✅ Monitoring + alerting (polling + log scanning scripts)  
✅ Repeatable “runbook-style” workflows  

---

## Architecture

```text
         +---------------------------+
         |        Monitoring         |
         |  monitoring/log_monitor.py|
         |  (scans logs periodically)|
         +-------------+-------------+
                       | reads logs
                       v
+--------------------------------------------------+
|                    FastAPI App                   |
|  Endpoints: /health  /api/data  /metrics         |
|  Logs: logs/app.log                              |
|  Incident toggles via environment variables       |
+-------------------------+------------------------+
                          | reads/writes
                          v
                   +-------------+
                   |  SQLite DB  |
                   | app_dev...  |
                   +-------------+

```
---

## Tech Stack
- **API:** FastAPI + Uvicorn
- **DB:** SQLite (local)
- **Observability:** structured file logs + Prometheus-style metrics at `/metrics`
- **Monitoring:** lightweight polling + log scanning scripts

---

## Repository Structure
```text
app-support-lab/
├─ app/
│  └─ main.py                 # FastAPI service (health, data, metrics)
├─ monitoring/
│  └─ log_monitor.py          # Scans logs & alerts on thresholds
├─ logs/
│  └─ .gitkeep               # Keeps folder in repo (app writes logs/app.log at runtime)
├─ requirements.txt
└─ README.md
```
Tip: keep the `logs/` folder tracked (via `logs/.gitkeep`), but do not commit `logs/app.log` (see .gitignore section below).

---

## Quick Start (2-Minute Setup)

1) Clone + venv + install
```bash
git clone https://github.com/harshitmaann/app-support-lab.git
cd app-support-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Create logs folder + reset log file
```bash
mkdir -p logs
: > logs/app.log
```

3) Run the API (Tab 1)
```bash
uvicorn app.main:app --reload
```

4) Verify endpoints (Tab 2 or scratch tab)
```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/api/data
curl -s http://127.0.0.1:8000/metrics | egrep "app_requests_total|app_errors_total|app_slow_responses_total"
```

Expected:
- `/api/data` returns **200** and JSON data
- `app_requests_total` increases
- `app_errors_total` stays at **0** (during healthy state)

---

## Monitoring (Log Alerting)

Run the log monitor in a dedicated terminal (Tab 2):
```bash
source .venv/bin/activate
python monitoring/log_monitor.py
```

It will:
- Read `logs/app.log`
- Keep a rolling window of recent lines
- Alert when thresholds are exceeded

Configure via environment variables (optional)
```bash
export LOG_PATH=logs/app.log
export ERROR_THRESHOLD=2
export SLOW_THRESHOLD=1
export INTERVAL_SECONDS=5
export WINDOW_LINES=250
# export HEARTBEAT_SECONDS=30   # optional
python monitoring/log_monitor.py
```


---

## Incident Drills (Runbook-Style)

These drills are designed to simulate realistic incidents and show your troubleshooting workflow.

Drill A — Simulate DB Down (503 errors)

Goal: /api/data returns 503 and logs show “Simulated DB down”. Monitor should alert.

### Step 1: Stop the API (Tab 1)
Press:

Ctrl+C

### Step 2: Clear logs (scratch tab)
```bash
: > logs/app.log
```

### Step 3: Start API with DB-down simulation (Tab 1)
```bash
SIMULATE_DB_DOWN=1 uvicorn app.main:app --reload
```

### Step 4: Trigger traffic (scratch tab)
```bash
for i in {1..5}; do curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/data; done
```

Expected:
- Output shows 503 five times

### Step 5: Confirm logs (scratch tab)
```bash
tail -n 30 logs/app.log | egrep "/api/data|Simulated DB down|ERROR"
```

Expected:
- log lines include 503 | Simulated DB down

### Step 6: Monitor alerts (Tab 2)
Expected:
- [ALERT] ... ERROR threshold exceeded ...

### Step 7: Verify metrics (scratch tab)
```bash
curl -s http://127.0.0.1:8000/metrics | egrep "app_requests_total|app_errors_total"
```

Expected:
- app_errors_total increases

---

## Drill B — Recover from DB Down (back to healthy 200)

Goal: remove incident toggle, restart, verify recovery.

### Step 1: Stop API (Tab 1)

Ctrl+C

### Step 2: Clear logs (scratch tab)
```bash
: > logs/app.log
```

### Step 3: Start API normally (Tab 1)
```bash
uvicorn app.main:app --reload
```

### Step 4: Validate recovery (scratch tab)
```bash
for i in {1..5}; do curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/data; done
```

Expected:
- Output shows 200 five times

### Step 5: Confirm monitor returns to OK (Tab 2)
Expected:
- [OK] ... errors=0 ...


---

## Troubleshooting

### Port 8000 already in use

You likely have multiple Uvicorn processes running. Find and kill them:
```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
kill -9 <PID>
```

### log_monitor still alerting after recovery

If old error lines are still inside the monitor’s rolling window, it will continue to count them.
Fix by either:

- clearing the log file before recovery:
  ```bash
  : > logs/app.log
  ```

- or lowering window size temporarily:
  ```bash
  export WINDOW_LINES=20
  python monitoring/log_monitor.py
  ```



---

## .gitignore

Recommended ignores:
```gitignore
.venv/
__pycache__/
*.pyc
logs/*.log
*.sqlite3
.DS_Store
```

Keep the `logs/` folder itself in the repo by committing an empty `logs/.gitkeep` file.

---

## Why This Project Is Relevant

This project demonstrates:
	•	Incident triage (503 errors, recovery)
	•	Log analysis and alerting
	•	Metrics/monitoring workflows
	•	Environment-based configuration
	•	Basic operations hygiene

---

## License

MIT

---