# AI Daily Planner UI copy

This is the human-owned source of truth for every user-facing string in the
Flask app and static AI Scheduler demo. Stable IDs remain unchanged when text is
edited. Runtime text must match this inventory exactly.

## Flask app

| ID | State / component | Approved text | Location |
| --- | --- | --- | --- |
| `planner.flask.meta.title` | Browser title | AI Daily Planner | `HTML_TEMPLATE` |
| `planner.flask.brand.mark` | Brand mark | AI | `HTML_TEMPLATE` |
| `planner.flask.brand.name` | Brand | Daily Planner | `HTML_TEMPLATE` |
| `planner.flask.mode` | Selected-day status | Today mode / Tomorrow mode | `_schedule_instructions`, `daily_planner` |
| `planner.flask.hero` | Main heading | Turn messy task notes into a focused daily plan. | `HTML_TEMPLATE` |
| `planner.flask.intro` | Introduction | Choose today or tomorrow, describe the constraints, and generate a structured schedule that is saved locally for review. | `HTML_TEMPLATE` |
| `planner.flask.input.label` | Notes label | Planning details | `HTML_TEMPLATE` |
| `planner.flask.input.placeholder` | Notes example | Example: Work 9-5, gym at 7pm, finish database homework, and leave time for dinner. | `HTML_TEMPLATE` |
| `planner.flask.day.label` | Day choice label | Schedule date | `HTML_TEMPLATE` |
| `planner.shared.today` | Day choice | Today | `HTML_TEMPLATE` |
| `planner.shared.tomorrow` | Day choice | Tomorrow | `HTML_TEMPLATE` |
| `planner.flask.submit` | Primary action | Generate Plan | `HTML_TEMPLATE` |
| `planner.flask.result.title` | Result heading | Your plan | `HTML_TEMPLATE` |
| `planner.flask.history.kicker` | History context | Saved locally | `HTML_TEMPLATE` |
| `planner.flask.history.title` | History heading | Past schedules | `HTML_TEMPLATE` |
| `planner.flask.history.description` | History explanation | Generated plans are stored in the local SQLite database so the newest schedule stays visible after refresh. | `HTML_TEMPLATE` |
| `planner.flask.history.empty` | Empty state | No schedules saved yet. | `HTML_TEMPLATE` |
| `planner.flask.error` | Provider error | Couldn’t build the plan. Check the API configuration or try the local planner. | `daily_planner` |
| `planner.fallback.now` | Same-day start | Now | `_fallback_schedule` |
| `planner.fallback.morning` | Tomorrow start | 9:00 AM | `_fallback_schedule` |
| `planner.fallback.priorities` | Local-plan block | Capture priorities and choose the top three outcomes. | `_fallback_schedule` |
| `planner.fallback.focus-one` | Local-plan block | Focus block 1 - Work on the most time-sensitive task from your notes. | `_fallback_schedule` |
| `planner.fallback.break` | Local-plan block | Break - Reset, hydrate, and check for schedule conflicts. | `_fallback_schedule` |
| `planner.fallback.focus-two` | Local-plan block | Focus block 2 - Handle the next highest-impact task or errand. | `_fallback_schedule` |
| `planner.fallback.wrap` | Local-plan block | Wrap-up - Review progress, move unfinished items, and prepare tomorrow's first step. | `_fallback_schedule` |
| `planner.fallback.notes` | Local-plan echo label | Notes considered: {first 220 characters} | `_fallback_schedule` |

The optional remote model generates free-form plan text, so its output cannot
be pre-inventoried. It is always displayed beneath `planner.flask.result.title`.

## Static AI Scheduler demo

| ID | State / component | Approved text | Location |
| --- | --- | --- | --- |
| `planner.demo.meta.description` | Page metadata | AI Scheduler daily planning demo. | `index.html` |
| `planner.demo.meta.title` | Browser title | AI Scheduler | `index.html` |
| `planner.demo.brand.label` | Accessible home label | AI Scheduler home | `index.html` |
| `planner.demo.brand` | Brand | AI SCHEDULER | `index.html` |
| `planner.demo.hero` | Main heading | AI Scheduler | `index.html` |
| `planner.demo.intro` | Input guidance | Enter one task per line and include a duration when it matters. Build the schedule to see the tasks arranged into time blocks. | `index.html` |
| `planner.demo.input.label` | Notes label | Tasks | `index.html` |
| `planner.demo.input.example` | Initial task list | Review lecture notes — 45 min\nFinish database homework — 90 min\nGym — 60 min\nPack for tomorrow — 20 min | `index.html` |
| `planner.demo.day.label` | Day choice legend | Plan for | `index.html` |
| `planner.demo.submit` | Primary action | Build schedule | `index.html` |
| `planner.demo.examples.label` | Sample selector label | Examples | `index.html` |
| `planner.demo.examples.empty` | Sample selector placeholder | Choose a plan | `index.html` |
| `planner.demo.examples.project` | Sample plan | Project deadline | `index.html` |
| `planner.demo.examples.class` | Sample plan | Class and gym | `index.html` |
| `planner.demo.examples.interview` | Sample plan | Interview prep | `index.html` |
| `planner.demo.examples.errands` | Sample plan | Errands and admin | `index.html` |
| `planner.demo.examples.weekend` | Sample plan | Quiet weekend reset | `index.html` |
| `planner.demo.ready` | Initial schedule date | Today | `index.html` |
| `planner.demo.result.title` | Result heading | Schedule | `index.html` |
| `planner.demo.clear` | Destructive action | Clear saved plan | `index.html` |
| `planner.demo.empty.time` | Empty-sheet time | 09:00 | `index.html` |
| `planner.demo.empty` | Empty state | The generated schedule appears here. | `index.html` |
| `planner.demo.unsaved` | Initial persistence state | Edit the tasks and rebuild to update the schedule. | `index.html` |
| `planner.demo.project-link` | Repository link | View source | `index.html` |
| `planner.demo.validation` | Empty-input validation | Add at least one task to build your day. | `app.js` |
| `planner.demo.break` | Inserted break | Reset and review | `app.js` |
| `planner.demo.close` | Final block | Close the loop | `app.js` |
| `planner.demo.duration` | Duration suffix | {minutes} minutes | `app.js` |
| `planner.demo.saved` | Update confirmation | Schedule updated. | `app.js` |
| `planner.demo.date` | Schedule date | Locale-formatted weekday, month, and day | `app.js` |

## Required states

- Empty, five sample plans, custom input, populated, saved, cleared,
  validation-error, today, and tomorrow states.
- Keyboard-visible focus, semantic labels, a live result region, 320 px layout,
  200% zoom, and reduced-motion compatibility.
- The static demo must remain dependency-free, must not make network requests,
  and must not imply that its deterministic rules call an AI model.
