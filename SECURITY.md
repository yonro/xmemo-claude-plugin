# Security

## Reporting a vulnerability

Please report suspected vulnerabilities privately to `security@xmemo.dev`. Do not include secrets or sensitive user data beyond what is necessary to reproduce the issue.

For product support, contact `support@xmemo.dev` or visit https://xmemo.dev/support.

## Plugin security model

- The plugin connects only to the hosted XMemo endpoint declared in `.mcp.json`.
- Authentication uses OAuth; no credentials are stored in this repository.
- Memory operations remain scoped to the signed-in user's authorized XMemo account.
- The Skill forbids saving secrets, raw authorization data, private traces, or unnecessary personal identifiers.
- Permanent deletion requires an explicit user request and an exact target.
- The checkpoint Hook is a single prompt-based Stop hook. The plugin ships no
  command hook and no executable script, and the Hook never blocks a tool call.
  It asks Claude to continue at most once per turn (`stop_hook_active`), and
  lets the turn end in subagents, while background work is pending, and when
  the model is unsure.
- The Hook keeps no local state and sends nothing to XMemo. Its single model
  call is made by Claude Code under the user's own Claude account, and it treats
  the final assistant message as data, not instructions.

## Repository hygiene

Before publishing a change:

1. Run `python scripts/validate-package.py`.
2. Run `claude plugin validate <plugin-path> --strict`.
3. Run `node scripts/test-checkpoint-hook.js` (Hook contract tests).
4. Review the diff for credentials, test accounts, internal endpoints, and accidental data exports.
