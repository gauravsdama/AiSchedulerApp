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


def test_storage_initialization_creates_instance_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    instance_path = tmp_path / "instance"
    create_all_called = False

    def create_all() -> None:
        nonlocal create_all_called
        create_all_called = True

    monkeypatch.setattr(schedulingApp.app, "instance_path", str(instance_path))
    monkeypatch.setattr(schedulingApp.db, "create_all", create_all)

    schedulingApp.initialize_storage()

    assert instance_path.is_dir()
    assert create_all_called is True


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


def test_provider_timeouts_do_not_leak_exception_text(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(_text: str, _day: str) -> str:
        raise TimeoutError("provider-secret-detail")

    monkeypatch.setattr(schedulingApp, "generate_schedule", fail)
    response = schedulingApp.app.test_client().post(
        "/",
        data={"input_text": "Write report", "schedule_date": "today"},
    )
    assert response.status_code == 200
    assert b"provider-secret-detail" not in response.data
    assert "Couldn’t build the plan" in response.get_data(as_text=True)


def test_provider_client_has_bounded_waits(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(schedulingApp, "OpenAI", FakeClient)

    assert schedulingApp._make_openai_client() is not None
    assert captured == {"api_key": "test-key", "timeout": 30.0, "max_retries": 1}


def test_failed_commit_rolls_back_and_preserves_history(monkeypatch: pytest.MonkeyPatch) -> None:
    with schedulingApp.app.app_context():
        schedulingApp.db.session.add(schedulingApp.Schedule(content="Existing plan"))
        schedulingApp.db.session.commit()

    def fail_save(_content: str) -> None:
        schedulingApp.db.session.add(schedulingApp.Schedule(content=None))
        schedulingApp.db.session.commit()

    monkeypatch.setattr(schedulingApp, "_save_schedule", fail_save)
    response = schedulingApp.app.test_client().post(
        "/",
        data={"input_text": "Write report", "schedule_date": "today"},
    )

    assert response.status_code == 200
    assert "Couldn’t build the plan" in response.get_data(as_text=True)
    assert b"Existing plan" in response.data
    with schedulingApp.app.app_context():
        assert schedulingApp.Schedule.query.count() == 1


def test_duplicate_submissions_are_stored_once(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = schedulingApp.app.test_client()
    submission = {"input_text": "Write report", "schedule_date": "today"}

    assert client.post("/", data=submission).status_code == 200
    assert client.post("/", data=submission).status_code == 200

    with schedulingApp.app.app_context():
        assert schedulingApp.Schedule.query.count() == 1


def test_history_is_pruned_to_five_schedules(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = schedulingApp.app.test_client()

    for index in range(7):
        response = client.post(
            "/",
            data={"input_text": f"Task {index}", "schedule_date": "today"},
        )
        assert response.status_code == 200

    with schedulingApp.app.app_context():
        schedules = schedulingApp.Schedule.query.order_by(schedulingApp.Schedule.id).all()
        assert len(schedules) == schedulingApp.HISTORY_LIMIT
        assert "Task 0" not in {schedule.content for schedule in schedules}
        assert "Task 6" in schedules[-1].content


def test_server_rejects_oversized_input(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def generate(_text: str, _day: str) -> str:
        nonlocal called
        called = True
        return "plan"

    monkeypatch.setattr(schedulingApp, "generate_schedule", generate)
    response = schedulingApp.app.test_client().post(
        "/",
        data={
            "input_text": "x" * (schedulingApp.MAX_INPUT_CHARS + 1),
            "schedule_date": "today",
        },
    )

    assert response.status_code == 413
    assert called is False


def test_server_rejects_oversized_request_body() -> None:
    response = schedulingApp.app.test_client().post(
        "/",
        data="x" * (schedulingApp.MAX_REQUEST_BYTES + 1),
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 413


def test_generated_output_is_bounded_before_storage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        schedulingApp,
        "generate_schedule",
        lambda _text, _day: "x" * (schedulingApp.MAX_SCHEDULE_CHARS + 1),
    )
    response = schedulingApp.app.test_client().post(
        "/",
        data={"input_text": "Write report", "schedule_date": "today"},
    )

    assert response.status_code == 200
    with schedulingApp.app.app_context():
        saved = schedulingApp.Schedule.query.one()
        assert len(saved.content) == schedulingApp.MAX_SCHEDULE_CHARS


def test_static_demo_is_local_and_uses_relative_assets() -> None:
    html = Path("docs/demo/index.html").read_text(encoding="utf-8")
    script = Path("docs/demo/app.js").read_text(encoding="utf-8")
    assert 'href="./styles.css"' in html
    assert 'src="./app.js"' in html
    assert "AI Scheduler" in html
    assert "Build schedule" in html
    assert "Finish database homework" in html
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
