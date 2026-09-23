"""Ingests backend/data/sample_docs/* into the FAISS store and links entities
into the Neo4j knowledge graph, printing summary metrics.

Run: python -m data.seed_data   (from the backend/ directory, with venv active)
"""
from __future__ import annotations

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import get_knowledge_graph, get_vector_store  # noqa: E402

_SAMPLE_DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_docs")


def seed() -> dict:
    vector_store = get_vector_store()
    knowledge_graph = get_knowledge_graph()

    triples_created = 0
    files = sorted(glob.glob(os.path.join(_SAMPLE_DOCS_DIR, "*.md")))
    already_indexed = set(vector_store.stats["document_names"])

    for file_path in files:
        document_name = os.path.basename(file_path)
        if document_name in already_indexed:
            print(f"Skipping {document_name} (already indexed)")
            continue

        result = vector_store.ingest_document(file_path, document_name=document_name)
        for chunk in vector_store.chunks:
            if chunk.document_name == document_name:
                triples_created += knowledge_graph.link_document_entities(
                    chunk.document_name, chunk.page_number, chunk.text
                )
        print(f"Indexed {document_name}: {result['pages_indexed']} pages")

    summary = {
        "documents_indexed": vector_store.stats["documents_indexed"],
        "total_pages": vector_store.stats["total_pages"],
        "graph_triples_created": knowledge_graph.stats["triples_created"],
        "graph_backend": knowledge_graph.stats["backend"],
    }
    print("\nSeed summary:", summary)
    return summary


if __name__ == "__main__":
    seed()
