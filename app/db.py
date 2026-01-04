import sqlite3
from typing import Optional, Tuple, List, Dict, Any

def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=2)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str) -> None:
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sample_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value TEXT NOT NULL
            )
        """)
        cur.execute("SELECT COUNT(*) AS c FROM sample_data")
        if cur.fetchone()["c"] == 0:
            cur.executemany(
                "INSERT INTO sample_data(value) VALUES (?)",
                [("alpha",), ("bravo",), ("charlie",)],
            )
        conn.commit()
    finally:
        conn.close()

def fetch_sample(db_path: str) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        conn = get_conn(db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, value FROM sample_data ORDER BY id LIMIT 50")
            rows = [dict(r) for r in cur.fetchall()]
            return True, rows, None
        finally:
            conn.close()
    except Exception as e:
        return False, None, str(e)