# XMemo checkpoint continuity without command hooks

- Status: design spike, not for release. DevFlow task `INBOX-20261106-109054`.
- Branch: `spike/checkpoint-without-command-hooks`, cut from `main` at `9d846b6` (1.0.10).
- Author: pc-claude (executor), 2026-11-06. Claude Code used for experiments: 2.1.318.

## 1. Problem

The Anthropic Directory holds 1.0.10 (`claude-directory` `2257766`) for one finding: "Hooks of type 'command' accepted only from Verified organizations". The live listing is 1.0.4 (`d4312db`), whose `hooks/hooks.json` has the same 7 command hooks; it was accepted before this rule applied.

The Owner rejected a 1.0.11 that simply drops the Hook, because it would be worse than 1.0.4. This note looks for a design that keeps the checkpoint reminder, or something close to it, using only mechanisms an unverified publisher can ship.

What the public documentation says about the rule:

- The pre-submission checklist has no rule that ties a hook type to publisher verification. Its only hook-type rule is a validity check: "use only the hook events and hook types in the hooks reference, and an `https://` URL on each HTTP hook", result Blocks ("hooks.json is invalid"). Source: https://claude.com/docs/plugins/pre-submission-checklist, "Hooks, skills, commands, and agents".
- "Verified" is defined only for connectors, and there is "no separate application for the Verified label". Sources: https://claude.com/docs/connectors/verification.md, "Connector labels > Verified" and "List your own connector"; https://claude.com/docs/directory/publish.md, "Prepare for review".

So the rule is known only from the Directory finding itself (status: **reported**). Whether other hook types are accepted from an unverified publisher is **not documented**.

## 2. Baseline: what the command hook does

`scripts/checkpoint-hook.js` at `9d846b6` runs on 7 events and keeps per-project state under `CLAUDE_PLUGIN_DATA`:

| Capability | Event | Code at `9d846b6` |
|---|---|---|
| Recover an interrupted or unsaved session | SessionStart | `onSessionStart`, lines 282-304 |
| Count work and writes; clear on a verified `update_state` receipt | PostToolBatch | `handleToolBatch` 172-202, `checkpointSaved` 136-170 |
| Force a checkpoint at task completion | TaskCompleted | `main`, lines 322-324 |
| Force a checkpoint before compaction | PreCompact | `main`, lines 325-329 |
| Remind once after sustained work (6 actions or 15 minutes with a write), 10-minute cooldown | Stop | `checkpointDue` 204-218, `onStop` 220-262 |
| Mark an interruption for the next session | StopFailure, SessionEnd | `recordRecovery` 264-280 |

1.0.4 had the same structure but cleared the reminder on any server's `update_state` call (`/^mcp__.+__update_state$/`, `git show v1.0.4:scripts/checkpoint-hook.js`), without checking the receipt. 1.0.10 accepts only a successful receipt from `mcp__plugin_xmemo_xmemo__update_state`.

## 3. Platform facts

All from the hooks reference, https://code.claude.com/docs/en/hooks, unless marked otherwise.

- **Hook types.** `command`, `http`, `mcp_tool`, `prompt`, `agent` ("Hook handler fields").
- **Prompt hooks** "send a prompt to a Claude model for single-turn evaluation" ("Hook handler fields"). They support PermissionDenied, PostToolBatch, PostToolUse, PostToolUseFailure, PreToolUse, Stop, SubagentStop, TaskCompleted, TaskCreated, TeammateIdle, UserPromptExpansion and UserPromptSubmit. They are not supported on SessionStart, PreCompact, StopFailure or SessionEnd ("Prompt-based hooks"). Default timeout 30 seconds. `$ARGUMENTS` is replaced by the hook input JSON ("Prompt hook configuration").
- **Prompt hook response.** `{"ok": true|false, "reason": "...", "impossible": true|false}`. On Stop, `ok: false` means "the reason is fed back to Claude as its next instruction and the turn continues", unless `impossible` is true ("Response schema").
- **Stop input.** Common fields plus `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons`; `agent_id` appears only in subagent contexts. `stop_hook_active` is "`true` when Claude Code is already continuing as a result of a stop hook". Claude Code also "applies an 8-consecutive-continuation cap". Stop "does not run if the stoppage occurred due to a user interrupt" ("Stop", "Stop input", "Common input fields").
- **Agent hooks** are "experimental. Behavior and configuration may change", spawn a subagent with tools such as Read, Grep and Glob, up to 50 turns, default timeout 60 seconds ("Agent-based hooks").
- **`mcp_tool` hooks** call a tool on a configured MCP server, with `server` set to `plugin:<plugin-name>:<server-name>` and `input` values that support `${path}` substitution from the hook input. On SessionStart "at launch, including with `--continue` or `--resume`", they fire before MCP servers are available, so they are skipped. A tool error "produces a non-blocking error and execution continues", and the hook "never starts an OAuth flow" ("MCP tool hook fields").
- **Failure semantics of prompt hooks.** What happens when the model call fails or times out is not documented. The general rule is that on most events "when a hook fails or times out, Claude Code still carries out the action" ("Block the action when a hook fails").
- **Directory policy.** MCP servers and Skills must not "direct Claude to dynamically pull behavioral instructions from external sources" (2.F) and must not "intentionally call or coerce Claude into calling other external software" unless "requested and intended by a user" (2.D). Section 1.G forbids undisclosed "changes to Claude's behavior across sessions". Source: https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy.

