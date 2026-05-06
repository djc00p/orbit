#!/usr/bin/env python3
"""
Orbit View — Radial SVG generator for ontology graphs.

Usage:
    python3 scripts/orbit_viz.py --center proj_website
    python3 scripts/orbit_viz.py --center concept_cognitive-load --output concept.svg
    python3 scripts/orbit_viz.py --center p_alice --show-memory
"""

import argparse
import json
import math
from pathlib import Path
from datetime import datetime

COLORS = {
    "Project": "#FF6B35", "Task": "#4ECDC4", "Learning": "#45B7D1",
    "Skill": "#96CEB4", "Document": "#FFEAA7", "Person": "#DDA0DD",
    "Concept": "#F7DC6F", "Agent": "#BB8FCE", "MemoryChunk": "#B8B8B8",
}

RING_CONFIG = [
    {"radius": 0, "label": "Center", "max_nodes": 1, "base_radius": 36},
    {"radius": 140, "label": "Direct", "max_nodes": 10, "base_radius": 28},
    {"radius": 260, "label": "Siblings", "max_nodes": 16, "base_radius": 22},
    {"radius": 380, "label": "Adjacency", "max_nodes": 22, "base_radius": 16},
    {"radius": 480, "label": "Loose", "max_nodes": 28, "base_radius": 10},
]

STAR_THRESHOLD = 8
PLANET_THRESHOLD = 4
FONT_SIZE = 11
SMALL_FONT = 9
CENTER_X = 500
CENTER_Y = 500
SVG_SIZE = 1000
DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "Orbit-Viz"


def load_graph(graph_path, show_memory=False):
    entities, relations = {}, []
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
                pass
    return entities, relations


def get_related_ids(entity_id, relations):
    related = set()
    for rel in relations:
        if rel.get("from") == entity_id:
            related.add(rel.get("to"))
        elif rel.get("to") == entity_id:
            related.add(rel.get("from"))
    return related


def calc_degrees(entities, relations):
    degrees = {eid: 0 for eid in entities}
    for rel in relations:
        f, t = rel.get("from"), rel.get("to")
        if f in degrees:
            degrees[f] += 1
        if t in degrees:
            degrees[t] += 1
    return degrees


def get_ring_entities(center_id, entities, relations):
    center = entities.get(center_id)
    if not center:
        return {}
    center_type = center.get("type", "Unknown")
    assigned = {center_id: 0}
    ring_counts = {i: 0 for i in range(len(RING_CONFIG))}
    ring_counts[0] = 1

    def try_assign(eid, ring):
        if eid in assigned or ring >= len(RING_CONFIG):
            return False
        cap = RING_CONFIG[ring]["max_nodes"]
        if ring_counts[ring] >= cap:
            return False
        assigned[eid] = ring
        ring_counts[ring] += 1
        return True

    for eid in get_related_ids(center_id, relations):
        if eid in entities:
            try_assign(eid, 1)
    for eid, e in entities.items():
        if eid != center_id and e.get("type") == center_type and eid not in assigned:
            try_assign(eid, 2)
    ring_1_2 = {eid for eid, r in assigned.items() if r in (1, 2)}
    for src in ring_1_2:
        for rid in get_related_ids(src, relations):
            if rid in entities and rid not in assigned:
                try_assign(rid, 3)
    for eid in entities:
        if eid not in assigned:
            try_assign(eid, 4)
    return assigned


def calculate_positions(center_id, ring_assignments):
    positions = {center_id: (CENTER_X, CENTER_Y)}
    ring_groups = {i: [] for i in range(len(RING_CONFIG))}
    for eid, ring in ring_assignments.items():
        if ring < len(RING_CONFIG):
            ring_groups[ring].append(eid)
    for ring_idx, config in enumerate(RING_CONFIG):
        if ring_idx == 0:
            continue
        ents = ring_groups.get(ring_idx, [])
        if not ents:
            continue
        radius = config["radius"]
        count = len(ents)
        for i, eid in enumerate(ents):
            angle = (2 * math.pi * i) / count - math.pi / 2
            x = CENTER_X + radius * math.cos(angle)
            y = CENTER_Y + radius * math.sin(angle)
            positions[eid] = (x, y)
    return positions


def truncate_name(name, max_len=14):
    if len(name) <= max_len:
        return name
    return name[:max_len - 1] + "…"


