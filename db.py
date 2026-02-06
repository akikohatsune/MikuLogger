import os
import sqlite3
from contextlib import contextmanager
from typing import Optional, Tuple

DB_PATH = os.getenv("MIKU_DB", "miku.db")


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER NOT NULL,
                active INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS member_last_join (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                last_join_ts INTEGER NOT NULL,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS member_last_out (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                last_out_ts INTEGER NOT NULL,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )
        if not _column_exists(conn, "guild_settings", "active"):
            conn.execute(
                "ALTER TABLE guild_settings ADD COLUMN active INTEGER NOT NULL DEFAULT 0"
            )


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == column for row in rows)


def get_guild_settings(guild_id: int) -> Tuple[Optional[int], bool]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT log_channel_id, active FROM guild_settings WHERE guild_id = ?",
            (guild_id,),
        ).fetchone()
        if not row:
            return None, False
        return row[0], bool(row[1])


def set_active(guild_id: int, channel_id: int) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO guild_settings (guild_id, log_channel_id, active)
            VALUES (?, ?, 1)
            ON CONFLICT(guild_id) DO UPDATE SET
                log_channel_id = excluded.log_channel_id,
                active = 1
            """,
            (guild_id, channel_id),
        )

def set_inactive(guild_id: int) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE guild_settings SET active = 0 WHERE guild_id = ?",
            (guild_id,),
        )


def get_last_join_ts(guild_id: int, user_id: int) -> Optional[int]:
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT last_join_ts
            FROM member_last_join
            WHERE guild_id = ? AND user_id = ?
            """,
            (guild_id, user_id),
        ).fetchone()
        return row[0] if row else None


def set_last_join_ts(guild_id: int, user_id: int, ts: int) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO member_last_join (guild_id, user_id, last_join_ts)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET last_join_ts = excluded.last_join_ts
            """,
            (guild_id, user_id, ts),
        )


def get_last_out_ts(guild_id: int, user_id: int) -> Optional[int]:
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT last_out_ts
            FROM member_last_out
            WHERE guild_id = ? AND user_id = ?
            """,
            (guild_id, user_id),
        ).fetchone()
        return row[0] if row else None


def set_last_out_ts(guild_id: int, user_id: int, ts: int) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO member_last_out (guild_id, user_id, last_out_ts)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET last_out_ts = excluded.last_out_ts
            """,
            (guild_id, user_id, ts),
        )
