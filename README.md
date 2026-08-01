# XMemo for Claude

**Claude works. XMemo remembers.**

XMemo for Claude adds a durable, user-controlled memory workflow to Claude Code. It combines:

- an XMemo MCP connection with a focused 16-tool profile for memory lifecycle, project context, TODOs, checkpoints, decisions, and handoffs;
- the `xmemo-memory-steward` Skill for deciding what deserves memory, creating useful checkpoints, resuming work, reviewing plans, and handing work to another agent without archiving raw conversations.

The plugin is intentionally conservative: it writes only when the user or active workflow calls for a durable outcome, never stores secrets, and treats retrieved memory as context rather than unquestionable truth.

## What it enables

- Recover the decisions, constraints, TODOs, and verified progress that matter before starting work.
- Turn an important discussion into concise decisions, preferences, follow-up actions, and a restart-ready checkpoint.
- Resume a project from its latest verified state instead of replaying chat history.
- Review a plan or progress report from Claude, Codex, GitHub Copilot, Kiro, or another agent against saved decisions and evidence.
- Prepare a compact cross-agent handoff with provenance, blockers, and one exact next action.
- Search, update, soft-delete, restore, and explicitly hard-delete memories under the signed-in user's control.

## Package structure

```text
.claude-plugin/plugin.json                 Claude Plugin manifest
.mcp.json                                  Hosted XMemo MCP connection
skills/xmemo-memory-steward/SKILL.md       Memory workflow and safety policy
skills/xmemo-memory-steward/references/    Focused workflow references
scripts/validate-package.py                Offline package validator
```

## Install for local development

Prerequisites:

- Claude Code installed.
- An XMemo account.
- A browser available for the OAuth authorization flow.

Start Claude Code with the plugin directory:

```powershell
claude --plugin-dir D:\repos\xmemo-claude-plugin
```

Inside Claude Code:

1. Run `/mcp` and complete the XMemo OAuth flow.
2. Run `/reload-plugins` after local plugin changes.
3. Invoke `/xmemo-claude-plugin:xmemo-memory-steward`, or ask naturally to recall project context, save a checkpoint, review a plan, resume work, or prepare a handoff.

OAuth tokens are managed by Claude Code and are never stored in this repository.

## Validate

Run the repository validator:

```powershell
python scripts/validate-package.py
```

Then run Claude Code's official validator:

```powershell
claude plugin validate D:\repos\xmemo-claude-plugin --strict
```

## Capability boundary

The plugin's signed Claude Code OAuth identity selects an exact 16-tool server profile. It includes durable memory, project context and explicit project creation, consolidated TODO operations, working-state checkpoints, pending decisions, and milestone/handoff events. It excludes Ledger, aggregate analytics, ChatGPT widgets, bulk TODO deletion, and hidden legacy aliases.

This profile is independent from the separately submitted Claude Directory Connector, whose 19-tool contract is unchanged. The Skill does not grant access to private server tools and never claims that an unavailable operation succeeded.

## Links

- Product: https://xmemo.dev/product/mcp
- Documentation: https://xmemo.dev/docs
- Support: https://xmemo.dev/support
- Privacy: https://xmemo.dev/legal/privacy
- Terms: https://xmemo.dev/legal/tos

## License

MIT © 2026 Yonro
