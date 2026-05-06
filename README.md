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
| `Project` | Active or planned work | `proj_website` — your web app |
| `Task` | Actionable items with status | `task_setup-ci` |
| `Learning` | Lessons, gotchas, insights | `learn_cors-preflight-20260506` |
| `Skill` | Published or internal capabilities | `skill_api-design` |
| `Document` | Research, summaries, concepts | `doc_scaling-strategies` |
| `Person` | Authors, collaborators, contacts | `p_ada-lovelace` |
| `Concept` | Abstract ideas and frameworks | `concept_cognitive-load` |
| `Agent` | AI agents themselves | `agent_alice`, `agent_bob` |

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

## Setting Up the `ont` Command

The examples use `ont` as a shorthand. It's just a shell function that calls `scripts/ontology.py` with the right `--graph` path.

### Option A: Shell function (recommended)

Add to your `.bashrc`, `.zshrc`, or `.bash_profile`:

```bash
ont() {
  local graph="${ORBIT_GRAPH:-graph.jsonl}"
  python3 /path/to/orbit/scripts/ontology.py "$@" --graph "$graph"
}
```

Then reload:
```bash
source ~/.bashrc   # or ~/.zshrc
```

### Option B: Alias with fixed path

```bash
alias ont='python3 /path/to/orbit/scripts/ontology.py --graph graph.jsonl'
```

### Option C: Run directly (no setup)

Skip `ont` and call the script directly:

```bash
python3 scripts/ontology.py create --type Project --id proj_demo \
  --props '{"name":"Demo","status":"active"}' --graph graph.jsonl
```

### Custom graph location

Set `ORBIT_GRAPH` to use a graph outside the repo directory:

```bash
export ORBIT_GRAPH="$HOME/projects/my-project/graph.jsonl"
ont list
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

If you use OpenClaw, point your `ont` function at your shared ontology directory:

```bash
ont() {
  (cd ~/.openclaw/shared-ontology && \
   python3 /path/to/orbit/scripts/ontology.py "$@" --graph graph.jsonl)
}
```

## Tools

| Script | Purpose |
| ------ | ------- |
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

```text
┌─────────────┐     ┌─────────────┐
│  Agent 1    │     │  Agent 2    │
│  (Alice)    │     │   (Bob)     │
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
# Alice creates a task for Bob
ont create --type Task --id task_research \
  --props '{"name":"Research API rate limits","status":"pending","assignee":"bob"}'
ont relate --from task_research --rel created_by --to agent_alice
```

Bob picks it up on their next session:

```bash
ont query --type Task --where '{"status":"pending","assignee":"bob"}'
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

Built with the philosophy that AI agents deserve persistent memory. The weeds spread when the good soil stops pushing back.
