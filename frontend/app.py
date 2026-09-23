"""Streamlit entrypoint: Top 2-page navigation (Document Upload / Chatbot)."""
from __future__ import annotations

import os
import sys

import streamlit as st

_FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_FRONTEND_DIR)
_BACKEND_DIR = os.path.join(_PROJECT_ROOT, "backend")

for path in (_FRONTEND_DIR, _BACKEND_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from runtime import get_knowledge_graph, get_vector_store  # noqa: E402
from crew.support_crew import SupportCrew  # noqa: E402

from pages_view import chat_page, upload_page  # noqa: E402

st.set_page_config(
    page_title="Customer Support Multi-Agent System",
    page_icon="💬",
    layout="wide",
)


def _load_css() -> None:
    css_path = os.path.join(_FRONTEND_DIR, "styles.css")
    with open(css_path, "r") as fh:
        st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def _get_crew() -> SupportCrew:
    return SupportCrew()


def main() -> None:
    _load_css()

    st.markdown("# 🎧 Multi-Agent Customer Support System")
    st.caption("Hybrid RAG (FAISS + Neo4j) · SerpAPI Web Intelligence · CrewAI Agents")

    vector_store = get_vector_store()
    knowledge_graph = get_knowledge_graph()
    crew = _get_crew()

    tab1, tab2 = st.tabs(["📁 Document Upload", "💬 Customer Support Chatbot"])

    with tab1:
        upload_page.render(vector_store, knowledge_graph)

    with tab2:
        chat_page.render(vector_store, knowledge_graph, crew)


if __name__ == "__main__":
    main()
