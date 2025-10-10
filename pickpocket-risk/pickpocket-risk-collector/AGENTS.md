# Repository Guidelines

## Project Structure & Module Organization
- `mcp_server/server.py`: fastMCP server exposing the `collect_pickpocket_reports` tool and writing daily JSONL snapshots into `data/`.
- `agent/run_collector.py`: CLI client that connects to a local or remote FastMCP transport and triggers data collection.
- `requirements.txt`: Python dependencies (`fastmcp`, `httpx`). Run inside a `python3 -m venv .venv` environment.
- `data/`: Output directory ignored by Git; each file is named `YYYY-MM-DD.jsonl`.

## Build, Test, and Development Commands
- `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` — bootstrap the environment.
- `fastmcp run mcp_server/server.py:app` — start the server via stdio transport (suitable for local development).
- `fastmcp run --transport http mcp_server/server.py:app` — expose the server over HTTP at `http://127.0.0.1:8000/mcp` for remote agents.
- `python -m agent.run_collector --query "Seoul pickpocket"` — invoke the agent against the default server; add `--server http://host:8000/mcp` for remote targets.

## Coding Style & Naming Conventions
- Python 3.10+ with four-space indentation and trailing commas on multiline literals.
- Use snake_case for functions, variables, and filenames; use UpperCamelCase only for classes.
- Keep functions small; add docstrings or inline comments when logic is non-trivial.
- Run `python -m compileall agent mcp_server` before committing to catch syntax errors quickly.

## Testing Guidelines
- No automated test suite yet; validate changes by running the server and agent commands above.
- When adding automated tests, place them under `tests/` (create if needed) and name files `test_<module>.py`.
- Ensure new data fields appear in the JSONL output and handle network failures gracefully.

## Commit & Pull Request Guidelines
- Prefer imperative, concise commit messages (e.g., `Add HTTP transport normalization`).
- Reference related issues in commit bodies or PR descriptions when applicable.
- Pull requests should include: summary of changes, manual test evidence (command output or data snippet), and any follow-up tasks.
- Keep diffs focused; open separate PRs for unrelated features or refactors.
