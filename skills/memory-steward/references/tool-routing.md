# XMemo tool routing for Claude

Use only tools visible in the active XMemo MCP connection. This plugin does not expose private server tools, ChatGPT widget tools, or hidden legacy aliases.

## Connection rule

The host may show XMemo tools with a prefix, such as `mcp__plugin_xmemo_xmemo__recall` or `mcp__claude_ai_XMemo__recall`. Match tools by the names below, not by the prefix.

Before reporting that XMemo is disconnected, check whether any XMemo tool is available. If none is, or a needed tool is missing:

1. Say plainly that nothing was read from or written to XMemo.
2. Point the user to the host's connection control: run `/mcp` and sign in to XMemo in Claude Code, or open the XMemo plugin's Connectors tab and select Connect in the Claude app or Cowork.
3. Continue from the live workspace or material the user supplied when that is still useful, and label the result as not grounded in saved memory.

Never ask for tokens, passwords, or authorization codes in the conversation, and never claim a recall or save that did not run.

## Time-aware queries

`recall`, `search_memory`, and `recall_context` can filter and sort by time. Check each tool's schema first and send only the time parameters it exposes.

- **Convert relative time to absolute time.** Turn "today", "yesterday", "last week", "since Monday", "in Q3", and similar phrases into RFC 3339 timestamps with the user's time-zone offset, such as `2026-10-17T00:00:00+09:00`. Use local midnight for day boundaries. If the user's time zone is unknown, use the best available signal and state the assumption.
- **Read "last week" as the previous calendar week.** It runs from Monday 00:00 to the following Monday 00:00 in the user's time zone, unless the user's locale starts weeks on another day. Use a rolling window ending now only for phrases such as "the past 7 days". State which reading you used.
- **Bound the window.** `since` and `until` form the half-open window [since, until), and `until` must be later than `since`. One query covers at most 90 days; split a longer range into consecutive windows, merge the results, and say if any window could not be read.
- **Order by recency when it matters.** Pass `time_order` with `desc` for "latest", "recent", or "newest first", and with `asc` for a timeline or "oldest first". Without a time constraint or recency intent, leave it unset so relevance ranking applies.
- **Match the mode to the question.** When the question names a topic, project, or repository, such as "what did I do on the Claude plugin last week", search in the default topic mode with the time window first. `activity_log` ignores the topic and returns everything in the window. Pass `query_mode` with `activity_log`, together with both `since` and `until`, only for topic-free questions such as "what did I do last week", or to fill gaps after a topic search. It fails without both bounds.
- **Filter results to the topic in both modes.** A time window narrows what the server ranks, so a topic search over a sparse window can return nearly everything in it. Before reporting, keep only results that clearly belong to the named topic, project, or repository, whichever mode produced them, and say when nothing relevant was found.
- **Treat a full page as possibly incomplete.** When the number of results equals the limit, more items may exist. Split the window into smaller windows, such as one day each, or raise the limit where the tool allows it, and say in the answer when coverage may be incomplete. For work in a repository, cross-check the window against its commit and CI history.
- **Know the time axis.** Results show which time a filter used, such as `Axis: created_at`. Do not describe a memory as updated in a window when only its creation time was filtered.
- **Report the window.** State the absolute window you used, in the user's time zone, so the user can correct it.

## Tools the Skills call

The server selects the tool set from the OAuth client identity. Claude Code receives the 19-tool XMemo plugin profile; the Claude app and Cowork receive the 27-tool XMemo Connector. Both include these 16 tools, and the Skills call only these. The extra tools on each surface (document reading and restart snapshots on the plugin profile; Ledger, legacy TODO, aggregate analytics, and document reading on the Connector) are not routed by any Skill.

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
- `project` is limited to explicit formal project creation in this plugin.
- `todo` does not expose bulk deletion.
- Never use hard deletion without the user's explicit irreversible-delete request and an exact target.
- Never use one memory write to archive an entire raw conversation.
