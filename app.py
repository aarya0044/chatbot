import os
import uuid
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from langchain.schema import HumanMessage, AIMessage

from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.callbacks.base import BaseCallbackHandler

# --------------------------------------------------
# ENV
# --------------------------------------------------
load_dotenv()
DB_FILE = "chatbot.db"

# --------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------
def get_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id TEXT PRIMARY KEY,
            username TEXT,
            title TEXT,
            summary TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            role TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# --------------------------------------------------
# STREAMING HANDLER
# --------------------------------------------------
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.container.markdown(self.text)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")
st.markdown(
    """
    <style>
    .chat-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .chat-menu {
        visibility: hidden;
    }
    .chat-row:hover .chat-menu {
        visibility: visible;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# AUTH
# --------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Login")
    username = st.text_input("Enter username")

    if st.button("Login") and username.strip():
        st.session_state.user = username.strip()
        st.rerun()

    st.stop()

# --------------------------------------------------
# DB HELPERS
# --------------------------------------------------
def get_user_chats(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT chat_id, title, summary FROM chats WHERE username=?", (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def create_chat(username):
    chat_id = str(uuid.uuid4())
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO chats VALUES (?, ?, ?, ?)",
        (chat_id, username, "New Chat", None)
    )
    conn.commit()
    conn.close()
    return chat_id

def delete_chat(chat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM chats WHERE chat_id=?", (chat_id,))
    c.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

def rename_chat(chat_id, title):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE chats SET title=? WHERE chat_id=?", (title, chat_id))
    conn.commit()
    conn.close()

def get_messages(chat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM messages WHERE chat_id=? ORDER BY id",
        (chat_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows

def save_message(chat_id, role, content):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
        (chat_id, role, content)
    )
    conn.commit()
    conn.close()

def update_summary(chat_id, summary):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE chats SET summary=? WHERE chat_id=?",
        (summary, chat_id)
    )
    conn.commit()
    conn.close()

def get_chat_title(chat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT title FROM chats WHERE chat_id=?", (chat_id,))
    title = c.fetchone()[0]
    conn.close()
    return title

def is_duplicate_title(username, title, exclude_chat_id=None):
    conn = get_db()
    c = conn.cursor()

    if exclude_chat_id:
        c.execute(
            """
            SELECT COUNT(*) FROM chats
            WHERE username=? AND title=? AND chat_id!=?
            """,
            (username, title, exclude_chat_id)
        )
    else:
        c.execute(
            """
            SELECT COUNT(*) FROM chats
            WHERE username=? AND title=?
            """,
            (username, title)
        )

    count = c.fetchone()[0]
    conn.close()
    return count > 0



# --------------------------------------------------
# FEATURE 1: TRANSPARENCY
# --------------------------------------------------
def explain_memory(messages):
    past = [m[1] for m in messages if m[0] == "user"]
    if len(past) < 2:
        return "This response did not rely on earlier memory."
    return (
        "I remembered this because earlier you said:\n\n"
        f"> *{past[-2]}*\n\n"
        "That information influenced this response."
    )

# --------------------------------------------------
# FEATURE 2: CHAT SUMMARY
# --------------------------------------------------
def generate_summary(llm, messages):
    text = "\n".join(f"{r}: {c}" for r, c in messages[-10:])
    prompt = "Summarize this conversation in 3 bullet points:\n\n" + text
    return llm.predict(prompt)

# --------------------------------------------------
# LOAD USER CHATS
# --------------------------------------------------
user_chats = get_user_chats(st.session_state.user)

# --- Ensure current_chat_id is always initialized ---
if "current_chat_id" not in st.session_state:
    if user_chats:
        st.session_state.current_chat_id = user_chats[0][0]
    else:
        st.session_state.current_chat_id = create_chat(st.session_state.user)


# Ensure current_chat_id is valid after DB changes
chat_ids = [c[0] for c in user_chats]

if not chat_ids:
    st.session_state.current_chat_id = create_chat(st.session_state.user)
elif st.session_state.current_chat_id not in chat_ids:
    st.session_state.current_chat_id = chat_ids[0]

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True):
        new_chat_id = create_chat(st.session_state.user)
        st.session_state.current_chat_id = new_chat_id
        st.rerun()

    for chat_id, title, summary in user_chats:
      col1, col2 = st.columns([6, 1])

      with col1:
        if st.button(
            title,
            key=f"open_{chat_id}",
            use_container_width=True
        ):
            st.session_state.current_chat_id = chat_id
            st.rerun()

      with col2:
        with st.popover("⋮"):
            new_title = st.text_input(
                "Rename chat",
                value=title,
                key=f"rename_{chat_id}"
            )

            if st.button("Save", key=f"save_{chat_id}"):
               clean_title = new_title.strip()

               if not clean_title:
                  st.warning("Chat name cannot be empty.")
               elif is_duplicate_title(
                  st.session_state.user,
                  clean_title,
                  exclude_chat_id=chat_id
                ):
                  st.warning("A chat with this name already exists.")
               else:
                   rename_chat(chat_id, clean_title)
                   st.rerun()


            if st.button("🗑 Delete", key=f"delete_{chat_id}"):
                delete_chat(chat_id)
                st.rerun()


    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"👤 {st.session_state.user}")

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --------------------------------------------------
# LOAD CURRENT CHAT
# --------------------------------------------------
messages = get_messages(st.session_state.current_chat_id)

memory = ConversationBufferMemory()
for role, content in messages:
    if role == "user":
        memory.chat_memory.add_message(HumanMessage(content=content))
    else:
        memory.chat_memory.add_message(AIMessage(content=content))

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    streaming=True,
    api_key=os.getenv("GROQ_API_KEY")
)

chatbot = ConversationChain(llm=llm, memory=memory)

# --------------------------------------------------
# MAIN UI
# --------------------------------------------------

current_chat_title = get_chat_title(st.session_state.current_chat_id)

st.title("🤖 AI Chatbot")
st.caption(f"🗂️ {current_chat_title}")

# Display chat history
for role, content in messages:
    with st.chat_message(role):
        st.markdown(content)

user_input = st.chat_input("Type your message...")

if isinstance(user_input, str) and user_input.strip():
    # Save user message
    save_message(st.session_state.current_chat_id, "user", user_input)

    # Auto-title (ChatGPT-style, ONLY once)
    current_title = get_chat_title(st.session_state.current_chat_id)
    if current_title == "New Chat":
        proposed_title = user_input.strip()[:40]

        if is_duplicate_title(
            st.session_state.user,
            proposed_title
        ):
            proposed_title = f"{proposed_title} (2)"

        rename_chat(
            st.session_state.current_chat_id,
            proposed_title
        )

    # Assistant response (streaming)
    with st.chat_message("assistant"):
        container = st.empty()
        handler = StreamHandler(container)

        response = chatbot.predict(
            input=user_input,
            callbacks=[handler]
        )

    save_message(st.session_state.current_chat_id, "assistant", response)

    # Transparency
    st.session_state.last_explanation = explain_memory(
        get_messages(st.session_state.current_chat_id)
    )

    with st.expander("🧠 Why did I remember this?"):
        st.markdown(st.session_state.last_explanation)

    # Auto summary every 4 messages
    all_msgs = get_messages(st.session_state.current_chat_id)
    if len(all_msgs) % 4 == 0:
        summary = generate_summary(llm, all_msgs)
        update_summary(st.session_state.current_chat_id, summary)
