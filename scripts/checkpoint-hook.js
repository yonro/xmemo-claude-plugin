#!/usr/bin/env node
"use strict";

const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const STATE_VERSION = 1;
const MAX_INPUT_BYTES = 16 * 1024 * 1024;
const CHECKPOINT_INTERVAL_MS = 15 * 60 * 1000;
const PROMPT_COOLDOWN_MS = 10 * 60 * 1000;
const ACTIVITY_THRESHOLD = 6;

// Only the plugin-owned connection may acknowledge its checkpoint reminder.
const XMEMO_UPDATE_STATE = "mcp__plugin_xmemo_xmemo__update_state";
const WRITE_TOOLS = new Set(["Edit", "Write", "NotebookEdit", "MultiEdit"]);
const WORK_TOOLS = new Set([
  ...WRITE_TOOLS,
  "Bash",
  "TaskUpdate",
  "WebFetch",
  "WebSearch"
]);

function readInput() {
  const raw = fs.readFileSync(0, "utf8");
  if (Buffer.byteLength(raw, "utf8") > MAX_INPUT_BYTES) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function normalizeProject(cwd) {
  const resolved = path.resolve(String(cwd || process.cwd()));
  return process.platform === "win32" ? resolved.toLowerCase() : resolved;
}

function stateLocation(input) {
  const dataRoot = process.env.CLAUDE_PLUGIN_DATA;
  if (!dataRoot) {
    return null;
  }
  const project = normalizeProject(input.cwd);
  const projectKey = crypto.createHash("sha256").update(project).digest("hex");
  const directory = path.join(dataRoot, "checkpoint-hooks");
  fs.mkdirSync(directory, { recursive: true, mode: 0o700 });
  return {
    file: path.join(directory, `${projectKey}.json`),
    projectKey
  };
}

function emptyState(projectKey) {
  return {
    version: STATE_VERSION,
    projectKey,
    dirty: false,
    activityCount: 0,
    writeCount: 0,
    reasons: [],
    firstDirtyAt: null,
    lastActivityAt: null,
    lastCheckpointAt: null,
    lastPromptAt: null,
    forceCheckpoint: false,
    recovery: null
  };
}

function loadState(location) {
  if (!fs.existsSync(location.file)) {
    return emptyState(location.projectKey);
  }
  try {
    const state = JSON.parse(fs.readFileSync(location.file, "utf8"));
    if (state.version !== STATE_VERSION || state.projectKey !== location.projectKey) {
      return emptyState(location.projectKey);
    }
    return { ...emptyState(location.projectKey), ...state };
  } catch {
    return emptyState(location.projectKey);
  }
}

function saveState(location, state) {
  const temporary = `${location.file}.${process.pid}.tmp`;
  fs.writeFileSync(temporary, `${JSON.stringify(state, null, 2)}\n`, {
    encoding: "utf8",
    mode: 0o600
  });
  try {
    fs.renameSync(temporary, location.file);
  } catch {
    fs.rmSync(location.file, { force: true });
    fs.renameSync(temporary, location.file);
  }
}

function addReason(state, reason) {
  if (!state.reasons.includes(reason)) {
    state.reasons.push(reason);
  }
  state.reasons = state.reasons.slice(-8);
}

function markActivity(state, { count = 1, writes = 0, reason, force = false }) {
  const now = Date.now();
  state.dirty = true;
  state.activityCount += count;
  state.writeCount += writes;
  state.firstDirtyAt ||= now;
  state.lastActivityAt = now;
  state.forceCheckpoint ||= force;
  if (reason) {
    addReason(state, reason);
  }
}

function clearCheckpoint(state) {
  state.dirty = false;
  state.activityCount = 0;
  state.writeCount = 0;
  state.reasons = [];
  state.firstDirtyAt = null;
  state.lastActivityAt = null;
  state.lastCheckpointAt = Date.now();
  state.lastPromptAt = null;
  state.forceCheckpoint = false;
  state.recovery = null;
}

function checkpointSaved(call) {
  if (!call || call.tool_name !== XMEMO_UPDATE_STATE ||
      call.is_error === true || call.isError === true) return false;
  // PostToolBatch supplies serialized text or text content blocks. Inspect only
  // a bounded receipt; never retain it or impose a new state slot on Skills.
  const response = call.tool_response;
  let text;
  if (typeof response === "string") text = response;
  else if (Array.isArray(response) && response.length > 0 && response.length <= 16) {
    const parts = [];
    let length = 0;
    for (const block of response) {
      if (block?.type !== "text" || typeof block.text !== "string") return false;
      length += block.text.length + 1;
      if (length > 4096) return false;
      parts.push(block.text);
    }
    text = parts.join("\n");
  }
  if (typeof text !== "string" || text.length > 4096) return false;
  try {
    const envelope = JSON.parse(text);
    if (envelope && typeof envelope === "object" && !Array.isArray(envelope) &&
        Object.keys(envelope).length === 1 && typeof envelope.result === "string") {
      text = envelope.result;
    }
  } catch {
    // Claude may provide the receipt as plain text instead of a JSON envelope.
  }
  if (text.length > 4096) return false;
  const lines = text.trim().split(/\r?\n/).map(line => line.trim());
  const statuses = lines.filter(line => /^Status\s*:/i.test(line));
  return /^✅\s+Working state updated[.!]?$/.test(lines[0] || "") &&
    statuses.length === 1 && /^Status:\s*(created|updated)$/.test(statuses[0]);
}

function handleToolBatch(input, state) {
  const calls = Array.isArray(input.tool_calls) ? input.tool_calls : [];
  let activities = 0;
  let writes = 0;
  let saved = false;

  for (const call of calls) {
    const toolName = String(call && call.tool_name ? call.tool_name : "");
    if (checkpointSaved(call)) {
      saved = true;
      continue;
    }
    if (WORK_TOOLS.has(toolName)) {
      activities += 1;
    }
    if (WRITE_TOOLS.has(toolName)) {
      writes += 1;
    }
  }

  if (saved) {
    clearCheckpoint(state);
  }
  if (activities > 0) {
    markActivity(state, {
      count: activities,
      writes,
      reason: writes > 0 ? "workspace_changed" : "work_activity"
    });
  }
}

function checkpointDue(state) {
  if (!state.dirty) {
    return false;
  }
  if (state.forceCheckpoint) {
    return true;
  }

  const now = Date.now();
  const elapsed = state.firstDirtyAt ? now - state.firstDirtyAt : 0;
  const sustainedWork =
    state.writeCount > 0 &&
    (state.activityCount >= ACTIVITY_THRESHOLD || elapsed >= CHECKPOINT_INTERVAL_MS);
  return sustainedWork;
}

function onStop(input, state) {
  if (input.agent_id || input.stop_hook_active) {
    return null;
  }
  if ((input.background_tasks || []).length || (input.session_crons || []).length) {
    return null;
  }
  if (!checkpointDue(state)) {
    return null;
  }

  const now = Date.now();
  if (
    !state.forceCheckpoint &&
    state.lastPromptAt &&
    now - state.lastPromptAt < PROMPT_COOLDOWN_MS
  ) {
    return null;
  }
  state.lastPromptAt = now;
  state.forceCheckpoint = false;

  const reasons = state.reasons.length
    ? state.reasons.join(", ")
    : "material project progress";
  return {
    hookSpecificOutput: {
      hookEventName: "Stop",
      additionalContext:
        `XMemo checkpoint due (${reasons}). Before ending, determine whether the ` +
        "verified project state materially changed. If it did, use the plugin-owned " +
        "XMemo update_state using the project's existing state slot (default active_task) " +
        "to replace the scoped working checkpoint with the objective, verified status " +
        "and evidence, completed work, settled decisions, blocker, relevant artifacts, " +
        "provenance, and one exact next action. Use record_event only for a significant " +
        "milestone or handoff. Do not save raw transcripts, secrets, speculative claims, " +
        "or verbose reasoning. If no durable change exists or XMemo is unavailable, say " +
        "so briefly and do not fabricate a successful save. If the plugin-owned " +
        "connection is not authorized, ask the user to authorize it through /mcp. " +
        "Saving through the claude.ai Connector does not clear this reminder."
    }
  };
}

function recordRecovery(input, state) {
  if (!state.dirty) {
    return;
  }
  const rawReason = String(input.reason || input.error || "unspecified");
  const safeReason = /^[a-z0-9_-]{1,64}$/i.test(rawReason)
    ? rawReason
    : "unspecified";
  state.recovery = {
    at: Date.now(),
    event: String(input.hook_event_name || "unknown"),
    reason: safeReason,
    activityCount: state.activityCount,
    writeCount: state.writeCount,
    reasons: state.reasons.slice(-8)
  };
}

function onSessionStart(state) {
  if (!state.recovery && !state.dirty) {
    return null;
  }
  const reasons = (state.recovery && state.recovery.reasons.length
    ? state.recovery.reasons
    : state.reasons).length
    ? (state.recovery && state.recovery.reasons.length
        ? state.recovery.reasons
        : state.reasons).join(", ")
    : "unfinished project activity";
  return {
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext:
        `XMemo's local checkpoint guard detected an interrupted or unsaved prior session ` +
        `for this project (${reasons}). After the XMemo MCP connection is available, ` +
        "recover the latest verified checkpoint with the resume-work workflow, reconcile " +
        "it against the live workspace, and preserve only verified new progress. The guard " +
        "stored no transcript or message content."
    }
  };
}

function main() {
  const input = readInput();
  if (!input || typeof input.hook_event_name !== "string") {
    return;
  }
  const location = stateLocation(input);
  if (!location) {
    return;
  }
  const state = loadState(location);
  let output = null;

  switch (input.hook_event_name) {
    case "PostToolBatch":
      handleToolBatch(input, state);
      break;
    case "TaskCompleted":
      markActivity(state, { reason: "task_completed", force: true });
      break;
    case "PreCompact":
      if (state.dirty) {
        markActivity(state, { count: 0, reason: "context_compaction", force: true });
      }
      break;
    case "Stop":
      output = onStop(input, state);
      break;
    case "StopFailure":
    case "SessionEnd":
      recordRecovery(input, state);
      break;
    case "SessionStart":
      output = onSessionStart(state);
      break;
    default:
      return;
  }

  saveState(location, state);
  if (output) {
    process.stdout.write(JSON.stringify(output));
  }
}

try {
  main();
} catch {
  // Checkpoint automation is fail-open: it must never block Claude Code work.
  process.exitCode = 0;
}
