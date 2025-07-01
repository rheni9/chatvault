"""
SQLite writer utilities for Telegram chat and message data (Arcanum App).

Handles table creation and data insertion into the SQLite database.
"""

import json
import logging
import sqlite3
from sqlite3 import Cursor

logger = logging.getLogger(__name__)


def enable_foreign_keys(connection: sqlite3.Connection) -> None:
    """
    Enable foreign key constraints in SQLite.

    :param connection: SQLite connection object.
    """
    connection.execute("PRAGMA foreign_keys = ON")
    logger.debug("[DB|INIT] Foreign key constraints enabled.")


def ensure_tables(cursor: Cursor) -> None:
    """
    Ensure required tables exist in the SQLite database.

    :param cursor: SQLite cursor object.
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            chat_id INTEGER,
            type TEXT,
            name TEXT,
            link TEXT,
            joined TEXT,
            is_active BOOLEAN,
            is_member BOOLEAN,
            is_public BOOLEAN,
            notes TEXT
        )
    """)
    logger.debug("[DB|SCHEMA] Ensured 'chats' table exists.")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            msg_id INTEGER,
            chat_ref_id INTEGER NOT NULL,
            timestamp TEXT,
            link TEXT,
            text TEXT,
            media TEXT,
            screenshot TEXT,
            tags TEXT,
            notes TEXT,
            FOREIGN KEY(chat_ref_id) REFERENCES chats(id) ON DELETE CASCADE
        )
    """)
    logger.debug("[DB|SCHEMA] Ensured 'messages' table exists.")

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_msg_id
        ON messages(chat_ref_id, msg_id)
        WHERE msg_id IS NOT NULL
    """)
    logger.debug(
        "[DB|INDEX] Ensured unique index on (chat_ref_id, msg_id) "
        "WHERE msg_id IS NOT NULL."
    )


def insert_chat(cursor: Cursor, chat: dict) -> None:
    """
    Insert or update a chat entry in the SQLite database.

    :param cursor: SQLite cursor object.
    :param chat: Chat metadata dictionary.
    :raises ValueError: If 'slug' is missing or chat_id duplicates another.
    """
    slug = chat.get("slug")
    if not slug:
        logger.error("[DB|INSERT] Missing 'slug' in chat: %s", chat)
        raise ValueError("Missing required field: 'slug'")

    chat_id = chat.get("chat_id")
    if chat_id is not None:
        cursor.execute(
            "SELECT 1 FROM chats WHERE chat_id = ? AND slug != ? LIMIT 1;",
            (chat_id, slug))
        if cursor.fetchone():
            logger.error(
                "[DB|INSERT] Duplicate chat_id=%s found for another slug.",
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
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            chat_id = excluded.chat_id,
            type = excluded.type,
            name = excluded.name,
            link = excluded.link,
            joined = excluded.joined,
            is_active = excluded.is_active,
            is_member = excluded.is_member,
            is_public = excluded.is_public,
            notes = excluded.notes
    """,
        (chat["slug"], chat.get("chat_id"), chat.get("type"), chat.get("name"),
         chat.get("link"), chat.get("joined"), chat.get("is_active"),
         chat.get("is_member"), chat.get("is_public"), chat.get("notes")))
    logger.debug("[DB|INSERT] Chat inserted or updated: '%s'.", slug)


def insert_message(cursor: Cursor, msg: dict, chat_ref_id: int) -> None:
    """
    Insert a message entry into the SQLite database.

    :param cursor: SQLite cursor object.
    :param msg: Message data dictionary.
    :param chat_ref_id: ID of the parent chat (foreign key to chats.id).
    """
    msg_id = msg.get("msg_id")
    timestamp = msg.get("timestamp")
    media_json = json.dumps(msg.get("media", []), ensure_ascii=False)
    tags_json = json.dumps(msg.get("tags", []), ensure_ascii=False)

    if msg_id is not None:
        cursor.execute(
            """
            SELECT 1 FROM messages
            WHERE chat_ref_id = ? AND msg_id = ?
            LIMIT 1
            """, (chat_ref_id, msg_id))
        if cursor.fetchone():
            logger.debug(
                "[DB|SKIP] Duplicate msg_id=%s in chat_ref_id=%d. Skipping.",
                msg_id, chat_ref_id)
            return

    cursor.execute(
        """
        INSERT INTO messages (
            msg_id, chat_ref_id, timestamp, link, text,
            media, screenshot, tags, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, chat_ref_id, timestamp, msg.get("link"), msg.get("text"),
              media_json, msg.get("screenshot"), tags_json, msg.get("notes")))

    logger.debug("[DB|INSERT] Message inserted (msg_id=%s, chat_ref_id=%d).",
                 str(msg_id), chat_ref_id)
