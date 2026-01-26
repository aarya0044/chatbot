#  AI Chatbot with Persistent Memory

🔗 **Live App**: https://chatbot-00.streamlit.app/

A production-ready AI chatbot inspired by ChatGPT, built using **Streamlit** and **LangChain**, featuring **persistent multi-chat memory**, **streaming responses**, and **transparent memory explanations**.

---

##  Key Features

-  **Multi-Chat Conversations**
  - Create, switch, rename, and delete chats
  - Chat titles auto-generated from the first user message (ChatGPT-style)

-  **Persistent Memory (SQLite)**
  - All conversations are stored and restored automatically
  - Chats remain available across sessions

-  **Streaming AI Responses**
  - Token-by-token streaming using Groq LLMs
  - Fast, real-time conversational experience

-  **Transparency Mode**
  - “Why did I remember this?” explanation
  - Shows which past user input influenced the response

-  **Automatic Chat Summaries**
  - Periodic summarization of conversations
  - Stored per chat for future insights and enhancements

-  **Clean Chat UI**
  - Sidebar chat navigation
  - Hover-based rename / delete options
  - Active chat title displayed in the main view

---

##  Tech Stack

- **Frontend**: Streamlit  
- **LLM Provider**: Groq (`llama-3.1-8b-instant`)  
- **Framework**: LangChain (Core APIs)  
- **Database**: SQLite  
- **Language**: Python  

---

##  Project Structure

Terminal Chatbot/
├── app.py # Main Streamlit application
├── chatbot.db # SQLite database (auto-generated)
├── requirements.txt # Dependencies
├── README.md
├── .env # Environment variables (not committed)
└── .gitignore

---

##  Planned Enhancements

- 🔐 OAuth authentication (Google / GitHub)
- 🔗 Shareable chat links
- 📤 Export chats as PDF / Markdown
- 🧠 Long-term memory per user
- 📊 Usage analytics dashboard

---

>  This project demonstrates real-world AI application development, including state management, persistence, streaming UX, and cloud deployment.
