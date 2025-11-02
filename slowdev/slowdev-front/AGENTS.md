# Repository Guidelines

## Project Structure & Module Organization
- `streamlit_app.py` is the primary Streamlit entry point and should stay lightweight, delegating logic to modules under `pages/`.
- `pages/index.py` hosts the interactive pickpocket explorer; split new views into dedicated modules under `pages/` and reuse shared helpers.
- The app expects `pages/data/pickpocket_300.csv` (or similar) for seed data; keep raw assets versioned under `data/` and load processed copies from `pages/data/`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` creates an isolated environment for local work.
- `pip install -r requirements.txt` installs the Streamlit runtime; add any new dependencies here.
- `streamlit run streamlit_app.py` launches the default app shell, while `streamlit run pages/index.py` jumps straight to the pickpocket dashboard.
- Use `streamlit cache clear` after schema changes to avoid stale CSV data.

## Coding Style & Naming Conventions
- Write Python 3.10+ that follows PEP 8: four-space indents, snake_case for functions/variables, PascalCase for component classes.
- Keep Streamlit widgets named after the user-facing label to simplify state tracking (e.g., `selected_cities`).
- Guard secrets with `st.secrets` lookups and avoid hard-coding API keys in source files.

## Testing Guidelines
- No automated suite exists yet; when adding non-trivial logic, place unit tests in a new `tests/` package and run them with `pytest`.
- For UI updates, attach a screenshot or screen recording from a local `streamlit run` session and note the dataset sample used.
- Smoke-test filters (country, city, type) and map rendering before merging to confirm the CSV schema has not broken the UI.

## Commit & Pull Request Guidelines
- Follow the repository history convention of short, imperative commit messages (e.g., `add pickpocket data`, `fix page layout`).
- Reference related issues in the commit body or PR description, and document any dataset additions or schema adjustments.
- Pull requests must include: a concise summary, the manual test plan, updated dependency notes, and configuration steps for required secrets.

## Security & Configuration Tips
- Store `GEMINI_API_KEY` and other credentials in `.streamlit/secrets.toml`; share sample keys via `.streamlit/secrets.example.toml`.
- Review access controls when adding new external APIs, and sanitize any user-supplied text before reuse in prompts or logs.
