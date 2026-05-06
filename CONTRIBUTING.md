# Contributing to Orbit

Thanks for your interest in Orbit! This is a lightweight knowledge graph for AI agents and humans. Contributions are welcome — whether it's code, documentation, bug reports, or ideas.

## How to Contribute

### 1. Report a Bug or Request a Feature

- Check existing [issues](https://github.com/djc00p/orbit/issues) first
- Open a new issue using our templates
- Provide clear reproduction steps for bugs
- Explain the use case for feature requests

### 2. Submit Code Changes

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/orbit.git
   cd orbit
   ```
3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```
4. **Make your changes** — keep commits focused and descriptive
5. **Test your changes**:
   - Run `python3 scripts/ontology.py validate --graph graph.jsonl`
   - Test any new scripts with sample data
6. **Push** and open a **Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### 3. Improve Documentation

- Fix typos, clarify explanations, add examples
- Docs live in `README.md`, `AGENTS.md`, and `docs/`
- No code needed — PRs welcome for doc-only changes

## Development Setup

```bash
git clone https://github.com/djc00p/orbit.git
cd orbit

# Test the CLI
python3 scripts/ontology.py list --graph graph.jsonl

# Run dedup script
python3 scripts/dedup_ontology.py
```

No dependencies to install — it's just Python 3.8+ and JSONL.

## Code Style

- **Python:** PEP 8, 4-space indentation
- **Docstrings:** Google style or plain description
- **Error handling:** Graceful fallbacks, never corrupt graph.jsonl
- **Graph safety:** All scripts should validate paths before writing

## Commit Message Style

Use present tense, imperative mood:

```
Add batch import script for CSV data
Fix dedup script to preserve relation order
Update README with Docker examples
```

## Areas That Need Help

- [ ] Radial SVG visualizer (`scripts/orbit_viz.py`)
- [ ] Interactive web viewer
- [ ] Python package (`pip install orbit`)
- [ ] More example enrichment scripts (CSV, Notion, Obsidian imports)
- [ ] Time-travel graph replay
- [ ] Better fuzzy matching in `link_session_to_ontology.py`
- [ ] TypeScript/JavaScript client library
- [ ] Documentation translations

## Questions?

Open an issue with the `question` label or reach out in discussions.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
