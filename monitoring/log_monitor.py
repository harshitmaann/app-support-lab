import os
import time

LOG_PATH = os.getenv("LOG_PATH", "logs/app.log")
ERROR_THRESHOLD = int(os.getenv("ERROR_THRESHOLD", "2"))  # alert if >=2 errors seen
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "5"))

def count_errors_recent(lines):
    # Simple pattern match – good enough for the lab
    return sum(1 for line in lines if " | ERROR | " in line)

def tail_lines(path: str, max_lines: int = 200):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()[-max_lines:]

def main():
    print(f"[INFO] log_monitor watching {LOG_PATH} every {INTERVAL_SECONDS}s (threshold={ERROR_THRESHOLD})")
    while True:
        lines = tail_lines(LOG_PATH)
        errors = count_errors_recent(lines)

        if errors >= ERROR_THRESHOLD:
            print(f"[ALERT] log_monitor: ERROR threshold exceeded ({errors} recent errors)")
        else:
            print(f"[OK] log_monitor: errors seen recently = {errors}")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()