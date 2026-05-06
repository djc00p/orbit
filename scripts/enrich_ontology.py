#!/usr/bin/env python3
"""Batch create ontology entries. Must run from shared-ontology dir."""
import json, subprocess, os, sys

os.chdir(os.path.expanduser("~/.openclaw/shared-ontology"))

SCRIPT = "/Users/DJC00P/.openclaw/workspace/skills/ontology/scripts/ontology.py"
GRAPH = "graph.jsonl"

def run(cmd_args):
    result = subprocess.run(["python3", SCRIPT] + cmd_args, capture_output=True, text=True)
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

# ============================================================================
# PROJECTS
# ============================================================================
for eid, props in [
    ("proj_mypridri", {"name":"mypridri","status":"active","goal":"Colorado rideshare app — Rails + Stripe, patron-to-driver matching with open ride board"}),
    ("proj_mypridri-mcp", {"name":"mypridri MCP Server","status":"active","goal":"Model Context Protocol server exposing mypridri JSON API to Claude Desktop"}),
    ("proj_walking-terminator", {"name":"Walking The Terminator","status":"active","goal":"YouTube doc series / podcast transcribed into book about life, existence, faith, power, truth"}),
    ("proj_kraken-trading", {"name":"Kraken Trading Agent","status":"pending","goal":"Dedicated trading/market agent on Linux machine via kraken-cli, paper trade first"}),
    ("proj_clawhub-maintenance", {"name":"ClawHub Skill Vetting","status":"active","goal":"Review, fix, and publish skills to ClawHub marketplace"}),
    ("proj_orbit-viz", {"name":"Orbit View Ontology Viz","status":"active","goal":"Build radial ontology visualization — concentric rings by relationship distance, not force-directed"}),
]:
    create("Project", eid, props)

# ============================================================================
# LEARNINGS
# ============================================================================
for eid, props in [
    ("learn_rails-db-prepare", {"name":"db:prepare pollutes test DB","status":"active","goal":"db:prepare runs seeds in CI → use db:schema:load instead for clean test DB"}),
    ("learn_turbo-v8-eval", {"name":"Turbo v8 script injection broken","status":"active","goal":"data-turbo-eval scripts via turbo_stream no longer execute in Turbo v8 — use Stimulus controller"}),
    ("learn_modal-turbo-frame", {"name":"Modal turbo-frame must exist in layout","status":"active","goal":"<turbo-frame id='modal'> must exist in layout for modal links to work on any page"}),
    ("learn_params-expect-rails8", {"name":"Rails 8 params.expect strips nested keys","status":"active","goal":"params.expect(model: [...]) strips nested '0' keys — use require/permit for complex nested forms"}),
    ("learn_rubocop-subagent-bugs", {"name":"RuboCop sub-agents introduce bugs","status":"active","goal":"Always verify behavior manually after refactor passes — automated scans may break logic"}),
    ("learn_token-hashing", {"name":"Never store raw API tokens","status":"active","goal":"SHA-256 hash tokens, return raw once, store digest only"}),
    ("learn_checkbox-hidden-field", {"name":"Boolean toggles need hidden_field_tag","status":"active","goal":"check_box_tag + hidden_field_tag needed for boolean toggles to send 0 when unchecked"}),
    ("learn_unprocessable-content", {"name":"Rails 8 unprocessable_entity deprecated","status":"active","goal":"Use :unprocessable_content in Rails 8.0.2+, not :unprocessable_entity"}),
    ("learn_skip-forgery", {"name":"skip_before_action verify_authenticity_token deprecated","status":"active","goal":"Use skip_forgery_protection, not skip_before_action :verify_authenticity_token"}),
    ("learn_before-validation", {"name":"before_create skipped by build in specs","status":"active","goal":"Use before_validation on: :create instead of before_create for specs that use build()"}),
    ("learn_human-approval-gate", {"name":"Human approval gate safety pattern","status":"active","goal":"Add explicit human approval before destructive actions (git push, live trading, external writes)"}),
    ("learn_concurrency-debug", {"name":"Concurrency investigation patterns","status":"active","goal":"Check gateway event loop delays, model auth failures, channel-level timeouts — not just maxConcurrent"}),
    ("learn_ollama-env-restart", {"name":".env changes need gateway restart","status":"active","goal":"OpenClaw gateway inherits env at startup only. Adding OLLAMA_API_KEY requires restart."}),
    ("learn_clawhub-vetting", {"name":"ClawHub vetting is noisy","status":"active","goal":"Automated scans flag legitimate capabilities — always manual-review before trusting classifications"}),
]:
    create("Learning", eid, props)

