from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

os.environ["SCHEDULER_DATABASE_URI"] = "sqlite:///:memory:"

import schedulingApp


@pytest.fixture(autouse=True)
def isolated_database():
    schedulingApp.app.config.update(TESTING=True)
    with schedulingApp.app.app_context():
        schedulingApp.db.session.remove()
        schedulingApp.db.drop_all()
        schedulingApp.db.create_all()
    yield
    with schedulingApp.app.app_context():
        schedulingApp.db.session.remove()


def test_health_check() -> None:
    response = schedulingApp.app.test_client().get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_no_key_path_builds_and_saves_local_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = schedulingApp.app.test_client()
    response = client.post(
        "/",
        data={"input_text": "Write report", "schedule_date": "tomorrow"},
    )
    assert response.status_code == 200
    assert b"9:00 AM - Capture priorities" in response.data
    assert b"\\n" not in response.data
    with schedulingApp.app.app_context():
        assert schedulingApp.Schedule.query.count() == 1


def test_invalid_day_falls_back_to_today(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = schedulingApp.app.test_client().post(
        "/",
        data={"input_text": "Write report", "schedule_date": "not-a-day"},
    )
    assert response.status_code == 200
    assert b"Now - Capture priorities" in response.data


def test_provider_errors_do_not_leak_exception_text(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(_text: str, _day: str) -> str:
        raise RuntimeError("provider-secret-detail")

    monkeypatch.setattr(schedulingApp, "generate_schedule", fail)
    response = schedulingApp.app.test_client().post(
        "/",
        data={"input_text": "Write report", "schedule_date": "today"},
    )
    assert response.status_code == 200
    assert b"provider-secret-detail" not in response.data
    assert "Couldn’t build the plan" in response.get_data(as_text=True)


def test_static_demo_is_local_and_uses_relative_assets() -> None:
    html = Path("docs/demo/index.html").read_text(encoding="utf-8")
    script = Path("docs/demo/app.js").read_text(encoding="utf-8")
    assert 'href="./styles.css"' in html
    assert 'src="./app.js"' in html
    assert "no account or API key" in html
    assert "not AI" in html
    assert html.count('<option value="') == 6
    for sample in (
        "Project deadline",
        "Class and gym",
        "Interview prep",
        "Errands and admin",
        "Quiet weekend reset",
    ):
        assert sample in html
    assert not re.search(
        r"https?://", html.replace("https://github.com/gauravsdama/AiSchedulerApp", "")
    )
    assert "fetch(" not in script
