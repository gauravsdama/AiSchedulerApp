(function () {
  "use strict";

  const STORAGE_KEY = "day-sheet-plan-v1";
  const DAY_END_MINUTES = 24 * 60;
  const CLOSE_BLOCK_MINUTES = 15;
  const EXAMPLES = {
    project: "Finish implementation — 90 min\nReview QA notes — 45 min\nWrite release notes — 45 min\nPrepare handoff — 30 min",
    class: "Review lecture notes — 45 min\nFinish database homework — 90 min\nGym — 60 min\nPack for tomorrow — 20 min",
    interview: "Review the role — 30 min\nPractice two coding problems — 90 min\nPrepare project stories — 45 min\nWrite questions for the interviewer — 20 min",
    errands: "Reply to important messages — 30 min\nBook appointments — 30 min\nPick up groceries — 45 min\nUpdate the monthly budget — 30 min",
    weekend: "Make breakfast — 30 min\nTake a long walk — 60 min\nRead — 45 min\nPlan the coming week — 30 min",
  };
  function parseDuration(text) {
    const hourMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)/i);
    if (hourMatch) return Math.max(15, Math.round(Number(hourMatch[1]) * 60));
    const minuteMatch = text.match(/(\d+)\s*(?:minutes?|mins?)/i);
    return minuteMatch ? Math.max(15, Number(minuteMatch[1])) : 45;
  }

  function cleanTask(text) {
    return text
      .replace(/^\s*(?:[-*•]\s+|\d{1,3}[.)]\s+)/, "")
      .replace(/\s*[-—,(]?\s*\d+(?:\.\d+)?\s*(?:hours?|hrs?|minutes?|mins?)\)?/i, "")
      .trim();
  }

  function parseTasks(value) {
    return value
      .split(/\n|;/)
      .map((line) => line.trim())
      .filter(Boolean)
      .slice(0, 10)
      .map((line) => ({ title: cleanTask(line) || line, minutes: Math.min(parseDuration(line), 180) }));
  }

  function formatTime(totalMinutes) {
    const hours = Math.floor(totalMinutes / 60) % 24;
    const minutes = totalMinutes % 60;
    return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(
      new Date(2020, 0, 1, hours, minutes),
    );
  }

  function startMinutes(day, now = new Date()) {
    if (day === "tomorrow") return 9 * 60;
    const rounded = Math.ceil((now.getHours() * 60 + now.getMinutes()) / 15) * 15;
    return Math.min(Math.max(rounded, 7 * 60), 20 * 60);
  }

  function buildPlan(tasks, day, now = new Date()) {
    let cursor = startMinutes(day, now);
    const taskBoundary = DAY_END_MINUTES - CLOSE_BLOCK_MINUTES;
    const blocks = [];
    for (const [index, task] of tasks.entries()) {
      const minutes = Math.min(task.minutes, taskBoundary - cursor);
      if (minutes <= 0) break;
      blocks.push({ ...task, minutes, start: cursor, kind: "task" });
      cursor += minutes;
      if (minutes < task.minutes) break;
      if ((index + 1) % 2 === 0 && index < tasks.length - 1) {
        const breakMinutes = Math.min(15, taskBoundary - cursor);
        if (breakMinutes <= 0) break;
        blocks.push({
          title: "Reset and review",
          minutes: breakMinutes,
          start: cursor,
          kind: "break",
        });
        cursor += breakMinutes;
      }
    }
    blocks.push({
      title: "Close the loop",
      minutes: CLOSE_BLOCK_MINUTES,
      start: cursor,
      kind: "break",
    });
    return blocks;
  }

  function dayDescription(day) {
    const value = new Date();
    if (day === "tomorrow") value.setDate(value.getDate() + 1);
    return new Intl.DateTimeFormat(undefined, { weekday: "long", month: "long", day: "numeric" }).format(value);
  }

  function persistenceState(isSaved) {
    return isSaved
      ? { clearHidden: false, status: "Schedule updated." }
      : { clearHidden: true, status: "Edit the tasks and rebuild to update the schedule." };
  }

  if (typeof document === "undefined") {
    module.exports = {
      buildPlan,
      cleanTask,
      parseDuration,
      parseTasks,
      persistenceState,
      startMinutes,
    };
    return;
  }

  const form = document.querySelector("#planner-form");
  const notes = document.querySelector("#task-notes");
  const list = document.querySelector("#schedule-list");
  const dateLabel = document.querySelector("#schedule-date");
  const saveStatus = document.querySelector("#save-status");
  const clearButton = document.querySelector("#clear-plan");
  const samplePlan = document.querySelector("#sample-plan");

  function render(plan, { isSaved = true } = {}) {
    list.replaceChildren();
    plan.blocks.forEach((block) => {
      const item = document.createElement("li");
      item.className = `schedule-item ${block.kind}`;

      const time = document.createElement("span");
      time.className = "schedule-time";
      time.textContent = formatTime(block.start);

      const copy = document.createElement("div");
      copy.className = "schedule-copy";
      const title = document.createElement("strong");
      title.textContent = block.title;
      const duration = document.createElement("span");
      duration.textContent = `${block.minutes} minutes`;
      copy.append(title, duration);
      item.append(time, copy);
      list.append(item);
    });
    dateLabel.textContent = dayDescription(plan.day);
    const persistence = persistenceState(isSaved);
    saveStatus.textContent = persistence.status;
    clearButton.hidden = persistence.clearHidden;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const tasks = parseTasks(notes.value);
    if (!tasks.length) {
      notes.setCustomValidity("Add at least one task to build your day.");
      notes.reportValidity();
      return;
    }
    notes.setCustomValidity("");
    const day = new FormData(form).get("day") || "today";
    const plan = { day, notes: notes.value, blocks: buildPlan(tasks, day) };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(plan));
    render(plan);
  });

  notes.addEventListener("input", () => notes.setCustomValidity(""));

  samplePlan.addEventListener("change", () => {
    if (!EXAMPLES[samplePlan.value]) return;
    notes.value = EXAMPLES[samplePlan.value];
    notes.focus();
  });

  clearButton.addEventListener("click", () => {
    localStorage.removeItem(STORAGE_KEY);
    window.location.reload();
  });

  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (saved && Array.isArray(saved.blocks) && saved.day) {
      notes.value = saved.notes || "";
      const selectedDay = document.querySelector(`input[name="day"][value="${saved.day}"]`);
      if (selectedDay) selectedDay.checked = true;
      render(saved);
    } else {
      render(
        {
          day: "today",
          notes: notes.value,
          blocks: buildPlan(parseTasks(notes.value), "today", new Date(2026, 7, 16, 9, 0)),
        },
        { isSaved: false },
      );
    }
  } catch (_error) {
    localStorage.removeItem(STORAGE_KEY);
  }
})();
