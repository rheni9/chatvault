"""
Chat extractor module for Telegram HTML export.

This module provides a function to extract metadata about chats from
an HTML file exported from Telegram.

The extracted data is returned as a list of dictionaries, each
representing a single chat.
"""

import re
from bs4 import BeautifulSoup
from extractors.slugify_utils import slugify
from extractors.time_utils import parse_datetime

PIN_ICON = "\U0001F4CD"
LINK_ICON = "\U0001F517"
DATE_ICON = "\U0001F4C5"
ID_ICON = "\U0001F194"
WARNING_SIGN = "\u26A0\uFE0F"


def extract_chats(
    soup: BeautifulSoup, used_slugs: set[str] = None
) -> list[dict]:
    """
    Extract chat information from a parsed Telegram export HTML soup.

    For each chat, extracts:
      - name: the chat name as shown in the caption
      - slug: unique identifier generated from the name
              (conflicts are resolved by adding a hash if needed)
      - link: optional hyperlink to the chat
      - joined: join date (parsed from caption text), if present
      - chat_id: numeric identifier provided by the user, or None
      - is_active: whether the chat is considered active (user input)
      - is_member: whether the sender is a member of the chat (user input)
      - type: placeholder field (currently always None)
      - notes: placeholder for user notes (currently None)
      - table: original <table> element used for message extraction

    :param soup: Parsed BeautifulSoup object of the HTML
    :type soup: bs4.BeautifulSoup
    :param used_slugs: Set of already used slugs to ensure uniqueness
    :type used_slugs: set[str] or None
    :return: List of dictionaries with chat information
    :rtype: list[dict]
    """
    if used_slugs is None:
        used_slugs = set()

    chat_data = []

    for table in soup.find_all("table"):
        caption = table.find("caption")
        if not caption:
            continue

        caption_text = caption.text.strip()
        link_tag = caption.find("a")

        name = link_tag.text.strip() if link_tag else caption_text
        name = re.sub(r"\s*\(joined the group.*?\)", "", name).strip()

        link = (
            link_tag["href"]
            if link_tag and link_tag.has_attr("href")
            else None
        )

        match = re.search(
            r"joined the group\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
            caption_text
        )
        joined_date = (
            parse_datetime(match.group(1), date_only=True) if match else None
        )

        slug = slugify(name, used_slugs=used_slugs)

        print("\n" + "=" * 30)
        print(f"{PIN_ICON}  Name: {name}")
        print(f"{LINK_ICON}  Link: {link or '(none)'}")
        print(f"{DATE_ICON}  Joined: {joined_date or '(none)'}")
        print(f"{ID_ICON}  Slug: {slug}")

        while True:
            chat_id_input = input(
                "Enter chat_id (digits only, or press Enter to skip): "
            ).strip()
            if not chat_id_input:
                chat_id = None
                break
            if chat_id_input.isdigit():
                chat_id = int(chat_id_input)
                break
            print(
                f"{WARNING_SIGN}  Chat ID must be numeric or empty. "
                "Please try again."
            )

        is_active = (
            input("Is this chat active? (y/n, default y): ")
            .strip().lower() != "n"
        )

        is_member = (
            input("Are they a member of this chat? (y/n, default y): ")
            .strip()
            .lower() != "n"
        ) if is_active else False

        chat_data.append({
            "slug": slug,
            "chat_id": chat_id,
            "type": None,
            "name": name,
            "link": link,
            "joined": joined_date,
            "is_active": is_active,
            "is_member": is_member,
            "notes": None,
            "table": table
        })

    return chat_data
