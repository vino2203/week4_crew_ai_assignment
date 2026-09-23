"""Neo4j knowledge graph client with an in-memory mock fallback.

Models (:Document), (:Product), (:Issue), (:Solution), (:Customer), and
(:CustomerSession) nodes so support conversations and cited documents become
durable, queryable long-term memory. If a real Neo4j instance is not
reachable, an in-memory mock store with an identical interface is used
automatically so the rest of the app keeps working.
"""
from __future__ import annotations

import itertools
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Lightweight heuristic entity vocabulary (kept intentionally simple/offline).
_PRODUCT_TERMS = ["CloudSync", "SyncBox Pro", "Admin Console", "CloudSync Pro"]
_ISSUE_TERMS = [
    "sync conflict",
    "lockout",
    "password reset",
    "overheating",
    "fan noise",
    "network",
    "no network",
    "boot",
    "power",
    "storage quota",
    "billing",
    "refund",
    "cancellation",
    "downgrade",
    "uptime",
    "outage",
    "2fa",
    "rma",
]
_SOLUTION_TERMS = [
    "factory reset",
    "power-cycle",
    "unlock account",
    "force password reset",
    "service credit",
    "prepaid shipping label",
    "safe-mode boot",
    "firmware update",
    "upgrade the plan",
]


def extract_entities(text: str) -> Dict[str, List[str]]:
    lower = text.lower()
    found = {"Product": [], "Issue": [], "Solution": []}
    for term in _PRODUCT_TERMS:
        if term.lower() in lower and term not in found["Product"]:
            found["Product"].append(term)
    for term in _ISSUE_TERMS:
        if term.lower() in lower and term not in found["Issue"]:
            found["Issue"].append(term)
    for term in _SOLUTION_TERMS:
        if term.lower() in lower and term not in found["Solution"]:
            found["Solution"].append(term)
    return found


class _MockGraphStore:
    """In-memory graph store matching the Neo4j-backed store's interface."""

    def __init__(self):
        self.documents: Dict[str, dict] = {}
        self.entities: Dict[str, set] = {"Product": set(), "Issue": set(), "Solution": set()}
        self.entity_links: List[dict] = []  # {document, entity_type, entity}
        self.sessions: List[dict] = []
        self.connected = False
        self.backend = "mock (in-memory)"

    def link_document_entities(self, document_name: str, page_number: int, text: str) -> int:
        self.documents.setdefault(document_name, {"pages": 0})
        self.documents[document_name]["pages"] += 1
        entities = extract_entities(text)
        triples_created = 0
        for entity_type, names in entities.items():
            for name in names:
                self.entities[entity_type].add(name)
                self.entity_links.append(
                    {
                        "document": document_name,
                        "page": page_number,
                        "entity_type": entity_type,
                        "entity": name,
                    }
                )
                triples_created += 1
        return triples_created

    def related_entities(self, text: str) -> Dict[str, List[str]]:
        return extract_entities(text)

    def persist_session(
        self,
        session_id: str,
        customer_id: str,
        query: str,
        resolution: str,
        cited_documents: List[str],
    ) -> dict:
        record = {
            "session_id": session_id,
            "customer_id": customer_id,
            "query": query,
            "resolution": resolution,
            "cited_documents": cited_documents,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.sessions.append(record)
        return record

    @property
    def stats(self) -> dict:
        return {
            "backend": self.backend,
            "connected": self.connected,
            "documents": len(self.documents),
            "triples_created": len(self.entity_links),
            "sessions_persisted": len(self.sessions),
        }


class _Neo4jGraphStore:
    """Real Neo4j-backed graph store."""

    def __init__(self, uri: str, username: str, password: str):
        from neo4j import GraphDatabase

        self._driver = GraphDatabase.driver(uri, auth=(username, password))
        self._driver.verify_connectivity()
        self.connected = True
        self.backend = f"neo4j ({uri})"

    def close(self):
        self._driver.close()

    def link_document_entities(self, document_name: str, page_number: int, text: str) -> int:
        entities = extract_entities(text)
        triples_created = 0
        with self._driver.session() as session:
            session.run(
                "MERGE (d:Document {name: $name})",
                name=document_name,
            )
            for entity_type, names in entities.items():
                for name in names:
                    session.run(
                        f"""
                        MERGE (e:{entity_type} {{name: $entity}})
                        WITH e
                        MATCH (d:Document {{name: $doc}})
                        MERGE (d)-[:MENTIONS {{page: $page}}]->(e)
                        """,
                        entity=name,
                        doc=document_name,
                        page=page_number,
                    )
                    triples_created += 1
        return triples_created

    def related_entities(self, text: str) -> Dict[str, List[str]]:
        return extract_entities(text)

    def persist_session(
        self,
        session_id: str,
        customer_id: str,
        query: str,
        resolution: str,
        cited_documents: List[str],
    ) -> dict:
        with self._driver.session() as session:
            session.run(
                """
                MERGE (c:Customer {customer_id: $customer_id})
                CREATE (s:CustomerSession {
                    session_id: $session_id, query: $query, resolution: $resolution,
                    timestamp: datetime()
                })
                MERGE (c)-[:HAD_SESSION]->(s)
                WITH s
                UNWIND $docs AS doc_name
                MATCH (d:Document {name: doc_name})
                MERGE (s)-[:CITED]->(d)
                """,
                customer_id=customer_id,
                session_id=session_id,
                query=query,
                resolution=resolution,
                docs=cited_documents,
            )
        return {
            "session_id": session_id,
            "customer_id": customer_id,
            "query": query,
            "resolution": resolution,
            "cited_documents": cited_documents,
        }

    @property
    def stats(self) -> dict:
        with self._driver.session() as session:
            doc_count = session.run("MATCH (d:Document) RETURN count(d) AS c").single()["c"]
            triple_count = session.run(
                "MATCH (:Document)-[r:MENTIONS]->() RETURN count(r) AS c"
            ).single()["c"]
            session_count = session.run(
                "MATCH (s:CustomerSession) RETURN count(s) AS c"
            ).single()["c"]
        return {
            "backend": self.backend,
            "connected": self.connected,
            "documents": doc_count,
            "triples_created": triple_count,
            "sessions_persisted": session_count,
        }


class KnowledgeGraph:
    """Facade that transparently uses Neo4j when reachable, else the mock store."""

    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self._store = None
        if uri and username and password:
            try:
                self._store = _Neo4jGraphStore(uri, username, password)
            except Exception:
                self._store = None
        if self._store is None:
            self._store = _MockGraphStore()

    def link_document_entities(self, document_name: str, page_number: int, text: str) -> int:
        return self._store.link_document_entities(document_name, page_number, text)

    def related_entities(self, text: str) -> Dict[str, List[str]]:
        return self._store.related_entities(text)

    def persist_session(
        self,
        query: str,
        resolution: str,
        cited_documents: List[str],
        session_id: Optional[str] = None,
        customer_id: str = "anonymous",
    ) -> dict:
        session_id = session_id or str(uuid.uuid4())[:8]
        return self._store.persist_session(session_id, customer_id, query, resolution, cited_documents)

    @property
    def stats(self) -> dict:
        return self._store.stats

    @property
    def is_connected_to_real_neo4j(self) -> bool:
        return isinstance(self._store, _Neo4jGraphStore)
