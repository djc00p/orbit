#!/usr/bin/env python3
"""
Manual trigger: links current session's memory_search results to the shared ontology.
Reads the active Kael session transcript, extracts memory snippets, matches them to
ontology entity names, and writes MemoryChunk + referenced_in ops to the graph.

Usage: python3 link_session_to_ontology.py
"""
import json
from pathlib import Path
from datetime import datetime, timezone

GRAPH_PATH = Path.home() / ".openclaw/shared-ontology/graph.jsonl"
SESSION_FILE = Path.home() / ".openclaw/agents/main/sessions/32ae8659-7b66-4143-b2c8-b1a88353f1c8.jsonl"
MIN_SCORE = 0.4

def load_entities():
    entities = {}
    for line in GRAPH_PATH.read_text().strip().split("\n"):
        try:
            op = json.loads(line)
            if op["op"] == "create" and "entity" in op:
                entities[op["entity"]["id"]] = op["entity"]
            elif op["op"] == "delete":
                entities.pop(op.get("id", ""), None)
        except:
            pass
    return entities

def extract_results():
    results = []
    seen = set()
    for line in SESSION_FILE.read_text().strip().split("\n"):
        try:
            msg = json.loads(line)
            details = msg.get("message", {}).get("details", {})
            if isinstance(details, dict) and "results" in details:
                for r in details["results"]:
                    if isinstance(r, dict) and r.get("score", 0) >= MIN_SCORE and r.get("snippet"):
                        key = r["snippet"][:100]
                        if key not in seen:
                            seen.add(key)
                            results.append({"snippet": r["snippet"], "score": r["score"]})
        except:
            pass
    return results

def find_entities(snippet, entities):
    lower = snippet.lower()
    matched = []
    for eid, entity in entities.items():
        if entity.get("type") in ("MemoryChunk", "Agent"):
            continue
        for field in ["name", "title", "goal"]:
            val = entity.get("properties", {}).get(field, "").lower()
            if val and val in lower:
                matched.append(eid)
                break
    return list(set(matched))

def main():
    if not GRAPH_PATH.exists():
        print("No shared ontology found at", GRAPH_PATH)
        return

    entities = load_entities()
    results = extract_results()
    print(f"Found {len(results)} unique memory snippets (score >= {MIN_SCORE})")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    ops = []
    linked = 0

    for i, r in enumerate(results):
        matched = find_entities(r["snippet"], entities)
        if not matched:
            continue
        chunk_id = f"mc_{ts}_{i}"
        chunk = {
            "id": chunk_id,
            "type": "MemoryChunk",
            "properties": {
                "content": r["snippet"][:300].replace("\n", " "),
                "source": "memory_search_manual",
                "score": str(round(r["score"], 4)),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        ops.append(json.dumps({"op": "create", "entity": chunk}))
        for eid in matched:
            ops.append(json.dumps({"op": "relate", "from": chunk_id, "rel": "referenced_in", "to": eid}))
            linked += 1
            print(f"  {chunk_id} → {eid} (score: {r['score']:.2f})")

    if ops:
        with open(GRAPH_PATH, "a") as f:
            f.write("\n".join(ops) + "\n")
        print(f"\n✅ Linked {linked} connection(s) to ontology")
    else:
        print("No entity matches found. Add more entities with: ont create --type Project ...")

if __name__ == "__main__":
    main()
