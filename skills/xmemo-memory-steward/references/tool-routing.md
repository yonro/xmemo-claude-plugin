# XMemo tool routing for Claude

Use only tools visible in the active XMemo MCP connection. This plugin does not expose private server tools, ChatGPT widget tools, or hidden legacy aliases.

## Current Claude public tools

The hosted Claude profile is expected to expose these 19 tool names at the time of the initial plugin release. The live connection remains authoritative.

### Connection and memory lifecycle

| Intent | Tool |
| --- | --- |
| Check connection or signed-in identity | `get_mcp_identity` |
| Save one new durable concept | `remember` |
| Correct an existing durable concept | `update_memory` |
| Soft-delete by default; hard-delete only on explicit request | `forget` |
| Restore an eligible soft-deleted memory | `restore_memory` |
| Explain why a memory exists or matched | `explain_memory` |

### Recall and analysis

| Intent | Tool |
| --- | --- |
| Quick recall | `recall` |
| Exact or scoped search | `search_memory` |
| Bounded multi-memory context or resume | `recall_context` |
| Analyze supplied text for memory-worthiness | `analyze_memory_text` |
| Recent activity | `memory_activity` |
| Aggregate overview | `memory_overview` |
| Aggregate statistics | `memory_stats` |

### TODOs

| Intent | Tool |
| --- | --- |
| Create an action item | `create_memory_todo` |
| List action items | `list_memory_todos` |
| Complete an action item | `complete_memory_todo` |

### Ledger

| Intent | Tool |
| --- | --- |
| Add an expense | `add_expense` |
| List transactions | `list_ledger_transactions` |
| Summarize the current month | `get_monthly_ledger_summary` |

## Availability-aware workflow helpers

Some XMemo profiles may expose dedicated tools such as `update_state`, `record_event`, or project helpers. Use them only when they are visible in the current MCP tool list and their input contract is clear.

If a dedicated helper is unavailable:

- **Checkpoint:** search for the existing scoped `Working state` memory, then update it; create one only if it does not exist.
- **Handoff:** save or update one concise `Handoff` memory with source, verified status, artifacts, blocker, and exact next action.
- **Milestone:** save a durable milestone only when its future retrieval value justifies it; do not create noisy event history.
- **Project context:** use an existing formal project path only when known and authorized; do not infer project creation from a path-like phrase.

## Safety rules

- Never call a nonexistent tool or claim an unavailable capability succeeded.
- Never route financial data through generic memory when Ledger tools are available.
- Never use hard deletion without the user's explicit irreversible-delete request and an exact target.
- Never use one memory write to archive an entire raw conversation.
