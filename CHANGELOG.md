# Changelog

All notable changes to the XMemo Claude plugin are documented here.

## 1.0.1 - 2026-10-23

- Rewrite the README in plain Markdown so it renders in the Claude plugin page, and update it for the Anthropic Directory listing, Claude app and Cowork setup through the plugin's Connectors tab, and Hook availability by surface.
- Add the `get-started` Skill for first-run onboarding: check the connection in plain language, show what XMemo already knows about the current work, offer to seed a few confirmed memories, offer once to add an every-session `## XMemo memory` section to the project's `CLAUDE.md` (or the uncommitted `CLAUDE.local.md` when repository rules exclude `CLAUDE.md`), and return to the original task.
- Read narrowly before widening in `get-started` and `memory-steward`: query by project or repository name first, reuse the distinctive words of a saved location instead of its full path, retry once instead of showing off-topic document excerpts and then stop using `recall_context` for that scope, and show only TODOs that belong to the current scope.
- Report recalled context in two groups, durable facts and working state, and offer to update or soft-delete working state that newer memories or the live workspace show as completed or superseded.
- Add proactive recall and save guidance to `memory-steward`: recall when saved context could change the result, offer to save lasting preferences and settled decisions, and skip XMemo for casual or one-turn work.
- Add "Make memory compound" guidance to `memory-steward`: apply saved preferences visibly, update memories from user corrections, keep TODOs, decisions, and checkpoints fresh, organize for retrieval, and offer clean-up of duplicates and stale items.
- Add good memory candidates to the memory policy.
- Add a shared connection rule to `tool-routing.md`, referenced by every Skill: match tools regardless of host prefix, report that nothing was read or written when XMemo is not connected, point to `/mcp` or the plugin's Connectors tab, and never request credentials in chat.
- Let the checkpoint Hook accept `update_state` from any MCP server name, so checkpoints saved through a project-scoped server or a connector also clear the pending marker.

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
