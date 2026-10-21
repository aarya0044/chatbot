"""
Safety and Guardrails Module for TermiPilot.
Provides risk classification, destructive command interception, and prompt safety.
"""
import re
from enum import Enum
from typing import Dict, Any, Tuple


class RiskLevel(Enum):
    SAFE = "SAFE"                 # Read-only or benign inspection -> Auto-run
    MODERATE = "MODERATE"         # Mutating or file writing -> Requires User Confirmation
    CRITICAL = "CRITICAL"         # High destructive potential -> Strict Warning & Confirmation
    BLOCKED = "BLOCKED"           # Catastrophic commands -> Hard blocked


# Regex patterns for dangerous / catastrophic commands
BLOCKED_PATTERNS = [
    r"\bformat\s+[a-zA-Z]:",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",   # Fork bomb
    r"\brm\s+(-[rfRF]+\s+)?(\/|[a-zA-Z]:\\|\*)",   # Root / wildcard wipe
    r"\bdel\s+\/f\s+\/s\s+\/q\s+(c:\\|\*)",
    r"\bRemove-Item\s+.*-(Recurse|Force)\s+(C:\\|\/)",
    r"\bshutdown\b",
    r"\breg\s+delete\b",
]

MODERATE_PATTERNS = [
    r"\b(del|rm|rmdir|unlink)\b",
    r"\bRemove-Item\b",
    r"\b(kill|Stop-Process|taskkill)\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+clean\s+-f\b",
    r"\bgit\s+push\s+.*--force\b",
    r"\bdrop\s+table\b",
    r"\bdrop\s+database\b",
    r"\bpip\s+uninstall\b",
    r"\bnpm\s+uninstall\b",
]

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above)\s+instructions",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"jailbreak",
    r"bypass\s+all\s+safety",
]


class SafetyEngine:
    @staticmethod
    def assess_command(command: str) -> Tuple[RiskLevel, str]:
        """
        Evaluates a shell command and returns its RiskLevel and explanatory reason.
        """
        cmd_clean = command.strip().lower()

        # 1. Check blocked catastrophic patterns
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, cmd_clean, re.IGNORECASE):
                return (
                    RiskLevel.BLOCKED,
                    f"Command matches forbidden catastrophic pattern: '{pattern}'."
                )

        # 2. Check moderate/mutating patterns that require HITL approval
        for pattern in MODERATE_PATTERNS:
            if re.search(pattern, cmd_clean, re.IGNORECASE):
                return (
                    RiskLevel.MODERATE,
                    "Command modifies or deletes system resources. Requires user confirmation."
                )

        # 3. Check for shell redirection write/overwrite (e.g., > or >>)
        if ">" in cmd_clean and not re.search(r"grep|findstr", cmd_clean):
            return (
                RiskLevel.MODERATE,
                "Command redirects output to overwrite/create files."
            )

        # Default: Safe read-only inspection
        return (RiskLevel.SAFE, "Read-only / benign operational command.")

    @staticmethod
    def inspect_prompt_injection(prompt: str) -> Tuple[bool, str]:
        """
        Checks for basic adversarial prompt injection attacks.
        """
        prompt_clean = prompt.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, prompt_clean):
                return True, f"Detected adversarial prompt injection pattern: '{pattern}'."
        return False, "Prompt is clean."
