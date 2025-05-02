"""
Message extractor module for Telegram HTML export.

This module provides a function to extract individual messages from
a single Telegram chat table represented as a BeautifulSoup Tag.
Each message contains metadata such as message ID, timestamp, link,
and full text with paragraph structure preserved.
"""

from bs4 import Tag
from extractors.time_utils import parse_datetime


def extract_messages(table: Tag, chat_slug: str) -> list[dict]:
    """
    Extract messages from a specific Telegram chat table.

    :param table: <table> element containing message rows (<tr>)
    :type table: bs4.element.Tag
    :param chat_slug: Slug used to associate messages with a chat
    :type chat_slug: str
    :return: List of structured message dictionaries
    :rtype: list[dict]
    """
    messages = []

    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) != 3:
            continue

        id_cell, date_cell, text_cell = cols

        # ID and link
        id_link = id_cell.find("a")
        msg_id = (
            int(id_link.text.strip())
            if id_link and id_link.text.strip().isdigit()
            else int(id_cell.text.strip()) if id_cell.text.strip().isdigit()
            else None
        )

        msg_link = (
            id_link["href"] if id_link and id_link.has_attr("href") else None
        )

        parsed_dt = parse_datetime(date_cell.text.strip())

        text = "\n\n".join(
            p.strip()
            for p in text_cell.decode_contents().strip().split("<br/>")
            if p.strip()
        )

        msg = {
            "chat_slug": chat_slug,
            "msg_id": msg_id,
            "timestamp": parsed_dt,
            "link": msg_link,
            "text": text or None,
            "media": None,
            "screenshot": None,
            "tags": [],
            "notes": None
        }

        messages.append(msg)

    print(
        f"\n\u2705 Done. Extracted {len(messages)} messages from '{chat_slug}'"
    )
    return messages
