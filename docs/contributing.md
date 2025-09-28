# Contributing

Concise guide to get a change from idea to merged.

## 1. Setup

Prerequisites:

- Python 3.9+
- uv (see: https://docs.astral.sh/uv/getting-started/installation/)

```bash
git clone https://github.com/yourusername/notionary.git
cd notionary
uv sync --all-extras
uv run pre-commit install
uv run pytest  # sanity check
```

## 2. Workflow

```bash
git checkout -b feature/short-description

# implement
uv run pytest                # tests
uv run ruff check .          # lint
uv run ruff format .         # format (or let pre-commit do it)
uv run mypy notionary        # types

git add .
git commit -m "feat: short description"
git push origin feature/short-description
```

Open a Pull Request (PR) when the change is isolated and passes local checks.

## 3. Local Checks

| Tool       | Purpose                                |
| ---------- | -------------------------------------- |
| Ruff       | Lint + format                          |
| Pytest     | Tests                                  |
| MyPy       | Type safety                            |
| pre-commit | Runs the above fast before each commit |

You normally only run pytest explicitly; the rest is enforced automatically.

## 4. Contribution Areas

- Bug fixes
- Small quality improvements (naming, clarity, docs)
- Documentation & examples
- Additional tests (round‑trip, regression, fixtures)
- Features you would like to see in Notionary

## 5. Style & Scope

- Keep PRs small and focused; large refactors → split.
- Avoid drive‑by formatting unrelated to the change.
- Public API changes must be documented and mentioned in the PR description.
- Prefer incremental improvement over speculative abstraction.
