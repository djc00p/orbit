# AGENTS.md — How Agents Use Orbit

## What Is This?

This document is for AI agents (like you) who need to read from and write to the Orbit knowledge graph. It's the operating manual for multi-agent memory.

## Core Principle

**The ontology is the source of truth.** Agents coordinate via shared graph state, not direct messages. When Alice creates a task, Bob sees it on their next session because it's in `graph.jsonl` — not because Alice messaged them.

## Directory Structure

```
~/orbit/
├── graph.jsonl              # The shared knowledge graph
├── scripts/
│   ├── ontology.py          # Core CLI tool
│   ├── dedup_ontology.py    # Remove duplicates after bulk imports
│   ├── enrich_ontology.py     # Batch import from structured data
│   └── orbit_viz.py         # Radial SVG generator (coming soon)
├── docs/
│   └── concepts/
│       └── orbit-view-design.md  # Visualization design spec
├── README.md
├── LICENSE
└── AGENTS.md               # This file
```

## How to Read the Graph

### On Session Start

Every session, read the graph to understand current state:

```bash
# Count entities by type
ont list | grep '"type"' | sort | uniq -c

# Check your active tasks
ont query --type Task --where '{"status":"pending","assignee":"you"}'

# Review recent learnings
ont query --type Learning --limit 20
```

### Using the `ont` Command

The `ont` function is defined in your shell config. It runs `ontology.py` from the shared-ontology directory:

```bash
ont create --type Project --id proj_example --props '{...}'
ont query --type Task --where '{"status":"open"}'
ont relate --from proj_example --rel has_task --to task_001
ont list --type Learning
ont get --id proj_example
ont delete --id old_entity
ont validate
```

## How to Write to the Graph

### Adding a Project

```bash
ont create --type Project --id proj_mynewthing \
  --props '{"name":"My New Thing","status":"active","goal":"Solve a specific problem"}'
```

### Adding a Learning

When you discover something worth remembering:

```bash
ont create --type Learning --id learn_tls-error-20260506 \
  --props '{"name":"TLS handshake failures","status":"active","goal":"Intermittent TLS errors usually resolve after service restart"}'

# Link it to the relevant concept
ont relate --from learn_tls-error-20260506 --rel relates_to --to concept_networking
```

### Adding a Task (Ontology-First Commissioning)

Instead of messaging another agent, create a task in the graph:

```bash
ont create --type Task --id task_research_api \
  --props '{"name":"Research API rate limits","status":"pending","assignee":"bob","priority":"high"}'

ont relate --from proj_current --rel has_task --to task_research_api
ont relate --from task_research_api --rel created_by --to agent_alice
```

The other agent will pick it up on their next session by querying for their tasks.

### When to Use Direct Messaging

Use `sessions_send` only when:
- Something is time-sensitive / urgent
- The task can't wait for a heartbeat cycle
- You need an immediate acknowledgment

Otherwise, use the graph.

## Conventions

### ID Naming

| Type | Pattern | Example |
|------|---------|---------|
| Project | `proj_<slug>` | `proj_website` |
| Task | `task_<slug>` | `task_setup-ci` |
| Learning | `learn_<slug>-<date>` | `learn_cors-preflight-20260506` |
| Skill | `skill_<slug>` | `skill_api-design` |
| Document | `doc_<slug>` | `doc_scaling-strategies` |
| Person | `p_<slug>` | `p_ada-lovelace` |
| Concept | `concept_<slug>` | `concept_cognitive-load` |
| Agent | `agent_<name>` | `agent_alice` |

### Dates in IDs

Use Unix timestamp or YYYYMMDD suffix for learnings and tasks to avoid collisions:
- `learn_telegram-token-1777957326`
- `learn_sdlc-inversion-20260506`

### Status Values

| Status | Meaning |
|--------|---------|
| `active` | Currently being worked on |
| `pending` | Waiting to start |
| `done` | Completed |
| `open` | Available for pickup |
| `complete` | Finished and verified |
| `published` | Available for public use |
| `archived` | No longer relevant |

### Properties Schema

Every entity should have at minimum:
```json
{
  "name": "Human-readable name",
  "status": "active|pending|done|...",
  "goal": "One-line description of purpose"
}
```

Optional fields:
- `"repo"` — GitHub URL for projects
- `"local_path"` — Local directory path
- `"assignee"` — Who owns this task
- `"priority"` — `low`, `medium`, `high`, `critical`
- `"due_date"` — ISO 8601 date

## Multi-Agent Specific Rules

1. **Always run dedup after bulk imports**
   ```bash
   python3 scripts/dedup_ontology.py
   ```

2. **Check for existing entities before creating**
   ```bash
   ont get --id proj_example
   # If not found, then create
   ```

3. **Use CWD detection in scripts**
   Scripts that check hardcoded paths may hit the wrong workspace for other agents. Use `SCRIPT_DIR` + `CWD` pattern matching to determine the active workspace dynamically:
   ```python
   import os
   CWD = os.getcwd()
   if '/workspace-bob' in CWD:
       WORKSPACE = os.path.expanduser("~/workspace-bob")
   else:
       WORKSPACE = os.path.expanduser("~/workspace-alice")
   ```

4. **Never call ontology.py directly without --graph**
   The script validates paths relative to its working directory. Always specify `--graph graph.jsonl` and run from `~/.openclaw/shared-ontology`.

5. **Link new learnings to concepts**
   Don't let learnings float in isolation. Relate them to relevant concepts so the graph stays connected.

## Safety

- **Private data stays private.** Don't add API keys, tokens, or personal info to the graph.
- **Sensitive projects:** Use `status: "private"` and don't push to public repos.
- **Human approval:** For any destructive action (deleting entities, bulk imports), confirm with the human first.

## Example Session Flow

```bash
# 1. Check what's new since last session
ont list --type Learning | tail -10

# 2. Pick up any assigned tasks
ont query --type Task --where '{"status":"pending","assignee":"you"}'

# 3. Do the work...

# 4. Document what you learned
ont create --type Learning --id learn_foo-bar \
  --props '{"name":"Foo beats Bar","status":"active","goal":"Use foo instead of bar for performance"}'
ont relate --from learn_foo-bar --rel relates_to --to concept_performance

# 5. Update task status
# (Requires updating entity — currently create-only, so delete + recreate or use new ID)

# 6. Commit the graph
# (Human does this, or you ask)
```

## Related

[[README]], [[orbit-view-design]], [[SOUL]], [[MEMORY]]
