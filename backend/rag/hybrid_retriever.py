"""Blends FAISS page-by-page vector retrieval with Neo4j graph context."""
from __future__ import annotations

from typing import List

from rag.knowledge_graph import KnowledgeGraph
from rag.vector_store import VectorStore


class HybridRetriever:
    def __init__(self, vector_store: VectorStore, knowledge_graph: KnowledgeGraph):
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph

    def retrieve(self, query: str, top_k: int = 3) -> dict:
        results = self.vector_store.search(query, top_k=top_k)

        if not results:
            return {
                "found": False,
                "passages": [],
                "avg_accuracy": 0.0,
                "citations": [],
                "graph_entities": {},
            }

        graph_entities = self.knowledge_graph.related_entities(
            " ".join(r.text for r in results)
        )

        return {
            "found": True,
            "passages": [
                {
                    "document_name": r.document_name,
                    "page_number": r.page_number,
                    "text": r.text,
                    "accuracy_pct": r.accuracy_pct,
                }
                for r in results
            ],
            "avg_accuracy": round(sum(r.accuracy_pct for r in results) / len(results), 1),
            "citations": [
                {"document": r.document_name, "page": r.page_number} for r in results
            ],
            "graph_entities": graph_entities,
        }
