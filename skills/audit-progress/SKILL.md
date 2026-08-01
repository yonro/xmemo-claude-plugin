---
name: audit-progress
description: Audit implementation or project progress against the approved XMemo plan, checkpoint, decisions, and current evidence. Use when Claude must verify another agent's completion report, reconcile multi-agent claims, identify drift or blockers, and determine the exact next action. Never promote a claim to verified state without evidence.
---

# Audit Progress with XMemo

Measure reality against the approved baseline. Follow **baseline → claims → evidence → reconcile → verdict → checkpoint**.

## 1. Recover the governing baseline

Use `recall_context`, `get_project_context`, `search_memory`, and relevant `todo` reads to recover the approved plan, acceptance criteria, settled decisions, last verified checkpoint, and known blockers. State which artifact or memory is the baseline and flag ambiguity before auditing.

## 2. Normalize the progress claims

Break the report into atomic claims: changed, tested, deployed, reviewed, documented, blocked, or deferred. Preserve the source agent and artifact/version when known, but do not treat source identity as evidence.

## 3. Verify against current evidence

Inspect the live artifacts available to Claude: files, diffs, commits, tests, logs, deployments, or explicit user confirmation. Classify each claim as:

- **verified** — direct evidence satisfies the criterion;
- **partial** — some evidence exists, but the criterion is incomplete;
- **claimed** — asserted without adequate evidence;
- **stale** — once true but superseded by newer state;
- **conflicting** — sources disagree and evidence does not resolve them;
- **blocked** — a named dependency prevents verification or completion.

Absence of evidence is not proof of failure. A passing local test is not proof of deployment. A commit is not proof of runtime behavior.

## 4. Reconcile drift and conflicts

Resolve disagreement by exact scope, recency, provenance, and verifiable evidence. Current explicit user decisions override older memories. If a saved baseline is wrong, propose a correction; do not silently rewrite history.

## 5. Return a formal audit

Use this structure:

1. **Audit scope and baseline**
2. **Verdict** — `on_track`, `at_risk`, `blocked`, or `not_verified`
3. **Claim matrix** — claim, status, evidence, gap
4. **Plan drift**
5. **Risks and blockers**
6. **Acceptance gaps**
7. **Exact next action**

When the user requests a durable review artifact, write the report in the
repository's established documentation location using
`assets/progress-audit-template.md`. Keep the baseline, evidence, status, gaps,
and exact next action independently reviewable. Do not create or overwrite a
file when the request is report-only.

## 6. Update XMemo only from reconciled truth

With user authorization or an active save workflow:

- replace the working checkpoint with verified status via `update_state`;
- complete or update TODOs only when their conditions are met;
- record a material milestone or handoff via `record_event`;
- correct a durable claim via `update_memory`;
- preserve a new durable lesson via `remember`.

Never save the audit narrative as a raw transcript. Do not mark completion from an agent's confidence alone. Return a receipt that distinguishes verified updates from unresolved claims.

Read `../memory-steward/references/review-playbooks.md`, `../memory-steward/references/workflows.md`, and `../memory-steward/references/tool-routing.md` for detailed review and routing contracts. Use `assets/progress-audit-template.md` for a requested Markdown audit artifact.
