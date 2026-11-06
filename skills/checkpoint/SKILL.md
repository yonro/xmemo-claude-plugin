---
name: checkpoint
description: Save one verified XMemo working checkpoint for the current project now, replacing the previous one, so the next session or agent can continue from an exact next action. Use when the user asks to checkpoint, save progress, save where we are, or prepare to stop, switch machines, or hand over; when a material milestone was just completed; or when Claude Code asks for an XMemo checkpoint check at the end of a turn. Never saves raw transcripts, secrets, or unverified claims.
---

# XMemo Checkpoint

Save the verified working state of one scope in one `update_state` call. Follow **scope → evidence → compose → save → status**.

## 1. Scope

Identify the project, repository, or task the checkpoint belongs to. Reuse the project's existing state slot; use the default `active_task` when none exists. Check whether XMemo tools are available on the plugin's own connection first. If they are not, say that nothing was saved, suggest `/mcp` in Claude Code or the plugin's Connectors tab in the Claude app or Cowork, and end with `XMemo checkpoint: unavailable`.

## 2. Gather evidence

Use only what this session verified: commands that ran and their results, files changed, tests, commits, pull requests, releases, and decisions the user settled. Read the existing checkpoint with `search_memory` (use `time_order=desc` where supported) so the new one replaces it instead of stacking a second one.

If nothing durable changed since that checkpoint, do not write. Say so and end with `XMemo checkpoint: not needed`.

## 3. Compose

Write a compact checkpoint with:

- current objective;
- verified status and evidence;
- completed work not to repeat;
- settled decisions;
- blocker or required input, if any;
- stable artifact references (paths, branch, commit, pull request, run);
- one exact next action another session or agent can execute.

Leave out raw transcripts, secrets, tokens, credentials, personal identifiers, speculation, and verbose reasoning. Mark anything unverified as unverified, or leave it out.

## 4. Save

Call `update_state` once on the plugin's own XMemo connection. Do not use a same-named tool on any other server. When the user invoked this Skill directly, save without a further question; otherwise follow the save rules in `../memory-steward/SKILL.md`. Use `record_event` only for a significant milestone or handoff, as `/xmemo:handoff-work` describes.

## 5. Report status

Return a two-line receipt: what the checkpoint now says the next action is, and whether an older checkpoint was replaced. End with exactly one line:

- `XMemo checkpoint: saved` only after `update_state` returned a successful receipt;
- `XMemo checkpoint: not needed` when nothing durable changed;
- `XMemo checkpoint: unavailable` when the plugin connection is not authorized.

Never claim a save that did not succeed. Read `../memory-steward/references/memory-policy.md` for what may be saved and `../memory-steward/references/tool-routing.md` for tool routing.
