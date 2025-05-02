"""
SQLite writer utilities for Telegram chat and message data.

This module defines helper functions for creating and populating
SQLite tables to persist Telegram chat metadata and messages.

Tables:
-------
- chats (slug TEXT PRIMARY KEY, name, link, joined, chat_id)
- messages (msg_id, chat_slug, timestamp, link, text, media, screenshot,
  tags, notes)
"""

from sqlite3 import Cursor
import json


def ensure_tables(cursor: Cursor) -> None:
    """
    Create necessary SQLite tables if they do not already exist.

    :param cursor: SQLite cursor object
    :type cursor: sqlite3.Cursor
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            slug TEXT PRIMARY KEY,
            chat_id INTEGER,
            type TEXT,
            name TEXT,
            link TEXT,
            joined TEXT,
            is_active BOOLEAN,
            is_member BOOLEAN,
            notes TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            msg_id INTEGER,
            chat_slug TEXT,
            timestamp TEXT,
            link TEXT,
            text TEXT,
            media TEXT,
            screenshot TEXT,
            tags TEXT,
            notes TEXT,
            FOREIGN KEY(chat_slug) REFERENCES chats(slug)
        )
    """)


def insert_chat(cursor: Cursor, chat: dict) -> None:
    """
    Insert or replace a chat entry into the database.

    :param cursor: SQLite cursor object
    :type cursor: sqlite3.Cursor
    :param chat: Chat metadata
    :type chat: dict
    """
    cursor.execute(
        """
        INSERT OR REPLACE INTO chats (
            slug, chat_id, type, name, link,
            joined, is_active, is_member, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chat["slug"],
            chat["chat_id"],
            chat["type"],
            chat["name"],
            chat.get("link"),
            chat.get("joined"),
            chat["is_active"],
            chat["is_member"],
            chat["notes"]
        )
    )


def insert_message(cursor: Cursor, msg: dict) -> None:
    """
    Insert a message entry into the database.

    :param cursor: SQLite cursor object
    :type cursor: sqlite3.Cursor
    :param msg: Message data dictionary
    :type msg: dict
    """
    cursor.execute(
        """
        INSERT INTO messages (
            msg_id, chat_slug, timestamp, link, text,
            media, screenshot, tags, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            msg["msg_id"],
            msg["chat_slug"],
            msg.get("timestamp"),
            msg.get("link"),
            msg.get("text"),
            msg.get("media"),
            msg.get("screenshot"),
            json.dumps(msg.get("tags", []), ensure_ascii=False),
            msg.get("notes")
        )
    )
