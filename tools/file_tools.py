"""
File System Inspector and Utility Tools for TermiPilot.
"""
import os
import glob
from typing import Dict, Any, List, Optional


class FileSystemTools:
    @staticmethod
    def read_file(file_path: str, max_lines: int = 150) -> Dict[str, Any]:
        """Reads contents of a file safely with line truncation."""
        try:
            if not os.path.exists(file_path):
                return {"status": "error", "output": f"File '{file_path}' does not exist."}
            if os.path.isdir(file_path):
                return {"status": "error", "output": f"'{file_path}' is a directory, not a file."}

            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = [f.readline() for _ in range(max_lines)]
                content = "".join(lines)

            return {
                "status": "success",
                "file_path": file_path,
                "lines_read": len(lines),
                "output": content.strip()
            }
        except Exception as e:
            return {"status": "error", "output": f"Failed to read file: {str(e)}"}

    @staticmethod
    def list_directory(directory: str = ".", max_items: int = 50) -> Dict[str, Any]:
        """Lists directory contents with file size and type info."""
        try:
            target_dir = os.path.abspath(directory)
            if not os.path.exists(target_dir):
                return {"status": "error", "output": f"Directory '{target_dir}' does not exist."}

            entries = []
            for item in os.listdir(target_dir)[:max_items]:
                full_p = os.path.join(target_dir, item)
                is_dir = os.path.isdir(full_p)
                size_str = "<DIR>" if is_dir else f"{os.path.getsize(full_p)} bytes"
                entries.append(f"{'[DIR] ' if is_dir else '[FILE] '} {item} ({size_str})")

            return {
                "status": "success",
                "directory": target_dir,
                "output": "\n".join(entries) if entries else "(Directory is empty)"
            }
        except Exception as e:
            return {"status": "error", "output": f"Failed to list directory: {str(e)}"}

    @staticmethod
    def find_files(pattern: str, search_path: str = ".") -> Dict[str, Any]:
        """Finds files matching glob pattern."""
        try:
            matches = glob.glob(os.path.join(search_path, "**", pattern), recursive=True)[:50]
            if not matches:
                return {"status": "success", "output": f"No files matching '{pattern}' were found."}
            return {
                "status": "success",
                "matches": matches,
                "output": "\n".join(matches)
            }
        except Exception as e:
            return {"status": "error", "output": f"Error searching files: {str(e)}"}
