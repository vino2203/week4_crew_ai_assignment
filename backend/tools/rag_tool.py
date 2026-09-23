"""CrewAI tool wrapping the Hybrid RAG retriever (FAISS + Neo4j) for Agent 1."""
from __future__ import annotations

import json

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from runtime import get_hybrid_retriever


class HybridRAGInput(BaseModel):
    query: str = Field(..., description="The customer's question to search the internal knowledge base for.")


class HybridRAGTool(BaseTool):
    name: str = "Hybrid RAG Search"
    description: str = (
        "Searches the internal company knowledge base (FAISS page-by-page vector index "
        "blended with the Neo4j knowledge graph). Returns the most relevant passages with "
        "exact document name + page number citations, a 0-100 accuracy score per passage, "
        "and related graph entities (Product/Issue/Solution)."
    )
    args_schema: type[BaseModel] = HybridRAGInput

    def _run(self, query: str) -> str:
        retriever = get_hybrid_retriever()
        result = retriever.retrieve(query, top_k=3)
        return json.dumps(result, indent=2)
