---
name: resume-work
description: Resume a project or unfinished task from XMemo by recovering the latest verified checkpoint, relevant decisions, TODOs, blockers, and exact next action. Use at the start of a new Claude session, after an interruption, or when continuing work previously handled by another compatible agent. Reconcile saved state with current evidence before acting.
---

# Resume Work with XMemo

Reconstruct actionable continuity without replaying chat history. Follow **identify → recover → reconcile → brief → continue → checkpoint**.

## 1. Identify the work precisely

Establish the project, task, artifact, branch, environment, or authorized scope. If several candidates match, present the candidates instead of guessing.

## 2. Recover the minimum complete context

Prefer `get_project_context` for a known project and `recall_context` for a task-oriented pack. Add `search_memory`, pending decisions, or `todo` reads only when needed to close a specific gap. Recover:

- objective and acceptance criteria;
- latest verified checkpoint;
- completed work not to repeat;
- settled and pending decisions;
- relevant constraints and artifacts;
- open actions, blocker, and exact next action.

## 3. Reconcile before trusting

Compare the recovered state with the live workspace, newer evidence, and the user's current correction. Mark saved statements as current, stale, conflicting, or unverified. Never continue from a checkpoint whose identity or scope is uncertain.

## 4. Produce a deterministic Resume Brief

Return:

1. **Objective**
2. **Verified current state**
3. **Completed work not to repeat**
4. **Active decisions and constraints**
5. **Open TODOs**
6. **Blocker or required input**
7. **Exact next action**
8. **Evidence and artifact references**

Clearly separate remembered context from freshly verified evidence.

## 5. Continue from the next action

If the user asked to continue and the action is safe and in scope, execute it without repeating completed work. If blocked, name the missing authority, evidence, or external change.

## 6. Refresh continuity at a material checkpoint

Use `update_state` after verified progress, a new blocker, or a meaningful pause. Use `record_event` only for a significant milestone or transfer, `todo` for concrete future actions, and `remember` for durable knowledge. Do not create a checkpoint every turn.

Resume restores useful context, not the original Claude conversation. Return a receipt for any XMemo updates.

Read `../memory-steward/references/workflows.md`, `../memory-steward/references/memory-policy.md`, and `../memory-steward/references/tool-routing.md` for the complete Resume Brief and checkpoint contracts.
