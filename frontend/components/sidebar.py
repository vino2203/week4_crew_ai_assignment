"""Left sidebar for the chatbot page: New Chat, session switcher, status badges,
and quick test presets.
"""
from __future__ import annotations

import os
import uuid

import streamlit as st

PRESET_QUERIES = [
    "How do I resolve a CloudSync conflict copy?",
    "My SyncBox Pro won't power on, what should I check?",
    "What's your refund policy if my uptime SLA is missed?",
]


def _new_session() -> str:
    session_id = str(uuid.uuid4())[:8]
    st.session_state.chat_sessions[session_id] = {
        "title": f"New chat {len(st.session_state.chat_sessions) + 1}",
        "messages": [],
    }
    st.session_state.active_session_id = session_id
    return session_id


def init_session_state() -> None:
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
    if "active_session_id" not in st.session_state or st.session_state.active_session_id not in st.session_state.chat_sessions:
        _new_session()
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None


def render_sidebar(vector_store, knowledge_graph) -> None:
    with st.sidebar:
        st.markdown("### 💬 Customer Support")

        st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
        if st.button("➕ New Chat", use_container_width=True):
            _new_session()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("#### Sessions")
        for sid, session in reversed(list(st.session_state.chat_sessions.items())):
            label = session["title"]
            is_active = sid == st.session_state.active_session_id
            if st.button(("🟢 " if is_active else "") + label, key=f"session_{sid}", use_container_width=True):
                st.session_state.active_session_id = sid
                st.rerun()

        st.markdown("---")
        st.markdown("#### System Status")

        faiss_ready = vector_store.stats["total_pages"] > 0
        st.markdown(
            f'<span class="badge {"badge-green" if faiss_ready else "badge-amber"}">'
            f'{"🟢" if faiss_ready else "🟡"} FAISS: {"Ready" if faiss_ready else "Empty — upload docs"}</span>',
            unsafe_allow_html=True,
        )

        kg_connected = knowledge_graph.is_connected_to_real_neo4j
        st.markdown(
            f'<span class="badge {"badge-green" if kg_connected else "badge-gray"}">'
            f'{"🟢" if kg_connected else "⚪"} Neo4j: {"Active" if kg_connected else "Mock"}</span>',
            unsafe_allow_html=True,
        )

        serpapi_key = os.getenv("SERPAPI_API_KEY", "")
        serpapi_ok = bool(serpapi_key) and not serpapi_key.startswith("your-")
        st.markdown(
            f'<span class="badge {"badge-green" if serpapi_ok else "badge-amber"}">'
            f'{"🟢" if serpapi_ok else "🟡"} SerpAPI: {"Configured" if serpapi_ok else "Not set"}</span>',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("#### Quick Test Presets")
        for preset in PRESET_QUERIES:
            if st.button(preset, key=f"preset_{preset}", use_container_width=True):
                st.session_state.pending_query = preset
                st.rerun()
