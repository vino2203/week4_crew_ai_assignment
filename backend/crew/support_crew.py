"""Crew orchestration: runs the sequential multi-agent support workflow and
structures the output into a transparent payload (final resolution + each
specialist agent's response, accuracy/relevance scores, citations, and the
memory persistence confirmation) for the frontend to render.
"""
from __future__ import annotations

import json
import re
import uuid
from typing import Any

from crewai import Crew, Process

from crew.agents import build_agents
from crew.tasks import build_tasks

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse_json_output(raw: Any) -> dict:
    text = str(raw)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    match = _JSON_BLOCK_RE.search(text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {"raw_text": text}


class SupportCrew:
    """Builds and runs the 4-agent sequential customer support crew."""

    def run(self, query: str, session_id: str | None = None, customer_id: str = "anonymous") -> dict:
        session_id = session_id or str(uuid.uuid4())[:8]

        agents = build_agents()
        tasks = build_tasks(agents, query=query, session_id=session_id, customer_id=customer_id)

        crew = Crew(
            agents=list(agents.values()),
            tasks=list(tasks.values()),
            process=Process.sequential,
            verbose=True,
        )
        crew.kickoff()

        kb_output = _parse_json_output(tasks["knowledge_retrieval_task"].output.raw)
        web_output = _parse_json_output(tasks["web_intelligence_task"].output.raw)
        synthesis_output = _parse_json_output(tasks["resolution_synthesis_task"].output.raw)
        memory_output = _parse_json_output(tasks["memory_archival_task"].output.raw)

        return {
            "session_id": session_id,
            "query": query,
            "final_resolution": synthesis_output.get(
                "final_resolution", synthesis_output.get("raw_text", "")
            ),
            "sources_used": synthesis_output.get("sources_used", []),
            "agent_1_internal_rag": {
                "response": kb_output.get("response", kb_output.get("raw_text", "")),
                "confidence_score": kb_output.get("confidence_score", 0),
                "citations": kb_output.get("citations", []),
                "graph_context": kb_output.get("graph_context", ""),
            },
            "agent_2_web_search": {
                "response": web_output.get("response", web_output.get("raw_text", "")),
                "relevance_score": web_output.get("relevance_score", 0),
                "queries_used": web_output.get("queries_used", []),
                "sources": web_output.get("sources", []),
            },
            "agent_3_memory": {
                "memory_confirmation": memory_output.get(
                    "memory_confirmation", memory_output.get("raw_text", "")
                ),
                "session_id": memory_output.get("session_id", session_id),
                "persisted": memory_output.get("persisted", False),
            },
        }
