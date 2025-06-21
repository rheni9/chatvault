"""
PostgreSQL table cleanup script for the Arcanum application.

This script connects to the PostgreSQL database using credentials
from the environment and drops the `messages` and `chats` tables
if they exist. Intended for development or reset purposes only.
"""

import os
import logging
import psycopg2
from dotenv import load_dotenv

# === Load environment ===
load_dotenv()
PG_URL = os.getenv("DATABASE_URL")

# === Logger configuration ===
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def drop_tables() -> None:
  """
    Drop the 'messages' and 'chats' tables if they exist.

    Connects to the PostgreSQL database using the `DATABASE_URL`
    environment variable. Executes SQL statements to drop both
    tables and commits the changes.

    :raises psycopg2.DatabaseError: If connection or execution fails.
    """
  logger.info("[DROP] Connecting to PostgreSQL...")
  try:
    conn = psycopg2.connect(PG_URL)
    cur = conn.cursor()

    logger.info("[DROP] Dropping 'messages' and 'chats' tables (if exist)...")
    cur.execute("DROP TABLE IF EXISTS messages;")
    cur.execute("DROP TABLE IF EXISTS chats;")

    conn.commit()
    logger.info("✅ Tables 'messages' and 'chats' deleted successfully.")

  except psycopg2.DatabaseError as e:
    logger.error("[DROP] Database error: %s", e)
    raise
  finally:
    if cur:
      cur.close()
    if conn:
      conn.close()
    logger.info("[DROP] Connection closed.")


if __name__ == "__main__":
  try:
    drop_tables()
  except KeyboardInterrupt:
    logger.warning("[INTERRUPT] Operation cancelled by user.")
