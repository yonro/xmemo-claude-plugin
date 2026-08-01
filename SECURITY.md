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
- The checkpoint Hook is fail-open, executes a bundled Node script in exec form,
  does not spawn child processes or open network connections, and never blocks a
  tool call or session exit.
- Hook state contains only bounded counters, timestamps, reason labels, and a
  project-path hash under `CLAUDE_PLUGIN_DATA`; it does not inspect or retain the
  session transcript or tool results.

## Repository hygiene

Before publishing a change:

1. Run `python scripts/validate-package.py`.
2. Run `claude plugin validate <plugin-path> --strict`.
3. Run `node scripts/test-checkpoint-hook.js`.
4. Review the diff for credentials, test accounts, internal endpoints, and accidental data exports.
