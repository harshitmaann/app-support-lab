#!/usr/bin/env python3
import os
import time
from collections import deque
from typing import Deque, List, Optional, Tuple


LOG_PATH = os.getenv("LOG_PATH", "logs/app.log")
ERROR_THRESHOLD = int(os.getenv("ERROR_THRESHOLD", "2"))
SLOW_THRESHOLD = int(os.getenv("SLOW_THRESHOLD", "1"))
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "5"))
WINDOW_LINES = int(os.getenv("WINDOW_LINES", "250"))

# Optional: print a periodic "still alive" message even if state doesn't change
HEARTBEAT_SECONDS = int(os.getenv("HEARTBEAT_SECONDS", "0"))  # 0 = off


def file_id(path: str) -> Optional[Tuple[int, int]]:
    """
    Identify a file across rotations using (device, inode) when available.
    Returns None if file doesn't exist.
    """
    try:
        st = os.stat(path)
        return (st.st_dev, st.st_ino)
    except FileNotFoundError:
        return None


def read_new_lines(
    path: str,
    last_pos: int,
    last_fid: Optional[Tuple[int, int]],
) -> Tuple[List[str], int, Optional[Tuple[int, int]], bool]:
    """
    Read only newly appended lines since last_pos.

    Returns: (new_lines, new_pos, new_file_id, reset)
    reset=True if the file was rotated/recreated/truncated and we reset position.
    """
    fid = file_id(path)
    if fid is None:
        # File missing: treat as reset (so caller can clear window)
        return [], 0, None, True

    reset = False

    # Detect rotation/recreate (inode changed)
    if last_fid is not None and fid != last_fid:
        last_pos = 0
        reset = True

    # Detect truncation (file smaller than our pointer)
    size = os.path.getsize(path)
    if size < last_pos:
        last_pos = 0
        reset = True

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(last_pos)
        new_lines = f.readlines()
        new_pos = f.tell()

    return new_lines, new_pos, fid, reset


def count_errors(lines: Deque[str]) -> int:
    return sum(1 for line in lines if " | ERROR | " in line)


def count_slows(lines: Deque[str]) -> int:
    return sum(1 for line in lines if "Simulated slow response" in line)


def main() -> None:
    print(f"[INFO] log_monitor watching {LOG_PATH} every {INTERVAL_SECONDS}s")
    print(f"[INFO] thresholds: ERROR>={ERROR_THRESHOLD}, SLOW>={SLOW_THRESHOLD}")
    print(f"[INFO] window: last {WINDOW_LINES} total log lines")
    if HEARTBEAT_SECONDS > 0:
        print(f"[INFO] heartbeat every {HEARTBEAT_SECONDS}s")

    last_pos = 0
    last_fid: Optional[Tuple[int, int]] = None
    window: Deque[str] = deque(maxlen=WINDOW_LINES)

    last_state: Optional[str] = None  # "OK" | "SLOW" | "ERROR"
    last_print_ts = 0.0

    while True:
        new_lines, last_pos, last_fid, reset = read_new_lines(LOG_PATH, last_pos, last_fid)

        # If the log was truncated/rotated/missing, clear the window so we don't get "stuck" on old errors.
        if reset:
            window.clear()

        # Keep last WINDOW_LINES TOTAL lines (INFO/WARN/ERROR), so the state naturally heals.
        for line in new_lines:
            window.append(line)

        errors = count_errors(window)
        slows = count_slows(window)

        if errors >= ERROR_THRESHOLD:
            state = "ERROR"
            msg = f"[ALERT] log_monitor: ERROR threshold exceeded ({errors} in last {len(window)} lines)"
        elif slows >= SLOW_THRESHOLD:
            state = "SLOW"
            msg = f"[ALERT] log_monitor: SLOW detected ({slows} in last {len(window)} lines)"
        else:
            state = "OK"
            msg = f"[OK] log_monitor: errors={errors}, slow={slows} (window={len(window)} lines)"

        now = time.time()

        # Print only when state changes (plus first run)
        if state != last_state:
            print(msg)
            last_state = state
            last_print_ts = now

        # Optional heartbeat
        elif HEARTBEAT_SECONDS > 0 and (now - last_print_ts) >= HEARTBEAT_SECONDS:
            print(f"[HEARTBEAT] state={state} | errors={errors} | slow={slows} | window={len(window)}")
            last_print_ts = now

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()