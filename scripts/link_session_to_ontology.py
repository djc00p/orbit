#!/usr/bin/env python3
"""
Link session memory to your Orbit ontology.

Reads a session transcript, extracts memory snippets, matches them to
ontology entity names, and writes MemoryChunk + referenced_in ops.

Usage:
    python3 link_session_to_ontology.py --session /path/to/session.jsonl
    python3 link_session_to_ontology.py --latest  # auto-find latest session
"""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

def find_latest_session(agent_dir: Path) -> Path:
    """Find the most recently modified session file."""
    sessions = sorted(
        agent_dir.glob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    if not sessions:
        raise FileNotFoundError(f"No session files in {agent_dir}")
    return sessions[0]

def load_entities(graph_path: Path):
    """Load all entities from the ontology graph."""
    entities = {}
    if not graph_path.exists():
        return entities
    for line in graph_path.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            op = json.loads(line)
            if op.get("op") == "create" and "entity" in op:
                entities[op["entity"]["id"]] = op["entity"]
        except (json.JSONDecodeError, KeyError):
            pass
    return entities

def extract_results(session_path: Path, min_score: float = 0.4):
    """Extract memory_search results from a session transcript."""
    results = []
    for line in session_path.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            msg = json.loads(line)
            if msg.get("role") != "assistant":
                continue
            for part in msg.get("content", []):
                if part.get("type") == "toolCall" and part.get("name") == "memory_search":
                    args = json.loads(part.get("arguments", "{}"))
                    results.append(args.get("query", "unknown"))
        except (json.JSONDecodeError, KeyError):
            pass
    return results

def match_to_entities(queries, entities):
    """Match query text to entity names by simple substring."""
    matches = []
    entity_names = {
        eid: e.get("properties", {}).get("name", "")
        for eid, e in entities.items()
    }
    for query in queries:
        query_lower = query.lower()
        for eid, name in entity_names.items():
            if name and name.lower() in query_lower:
                matches.append((query, eid))
                break
    return matches

def main():
    parser = argparse.ArgumentParser(description="Link session memory to ontology")
    parser.add_argument("--graph", type=Path, default=Path("graph.jsonl"),
                        help="Path to ontology graph (default: ./graph.jsonl)")
    parser.add_argument("--session", type=Path,
                        help="Path to specific session transcript")
    parser.add_argument("--agent-dir", type=Path,
                        help="Directory containing agent sessions (for --latest)")
    parser.add_argument("--latest", action="store_true",
                        help="Use most recent session from agent-dir")
    parser.add_argument("--min-score", type=float, default=0.4,
                        help="Minimum relevance score (default: 0.4)")
    args = parser.parse_args()

    # Resolve graph path
    graph_path = args.graph
    if not graph_path.is_absolute():
        graph_path = Path.cwd() / graph_path

    # Resolve session path
    if args.latest:
        if not args.agent_dir:
            print("Error: --latest requires --agent-dir")
            return
        session_path = find_latest_session(args.agent_dir)
        print(f"Using latest session: {session_path}")
    elif args.session:
        session_path = args.session
    else:
        print("Error: Provide --session or --latest + --agent-dir")
        return

    # Load data
    entities = load_entities(graph_path)
    print(f"Loaded {len(entities)} entities from {graph_path}")

    queries = extract_results(session_path, args.min_score)
    print(f"Extracted {len(queries)} memory queries from {session_path}")

    matches = match_to_entities(queries, entities)
    print(f"Matched {len(matches)} queries to entities")

    # Write MemoryChunk ops
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(graph_path, "a") as f:
        for query, eid in matches:
            chunk_id = f"mc_{timestamp.replace(':', '').replace('-', '')}"
            chunk = {
                "op": "create",
                "entity": {
                    "id": chunk_id,
                    "type": "MemoryChunk",
                    "properties": {
                        "content": query[:200],
                        "source": "session_link",
                        "timestamp": timestamp
                    }
                }
            }
            rel = {
                "op": "relate",
                "from": chunk_id,
                "rel": "referenced_in",
                "to": eid
            }
            json.dump(chunk, f)
            f.write("\n")
            json.dump(rel, f)
            f.write("\n")
            print(f"  Linked: {query[:60]}... -> {eid}")

    print(f"\nAppended {len(matches)} MemoryChunks to {graph_path}")

if __name__ == "__main__":
    main()
