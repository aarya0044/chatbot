"""
TermiPilot Web Dashboard (Streamlit).
Autonomous DevOps & Terminal Copilot with Live Tool Execution Cards, Safety Gateways, and Audit Trail.
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
    page_title="TermiPilot - Autonomous CLI & DevOps Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern developer theme
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e2e;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #313244;
    }
    .tool-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        background-color: #45475a;
        color: #cdd6f4;
    }
    .badge-safe { color: #a6e3a1; font-weight: bold; }
    .badge-mod { color: #f9e2af; font-weight: bold; }
    .badge-crit { color: #f38ba8; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# INITIALIZE DATABASE & SESSION STATE
# --------------------------------------------------
db = DatabaseManager()

if "user" not in st.session_state:
    st.session_state.user = None

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None

# Login Screen
if st.session_state.user is None:
    st.title("🔐 TermiPilot - Access Portal")
    st.caption("Autonomous AI DevOps & Terminal Copilot (B.Tech Final Year Edition)")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Enter Developer / Operator Username", value="developer")
        if st.button("Launch Copilot", use_container_width=True) and username.strip():
            st.session_state.user = username.strip()
            st.rerun()
    st.stop()

# --------------------------------------------------
# SIDEBAR: SESSIONS & SYSTEM METRICS
# --------------------------------------------------
user_chats = db.get_user_chats(st.session_state.user)

if "current_chat_id" not in st.session_state:
    if user_chats:
        st.session_state.current_chat_id = user_chats[0]["chat_id"]
    else:
        st.session_state.current_chat_id = db.create_chat(st.session_state.user, "DevOps Session 1")
        user_chats = db.get_user_chats(st.session_state.user)

# Ensure valid current chat ID
chat_ids = [c["chat_id"] for c in user_chats]
if not chat_ids:
    st.session_state.current_chat_id = db.create_chat(st.session_state.user, "DevOps Session 1")
    user_chats = db.get_user_chats(st.session_state.user)
elif st.session_state.current_chat_id not in chat_ids:
    st.session_state.current_chat_id = chat_ids[0]

with st.sidebar:
    st.title("⚡ TermiPilot")
    st.caption("AI DevOps & Terminal Agent")
    st.divider()

    if st.button("➕ New Session", use_container_width=True, type="primary"):
        new_id = db.create_chat(st.session_state.user, f"Session {len(user_chats) + 1}")
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("### 💬 Sessions")
    for chat in user_chats:
        c_id = chat["chat_id"]
        title = chat["title"] or "Untitled Session"
        col_btn, col_opt = st.columns([5, 1])

        with col_btn:
            is_active = (c_id == st.session_state.current_chat_id)
            btn_label = f"▸ {title}" if is_active else title
            if st.button(btn_label, key=f"session_{c_id}", use_container_width=True):
                st.session_state.current_chat_id = c_id
                st.rerun()

        with col_opt:
            with st.popover("⋮"):
                new_title = st.text_input("Rename", value=title, key=f"ren_{c_id}")
                if st.button("Save", key=f"save_ren_{c_id}"):
                    if new_title.strip():
                        db.rename_chat(c_id, new_title.strip())
                        st.rerun()
                if st.button("🗑 Delete", key=f"del_{c_id}", type="secondary"):
                    db.delete_chat(c_id)
                    st.rerun()

    st.divider()
    st.markdown(f"**Operator:** `{st.session_state.user}`")
    st.markdown(f"**Working Dir:** `{os.path.basename(os.getcwd())}`")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --------------------------------------------------
# MAIN UI: TABS (COPILOT & AUDIT DASHBOARD)
# --------------------------------------------------
tab_copilot, tab_audit, tab_benchmark = st.tabs([
    "💬 Autonomous Copilot",
    "🛡️ Security & Tool Audit Trail",
    "📊 Project Architecture & Metrics"
])

# Web approval callback
def web_approval_handler(command: str, reason: str) -> bool:
    return st.session_state.get("auto_approve_mutations", False)

agent = TermiPilotAgent(
    db_manager=db,
    approval_callback=web_approval_handler
)

# --- TAB 1: COPILOT INTERFACE ---
with tab_copilot:
    # Find current chat title
    current_title = "Active Session"
    for c in user_chats:
        if c["chat_id"] == st.session_state.current_chat_id:
            current_title = c["title"]
            break

    col_title, col_toggle = st.columns([3, 2])
    with col_title:
        st.subheader(f"Session: {current_title}")
    with col_toggle:
        st.session_state.auto_approve_mutations = st.toggle(
            "🛡️ Auto-Authorize Safe Mutations",
            value=False,
            help="When OFF, commands that alter or delete files will be blocked unless explicitly permitted."
        )

    # Render Chat History
    messages = db.get_messages(st.session_state.current_chat_id)
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input Box
    user_prompt = st.chat_input("Enter DevOps task, command request, or system query...")

    if user_prompt:
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Assistant turn with live status
        with st.chat_message("assistant"):
            status_container = st.status("🧠 TermiPilot is reasoning and planning...", expanded=True)

            def web_status_hook(event_type: str, tool_name: str, data: dict):
                if event_type == "tool_start":
                    status_container.write(f"⚡ **Executing Tool:** `{tool_name}`")
                    status_container.code(str(data), language="json")
                elif event_type == "tool_end":
                    res_status = data.get("status", "done")
                    status_container.write(f"✓ Tool `{tool_name}` finished with status: `{res_status}`")

            # Run agent turn
            res = agent.run_step(
                chat_id=st.session_state.current_chat_id,
                user_message=user_prompt,
                status_callback=web_status_hook
            )

            status_container.update(
                label=f"Completed in {res['latency_sec']:.2f}s ({len(res['tool_executions'])} tools executed)",
                state="complete",
                expanded=False
            )

            st.markdown(res["reply"])

        st.rerun()

# --- TAB 2: AUDIT & SECURITY LOGS ---
with tab_audit:
    st.subheader("🛡️ Real-Time Tool Execution Audit Trail")
    st.caption("Every command invocation and parameter executed by the agent is stored with its risk level and exit code for compliance and evaluation.")

    audit_logs = db.get_audit_logs(limit=40)
    if not audit_logs:
        st.info("No tool executions recorded yet.")
    else:
        # Metrics summary
        total_runs = len(audit_logs)
        safe_runs = sum(1 for l in audit_logs if l["risk_level"] == "SAFE")
        mod_runs = sum(1 for l in audit_logs if l["risk_level"] in ["MODERATE", "CRITICAL"])
        avg_lat = sum(l["duration_ms"] for l in audit_logs) / max(total_runs, 1)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Tool Calls", total_runs)
        m2.metric("Safe Invocations", safe_runs)
        m3.metric("Gated / High-Risk Intercepts", mod_runs)
        m4.metric("Avg Latency", f"{avg_lat:.1f} ms")

        st.divider()

        for log in audit_logs:
            with st.expander(f"[{log['risk_level']}] {log['tool_name']} @ {log['timestamp']} ({log['duration_ms']:.1f}ms)"):
                c1, c2 = st.columns([1, 3])
                with c1:
                    st.write(f"**Risk Level:** `{log['risk_level']}`")
                    st.write(f"**User Approved:** `{'Yes' if log['user_approved'] else 'No'}`")
                    st.write(f"**Exit Code:** `{log['exit_code']}`")
                with c2:
                    st.write("**Command / Parameters:**")
                    st.code(log["command"], language="bash")
                    st.write("**Output:**")
                    st.code(log["output"][:1000], language="text")

# --- TAB 3: PROJECT ARCHITECTURE & VIVA REPORT ---
with tab_benchmark:
    st.subheader("📐 System Architecture & B.Tech Capstone Details")
    st.markdown("""
    ### Project Synopsis
    **TermiPilot** addresses the challenge of autonomous AI assistance in system operations and software engineering.
    Unlike standard LLM chat wrappers that can only output unverified text, TermiPilot is an **Agentic System** capable of:
    - **Closed-Loop Verification:** Using the **ReAct (Reasoning + Acting)** framework to iteratively inspect files, execute diagnostics, and verify outcomes.
    - **Safety & Guardrail Engine:** Classifying commands into tiered risk levels (`SAFE`, `MODERATE`, `CRITICAL`, `BLOCKED`) with Human-in-the-Loop authorization.
    - **Dual Presentation:** Both a developer-first Terminal TUI (via `rich`) and an administrative Web UI (via `streamlit`).
    - **Persistent Audit Logging:** Storing conversation trajectories and tool metadata into an embedded SQLite store for accountability and reproducibility.
    """)

    st.markdown("### Architecture Flowchart")
    st.code("""
    [ User Query ]
          │
    ▼ (Safety Filter)
    [ Prompt Injection Guard ]
          │
    ▼ (Orchestrator)
    [ Groq Llama/Qwen Model ] ◄───────┐
          │ (Tool Calls)               │
    ▼ (Security Interceptor)           │ (Observation)
    [ Safe vs. Destructive Check ]     │
          │                            │
    ▼ (Tool Bus)                       │
    [ PowerShell / Python / Search ] ──┘
          │
    ▼ (Final Verification)
    [ Verified Terminal Output + SQLite Audit Trail ]
    """, language="text")
