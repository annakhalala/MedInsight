"""
Prediction logging — stores every prediction a signed-in user makes so it
can be revisited later (referenced by README/Home.py as
"data/prediction_logs.db" and "Prediction History").
"""
from pathlib import Path
import json
import sqlite3

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "prediction_logs.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_logs_db():
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            review_text TEXT NOT NULL,
            predicted_condition TEXT NOT NULL,
            probabilities TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    conn.close()


def log_prediction(username: str, review_text: str, predicted_condition: str, probabilities: dict):
    init_logs_db()
    conn = _connect()
    conn.execute(
        """INSERT INTO prediction_logs (username, review_text, predicted_condition, probabilities)
           VALUES (?, ?, ?, ?)""",
        (username, review_text, predicted_condition, json.dumps(probabilities)),
    )
    conn.commit()
    conn.close()


def get_user_logs(username: str, limit: int = 20):
    init_logs_db()
    conn = _connect()
    rows = conn.execute(
        """SELECT * FROM prediction_logs WHERE username = ?
           ORDER BY created_at DESC LIMIT ?""",
        (username, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_logs(limit: int = 500):
    init_logs_db()
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM prediction_logs ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
