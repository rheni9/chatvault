import os
import re
import json
import unicodedata
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

HTML_PATH = "565235492_messages.html"
OUTPUT_DIR = "messages"
CHAT_LIST_PATH = os.path.join(OUTPUT_DIR, "chats.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Transliteration ---
CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "h", "ґ": "g", "д": "d", "е": "e", "є": "ie", "ж": "zh",
    "з": "z", "и": "y", "і": "i", "ї": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "shch", "ь": "", "ю": "iu", "я": "ia"
}

def transliterate(text):
    return ''.join(CYR_TO_LAT.get(char, char) for char in text.lower())

def slugify(text, max_words=3):
    text = unicodedata.normalize("NFKD", text)
    text = transliterate(text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    words = text.strip().split()
    return "_".join(words[:max_words]) or "chat"

# --- Load HTML ---
with open(HTML_PATH, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "lxml")

tables = soup.find_all("table")

# --- Load existing chat list ---
if os.path.exists(CHAT_LIST_PATH):
    with open(CHAT_LIST_PATH, "r", encoding="utf-8") as f:
        all_chats = json.load(f)
else:
    all_chats = []

existing_slugs = {c["slug"] for c in all_chats}
kyiv_tz = ZoneInfo("Europe/Kyiv")
utc_tz = ZoneInfo("UTC")

# --- Process each chat ---
for i, table in enumerate(tables):
    caption = table.caption
    raw_caption = caption.get_text(strip=True) if caption else ""
    chat_link = caption.find("a")["href"] if caption and caption.find("a") else None

    # --- Extract joined date ---
    joined_date = None
    chat_name = raw_caption
    match = re.search(r"joined the group\s*(\d{2}\.\d{2}\.\d{4})", raw_caption, re.IGNORECASE)
    if match:
        try:
            dt = datetime.strptime(match.group(1), "%d.%m.%Y")
            joined_date = dt.date().isoformat()
        except ValueError:
            joined_date = None
        chat_name = re.sub(r"joined the group\s*\d{2}\.\d{2}\.\d{4}", "", raw_caption, flags=re.IGNORECASE).strip()
        chat_name = re.sub(r"\(\s*\)", "", chat_name).strip()

    chat_slug = slugify(chat_name)

    print(f"\n🔹 Chat {i+1}/{len(tables)}: {chat_name}")
    print(f"   Slug: {chat_slug}")
    if chat_link:
        print(f"   Link: {chat_link}")
    if joined_date:
        print(f"   Joined: {joined_date}")

    # Ask user for chat ID
    chat_id_input = input("   Enter chat ID (or press Enter to skip): ").strip()
    chat_id = None
    if chat_id_input:
        try:
            chat_id = int(chat_id_input)
        except ValueError:
            print("   ⚠️ Invalid chat ID, skipping.")

    # --- Save chat info if not already saved ---
    if chat_slug not in existing_slugs:
        all_chats.append({
            "chatTitle": chat_name,
            "chatLink": chat_link,
            "joinedDate": joined_date,
            "chatid": chat_id,
            "slug": chat_slug
        })
        existing_slugs.add(chat_slug)

    # --- Extract messages ---
    rows = table.find("tbody").find_all("tr")
    messages = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        msg_id = cols[0].get_text(strip=True)
        msg_link = cols[0].find("a")["href"] if cols[0].find("a") else None
        date_str = cols[1].get_text(strip=True)

        try:
            dt_kyiv = datetime.strptime(date_str, "%H:%M:%S %d.%m.%Y").replace(tzinfo=kyiv_tz)
            dt_utc = dt_kyiv.astimezone(utc_tz)
            date_iso = dt_utc.isoformat().replace("+00:00", "Z")
        except ValueError:
            date_iso = date_str

        raw_text = cols[2].get_text(separator="\n")
        message_text = "\n".join(line.strip() for line in raw_text.splitlines())

        messages.append({
            "chatSlug": chat_slug,
            "messageid": msg_id,
            "dateTime": date_iso,
            "messageText": message_text,
            "messageLink": msg_link,
            "imagePath": None,
            "screenshotPath": None,
            "tags": [],
            "notes": ""
        })

    # --- Save messages ---
    msg_path = os.path.join(OUTPUT_DIR, f"messages_{chat_slug}.json")
    with open(msg_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print(f"   ✅ Saved {len(messages)} messages → {msg_path}")

# --- Save chats.json ---
with open(CHAT_LIST_PATH, "w", encoding="utf-8") as f:
    json.dump(all_chats, f, ensure_ascii=False, indent=2)

print(f"\n📋 Updated chats list → {CHAT_LIST_PATH}")
