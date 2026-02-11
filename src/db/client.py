import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from src.config.settings import get_settings

settings = get_settings()


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_hash TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                revoked INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                model TEXT NOT NULL,
                system_prompt TEXT,
                metadata TEXT DEFAULT '{}',
                is_archived INTEGER DEFAULT 0,
                is_deleted INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                token_count INTEGER DEFAULT 0,
                model TEXT,
                finish_reason TEXT,
                latency_ms INTEGER,
                metadata TEXT DEFAULT '{}',
                estimated_cost_usd REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                key_prefix TEXT NOT NULL,
                name TEXT NOT NULL,
                scopes TEXT DEFAULT '[]',
                last_used_at TEXT,
                expires_at TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