## 4. Local experiments

The experiments ran headless Claude Code 2.1.318 against this branch's working tree:

```text
claude -p "<task>" --plugin-dir <this repo> --setting-sources project --disallowedTools "mcp__*" \
  --permission-mode acceptEdits --output-format stream-json --verbose --include-hook-events \
  --debug-file <log> [--allowedTools "PowerShell(python -m unittest*)" "PowerShell(git *)"]
```

- MCP tools were disallowed, so no run could read or write XMemo.
- The test project was a throwaway git repository, `invoice-calc`, in the session scratchpad, with a failing `add()` test.

| Run | Turn | Hook decision (debug log) | Outcome |
|---|---|---|---|
| E2 | "What is 17 times 3?" | `ok: true`, "only answers a simple arithmetic question" | Ended, 1 turn |
| E1a | Create `hello.txt` | `ok: true`, "a routine small step" | Ended |
| E1b | Create and read back `greet.py` | `ok: true`, "a trivial … scratch-file exercise" | Ended |
| E1d | Fix `add()`, run tests (`OK`), commit `bc45fab` | 1st Stop `ok: false` with the exact reason text; 2nd Stop `ok: true`, "stop_hook_active is true" | Claude continued once, said XMemo is not authorized, suggested `/mcp`, ended with `XMemo checkpoint: unavailable` |
| E3b | Same fix and commit, reply already ends with `XMemo checkpoint: unavailable` | `ok: true`, "has a line that starts with 'XMemo checkpoint:'" | Ended without a continuation |

`claude plugin validate . --strict` (2.1.318) accepts the prompt hook, including the top-level `description` and `statusMessage` fields.

Facts observed in the debug logs, which the hooks reference does not state:

1. **The hook model sees the conversation.** Claude Code wraps the prompt as "Based on the conversation transcript above, has the following stopping condition been satisfied? Answer based on transcript evidence only. Condition: <prompt>" and logs "Querying model with 15 … 37 messages". The model can therefore see the turn's tool calls, not only `last_assistant_message`. This matters for privacy (section 5, C1) and is version-specific.
2. **Model and latency.** The call is dispatched to `claude-haiku-5-5` (`source=hook_prompt`). Each Stop added 0.9 to 2.9 seconds.
3. **Feedback echoes the prompt.** On `ok: false`, Claude receives "Stop hook feedback: [<the whole prompt>]: <reason>", 2,404 characters here. The prompt length is paid again on every block.
4. **Judgment drift.** In one early run (E3, a dirty work tree), the hook cited a status line that appeared only in the user's request. Because the model sees the conversation, it can attribute text to the wrong message.

## 5. Candidates

### C1. Prompt-based Stop hook (prototyped)

**Mechanism.** One `type: "prompt"` Stop hook. It returns `ok: true` when any of these holds:

- `stop_hook_active` is true;
- `agent_id` is present;
- `background_tasks` or `session_crons` is non-empty;
- the final message has an `XMemo checkpoint:` line;
- the turn only answered, explained, explored or planned;
- the model is unsure.

It returns `ok: false` with a fixed reason only when the final message reports a completed, material milestone. A PreCompact variant is not possible, because PreCompact does not accept prompt hooks (section 3).

