---
name: plan-project
description: Design or revise an evidence-gated project plan and executable Markdown plan using XMemo context and the live workspace. Use when starting a project, turning goals or a brainstorm into PROJECT_PLAN.md and EXECUTION_PLAN.md, decomposing work into phases and acceptance gates, assigning multi-agent ownership, or correcting a plan after review. Keep proposals distinct from approved decisions and implemented progress.
---

# Plan Project with XMemo

Turn intent into reviewable, executable project artifacts. Follow **discover → recall → frame → decompose → gate → write → approve → checkpoint**.

## 1. Discover the planning surface

Inspect the live repository or project before designing the plan. Identify its canonical documentation location, existing plans, architecture, test and release commands, ownership conventions, and dirty-worktree boundaries. Do not invent commands, paths, capabilities, or completed work.

Clarify whether the request needs:

- a strategic project plan;
- an implementation or migration plan;
- a release or launch plan;
- a recovery plan for partially completed work;
- both a stable project plan and a changeable execution plan.

## 2. Recall relevant XMemo context

Use `recall_context` or `get_project_context` for goals, constraints, prior decisions, rejected approaches, known risks, acceptance criteria, and the latest verified state. Use `search_memory` for exact decisions or lessons. Treat memory as context to reconcile with the live workspace, not as proof.

## 3. Frame the project contract

Define:

- problem and desired outcome;
- users or stakeholders;
- in-scope and explicitly out-of-scope work;
- current verified baseline;
- constraints and invariants;
- success measures and acceptance evidence;
- assumptions, dependencies, and unresolved decisions.

Do not convert unresolved choices into silent assumptions. Track a material unresolved choice with `create_pending_decision` only after the user agrees it belongs in XMemo.

## 4. Decompose into executable work

Organize work into independently reviewable phases or workstreams. For each phase include:

- objective and rationale;
- exact scope and affected artifacts;
- dependencies and owner;
- ordered implementation steps;
- verification commands or evidence;
- acceptance gate and rollback or recovery path;
- handoff condition and next phase.

Prefer phases that can be completed, verified, and reviewed independently. Separate implementation, review, merge, deployment, and production verification as distinct states.

## 5. Design evidence gates

Every completion claim must name its evidence. Include a verification matrix mapping requirements to tests, inspection, review, deployment, or user acceptance. Add risk controls for security, privacy, compatibility, data loss, migration, and operational recovery when applicable.

Read `references/plan-quality-gates.md` before producing a formal project or execution plan.

## 6. Write the Markdown artifacts

Respect the repository's existing plan names and locations. When no convention exists and the user wants files, use:

- `PROJECT_PLAN.md` for stable purpose, scope, architecture, milestones, risks, and success criteria;
- `EXECUTION_PLAN.md` for ordered phases, task status, evidence gates, ownership, and exact next action.

Use `assets/project-plan-template.md` and `assets/execution-plan-template.md` as starting structures, adapting rather than copying irrelevant sections. Keep one authoritative source for each fact and link related artifacts instead of duplicating them.

## 7. Review before approval

Return a planning receipt containing files created or changed, unresolved decisions, assumptions, critical risks, first acceptance gate, and exact next action. Label the artifacts `draft` until the user or authorized reviewer approves them. Use `/xmemo:review-plan` for a formal independent review.

## 8. Preserve only the approved state

After approval:

- save durable plan decisions or constraints with `remember` or `update_memory`;
- resolve tracked choices with `resolve_decision`;
- create only concrete near-term actions with `todo`;
- save the active phase, verified baseline, blocker, and next action with `update_state`;
- record a material approval or phase transition with `record_event`.

Do not mirror the entire Markdown plan into XMemo, create a formal XMemo project without an explicit request, or mark planned work as implemented.

Read `../memory-steward/references/memory-policy.md`, `../memory-steward/references/workflows.md`, and `../memory-steward/references/tool-routing.md` for write, checkpoint, and tool-routing rules.
