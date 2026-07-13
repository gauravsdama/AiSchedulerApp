# AI Daily Planner

Flask app that turns free-form task notes into a structured daily schedule and saves generated plans to a local SQLite database.

The app uses the OpenAI API when `OPENAI_API_KEY` is configured. If no key is available, it falls back to a deterministic local schedule so the app still runs for demos, testing, and screenshots.

## Features

- Today/tomorrow planning mode
- OpenAI-powered schedule generation with `OPENAI_MODEL` override support
- Local no-key fallback schedule
- SQLite history of recent schedules
- Clean responsive browser UI

## Run Locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python schedulingApp.py
```

Open `http://127.0.0.1:3000`.

Optional `.env`:

```bash
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
```

## Project Files

```text
schedulingApp.py        Flask app, planner logic, and UI template
instance/schedules.db   Local SQLite schedule history
requirements.txt        Python dependencies
```
