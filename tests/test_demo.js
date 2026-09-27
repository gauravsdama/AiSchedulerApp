"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");

const { buildPlan, cleanTask, parseTasks } = require("../docs/demo/app.js");

test("numeric task titles survive list-marker cleanup", () => {
  assert.equal(cleanTask("1. Write release notes"), "Write release notes");
  assert.equal(cleanTask("12) Prepare handoff"), "Prepare handoff");
  assert.equal(cleanTask("401(k) rollover review"), "401(k) rollover review");
  assert.equal(cleanTask("2026 planning"), "2026 planning");
});

test("task parsing keeps numeric titles and bounds durations", () => {
  assert.deepEqual(parseTasks("401(k) review — 30 min\n2. Deep work — 9 hours"), [
    { title: "401(k) review", minutes: 30 },
    { title: "Deep work", minutes: 180 },
  ]);
});

test("a plan never crosses the selected day boundary", () => {
  const tasks = Array.from({ length: 10 }, (_, index) => ({
    title: `Task ${index}`,
    minutes: 180,
  }));
  const blocks = buildPlan(tasks, "tomorrow");

  assert.equal(blocks.at(-1).title, "Close the loop");
  assert.equal(blocks.at(-1).start + blocks.at(-1).minutes, 24 * 60);
  assert.ok(blocks.every((block) => block.start >= 0));
  assert.ok(blocks.every((block) => block.start + block.minutes <= 24 * 60));
});
