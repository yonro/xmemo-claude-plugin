# Example prompts

These synthetic prompts exercise each professional workflow without assuming
that XMemo writes happen automatically.

## Brainstorm

- `/xmemo:brainstorm` Explore three architecture directions for offline-first project memory. Recall our saved constraints, compare trade-offs and experiments, and keep every option tentative until I approve one.
- Brainstorm a launch strategy with XMemo. Include prior failed approaches, challenge the strongest options, and ask me which direction to preserve.

## Review a plan

- `/xmemo:review-plan` Review this implementation plan against our saved decisions. Return a formal verdict, blocking findings, required changes, risks, missing evidence, and an acceptance gate.
- Review a plan produced by another agent. Preserve its provenance, but do not treat its claims as verified implementation.

## Design a project and execution plan

- `/xmemo:plan-project` Inspect this repository and design `PROJECT_PLAN.md` plus `EXECUTION_PLAN.md`. Ground them in our saved XMemo decisions, separate draft from approved work, and give every phase a verification command, acceptance gate, owner, rollback path, and exact next action.
- Turn the approved brainstorm into an implementation plan without treating planned work as completed. Reuse the repository's existing planning location and conventions.

## Audit progress

- `/xmemo:audit-progress` Audit this agent's progress report against the approved plan, current files, tests, and latest checkpoint. Classify each claim as verified, partial, claimed, stale, conflicting, or blocked.
- Reconcile the conflicting completion reports from Claude and Codex, then identify the exact next action supported by evidence.
- Write a development progress audit Markdown that compares the approved execution plan with current files, commits, tests, review status, and deployment evidence.

## Distill a session

- `/xmemo:distill-session` Turn this conversation into durable XMemo outcomes. Preview the decisions, stable constraints, TODOs, unresolved choices, checkpoint, and skipped content before saving.
- Summarize the important points from this session without storing the raw transcript or tentative brainstorms as facts.

## Resume work

- `/xmemo:resume-work` Bring me up to speed on this project. Reconcile the saved checkpoint with the live workspace and return a Resume Brief with one exact next action.
- Recover the work another agent paused yesterday, show what is verified versus remembered, and continue without repeating completed work.

## Cross-agent handoff

- `/xmemo:handoff-work` Prepare a handoff for Codex with objective, artifacts, verified state, completed work, decisions, evidence, constraints, remaining work, blocker, exact next action, and review gate.
- Receive this Kiro handoff, compare it with XMemo and current evidence, and respond with accepted, accepted with gaps, blocked, or rejected.

## General stewardship and lifecycle

- `/xmemo:memory-steward` Recall what we decided about the release architecture and explain any conflicting or outdated memories.
- Save a restart-ready checkpoint for this task, including completed evidence, work not to repeat, and one exact next action.
- Find the exact memory about our deprecated deployment process and soft-delete it.
- Restore the memory I just soft-deleted.
