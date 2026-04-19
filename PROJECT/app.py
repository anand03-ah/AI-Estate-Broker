import streamlit as st
import os
import sqlite3
from datetime import datetime
from groq import Groq
from hindsight import Hindsight

# =========================
# 🔐 CONFIG
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing")
    st.stop()

if not HINDSIGHT_API_KEY:
    st.error("❌ HINDSIGHT_API_KEY missing")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
hindsight = Hindsight(api_key=HINDSIGHT_API_KEY)

# =========================
# 💾 DATABASE (SQLite)
# =========================
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session TEXT,
    role TEXT,
    content TEXT,
    timestamp TEXT
)
""")
conn.commit()

# =========================
# 🎨 PAGE CONFIG
# =========================
st.set_page_config(page_title="estate broker AI", layout="wide")

# =========================
# 🎨 CHATGPT STYLE UI
# =========================
st.markdown("""
<style>
body {
    background-color: #343541;
    color: white;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 6rem;
}

.user-bubble {
    background: #0b93f6;
    color: white;
    padding: 10px;
    border-radius: 12px;
    margin: 5px 0;
    text-align: right;
}

.bot-bubble {
    background: #444654;
    color: white;
    padding: 10px;
    border-radius: 12px;
    margin: 5px 0;
    text-align: left;
}

/* input fixed bottom look */
.stChatInput {
    position: fixed;
    bottom: 10px;
    width: 70%;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 💾 SESSION STATE
# =========================
if "session" not in st.session_state:
    st.session_state.session = "Chat 1"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "sessions" not in st.session_state:
    st.session_state.sessions = {"Chat 1": []}

# =========================
# 📌 SIDEBAR (CHAT HISTORY)
# =========================
with st.sidebar:
    st.title("💬 Chats")

    if st.button("➕ New Chat"):
        new_name = f"Chat {len(st.session_state.sessions)+1}"
        st.session_state.sessions[new_name] = []
        st.session_state.session = new_name

    for s in st.session_state.sessions:
        if st.button(s):
            st.session_state.session = s

    st.markdown("---")
    st.caption("AI estate Broker")

# =========================
# LOAD CURRENT CHAT
# =========================
st.session_state.messages = st.session_state.sessions[st.session_state.session]

# =========================
# 🧠 TITLE
# =========================
st.title("🤖 AI estate Broker ")
st.caption("using Hindsight and groq")

# =========================
# 💬 DISPLAY CHAT
# =========================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

# =========================
# ✍️ INPUT
# =========================
user_input = st.chat_input("any land enquiry ...")

if user_input:

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    cursor.execute(
        "INSERT INTO messages (session, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (st.session_state.session, "user", user_input, timestamp)
    )
    conn.commit()

    # =========================
    # 🤖 GROQ RESPONSE
    # =========================
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.messages,
            temperature=0.7
        )
        bot_reply = response.choices[0].message.content

    except Exception as e:
        bot_reply = f"Error: {e}"

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    cursor.execute(
        "INSERT INTO messages (session, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (st.session_state.session, "assistant", bot_reply, timestamp)
    )
    conn.commit()

    # =========================
    # 🧠 HINDSIGHT LOG
    # =========================
    try:
        hindsight.save({
            "input": user_input,
            "output": bot_reply,
            "session": st.session_state.session,
            "timestamp": timestamp
        })
    except:
        pass

    st.rerun()