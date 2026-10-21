"""
Web Search Tool using DuckDuckGo for live tech documentation, error codes, and solutions.
"""
import warnings
warnings.filterwarnings("ignore")
from typing import Dict, Any
from duckduckgo_search import DDGS


class WebSearchTool:
    @staticmethod
    def search(query: str, max_results: int = 4) -> Dict[str, Any]:
        """Performs a live DuckDuckGo web search and returns summaries."""
        try:
            results = []
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=max_results))
                for r in raw_results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    href = r.get("href", "")
                    results.append(f"**{title}**\n{body}\nSource: {href}")

            if not results:
                return {
                    "status": "success",
                    "output": f"No live search results found for query: '{query}'."
                }

            return {
                "status": "success",
                "output": "\n\n---\n\n".join(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "output": f"Web search failed or timed out: {str(e)}"
            }
