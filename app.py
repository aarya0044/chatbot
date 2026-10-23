"""
TermiPilot Web Dashboard (Streamlit).
Ultra-Modern, Developer-Grade AI Chatbot & DevOps Copilot.
"""
import os
import streamlit as st
from dotenv import load_dotenv

from core.memory import DatabaseManager
from core.agent import TermiPilotAgent
from core.safety import SafetyEngine, RiskLevel

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="TermiPilot | Autonomous AI DevOps Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# ULTRA-MODERN CUSTOM CSS & THEMING
# --------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1050px;
    }

    /* Gradient Brand Text */
    .brand-title {
        background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 1.8rem;
        letter-spacing: -0.5px;
        display: inline-block;
    }
    
    .brand-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 2px 10px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-left: 8px;
        vertical-align: middle;
    }

    /* Hero / Empty State Card */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        border-radius: 20px;
        background: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.12) 0%, rgba(15, 23, 42, 0) 70%);
        margin-bottom: 2rem;
    }
    .hero-icon {
        font-size: 3rem;
        display: inline-block;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 20px rgba(96, 165, 250, 0.4));
    }
    .hero-headline {
        font-size: 1.85rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 0.4rem;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        font-size: 0.95rem;
        color: #94A3B8;
        max-width: 580px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* Prompt Suggestion Cards */
    .prompt-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(51, 65, 85, 0.8);
        border-radius: 14px;
        padding: 14px 16px;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
        height: 100%;
    }
    .prompt-card:hover {
        background: rgba(51, 65, 85, 0.7);
        border-color: #6366F1;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
    }
    .prompt-card-icon {
        font-size: 1.3rem;
        margin-bottom: 6px;
    }
    .prompt-card-title {
        font-weight: 600;
        font-size: 0.88rem;
        color: #F1F5F9;
        margin-bottom: 4px;
    }
    .prompt-card-desc {
        font-size: 0.78rem;
        color: #94A3B8;
        line-height: 1.3;
    }

    /* Chat Messages Styling */
    .stChatMessage {
        border-radius: 14px !important;
        margin-bottom: 1rem !important;
        padding: 1rem 1.2rem !important;
        background-color: #0F172A !important;
        border: 1px solid rgba(51, 65, 85, 0.5) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Assistant Chat Message Custom Accent */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
    }

    /* Tool Execution Card */
    .tool-box {
        background: #020617;
        border: 1px solid #1E293B;
        border-left: 3px solid #6366F1;
        border-radius: 10px;
        padding: 12px 14px;
        margin: 10px 0;
        font-size: 0.85rem;
    }
    .tool-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #A5B4FC;
        font-weight: 600;
        margin-bottom: 6px;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #090D16 !important;
        border-right: 1px solid rgba(30, 41, 59, 0.8);
    }
    
    /* Sleek buttons */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Modern Chat Input */
    .stChatInput {
        border-radius: 16px !important;
    }
    .stChatInput>div {
        border-radius: 14px !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        background: #0F172A !important;
    }
    .stChatInput>div:focus-within {
        border-color: #818CF8 !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.25) !important;
    }

    /* Custom Metric Cards */
    .metric-pill {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(51, 65, 85, 0.6);
        border-radius: 12px;
        padding: 14px;
        text-align: center;
    }
    .metric-num {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .metric-lbl {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# INITIALIZE DATABASE & SESSION STATE
# --------------------------------------------------
db = DatabaseManager()

if "user" not in st.session_state:
    st.session_state.user = None

if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = None

# Login Screen
if st.session_state.user is None:
    st.markdown("""
        <div style="text-align:center; padding-top: 5rem;">
            <div style="font-size: 3.5rem;">⚡</div>
            <div class="brand-title">TermiPilot</div>
            <p style="color: #94A3B8; margin-top: 8px;">Autonomous AI DevOps & Terminal Copilot</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.container(border=True):
            st.markdown("#### Operator Login")
            username = st.text_input("Username", value="developer", placeholder="Enter your handle...")
            if st.button("Access Copilot →", use_container_width=True, type="primary") and username.strip():
                st.session_state.user = username.strip()
                st.rerun()
    st.stop()

# --------------------------------------------------
# SIDEBAR: SESSIONS & USER PROFILE
# --------------------------------------------------
user_chats = db.get_user_chats(st.session_state.user)

if "current_chat_id" not in st.session_state:
    if user_chats:
        st.session_state.current_chat_id = user_chats[0]["chat_id"]
    else:
        st.session_state.current_chat_id = db.create_chat(st.session_state.user, "DevOps Session 1")
        user_chats = db.get_user_chats(st.session_state.user)

chat_ids = [c["chat_id"] for c in user_chats]
if not chat_ids:
    st.session_state.current_chat_id = db.create_chat(st.session_state.user, "DevOps Session 1")
    user_chats = db.get_user_chats(st.session_state.user)
elif st.session_state.current_chat_id not in chat_ids:
    st.session_state.current_chat_id = chat_ids[0]

with st.sidebar:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom: 1.2rem;">
            <span style="font-size: 1.8rem;">⚡</span>
            <div>
                <span class="brand-title" style="font-size: 1.4rem;">TermiPilot</span>
                <span class="brand-badge">Agentic</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("＋ New Chat", use_container_width=True, type="primary"):
        new_id = db.create_chat(st.session_state.user, f"DevOps Session {len(user_chats) + 1}")
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("<p style='font-size:0.75rem; font-weight:600; color:#64748B; text-transform:uppercase; letter-spacing:0.5px; margin-top:1.2rem; margin-bottom:0.5rem;'>Your Conversations</p>", unsafe_allow_html=True)
    
    for chat in user_chats:
        c_id = chat["chat_id"]
        title = chat["title"] or "Untitled Chat"
        is_active = (c_id == st.session_state.current_chat_id)
        
        col_btn, col_opt = st.columns([5, 1])
        with col_btn:
            btn_style = f"💬 {title}" if not is_active else f"⚡ {title}"
            if st.button(btn_style, key=f"session_{c_id}", use_container_width=True, type="secondary" if not is_active else "primary"):
                st.session_state.current_chat_id = c_id
                st.rerun()

        with col_opt:
            with st.popover("⋮"):
                new_title = st.text_input("Rename", value=title, key=f"ren_{c_id}")
                if st.button("Save", key=f"save_ren_{c_id}", use_container_width=True):
                    if new_title.strip():
                        db.rename_chat(c_id, new_title.strip())
                        st.rerun()
                if st.button("🗑 Delete", key=f"del_{c_id}", type="secondary", use_container_width=True):
                    db.delete_chat(c_id)
                    st.rerun()

    st.markdown("<div style='flex:1; min-height: 50px;'></div>", unsafe_allow_html=True)
    st.divider()

    # User Profile Pill
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding: 6px 0;">
            <div style="width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#6366F1,#EC4899); display:flex; align-items:center; justify-content:center; font-weight:bold; color:white;">
                {st.session_state.user[0].upper()}
            </div>
            <div style="flex:1; overflow:hidden;">
                <div style="font-weight:600; font-size:0.85rem; color:#F1F5F9; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{st.session_state.user}</div>
                <div style="font-size:0.72rem; color:#10B981;">● Groq LPU Online</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --------------------------------------------------
# MAIN UI: HEADER & TABS
# --------------------------------------------------
# Find current chat title
current_title = "DevOps Session"
for c in user_chats:
    if c["chat_id"] == st.session_state.current_chat_id:
        current_title = c["title"]
        break

# Top Status Bar
col_header_title, col_header_tools = st.columns([3, 2])
with col_header_title:
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom: 0.5rem;">
            <h2 style="margin:0; font-weight:700; font-size:1.45rem; letter-spacing:-0.5px;">{current_title}</h2>
        </div>
    """, unsafe_allow_html=True)
with col_header_tools:
    st.session_state.auto_approve_mutations = st.toggle(
        "🛡️ Auto-Authorize Safe Mutations",
        value=False,
        help="When OFF, commands that alter or delete files will be blocked unless explicitly permitted."
    )

tab_copilot, tab_audit, tab_benchmark = st.tabs([
    "💬 AI Copilot",
    "🛡️ Live Audit Trail",
    "📐 Architecture & Viva Synopsis"
])

def web_approval_handler(command: str, reason: str) -> bool:
    return st.session_state.get("auto_approve_mutations", False)

agent = TermiPilotAgent(
    db_manager=db,
    approval_callback=web_approval_handler
)

# --------------------------------------------------
# TAB 1: COPILOT CONVERSATION
# --------------------------------------------------
with tab_copilot:
    messages = db.get_messages(st.session_state.current_chat_id)

    # If new chat with no messages, show modern ChatGPT-style welcome hero + suggestions
    if not messages:
        st.markdown("""
            <div class="hero-container">
                <div class="hero-icon">⚡</div>
                <div class="hero-headline">How can TermiPilot assist you today?</div>
                <div class="hero-sub">
                    An autonomous agent equipped with real-time shell execution, sandboxed Python computation, workspace file inspection, and technical web research.
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 4 Prompt Suggestions
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("📁 Inspect Workspace\n\nList and summarize all files in this project repository.", use_container_width=True):
                st.session_state.preset_prompt = "Inspect all files in the current repository and summarize their technical roles."
                st.rerun()
            if st.button("💻 System Diagnostics\n\nCheck operating system specs, installed Python version, and network.", use_container_width=True):
                st.session_state.preset_prompt = "Run system diagnostics: check Python version, OS release, and current environment specs."
                st.rerun()
        with sc2:
            if st.button("🧮 Python Sandbox REPL\n\nCompute the first 25 Fibonacci numbers and verify prime numbers.", use_container_width=True):
                st.session_state.preset_prompt = "Write and execute sandboxed Python code to calculate the first 25 Fibonacci numbers and find which ones are prime."
                st.rerun()
            if st.button("🌐 Live Tech Documentation\n\nSearch DuckDuckGo for Groq function-calling best practices.", use_container_width=True):
                st.session_state.preset_prompt = "Search the web for the latest documentation on Groq LPU tool calling and function arguments."
                st.rerun()

    # Render Chat History
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "⚡"):
            st.markdown(content)

    # Handle preset clicks or chat input
    prompt_to_run = None
    if st.session_state.preset_prompt:
        prompt_to_run = st.session_state.preset_prompt
        st.session_state.preset_prompt = None
    else:
        user_input = st.chat_input("Ask TermiPilot to run commands, inspect code, or diagnose issues...")
        if user_input:
            prompt_to_run = user_input

    if prompt_to_run:
        # User message
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt_to_run)

        # Assistant turn
        with st.chat_message("assistant", avatar="⚡"):
            status_container = st.status("🧠 **TermiPilot** is reasoning and planning...", expanded=True)

            def web_status_hook(event_type: str, tool_name: str, data: dict):
                if event_type == "tool_start":
                    status_container.markdown(f"⚡ **Invoking Tool:** `{tool_name}`")
                    status_container.code(str(data), language="json")
                elif event_type == "tool_end":
                    res_status = data.get("status", "done")
                    status_container.markdown(f"✓ Tool `{tool_name}` finished with status: `{res_status}`")

            # Run agent turn
            res = agent.run_step(
                chat_id=st.session_state.current_chat_id,
                user_message=prompt_to_run,
                status_callback=web_status_hook
            )

            status_container.update(
                label=f"✓ Completed in {res['latency_sec']:.2f}s ({len(res['tool_executions'])} tools executed)",
                state="complete",
                expanded=False
            )

            st.markdown(res["reply"])

        st.rerun()

# --------------------------------------------------
# TAB 2: AUDIT TRAIL & SYSTEM METRICS
# --------------------------------------------------
with tab_audit:
    st.markdown("### 🛡️ Real-Time Tool Execution Audit Trail")
    st.caption("Every system command, Python script, or file access executed by the agent is logged with security classification and millisecond latency.")

    audit_logs = db.get_audit_logs(limit=40)
    if not audit_logs:
        st.info("No tool executions recorded yet in this session.")
    else:
        total_runs = len(audit_logs)
        safe_runs = sum(1 for l in audit_logs if l["risk_level"] == "SAFE")
        mod_runs = sum(1 for l in audit_logs if l["risk_level"] in ["MODERATE", "CRITICAL"])
        avg_lat = sum(l["duration_ms"] for l in audit_logs) / max(total_runs, 1)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class="metric-pill"><div class="metric-num">{total_runs}</div><div class="metric-lbl">Total Executions</div></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-pill"><div class="metric-num" style="color:#10B981;">{safe_runs}</div><div class="metric-lbl">Safe Operations</div></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class="metric-pill"><div class="metric-num" style="color:#F59E0B;">{mod_runs}</div><div class="metric-lbl">Gated Interceptions</div></div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class="metric-pill"><div class="metric-num" style="color:#60A5FA;">{avg_lat:.1f}ms</div><div class="metric-lbl">Average Latency</div></div>""", unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        for log in audit_logs:
            badge_color = "#10B981" if log['risk_level'] == "SAFE" else "#F59E0B"
            with st.expander(f"[{log['risk_level']}] {log['tool_name']} • {log['timestamp']} • {log['duration_ms']:.1f}ms"):
                c1, c2 = st.columns([1, 2.5])
                with c1:
                    st.markdown(f"**Security Tier:** <span style='color:{badge_color}; font-weight:700;'>{log['risk_level']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Authorized:** `{'Yes' if log['user_approved'] else 'No'}`")
                    st.markdown(f"**Exit Code:** `{log['exit_code']}`")
                with c2:
                    st.markdown("**Command / Input:**")
                    st.code(log["command"], language="bash")
                    st.markdown("**Execution Output:**")
                    st.code(log["output"][:1200], language="text")

# --------------------------------------------------
# TAB 3: PROJECT ARCHITECTURE & VIVA REPORT
# --------------------------------------------------
with tab_benchmark:
    st.markdown("### 📐 System Architecture & Final Year Project Synopsis")
    st.markdown("""
    **Project Title:** *TermiPilot: An Agentic Terminal Copilot with Guardrailed System Execution, Dual Interfaces, and Audit Logging*  
    **Category:** *Agentic AI, Systems Administration & AI Safety*
    """)

    c_card1, c_card2 = st.columns(2)
    with c_card1:
        with st.container(border=True):
            st.markdown("#### ⚡ 1. ReAct Execution Bus")
            st.markdown("""
            - Implements the **Reasoning + Acting** loop via high-speed Groq inference (`qwen-2.5` / `llama-3.3`).
            - Supports multi-step task breakdown: file inspection, script synthesis, diagnostic testing, and verification.
            """)
    with c_card2:
        with st.container(border=True):
            st.markdown("#### 🛡️ 2. Tiered Safety Guardrail Engine")
            st.markdown("""
            - **`SAFE`:** Non-destructive read operations run automatically.
            - **`MODERATE`:** Destructive actions (`rm`, `kill`, overwrite) require Human-in-the-Loop authorization.
            - **`BLOCKED`:** Catastrophic wildcards (`rm -rf /`, fork bombs) are intercepted and halted.
            """)

    c_card3, c_card4 = st.columns(2)
    with c_card3:
        with st.container(border=True):
            st.markdown("#### 📊 3. Quantitative Evaluation")
            st.markdown("""
            - Evaluated with an automated test suite across 7 developer benchmarks.
            - Achieved **100.0% completion rate** with sub-10 second average latency.
            """)
    with c_card4:
        with st.container(border=True):
            st.markdown("#### 💻 4. Dual User Interfaces")
            st.markdown("""
            - **Terminal TUI (`cli_app.py`):** Rich terminal UI with spinners, colorized tables, and interactive approval prompts.
            - **Web Dashboard (`app.py`):** Modern ChatGPT-style interface with real-time tool inspection.
            """)
