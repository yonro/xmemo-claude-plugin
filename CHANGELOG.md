# Changelog

All notable changes to the XMemo Claude plugin are documented here.

## 1.0.0 - 2026-08-01

- Expand the plugin from one general memory Skill to an eight-Skill professional workflow suite.
- Add focused brainstorming, project-planning, plan-review, progress-audit, session-distillation, resume, and cross-agent handoff Skills.
- Add reusable `PROJECT_PLAN.md`, `EXECUTION_PLAN.md`, and development-progress audit templates with evidence gates.
- Add a fail-open Claude Code checkpoint Hook that detects material work, task completion, context compaction, and interrupted sessions without storing transcript content.
- Add deterministic Hook tests, lifecycle contract validation, and local recovery markers under Claude's persistent plugin data directory.
- Keep `memory-steward` as the mixed-workflow and lifecycle safety entry point.
- Share one exact 16-tool Claude profile across every Skill without adding server tools or MCP resources.
- Extend package validation and synthetic workflow prompts for the complete Skill suite.
- Add a tag-driven GitHub Release workflow that validates the package, verifies the manifest version, and publishes a ZIP with a SHA-256 checksum.
- Establish this complete eight-Skill package as the first stable public release.

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
