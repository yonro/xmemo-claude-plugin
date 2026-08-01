---
name: brainstorm
description: Run a structured XMemo-grounded brainstorm that recalls prior goals, constraints, decisions, and failed approaches; generates distinct options; tests them; and converges on a user-approved direction. Use when exploring ideas, product directions, architectures, strategies, or plans with Claude. Keep proposals tentative until the user approves them, and save only durable outcomes.
---

# Brainstorm with XMemo

Create new options without losing the decisions and constraints that already shape the work. Follow **frame → recall → diverge → challenge → converge → preserve**.

## 1. Frame the exploration

State the problem, desired outcome, decision horizon, known constraints, and what must remain open. Ask only for missing information that would materially change the option space.

## 2. Recall only decision-relevant context

Use `recall_context` for the bounded background, `search_memory` for a named decision or failed approach, and `get_project_context` for a known project. Retrieve goals, prior decisions, constraints, user preferences, unresolved choices, and lessons—not broad history.

Label retrieved items as current, potentially stale, or conflicting. The live workspace and the user's current correction outrank memory.

## 3. Diverge deliberately

Generate several genuinely different approaches. For each option include:

- core idea and intended value;
- assumptions and dependencies;
- major trade-offs and risks;
- reversibility and cost of being wrong;
- evidence or experiment that would reduce uncertainty.

Do not quietly collapse to the first plausible answer. Do not treat an earlier decision as immutable when the user explicitly wants to reopen it.

## 4. Challenge and compare

Stress-test the strongest options against saved constraints and current evidence. Identify contradictions, missing evidence, second-order effects, and criteria that distinguish the options. If an unresolved choice should survive this session, use `create_pending_decision` only after the user agrees it is a real decision to track.

## 5. Converge with the user

Return:

1. **Problem frame**
2. **Relevant remembered context**
3. **Option set**
4. **Comparison and risks**
5. **Recommended direction**
6. **Open questions or experiments**
7. **Decision required from the user**

Keep the recommendation explicitly provisional until approved.

## 6. Preserve only approved outcomes

After approval, route outcomes precisely:

- durable direction or rationale → `remember`;
- correction to an existing concept → `update_memory`;
- settled tracked choice → `resolve_decision`;
- concrete follow-up → `todo`;
- unfinished exploration state → `update_state`.

Preview multiple writes before saving. Never store the raw brainstorm, discarded alternatives as facts, or unverified claims as decisions. Return a compact receipt of what was saved, updated, or intentionally left tentative.

Read `../memory-steward/references/review-playbooks.md`, `../memory-steward/references/memory-policy.md`, and `../memory-steward/references/tool-routing.md` when detailed policy or routing is needed.
