"""Interactive CLI entrypoint for the multi-agent customer support system.

Usage (from backend/ with the venv active):
    python main.py --seed        # ingest sample_docs into FAISS + Neo4j
    python main.py                # interactive chat loop
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crew.support_crew import SupportCrew  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="CrewAI multi-agent customer support CLI")
    parser.add_argument("--seed", action="store_true", help="Seed sample docs into FAISS + Neo4j and exit")
    args = parser.parse_args()

    if args.seed:
        from data.seed_data import seed

        seed()
        return

    print("Multi-Agent Customer Support CLI. Type 'exit' to quit.\n")
    crew = SupportCrew()
    session_id = None

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            break

        result = crew.run(query, session_id=session_id)
        session_id = result["session_id"]

        print("\n--- Support Lead Resolution ---")
        print(result["final_resolution"])
        print("\n--- Agent 1: Internal RAG ---")
        print(json.dumps(result["agent_1_internal_rag"], indent=2))
        print("\n--- Agent 2: Web Search ---")
        print(json.dumps(result["agent_2_web_search"], indent=2))
        print("\n--- Agent 3: Memory ---")
        print(json.dumps(result["agent_3_memory"], indent=2))
        print()


if __name__ == "__main__":
    main()
