"""
Message extractor module for Telegram HTML export (Arcanum App).

Provides a function to extract individual messages from a Telegram chat
represented as a <table> element parsed with BeautifulSoup.

Each message includes core metadata and placeholders for media, tags, etc.
"""

import re
import logging
from bs4 import Tag
from extractors.time_utils import parse_datetime

logger = logging.getLogger(__name__)


def extract_messages(table: Tag, chat_slug: str) -> list[dict]:
    """
    Extract messages from a specific Telegram chat table.

    Each message includes:
      - msg_id, timestamp, link, cleaned text, chat_slug
      - placeholders for media, screenshot, tags, notes

    :param table: <table> element containing the message rows.
    :param chat_slug: Slug of the parent chat.
    :return: List of message dictionaries.
    """
    messages = []

    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) != 3:
            continue

        id_cell, date_cell, text_cell = cols

        # Extract message ID and link
        id_link = id_cell.find("a")
        raw_id = (
            id_link.text.strip()
            if id_link and id_link.text.strip()
            else id_cell.text.strip()
        )

        msg_id = int(raw_id) if re.fullmatch(r"\d{1,10}", raw_id) else None
        msg_link = id_link["href"] if id_link and id_link.has_attr("href") else None

        # Extract timestamp
        parsed_dt = parse_datetime(date_cell.text.strip())

        # Extract and normalize message text
        text = text_cell.get_text(separator="\n\n", strip=True)
        text = re.sub(r"[ \t]*(\n+)[ \t]*", lambda m: m.group(1), text)

        messages.append({
            "chat_slug": chat_slug,
            "msg_id": msg_id,
            "timestamp": parsed_dt,
            "link": msg_link,
            "text": text or None,
            "media": [],
            "screenshot": None,
            "tags": [],
            "notes": None
        })

    logger.info("[MSG|EXTRACT] Extracted %d messages from chat '%s'",
                len(messages), chat_slug)

    return messages
