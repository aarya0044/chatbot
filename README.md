# TermiPilot ⚡
### Autonomous AI DevOps & Terminal Copilot with Guardrailed Execution & Dual Interfaces

> **Academic Final Year Project (B.Tech / B.E. / BCA / BS)**  
> *Domain: Agentic Artificial Intelligence, Systems Administration, and AI Safety*

---

## 📖 Abstract

Traditional conversational chatbots rely solely on static pre-trained weights and cannot directly interact with, diagnose, or manage computational environments. When tasked with real-world developer problems (e.g., diagnosing build errors, inspecting system logs, querying network configurations), basic LLM wrappers often hallucinate commands or deliver outdated advice.

**TermiPilot** is an autonomous, agentic terminal assistant that bridges natural language intent with real-time operating system execution. Powered by Groq's high-throughput LLM infrastructure, TermiPilot implements a **Reasoning + Acting (ReAct)** loop capable of invoking a suite of system tools (shell command execution, sandboxed Python computation, directory search, and live documentation retrieval). 

To prevent accidental system disruption, TermiPilot incorporates a **Multi-Tier Safety Guardrail Engine** that automatically classifies commands into risk tiers (`SAFE`, `MODERATE`, `CRITICAL`, `BLOCKED`) and enforces **Human-in-the-Loop (HITL)** authorization before executing any mutating or destructive system action.

---

## 🏗️ System Architecture

```
                      ┌────────────────────────────────────────┐
                      │            User Interfaces             │
                      │   [Rich Terminal TUI]  [Streamlit Web] │
                      └───────────────────┬────────────────────┘
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │       Safety & Guardrails Layer        │
                      │  • Prompt Injection Filter             │
                      │  • Destructive Command Risk Classifier │
                      │  • Human-in-the-Loop Approval Intercept│
                      └───────────────────┬────────────────────┘
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │        Agentic Orchestration           │
                      │       (Groq High-Speed LLM)            │
                      │     ReAct (Reason + Act Loop)          │
                      └──────────────┬───────────────▲─────────┘
                                     │               │
                                     ▼               │ (Observations)
                      ┌──────────────────────────────┴─────────┐
                      │           Tool Execution Bus           │
                      │  ├─ PowerShell / Shell Executor        │
                      │  ├─ Sandboxed Python REPL              │
                      │  ├─ File System Inspector (Grep/Tree)  │
                      │  └─ DuckDuckGo Live Search API         │
                      └──────────────┬─────────────────────────┘
                                     │
                                     ▼
                      ┌────────────────────────────────────────┐
                      │    Persistent Memory & Audit Store     │
                      │        (SQLite: chatbot.db)            │
                      │  • Session Threads  • Tool Audit Logs  │
                      └────────────────────────────────────────┘
```

---

## 🚀 Key Technical Highlights

1. **Autonomous Tool Calling (ReAct Framework):**
   - Implements closed-loop iteration: the agent diagnoses issues by running read-only diagnostic commands, analyzes the stdout/stderr, and iteratively resolves multi-step developer requests.
2. **Tiered Safety & Human-in-the-Loop (HITL) Gate:**
   - **`SAFE` (Auto-run):** `dir`, `Get-ChildItem`, `git status`, `python --version`, `cat`.
   - **`MODERATE` (Gated):** `del`, `rm`, `kill`, `git reset --hard`, file overwrite redirection. Requires interactive user approval.
   - **`BLOCKED` (Hard Deny):** Wildcard root deletion (`rm -rf /`, `del /f /s /q C:\`), fork bombs, system formatting.
3. **Dual Interactive Frontends:**
   - **Developer Terminal TUI (`cli_app.py`):** Built with `rich`, featuring live spinners, colorized tables, and interactive approval prompts.
   - **Management Dashboard (`app.py`):** Built with `streamlit`, featuring live tool execution cards, multi-session management, and a compliance audit dashboard.
4. **Full Traceability & Compliance Audit Trail:**
   - Every single command, tool invocation, risk tier, duration, exit code, and stdout is persisted in SQLite for accountability.

---

## 🛠️ Project Structure

```
Terminal Chatbot/
├── core/
│   ├── agent.py            # ReAct orchestrator & Groq tool calling loop
│   ├── memory.py           # SQLite persistence for chats & tool audit logs
│   └── safety.py           # Risk assessment, regex classifier, and prompt guard
├── tools/
│   ├── system_tools.py     # Shell execution with timeout and output truncation
│   ├── python_runner.py    # Sandboxed Python code evaluation
│   ├── file_tools.py       # File reading, listing, and pattern searching
│   └── web_tools.py        # Live search via DuckDuckGo
├── eval/
│   ├── benchmark_tasks.json# 7 reproducible benchmark test cases
│   ├── run_benchmark.py    # Automated test runner measuring accuracy and latency
│   └── benchmark_results.json# Exported evaluation metrics
├── cli_app.py              # Interactive Rich Terminal User Interface (TUI)
├── app.py                  # Streamlit Web UI & Metrics Dashboard
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation & viva guide
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites & Environment Setup
Clone the repository and install the dependencies:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Launch the Terminal Copilot (TUI)
For an interactive command-line experience:
```bash
python cli_app.py
```
*Special commands:* `/history` (view audit log), `/clear` (clear screen), `exit` (quit).

### 3. Launch the Web Dashboard
For visual interaction, session management, and metrics:
```bash
streamlit run app.py
```

### 4. Run the Academic Evaluation Benchmark
To generate the metrics and success rates for your project report:
```bash
python eval/run_benchmark.py
```
