"""
Chat extractor module for Telegram HTML export (Arcanum App).

Provides a function to extract structured metadata about chats from
an exported Telegram HTML file using BeautifulSoup.
"""

import re
import logging
from bs4 import BeautifulSoup
from extractors.slugify_utils import slugify
from extractors.time_utils import parse_datetime

logger = logging.getLogger(__name__)

PIN_ICON = "\U0001F4CD"
LINK_ICON = "\U0001F517"
DATE_ICON = "\U0001F4C5"
ID_ICON = "\U0001F194"
WARNING_SIGN = "\u26A0\uFE0F"


def extract_chats(soup: BeautifulSoup) -> list[dict]:
    """
    Extract chat information from a parsed Telegram export HTML soup.

    For each chat, extracts:
      - name, slug, link, join date, and user-confirmed attributes.

    :param soup: Parsed BeautifulSoup object of the HTML
    :return: List of dictionaries with chat information
    """
    chat_data = []

    for table in soup.find_all("table"):
        caption = table.find("caption")
        if not caption:
            continue

        caption_text = caption.text.strip()
        link_tag = caption.find("a")

        name = link_tag.text.strip() if link_tag else caption_text
        name = re.sub(r"\s*\(joined the group.*?\)", "", name).strip()

        link = link_tag["href"] if link_tag and link_tag.has_attr("href") else None

        match = re.search(
            r"joined the group\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})", caption_text
        )
        joined_date = (
            parse_datetime(match.group(1), return_date_only=True) if match else None
        )

        slug = slugify(name)

        print("\n" + "=" * 30)
        print(f"{PIN_ICON}  Name: {name}")
        print(f"{LINK_ICON}  Link: {link or '(none)'}")
        print(f"{DATE_ICON}  Joined: {joined_date or '(none)'}")
        print(f"{ID_ICON}  Slug: {slug}")

        # === Prompt for chat_id ===
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
            print(f"{WARNING_SIGN}  Chat ID must be numeric or empty. Please try again.")

        # === Prompt for active/member/public ===
        is_active = input("Is this chat active? (y/n, default y): ").strip().lower() != "n"

        if is_active:
            is_member = (
                input("Are they a member of this chat? (y/n, default y): ").strip().lower()
                != "n"
            )
            is_public = (
                input("Is this chat public? (y/n, default y): ").strip().lower() != "n"
            )
        else:
            is_member = False
            is_public = False

        logger.info("[CHAT|PARSE] Chat extracted: %s | ID=%s | active=%s | member=%s",
                    slug, chat_id or "—", is_active, is_member)

        chat_data.append({
            "slug": slug,
            "chat_id": chat_id,
            "type": None,
            "name": name,
            "link": link,
            "joined": joined_date,
            "is_active": is_active,
            "is_member": is_member,
            "is_public": is_public,
            "notes": None,
            "table": table
        })

    return chat_data