# ============================================================================
# SKILLS
# ============================================================================
for eid, props in [
    ("skill_rest-api-design", {"name":"rest-api-design","status":"published","goal":"Design RESTful APIs with proper versioning, authentication, and documentation"}),
    ("skill_rails-ci-fixer", {"name":"rails-ci-fixer","status":"published","goal":"Fix CI issues in Rails projects — RuboCop, test DB, asset precompilation"}),
    ("skill_freqtrade-tools", {"name":"freqtrade-tools","status":"published","goal":"Tools for freqtrade backtesting and strategy development"}),
    ("skill_claude-api-cost-optimizer", {"name":"claude-api-cost-optimizer","status":"published","goal":"Optimize Claude API usage costs through model selection and prompt engineering"}),
    ("skill_openclaw-docker-linux", {"name":"openclaw-docker-linux","status":"published","goal":"Deploy OpenClaw on Linux via Docker"}),
    ("skill_openclaw-dual-agent", {"name":"openclaw-dual-agent","status":"published","goal":"Configure and coordinate dual-agent setups (Kael + Ayo)"}),
]:
    create("Skill", eid, props)

# ============================================================================
# TASKS
# ============================================================================
for eid, props in [
    ("task_merge-pr69", {"name":"Merge PR #69 (admin dashboard)","status":"pending","goal":"Admin dashboard, payments, refund flow ready to merge into mypridri"}),
    ("task_mypridri-launch-prep", {"name":"mypridri launch preparation","status":"pending","goal":"Stripe version upgrade, 2FA for drivers, Google Reviews integration, customer support ticketing"}),
    ("task_mypridri-admin-complete", {"name":"Complete admin dashboard","status":"pending","goal":"Financial summary, dispute/refund flow for admin"}),
    ("task_mypridri-2fa", {"name":"2FA for driver accounts","status":"pending","goal":"Implement devise-two-factor for driver accounts, enforce for all drivers"}),
    ("task_mypridri-mobile-api", {"name":"Mobile app API","status":"pending","goal":"FCM push notifications, deep linking for mobile experience"}),
    ("task_mypridri-auto-quotes", {"name":"Agent-negotiated quotes","status":"pending","goal":"auto_accept_quote_within_percent preference for autonomous agent acceptance"}),
    ("task_kraken-telegram-bot", {"name":"Set up Telegram bot for Kraken agent","status":"pending","goal":"Deonte to create via BotFather, then wire up to Linux agent"}),
    ("task_kraken-linux-setup", {"name":"Install OpenClaw on Linux for Kraken","status":"pending","goal":"Fresh workspace, identity, kraken-cli setup on djc00p23@100.103.204.29"}),
    ("task_orbit-viz-mvp", {"name":"Build Orbit View MVP","status":"pending","goal":"Python SVG generator for radial ontology visualization"}),
    ("task_ontology-enrich", {"name":"Enrich shared ontology","status":"in_progress","goal":"Add all projects, learnings, skills, tasks, documents, and people to graph"}),
]:
    create("Task", eid, props)

# ============================================================================
# DOCUMENTS
# ============================================================================
for eid, props in [
    ("doc_gardening-alt-methods", {"name":"Alternative Gardening Methods","status":"complete","goal":"Hexagonal spacing, permaculture guilds, chaos gardening, forest gardening research"}),
    ("doc_season-extension", {"name":"Season Extension for Zone 5b","status":"complete","goal":"13 techniques for Colorado short season/high UV growing"}),
    ("doc_underground-greenhouse", {"name":"Underground Compost Greenhouse Colorado","status":"complete","goal":"Walipini + compost bioreactor design for year-round growing at 5,800ft"}),
    ("doc_behold-pale-horse", {"name":"Behold a Pale Horse Summaries","status":"complete","goal":"All 17 chapters + 7 appendices summarized, Ch1 and Ch12 highest signal"}),
    ("doc_orbit-viz-concept", {"name":"Orbit View Ontology Viz Concept","status":"active","goal":"Radial knowledge visualization with concentric rings — concept document"}),
]:
    create("Document", eid, props)

# ============================================================================
# PEOPLE
# ============================================================================
for eid, props in [
    ("p_ethan-ding", {"name":"Ethan Ding","role":"Writer/Analyst","goal":"Author of 'Claude Code Is Not Making Your Product Better'"}),
    ("p_eugene-yan", {"name":"Eugene Yan","role":"Engineer/Researcher","goal":"Author of 'How to Work and Compound with AI', ex-Amazon/Shopify"}),
    ("p_addy-osmani", {"name":"Addy Osmani","role":"Engineering Leader","goal":"Google Chrome, author of 'Cognitive Surrender' and comprehension debt research"}),
    ("p_ben-thompson", {"name":"Ben Thompson","role":"Analyst","goal":"Author of Stratechery, tech strategy analyst"}),
    ("p_william-cooper", {"name":"William Cooper","role":"Author","goal":"Author of 'Behold a Pale Horse' — conspiracy research, separating documents from testimony"}),
]:
    create("Person", eid, props)

