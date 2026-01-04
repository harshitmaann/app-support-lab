import time
import requests

URL = "http://127.0.0.1:8000/health"
INTERVAL_SECONDS = 5
TIMEOUT_SECONDS = 2
LATENCY_ALERT_SECONDS = 1.0  # alert if response takes longer than this

def main():
    print(f"[INFO] health_check polling {URL} every {INTERVAL_SECONDS}s")
    print(f"[INFO] timeout={TIMEOUT_SECONDS}s | latency_alert>{LATENCY_ALERT_SECONDS}s")

    while True:
        start = time.time()
        try:
            r = requests.get(URL, timeout=TIMEOUT_SECONDS)
            elapsed = time.time() - start

            if r.status_code != 200:
                print(f"[ALERT] health_check: HTTP {r.status_code} from {URL} ({elapsed:.2f}s)")
            elif elapsed > LATENCY_ALERT_SECONDS:
                print(f"[ALERT] health_check: slow response {elapsed:.2f}s (> {LATENCY_ALERT_SECONDS}s)")
            else:
                print(f"[OK] health_check: service healthy ({elapsed:.2f}s)")
        except Exception as e:
            elapsed = time.time() - start
            print(f"[ALERT] health_check: service unreachable after {elapsed:.2f}s: {e}")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()