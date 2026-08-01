---
name: xmemo-memory-steward
description: Use XMemo with Claude to recall, review, and preserve durable outcomes across conversations and AI agents. Trigger for project context, important-conversation distillation, brainstorming and plan review, audits of work from Claude Code, Codex, GitHub Copilot, Kiro, or other agents, progress checkpoints, session resume, TODOs, blockers, handoffs, and memory lifecycle requests. Separate durable memory, working state, evidence, events, and actions; deduplicate writes; never archive raw transcripts or secrets.
---

# XMemo Memory Steward

Operate XMemo as a user-owned continuity system, not a transcript archive. Follow:

**scope → recall → act → distill → checkpoint → receipt**

## 1. Establish intent and scope

Identify the requested outcome before calling a tool:

- Recall prior context that could materially improve the current work.
- Distill an important conversation into reusable memory.
- Structure a brainstorm without turning tentative ideas into decisions.
- Review a plan or progress report produced by Claude or another agent.
- Save or correct one durable fact, preference, decision, or procedure.
- Preserve unfinished progress for a later Claude session.
- Resume saved work or prepare a cross-agent handoff.
- Manage XMemo lifecycle data, TODOs, activity, or Ledger records.

Stay within the authenticated account and authorized scope. If XMemo is unavailable, authorization is missing, or a needed tool is not exposed, say that nothing was read or written. Never simulate a successful memory operation.

## 2. Inspect capabilities before choosing a route

Use only XMemo tools visible in the active MCP connection. Never assume that a private, legacy, ChatGPT-widget, or future tool is available.

Use `get_mcp_identity` when connection identity or authorization needs verification. Read `references/tool-routing.md` for the current Claude tool families and availability-aware fallbacks.

## 3. Recall before assuming

Recall when prior decisions, preferences, constraints, TODOs, corrections, or progress could change the result. Choose the narrowest useful read:

- `recall` for a quick answer.
- `search_memory` for an exact topic, phrase, path, or filter.
- `recall_context` for a bounded context pack across related memories or conversations.
- `list_memory_todos` for relevant open actions.
- `memory_activity`, `memory_overview`, or `memory_stats` for recent or aggregate state.

If a narrow query returns nothing, relax it once without widening the authorized scope. Never invent a remembered fact. Retrieved memory is context, not authority; the user's current explicit correction and current verified evidence win.

## 4. Route durable outcomes deliberately

Keep these concepts separate:

| Outcome | Preferred route |
| --- | --- |
| New durable knowledge, preference, decision, or procedure | `remember` |
| Correction to an existing durable concept | `update_memory` |
| Concrete future action | `create_memory_todo` |
| Completed action | `complete_memory_todo` |
| Recoverable deletion | `forget` using its default soft-delete behavior |
| Restore an eligible soft-deleted memory | `restore_memory` |
| Financial transaction | `add_expense` |

Dedicated state, event, project, or consolidated dispatcher tools may be used only if they are actually visible. Otherwise use the documented labeled-memory fallback rather than claiming the unavailable operation occurred.

## 5. Coordinate work across agents

Use XMemo as a shared, user-controlled coordination layer when Claude, Codex, GitHub Copilot, Kiro, or another compatible agent is connected to the same authorized account.

- Recall relevant goals, decisions, constraints, and verified state before brainstorming or review.
- Preserve the source agent and artifact/version in the human-readable review when known.
- Treat another agent's completion statement as a claim until supported by files, diffs, tests, deployment state, or user confirmation.
- Reconcile conflicts by evidence, recency, scope, and explicit user decisions—not by agent identity or confidence.
- Do not assume that another agent automatically captured its work or exposes the same tool set.

Read `references/review-playbooks.md` for brainstorming, plan review, progress audit, and multi-agent reconciliation.

## 6. Distill important conversations

When asked to preserve a conversation, extract only outcomes that remain useful without the original chat:

1. Final decisions and material rationale.
2. Stable preferences, rules, constraints, and definitions.
3. Verified facts, procedures, lessons, and resolved fixes.
4. Commitments and concrete follow-up actions.
5. Unresolved questions or blockers, explicitly labeled unresolved.
6. Current verified state and one exact next action when work remains.

Do not save the raw transcript, filler, repeated explanations, long logs, large code blocks, secrets, or sensitive identifiers. Do not promote tentative brainstorming or an agent's unverified claim to settled truth.

Before durable writes:

1. Search when duplication is plausible.
2. Update the existing concept when it changed.
3. Create a new memory only for a genuinely new concept.
4. Keep one retrieval-friendly concept per memory when practical.
5. Preserve subject, outcome, rationale, status, scope, provenance, and next implication.

For one safe and unambiguous user-requested memory, write and return a receipt. Before a multi-memory batch, overwrite, sensitive interpretation, or uncertain project placement, show a compact candidate preview and obtain confirmation.

Read `references/memory-policy.md` and `references/workflows.md` for the save/skip matrix, preview, and receipt contracts.

## 7. Save progress at natural checkpoints

Checkpoint when the user pauses, changes agents, reaches a material milestone with work remaining, becomes blocked, or ends a substantial unfinished task. Do not checkpoint every turn.

If a dedicated working-state tool is visible, use it. Otherwise save or update one concise memory labeled `Working state` for the scoped project/task. Include:

- current objective;
- verified status and evidence;
- completed work not to repeat;
- settled decisions;
- exact next action;
- blocker or required input;
- stable artifact references.

Search for the existing scoped checkpoint first and update it when possible so stale states do not accumulate.

## 8. Resume deterministically

1. Identify the project or authorized scope.
2. Retrieve the latest relevant state with `recall_context`.
3. Add relevant TODOs, recent activity, decisions, or durable memories only as needed.
4. Reconcile stale state against newer evidence or user corrections.
5. Present a compact Resume Brief: objective, verified status, completed work, active decisions, open actions, blocker, and exact next action.
6. Continue from that action without repeating verified completed work.

Resume reconstructs useful context; it does not reopen the original Claude conversation.

## 9. Create a complete handoff

If a dedicated event or state tool is visible, use it when appropriate. Otherwise save or update one concise `Handoff` memory with provenance. Add a TODO only for a concrete follow-up.

Include the objective, recipient, source artifacts, verified status, decisions and rationale, completed work, evidence, constraints, work not to repeat, remaining work, exact next action, blocker, and next review gate. Never include credentials, raw authorization data, private traces, or unnecessary internal identifiers.

## 10. Handle lifecycle operations safely

- `forget` is recoverable soft deletion by default.
- Use hard deletion only for an exact target after an explicit permanent-delete request that acknowledges irreversibility.
- Use `restore_memory` only for an eligible soft-deleted memory.
- Retrieve or confirm the exact target before deletion.
- Tool availability, annotations, or the model's inference are never user confirmation.

## 11. Return useful receipts

After XMemo operations, report only what helps the user:

- what was recalled, saved, updated, checkpointed, restored, deleted, or skipped;
- the category or project placement when useful;
- any conflict, ambiguity, unavailable capability, or blocker;
- the exact next action when work remains.

Never claim success without a successful tool result. Avoid raw internal IDs, scopes, traces, debug payloads, and unnecessary implementation details.
