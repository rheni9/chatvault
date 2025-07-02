"""
Telegram HTML parser and writer entrypoint (Arcanum App).

Extracts chat and message data from a Telegram HTML export,
and stores it in both SQLite and PostgreSQL databases. Also
saves intermediate JSON summaries for each chat.
"""

import os
import logging
import sqlite3
import psycopg2
from psycopg2 import DatabaseError as PGDatabaseError
from dotenv import load_dotenv

from extractors.html_loader import load_html
from extractors.get_input_html import get_input_html_path
from extractors.chat_extractor import extract_chats
from extractors.message_extractor import extract_messages
from storage.json_writer import save_chat_summary, save_messages_to_json
from storage.db_writer import (ensure_tables as ensure_sqlite_tables,
                               insert_chat as insert_sqlite_chat,
                               insert_message as insert_sqlite_message)
from storage.db_pg_writer import (ensure_tables as ensure_pg_tables,
                                  insert_chat as insert_pg_chat, insert_message
                                  as insert_pg_message)

# === Logging Configuration ===
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# === Load environment ===
load_dotenv()

# === SQLite: use SQLITE_PATH if set, else fallback ===
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

# === PostgreSQL ===
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")


def get_chat_id_by_slug_sqlite(cursor: sqlite3.Cursor, slug: str) -> int:
    """
    Get the internal chat ID from SQLite by its slug.

    :param cursor: SQLite cursor.
    :param slug: Unique chat slug.
    :return: Chat ID in the SQLite DB.
    :raises ValueError: If the slug is not found.
    """
    cursor.execute("SELECT id FROM chats WHERE slug = ?", (slug, ))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"[SQLite] Chat slug '{slug}' not found.")
    return row[0]


def get_chat_id_by_slug_pg(cursor: psycopg2.extensions.cursor,
                           slug: str) -> int:
    """
    Get the internal chat ID from PostgreSQL by its slug.

    :param cursor: PostgreSQL cursor.
    :param slug: Unique chat slug.
    :return: Chat ID in the PostgreSQL DB.
    :raises ValueError: If the slug is not found.
    """
    cursor.execute("SELECT id FROM chats WHERE slug = %s", (slug, ))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"[Postgres] Chat slug '{slug}' not found.")
    return row[0]


def main():
    """
    Run the full extraction and database insertion workflow.
    """
    path = get_input_html_path()
    soup = load_html(path)
    chats = extract_chats(soup)

    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)

    sqlite_conn = pg_conn = None
    sqlite_cur = pg_cur = None
    try:
        sqlite_conn = sqlite3.connect(SQLITE_PATH)
        sqlite_cur = sqlite_conn.cursor()
        ensure_sqlite_tables(sqlite_cur)

        pg_conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        pg_cur = pg_conn.cursor()
        ensure_pg_tables(pg_cur)
    except (sqlite3.DatabaseError, PGDatabaseError) as e:
        logger.error("[ERROR] Failed to initialize databases: %s", e)
        return

    total_messages = 0

    for chat in chats:
        try:
            messages = extract_messages(chat["table"], chat["slug"])

            save_chat_summary(chat)
            save_messages_to_json(chat["slug"], messages)

            insert_sqlite_chat(sqlite_cur, chat)
            insert_pg_chat(pg_cur, chat)

            sqlite_chat_ref_id = get_chat_id_by_slug_sqlite(
                sqlite_cur, chat["slug"])
            pg_chat_ref_id = get_chat_id_by_slug_pg(pg_cur, chat["slug"])

            for msg in messages:
                insert_sqlite_message(sqlite_cur, msg, sqlite_chat_ref_id)
                insert_pg_message(pg_cur, msg, pg_chat_ref_id)

            sqlite_conn.commit()
            pg_conn.commit()

            total_messages += len(messages)

            logger.info("[CHAT] Saved '%s' with %d messages.",
                        chat["slug"], len(messages))
        except (sqlite3.DatabaseError, PGDatabaseError, KeyError) as e:
            logger.error("[ERROR] Failed to process chat '%s': %s",
                         chat["slug"], e)
            if sqlite_conn:
                sqlite_conn.rollback()
            if pg_conn:
                pg_conn.rollback()

    # === Proper cleanup after all chats processed ===
    if sqlite_cur:
        sqlite_cur.close()
    if sqlite_conn:
        sqlite_conn.close()
    if pg_cur:
        pg_cur.close()
    if pg_conn:
        pg_conn.close()

    logger.info("[DONE] All chats and messages processed.")
    logger.info("🗂️  Chats processed: %d", len(chats))
    logger.info("💬  Total messages: %d", total_messages)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("[INTERRUPT] Workflow interrupted by user.")
