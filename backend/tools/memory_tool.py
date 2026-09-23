"""CrewAI tool for persisting conversation memory into Neo4j for Agent 3."""
from __future__ import annotations

import json
from typing import List

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from runtime import get_knowledge_graph


class MemoryArchivalInput(BaseModel):
    session_id: str = Field(..., description="The chat session ID this interaction belongs to.")
    customer_id: str = Field(default="anonymous", description="The customer's identifier, if known.")
    query: str = Field(..., description="The original customer question.")
    resolution: str = Field(..., description="The final resolution given to the customer.")
    cited_documents: List[str] = Field(
        default_factory=list, description="Document names cited in the resolution, if any."
    )


class MemoryArchivalTool(BaseTool):
    name: str = "Memory Archival"
    description: str = (
        "Persists a customer support interaction (query, final resolution, and cited "
        "documents) into the Neo4j long-term memory knowledge graph, linked to the "
        "customer and session."
    )
    args_schema: type[BaseModel] = MemoryArchivalInput

    def _run(
        self,
        session_id: str,
        query: str,
        resolution: str,
        customer_id: str = "anonymous",
        cited_documents: List[str] | None = None,
    ) -> str:
        kg = get_knowledge_graph()
        record = kg.persist_session(
            query=query,
            resolution=resolution,
            cited_documents=cited_documents or [],
            session_id=session_id,
            customer_id=customer_id,
        )
        record["backend"] = kg.stats["backend"]
        return json.dumps(record, indent=2)
