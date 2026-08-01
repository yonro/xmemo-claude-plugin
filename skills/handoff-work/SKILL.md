---
name: handoff-work
description: Prepare or receive a professional XMemo handoff between Claude sessions or compatible AI agents such as Claude, Codex, GitHub Copilot, or Kiro. Use when switching agents, transferring unfinished work, reconciling a received handoff, or preserving a restart-ready package with provenance, evidence, blockers, and one exact next action.
---

# Handoff Work with XMemo

Transfer verified continuity, not confidence or chat history. Follow **scope → verify → package → persist → receive → acknowledge**.

## 1. Establish the transfer

Identify the objective, source, recipient, project or scope, artifacts, handoff direction, and whether work is paused or complete. Never assume the recipient exposes the same tools or can access local-only artifacts.

## 2. Verify the outgoing state

Recover the latest context with `recall_context` or `get_project_context`, then compare it with current files, diffs, tests, deployment state, or user confirmation. Treat another agent's completion statement as a claim until evidence supports it.

## 3. Build the handoff package

Include:

1. **Objective and acceptance criteria**
2. **Source, recipient, and artifact/version provenance**
3. **Verified current state**
4. **Completed work not to repeat**
5. **Decisions and rationale**
6. **Evidence and relevant artifacts**
7. **Constraints and safety boundaries**
8. **Remaining work and open TODOs**
9. **Blocker or required input**
10. **Exact next action**
11. **Next review or acceptance gate**

Exclude credentials, authorization data, private traces, raw logs, raw transcripts, and irrelevant internal identifiers.

## 4. Persist the transfer deliberately

- replace the scoped working checkpoint via `update_state`;
- record the material transfer via `record_event`;
- add a `todo` only for a concrete follow-up;
- save durable decisions or constraints separately with `remember` or `update_memory`;
- preserve unresolved formal choices with `create_pending_decision`.

Preview a multi-record handoff before writing. Return a receipt with the records changed and what remains unresolved.

## 5. Receive and reconcile a handoff

When receiving, recall the relevant saved state, compare the incoming claims with current evidence, and classify conflicts by scope, recency, provenance, and verification. Do not overwrite newer verified state with an older handoff. Produce an acceptance response: accepted, accepted with gaps, blocked, or rejected, plus the exact next action.

## 6. Acknowledge capability boundaries

XMemo can preserve shared context only for agents connected to the same authorized account and scope. It does not guarantee that another agent saved its work, exposes the same tool surface, or can reopen the original conversation.

Read `../memory-steward/references/workflows.md`, `../memory-steward/references/review-playbooks.md`, `../memory-steward/references/memory-policy.md`, and `../memory-steward/references/tool-routing.md` for detailed handoff and reconciliation rules.
