---
name: review-plan
description: Review a proposed plan against XMemo's saved goals, decisions, constraints, lessons, project state, and acceptance criteria. Use for architecture plans, implementation plans, launch plans, or plans produced by Claude or another agent. Return a formal verdict and review gate; do not mistake a proposal for approved work or implemented progress.
---

# Review Plan with XMemo

Test a proposal against durable context before work begins. Follow **scope → baseline → decompose → challenge → verdict → gate**.

## 1. Define the review contract

Identify the plan version, intended outcome, project or scope, decision owner, risk tolerance, and required review depth. Distinguish a draft, proposed plan, approved plan, and implemented state.

## 2. Recover the authoritative context

Use `recall_context` for the bounded decision set, `search_memory` for exact constraints or prior choices, `get_project_context` for project state, and `todo` for active commitments. Retrieve only what can materially affect the review.

Resolve conflicts by current user instruction, verified evidence, recency, and scope. Memory is context, not automatic authority.

## 3. Decompose the plan

Map goals, assumptions, dependencies, sequence, ownership, rollback, verification, acceptance criteria, and unresolved decisions. Identify steps that are too broad to verify or that silently expand scope.

## 4. Challenge the proposal

Check:

- alignment with saved goals and constraints;
- contradictions with settled decisions;
- missing evidence, dependencies, or migration paths;
- security, privacy, data-loss, compatibility, and operational risks;
- testability, rollback, observability, and release gates;
- work that duplicates completed effort or ignores known lessons;
- cross-agent ownership and handoff boundaries.

Use `explain_memory` when the provenance or match rationale of a decisive memory is unclear.

## 5. Return a formal review

Use this structure:

1. **Plan and baseline reviewed**
2. **Verdict** — `approved`, `changes_requested`, `blocked`, or `rejected`
3. **Critical findings**
4. **Required changes**
5. **Risks and assumptions**
6. **Missing evidence or decisions**
7. **Acceptance gate** — exact evidence required before approval or execution

Make findings specific enough to act on. Separate blocking issues from optional improvements.

## 6. Preserve the review outcome carefully

Do not save the proposal as approved unless the user approves it. After approval:

- save the durable plan decision or rationale with `remember` or `update_memory`;
- track unresolved choices with `create_pending_decision`;
- create concrete actions with `todo`;
- checkpoint the approved execution start with `update_state`.

Preview multi-record writes and return a receipt. Never claim implementation or deployment merely because the plan passed review.

Read `../memory-steward/references/review-playbooks.md`, `../memory-steward/references/memory-policy.md`, and `../memory-steward/references/tool-routing.md` for detailed gates and routing.
