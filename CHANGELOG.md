# Changelog

All notable changes to the XMemo Claude plugin are documented here.

## 0.1.1 - 2026-08-01

- Update plugin manifest homepage to official `https://xmemo.dev/integrations/claude` landing page.

## 0.1.0 - 2026-08-01

- Add the initial Claude Plugin manifest and hosted XMemo OAuth MCP configuration.
- Add the Claude-focused `memory-steward` Skill.
- Add durable-memory, checkpoint, resume, plan-review, progress-audit, and cross-agent handoff playbooks.
- Add a review-ready README with OAuth architecture, exact capability boundaries, and agent-readable metadata.
- Add a public architecture diagram and validate all README assets deterministically.
- Add offline validation and GitHub Actions package checks.
- Run Anthropic's official `claude plugin validate . --strict` check in CI.
- Add the official manifest schema and document cross-platform local loading and release versioning.
- Align the package with a signed, isolated 16-tool Claude Code profile while preserving the separate 19-tool Claude Directory Connector contract.
