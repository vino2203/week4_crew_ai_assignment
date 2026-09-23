# Multi-Agent Customer Support System

CrewAI multi-agent backend (Hybrid RAG: FAISS + Neo4j + SerpAPI) with a Streamlit
frontend. See [Crew_ai.md](Crew_ai.md) for the full architecture spec and
[backend/README.md](backend/README.md) for backend setup.

## Quickstart

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Fill in backend/.env with your OpenAI + SerpAPI keys (Neo4j is optional —
# the app falls back to an in-memory mock graph store automatically).

python backend/main.py --seed      # ingest the 3 sample support docs
streamlit run frontend/app.py      # launch the full app
```

Open the app, use **📁 Document Upload** to add more docs (or rely on the
seeded ones), then go to **💬 Customer Support Chatbot** to ask a question and
inspect each agent's response.
