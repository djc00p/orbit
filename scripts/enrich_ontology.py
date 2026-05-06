#!/usr/bin/env python3
"""Example: Batch enrich your Orbit ontology from structured data.

This is a template. Replace the data below with your own projects,
learnings, skills, tasks, documents, people, and concepts.
"""
import json, subprocess, os

# Configuration
ONT_DIR = os.path.expanduser("~/orbit")  # Or wherever you cloned the repo
GRAPH = os.path.join(ONT_DIR, "graph.jsonl")
SCRIPT = os.path.join(ONT_DIR, "scripts", "ontology.py")

def run(cmd_args):
    result = subprocess.run(
        ["python3", SCRIPT] + cmd_args,
        cwd=ONT_DIR, capture_output=True, text=True
    )
    out = (result.stdout.strip() or "(no output)").splitlines()[-1] if result.stdout.strip() else ""
    if result.returncode != 0:
        print(f"FAIL: {result.stderr.strip()}")
    else:
        print(f"OK: {out}")
    return result.returncode == 0

def create(etype, eid, props):
    run(["create", "--type", etype, "--id", eid, "--props", json.dumps(props), "--graph", GRAPH])

def relate(from_id, rel, to_id):
    run(["relate", "--from", from_id, "--rel", rel, "--to", to_id, "--graph", GRAPH])

# ═══════════════════════════════════════════════════════════════════
# REPLACE EVERYTHING BELOW WITH YOUR OWN DATA
# ═══════════════════════════════════════════════════════════════════

# Example projects
projects = [
    ("proj_website", {"name": "Personal Website", "status": "active", "goal": "Build a portfolio site with blog"}),
    ("proj_api", {"name": "REST API", "status": "pending", "goal": "Design and implement a JSON API"}),
]

# Example learnings
learnings = [
    ("learn_cors-20260506", {"name": "CORS preflight caching", "status": "active", "goal": "Preflight responses can be cached for 24h to reduce OPTIONS requests"}),
    ("learn_sql-index-20260506", {"name": "Partial indexes save space", "status": "active", "goal": "Index only WHERE active=true rows instead of entire table"}),
]

# Example skills
skills = [
    ("skill_python", {"name": "Python", "status": "active", "goal": "General-purpose scripting and automation"}),
    ("skill_docker", {"name": "Docker", "status": "active", "goal": "Containerize applications for consistent deployment"}),
]

# Example tasks
tasks = [
    ("task_setup-ci", {"name": "Setup CI pipeline", "status": "pending", "goal": "Configure GitHub Actions for test + deploy"}),
    ("task_write-docs", {"name": "Write API documentation", "status": "open", "goal": "Document all endpoints with OpenAPI spec"}),
]

# Example documents
docs = [
    ("doc_architecture", {"name": "System Architecture", "status": "complete", "goal": "High-level design decisions and tradeoffs"}),
]

# Example people
people = [
    ("p_you", {"name": "You", "role": "Developer", "goal": "Building useful things"}),
]

# Example concepts
concepts = [
    ("concept_cognitive-load", {"name": "Cognitive Load", "status": "active", "goal": "Mental effort required to process information"}),
]

# ═══════════════════════════════════════════════════════════════════
# CREATE ENTITIES
# ═══════════════════════════════════════════════════════════════════

print("Creating projects...")
for eid, props in projects:
    create("Project", eid, props)

print("\nCreating learnings...")
for eid, props in learnings:
    create("Learning", eid, props)

print("\nCreating skills...")
for eid, props in skills:
    create("Skill", eid, props)

print("\nCreating tasks...")
for eid, props in tasks:
    create("Task", eid, props)

print("\nCreating documents...")
for eid, props in docs:
    create("Document", eid, props)

print("\nCreating people...")
for eid, props in people:
    create("Person", eid, props)

print("\nCreating concepts...")
for eid, props in concepts:
    create("Concept", eid, props)

# ═══════════════════════════════════════════════════════════════════
# CREATE RELATIONSHIPS
# ═══════════════════════════════════════════════════════════════════

print("\nCreating relationships...")
for from_id, rel, to_id in [
    # Project has tasks
    ("proj_website", "has_task", "task_setup-ci"),
    ("proj_api", "has_task", "task_write-docs"),
    # Person owns projects
    ("p_you", "owns", "proj_website"),
    ("p_you", "owns", "proj_api"),
    # Learnings relate to concepts
    ("learn_cors-20260506", "relates_to", "concept_cognitive-load"),
    # Document belongs to project
    ("proj_api", "has_doc", "doc_architecture"),
]:
    relate(from_id, rel, to_id)

print("\n=== Done ===")
print("Run 'ont list' to see your new entities.")
print("Run 'python3 scripts/dedup_ontology.py' after bulk imports.")
