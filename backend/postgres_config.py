"""PostgreSQL database configuration for Watch1 backend."""
from __future__ import annotations

import logging
import os
from contextlib import contextmanager

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection as PGConnection
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

DEFAULTS = {
    "host": os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "watch1-postgres")),
    "port": int(os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432"))),
    "dbname": os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "watch1")),
    "user": os.getenv("POSTGRES_USER", os.getenv("DB_USER", "watch1")),
    "password": os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD", "watch1password")),
    "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
}


def _connect() -> PGConnection:
    conn = psycopg2.connect(**DEFAULTS)
    conn.autocommit = False
    conn.cursor_factory = RealDictCursor
    return conn


def get_db_connection() -> PGConnection:
    """Return a new PostgreSQL connection."""
    try:
        return _connect()
    except Exception as exc:  # pragma: no cover - log before raising
        logger.error("Database connection failed: %s", exc)
        raise


def test_db_connection() -> bool:
    """Perform a lightweight connectivity check."""
    try:
        with contextmanager(lambda: (_connect(), None))() as (conn, _):
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("SELECT 1"))
                cursor.fetchone()
        return True
    except Exception as exc:
        logger.error("Database test query failed: %s", exc)
        return False
