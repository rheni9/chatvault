"""
Database table cleanup script for the Arcanum application.

Connects to PostgreSQL and SQLite databases using credentials
from environment variables and drops the `messages` and `chats`
tables if they exist. Intended for development or reset purposes only.
"""

import os
import logging
import argparse
import sqlite3
import psycopg2
from dotenv import load_dotenv

# === Load environment ===
load_dotenv()
PG_URL = os.getenv("DATABASE_URL")
SQLITE_PATH = os.getenv(
    "SQLITE_PATH",
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "db",
            "chatvault.sqlite"
        )
    )
)

# === Logger configuration ===
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def drop_pg_tables() -> None:
    """
    Drop the 'messages' and 'chats' tables in PostgreSQL.

    Connects using `DATABASE_URL` from environment variables.
    Executes SQL statements to drop both tables and commits the changes.

    :raises psycopg2.DatabaseError: If connection or execution fails.
    """
    logger.info("[DROP] Connecting to PostgreSQL...")
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(PG_URL)
        cur = conn.cursor()

        logger.info(
           "[DROP] Dropping 'messages' and 'chats' tables (if exist)..."
        )
        cur.execute("DROP TABLE IF EXISTS messages;")
        cur.execute("DROP TABLE IF EXISTS chats;")

        conn.commit()
        logger.info(
            "✅ PostgreSQL tables 'messages' and 'chats' deleted successfully."
        )

    except psycopg2.DatabaseError as e:
        logger.error("[DROP] Database error: %s", e)
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            logger.info("[DROP] Connection closed.")


def drop_sqlite_tables() -> None:
    """
    Drop the 'messages' and 'chats' tables in SQLite.

    Connects using `SQLITE_PATH` from environment variables.
    Executes SQL statements to drop both tables and commits the changes.

    :raises sqlite3.DatabaseError: If connection or execution fails.
    """
    logger.info("[DROP|SQLite] Connecting to SQLite...")
    conn = None
    try:
        conn = sqlite3.connect(SQLITE_PATH)
        cur = conn.cursor()

        logger.info(
            "[DROP|SQLite] Dropping 'messages' and 'chats' tables "
            "(if exist)..."
        )
        cur.execute("DROP TABLE IF EXISTS messages;")
        cur.execute("DROP TABLE IF EXISTS chats;")

        conn.commit()
        logger.info(
            "✅ SQLite tables 'messages' and 'chats' deleted successfully."
        )

    except sqlite3.DatabaseError as e:
        logger.error("[DROP|SQLite] Database error: %s", e)
        raise
    finally:
        if conn:
            conn.close()
            logger.info("[DROP|SQLite] Connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Drop 'messages' and 'chats' tables in PostgreSQL and/or SQLite."
        )
    )
    parser.add_argument(
        "--pg-only",
        action="store_true",
        help="Drop only PostgreSQL tables."
    )
    parser.add_argument(
        "--sqlite-only",
        action="store_true",
        help="Drop only SQLite tables."
    )

    args = parser.parse_args()

    try:
        if args.pg_only and args.sqlite_only:
            logger.warning(
                "[WARN] Both --pg-only and --sqlite-only specified. "
                "Doing both."
            )
            drop_pg_tables()
            drop_sqlite_tables()
        elif args.pg_only:
            drop_pg_tables()
        elif args.sqlite_only:
            drop_sqlite_tables()
        else:
            drop_pg_tables()
            drop_sqlite_tables()

    except KeyboardInterrupt:
        logger.warning("[INTERRUPT] Operation cancelled by user.")
