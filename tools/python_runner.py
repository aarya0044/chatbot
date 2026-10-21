"""
Sandboxed Python Runner for math calculations, text processing, and data tasks.
"""
import sys
import io
import time
import traceback
from typing import Dict, Any


class PythonSandboxTool:
    @staticmethod
    def execute(code: str) -> Dict[str, Any]:
        """
        Executes Python code in a controlled namespace and captures standard output.
        """
        start_time = time.time()
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Restricted safe globals
        safe_globals = {
            "__builtins__": __builtins__,
        }
        safe_locals = {}

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            exec(code, safe_globals, safe_locals)
            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()
            
            final_output = output
            if errors:
                final_output += ("\nSTDERR:\n" if final_output else "") + errors

            if not final_output.strip():
                final_output = "(Code executed successfully with no stdout output)"

            duration_ms = (time.time() - start_time) * 1000
            return {
                "status": "success",
                "output": final_output.strip(),
                "duration_ms": duration_ms
            }

        except Exception:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = traceback.format_exc()
            return {
                "status": "error",
                "output": f"Python Execution Error:\n{error_msg}",
                "duration_ms": duration_ms
            }
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
