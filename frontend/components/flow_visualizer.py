"""Visual step-by-step document ingestion pipeline flow."""
from __future__ import annotations

import streamlit as st

STEPS = [
    ("📄", "Document Parsing", "Reads uploaded documents and extracts individual pages."),
    ("📑", "Page-by-Page Metadata Tagging", "Tags chunks with document_name and page_number."),
    ("🧠", "Dense Vector Indexing", "Embeds text and indexes into FAISS."),
    ("🕸️", "Graph Entity Extraction", "Discovers Product/Issue/Solution entities and links them into Neo4j."),
    ("🚀", "Pipeline Ready", "Ingestion complete — document is now searchable."),
]


def render_flow(current_step: int, total_steps: int = len(STEPS)) -> None:
    """Renders the 5-step ingestion flow. Steps < current_step are marked done."""
    for i, (icon, title, desc) in enumerate(STEPS):
        state = "done" if i < current_step else "pending"
        check = "✅" if state == "done" else "⏳"
        markup = (
            f'<div class="flow-step {state}">'
            f'<span class="icon">{icon}</span>'
            "<div>"
            f"<strong>{title}</strong> {check}<br/>"
            f'<span class="meta">{desc}</span>'
            "</div>"
            "</div>"
        )
        st.markdown(markup, unsafe_allow_html=True)


def render_summary_metrics(documents_indexed: int, total_pages: int, graph_triples: int) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("📚 Documents Indexed", documents_indexed)
    col2.metric("📑 Total Pages", total_pages)
    col3.metric("🕸️ Graph Triples Created", graph_triples)