# ============================================================================
# CONCEPTS
# ============================================================================
for eid, props in [
    ("concept_cognitive-surrender", {"name":"Cognitive Surrender","status":"active","goal":"AI output replaces independent judgment; 73% accept wrong answers when AI available"}),
    ("concept_comprehension-debt", {"name":"Comprehension Debt","status":"active","goal":"Gap between code volume and human understanding; mechanism is cognitive surrender"}),
    ("concept_token-economics", {"name":"Token Economics","status":"active","goal":"Inference demand compounding: users × tasks × tokens per task; Jevons paradox"}),
    ("concept_loop-intelligence", {"name":"Loop Intelligence","status":"active","goal":"Which AI-assisted loops produce learning vs. decay; organizational learning from agent work"}),
    ("concept_jits", {"name":"JITS (Just-In-Time Software)","status":"active","goal":"Natural language prompts generate working code on demand via agentic coding tools"}),
    ("concept_learning-velocity", {"name":"Learning Velocity","status":"active","goal":"Rate at which orgs learn from AI usage; next competitive advantage after access"}),
]:
    create("Concept", eid, props)

# ============================================================================
# RELATIONSHIPS
# ============================================================================
for from_id, rel, to_id in [
    ("proj_mypridri", "has_task", "task_merge-pr69"),
    ("proj_mypridri", "has_task", "task_mypridri-launch-prep"),
    ("proj_mypridri", "has_task", "task_mypridri-admin-complete"),
    ("proj_mypridri", "has_task", "task_mypridri-2fa"),
    ("proj_mypridri", "has_task", "task_mypridri-mobile-api"),
    ("proj_mypridri", "has_task", "task_mypridri-auto-quotes"),
    ("proj_mypridri", "has_task", "task_ontology-enrich"),
    ("proj_mypridri-mcp", "relates_to", "proj_mypridri"),
    ("proj_kraken-trading", "has_task", "task_kraken-telegram-bot"),
    ("proj_kraken-trading", "has_task", "task_kraken-linux-setup"),
    ("proj_orbit-viz", "has_task", "task_orbit-viz-mvp"),
    ("proj_clawhub-maintenance", "has_skill", "skill_rest-api-design"),
    ("proj_clawhub-maintenance", "has_skill", "skill_rails-ci-fixer"),
    ("proj_clawhub-maintenance", "has_skill", "skill_freqtrade-tools"),
    ("proj_clawhub-maintenance", "has_skill", "skill_claude-api-cost-optimizer"),
    ("proj_clawhub-maintenance", "has_skill", "skill_openclaw-docker-linux"),
    ("proj_clawhub-maintenance", "has_skill", "skill_openclaw-dual-agent"),
    ("proj_walking-terminator", "has_task", "task_ontology-enrich"),
    ("proj_gardening", "has_doc", "doc_gardening-alt-methods"),
    ("proj_gardening", "has_doc", "doc_season-extension"),
    ("proj_gardening", "has_doc", "doc_underground-greenhouse"),
    ("proj_behold-pale-horse", "has_doc", "doc_behold-pale-horse"),
    ("p_ethan-ding", "wrote_about", "concept_cognitive-surrender"),
    ("p_eugene-yan", "wrote_about", "concept_token-economics"),
    ("p_addy-osmani", "wrote_about", "concept_cognitive-surrender"),
    ("p_addy-osmani", "wrote_about", "concept_comprehension-debt"),
    ("p_ben-thompson", "wrote_about", "concept_token-economics"),
    ("p_william-cooper", "author_of", "doc_behold-pale-horse"),
    ("p_djc", "owns", "proj_mypridri"),
    ("p_djc", "owns", "proj_mypridri-mcp"),
    ("p_djc", "owns", "proj_gardening"),
    ("p_djc", "owns", "proj_behold-pale-horse"),
    ("p_djc", "owns", "proj_walking-terminator"),
    ("p_djc", "owns", "proj_kraken-trading"),
    ("p_djc", "owns", "proj_clawhub-maintenance"),
    ("p_djc", "owns", "proj_orbit-viz"),
]:
    relate(from_id, rel, to_id)

print("\n=== Ontology enrichment complete ===")
