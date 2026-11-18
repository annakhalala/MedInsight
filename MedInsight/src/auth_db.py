"""
User authentication storage.

Matches the schema already present in auth.db at the repo root:
    users(id, username, email, salt, pw_hash, created_at)
where pw_hash = sha256(salt + password).hexdigest()
"""
from pathlib import Path
import hashlib
import secrets
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "auth.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the users table if it doesn't already exist (no-op here since
    auth.db already ships with the table, but safe to call on a fresh clone)."""
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            salt TEXT NOT NULL,
            pw_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    conn.close()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def username_or_email_exists(username: str, email: str) -> bool:
    conn = _connect()
    row = conn.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (username, email),
    ).fetchone()
    conn.close()
    return row is not None


def create_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """Create a new user. Returns (success, message)."""
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if username_or_email_exists(username, email):
        return False, "That username or email is already registered."

    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)

    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO users (username, email, salt, pw_hash) VALUES (?, ?, ?, ?)",
            (username, email, salt, pw_hash),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False, "That username or email is already registered."
    conn.close()
    return True, "Account created successfully."


def verify_user(identifier: str, password: str) -> dict | None:
    """Verify a login by username or email + password.

    Returns a plain dict {id, username, email} on success, else None.
    """
    identifier = identifier.strip()
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (identifier, identifier.lower()),
    ).fetchone()
    conn.close()

    if row is None:
        return None

    expected = _hash_password(password, row["salt"])
    if not secrets.compare_digest(expected, row["pw_hash"]):
        return None

    return {"id": row["id"], "username": row["username"], "email": row["email"]}
