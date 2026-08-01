#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const ROOT = path.resolve(__dirname, "..");
const HOOK = path.join(ROOT, "scripts", "checkpoint-hook.js");
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "xmemo-hook-test-"));
const project = path.join(temporary, "project");
fs.mkdirSync(project);

function run(event) {
  const result = spawnSync(process.execPath, [HOOK], {
    cwd: ROOT,
    env: { ...process.env, CLAUDE_PLUGIN_DATA: temporary },
    input: JSON.stringify({
      session_id: "test-session",
      cwd: project,
      transcript_path: path.join(temporary, "never-read.jsonl"),
      ...event
    }),
    encoding: "utf8"
  });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout ? JSON.parse(result.stdout) : null;
}

function batch(toolNames) {
  return run({
    hook_event_name: "PostToolBatch",
    tool_calls: toolNames.map((tool_name) => ({
      tool_name,
      tool_input: {},
      tool_response: "SENSITIVE_TRANSCRIPT_MARKER"
    }))
  });
}

try {
  assert.equal(run({ hook_event_name: "SessionStart", source: "startup" }), null);

  batch(["Edit", "Bash", "Write", "Bash", "Bash", "Bash"]);
  const stop = run({
    hook_event_name: "Stop",
    stop_hook_active: false,
    last_assistant_message: "Implementation is complete and verified.",
    background_tasks: [],
    session_crons: []
  });
  assert.equal(stop.hookSpecificOutput.hookEventName, "Stop");
  assert.match(stop.hookSpecificOutput.additionalContext, /XMemo checkpoint due/);

  assert.equal(
    run({
      hook_event_name: "Stop",
      stop_hook_active: true,
      last_assistant_message: "Saving checkpoint.",
      background_tasks: [],
      session_crons: []
    }),
    null
  );

  batch(["mcp__plugin_xmemo_xmemo__update_state"]);
  assert.equal(
    run({
      hook_event_name: "Stop",
      stop_hook_active: false,
      last_assistant_message: "Checkpoint saved.",
      background_tasks: [],
      session_crons: []
    }),
    null
  );

  run({
    hook_event_name: "TaskCompleted",
    task_id: "task-1",
    task_subject: "Complete the release slice"
  });
  const taskStop = run({
    hook_event_name: "Stop",
    stop_hook_active: false,
    last_assistant_message: "Task completed.",
    background_tasks: [],
    session_crons: []
  });
  assert.match(taskStop.hookSpecificOutput.additionalContext, /task_completed/);

  run({
    hook_event_name: "StopFailure",
    error: "rate_limit",
    error_details: "SENSITIVE_TRANSCRIPT_MARKER"
  });
  const resumed = run({ hook_event_name: "SessionStart", source: "resume" });
  assert.equal(resumed.hookSpecificOutput.hookEventName, "SessionStart");
  assert.match(resumed.hookSpecificOutput.additionalContext, /interrupted or unsaved/);

  const persisted = fs
    .readdirSync(path.join(temporary, "checkpoint-hooks"))
    .map((name) => fs.readFileSync(path.join(temporary, "checkpoint-hooks", name), "utf8"))
    .join("\n");
  assert.doesNotMatch(persisted, /SENSITIVE_TRANSCRIPT_MARKER/);
  assert.doesNotMatch(persisted, /transcript_path/);
  assert.equal(persisted.includes(project), false);

  console.log("XMemo checkpoint hook tests passed.");
} finally {
  fs.rmSync(temporary, { recursive: true, force: true });
}
