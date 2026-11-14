# Privacy

The XMemo Claude plugin connects Claude Code to the hosted XMemo MCP service. The plugin repository itself does not receive or retain memory content.

## Data flow

1. Claude Code connects to `https://xmemo.dev/mcp`.
2. The user signs in to XMemo and authorizes the requested OAuth scopes.
3. Claude may retrieve scoped XMemo content relevant to the user's request.
4. Claude may create or modify XMemo data only when the user or active workflow requests it.

## Checkpoints

The plugin has no hooks, scripts, or local storage. Working checkpoints are
saved only when a Skill calls for one after a project milestone, or when the
user runs `/xmemo:checkpoint`. Claude applies the active Skill's verification
and memory policy before any `update_state` call is made through the authorized
XMemo MCP connection.

The service may process project context, decisions, preferences, working state, TODOs, handoff notes, and Ledger entries that the user chooses to send. This data supports recall, search, continuity, review, export, and user-directed lifecycle operations.

With the `knowledge:read` scope, Claude may also read items from the user's XMemo Knowledge bases when they are relevant to a request. The plugin does not request `knowledge:write`, so it cannot create or change Knowledge content.

## Credentials

- OAuth tokens are managed by Claude Code and must never be committed to this repository.
- Never place passwords, API keys, bearer tokens, authorization codes, cookies, or reviewer credentials in memory or plugin files.
- The plugin does not require a static API key.

## User control

Users can recall, search, update, soft-delete, restore, and explicitly hard-delete eligible XMemo content through available service tools. Exact retention and account controls are governed by the canonical XMemo policies:

- Privacy Policy: https://xmemo.dev/legal/privacy
- Terms of Service: https://xmemo.dev/legal/tos
- Support: https://xmemo.dev/support
