# Arcanum ChatVault Parser

A flexible parser for extracting Telegram chat and message data from HTML exports, saving structured data to SQLite and PostgreSQL, and generating intermediate JSON files.

---

## 📦 Requirements

- Python 3.12+
- PostgreSQL server
- See `requirements.txt` for dependencies:
  - `beautifulsoup4`, 
  - `lxml`,
  - `psycopg2-binary`,
  - `python-dateutil`,
  - `python-dotenv`,
  - `pytz`

---

## 📂 Project Structure

```graphql
.
├── main.py              # Entrypoint: parse HTML, write to DB/JSON
├── delete.py            # Drop PostgreSQL and SQLite tables
├── docker-compose.yml   # PostgreSQL container for local development
├── .env.example         # Template for env config
├── requirements.txt     # pip dependencies
├── pyproject.toml       # Poetry config
├── poetry.lock          # Poetry lockfile
├── LICENSE
├── README.md

├── data/
│   ├── html/            # Place exported Telegram HTML files here (.gitkeep)
│   └── json/            # Saved chat/message JSON snapshots (auto-created)

├── db/                  # Local SQLite database folder (auto-created)

├── extractors/          # HTML parsing utilities
│   ├── __init__.py
│   ├── chat_extractor.py      # Extract chat metadata
│   ├── message_extractor.py   # Extract messages from tables
│   ├── get_input_html.py      # Locate input HTML file
│   ├── html_loader.py         # Load HTML with BeautifulSoup
│   ├── slugify_utils.py       # Slugify and transliteration helpers
│   └── time_utils.py          # Flexible date/time parsing

├── storage/             # Writers for DB and JSON
│   ├── __init__.py
│   ├── db_writer.py           # SQLite tables and inserts
│   ├── db_pg_writer.py        # PostgreSQL tables and inserts
│   └── json_writer.py         # Save chats/messages as JSON
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
# ============================================
# PostgreSQL connection URI (SQLAlchemy style)
# ============================================
PG_DATABASE_URL=postgresql://your_pg_user:your_pg_password@your_pg_host:5432/your_pg_database

# ============================================
# PostgreSQL individual components (optional)
# ============================================
PG_USER=your_pg_user
PG_PASSWORD=your_pg_password
PG_HOST=your_pg_host
PG_PORT=5432
PG_DATABASE=your_pg_database

# ============================================
# SQLite local file path
# ============================================
SQLITE_PATH=./db/chatvault.sqlite
```

---

## 🐳 Run PostgreSQL with Docker

You can run PostgreSQL using the provided `docker-compose.yml`:

```bash
docker compose up -d
```

Stop containers:

```bash
docker compose down
```

---

## 🚀 Run

Install dependencies:

```bash
# Using Poetry
poetry install --no-root

# Or using pip
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the parser:

```bash
python main.py
```

- You will be prompted to select a Telegram HTML file (or pass it as an argument).

- During parsing, you will be asked for:
  - **Chat ID** — optional, can be skipped by pressing Enter.
  - **Is the chat active?** — default: **Yes**
  - If active: 
    - **Are they a member of the chat?** — default: **Yes**
    - **Is the chat public?** — default: **Yes**

---

## 🗑️ Drop tables:

Drop both PostgreSQL and SQLite tables:
```bash
python delete.py
```
Drop only PostgreSQL tables:
```bash
python delete.py --pg-only
```

Drop only SQLite tables:
```bash
python delete.py --sqlite-only
```
