---
name: distill-session
description: Turn an important Claude conversation or work session into concise, retrieval-ready XMemo outcomes. Use when summarizing key points, preserving decisions and rationale, extracting TODOs and unresolved questions, or saving unfinished progress. Do not archive raw transcripts, filler, secrets, or tentative ideas as confirmed facts.
---

# Distill Session to XMemo

Preserve what remains useful after the conversation disappears. Follow **collect → classify → deduplicate → preview → write → receipt**.

## 1. Identify the durable boundary

Determine the subject, project or scope, and whether the user wants a summary only, a durable save, or both. Do not infer consent for sensitive or ambiguous writes.

## 2. Extract outcomes, not chronology

Classify the session into:

- final decisions and material rationale;
- stable preferences, rules, constraints, and definitions;
- verified facts, procedures, fixes, and lessons;
- concrete commitments and follow-up actions;
- unresolved questions, choices, or blockers;
- current verified state and exact next action.

Exclude greetings, repeated explanations, raw transcripts, long logs, large code blocks, secrets, credentials, private traces, and speculative ideas that were not accepted.

## 3. Check existing memory before writing

Use `search_memory` or `recall_context` when duplicate or superseding content is plausible. Prefer `update_memory` for a changed concept and a new `remember` record for a genuinely new durable concept. Keep one retrieval-friendly concept per durable memory when practical.

## 4. Show a candidate distillation

Before multiple writes, uncertain classification, overwrite, or project placement, present:

1. **Decisions**
2. **Durable context**
3. **TODOs**
4. **Unresolved items**
5. **Working checkpoint**
6. **Skipped content and why**

Label tentative and verified items explicitly. Obtain confirmation for the proposed batch.

## 5. Route confirmed outcomes

- new durable concept → `remember`;
- corrected durable concept → `update_memory`;
- concrete action → `todo`;
- unresolved formal choice → `create_pending_decision`;
- unfinished working state → `update_state`;
- significant milestone → `record_event`.

Do not create all record types mechanically. Use only the routes supported by the actual outcomes.

## 6. Return a concise receipt

Report saved, updated, checkpointed, skipped, and unresolved counts plus the exact next action. Never expose unnecessary internal IDs or claim success without successful tool results.

Read `../memory-steward/references/workflows.md`, `../memory-steward/references/memory-policy.md`, and `../memory-steward/references/tool-routing.md` for preview, receipt, and routing details.
