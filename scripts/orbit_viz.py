#!/usr/bin/env python3
"""
Orbit View — Radial SVG generator for ontology graphs.

Usage:
    python3 scripts/orbit_viz.py --center proj_website --output orbit.svg
    python3 scripts/orbit_viz.py --center concept_cognitive-load --output concept.svg
    python3 scripts/orbit_viz.py --center p_alice --output person.svg --show-memory
"""

import argparse
import json
import math
import os
from pathlib import Path
from datetime import datetime

# Color palette from orbit-view-design.md
COLORS = {
    "Project": "#FF6B35",
    "Task": "#4ECDC4",
    "Learning": "#45B7D1",
    "Skill": "#96CEB4",
    "Document": "#FFEAA7",
    "Person": "#DDA0DD",
    "Concept": "#F7DC6F",
    "Agent": "#BB8FCE",
    "MemoryChunk": "#B8B8B8",
}

# Ring configuration: radius, label, max nodes, node radius
RING_CONFIG = [
    {"radius": 0, "label": "Center", "max_nodes": 1, "node_radius": 36},
    {"radius": 140, "label": "Direct", "max_nodes": 10, "node_radius": 26},
    {"radius": 260, "label": "Siblings", "max_nodes": 16, "node_radius": 20},
    {"radius": 380, "label": "Adjacency", "max_nodes": 22, "node_radius": 16},
    {"radius": 480, "label": "Loose", "max_nodes": 28, "node_radius": 12},
]

FONT_SIZE = 11
CENTER_X = 500
CENTER_Y = 500
SVG_SIZE = 1000

# Default output directory
DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "Orbit-Viz"


