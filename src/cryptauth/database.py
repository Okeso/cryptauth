import secrets
import sqlite3
from base64 import b32encode
from datetime import datetime
from pathlib import Path
from typing import Optional, Iterator


def load_authorized_addresses(path: Path) -> Iterator[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Authorized addresses file not found: {path}")
    with open(path) as f:
        for line in f.readlines():
            content = line.strip()
            if not content.startswith("#"):
                yield content


def setup_database(path: Path, authorized_addresses: list[str]) -> sqlite3.Connection:
    db = sqlite3.connect(path, check_same_thread=False)
    db.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            expires_at TEXT,
            valid BOOLEAN DEFAULT TRUE,
            nonce STRING UNIQUE,
            address STRING
        );
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS authorized_addresses (
            address STRING PRIMARY KEY
        );
        """)
    db.commit()

    # Ensure only authorized addresses are in the table
    cursor = db.cursor()
    cursor.execute("DELETE FROM authorized_addresses")
    cursor.executemany(
        "INSERT INTO authorized_addresses (address) VALUES (?)",
        [(address,) for address in authorized_addresses],
    )
    db.commit()

    return db


def session_is_valid(
    db: sqlite3.Connection, session_id: Optional[str], date: datetime
) -> bool:
    """Check if a session is valid based on the session_id and the current date."""
    if not session_id:
        return False
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM sessions WHERE session_id = ? AND expires_at > ? AND valid = TRUE",
        (session_id, date),
    )
    return cursor.fetchone() is not None


def create_session(db: sqlite3.Connection, expires_at: datetime) -> tuple[str, str]:
    """Create a new session."""
    session_id = secrets.token_urlsafe(32)
    nonce = b32encode(secrets.token_bytes(16)).decode().rstrip("=")
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO sessions (session_id, expires_at, valid, nonce) VALUES (?, ?, ?, ?)",
        (session_id, expires_at, True, nonce),
    )
    db.commit()
    print("Created")
    return session_id, nonce


def get_session_nonce(db: sqlite3.Connection, session_id: str) -> Optional[str]:
    """Get the nonce associated with a session."""
    cursor = db.cursor()
    cursor.execute("SELECT nonce FROM sessions WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()
    return str(result[0])


def invalidate_session(db: sqlite3.Connection, session_id: str) -> None:
    """Invalidate a session based on the session_id."""
    cursor = db.cursor()
    cursor.execute(
        "UPDATE sessions SET valid = FALSE WHERE session_id = ?", (session_id,)
    )
    db.commit()


def associate_session_with_address(
    db: sqlite3.Connection, session_id: str, address: str
) -> None:
    """Associate a session with an address."""
    cursor = db.cursor()
    cursor.execute(
        "UPDATE sessions SET address = ? WHERE session_id = ?", (address, session_id)
    )
    db.commit()


def session_is_authenticated(
    db: sqlite3.Connection, session_id: Optional[str], date: datetime
) -> Optional[str]:
    """Check if a session is authenticated based on the session_id. If the session is authenticated, return the address associated with the session."""
    if not session_id:
        return None
    cursor = db.cursor()
    cursor.execute(
        "SELECT address FROM sessions WHERE session_id = ? AND valid = TRUE AND expires_at > ?",
        (session_id, date),
    )
    result = cursor.fetchone()
    return result[0] if result else None


def address_is_authorized(db: sqlite3.Connection, address: str) -> bool:
    """Check if an address is authorized to sign in."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM authorized_addresses WHERE address = ?", (address,))
    return cursor.fetchone() is not None


def session_is_authorized(
    db: sqlite3.Connection, session_id: Optional[str], date: datetime
) -> bool:
    """Check if a session is authorized to sign in with a given address."""
    address = session_is_authenticated(db, session_id, date)
    if address is None:
        return False
    return address_is_authorized(db, address)


def query_metrics(db: sqlite3.Connection, date: datetime) -> dict[str, int]:
    queries = {
        "active_sessions": "SELECT COUNT(*) FROM sessions WHERE valid = TRUE AND expires_at > ?",
        "authenticated_sessions": "SELECT COUNT(*) FROM sessions WHERE valid = TRUE AND address IS NOT NULL AND expires_at > ?",
        "expired_sessions": "SELECT COUNT(*) FROM sessions WHERE valid = FALSE AND expires_at > ?",
        "authorized_addresses": "SELECT COUNT(*) FROM authorized_addresses WHERE 1 = 1 AND ?",
    }
    return {
        field: db.execute(query, (date,)).fetchone()[0]
        for field, query in queries.items()
    }
