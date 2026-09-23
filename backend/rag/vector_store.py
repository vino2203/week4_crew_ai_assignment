"""Multi-document, page-by-page FAISS vector store.

Ingests documents (.md, .txt, .pdf) split into pages, embeds each page with a
local sentence-transformers model (no external API needed for indexing), and
supports similarity search returning intuitive percentage accuracy scores
plus exact document/page citations.
"""
from __future__ import annotations

import os
import pickle
import re
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

_PAGE_MARKER_RE = re.compile(r"^\s*#{1,6}\s*Page\s+(\d+)\s*$", re.IGNORECASE | re.MULTILINE)
_SYNTHETIC_PAGE_CHARS = 1500


@dataclass
class PageChunk:
    document_name: str
    page_number: int
    chunk_id: str
    text: str


@dataclass
class SearchResult:
    document_name: str
    page_number: int
    chunk_id: str
    text: str
    accuracy_pct: float


def parse_pages(file_path: str) -> List[str]:
    """Split a document into page-level text chunks."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        return [page.extract_text() or "" for page in reader.pages]

    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
        raw = fh.read()

    markers = list(_PAGE_MARKER_RE.finditer(raw))
    if markers:
        pages = []
        for i, m in enumerate(markers):
            start = m.end()
            end = markers[i + 1].start() if i + 1 < len(markers) else len(raw)
            pages.append(raw[start:end].strip())
        return [p for p in pages if p]

    # No explicit page markers: fall back to fixed-size synthetic pages.
    text = raw.strip()
    if not text:
        return []
    return [
        text[i : i + _SYNTHETIC_PAGE_CHARS]
        for i in range(0, len(text), _SYNTHETIC_PAGE_CHARS)
    ]


class VectorStore:
    """Page-by-page FAISS index across multiple documents."""

    def __init__(self, index_dir: str, embedding_model: str = "all-MiniLM-L6-v2"):
        self.index_dir = index_dir
        self.embedding_model_name = embedding_model
        os.makedirs(index_dir, exist_ok=True)

        self._index_path = os.path.join(index_dir, "index.faiss")
        self._meta_path = os.path.join(index_dir, "meta.pkl")

        self._model = None  # lazy-loaded sentence-transformers model
        self._index = None  # lazy-loaded faiss index
        self.chunks: List[PageChunk] = []

        self._load()

    # -- lazy loaders -----------------------------------------------------
    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.embedding_model_name)
        return self._model

    def _embed(self, texts: List[str]) -> np.ndarray:
        vectors = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        vectors = vectors.astype("float32")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-8
        return vectors / norms

    def _load(self) -> None:
        import faiss

        if os.path.exists(self._index_path) and os.path.exists(self._meta_path):
            self._index = faiss.read_index(self._index_path)
            with open(self._meta_path, "rb") as fh:
                self.chunks = pickle.load(fh)

    def _save(self) -> None:
        import faiss

        faiss.write_index(self._index, self._index_path)
        with open(self._meta_path, "wb") as fh:
            pickle.dump(self.chunks, fh)

    # -- public API ---------------------------------------------------------
    def ingest_document(self, file_path: str, document_name: Optional[str] = None) -> dict:
        """Ingest a document page-by-page. Returns ingestion metrics."""
        import faiss

        document_name = document_name or os.path.basename(file_path)
        pages = parse_pages(file_path)
        if not pages:
            return {"document_name": document_name, "pages_indexed": 0}

        new_chunks = [
            PageChunk(
                document_name=document_name,
                page_number=i + 1,
                chunk_id=f"{document_name}::p{i + 1}",
                text=page_text,
            )
            for i, page_text in enumerate(pages)
        ]

        vectors = self._embed([c.text for c in new_chunks])
        dim = vectors.shape[1]

        if self._index is None:
            self._index = faiss.IndexFlatIP(dim)

        self._index.add(vectors)
        self.chunks.extend(new_chunks)
        self._save()

        return {"document_name": document_name, "pages_indexed": len(new_chunks)}

    def search(self, query: str, top_k: int = 3) -> List[SearchResult]:
        if self._index is None or self._index.ntotal == 0:
            return []

        query_vec = self._embed([query])
        k = min(top_k, self._index.ntotal)
        scores, indices = self._index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]
            # cosine similarity in [-1, 1] -> intuitive 0-100% accuracy
            accuracy = max(0.0, min(1.0, (float(score) + 1) / 2)) * 100
            results.append(
                SearchResult(
                    document_name=chunk.document_name,
                    page_number=chunk.page_number,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    accuracy_pct=round(accuracy, 1),
                )
            )
        return results

    @property
    def stats(self) -> dict:
        doc_names = {c.document_name for c in self.chunks}
        return {
            "documents_indexed": len(doc_names),
            "total_pages": len(self.chunks),
            "document_names": sorted(doc_names),
        }
