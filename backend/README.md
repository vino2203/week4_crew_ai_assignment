# Backend — Hybrid RAG + CrewAI Multi-Agent Support

## Setup

```bash
cd Week4_assignment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Copy `backend/.env.example` to `backend/.env` (already done) and fill in:
- `OPENAI_API_KEY` / `OPENAI_MODEL_NAME` — required for the CrewAI agents' LLM.
- `SERPAPI_API_KEY` — required for Agent 2 (web search). Without it, Agent 2
  reports that it is not configured rather than failing the whole crew.
- `NEO4J_URI` / `NEO4J_USERNAME` / `NEO4J_PASSWORD` — optional. If no Neo4j
  instance is reachable (e.g. you haven't run `docker compose up`), the system
  automatically falls back to an in-memory mock graph store.

## Seed the knowledge base

```bash
cd backend
python main.py --seed
```

This ingests `data/sample_docs/*.md` page-by-page into FAISS and links
Product/Issue/Solution entities into the knowledge graph.

## Run

- CLI: `python backend/main.py`
- Full app (frontend + backend): `streamlit run frontend/app.py` from the
  project root.

## Optional: real Neo4j via Docker

```bash
cd backend
docker compose up -d
```
