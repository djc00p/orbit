#!/usr/bin/env python3
"""Deduplicate ontology graph by merging entities with same ID."""
import json, sys, shutil
from pathlib import Path

GRAPH = Path("/Users/DJC00P/.openclaw/shared-ontology/graph.jsonl")
BACKUP = GRAPH.with_suffix(".jsonl.pre-dedup")

# Backup
shutil.copy2(GRAPH, BACKUP)
print(f"Backup: {BACKUP}")

# Collect all operations, keeping only the latest entity per ID
entities = {}  # id -> latest entity dict
relations = []  # list of relation ops
other_ops = []  # anything else

with open(GRAPH) as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            op = json.loads(line)
        except json.JSONDecodeError:
            print(f"Skipping malformed line {i}: {line[:80]}")
            continue

        op_type = op.get("op")
        if op_type == "create" and "entity" in op:
            e = op["entity"]
            eid = e["id"]
            # Keep latest (later lines overwrite earlier)
            entities[eid] = e
        elif op_type == "relate":
            relations.append(op)
        else:
            other_ops.append(op)

print(f"Entities: {len(entities)}")
print(f"Relations: {len(relations)}")
print(f"Other ops: {len(other_ops)}")

# Deduplicate relations (same from+rel+to)
unique_rels = {}
for rel in relations:
    key = (rel.get("from"), rel.get("rel"), rel.get("to"))
    if key not in unique_rels:
        unique_rels[key] = rel
print(f"Relations deduped: {len(relations)} -> {len(unique_rels)}")

# Write deduplicated graph
with open(GRAPH, "w") as f:
    for eid, e in sorted(entities.items()):
        json.dump({"op": "create", "entity": e}, f)
        f.write("\n")
    for rel in unique_rels.values():
        json.dump(rel, f)
        f.write("\n")
    for op in other_ops:
        json.dump(op, f)
        f.write("\n")

# Verify
print(f"\nWrote {len(entities)} unique entities + {len(unique_rels)} unique relations to {GRAPH}")

# Count by type
from collections import Counter
types = Counter(e["type"] for e in entities.values())
print("\nBy type:")
for t, c in types.most_common():
    print(f"  {t}: {c}")