**Can it tell "meaningful work since the last `update_state`"?**
- From the documented input alone, only from `last_assistant_message`. It has no memory across turns, so there is no cooldown and no cumulative threshold.
- In 2.1.318 it also sees the conversation (section 4, fact 1), which would allow it to look for a successful `update_state` call. That behaviour is undocumented, so the prototype relies on the status line instead.

**Lost compared with 1.0.4:**
- recovery at SessionStart;
- the PreCompact checkpoint;
- the interruption marker on StopFailure and SessionEnd;
- the activity and time thresholds and the 10-minute cooldown;
- detection of a save by observing the tool call; it now relies on the status line, which Claude could write without saving.

1.0.10's receipt verification is lost too. 1.0.4 never had it.

**Gained:**
- no local program, no Node.js requirement, no local state;
- a semantic judgment of "milestone" instead of tool counting;
- one rule shared with the Skills (the status line).

**Directory acceptance: unknown.** The type is in the hooks reference, so it passes the validity rule. Whether the policy review accepts prompt hooks from an unverified publisher can only be learned from the developer portal (section 9).

**Privacy.** No data goes to XMemo or a third party. The extra model call is made by Claude Code under the user's own Claude account. In 2.1.318 it includes the conversation, not just the final message. Nothing is stored locally.

**Cost and risks:**
- one Haiku call on every main-agent Stop, with input that grows with the conversation;
- 1 to 3 seconds added per turn end;
- on a block, about 2.4 KB of echoed prompt plus one extra Claude turn.

False positives seen: none in five runs; the model was conservative, judging toy work routine. False negatives seen:
- a real but small fix is judged routine, by design;
- a fabricated status line suppresses the check.

Failure semantics on timeout are undocumented.

**Recommendation:** adopt, together with C3.

### C2. Agent-based Stop hook

**Mechanism.** `type: "agent"` on Stop. It can read the transcript file at `transcript_path` and verify an actual successful `update_state` receipt, which would restore receipt checking.

**Lost compared with 1.0.4:** the same event coverage as C1, since agent hooks support the same events. It is closer than C1 on save detection.

**Directory acceptance: unknown, at higher risk.** The type is documented as experimental, and an agent that reads local files may be judged like a command hook.

**Privacy.** It reads the whole local transcript file on every Stop.

**Cost.** A multi-turn subagent, up to 50 turns and 60 seconds by default, on every Stop. That is far heavier than C1.

**Recommendation:** do not adopt now. Revisit if agent hooks leave experimental status and C1's status-line trust proves insufficient.

### C3. Skill discipline and an explicit checkpoint Skill (prototyped)

**Mechanism.**
- `memory-steward` gains a "Checkpoint status line" rule: after a milestone turn, decide and end with `XMemo checkpoint: saved`, `not needed`, or `unavailable`. `saved` is allowed only after a successful plugin-connection receipt.
- A new `/xmemo:checkpoint` Skill saves one verified checkpoint on demand.

**Lost compared with 1.0.4:** all automatic triggers. It depends on the Skill being loaded and followed.

**Directory acceptance: known.** Skill-only plugins are accepted ("passes with a note", checklist "Repository and folder layout"). The rule is user-visible and limited to the plugin's own tools, so it stays within policy 2.D.

**Privacy.** None beyond normal Skill use.

**Recommendation:** adopt. It is the primary mechanism, and C1 is its backstop.

### C4. Server-side nudge (description only)

**Mechanism.** The XMemo MCP server reminds the model, for example through server `instructions` or a short trailing note on write-tool responses ("working state last saved 3 h ago for this project").

**Lost compared with 1.0.4:** turn-end and lifecycle triggers. The model sees the nudge only when it already calls an XMemo tool.

**Directory acceptance: unknown, and a policy risk.** It is close to 2.F (behavioural instructions from an external source) and needs careful wording to stay informational.

**Privacy.** No new data leaves the client. The server already holds the state.

**Recommendation:** optional follow-up in the memory-os repository. It is out of scope here and needs that repository's own review.

### C5. `mcp_tool` hooks (not in the brief; evaluated for completeness)

**Mechanism.** Hooks that call the plugin's own XMemo tool, for example on Stop or PreCompact.

**Lost compared with 1.0.4:** SessionStart recovery at launch, because the hooks are skipped before MCP servers connect (section 3). When the plugin connection is not authorized, the hook only produces a non-blocking error.

**Directory acceptance: unknown.**

