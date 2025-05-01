"""
Main script for extracting Telegram chat information from exported HTML files.
"""

import sys
import re
from bs4 import BeautifulSoup
from slugify_utils import slugify
from html_loader import load_html
from get_input_html import get_input_html_path
from time_utils import parse_datetime

PIN_ICON = "\U0001F4CD"
LINK_ICON = "\U0001F517"
DATE_ICON = "\U0001F4C5"
ID_ICON = "\U0001F194"
CHECK_ICON = "\u2705"
INFO_ICON = "\u2139"
WARNING_SIGN = "\u26A0\uFE0F"


def extract_chats(soup: BeautifulSoup) -> list[dict]:
    """
    Extract chat information from a parsed Telegram export HTML soup.

    For each chat, extracts:
        - name
        - slug (generated from name)
        - link (if present)
        - join date (if found and parseable)
        - optional chat_id entered by user (numeric only)

    :param soup: Parsed BeautifulSoup object of the HTML
    :type soup: bs4.BeautifulSoup
    :return: List of dictionaries with chat information
    :rtype: list[dict]
    """
    chat_data = []

    for table in soup.find_all("table"):
        caption = table.find("caption")
        if not caption:
            continue

        link_tag = caption.find("a")
        name = link_tag.text.strip() if link_tag else caption.text.strip()
        link = (
            link_tag["href"]
            if link_tag and link_tag.has_attr("href")
            else None
        )

        match = re.search(
            r"joined the group\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
            caption.text
        )
        joined_date = parse_datetime(match.group(1)) if match else None
        slug = slugify(name)

        print("\n" + "=" * 30)
        print(f"{PIN_ICON}  Name: {name}")
        print(f"{LINK_ICON}  Link: {link or '(none)'}")
        print(f"{DATE_ICON}  Joined: {joined_date or '(none)'}")
        print(f"{ID_ICON}  Slug: {slug}")

        chat_id_input = input(
            "Enter chat_id (digits only, or press Enter to skip): "
        ).strip()
        chat_id = int(chat_id_input) if chat_id_input.isdigit() else None

        chat_data.append({
            "name": name,
            "slug": slug,
            "link": link,
            "joined": joined_date,
            "chat_id": chat_id
        })

    return chat_data


def main() -> None:
    """
    Entry point for running the chat extraction process.
    Handles graceful interruption and displays final count.
    """
    try:
        path = get_input_html_path()
        soup = load_html(path)
        chats = extract_chats(soup)

        print(f"\n{CHECK_ICON}  Total chats processed: {len(chats)}")

    except KeyboardInterrupt:
        print(f"\n\n{INFO_ICON}  Interrupted by user. Exiting gracefully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
