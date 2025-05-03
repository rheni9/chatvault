"""
Main script for extracting and storing Telegram chat export data.

This script performs the following steps:

1. Loads the HTML file exported from Telegram (via parser.get_input_html).
2. Parses the content into a BeautifulSoup object (via parser.html_loader).
3. Extracts chat metadata (via parser.chat_extractor).
4. For each chat:
   - Extracts its messages (parser.message_extractor).
   - Saves the chat summary into a JSON file (storage.json_writer).
   - Saves all messages into a chat-specific JSON file.
   - Inserts chat and messages into the SQLite database (storage.db_writer).

JSON files are stored in:    ./data/json/
SQLite database is stored in: ./db/chatvault.sqlite

The script processes chats one by one and commits data after each.
It exits gracefully if interrupted (Ctrl+C).
"""

import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

from extractors.html_loader import load_html
from extractors.get_input_html import get_input_html_path
from extractors.chat_extractor import extract_chats
from extractors.message_extractor import extract_messages
from storage.json_writer import save_chat_summary, save_messages_to_json
from storage.db_writer import ensure_tables, insert_chat, insert_message
from storage.db_pg_writer import (
    ensure_tables_pg, insert_chat_pg, insert_message_pg
)

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "db", "chatvault.sqlite")
)

load_dotenv()
PG_URL = os.getenv("DATABASE_URL")


def main():
    """
    Main execution logic for parsing Telegram export and saving data.

    Loads and parses the HTML file, extracts chat metadata and messages,
    saves JSON files, and inserts data into the SQLite database.

    Prompts the user for chat_id during processing.
    """
    path = get_input_html_path()
    soup = load_html(path)
    chats = extract_chats(soup)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    sqlite_conn = sqlite3.connect(DB_PATH)
    sqlite_cur = sqlite_conn.cursor()
    ensure_tables(sqlite_cur)

    pg_conn = psycopg2.connect(PG_URL)
    pg_cur = pg_conn.cursor()
    ensure_tables_pg(pg_cur)

    total_messages = 0

    for chat in chats:
        messages = extract_messages(chat["table"], chat["slug"])

        save_chat_summary(chat)
        save_messages_to_json(chat["slug"], messages)

        insert_chat(sqlite_cur, chat)
        insert_chat_pg(pg_cur, chat)

        for msg in messages:
            insert_message(sqlite_cur, msg)
            insert_message_pg(pg_cur, msg)

        sqlite_conn.commit()
        pg_conn.commit()

        total_messages += len(messages)

        print(
            f"\n\u2705 Saved chat '{chat['slug']}' "
            f"with {len(messages)} messages."
        )

    sqlite_cur.close()
    sqlite_conn.close()
    pg_cur.close()
    pg_conn.close()

    print("\n\u2705 All chats and messages processed successfully.")
    print(f"\U0001F5C2️  Chats processed: {len(chats)}")
    print(f"\U0001F4AC  Total messages: {total_messages}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user. Exiting gracefully.")
