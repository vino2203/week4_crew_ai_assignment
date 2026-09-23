"""CrewAI tool wrapping SerpAPI (Google Search) for Agent 2."""
from __future__ import annotations

import json
import os

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SerpAPISearchInput(BaseModel):
    query: str = Field(..., description="The search query to run against live Google search results.")


class SerpAPISearchTool(BaseTool):
    name: str = "SerpAPI Web Search"
    description: str = (
        "Searches the live web via SerpAPI (Google Search) for information not covered by "
        "the internal knowledge base. Returns the top organic results with title, URL, "
        "snippet, and a rank-derived relevance score (0-100)."
    )
    args_schema: type[BaseModel] = SerpAPISearchInput

    def _run(self, query: str) -> str:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key or api_key.startswith("your-"):
            return json.dumps(
                {
                    "found": False,
                    "error": "SERPAPI_API_KEY is not configured in backend/.env",
                    "results": [],
                }
            )

        try:
            from serpapi import GoogleSearch
        except ImportError:
            return json.dumps(
                {"found": False, "error": "google-search-results package not installed", "results": []}
            )

        try:
            search = GoogleSearch({"q": query, "api_key": api_key, "num": 5})
            data = search.get_dict()
        except Exception as exc:  # network / API failure
            return json.dumps({"found": False, "error": str(exc), "results": []})

        organic = data.get("organic_results", [])[:5]
        results = []
        for rank, item in enumerate(organic, start=1):
            # Simple rank-derived relevance: rank 1 -> 95%, decaying by 12pts per rank.
            relevance = max(30, 95 - (rank - 1) * 12)
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "relevance_pct": relevance,
                }
            )

        avg_relevance = round(sum(r["relevance_pct"] for r in results) / len(results), 1) if results else 0.0

        return json.dumps(
            {
                "found": bool(results),
                "query_used": query,
                "avg_relevance": avg_relevance,
                "results": results,
            },
            indent=2,
        )
