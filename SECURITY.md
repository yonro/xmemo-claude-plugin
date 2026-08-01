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

## Repository hygiene

Before publishing a change:

1. Run `python scripts/validate-package.py`.
2. Run `claude plugin validate <plugin-path> --strict`.
3. Review the diff for credentials, test accounts, internal endpoints, and accidental data exports.
