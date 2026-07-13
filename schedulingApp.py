from __future__ import annotations

import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template_string, request, url_for
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI


load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schedules.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Daily Planner</title>
    <style>
        :root {
            --bg: #f5f4ee;
            --ink: #151917;
            --muted: #5d665f;
            --panel: #ffffff;
            --line: #d9d6ca;
            --green: #156b58;
            --green-dark: #0f4036;
            --blue: #315d8d;
            --gold: #c88b2a;
            --shadow: 0 22px 70px rgba(27, 42, 37, 0.13);
        }

        * { box-sizing: border-box; }

        body {
            min-width: 320px;
            margin: 0;
            color: var(--ink);
            background:
                linear-gradient(120deg, rgba(21, 107, 88, 0.12), transparent 34%),
                repeating-linear-gradient(90deg, rgba(21, 25, 23, 0.034) 0, rgba(21, 25, 23, 0.034) 1px, transparent 1px, transparent 92px),
                var(--bg);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .shell {
            width: min(1160px, calc(100% - 32px));
            margin: 0 auto;
            padding: 28px 0 64px;
        }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 46px;
        }

        .brand {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            font-weight: 900;
        }

        .brand-mark {
            display: grid;
            width: 44px;
            height: 44px;
            place-items: center;
            border-radius: 8px;
            background: var(--green-dark);
            color: #ffffff;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 0.8rem;
        }

        .layout {
            display: grid;
            grid-template-columns: minmax(0, 0.96fr) minmax(340px, 0.88fr);
            gap: 28px;
            align-items: start;
        }

        h1, h2, p { margin-top: 0; }

        .eyebrow {
            margin: 0 0 12px;
            color: var(--green);
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        h1 {
            max-width: 750px;
            margin-bottom: 16px;
            font-size: clamp(2.65rem, 6vw, 5rem);
            line-height: 0.96;
        }

        h2 {
            margin-bottom: 14px;
            font-size: 1.35rem;
        }

        p {
            color: var(--muted);
            line-height: 1.68;
        }

        .panel, .schedule-card, .pill {
            border-radius: 8px;
        }

        .panel, .schedule-card {
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.94);
            box-shadow: var(--shadow);
        }

        .panel {
            padding: 24px;
        }

        .form-stack {
            display: grid;
            gap: 15px;
        }

        label {
            display: block;
            margin-bottom: 7px;
            color: #26332f;
            font-size: 0.86rem;
            font-weight: 850;
        }

        textarea {
            width: 100%;
            min-height: 158px;
            resize: vertical;
            border: 1px solid #c9d2cc;
            border-radius: 8px;
            padding: 12px;
            background: #ffffff;
            color: var(--ink);
            font: inherit;
            line-height: 1.55;
        }

        textarea:focus, input:focus, button:focus {
            outline: 3px solid rgba(21, 107, 88, 0.23);
            outline-offset: 2px;
        }

        .segmented {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px;
        }

        .segmented input {
            position: absolute;
            opacity: 0;
            pointer-events: none;
        }

        .segmented label {
            display: grid;
            min-height: 44px;
            place-items: center;
            margin: 0;
            border: 1px solid #c9d2cc;
            border-radius: 8px;
            background: #ffffff;
            color: var(--muted);
            cursor: pointer;
        }

        .segmented input:checked + label {
            border-color: var(--green-dark);
            background: var(--green-dark);
            color: #ffffff;
        }

        button {
            min-height: 48px;
            border: 0;
            border-radius: 8px;
            background: var(--green-dark);
            color: #ffffff;
            font: inherit;
            font-weight: 900;
            cursor: pointer;
        }

        .result {
            border: 1px solid rgba(49, 93, 141, 0.25);
            border-radius: 8px;
            padding: 18px;
            background: #eef5fb;
        }

        .result p, .schedule-card p {
            margin-bottom: 0;
            white-space: pre-wrap;
        }

        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 9px;
            margin-top: 24px;
        }

        .pill {
            display: inline-flex;
            min-height: 34px;
            align-items: center;
            padding: 7px 10px;
            background: #e6eee9;
            color: #20362f;
            font-size: 0.84rem;
            font-weight: 850;
        }

        .pill.gold {
            background: #f5e0b8;
            color: #5a3b05;
        }

        .history {
            display: grid;
            gap: 12px;
        }

        .schedule-card {
            padding: 16px;
        }

        .schedule-card time {
            display: block;
            margin-bottom: 9px;
            color: var(--blue);
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
        }

        .empty {
            border: 1px dashed var(--line);
            border-radius: 8px;
            padding: 18px;
            background: rgba(255, 255, 255, 0.65);
        }

        @media (max-width: 860px) {
            .topbar { align-items: flex-start; flex-direction: column; }
            .layout { grid-template-columns: 1fr; }
            .segmented { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <main class="shell">
        <header class="topbar">
            <div class="brand">
                <span class="brand-mark">AI</span>
                <span>Daily Planner</span>
            </div>
            <p class="eyebrow">{{ mode_label }}</p>
        </header>

        <section class="layout">
            <div>
                <p class="eyebrow">AI scheduler</p>
                <h1>Turn messy task notes into a focused daily plan.</h1>
                <p>Choose today or tomorrow, describe the constraints, and generate a structured schedule that is saved locally for review.</p>
                <div class="pill-row" aria-label="Planner features">
                    <span class="pill">SQLite history</span>
                    <span class="pill">Today/tomorrow planning</span>
                    <span class="pill gold">No-key fallback</span>
                </div>
            </div>

            <div class="panel">
                <form method="post" action="{{ url_for('daily_planner') }}" class="form-stack">
                    <div>
                        <label for="input_text">Planning details</label>
                        <textarea name="input_text" id="input_text" maxlength="1000" placeholder="Example: Work 9-5, gym at 7pm, finish database homework, and leave time for dinner." required>{{ values.input_text }}</textarea>
                    </div>

                    <div>
                        <label>Schedule date</label>
                        <div class="segmented">
                            <input type="radio" name="schedule_date" id="today" value="today" {% if values.schedule_date == 'today' %}checked{% endif %}>
                            <label for="today">Today</label>
                            <input type="radio" name="schedule_date" id="tomorrow" value="tomorrow" {% if values.schedule_date == 'tomorrow' %}checked{% endif %}>
                            <label for="tomorrow">Tomorrow</label>
                        </div>
                    </div>

                    <button type="submit">Generate Plan</button>
                </form>

                {% if response %}
                    <div class="result" role="status" aria-live="polite">
                        <h2>Your plan</h2>
                        <p>{{ response }}</p>
                    </div>
                {% endif %}
            </div>
        </section>

        <section class="layout" style="margin-top: 34px;">
            <div>
                <p class="eyebrow">Saved locally</p>
                <h2>Past schedules</h2>
                <p>Generated plans are stored in the local SQLite database so the newest schedule stays visible after refresh.</p>
            </div>
            <div class="history">
                {% if schedules %}
                    {% for sched in schedules %}
                        <article class="schedule-card">
                            <time>{{ sched.created_at.strftime('%b %d, %Y %I:%M %p') }}</time>
                            <p>{{ sched.content }}</p>
                        </article>
                    {% endfor %}
                {% else %}
                    <div class="empty">
                        <p>No schedules saved yet.</p>
                    </div>
                {% endif %}
            </div>
        </section>
    </main>
</body>
</html>
"""


def _make_openai_client() -> OpenAI | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def _schedule_instructions(schedule_date: str) -> tuple[str, str]:
    if schedule_date == "today":
        current_time = datetime.now().strftime("%I:%M %p")
        return (
            "Today",
            f"Today is the scheduled day and the current time is {current_time}. Plan from now through the evening.",
        )
    return (
        "Tomorrow",
        "The schedule is for tomorrow. Plan from the morning through the evening.",
    )


def _fallback_schedule(user_input: str, schedule_date: str) -> str:
    start_label = "Now" if schedule_date == "today" else "9:00 AM"
    return (
        f"{start_label} - Capture priorities and choose the top three outcomes.\\n"
        "Focus block 1 - Work on the most time-sensitive task from your notes.\\n"
        "Break - Reset, hydrate, and check for schedule conflicts.\\n"
        "Focus block 2 - Handle the next highest-impact task or errand.\\n"
        "Wrap-up - Review progress, move unfinished items, and prepare tomorrow's first step.\\n\\n"
        f"Notes considered: {user_input[:220]}"
    )


def generate_schedule(user_input: str, schedule_date: str) -> str:
    mode_label, instructions = _schedule_instructions(schedule_date)
    client = _make_openai_client()
    if client is None:
        logging.info("OPENAI_API_KEY is not set. Using local fallback schedule.")
        return _fallback_schedule(user_input, schedule_date)

    system_message = (
        "You are an AI daily planner. "
        f"{instructions} Provide a structured, practical {mode_label.lower()} schedule from the user's constraints."
    )
    api_response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input},
        ],
        max_tokens=700,
        temperature=0.6,
    )
    return api_response.choices[0].message.content or _fallback_schedule(user_input, schedule_date)


@app.route("/", methods=["GET", "POST"])
def daily_planner():
    response_text = None
    values = {
        "input_text": "",
        "schedule_date": "today",
    }

    if request.method == "POST":
        values["input_text"] = request.form.get("input_text", "").strip()
        values["schedule_date"] = request.form.get("schedule_date", "today")

        if values["input_text"]:
            try:
                response_text = generate_schedule(values["input_text"], values["schedule_date"])
                db.session.add(Schedule(content=response_text))
                db.session.commit()
            except Exception as exc:
                logging.exception("Error generating schedule")
                response_text = f"Schedule generation failed: {exc}"

    schedules = Schedule.query.order_by(Schedule.created_at.desc()).limit(5).all()
    mode_label, _ = _schedule_instructions(values["schedule_date"])
    return render_template_string(
        HTML_TEMPLATE,
        mode_label=f"{mode_label} mode",
        response=response_text,
        schedules=schedules,
        values=values,
    )


@app.route("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
