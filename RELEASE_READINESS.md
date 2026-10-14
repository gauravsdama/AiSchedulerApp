# Release readiness

Last verified: 2026-10-14

## Verdict

Ready for owner review and a local commit as a public portfolio repository. It
is not a hosted scheduler, calendar integration, or production Flask service.
The owner still needs to decide whether the static Day Sheet or the Flask/AI
planner is the canonical product surface; this pass intentionally preserves
both and does not present that decision as settled.

## Audience and project story

The intended user is a portfolio reviewer who wants to see a small planning
workflow without supplying an API key. Gaurav Dama's Flask app can use OpenAI
when explicitly configured, falls back to a deterministic local outline, and
stores the five latest plans in an ignored local SQLite database. The separate
Day Sheet page is a dependency-free browser demo with five sample task lists,
visible deterministic rules, and localStorage persistence; it does not call an
AI service.

## Release surface and privacy

- Repository history and remotes identify Gaurav Dama as the original author.
- `LICENSE`, `THIRD_PARTY_NOTICES.md`, package metadata, `uv.lock`, CI, tests,
  and archive verification are present. The owner approved the MIT license on
  2026-09-15.
- The previously tracked `instance/schedules.db` and `.DS_Store` are deleted.
  Runtime databases, environments, secrets, build output, and caches are
  ignored and rejected by the release guard.
- Flask binds to loopback with debug mode off. API calls have a 30-second
  timeout and one retry; provider exceptions are logged but not shown in UI.
- Request bodies, task notes, generated output, SQLite lock waits, and stored
  history are bounded. Failed writes roll back before history is rendered, and
  consecutive duplicate results are not stored twice.
- Storage initializes when the Flask module is imported, including through a
  WSGI server, rather than only when the file is run as a script.
- `docs/product/UI_COPY.md` inventories the Flask and static-demo strings and
  their required states.

## Verification evidence

```text
uv lock --check
uv run ruff format --check schedulingApp.py tests scripts
uv run ruff check schedulingApp.py tests scripts
uv run pytest -q                         # 13 passed
node --test tests/test_demo.js           # 4 passed
uv run pip-audit                         # no known vulnerabilities
uv run python scripts/release_guard.py   # passed, 21 release files
uv build
uv run python scripts/verify_distribution.py
```

Browser verification exercised all five sample plans in desktop and 320 px
layouts, tested saved and cleared state, keyboard focus, 200% zoom, reduced
motion, and accessibility rules, and observed no console errors, page errors,
failed requests, or horizontal overflow. GitHub Pages served the current
commit over HTTPS with the expected HTML, JavaScript, and CSS MIME types.

Current screenshots:

- `docs/screenshots/day-sheet-empty.png`
- `docs/screenshots/day-sheet-plan.png`
- `docs/screenshots/flask-local-plan.png`

## Remaining boundaries

- Canonical product direction remains an owner decision: the Pages root still
  opens the deterministic Day Sheet, while the Flask/AI planner remains the
  local Python application.
- History intentionally records only generated output and its creation time.
  No task input, selected day, provider, model, or request identifier was added;
  expanding that data policy requires owner approval.
- The Day Sheet truncates the last fitting task and omits later tasks rather
  than wrapping into another date. Owner-approved copy is needed before adding
  an overflow explanation or choosing a different deferral experience.
- Oversized Flask submissions receive the standard HTTP 413 response. An
  inline validation message requires owner-approved wording in the copy
  inventory.
- The optional OpenAI path sends submitted notes to that service and was not
  exercised with a live key during this release pass.
- The Flask server has no authentication and is intentionally local-only.
- Hosted CI and the Pages deployment are checked after each pushed change.
