"""Page 2: Multi-Agent Customer Support Chatbot."""
from __future__ import annotations

import streamlit as st

from components.agent_card import render_agent1_card, render_agent2_card, render_agent3_badge
from components.sidebar import init_session_state, render_sidebar


def _run_query(crew, query: str, session_id: str) -> dict:
    with st.spinner("Support Lead is coordinating Agent 1 (Internal RAG), Agent 2 (Web Search), and Agent 3 (Memory)..."):
        return crew.run(query, session_id=session_id)


def _render_message(message: dict) -> None:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
        return

    with st.chat_message("assistant"):
        st.markdown(message["content"])
        result = message.get("result")
        if result:
            with st.expander("🔍 Inspect Multi-Agent Response", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    render_agent1_card(result["agent_1_internal_rag"])
                with col2:
                    render_agent2_card(result["agent_2_web_search"])
                render_agent3_badge(result["agent_3_memory"])


def render(vector_store, knowledge_graph, crew) -> None:
    init_session_state()
    render_sidebar(vector_store, knowledge_graph)

    st.markdown("## 💬 Multi-Agent Customer Support Chatbot")
    st.caption("Every response is synthesized by the Support Lead from 3 specialist agents — expand to inspect each one.")

    active_session_id = st.session_state.active_session_id
    session = st.session_state.chat_sessions[active_session_id]

    for message in session["messages"]:
        _render_message(message)

    query = st.chat_input("Describe your issue...")
    if st.session_state.pending_query:
        query = st.session_state.pending_query
        st.session_state.pending_query = None

    if query:
        session["messages"].append({"role": "user", "content": query})
        if session["title"].startswith("New chat"):
            session["title"] = query[:40] + ("…" if len(query) > 40 else "")
        with st.chat_message("user"):
            st.markdown(query)

        result = _run_query(crew, query, session_id=active_session_id)

        session["messages"].append(
            {"role": "assistant", "content": result["final_resolution"], "result": result}
        )
        with st.chat_message("assistant"):
            st.markdown(result["final_resolution"])
            with st.expander("🔍 Inspect Multi-Agent Response", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    render_agent1_card(result["agent_1_internal_rag"])
                with col2:
                    render_agent2_card(result["agent_2_web_search"])
                render_agent3_badge(result["agent_3_memory"])
