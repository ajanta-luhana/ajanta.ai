import os
import sqlite3
import threading
import time

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, intent TEXT, question TEXT,
  grounded INTEGER, flagged INTEGER, confidence REAL, latency_ms INTEGER, sources TEXT);
CREATE TABLE IF NOT EXISTS feedback(message_id INTEGER, value INTEGER, ts REAL);
CREATE TABLE IF NOT EXISTS hire_requests(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, role_type TEXT, scope TEXT, skills TEXT, name TEXT, email TEXT);
"""


def init_db(path: str) -> None:
    """SQLite for the MVP. For production, point the same queries at PostgreSQL."""
    global _conn
    if path != ":memory:":
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    _conn = sqlite3.connect(path, check_same_thread=False)
    _conn.row_factory = sqlite3.Row
    _conn.executescript(SCHEMA)


def execute(sql: str, args: tuple = ()) -> int:
    with _lock:
        cur = _conn.execute(sql, args)
        _conn.commit()
        return cur.lastrowid


def query(sql: str, args: tuple = ()) -> list[dict]:
    with _lock:
        return [dict(r) for r in _conn.execute(sql, args).fetchall()]


def now() -> float:
    return time.time()
