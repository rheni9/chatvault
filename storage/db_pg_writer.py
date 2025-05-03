import json
from psycopg2.extensions import cursor as PgCursor


def ensure_tables_pg(cur: PgCursor):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            slug TEXT PRIMARY KEY,
            chat_id BIGINT,
            type TEXT,
            name TEXT,
            link TEXT,
            joined TEXT,
            is_active BOOLEAN,
            is_member BOOLEAN,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            msg_id BIGINT,
            chat_slug TEXT REFERENCES chats(slug),
            timestamp TEXT,
            link TEXT,
            text TEXT,
            media TEXT,
            screenshot TEXT,
            tags JSONB,
            notes TEXT
        )
    """)


def insert_chat_pg(cur: PgCursor, chat: dict):
    cur.execute("""
        INSERT INTO chats (
            slug, chat_id, type, name, link,
            joined, is_active, is_member, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (slug) DO UPDATE SET
            chat_id = EXCLUDED.chat_id,
            type = EXCLUDED.type,
            name = EXCLUDED.name,
            link = EXCLUDED.link,
            joined = EXCLUDED.joined,
            is_active = EXCLUDED.is_active,
            is_member = EXCLUDED.is_member,
            notes = EXCLUDED.notes
    """, (
        chat["slug"],
        chat["chat_id"],
        chat["type"],
        chat["name"],
        chat.get("link"),
        chat.get("joined"),
        chat["is_active"],
        chat["is_member"],
        chat["notes"]
    ))


def insert_message_pg(cur: PgCursor, msg: dict):
    cur.execute("""
        INSERT INTO messages (
            msg_id, chat_slug, timestamp, link, text,
            media, screenshot, tags, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        msg["msg_id"],
        msg["chat_slug"],
        msg.get("timestamp"),
        msg.get("link"),
        msg.get("text"),
        msg.get("media"),
        msg.get("screenshot"),
        json.dumps(msg.get("tags", []), ensure_ascii=False),
        msg.get("notes")
    ))
