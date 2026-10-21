"""
System Command Execution Tool with Safety Checks and Timeout Limits.
"""
import subprocess
import platform
import os
import time
from typing import Dict, Any, Callable, Optional
from core.safety import SafetyEngine, RiskLevel


class SystemCommandTool:
    def __init__(self, approval_callback: Optional[Callable[[str, str], bool]] = None):
        """
        :param approval_callback: Function that asks user (prompt, command) -> bool
        """
        self.approval_callback = approval_callback
        self.os_type = platform.system()

    def execute(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes a shell command after running safety inspection.
        Returns: {
            "status": "success" | "error" | "blocked" | "rejected",
            "command": command,
            "risk_level": str,
            "output": str,
            "exit_code": int,
            "duration_ms": float
        }
        """
        start_time = time.time()
        risk_level, reason = SafetyEngine.assess_command(command)

        # 1. Hard blocked
        if risk_level == RiskLevel.BLOCKED:
            return {
                "status": "blocked",
                "command": command,
                "risk_level": risk_level.value,
                "output": f"SECURITY ALERT: {reason}",
                "exit_code": -1,
                "duration_ms": (time.time() - start_time) * 1000,
                "user_approved": False
            }

        # 2. Moderate / Critical: requires approval
        user_approved = True
        if risk_level in [RiskLevel.MODERATE, RiskLevel.CRITICAL]:
            if self.approval_callback:
                user_approved = self.approval_callback(command, reason)
            else:
                user_approved = False  # Default to deny if no callback provided

            if not user_approved:
                return {
                    "status": "rejected",
                    "command": command,
                    "risk_level": risk_level.value,
                    "output": "User declined permission to execute this command.",
                    "exit_code": -2,
                    "duration_ms": (time.time() - start_time) * 1000,
                    "user_approved": False
                }

        # 3. Execution
        shell_cmd = command
        if self.os_type == "Windows":
            shell_cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", command]
        else:
            shell_cmd = ["/bin/bash", "-c", command]

        try:
            process = subprocess.run(
                shell_cmd,
                capture_output=True,
                text=True,
                timeout=20,  # 20 second max execution to prevent freezing
                cwd=cwd or os.getcwd()
            )
            output = process.stdout
            if process.stderr:
                output += ("\nSTDERR:\n" if output else "") + process.stderr

            if not output.strip():
                output = "(Command executed successfully with no output)"

            # Cap output to 4000 chars to avoid breaking LLM context
            if len(output) > 4000:
                output = output[:4000] + "\n...[Output truncated to 4000 characters]..."

            duration_ms = (time.time() - start_time) * 1000
            return {
                "status": "success" if process.returncode == 0 else "error",
                "command": command,
                "risk_level": risk_level.value,
                "output": output.strip(),
                "exit_code": process.returncode,
                "duration_ms": duration_ms,
                "user_approved": user_approved
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "command": command,
                "risk_level": risk_level.value,
                "output": "Execution timed out after 20 seconds.",
                "exit_code": -3,
                "duration_ms": (time.time() - start_time) * 1000,
                "user_approved": user_approved
            }
        except Exception as e:
            return {
                "status": "error",
                "command": command,
                "risk_level": risk_level.value,
                "output": f"Execution error: {str(e)}",
                "exit_code": -4,
                "duration_ms": (time.time() - start_time) * 1000,
                "user_approved": user_approved
            }
