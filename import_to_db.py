import os
import json
import sqlite3

DB_PATH = "messages.db"
MESSAGES_DIR = "messages"
CHAT_FILE = os.path.join(MESSAGES_DIR, "chats.json")

# --- Create tables ---
def setup_db(conn):
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chatTitle TEXT,
        slug TEXT UNIQUE,
        chatLink TEXT,
        joinedDate TEXT,
        chatid INTEGER
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chatSlug TEXT,
        messageid TEXT,
        dateTime TEXT,
        messageText TEXT,
        messageLink TEXT,
        imagePath TEXT,
        screenshotPath TEXT,
        tags TEXT,
        notes TEXT,
        FOREIGN KEY (chatSlug) REFERENCES chats(slug)
    )""")

    conn.commit()

# --- Import chats ---
def import_chats(conn):
    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        chats = json.load(f)

    cur = conn.cursor()
    for chat in chats:
        cur.execute("""
        INSERT OR IGNORE INTO chats (chatTitle, slug, chatLink, joinedDate, chatid)
        VALUES (?, ?, ?, ?, ?)
        """, (
            chat["chatTitle"],
            chat["slug"],
            chat.get("chatLink"),
            chat.get("joinedDate"),
            chat.get("chatid")
        ))
    conn.commit()
    print(f"✅ Imported {len(chats)} chats")

# --- Import all messages ---
def import_messages(conn):
    cur = conn.cursor()
    total = 0

    for fname in os.listdir(MESSAGES_DIR):
        if fname.startswith("messages_") and fname.endswith(".json"):
            fpath = os.path.join(MESSAGES_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                msgs = json.load(f)

            for msg in msgs:
                cur.execute("""
                INSERT INTO messages (
                    chatSlug, messageid, dateTime, messageText, messageLink,
                    imagePath, screenshotPath, tags, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg["chatSlug"],
                    msg["messageid"],
                    msg["dateTime"],
                    msg["messageText"],
                    msg.get("messageLink"),
                    msg.get("imagePath"),
                    msg.get("screenshotPath"),
                    json.dumps(msg.get("tags", [])),
                    msg.get("notes", "")
                ))
            total += len(msgs)
            print(f"   📥 {len(msgs)} from {fname}")

    conn.commit()
    print(f"✅ Total messages imported: {total}")

# --- MAIN ---
def main():
    conn = sqlite3.connect(DB_PATH)
    setup_db(conn)
    import_chats(conn)
    import_messages(conn)
    conn.close()
    print(f"\n🎉 Done. All data saved to {DB_PATH}")

if __name__ == "__main__":
    main()
