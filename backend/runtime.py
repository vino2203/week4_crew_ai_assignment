"""Shared singleton runtime state: one VectorStore / KnowledgeGraph / HybridRetriever
per process, so the Streamlit frontend, the CLI, and the CrewAI tools all see the
same ingested data without re-loading FAISS/Neo4j on every call.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

from rag.hybrid_retriever import HybridRetriever
from rag.knowledge_graph import KnowledgeGraph
from rag.vector_store import VectorStore

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BACKEND_DIR, ".env"))

_vector_store: VectorStore | None = None
_knowledge_graph: KnowledgeGraph | None = None
_hybrid_retriever: HybridRetriever | None = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        default_dir = os.path.join(_BACKEND_DIR, "data", "faiss_index")
        index_dir = os.getenv("FAISS_INDEX_DIR", default_dir)
        model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        _vector_store = VectorStore(index_dir=index_dir, embedding_model=model)
    return _vector_store


def get_knowledge_graph() -> KnowledgeGraph:
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph(
            uri=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD"),
        )
    return _knowledge_graph


def get_hybrid_retriever() -> HybridRetriever:
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever(get_vector_store(), get_knowledge_graph())
    return _hybrid_retriever
