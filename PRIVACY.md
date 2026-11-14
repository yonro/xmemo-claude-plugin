# Privacy

The XMemo Claude plugin connects Claude Code to the hosted XMemo MCP service. The plugin repository itself does not receive or retain memory content.

## Data flow

1. Claude Code connects to `https://xmemo.dev/mcp`.
2. The user signs in to XMemo and authorizes the requested OAuth scopes.
3. Claude may retrieve scoped XMemo content relevant to the user's request.
4. Claude may create or modify XMemo data only when the user or active workflow requests it.

## Checkpoint check

The plugin includes a prompt-based Stop Hook that helps prevent meaningful work
from being lost between sessions. It runs no local program and stores nothing on
the user's machine. When a turn ends, Claude Code makes one extra Claude model
call, as it does for any prompt-based hook, under the user's own Claude account.
That call receives the Stop hook input (session identifiers, the working
directory, the turn's final assistant message, and pending background tasks or
scheduled jobs). In Claude Code 2.1.318 it also receives the current
conversation as context. The model uses it only to decide whether to ask Claude
to save a checkpoint, and nothing from it is stored or sent to XMemo.

The Hook never sends anything to XMemo. When a turn reports a project milestone
without a checkpoint status, it gives Claude one continuation reminder. Claude
then applies the active Skill's verification and memory policy before any
`update_state` call is made through the authorized XMemo MCP connection.

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