def generate_svg(center_id, entities, relations, ring_assignments, positions, degrees):
    center = entities.get(center_id, {})
    center_name = center.get("properties", {}).get("name", center_id)
    center_type = center.get("type", "Unknown")
    center_degree = degrees.get(center_id, 0)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_SIZE}" height="{SVG_SIZE}" viewBox="0 0 {SVG_SIZE} {SVG_SIZE}">',
        f'  <rect width="{SVG_SIZE}" height="{SVG_SIZE}" fill="#0d0d1a"/>',
        f'  <text x="20" y="30" fill="#e0e0e0" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="bold">Orbit View</text>',
        f'  <text x="20" y="52" fill="#a0a0a0" font-family="system-ui, -apple-system, sans-serif" font-size="12">Center: {truncate_name(center_name)} ({center_type}) — {center_degree} connections</text>',
    ]

    for ring_idx, config in enumerate(RING_CONFIG):
        if ring_idx == 0:
            continue
        radius = config["radius"]
        label = config["label"]
        lines.append(f'  <circle cx="{CENTER_X}" cy="{CENTER_Y}" r="{radius}" fill="none" stroke="#1a1a3a" stroke-width="1" stroke-dasharray="3,6"/>')
        lines.append(f'  <text x="{CENTER_X}" y="{CENTER_Y - radius - 8}" text-anchor="middle" fill="#4a4a6a" font-family="system-ui, sans-serif" font-size="10" font-style="italic">{label}</text>')

    drawn = set()
    for rel in relations:
        f, t = rel.get("from"), rel.get("to")
        if f not in positions or t not in positions:
            continue
        key = tuple(sorted([f, t]))
        if key in drawn:
            continue
        drawn.add(key)
        rf = ring_assignments.get(f, 5)
        rt = ring_assignments.get(t, 5)
        if rf > 1 and rt > 1:
            continue
        x1, y1 = positions[f]
        x2, y2 = positions[t]
        lines.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#2a2a5a" stroke-width="0.8" opacity="0.35"/>')

    for eid, (x, y) in positions.items():
        entity = entities.get(eid, {})
        e_type = entity.get("type", "Unknown")
        name = entity.get("properties", {}).get("name", eid)
        color = COLORS.get(e_type, "#888888")
        ring = ring_assignments.get(eid, 4)
        degree = degrees.get(eid, 0)
        base = RING_CONFIG[min(ring, len(RING_CONFIG) - 1)]["base_radius"]
        if degree >= STAR_THRESHOLD:
            radius = base * 1.4
            glow = True
        elif degree >= PLANET_THRESHOLD:
            radius = base * 1.15
            glow = False
        else:
            radius = base
            glow = False
        if eid == center_id:
            radius = base * 1.5
            glow = True

        if glow:
            lines.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{radius + 6}" fill="{color}" opacity="0.15"/>')
        stroke_w = 3 if eid == center_id else 2 if degree >= STAR_THRESHOLD else 1.5
        stroke_c = "#ffffff" if eid == center_id else "#ffd700" if degree >= STAR_THRESHOLD else "#2a2a4e"
        lines.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{color}" stroke="{stroke_c}" stroke-width="{stroke_w}"/>')

        if degree >= 2:
            badge_r = 8 if ring <= 2 else 6
            badge_x = x + radius * 0.7
            badge_y = y - radius * 0.7
            lines.append(f'  <circle cx="{badge_x:.1f}" cy="{badge_y:.1f}" r="{badge_r}" fill="#1a1a3a" stroke="#a0a0a0" stroke-width="0.5"/>')
            lines.append(f'  <text x="{badge_x:.1f}" y="{badge_y + 2.5:.1f}" text-anchor="middle" fill="#e0e0e0" font-family="system-ui, sans-serif" font-size="{7 if ring <= 2 else 6}">{degree}</text>')

        if ring <= 3:
            display = truncate_name(name)
            lines.append(f'  <text x="{x:.1f}" y="{y + radius + 13:.1f}" text-anchor="middle" fill="#e0e0e0" font-family="system-ui, sans-serif" font-size="{FONT_SIZE}">{display}</text>')
            if degree >= STAR_THRESHOLD:
                cls, cls_color = "★ Star", "#ffd700"
            elif degree >= PLANET_THRESHOLD:
                cls, cls_color = "● Planet", "#a0c0e0"
            else:
                cls, cls_color = "◆ Comet", "#a0a0a0"
            lines.append(f'  <text x="{x:.1f}" y="{y + radius + 25:.1f}" text-anchor="middle" fill="{cls_color}" font-family="system-ui, sans-serif" font-size="{SMALL_FONT}">{cls} ({degree})</text>')

    # Legend panel
    lx, ly = 20, SVG_SIZE - 110
    lines.append(f'  <rect x="{lx}" y="{ly}" width="160" height="90" fill="#0d0d1a" stroke="#2a2a4e" stroke-width="1" rx="4"/>')
    lines.append(f'  <text x="{lx + 10}" y="{ly + 18}" fill="#e0e0e0" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">Legend</text>')
    for i, (sym, col, desc) in enumerate([("★ Star", "#ffd700", "8+ connections"), ("● Planet", "#a0c0e0", "4-7 connections"), ("◆ Comet", "#a0a0a0", "1-3 connections")]):
        lines.append(f'  <text x="{lx + 10}" y="{ly + 35 + i * 18}" fill="{col}" font-family="system-ui, sans-serif" font-size="10">{sym} {desc}</text>')

    # Type legend
    tx, ty = SVG_SIZE - 140, SVG_SIZE - 110
    lines.append(f'  <rect x="{tx}" y="{ty}" width="120" height="90" fill="#0d0d1a" stroke="#2a2a4e" stroke-width="1" rx="4"/>')
    lines.append(f'  <text x="{tx + 10}" y="{ty + 18}" fill="#e0e0e0" font-family="system-ui, sans-serif" font-size="12" font-weight="bold">Types</text>')
    type_items = [("Project", "#FF6B35"), ("Task", "#4ECDC4"), ("Learning", "#45B7D1"), ("Skill", "#96CEB4"), ("Document", "#FFEAA7"), ("Person", "#DDA0DD"), ("Concept", "#F7DC6F")]
    for i, (tname, tcolor) in enumerate(type_items):
        lines.append(f'  <circle cx="{tx + 16}" cy="{ty + 35 + i * 12 - 3}" r="5" fill="{tcolor}"/>')
        lines.append(f'  <text x="{tx + 28}" y="{ty + 35 + i * 12}" fill="#a0a0a0" font-family="system-ui, sans-serif" font-size="9">{tname}</text>')

    total = len(positions)
    lines.append(f'  <text x="{CENTER_X}" y="{SVG_SIZE - 8}" text-anchor="middle" fill="#4a4a6a" font-family="system-ui, sans-serif" font-size="10">Orbit View — {total} entities shown — {len(entities) - total} filtered — generated {datetime.now().strftime("%Y-%m-%d %H:%M")}</text>')
    lines.append('</svg>')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate radial SVG visualization of Orbit ontology")
    parser.add_argument("--center", required=True, help="Entity ID to center on")
    parser.add_argument("--graph", type=Path, default=Path("graph.jsonl"), help="Path to graph.jsonl")
    parser.add_argument("--output", type=Path, help="Output SVG path")
    parser.add_argument("--show-memory", action="store_true", help="Include MemoryChunk entities")
    args = parser.parse_args()

    graph_path = args.graph if args.graph.is_absolute() else Path.cwd() / args.graph
    print(f"Loading graph from {graph_path}...")
    entities, relations = load_graph(graph_path, args.show_memory)
    print(f"Loaded {len(entities)} entities, {len(relations)} relations")

    if args.center not in entities:
        print(f"Error: Center entity '{args.center}' not found")
        print(f"Available: {', '.join(list(entities.keys())[:10])}...")
        return 1

    degrees = calc_degrees(entities, relations)
    ring_assignments = get_ring_entities(args.center, entities, relations)
    positions = calculate_positions(args.center, ring_assignments)

    ring_counts = {}
    for eid, ring in ring_assignments.items():
        ring_counts[ring] = ring_counts.get(ring, 0) + 1
    total_visible = sum(ring_counts.values())
    dropped = len(entities) - total_visible
    print("\nRing distribution:")
    for i, config in enumerate(RING_CONFIG):
        count = ring_counts.get(i, 0)
        cap = config["max_nodes"]
        if count > 0:
            print(f"  Ring {i} ({config['label']}): {count}/{cap}{' (capped)' if count == cap and i > 0 else ''}")
    if dropped > 0:
        print(f"  Dropped: {dropped} entities")

    svg = generate_svg(args.center, entities, relations, ring_assignments, positions, degrees)

    output_path = args.output
    if output_path:
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
    else:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        safe = args.center.replace("_", "-")
        output_path = DEFAULT_OUTPUT_DIR / f"{safe}_orbit.svg"

    with open(output_path, "w") as f:
        f.write(svg)
    print(f"\nSVG: {output_path}")
    print(f"Open: file://{output_path.absolute()}")
    return 0


if __name__ == "__main__":
    exit(main())
