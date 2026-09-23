"""CrewAI Task definitions for the multi-agent customer support team."""
from __future__ import annotations

from pathlib import Path

import yaml
from crewai import Agent, Task

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "tasks.yaml"


def _load_task_configs() -> dict:
    with open(_CONFIG_PATH, "r") as fh:
        return yaml.safe_load(fh)


def build_tasks(agents: dict[str, Agent], query: str, session_id: str, customer_id: str) -> dict[str, Task]:
    cfg = _load_task_configs()
    fmt = {"query": query, "session_id": session_id, "customer_id": customer_id}

    knowledge_retrieval_task = Task(
        description=cfg["knowledge_retrieval_task"]["description"].format(**fmt),
        expected_output=cfg["knowledge_retrieval_task"]["expected_output"],
        agent=agents["knowledge_base_specialist"],
        verbose=True,
    )

    web_intelligence_task = Task(
        description=cfg["web_intelligence_task"]["description"].format(**fmt),
        expected_output=cfg["web_intelligence_task"]["expected_output"],
        agent=agents["web_search_specialist"],
        verbose=True,
    )

    resolution_synthesis_task = Task(
        description=cfg["resolution_synthesis_task"]["description"].format(**fmt),
        expected_output=cfg["resolution_synthesis_task"]["expected_output"],
        agent=agents["support_lead"],
        context=[knowledge_retrieval_task, web_intelligence_task],
        verbose=True,
    )

    memory_archival_task = Task(
        description=cfg["memory_archival_task"]["description"].format(**fmt),
        expected_output=cfg["memory_archival_task"]["expected_output"],
        agent=agents["memory_archivist"],
        context=[resolution_synthesis_task, knowledge_retrieval_task, web_intelligence_task],
        verbose=True,
    )

    return {
        "knowledge_retrieval_task": knowledge_retrieval_task,
        "web_intelligence_task": web_intelligence_task,
        "resolution_synthesis_task": resolution_synthesis_task,
        "memory_archival_task": memory_archival_task,
    }
