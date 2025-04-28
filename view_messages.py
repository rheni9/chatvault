import streamlit as st
import sqlite3
import pandas as pd
import ast

st.set_page_config(page_title="ChatVault Viewer", layout="wide")

DB_PATH = "messages.db"

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    chats_df = pd.read_sql("SELECT slug, chatTitle FROM chats ORDER BY chatTitle", conn)
    conn.close()
    return chats_df

# Load list of chats
chats_df = load_data()
chat_title = st.selectbox("Select a chat", chats_df["chatTitle"])
chat_slug = chats_df[chats_df["chatTitle"] == chat_title]["slug"].values[0]

# Load messages for selected chat
@st.cache_data
def load_messages(chat_slug):
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT messageid, dateTime, messageText, tags, notes
    FROM messages
    WHERE chatSlug = ?
    ORDER BY dateTime DESC
    """
    df = pd.read_sql(query, conn, params=(chat_slug,))
    conn.close()
    return df

messages_df = load_messages(chat_slug)

# Search filter
search = st.text_input("Search message text")
if search:
    messages_df = messages_df[messages_df["messageText"].str.contains(search, case=False, na=False)]

# Parse tags from JSON strings
def format_tags(t):
    try:
        parsed = ast.literal_eval(t) if isinstance(t, str) else t
        return ", ".join(parsed) if parsed else ""
    except Exception:
        return ""

messages_df["tags"] = messages_df["tags"].apply(format_tags)

# Display results
st.markdown(f"### {len(messages_df)} messages from **{chat_title}**")
st.dataframe(messages_df, use_container_width=True)
