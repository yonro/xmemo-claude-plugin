# XMemo tool routing for Claude

Use only tools visible in the active XMemo MCP connection. This plugin does not expose private server tools, ChatGPT widget tools, or hidden legacy aliases.

## Signed Claude Code plugin tools

The plugin OAuth profile exposes exactly these 16 tools. The separately submitted Claude Directory Connector remains an independent 19-tool surface.

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
| Bounded formal-project context | `get_project_context` |

### Projects, decisions, TODOs, and progress

| Intent | Tool |
| --- | --- |
| Create a formal project after an explicit request | `project` |
| Save an unresolved choice | `create_pending_decision` |
| Close an exact pending choice | `resolve_decision` |
| Create, update, complete, or list actions | `todo` |
| Save or replace scoped working state | `update_state` |
| Record a milestone or handoff event | `record_event` |

## Safety rules

- Never call a nonexistent tool or claim an unavailable capability succeeded.
- `project` is limited to explicit formal project creation on this profile.
- `todo` does not expose bulk deletion on this profile.
- Never use hard deletion without the user's explicit irreversible-delete request and an exact target.
- Never use one memory write to archive an entire raw conversation.
