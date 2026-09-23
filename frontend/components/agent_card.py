"""Agent transparency cards: Agent 1 (Hybrid RAG), Agent 2 (SerpAPI), Agent 3 (Memory)."""
from __future__ import annotations

import html

import streamlit as st


def _accuracy_bar(pct: float) -> str:
    pct = max(0, min(100, pct))
    return (
        f'<div class="accuracy-bar-bg"><div class="accuracy-bar-fill" '
        f'style="width:{pct}%;"></div></div>'
    )


def render_agent1_card(agent_data: dict) -> None:
    confidence = agent_data.get("confidence_score", 0) or 0
    citations = agent_data.get("citations", []) or []
    response = agent_data.get("response", "") or "_No internal knowledge base match found._"
    graph_context = agent_data.get("graph_context", "")

    citation_html = "".join(
        f'<span class="citation-chip">📄 {html.escape(str(c.get("document", "")))} '
        f'| Page {html.escape(str(c.get("page", "")))}</span>'
        for c in citations
    ) or '<span class="meta">No citations</span>'

    graph_badge = (
        f"<span class='badge badge-gray'>Graph: {html.escape(graph_context)}</span>"
        if graph_context
        else ""
    )

    markup = (
        '<div class="support-card">'
        "<h4>🧠 Agent 1 — Internal Hybrid RAG</h4>"
        f'<span class="badge badge-indigo">{confidence}% Confidence</span>'
        f"{graph_badge}"
        f"{_accuracy_bar(confidence)}"
        f'<p style="margin-top:10px;">{html.escape(response)}</p>'
        '<div class="meta">Citations:</div>'
        f"<div>{citation_html}</div>"
        "</div>"
    )
    st.markdown(markup, unsafe_allow_html=True)


def render_agent2_card(agent_data: dict) -> None:
    relevance = agent_data.get("relevance_score", 0) or 0
    queries = agent_data.get("queries_used", []) or []
    sources = agent_data.get("sources", []) or []
    response = agent_data.get("response", "") or "_No web search performed._"

    queries_html = ", ".join(f"“{html.escape(str(q))}”" for q in queries) or "—"
    sources_html = "".join(
        f'<div><a href="{html.escape(str(s.get("url","")))}" target="_blank">'
        f'{html.escape(str(s.get("title", s.get("url",""))))}</a></div>'
        for s in sources
    ) or '<span class="meta">No sources</span>'

    markup = (
        '<div class="support-card">'
        "<h4>🌐 Agent 2 — SerpAPI Web Intelligence</h4>"
        f'<span class="badge badge-amber">{relevance}% Relevance</span>'
        f"{_accuracy_bar(relevance)}"
        f'<p style="margin-top:10px;">{html.escape(response)}</p>'
        f'<div class="meta">Queries used: {queries_html}</div>'
        f'<div style="margin-top:6px;">{sources_html}</div>'
        "</div>"
    )
    st.markdown(markup, unsafe_allow_html=True)


def render_agent3_badge(agent_data: dict) -> None:
    persisted = agent_data.get("persisted", False)
    confirmation = agent_data.get("memory_confirmation", "")
    session_id = agent_data.get("session_id", "")
    badge_class = "badge-green" if persisted else "badge-gray"
    icon = "💾" if persisted else "⚠️"

    markup = (
        '<div class="support-card">'
        "<h4>🗄️ Agent 3 — Long-Term Memory Archivist</h4>"
        f'<span class="badge {badge_class}">{icon} Recorded into Neo4j Knowledge Graph '
        f"(Session #{html.escape(str(session_id))})</span>"
        f'<p style="margin-top:10px;">{html.escape(str(confirmation))}</p>'
        "</div>"
    )
    st.markdown(markup, unsafe_allow_html=True)
