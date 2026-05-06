# Orbit

> A lightweight JSONL knowledge graph for multi-agent AI systems.

Persist entities, relationships, and learnings across sessions. Two agents, one shared graph. Queryable, versionable, human-readable. Built for OpenClaw but works anywhere.

---

## What Is Orbit?

AI agents wake up fresh every session. Orbit is their **long-term memory** — a structured, versionable, shareable graph that agents and humans can both query and update.

Instead of losing context every restart, your agents build a growing knowledge base:
- Projects they're working on
- Tasks with status
- Learnings from mistakes
- Skills they can use
- Documents they've read
- People they interact with
- Concepts they've explored

## Entity Types

| Type | Purpose | Example |
|------|---------|---------|
| `Project` | Active or planned work | `mypridri` — rideshare app |
| `Task` | Actionable items with status | `Merge PR #69` |
| `Learning` | Lessons, gotchas, insights | `db:prepare pollutes test DB` |
| `Skill` | Published or internal capabilities | `rails-ci-fixer` |
| `Document` | Research, summaries, concepts | `Season Extension for Zone 5b` |
| `Person` | Authors, collaborators, contacts | `Eugene Yan` |
| `Concept` | Abstract ideas and frameworks | `Cognitive Surrender` |
| `Agent` | AI agents themselves | `Kael`, `Ayo` |

## Relationship Types

| Relation | From → To |
|----------|-----------|
| `has_task` | Project → Task |
| `has_doc` | Project → Document |
| `has_skill` | Project/Agent → Skill |
| `owns` | Person → anything |
| `wrote_about` | Person → Concept |
| `author_of` | Person → Document |
| `relates_to` | cross-linking |
| `discovered_by` | Learning → Agent |

## Quick Start

### 1. Create an entity

```bash
ont create --type Project --id proj_myapp \
  --props '{"name":"My App","status":"active","goal":"Build something useful"}'
```

### 2. Query entities

```bash
ont query --type Task --where '{"status":"open"}'
ont list --type Learning | head -20
```

### 3. Relate entities

```bash
ont relate --from proj_myapp --rel has_task --to task_setup-ci
ont relate --from p_you --rel owns --to proj_myapp
```

### 4. Visualize (coming soon)

```bash
python3 scripts/orbit_viz.py --center proj_myapp --output orbit.svg
```

## Installation

```bash
git clone https://github.com/djc00p/orbit.git
cd orbit
```

The graph is just JSONL — no database, no server, no dependencies. Python 3.8+ recommended for the CLI tools.

### OpenClaw Users

If you use OpenClaw, point your `ont` function at the shared ontology directory:

```bash
ont() {
  (cd ~/.openclaw/shared-ontology && \
   python3 /path/to/orbit/scripts/ontology.py "$@" --graph graph.jsonl)
}
```

## Tools

| Script | Purpose |
|--------|---------|
| `scripts/ontology.py` | Core CLI: create, query, relate, list, validate |
| `scripts/dedup_ontology.py` | Remove duplicates after bulk imports |
| `scripts/enrich_ontology.py` | Batch-import from structured data |
| `scripts/orbit_viz.py` | Generate radial SVG (MVP) |

### Shell Helper

Add to your `.zshrc` or `.bashrc`:

```bash
ont() {
  (cd ~/.openclaw/shared-ontology && \
   python3 /path/to/orbit/scripts/ontology.py "$@" --graph graph.jsonl)
}
```

## Multi-Agent Setup

The key insight: **agents coordinate via the graph, not messages.**

```
┌─────────────┐     ┌─────────────┐
│    Kael     │     │     Ayo     │
│  (agent 1)  │     │  (agent 2)  │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 ▼
      ┌─────────────────────┐
      │   shared-ontology/  │
      │    graph.jsonl      │
      └─────────────────────┘
```

Each agent:
1. Reads the graph on startup
2. Enriches it from their own perspective
3. Deduplication merges overlaps

### Ontology-First Communication

Instead of messaging:
```bash
# Kael creates a task for Ayo
ont create --type Task --id task_research \
  --props '{"name":"Research TLS errors","status":"pending","assignee":"ayo"}'
ont relate --from task_research --rel created_by --to agent_kael
```

Ayo picks it up on her next session:
```bash
ont query --type Task --where '{"status":"pending","assignee":"ayo"}'
```

## Orbit View

A radial knowledge visualization where any entity becomes the center:

| Ring | Meaning |
|------|---------|
| Center | The focused entity |
| Ring 1 | Direct relationships |
| Ring 2 | Type siblings |
| Ring 3 | Topic adjacency |
| Ring 4 | Loose connections |

See `docs/concepts/orbit-view-design.md` for full design spec.

## Graph Structure

```jsonl
{"op": "create", "entity": {"id": "proj_test", "type": "Project", "properties": {"name": "Test", "status": "active"}}}
{"op": "relate", "from": "p_user", "rel": "owns", "to": "proj_test"}
```

- Plain JSONL — human-readable, git-friendly
- Append-only operations — never corrupts existing data
- Versionable — `git diff` shows exactly what changed

## Example: Enriching from Your Codebase

```python
# scripts/enrich_from_git.py
import subprocess, json

projects = [
    ("proj_orbit", {"name": "Orbit", "status": "active"}),
    ("proj_myapp", {"name": "My App", "status": "pending"}),
]

for eid, props in projects:
    subprocess.run([
        "ont", "create", "--type", "Project",
        "--id", eid, "--props", json.dumps(props)
    ])

# Then deduplicate after bulk imports
subprocess.run(["python3", "scripts/dedup_ontology.py"])
```

## Cost

Free. No database. No API keys. No server. Just JSONL.

## Contributing

1. Fork the repo
2. Add your enrichment script or tool
3. Open a PR with what you added to the graph

## Roadmap

- [x] Core ontology engine
- [x] Deduplication
- [x] Batch enrichment
- [x] Multi-agent support
- [ ] Radial SVG visualizer
- [ ] Interactive web viewer
- [ ] Time-travel (graph at any point)
- [ ] Auto-enrichment from transcripts
- [ ] Python package (pip install orbit)

## License

MIT — use it, fork it, make it yours.

## Related

- [OpenClaw](https://github.com/openclaw/openclaw) — The AI agent framework Orbit was built for
- [Obsidian](https://obsidian.md) — The note-taking app that inspired Orbit View

## Acknowledgments

Built by Kael and Ayo for Deonte Cooper. The weeds spread when the good soil stops pushing back.
