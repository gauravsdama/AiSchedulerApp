# AI Daily Planner

AI Daily Planner is a small Flask portfolio demo that turns free-form task notes into a daily schedule and saves recent results to a local SQLite database.

The app uses the OpenAI API when `OPENAI_API_KEY` is configured. If no key is available, it falls back to a deterministic local schedule so the app still runs for demos, testing, and screenshots.

## Features

- Today/tomorrow planning mode
- OpenAI-powered schedule generation with `OPENAI_MODEL` override support
- Local no-key fallback schedule
- SQLite history of the five most recent schedules
- Responsive single-page browser UI

## Run Locally

```bash
uv sync --python 3.12 --locked
uv run python schedulingApp.py
```

Open `http://127.0.0.1:3000`.

## Static GitHub Pages demo

`docs/demo/` contains a separate, dependency-free showcase that runs entirely
in the browser. It turns one-task-per-line notes into deterministic time blocks
and stores the latest plan in `localStorage`. Five sample task lists cover a
project deadline, class and gym, interview preparation, errands, and a quiet
weekend reset. It does **not** call OpenAI or claim to reproduce the Flask app's
optional model-generated schedule.

Preview it from the repository root:

```bash
python -m http.server 8080
```

Then open `http://127.0.0.1:8080/docs/`. The Pages root redirects to the demo,
which uses only relative assets and no client-side routes. It therefore works
under the `/AiSchedulerApp/` GitHub Pages base path and on direct reload.
Configure Pages to publish from the repository's `docs/` folder when it is
ready to go live.

The UI copy inventory and editorial workflow live in
[`docs/product/UI_COPY.md`](docs/product/UI_COPY.md).

Optional `.env`:

```bash
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
```

The Flask server binds to `127.0.0.1` and disables debug mode by default. Task
notes and generated schedules are stored in `instance/schedules.db`, which is
ignored by Git. The optional API path sends the submitted notes to OpenAI; the
static demo and no-key fallback make no network request.

## Project Files

```text
schedulingApp.py        Flask app, planner logic, and UI template
instance/schedules.db   Local SQLite schedule history
requirements.txt        Python dependencies
uv.lock                 Exact resolved dependency graph
```

## Verify

```bash
uv run pytest -q
uv run ruff check schedulingApp.py tests scripts/release_guard.py
uv run pip-audit
uv run python scripts/release_guard.py
uv build
uv run python scripts/verify_distribution.py
```

## Limitations

- The app runs Flask's development server and is intended for local use.
- Generated schedules are suggestions, not a dependable calendar or task-management system.
- There is no user authentication; anyone who can reach the local server can view its recent schedule history.
- The local fallback uses a fixed outline and does not infer times or durations from the notes.
- OpenAI requests require network access and may incur API usage charges.
