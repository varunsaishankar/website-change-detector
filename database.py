import sqlite3
import hashlib
from datetime import datetime

DB_FILE = "detector.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row   # lets us use column names
    return conn


def init_db():
    """Create the tables if they don't exist yet."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            interval_minutes INTEGER NOT NULL,
            sensitivity TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'NEW',
            last_checked TEXT,
            last_changed TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            hash TEXT NOT NULL,
            screenshot TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def make_hash(text):
    """Turn text into a short fingerprint."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def add_page(name, url, interval_minutes, sensitivity="medium"):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO pages (name, url, interval_minutes, sensitivity) VALUES (?, ?, ?, ?)",
        (name, url, interval_minutes, sensitivity),
    )
    conn.commit()
    page_id = cur.lastrowid
    conn.close()
    return page_id


def get_all_pages():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM pages").fetchall()
    conn.close()
    return rows

def get_page(page_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM pages WHERE id = ?", (page_id,)).fetchone()
    conn.close()
    return row


def get_latest_hash(page_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT hash FROM snapshots WHERE page_id = ? ORDER BY id DESC LIMIT 1",
        (page_id,),
    ).fetchone()
    conn.close()
    return row["hash"] if row else None


def save_snapshot(page_id, text, text_hash, screenshot):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    conn.execute(
        "INSERT INTO snapshots (page_id, text, hash, screenshot, created_at) VALUES (?, ?, ?, ?, ?)",
        (page_id, text, text_hash, screenshot, now),
    )
    conn.execute("UPDATE pages SET last_changed = ? WHERE id = ?", (now, page_id))
    conn.commit()
    conn.close()


def update_status(page_id, status):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    conn.execute(
        "UPDATE pages SET status = ?, last_checked = ? WHERE id = ?",
        (status, now, page_id),
    )
    conn.commit()
    conn.close()
def get_snapshots(page_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, hash, screenshot, created_at FROM snapshots WHERE page_id = ? ORDER BY id DESC",
        (page_id,),
    ).fetchall()
    conn.close()
    return rows


def save_snapshot(page_id, text, text_hash, screenshot):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO snapshots (page_id, text, hash, screenshot, created_at) VALUES (?, ?, ?, ?, ?)",
        (page_id, text, text_hash, screenshot, now),
    )
    snapshot_id = cur.lastrowid
    conn.execute("UPDATE pages SET last_changed = ? WHERE id = ?", (now, page_id))
    conn.commit()
    conn.close()
    return snapshot_id
