"""
JSON writer utilities for Telegram chat data (Arcanum App).

Provides functions to store extracted chat and message information
as structured JSON files for reference or debugging.

Each chat's metadata is saved in `chats.json`, while messages
are saved in individual files named `msg_{slug}.json`.
"""

import os
import json
import logging

# === Logging ===
logger = logging.getLogger(__name__)

# === Paths ===
JSON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "json"))
os.makedirs(JSON_PATH, exist_ok=True)


def save_chat_summary(chat: dict) -> None:
    """
    Save or update a chat entry in chats.json.

    Replaces existing entry with the same slug (if any),
    preserving a full summary of the chat’s metadata.

    :param chat: Chat dictionary with required metadata fields.
    """
    path = os.path.join(JSON_PATH, "chats.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    existing = [c for c in existing if c["slug"] != chat["slug"]]
    existing.append({
        "slug": chat["slug"],
        "chat_id": chat["chat_id"],
        "type": chat["type"],
        "name": chat["name"],
        "link": chat.get("link"),
        "joined": chat.get("joined"),
        "is_active": chat["is_active"],
        "is_member": chat["is_member"],
        "notes": chat["notes"]
    })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    logger.info("[JSON|SAVE] Updated chats.json with slug='%s'", chat["slug"])


def save_messages_to_json(slug: str, messages: list[dict]) -> None:
    """
    Save all messages of a given chat to msg_{slug}.json.

    Overwrites the file if it already exists.

    :param slug: Slug of the chat whose messages are being saved.
    :param messages: List of message dictionaries.
    """
    path = os.path.join(JSON_PATH, f"msg_{slug}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    logger.info("[JSON|SAVE] Saved %d messages to msg_%s.json", len(messages),
                slug)
