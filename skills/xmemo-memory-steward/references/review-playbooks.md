# XMemo brainstorming and review playbooks

Use these playbooks when Claude shapes reasoning or reviews work produced by Claude, Codex, GitHub Copilot, Kiro, or another agent.

## Brainstorm and converge

1. Recall relevant goals, constraints, decisions, failed approaches, and open questions.
2. Separate divergent exploration from convergent planning.
3. Compare options by benefits, costs, risks, assumptions, reversibility, and needed evidence.
4. Surface contradictions with saved decisions instead of silently replacing them.
5. Recommend a direction only when evidence supports one.
6. Label unresolved ideas as tentative.
7. Save only the confirmed direction, rationale, unresolved questions, and concrete actions.

```text
Brainstorm Review
- Objective
- Relevant prior context
- Options and tradeoffs
- Assumptions requiring validation
- Risks and reversible experiments
- Recommended direction
- Unresolved questions
- Proposed XMemo updates
```

## Review a plan

Identify the source agent and artifact/version when known. Review against the user's goal, current XMemo decisions, and present evidence.

Check:

- objective, scope, and non-goals;
- compatibility with prior decisions and constraints;
- dependency order and independently verifiable phases;
- missing edge cases, recovery, security, privacy, and destructive actions;
- permissions, external coordination, and deployment boundaries;
- acceptance criteria, tests, evidence, rollback, and handoff readiness;
- whether the plan confuses proposal, implementation, commit, deployment, and verified production outcome.

Return one verdict:

- `approved`: coherent and ready to execute; not evidence of implementation;
- `changes_requested`: viable direction with named required fixes;
- `blocked`: required facts, access, or decisions are missing;
- `rejected`: conflicts with the goal or unacceptable constraints.

```text
Plan Review
- Source: <agent and artifact/version>
- Verdict
- What is strong
- Critical findings
- Missing evidence or decisions
- Required revisions in priority order
- Acceptance gate
- Recommended next action
```

Save a durable review decision only when it will guide future work.

## Audit progress

Do not accept a progress summary as proof by itself.

1. Recover the approved plan, latest checkpoint, prior reviews, and relevant TODOs.
2. Map each claimed completion to current files, diffs, tests, logs, review results, deployment state, or user confirmation.
3. Mark items `verified`, `partially verified`, `claimed`, `stale`, `conflicting`, or `blocked`.
4. Distinguish local implementation, commit, push, deployment, and production verification.
5. Detect scope drift, skipped gates, new risk, and stale next actions.
6. Update working state only from the reconciled result.

```text
Progress Audit
- Source: <agent and checkpoint/version>
- Overall status
- Verified completed work
- Claimed but unverified work
- Conflicts or stale state
- Remaining acceptance gates
- Risks and blockers
- Exact next action
```

## Reconcile multiple agents

- Compare claims concept by concept, not agent by agent.
- Prefer direct evidence and explicit user decisions over confidence language.
- Prefer newer evidence only when it addresses the same scope and is not superseded.
- Preserve material disagreement when no authoritative source resolves it.
- Keep source attribution readable; never treat an agent label as authentication or authorization.
- Do not expose raw tokens, traces, private metadata, or hidden reasoning.

```text
XMemo coordination update
- Sources reviewed
- Verdict or reconciled status
- Durable decisions saved or updated
- Working state updated
- TODOs created or changed
- Conflicts left unresolved
- Next review or execution gate
```
