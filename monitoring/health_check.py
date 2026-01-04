import time
import requests

URL = "http://127.0.0.1:8000/health"
INTERVAL_SECONDS = 5

def main():
    print(f"[INFO] health_check polling {URL} every {INTERVAL_SECONDS}s")
    while True:
        try:
            r = requests.get(URL, timeout=2)
            if r.status_code != 200:
                print(f"[ALERT] health_check: HTTP {r.status_code} from {URL}")
            else:
                print("[OK] health_check: service healthy")
        except Exception as e:
            print(f"[ALERT] health_check: service unreachable: {e}")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()