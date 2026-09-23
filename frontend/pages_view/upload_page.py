"""Page 1: Document Upload & Ingestion Flow."""
from __future__ import annotations

import os
import tempfile
import time

import streamlit as st

from components.flow_visualizer import render_flow, render_summary_metrics


def render(vector_store, knowledge_graph) -> None:
    st.markdown("## 📁 Document Upload & Ingestion")
    st.caption(
        "Upload support manuals (.pdf, .md, .txt). Each document is parsed page-by-page, "
        "embedded into FAISS with document_name + page_number metadata, and linked into "
        "the Neo4j knowledge graph."
    )

    uploaded_files = st.file_uploader(
        "Drop one or more documents here",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True,
    )

    process_clicked = st.button("🚀 Process Documents", type="primary", disabled=not uploaded_files)

    if process_clicked and uploaded_files:
        flow_placeholder = st.empty()
        total_triples = 0

        for uploaded_file in uploaded_files:
            st.markdown(f"#### Processing `{uploaded_file.name}`")
            step_placeholder = st.empty()

            for step in range(1, 6):
                with step_placeholder.container():
                    render_flow(current_step=step)
                time.sleep(0.25)

            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            try:
                result = vector_store.ingest_document(tmp_path, document_name=uploaded_file.name)
                for chunk in vector_store.chunks:
                    if chunk.document_name == uploaded_file.name:
                        total_triples += knowledge_graph.link_document_entities(
                            chunk.document_name, chunk.page_number, chunk.text
                        )
                st.success(f"✅ Indexed {result['pages_indexed']} pages from {uploaded_file.name}")
            finally:
                os.unlink(tmp_path)

        st.markdown("### 🚀 Pipeline Ready")
        render_summary_metrics(
            documents_indexed=vector_store.stats["documents_indexed"],
            total_pages=vector_store.stats["total_pages"],
            graph_triples=knowledge_graph.stats["triples_created"],
        )
        st.balloons()

    st.markdown("---")
    st.markdown("### Current Knowledge Base")
    render_summary_metrics(
        documents_indexed=vector_store.stats["documents_indexed"],
        total_pages=vector_store.stats["total_pages"],
        graph_triples=knowledge_graph.stats["triples_created"],
    )
    if vector_store.stats["document_names"]:
        st.markdown("**Indexed documents:**")
        for name in vector_store.stats["document_names"]:
            st.markdown(f"- 📄 {name}")
    else:
        st.info(
            "No documents indexed yet. Upload files above, or run "
            "`python backend/main.py --seed` to load the bundled sample docs."
        )
