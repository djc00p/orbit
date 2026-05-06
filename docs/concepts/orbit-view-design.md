# Orbit View — Radial Ontology Visualization

## Vision

A **centered radial knowledge system** instead of Obsidian's force-directed "hairball." Every view is anchored on one entity with concentric rings representing relationship distance.

## Core Design

| Ring | Meaning | Example (center = `proj_website`) |
| ---- | ------- | --------------------------------- |
| **Center** | The focused entity | proj_website |
| **Ring 1** | Direct relationships | `task_setup-ci`, `proj_website-api`, `p_alice` |
| **Ring 2** | Type siblings | Other Projects (mobile app, CLI tool, etc.) |
| **Ring 3** | Topic adjacency | `concept_learning-velocity`, `concept_api-design` |
| **Ring 4** | Loose connections | `p_bob` (wrote about topics relevant) |

## Interaction Model

- **Click any entity** → it becomes the new center, rings recalculate
- **Hover** → show relationship labels on the connecting arc
- **Filter** → show only certain types (Projects + Tasks only, hide MemoryChunks)
- **Time slider** → show graph as it existed at a point in time

## Rendering

- **Python SVG generator** (MVP) → `scripts/orbit_viz.py`
- **Web canvas** (later) → D3.js or custom canvas for smooth transitions
- **Export** → PNG/SVG, embed in reports, print as poster

## Color Palette

| Type | Color |
| ---- | ----- |
| Project | `#FF6B35` (warm orange — active, alive) |
| Task | `#4ECDC4` (teal — actionable) |
| Learning | `#45B7D1` (sky blue — wisdom) |
| Skill | `#96CEB4` (sage — craft) |
| Document | `#FFEAA7` (parchment — knowledge) |
| Person | `#DDA0DD` (orchid — human) |
| Concept | `#F7DC6F` (gold — idea) |
| Agent | `#BB8FCE` (purple — synthetic) |

## Implementation Phases

1. **MVP (now)** — Python script generates static SVG from `graph.jsonl`
2. **Interactive (later)** — Web viewer with click-to-recenter
3. **Time travel (future)** — Replay graph evolution over sessions

## Related

[[README]], [[orbit-readme]]
