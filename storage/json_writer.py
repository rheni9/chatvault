"""
JSON writer utilities for Telegram chat data.

This module provides functions to save chat metadata and message data
to structured JSON files. Each chat's messages are stored in a separate
file (msg_{slug}.json), and a cumulative list of chats is maintained
in chats.json.
"""

import os
import json

JSON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "json")
)
os.makedirs(JSON_PATH, exist_ok=True)


def save_chat_summary(chat: dict) -> None:
    """
    Save or update a chat summary in the chats.json file.

    :param chat: Dictionary containing chat metadata
    :type chat: dict
    """
    path = os.path.join(JSON_PATH, "chats.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    existing = [c for c in existing if c["slug"] != chat["slug"]]
    existing.append({
        "name": chat["name"],
        "slug": chat["slug"],
        "link": chat.get("link"),
        "joined": chat.get("joined"),
        "chat_id": chat.get("chat_id")
    })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def save_messages_to_json(slug: str, messages: list[dict]) -> None:
    """
    Save all messages of a chat into a separate JSON file.

    :param slug: Chat slug identifier
    :type slug: str
    :param messages: List of message dicts
    :type messages: list[dict]
    """
    path = os.path.join(JSON_PATH, f"msg_{slug}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
