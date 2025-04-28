import os
import re
from bs4 import BeautifulSoup
import unicodedata
import json
from datetime import datetime
from zoneinfo import ZoneInfo

HTML_PATH = "565235492_messages.html"

# Output folder path
OUTPUT_DIR = "messages"

# Ensure the directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Basic Ukrainian/Russian to Latin map
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
    text = re.sub(r"[^a-z0-9 ]", "", text)      # Remove non-alphanum (keep spaces)
    words = text.strip().split()
    return "_".join(words[:max_words]) or "chat"

# Read and parse the HTML file
with open(HTML_PATH, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "lxml")

tables = soup.find_all("table")
chat_names = [t.caption.get_text(strip=True) for t in tables]

# Let the user select which chat to parse
print("Available chats:")
for i, name in enumerate(chat_names):
    print(f"{i + 1}. {name}")

selected_index = int(input("Select a chat by number: ")) - 1
selected_table = tables[selected_index]
caption = selected_table.caption
raw_caption = caption.get_text(strip=True) if caption else ""
chat_link = caption.find("a")["href"] if caption and caption.find("a") else None

joined_date = None
chat_name = raw_caption

# Extract "joined the group" date, if present
match = re.search(r"joined the group\s*(\d{2}\.\d{2}\.\d{4})", raw_caption, re.IGNORECASE)
if match:
    date_str = match.group(1)
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        joined_date = dt.date().isoformat()  # Format: YYYY-MM-DD
    except ValueError:
        joined_date = None

    # Remove the "joined the group..." text from the chat name
    chat_name = re.sub(r"joined the group\s*\d{2}\.\d{2}\.\d{4}", "", raw_caption, flags=re.IGNORECASE).strip()
    # Remove empty brackets left behind
    chat_name = re.sub(r"\(\s*\)", "", chat_name).strip()

chat_slug = slugify(chat_name)

# Ask user to enter chat ID (optional)
chat_id_input = input(f'Enter chat ID for "{chat_name}" (or press Enter to skip): ').strip()
chat_id = None
if chat_id_input:
    try:
        chat_id = int(chat_id_input)
    except ValueError:
        print("⚠️ Invalid chat ID, skipping.")

# Parse messages
rows = selected_table.find("tbody").find_all("tr")
messages = []

kyiv_tz = ZoneInfo("Europe/Kyiv")
utc_tz = ZoneInfo("UTC")

for row in rows:
    cols = row.find_all("td")
    if len(cols) < 3:
        continue

    msg_id = cols[0].get_text(strip=True)
    msg_link = cols[0].find("a")["href"] if cols[0].find("a") else None
    date_str = cols[1].get_text(strip=True)

    # Convert Kyiv time to UTC
    try:
        dt_kyiv = datetime.strptime(date_str, "%H:%M:%S %d.%m.%Y").replace(tzinfo=kyiv_tz)
        dt_utc = dt_kyiv.astimezone(utc_tz)
        date_iso = dt_utc.isoformat().replace("+00:00", "Z")
    except ValueError:
        date_iso = date_str  # Fallback if parsing fails

    # Get raw text with line breaks
    raw_text = cols[2].get_text(separator="\n")
    message_text = "\n".join(line.strip() for line in raw_text.splitlines())

    messages.append({
        "chatid": chat_id,
        "chatTitle": chat_name,
        "chatLink": chat_link,
        "joinedDate": joined_date,
        "messageid": msg_id,        
        "dateTime": date_iso,
        "messageText": message_text,
        "messageLink": msg_link,
        "imagePath": None,
        "screenshotPath": None,
        "tags": [],
        "notes": ""
    })

# Generate full output path
OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"messages_{chat_slug}.json")

# Save messages to JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as out_file:
    json.dump(messages, out_file, ensure_ascii=False, indent=2)

print(f"\n✅ Saved {len(messages)} messages from '{chat_name}' to: {OUTPUT_PATH}")