def load_graph(graph_path: Path, show_memory: bool = False):
    """Load entities and relations from graph.jsonl."""
    entities = {}
    relations = []

    if not graph_path.exists():
        return entities, relations

    with open(graph_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                op = json.loads(line)
                if op.get("op") == "create" and "entity" in op:
                    e = op["entity"]
                    if not show_memory and e.get("type") == "MemoryChunk":
                        continue
                    entities[e["id"]] = e
                elif op.get("op") == "relate":
                    relations.append(op)
            except json.JSONDecodeError:
                continue

    return entities, relations


def get_related_ids(entity_id: str, relations: list):
    """Get all IDs directly related to an entity."""
    related = set()
    for rel in relations:
        if rel.get("from") == entity_id:
            related.add(rel.get("to"))
        elif rel.get("to") == entity_id:
            related.add(rel.get("from"))
    return related


def get_ring_entities(center_id: str, entities: dict, relations: list):
    """
    Assign entities to rings based on relationship distance from center.
    Caps each ring to max_nodes. Remaining entities are dropped.
    """
    center = entities.get(center_id)
    if not center:
        return {}

    center_type = center.get("type", "Unknown")
    assigned = {center_id: 0}
    ring_counts = {i: 0 for i in range(len(RING_CONFIG))}
    ring_counts[0] = 1

    def try_assign(eid: str, ring: int) -> bool:
        if eid in assigned or ring >= len(RING_CONFIG):
            return False
        config = RING_CONFIG[ring]
        if ring_counts[ring] >= config["max_nodes"]:
            return False
        assigned[eid] = ring
        ring_counts[ring] += 1
        return True

    # Ring 1: Direct relationships
    direct = get_related_ids(center_id, relations)
    for eid in direct:
        if eid in entities:
            try_assign(eid, 1)

    # Ring 2: Same type as center (siblings)
    for eid, e in entities.items():
        if eid == center_id:
            continue
        if e.get("type") == center_type:
            if eid not in assigned:
                try_assign(eid, 2)

    # Ring 3: Related to ring 1 or 2 entities
    ring_1_2 = {eid for eid, ring in assigned.items() if ring in (1, 2)}
    for source_id in ring_1_2:
        for related_id in get_related_ids(source_id, relations):
            if related_id in entities and related_id not in assigned:
                try_assign(related_id, 3)

    # Ring 4: Everything else connected in the graph
    for eid in entities:
        if eid not in assigned:
            try_assign(eid, 4)

    return assigned


def calculate_positions(center_id: str, ring_assignments: dict, entities: dict):
    """Calculate (x, y) positions for each entity in their ring."""
    positions = {}

    # Group by ring
    ring_groups = {i: [] for i in range(len(RING_CONFIG))}
    for eid, ring in ring_assignments.items():
        if ring < len(RING_CONFIG):
            ring_groups[ring].append(eid)

    # Position center
    positions[center_id] = (CENTER_X, CENTER_Y)

    # Position ring entities
    for ring_idx, config in enumerate(RING_CONFIG):
        if ring_idx == 0:
            continue

        ring_entities = ring_groups.get(ring_idx, [])
        if not ring_entities:
            continue

        radius = config["radius"]
        count = len(ring_entities)

        # Distribute evenly around the circle
        for i, eid in enumerate(ring_entities):
            angle = (2 * math.pi * i) / count - math.pi / 2  # Start at top
            x = CENTER_X + radius * math.cos(angle)
            y = CENTER_Y + radius * math.sin(angle)
            positions[eid] = (x, y)

    return positions


def truncate_name(name: str, max_len: int = 14) -> str:
    """Truncate long names for display."""
    if len(name) <= max_len:
        return name
    return name[:max_len - 1] + "…"


def generate_svg(center_id: str, entities: dict, relations: list, ring_assignments: dict, positions: dict):
    """Generate SVG XML."""
    center = entities.get(center_id, {})
    center_name = center.get("properties", {}).get("name", center_id)
    center_type = center.get("type", "Unknown")

    lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_SIZE}" height="{SVG_SIZE}" viewBox="0 0 {SVG_SIZE} {SVG_SIZE}">',
        f'  <rect width="{SVG_SIZE}" height="{SVG_SIZE}" fill="#1a1a2e"/>',
        f'  <text x="20" y="30" fill="#e0e0e0" font-family="system-ui, sans-serif" font-size="16" font-weight="bold">Orbit View</text>',
        f'  <text x="20" y="50" fill="#a0a0a0" font-family="system-ui, sans-serif" font-size="11">Center: {truncate_name(center_name)} ({center_type})</text>',
    ]

    # Draw ring circles (subtle)
    for ring_idx, config in enumerate(RING_CONFIG):
        if ring_idx == 0:
            continue
        radius = config["radius"]
        lines.append(
            f'  <circle cx="{CENTER_X}" cy="{CENTER_Y}" r="{radius}" '
            f'fill="none" stroke="#2a2a4e" stroke-width="1" stroke-dasharray="4,4"/>'
        )

    # Draw relationships as lines — only if both ends are in positions
    # Limit to avoid hairball: only show relations where one end is center or ring 1
    drawn_relations = set()
    for rel in relations:
        from_id = rel.get("from")
        to_id = rel.get("to")
        if from_id not in positions or to_id not in positions:
            continue

        # Skip duplicate lines
        key = tuple(sorted([from_id, to_id]))
        if key in drawn_relations:
            continue
        drawn_relations.add(key)

        # Only draw lines that connect to center or ring 1 entities
        # This avoids the hairball of ring 3-4 cross-connections
        ring_from = ring_assignments.get(from_id, 5)
        ring_to = ring_assignments.get(to_id, 5)
        if ring_from > 1 and ring_to > 1:
            continue

        x1, y1 = positions[from_id]
        x2, y2 = positions[to_id]
        lines.append(
            f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#3a3a5e" stroke-width="0.5" opacity="0.4"/>'
        )

    # Draw nodes
    for eid, (x, y) in positions.items():
        entity = entities.get(eid, {})
        e_type = entity.get("type", "Unknown")
        name = entity.get("properties", {}).get("name", eid)
        color = COLORS.get(e_type, "#888888")

        ring = ring_assignments.get(eid, 4)
        config = RING_CONFIG[min(ring, len(RING_CONFIG) - 1)]
        radius = config["node_radius"]

        # Highlight center
        stroke_width = 3 if eid == center_id else 1.5
        stroke_color = "#ffffff" if eid == center_id else "#2a2a4e"
        radius = radius * 1.3 if eid == center_id else radius

        lines.append(
            f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" '
            f'fill="{color}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        )

        # Label — skip for very small outer nodes if crowded
        if ring <= 3:
            display_name = truncate_name(name)
            lines.append(
                f'  <text x="{x:.1f}" y="{y + radius + 14:.1f}" '
                f'text-anchor="middle" fill="#e0e0e0" '
                f'font-family="system-ui, sans-serif" font-size="{FONT_SIZE}">{display_name}</text>'
            )

            # Type badge (small, below name)
            lines.append(
                f'  <text x="{x:.1f}" y="{y + radius + 26:.1f}" '
                f'text-anchor="middle" fill="#a0a0a0" '
                f'font-family="system-ui, sans-serif" font-size="9">{e_type}</text>'
            )

    # Legend
    legend_y = SVG_SIZE - 20
    lines.append(f'  <text x="{SVG_SIZE - 20}" y="{legend_y}" text-anchor="end" fill="#a0a0a0" font-family="system-ui, sans-serif" font-size="10">Generated by Orbit View — {len(positions)} entities shown</text>')

    lines.append('</svg>')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate radial SVG visualization of Orbit ontology")
    parser.add_argument("--center", required=True, help="Entity ID to center the visualization on")
    parser.add_argument("--graph", type=Path, default=Path("graph.jsonl"), help="Path to graph.jsonl")
    parser.add_argument("--output", type=Path, help="Output SVG file path (default: ~/Documents/Orbit-Viz/<entity>_orbit.svg)")
    parser.add_argument("--size", type=int, default=SVG_SIZE, help="SVG canvas size in pixels")
    parser.add_argument("--show-memory", action="store_true", help="Include MemoryChunk entities in visualization")
    args = parser.parse_args()

    # Resolve graph path
    graph_path = args.graph
    if not graph_path.is_absolute():
        graph_path = Path.cwd() / graph_path

    print(f"Loading graph from {graph_path}...")
    entities, relations = load_graph(graph_path, args.show_memory)
    print(f"Loaded {len(entities)} entities, {len(relations)} relations")

    if args.center not in entities:
        print(f"Error: Center entity '{args.center}' not found in graph")
        print(f"Available entities: {', '.join(list(entities.keys())[:10])}...")
        return 1

    print(f"Centering on: {args.center}")
    ring_assignments = get_ring_entities(args.center, entities, relations)
    positions = calculate_positions(args.center, ring_assignments, entities)

    # Count per ring
    ring_counts = {}
    for eid, ring in ring_assignments.items():
        ring_counts[ring] = ring_counts.get(ring, 0) + 1
    total_visible = sum(ring_counts.values())
    dropped = len(entities) - total_visible
    print("Ring distribution:")
    for i, config in enumerate(RING_CONFIG):
        count = ring_counts.get(i, 0)
        cap = config["max_nodes"]
        if count > 0:
            status = f" (capped at {cap})" if count == cap and i > 0 else ""
            print(f"  Ring {i} ({config['label']}): {count}/{cap} entities{status}")
    if dropped > 0:
        print(f"  Dropped: {dropped} entities (exceeded ring capacity)")

    svg = generate_svg(args.center, entities, relations, ring_assignments, positions)

    # Resolve output path
    output_path = args.output
    if output_path:
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
    else:
        # Default to ~/Documents/Orbit-Viz/
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = args.center.replace("_", "-")
        output_path = DEFAULT_OUTPUT_DIR / f"{safe_name}_orbit.svg"

    with open(output_path, "w") as f:
        f.write(svg)

    print(f"\nSVG written to {output_path}")
    print(f"Open in browser: file://{output_path.absolute()}")
    return 0


if __name__ == "__main__":
    exit(main())
