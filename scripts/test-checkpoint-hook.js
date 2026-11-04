#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const ROOT = path.resolve(__dirname, "..");
// XMEMO_HOOK_PATH lets the release pipeline test the hook inside a staged release tree.
const HOOK = process.env.XMEMO_HOOK_PATH
  ? path.resolve(process.env.XMEMO_HOOK_PATH)
  : path.join(ROOT, "scripts", "checkpoint-hook.js");
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "xmemo-hook-test-"));
const project = path.join(temporary, "project");
fs.mkdirSync(project);
const key = "active_task";
// Synthetic contract cases, not a captured Claude host fixture.
const receipt = (stateKey = key, status = "updated") =>
  `✅ Working state updated.\nState Key: ${stateKey}\nID: dummy-123\nStatus: ${status}\nExpires At: never`;
// Captured from Claude Code 2.1.318; the service record ID is redacted.
const liveToolResponse = JSON.stringify({
  result:
    "✅ Working state updated.\n" +
    "State Key: codex_plugin_receipt_fixture_20261104\n" +
    "ID: <redacted>\n" +
    "Status: created\n" +
    "Expires At: 2026-11-04T14:51:17.732249+00:00"
});
function acknowledge(overrides = {}) {
  return run({ hook_event_name: "PostToolBatch", tool_calls: [{
    tool_name: "mcp__plugin_xmemo_xmemo__update_state",
    tool_input: { state_key: key }, tool_response: receipt(), ...overrides
  }] });
}
function pending() {
  const file = fs.readdirSync(path.join(temporary, "checkpoint-hooks"))[0];
  return JSON.parse(fs.readFileSync(path.join(temporary, "checkpoint-hooks", file), "utf8")).dirty;
}

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

  acknowledge();
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

  // Other XMemo tools do not clear a pending checkpoint.
  batch(["Edit", "Bash", "Write", "Bash", "Bash", "Bash"]);
  batch(["mcp__plugin_xmemo_xmemo__recall"]);
  assert.match(
    run({
      hook_event_name: "Stop",
      stop_hook_active: false,
      last_assistant_message: "Recalled context.",
      background_tasks: [],
      session_crons: []
    }).hookSpecificOutput.additionalContext,
    /XMemo checkpoint due/
  );

  // Neither foreign connections nor failed or ambiguous saves acknowledge.
  for (const overrides of [
    { tool_name: "mcp__aded79cf__update_state" },
    { tool_name: "mcp__other__update_state" },
    { tool_response: "Error: unavailable" },
    { tool_response: receipt(), is_error: true },
    { tool_response: receipt(), isError: true },
    { tool_response: { status: "updated" } },
    { tool_response: receipt(key, "failed") },
    { tool_response: [{ type: "text", text: "Error" }] },
    { tool_response: undefined }
  ]) {
    acknowledge(overrides);
    assert.equal(pending(), true, JSON.stringify(overrides));
  }
  acknowledge({ tool_response: [{ type: "text", text: receipt(key, "created") }] });
  assert.equal(pending(), false);
  batch(["Write"]);
  assert.equal(pending(), true);
  acknowledge({ tool_response: liveToolResponse });
  assert.equal(pending(), false);
  for (const overrides of [
    { tool_input: {} }, // Skills may rely on the default active_task slot.
    { tool_input: { state_key: "My Slot" }, tool_response: receipt("my-slot") },
    { tool_response: "✅ Working state updated.\r\nExtra info\r\nStatus: updated" },
    { tool_response: [{ type: "text", text: "✅ Working state updated." },
                      { type: "text", text: "Status: created" }] }
  ]) {
    batch(["Write"]);
    assert.equal(pending(), true);
    acknowledge(overrides);
    assert.equal(pending(), false);
  }
  for (const response of [
    "✅ Working state updated.\nStatus: updated\nStatus: failed",
    "Error\n✅ Working state updated.\nStatus: updated",
    "✅ Working state updated.\nStatus: unknown",
    "✅ Working state updated.\nStatus: updated\n" + "x".repeat(4096),
    [{ type: "image", data: "unused" }]
  ]) {
    batch(["Write"]);
    acknowledge({ tool_response: response });
    assert.equal(pending(), true);
  }
  // A simultaneous workspace change remains pending even alongside a successful save.
  run({ hook_event_name: "PostToolBatch", tool_calls: [
    { tool_name: "mcp__plugin_xmemo_xmemo__update_state",
      tool_input: { state_key: key }, tool_response: receipt() },
    { tool_name: "Write" }
  ] });
  assert.equal(pending(), true);

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
