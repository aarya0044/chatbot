"""
Agent Orchestrator for TermiPilot.
Implements the ReAct tool-calling loop using Groq LLM with safety interception.
"""
import os
import json
import time
import platform
from typing import List, Dict, Any, Callable, Optional, Generator
import groq
from dotenv import load_dotenv

from core.safety import SafetyEngine, RiskLevel
from core.memory import DatabaseManager
from tools.system_tools import SystemCommandTool
from tools.python_runner import PythonSandboxTool
from tools.file_tools import FileSystemTools
from tools.web_tools import WebSearchTool

load_dotenv()

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

# Tool definitions conforming to OpenAI / Groq tool specification
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Execute a terminal/PowerShell command to inspect, configure, or run tasks on the system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The exact shell command to execute."
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python_code",
            "description": "Execute Python code in a sandboxed environment for calculations, parsing data, or algorithm tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python source code to execute."
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file in the workspace or system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read."
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": "Maximum lines to read (default 100)."
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and subdirectories inside a specific path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Path to the directory (default '.')."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search DuckDuckGo for technical documentation, library APIs, or troubleshooting error codes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


class TermiPilotAgent:
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        approval_callback: Optional[Callable[[str, str], bool]] = None,
        model: str = DEFAULT_MODEL
    ):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            try:
                import streamlit as st
                if "GROQ_API_KEY" in st.secrets:
                    self.api_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                pass

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing. Set it in .env or Streamlit Secrets.")

        self.client = groq.Groq(api_key=self.api_key)
        self.model = model
        self.db = db_manager or DatabaseManager()
        self.shell_tool = SystemCommandTool(approval_callback=approval_callback)
        self.python_tool = PythonSandboxTool()
        self.fs_tool = FileSystemTools()
        self.web_tool = WebSearchTool()

    def _build_system_prompt(self) -> str:
        os_info = f"{platform.system()} {platform.release()}"
        cwd = os.getcwd()
        return f"""You are TermiPilot, an expert AI DevOps & Terminal Copilot with system inspection and execution capabilities.
Environment Information:
- Operating System: {os_info}
- Current Working Directory: {cwd}

Operational Rules:
1. When asked to check system status, files, git, or dependencies, call the appropriate tool.
2. For PowerShell/Windows commands, prefer Windows-compatible commands (e.g. 'Get-ChildItem', 'dir', 'ipconfig', 'git').
3. For calculations or data formatting, use 'run_python_code'.
4. For live library documentation or unknown error codes, use 'search_web'.
5. Always explain your reasoning clearly and concisely after inspecting results.
6. Never attempt to bypass security policies or delete critical directories.
"""

    def run_step(
        self,
        chat_id: str,
        user_message: str,
        status_callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes a turn of the ReAct loop.
        :param status_callback: Optional hook called whenever a tool is invoked or completes.
                                fn(event_type: 'tool_start'|'tool_end'|'injection', tool_name, data)
        """
        start_time = time.time()

        # 1. Input Guardrail: Check for adversarial prompt injections
        is_injection, reason = SafetyEngine.inspect_prompt_injection(user_message)
        if is_injection:
            if status_callback:
                status_callback("security_warning", "prompt_guard", {"reason": reason})
            reply = f"⚠️ **Security Warning**: {reason} Request blocked by TermiPilot Safety Engine."
            self.db.save_message(chat_id, "user", user_message)
            self.db.save_message(chat_id, "assistant", reply)
            return {
                "reply": reply,
                "tool_executions": [],
                "latency_sec": time.time() - start_time
            }

        # 2. Save user message to persistent SQLite
        self.db.save_message(chat_id, "user", user_message)

        # 3. Build message history
        raw_history = self.db.get_messages(chat_id, limit=12)
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        for msg in raw_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        tool_execution_history = []
        max_turns = 5
        final_text = ""

        # 4. Multi-step ReAct Loop
        for turn in range(max_turns):
            # Resilience: retry on rate limit
            response = None
            for attempt in range(3):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=TOOL_DEFINITIONS,
                        tool_choice="auto",
                        temperature=0.2
                    )
                    break
                except groq.RateLimitError as rle:
                    if attempt < 2:
                        time.sleep(5)
                    else:
                        raise rle

            assistant_msg = response.choices[0].message
            tool_calls = assistant_msg.tool_calls

            # If no tools called, we've reached the final answer
            if not tool_calls:
                final_text = assistant_msg.content or ""
                break

            # Append the assistant message with tool calls to conversation trajectory
            messages.append(assistant_msg)

            # Process each tool call
            for tc in tool_calls:
                tool_name = tc.function.name
                call_id = tc.id
                raw_args = tc.function.arguments

                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except Exception:
                    args = {}

                if status_callback:
                    status_callback("tool_start", tool_name, args)

                # Execute requested tool
                exec_result = self._dispatch_tool(chat_id, tool_name, args)
                tool_execution_history.append({
                    "tool": tool_name,
                    "args": args,
                    "result": exec_result
                })

                if status_callback:
                    status_callback("tool_end", tool_name, exec_result)

                # Append tool result back to trajectory for the next reasoning step
                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": tool_name,
                    "content": str(exec_result.get("output", ""))
                })

        # Save assistant final response
        if final_text:
            self.db.save_message(chat_id, "assistant", final_text)

        total_latency = time.time() - start_time
        return {
            "reply": final_text,
            "tool_executions": tool_execution_history,
            "latency_sec": total_latency
        }

    def _dispatch_tool(self, chat_id: str, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches tool execution and logs audit record."""
        t0 = time.time()
        res = {}
        risk_level = "SAFE"
        user_approved = True

        if tool_name == "run_shell_command":
            cmd = args.get("command", "")
            res = self.shell_tool.execute(cmd)
            risk_level = res.get("risk_level", "SAFE")
            user_approved = res.get("user_approved", True)

        elif tool_name == "run_python_code":
            code = args.get("code", "")
            res = self.python_tool.execute(code)
            risk_level = "SAFE"

        elif tool_name == "read_file":
            path = args.get("file_path", "")
            max_lines = args.get("max_lines", 100)
            res = self.fs_tool.read_file(path, max_lines=max_lines)

        elif tool_name == "list_directory":
            directory = args.get("directory", ".")
            res = self.fs_tool.list_directory(directory)

        elif tool_name == "search_web":
            query = args.get("query", "")
            res = self.web_tool.search(query)

        else:
            res = {"status": "error", "output": f"Unknown tool: '{tool_name}'."}

        duration_ms = (time.time() - t0) * 1000

        # Audit log into SQLite
        self.db.log_tool_execution(
            chat_id=chat_id,
            tool_name=tool_name,
            command=str(args),
            risk_level=risk_level,
            user_approved=user_approved,
            exit_code=res.get("exit_code", 0),
            output=str(res.get("output", "")),
            duration_ms=duration_ms
        )

        return res