**Privacy.** Each Stop would send templated hook input, such as `cwd` or `last_assistant_message`, to xmemo.dev. That conflicts with this task's ban on sending session data to xmemo.dev, and it needs a new server tool.

**Recommendation:** reject for now.

### Rejected outright

- **An installer** (a Skill or command) that writes command hooks into the user's `~/.claude/settings.json` to get around the Directory rule. This circumvents the rule's intent and changes Claude's behaviour across all projects (policy 1.C, 1.G; the hooks reference "Configuration" table gives that scope as "All your projects"). It is also out of scope.
- **`http` hooks** that send session data to xmemo.dev. They are out of scope, a privacy regression, and they need the user's `allowedHttpHookUrls`.

## 6. Recommendation

Ship C3 as the primary mechanism with the C1 prompt Stop hook as a backstop. Keep C4 as a possible later server-side improvement.

## 7. Prototype on this branch

| File | Change |
|---|---|
| `hooks/hooks.json` | 7 command hooks → 1 prompt Stop hook (30 s timeout, default model) |
| `scripts/checkpoint-hook.js` | removed |
| `scripts/test-checkpoint-hook.js` | rewritten as contract tests: the shipped config passes; 17 mutations, including any command, agent, http or mcp_tool hook, a missing loop or subagent guard, transcript access and Connector routing, must fail |
| `scripts/validate-package.py` | accepts only one prompt Stop hook with the guard markers; rejects any `"type": "command"`; Skill suite of 10 |
| `skills/checkpoint/SKILL.md` | new `/xmemo:checkpoint` |
| `skills/memory-steward/SKILL.md` | "Checkpoint status line" rule |
| README, PRIVACY, SECURITY, CHANGELOG | describe the prompt hook, its model call and the lost capabilities |
| `.github/claude-directory/release-policy.json` | excludes `docs/**`; keeps the `scripts/checkpoint-hook.js` include so the golden baseline (`5d0d280`) still rebuilds |
| `.github/workflows/*.yml` | the artifact test steps pass `XMEMO_PLUGIN_ROOT` instead of the removed script path |

The plugin version stays 1.0.10. A release would need 1.0.11 or 1.1.0 and the version and change gates.

## 8. Open questions

1. Does the Directory accept a prompt hook from an unverified publisher? Only the portal can tell (section 9).
2. Does Cowork run plugin prompt hooks the way Claude Code does? This was not tested.
3. The conversation visibility of prompt hooks is undocumented and may change. The design must stay correct with or without it, which the status line provides.
4. Shortening the prompt would reduce the echoed feedback cost. Not attempted in this spike.

## 9. Comparison with 1.0.4 and how to validate

**Decision summary.** 1.0.4 remembers activity locally across a whole project and triggers a checkpoint mechanically: on task completion, before compaction, after sustained work, and at the start of the session after an interruption. It treats any `update_state` call as a save. It needs Node.js and a command hook, which the Directory now accepts only from verified organizations.

The spike keeps the main promise, that a milestone turn does not end without Claude deciding whether to checkpoint. It does so with:
- a Skill rule that every host can follow;
- a single prompt Stop check that runs no local code, keeps no local state and sends nothing to XMemo.

It gives up the lifecycle coverage: session-start recovery, the pre-compaction and failure markers, and the time and activity thresholds. It also adds an extra Haiku call on every turn end. Coverage is clearly lower than 1.0.4 on long, interrupted sessions, and about the same on ordinary milestone turns. Whether the Directory accepts it is unknown until the portal check below.

**Owner steps in the developer portal.** These follow https://claude.com/docs/plugins/submit.md, "Submit a plugin" step 2, and the checklist's "Validate in the developer portal". Do not change the tracked branch of the live submission: "Change the tracked branch or tag" on its Settings tab changes what that submission tracks.

1. Start a new plugin submission in the developer portal.
2. On the Source step, enter repository `yonro/xmemo-claude-plugin`, leave the plugin path empty, and set "Branch or tag" to `spike/checkpoint-without-command-hooks`.
3. Select **Validate**. "A validation result applies to one commit", so note the commit shown.
4. Read the hook findings. If no "Hooks of type 'command'" finding appears and no prompt-hook finding replaces it, the mechanism is acceptable at validation level.
5. Leave the draft unsubmitted.

The documentation does not say whether this Validate step also runs the policy review that raised the finding on 1.0.10. If it does not, the answer is known only after a real version is submitted.
