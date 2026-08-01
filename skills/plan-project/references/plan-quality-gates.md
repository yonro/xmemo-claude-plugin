# Project and Execution Plan Quality Gates

Use these gates when creating or revising a formal plan. Omit a gate only when it is demonstrably irrelevant.

## 1. Baseline gate

- The current state is verified from the live project.
- Existing work, constraints, and decisions are referenced accurately.
- Draft, approved, implemented, merged, deployed, and production-verified states are not conflated.

## 2. Scope gate

- The outcome, users, in-scope work, and non-goals are explicit.
- Each phase has a bounded artifact and ownership surface.
- Unrelated refactors and future ideas are excluded or separately tracked.

## 3. Decision gate

- Settled decisions include rationale and consequences.
- Unresolved decisions include owner, deadline or trigger, and impact.
- Assumptions are testable and are not presented as facts.

## 4. Execution gate

- Dependencies and ordering are explicit.
- Each phase can be completed and reviewed independently.
- The plan names exact artifacts, interfaces, migrations, and compatibility boundaries where known.
- The next action is executable without rediscovering the project.

## 5. Verification gate

- Every requirement maps to evidence.
- Test commands are real for the inspected project.
- Local tests, review, merge, deployment, and hosted smoke checks remain distinct.
- Negative paths and rollback or recovery behavior are covered where risk warrants it.

## 6. Safety gate

- Security, privacy, access, destructive changes, data migration, and sensitive information are addressed.
- User confirmation points are explicit for irreversible or externally visible operations.
- Existing unrelated work is preserved.

## 7. Handoff gate

- Owners and review gates are named.
- Completed work not to repeat, blockers, artifacts, and evidence are preserved.
- The receiving session or agent has one exact next action.

## 8. Approval gate

A plan is ready for execution only when blocking findings are resolved, required evidence is available, the decision owner approves the scope, and the first phase has a testable acceptance gate.
