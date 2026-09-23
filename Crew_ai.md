# Multi-Agent Customer Support System with CrewAI, Hybrid RAG & Streamlit UI

A multi-agent customer support platform featuring a **CrewAI** multi-agent backend and a **Streamlit** frontend designed by a UI/UX specialist.

All components are organized with a primary **`backend/`** (Hybrid RAG with page-by-page FAISS + Neo4j Knowledge Graph + SerpAPI Web Search + CrewAI agents) and **`frontend/`** (Streamlit interactive application with top 2-page navigation: File Upload Flow & Multi-Agent Chatbot).

---

## User Review Required

> [!IMPORTANT]
> **Key Architecture & UX Components**:
> 1. **Top 2-Page Navigation**:
>    - **Page 1: 📁 Document Upload**: Multi-file uploader with a visual step-by-step processing flow (Document Parsing $\to$ Page Extraction $\to$ FAISS Embedding with `document_name` & `page_number` $\to$ Neo4j Graph Entity Linking $\to$ Completed metrics).
>    - **Page 2: 💬 Customer Support Chatbot**: Interactive chat with a dedicated left sidebar containing a **`+ New Chat`** button, session switcher, and live backend health statuses.
> 2. **Multi-Agent Output Transparency**:
>    - Synthesized final customer response from Support Lead.
>    - **Agent 1 (Hybrid RAG)** response with **Accuracy Level / Confidence Score (in %)**, exact document name, and page number citations.
>    - **Agent 2 (SerpAPI Web Intelligence)** response with **Relevance / Accuracy Level (in %)**, query details, and live URLs.
>    - **Agent 3 (Long-Term Memory Archivist)** confirmation badge showing memory persistence in Neo4j.
> 3. **Main Folder Structure**:
>    - `backend/`: Core RAG, FAISS page-by-page store, Neo4j graph, SerpAPI tool, CrewAI agents & crew orchestrator.
>    - `frontend/`: Modern Streamlit app, custom styling, visual pipeline flow components, and session manager.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Frontend [Streamlit UI / UX Layer (frontend/)]
        Nav[Top 2-Page Navigation]
        Page1[Page 1: 📁 Document Upload & Ingestion Flow]
        Page2[Page 2: 💬 Multi-Agent Support Chatbot]
        Sidebar[Left Sidebar: ➕ New Chat & Sessions]
        
        Nav --> Page1
        Nav --> Page2
        Sidebar --> Page2
    end

    subgraph BackendCrew [CrewAI Multi-Agent Team (backend/crew)]
        Lead[Customer Support Lead Agent]
        A1[Agent 1: Internal RAG Specialist]
        A2[Agent 2: SerpAPI Web Specialist]
        A3[Agent 3: Long-term Memory Archivist]
        
        Lead --> A1
        Lead --> A2
        Lead --> A3
    end

    subgraph BackendRAG [Hybrid RAG & Storage (backend/rag)]
        FAISS[(FAISS Multi-Doc Page-by-Page Store)]
        Neo4j[(Neo4j Knowledge Graph & Long-Term Memory)]
        SerpAPI[(SerpAPI Google Search Engine)]
        
        A1 --> FAISS
        A1 --> Neo4j
        A2 --> SerpAPI
        A3 --> Neo4j
    end

    Page1 -->|Trigger Ingestion Pipeline| FAISS
    Page1 -->|Extract Graph Entities| Neo4j
    Page2 -->|Submit Customer Query| Lead
    A1 -->|Output + Accuracy % + Doc/Page| Page2
    A2 -->|Output + Accuracy % + Web URLs| Page2
    A3 -->|Memory Persistence Confirmation| Page2
    Lead -->|Final Resolution| Page2
