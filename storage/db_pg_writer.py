"""
PostgreSQL writer utilities for Telegram chat and message data (Arcanum App).

Handles table creation and data insertion into a PostgreSQL database.
"""

import logging
from datetime import datetime, date
from psycopg2.extras import Json
from psycopg2.extensions import cursor as PGCursor

logger = logging.getLogger(__name__)


def ensure_tables(cursor: PGCursor) -> None:
    """
    Ensure required tables exist in the PostgreSQL database.

    :param cursor: PostgreSQL cursor object.
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            chat_id BIGINT,
            type TEXT,
            name TEXT,
            link TEXT,
            joined DATE,
            is_active BOOLEAN,
            is_member BOOLEAN,
            is_public BOOLEAN,
            notes TEXT
        )
    """)
    logger.debug("[PG|SCHEMA] Ensured 'chats' table exists.")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            msg_id BIGINT,
            chat_ref_id INTEGER NOT NULL
                REFERENCES chats(id)
                ON DELETE CASCADE,
            timestamp TIMESTAMPTZ,
            link TEXT,
            text TEXT,
            media JSONB,
            screenshot TEXT,
            tags JSONB,
            notes TEXT
        )
    """)
    logger.debug("[PG|SCHEMA] Ensured 'messages' table exists.")

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_msg_id
        ON messages(chat_ref_id, msg_id)
        WHERE msg_id IS NOT NULL
    """)
    logger.debug(
        "[PG|INDEX] Ensured unique index on (chat_ref_id, msg_id) "
        "WHERE msg_id IS NOT NULL."
    )


def parse_iso_date(datestr: str | None) -> date | None:
    """
    Parse ISO-formatted date string into a Python date object.

    :param datestr: ISO date string (e.g., '2024-03-15')
    :return: date object or None
    """
    if datestr is None:
        return None
    try:
        return date.fromisoformat(datestr)
    except ValueError:
        logger.warning("[PG|DATE] Invalid date format: %s", datestr)
        return None


def parse_timestamp(ts: str | None) -> datetime | None:
    """
    Parse ISO-formatted timestamp string into a datetime object.

    :param ts: ISO timestamp string.
    :return: datetime object or None
    """
    if ts is None:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        logger.warning("[PG|TIMESTAMP] Invalid timestamp format: %s", ts)
        return None


def insert_chat(cursor: PGCursor, chat: dict) -> None:
    """
    Insert or update a chat entry in PostgreSQL.

    :param cursor: PostgreSQL cursor object.
    :param chat: Chat metadata dictionary.
    """
    slug = chat.get("slug")
    if not slug:
        logger.error("[PG|INSERT] Missing 'slug' in chat: %s", chat)
        raise ValueError("Missing required field: 'slug'")

    chat_id = chat.get("chat_id")
    if chat_id is not None:
        cursor.execute(
            "SELECT 1 FROM chats WHERE chat_id = %s AND slug != %s LIMIT 1;",
            (chat_id, slug))
        if cursor.fetchone():
            logger.error(
                "[PG|INSERT] Duplicate chat_id=%s found for another slug.",
                chat_id)
            raise ValueError(
                f"Chat ID {chat_id} already exists in another chat "
                f"(slug ≠ {slug})"
            )

    cursor.execute(
        """
        INSERT INTO chats (
            slug, chat_id, type, name, link,
            joined, is_active, is_member, is_public, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (slug) DO UPDATE SET
            chat_id = EXCLUDED.chat_id,
            type = EXCLUDED.type,
            name = EXCLUDED.name,
            link = EXCLUDED.link,
            joined = EXCLUDED.joined,
            is_active = EXCLUDED.is_active,
            is_member = EXCLUDED.is_member,
            is_public = EXCLUDED.is_public,
            notes = EXCLUDED.notes
    """, (chat["slug"], chat["chat_id"], chat["type"], chat["name"],
          chat.get("link"), parse_iso_date(
              chat.get("joined")), chat["is_active"], chat["is_member"],
          chat["is_public"], chat.get("notes")))
    logger.debug("[PG|INSERT] Chat inserted or updated: '%s'.", chat["slug"])


def insert_message(cursor: PGCursor, msg: dict, chat_ref_id: int) -> None:
    """
    Insert a message entry into PostgreSQL.

    :param cursor: PostgreSQL cursor object.
    :param msg: Message data dictionary.
    :param chat_ref_id: ID of the parent chat (foreign key to chats.id).
    """
    timestamp = parse_timestamp(msg.get("timestamp"))
    msg_id = msg.get("msg_id")
    media_json = Json(msg.get("media", []))
    tags_json = Json(msg.get("tags", []))

    # === Skip if msg_id already exists in the same chat ===
    if msg_id is not None:
        cursor.execute(
            """
            SELECT 1 FROM messages
            WHERE chat_ref_id = %s AND msg_id = %s
            LIMIT 1
            """, (chat_ref_id, msg_id))
        if cursor.fetchone():
            logger.debug(
                "[PG|SKIP] Duplicate msg_id=%s in chat_ref_id=%d. Skipping.",
                msg_id, chat_ref_id)
            return

    # === Insert message regardless of msg_id presence ===
    cursor.execute(
        """
        INSERT INTO messages (
            msg_id, chat_ref_id, timestamp, link, text,
            media, screenshot, tags, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (msg_id, chat_ref_id, timestamp, msg.get("link"), msg.get("text"),
              media_json, msg.get("screenshot"), tags_json, msg.get("notes")))

    logger.debug("[PG|INSERT] Message inserted (msg_id=%s, chat_ref_id=%d).",
                 str(msg_id), chat_ref_id)
