"""CrewAI Agent definitions for the multi-agent customer support team."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from crewai import Agent

from tools.memory_tool import MemoryArchivalTool
from tools.rag_tool import HybridRAGTool
from tools.serpapi_search_tool import SerpAPISearchTool

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agents.yaml"


def _load_agent_configs() -> dict:
    with open(_CONFIG_PATH, "r") as fh:
        return yaml.safe_load(fh)


def _llm() -> str:
    return os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")


def build_agents() -> dict[str, Agent]:
    cfg = _load_agent_configs()
    llm = _llm()

    knowledge_base_specialist = Agent(
        role=cfg["knowledge_base_specialist"]["role"],
        goal=cfg["knowledge_base_specialist"]["goal"],
        backstory=cfg["knowledge_base_specialist"]["backstory"],
        tools=[HybridRAGTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    web_search_specialist = Agent(
        role=cfg["web_search_specialist"]["role"],
        goal=cfg["web_search_specialist"]["goal"],
        backstory=cfg["web_search_specialist"]["backstory"],
        tools=[SerpAPISearchTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    memory_archivist = Agent(
        role=cfg["memory_archivist"]["role"],
        goal=cfg["memory_archivist"]["goal"],
        backstory=cfg["memory_archivist"]["backstory"],
        tools=[MemoryArchivalTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    support_lead = Agent(
        role=cfg["support_lead"]["role"],
        goal=cfg["support_lead"]["goal"],
        backstory=cfg["support_lead"]["backstory"],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    return {
        "knowledge_base_specialist": knowledge_base_specialist,
        "web_search_specialist": web_search_specialist,
        "memory_archivist": memory_archivist,
        "support_lead": support_lead,
    }