```

---

## Component Breakdown

### 1. Frontend: Streamlit UI/UX (`frontend/`)
Designed following modern SaaS dashboard patterns with custom CSS, clean typography, badge pills, and responsive layout.

* **Top 2-Page Navigation**:
  * **Page 1: Document Upload & Ingestion Flow (`pages/1_upload_file.py` or Top Tabs)**:
    * Multi-document upload widget (supports `.pdf`, `.md`, `.txt`).
    * **Visual Step-by-Step Processing Flow**:
      1. 📄 *Document Parsing*: Reads uploaded documents and extracts individual pages.
      2. 📑 *Page-by-Page Metadata Tagging*: Tags chunks with `document_name` and `page_number`.
      3. 🧠 *Dense Vector Indexing*: Embeds text and indexes into FAISS.
      4. 🕸️ *Graph Entity Extraction*: Discovers entities (`Product`, `Issue`, `Solution`) and links them into Neo4j.
      5. 🚀 *Pipeline Ready*: Displays summary metrics (Documents Indexed, Total Pages, Graph Triples Created).
  * **Page 2: Customer Support Chatbot (`pages/2_chatbot.py` or Top Tabs)**:
    * **Left Sidebar**:
      * **`➕ New Chat`** prominent button: Resets session state, clears message stream, creates fresh session ID, and refreshes context.
      * Chat Session History list allowing switching between previous support conversations.
      * Live Status Indicators: FAISS Status (🟢 Ready), Neo4j Status (🟢 Active / Mock), SerpAPI Status (🟢 Configured).
      * Quick Test Presets: One-click buttons to load realistic customer queries.
    * **Chat Stream & Transparent Multi-Agent Inspection**:
      * Each assistant message presents the **Synthesized Resolution** from the Customer Support Lead.
      * Expandable / side-by-side **Agent Transparency Cards**:
        * **Agent 1 (Internal Hybrid RAG)**:
          * **Accuracy Level / Confidence Score (%)** (e.g., `94.2% Match`).
          * Exact Citations: `[Document: CloudSync_Admin_Guide.md | Page: 3]`.
          * Retrieved internal KB excerpt and connected Neo4j entity graph.
        * **Agent 2 (SerpAPI Web Intelligence)**:
          * **Accuracy / Relevance Score (%)** (e.g., `89.5% Relevance`).
          * Live search queries executed, top external search results, and direct URLs.
        * **Agent 3 (Long-Term Memory Archivist)**:
          * Badge: `💾 Recorded into Neo4j Knowledge Graph (Session #...)`.
          * Shows the persistent memory node and connected customer profile.

---

### 2. Backend: Hybrid RAG & Storage (`backend/rag/`)
* **FAISS Multi-Doc Page-by-Page Store (`backend/rag/vector_store.py`)**:
  * Ingests files page-by-page.
  * Preserves metadata: `{"document_name": doc_name, "page_number": page_num, "chunk_id": chunk_id, "text": text}`.
  * Calculates vector cosine similarity scores converted to intuitive percentage accuracy (0–100%).
  * Returns formatted citations with exact document name and page number.
* **Neo4j Knowledge Graph & Long-Term Memory (`backend/rag/knowledge_graph.py`)**:
  * Cypher graph queries for multi-hop entity exploration (`Customer`, `Product`, `Issue`, `Solution`).
  * Persists session nodes `(:CustomerSession)` linked to `(:Customer)` and cited `(:Document)`.
  * Includes in-memory mock fallback when local Neo4j Docker container is not yet started.
* **Hybrid Retriever Engine (`backend/rag/hybrid_retriever.py`)**:
  * Blends FAISS page-by-page retrieval with Neo4j subgraphs.

---

### 3. Backend: Tools & CrewAI Agents (`backend/tools/` & `backend/crew/`)
* **Verbose Mode (`verbose=True`)**:
  * **All Agents** are instantiated with `verbose=True` to trace thought processes, goal alignment, and tool invocations.
  * **All Tasks** are instantiated with `verbose=True` (and full task output logging) to trace intermediate step execution.
  * **The Crew** runs with `verbose=True` for complete multi-agent pipeline observability.
* **`backend/tools/rag_tool.py`**: Queries FAISS (doc+page) + Neo4j for Agent 1.
* **`backend/tools/serpapi_search_tool.py`**: Custom tool calling SerpAPI (`GoogleSearch`) with organic ranking and relevance scoring for Agent 2.
* **`backend/tools/memory_tool.py`**: Records conversation inputs/outputs into Neo4j for Agent 3.
* **`backend/crew/agents.py`**:
  * `KnowledgeBaseSpecialist` (Agent 1, `verbose=True`)
  * `WebSearchSpecialist` (Agent 2, `verbose=True`)
  * `MemoryArchivist` (Agent 3, `verbose=True`)
  * `SupportLeadOrchestrator` (Crew Lead, `verbose=True`)
* **`backend/crew/tasks.py`**:
  * Knowledge Retrieval Task (`verbose=True`)
  * Web Intelligence Task (`verbose=True`)
  * Resolution Synthesis Task (`verbose=True`)
  * Memory Archival Task (`verbose=True`)
* **`backend/crew/support_crew.py`**: Executes the sequential agent tasks and structures output payloads with accuracy metrics, citations, and resolutions.

---

## Directory & File Structure

```
backend/
├── README.md                           # Setup and usage guide
├── requirements.txt                     # Dependencies (crewai, faiss-cpu, neo4j, google-search-results, etc.)
├── .env.example                        # Template for OPENAI_API_KEY, SERPAPI_API_KEY, NEO4J_URI
├── docker-compose.yml                  # Neo4j Community edition container
│
├── config/
│   ├── agents.yaml                     # CrewAI agent roles, backstories, and goals
│   └── tasks.yaml                      # CrewAI task descriptions and expected outputs
│
├── rag/
│   ├── __init__.py
│   ├── vector_store.py                 # Multi-document page-by-page FAISS indexer & retriever
│   ├── knowledge_graph.py              # Neo4j client & Cypher query engine (with mock fallback)
│   └── hybrid_retriever.py             # Blends Vector (doc+page) + Graph RAG outputs
│
├── tools/
│   ├── __init__.py
│   ├── rag_tool.py                     # CrewAI Tool for Hybrid RAG with doc & page citations
│   ├── serpapi_search_tool.py          # CrewAI Tool for SerpAPI Web Search
│   └── memory_tool.py                  # CrewAI Tool for storing interaction into Neo4j memory
│
├── crew/
│   ├── __init__.py
│   ├── agents.py                       # CrewAI Agent definitions
│   ├── tasks.py                        # CrewAI Task definitions
│   └── support_crew.py                 # Crew orchestration & sequential workflow execution
│
├── data/
│   ├── __init__.py
│   ├── seed_data.py                    # Script to populate FAISS docs (page-by-page) and Neo4j graph
│   └── sample_docs/                    # Multi-document support manuals with multiple pages
│       ├── CloudSync_Admin_Guide.md
│       ├── Hardware_Troubleshooting_Manual.md
│       └── SLA_and_Refund_Policy.md
│
└── main.py                             # Interactive CLI entrypoint

frontend/
├── app.py                              # Main Streamlit entrypoint with Top Navigation
├── styles.css                          # Modern custom CSS (cards, badges, animations)
├── components/
│   ├── __init__.py
│   ├── flow_visualizer.py              # Visual processing flow for document ingestion
│   ├── agent_card.py                   # Agent 1 & Agent 2 comparison cards with accuracy %
│   └── sidebar.py                      # Left panel: New Chat button, session list, status badges
└── pages_view/
    ├── upload_page.py                  # Page 1: Upload File & Data Processing Flow
    └── chat_page.py                    # Page 2: Chatbot with multi-agent breakdown
```

---

## Verification Plan

### Automated & Unit Verification
1. **Backend Tests**:
   * Verify FAISS multi-doc page-by-page indexing and exact citations (`[Document: ..., Page: ...]`).
   * Verify Neo4j knowledge graph queries and session memory writing.
   * Verify SerpAPI search tool output and relevance scoring.
   * Verify CrewAI multi-agent orchestration and task execution.
2. **Frontend Tests**:
   * Verify Streamlit imports and components render without syntax/runtime errors.
   * Verify file upload flow simulation (extracts pages, stores in FAISS, links to Neo4j).
   * Verify "New Chat" button creates a new session ID and clears history.
   * Verify Agent 1 and Agent 2 accuracy percentage rendering in the UI.

### Manual UI Verification
* Launch Streamlit app (`streamlit run frontend/app.py`).
* Navigate between **📁 Document Upload** and **💬 Chatbot** using the top navigation bar.
* Upload a sample document on Page 1 and observe the animated multi-step ingestion flow.
* Run a support query on Page 2, verify the left panel **New Chat** button, and inspect the Agent 1 vs Agent 2 comparison cards with accuracy percentages.
