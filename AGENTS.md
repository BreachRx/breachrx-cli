# BreachRx CLI

Python command line tool for the BreachRx incident response management platform's GraphQL API, 
shipped to customers as a single `breachrx-cli.pyz` zipapp. See `README.md` for usage and build 
steps.

## Layout

- `breachrx-cli/__main__.py` — the click commands.
- `breachrx-cli/client.py` — settings from env/`.env`, the GraphQL transport (`execute_query`)
  and helpers for building API variables (`build_variables`, `parse_attributes`).
- `breachrx-cli/__init__.py` — `__version__`, imported as a top-level module 
(`from __init__ import ...`) because the directory name is not importable. Bump it with 
`pyproject.toml`.

## Conventions

- Python 3.9+, 2-space indentation, matching the existing code.
- Keep dependencies pure Python (currently only `click` and `python-dotenv`) so one `.pyz`
  runs on every platform. Do not add packages with compiled extensions (e.g. aiohttp); use
  `urllib` for HTTP.
- Only send variables the user set (`build_variables`) so the API applies its own defaults.
- Report failures with `click.ClickException` / `click.BadParameter` so commands exit non-zero
  with a clean message; never print credentials.
- Keep `README.md` command help in sync with `--help` output when options change.

## Development

This is a standalone Poetry project.

```bash
poetry install
```

After changing dependencies, run `poetry lock` and re-export `requirements.txt`
(`poetry export -f requirements.txt --output requirements.txt --without-hashes`), then check the
zipapp build from `README.md` in a scratch directory rather than in the repository.

Checks against a real org need `BREACHRX_API_KEY`,
`BREACHRX_SECRET_KEY`, `BREACHRX_ORG_NAME` and optionally `BREACHRX_GRAPHQL_URL`; use ping command
to validate working connectivity.
