# XMemo workflow playbooks

Read only the playbook needed for the current request.

## Important-conversation distillation

1. Identify the conversation scope and saving intent.
2. Extract candidates into decisions, stable preferences, verified facts, TODOs, unresolved questions, and current state.
3. Remove raw dialogue, repetition, transient details, logs, code dumps, and sensitive data.
4. Search for existing versions of durable concepts.
5. Preview the proposed batch when several writes or ambiguity are present.
6. Route confirmed outcomes to `remember`, `update_memory`, `todo`, pending-decision tools, or `update_state`.
7. Return a receipt with counts, categories, skipped content, and next action.

```text
Proposed XMemo update
- Decision: <settled outcome and why>
- Preference: <stable future behavior>
- TODO: <owner or next action>
- Working state: <verified status and next resumable step>
- Unresolved: <question, explicitly not settled>
Skipped: raw transcript, repeated explanations, and transient details
```

```text
Saved to XMemo
- New memories: <count and categories>
- Updated memories: <count and categories>
- TODOs: <count>
- Working-state checkpoint: <saved, updated, or not needed>
- Skipped: <brief reason>
```

## Progress checkpoint

Use one scoped checkpoint so later updates replace stale working state.

```text
Working state
Objective: <one concrete outcome>
Verified status: <what is true now>
Completed: <finished work and evidence>
Decisions: <settled choices and rationale>
Artifacts: <stable references>
Do not repeat: <already verified work>
Next action: <one exact step>
Blocked by: <required input or dependency, if any>
```

Write the checkpoint with `update_state` so a later session replaces stale working state instead of accumulating duplicate checkpoint memories.

## Resume Brief

Build from `recall_context`, then reconcile with project context, TODOs, pending decisions, durable memories, and current evidence.

```text
Resume Brief
- Objective: <current goal>
- Verified status: <latest reconciled truth>
- Completed: <work not to repeat>
- Active decisions: <choices constraining the next step>
- Open actions: <only relevant TODOs>
- Blocker: <if any>
- Exact next action: <one directly executable step>
- Sources checked: <context, TODOs, activity, memories, evidence>
```

If sources disagree, surface the conflict instead of silently selecting an older checkpoint.

## Cross-agent handoff

Update the scoped checkpoint first. Then save or update one handoff record when it will help the recipient. Create a TODO only for a concrete follow-up.

```text
Handoff
- Objective: <desired outcome>
- Recipient: <agent or role when known>
- Source agents/artifacts: <useful provenance>
- Verified status: <current truth>
- Decisions and rationale: <settled constraints>
- Completed: <finished work>
- Evidence and artifacts: <stable references>
- Do not repeat: <completed checks or failed approaches>
- Remaining work: <bounded scope>
- Exact next action: <one executable step>
- Blocker / required input: <if any>
- Safety boundaries: <permissions and destructive-action limits>
- Next review gate: <evidence required before status transition>
```

Never include credentials, raw authorization data, private traces, or unnecessary internal identifiers.
