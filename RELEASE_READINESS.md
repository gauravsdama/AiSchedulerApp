# Release readiness

Last verified: 2026-09-15

## Verdict

Ready as a public local/static portfolio demo once the current working tree is
committed. It is not a hosted scheduler, calendar integration, or production
Flask service.

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
- `docs/product/UI_COPY.md` inventories the Flask and static-demo strings and
  their required states.

## Verification evidence

```text
uv lock --check
uv run ruff format --check schedulingApp.py tests scripts
uv run ruff check schedulingApp.py tests scripts
uv run pytest -q                         # 5 passed
uv run pip-audit                         # no known vulnerabilities
uv run python scripts/release_guard.py   # passed, 21 release files
uv build
uv run python scripts/verify_distribution.py
```

Browser verification launched the Flask app and `docs/demo/`, exercised empty,
sample, and populated plans, checked the explicit no-AI disclosure, verified
320 px layout without horizontal overflow, and observed no console errors,
page errors, or failed requests.

Current screenshots:

- `docs/screenshots/day-sheet-empty.png`
- `docs/screenshots/day-sheet-plan.png`
- `docs/screenshots/flask-local-plan.png`

## Remaining boundaries

- The optional OpenAI path sends submitted notes to that service and was not
  exercised with a live key during this release pass.
- The Flask server has no authentication and is intentionally local-only.
- GitHub Pages settings and a clean-clone CI run remain external checks after
  the owner commits the working tree.
