# XMemo memory policy

Use this reference to decide whether to save, update, checkpoint, preview, or skip information.

## Decision matrix

| Signal | Action |
| --- | --- |
| Explicit request to remember one safe, unambiguous fact | Save with `remember`, or update the existing memory |
| Stable preference useful in later conversations | Save and give a short receipt |
| Final project decision with rationale | Save a durable decision |
| Brainstorm options before a decision | Organize and review; do not save every option as truth |
| Approved plan that will guide future work | Save the approved outcome, rationale, scope, and acceptance gate |
| Progress claim from another agent | Preserve provenance; update verified state only after suitable evidence |
| Corrected version of an existing fact | Find and update the existing concept |
| Several independent durable candidates | Preview the proposed set and confirm before batch writes |
| Ambiguous durability, sensitivity, interpretation, or placement | Ask before writing |
| Task pauses with meaningful work remaining | Save or update one scoped working-state checkpoint |
| Concrete future action | Create a TODO |
| Casual chat or one-turn detail | Skip |
| Secret, credential, token, or highly sensitive identifier | Never save |
| Financial transaction | Use the available Ledger tool, not generic memory |

## Durable-memory quality

A durable memory must:

- stand alone without the original conversation;
- describe one concept when practical;
- state whether it is approved, active, pending, superseded, or unresolved;
- preserve rationale when it affects future behavior;
- name the relevant subject or project;
- avoid certainty when the source is uncertain;
- preserve source-agent or artifact provenance when useful without treating it as authority.

Preferred shape:

```text
Subject: <project, preference, or decision>
Durable outcome: <what should be remembered>
Rationale: <why it matters>
Status: <approved, active, superseded, pending, or unresolved>
Source: <agent, artifact, or user decision when useful>
Next implication: <what future work should do>
```

Natural concise prose is preferable when it remains equally clear.

## Batch-write consent

Do not interrupt one explicit safe memory request with redundant confirmation. Preview before writing when:

- a conversation yields several independent memories;
- candidates may be personal, sensitive, or short-lived;
- project placement is uncertain;
- a candidate would overwrite or supersede an existing decision;
- a review would promote an agent draft or progress claim to approved or verified status;
- settled decisions and unresolved ideas are difficult to distinguish.

```text
Proposed XMemo update
- 2 decisions
- 1 working-state checkpoint
- 3 TODOs
- 1 unresolved question (labeled unresolved)
Skipped: raw transcript and transient details
```

## Working-state quality

```text
Working state
Objective: <one concrete outcome>
Verified status: <what is true now>
Completed: <material finished work and evidence>
Decisions: <settled choices>
Next action: <one exact resumable step>
Blocked by: <only when blocked>
Artifacts: <stable references, never secrets or raw traces>
```

Update the same scoped checkpoint instead of creating permanent memories for every intermediate step.

## Conflict rules

- Prefer the user's current explicit correction over retrieved memory.
- Update a changed concept instead of creating a competing duplicate.
- Do not merge unrelated concepts merely because they share keywords.
- Do not let an unverified progress report overwrite a verified checkpoint.
- If equally credible sources conflict, report the conflict and ask instead of choosing silently.

## Always skip

- Raw transcripts and verbatim conversation archives.
- Long terminal output, stack traces, or code dumps.
- Passwords, API keys, bearer tokens, cookies, OAuth or MFA codes.
- Payment identifiers, government identifiers, or unrelated personal data.
- Unconfirmed claims presented as verified facts.
