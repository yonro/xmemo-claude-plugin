[![XMemo](https://cdn.jsdelivr.net/gh/yonro/xmemo-claude-plugin@main/assets/icon.png)](https://xmemo.dev/integrations/claude)

# XMemo for Claude

**Durable project memory and cross-agent continuity for Claude.**

Recall the context behind the work, preserve verified decisions and progress,
and hand projects across sessions without archiving raw conversations.

[![Validation](https://img.shields.io/github/actions/workflow/status/yonro/xmemo-claude-plugin/validate.yml?branch=main&style=flat-square&logo=githubactions&logoColor=white&label=validation)](https://github.com/yonro/xmemo-claude-plugin/actions/workflows/validate.yml)
![Plugin version](https://img.shields.io/badge/plugin-v1.0.4-8B5CF6?style=flat-square)
[![License](https://img.shields.io/github/license/yonro/xmemo-claude-plugin?style=flat-square)](LICENSE)
![Claude plugin](https://img.shields.io/badge/Claude-Anthropic%20Directory-D97757?style=flat-square)
![Hosted MCP](https://img.shields.io/badge/MCP-hosted-06B6D4?style=flat-square)
![OAuth](https://img.shields.io/badge/auth-OAuth%202.0-10B981?style=flat-square)

[Quick start](#quick-start) ·
[Architecture](#architecture) ·
[Memory workflow](#memory-workflow) ·
[Tool surface](#tool-surface) ·
[Security](#security-and-privacy) ·
[Validation](#validation)

---

The XMemo Claude plugin combines a reusable memory workflow with a hosted
[Model Context Protocol](https://code.claude.com/docs/en/mcp) connection.
Claude continues to reason, inspect, implement, and validate from the live
workspace; XMemo carries only the durable context that should survive the
current conversation.

The plugin is published in the Anthropic Directory. The separate XMemo
connector listing is still under review; until it is listed, Claude adds the
plugin's XMemo server as a custom connector (see [Quick start](#quick-start)).

## At a glance

| | |
|---|---|
| Display name | `XMemo` |
| Plugin ID | `xmemo` |
| Skills | Nine professional workflows under `/xmemo:*` |
| Automation | Fail-open lifecycle checkpoint Hook (Claude Code and Cowork) |
| Version | `1.0.4` |
| Bundle | Claude Skill suite + checkpoint Hook + hosted MCP configuration |
| MCP endpoint | `https://xmemo.dev/mcp` |
| Authentication | OAuth 2.0 browser sign-in with Dynamic Client Registration |
| Requested scopes | `memory:read memory:write` |
| Tools | XMemo Connector: 27 tools on Claude Code, the Claude app, and Cowork; direct MCP configuration: 35. The Skills call 17 |
| MCP resources | None |
| Local Hook state | Bounded metadata only under `CLAUDE_PLUGIN_DATA`; no transcript content |
| License | MIT |

### What it enables

- **Focused recall** — recover relevant project context, decisions, constraints,
  TODOs, and verified progress before starting work.
- **Durable outcomes** — turn an important conversation into concise decisions,
  approved plans, follow-up actions, and a restart-ready checkpoint.
- **Plan and progress review** — compare a proposal or another agent's report
  against saved decisions and evidence.
- **Working continuity** — resume from the latest verified state instead of
  replaying chat history.
- **Automatic checkpoint guard** — detect material implementation activity,
  completed tasks, context compaction, and interrupted sessions, then ask Claude
  to preserve one verified checkpoint at the right boundary.
- **Cross-agent handoff** — preserve provenance, blockers, remaining work, and
  one exact next action for another compatible agent.
- **User-controlled lifecycle** — search, update, soft-delete, restore, and
  explicitly hard-delete eligible memories.

### Professional Skill suite

Each Skill has a distinct trigger and evidence contract. Claude can select one
from natural language, or the user can invoke the namespaced command directly.

| Skill | Professional workflow |
|---|---|
| [`/xmemo:get-started`](skills/get-started/SKILL.md) | Connect XMemo, see what it already knows about the current work, seed the first durable memories, and optionally use XMemo in every session |
| [`/xmemo:brainstorm`](skills/brainstorm/SKILL.md) | Recall constraints, generate distinct options, challenge assumptions, converge, and preserve only approved outcomes |
| [`/xmemo:plan-project`](skills/plan-project/SKILL.md) | Design evidence-gated `PROJECT_PLAN.md` and `EXECUTION_PLAN.md` artifacts from XMemo context and the live project |
| [`/xmemo:review-plan`](skills/review-plan/SKILL.md) | Review a proposal against saved decisions and return a formal verdict plus acceptance gate |
| [`/xmemo:audit-progress`](skills/audit-progress/SKILL.md) | Separate verified work from partial, claimed, stale, conflicting, or blocked progress and optionally write a formal Markdown audit |
| [`/xmemo:distill-session`](skills/distill-session/SKILL.md) | Extract retrieval-ready decisions, context, TODOs, unresolved items, and checkpoints without archiving the transcript |
| [`/xmemo:resume-work`](skills/resume-work/SKILL.md) | Reconcile the latest checkpoint with current evidence and continue from one exact next action |
| [`/xmemo:handoff-work`](skills/handoff-work/SKILL.md) | Prepare or receive evidence-based handoffs across Claude sessions and compatible agents |
| [`/xmemo:memory-steward`](skills/memory-steward/SKILL.md) | Coordinate mixed workflows, proactive recall and save decisions, and memory lifecycle operations under the shared safety policy |

## Quick start

You need an XMemo account and a browser for the OAuth sign-in. Plugin
availability depends on your Claude plan, workspace settings, and app version;
see [Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

### Claude app and Cowork

1. Open **Customize → Plugins**, find **XMemo** in the Anthropic Directory, and
   add it.
2. Open the plugin's **Connectors** tab and select **Connect** next to `xmemo`.
   Until the XMemo connector is listed in the directory, Claude offers to add it
   as a custom connector with `https://xmemo.dev/mcp` already filled in.
3. Sign in to XMemo in the browser window and approve `memory:read` and
   `memory:write`.
4. Start a new conversation and run `/xmemo:get-started`, pick another Skill from
   the `/` menu, or ask naturally.

The checkpoint Hook runs in Cowork but not in Claude chat, so in chat Claude
saves checkpoints only when a Skill or your request calls for one.

### Claude Code

1. Run `/plugin`, find **XMemo** in the marketplace, and install it.
2. Run `/mcp`, select the XMemo server, and complete the browser sign-in for
   `memory:read` and `memory:write`.
3. Run `/xmemo:get-started` to see what XMemo already knows about the current
   project and seed its first memories.
4. Invoke a focused workflow such as `/xmemo:resume-work`, use
   `/xmemo:memory-steward` for mixed memory work, or ask naturally:

```text
Bring me up to speed on this project using XMemo. Show the latest verified
state, active decisions, open TODOs, blocker, and exact next action.
```

The checkpoint Hook needs Node.js available as `node`; the exec-form Hook
pattern works across Windows, macOS, and Linux.

Claude manages OAuth tokens outside this repository; no API key, client secret,
reviewer credential, or bearer token belongs in the package.

### Local development

Load a working copy instead of the published plugin:

```bash
git clone https://github.com/yonro/xmemo-claude-plugin.git
claude --plugin-dir ./xmemo-claude-plugin
```

After local plugin changes, run `/reload-plugins` or restart Claude Code.

### Versioning

Marketplace releases use semantic versions from
`.claude-plugin/plugin.json`. Because an explicit version pins Claude Code's
plugin cache, every published update must increment that value. Git tags and
GitHub Releases use the same version.

Every tag matching `v*.*.*` runs the release workflow. The workflow rejects a
tag that does not match the manifest version, reruns the official and package
validators plus Hook tests, then publishes an immutable plugin ZIP and SHA-256
checksum to the corresponding GitHub Release. Release archives are generated by
CI; local ZIP files under `dist/` are disposable and must not be committed.

## Architecture

![XMemo Claude plugin architecture](https://cdn.jsdelivr.net/gh/yonro/xmemo-claude-plugin@main/assets/claude-memory-flow.png)

The plugin has three complementary components:

| Component | Responsibility |
|---|---|
| `skills/*/SKILL.md` | Nine focused professional workflows sharing one XMemo safety and routing contract |
| `hooks/hooks.json` + `scripts/checkpoint-hook.js` | Detects checkpoint boundaries and interrupted work without reading or persisting transcripts |
| `.mcp.json` | Declares the hosted XMemo endpoint and pins the minimum OAuth scopes |

### Data path

1. Claude loads the focused Skill whose description matches the workflow, or
   `memory-steward` for mixed memory work and proactive recall or save decisions.
2. In Claude Code and Cowork, the local lifecycle Hook records only bounded
   activity metadata under `CLAUDE_PLUGIN_DATA` and asks Claude to checkpoint
   only at a material boundary.
3. Claude connects to `https://xmemo.dev/mcp` over HTTPS: Claude Code through
   `/mcp`, the Claude app and Cowork through the plugin's Connectors tab.
4. The server advertises OAuth metadata, and Claude registers its client and
   runs the browser authorization.
5. Every Claude surface uses the same XMemo Connector and its 27 tools; a
   direct MCP configuration exposes 35. The Skills call 17 of them.
6. Each tool reads or writes only data authorized for the signed-in XMemo
   account and requested scope.
7. Claude reports the useful result without exposing tokens, internal traces,
   or unnecessary identifiers.

The package contains no XMemo service implementation, production credentials,
private memories, deployment scripts, or internal runbooks.

## Memory workflow

### First run

`/xmemo:get-started` checks the connection, shows what XMemo already knows
about the current project, offers to save a few verified basics such as build
and test commands, and offers once to add a short `## XMemo memory` section to
the project's `CLAUDE.md` so XMemo is used in every session. When the repository
should not commit a `CLAUDE.md`, it proposes the uncommitted `CLAUDE.local.md`
instead. Nothing is written
without confirmation, and a "don't ask again" choice can be saved to XMemo so
every device respects it.

### At task start

1. Recall only context that could materially change the current work, such as
   prior decisions, preferences, constraints, open TODOs, or the last checkpoint.
2. Prefer bounded project context or a restart checkpoint over broad history.
3. Treat the live workspace and current evidence as canonical when memory is
   stale or conflicts with reality.

### During work

1. Separate tentative ideas from confirmed decisions.
2. When the user states a lasting preference or settles a decision, offer to
   save it; save directly only when the user asked.
3. Save durable conclusions, not verbose reasoning or raw transcripts.
4. Record unresolved choices as pending decisions.
5. Maintain the active objective, verified state, blocker, and next action.
6. Update existing memory instead of creating near-duplicates.

### Getting better with use

Claude applies saved preferences and decisions without being asked again and
says so in one line, updates a memory when the user corrects it, completes
TODOs and resolves pending decisions as work happens, and offers to clean up
duplicates or stale items it finds during recall. Because memory lives in the
XMemo service, the same context follows the user across sessions, devices,
and compatible agents.

### Automatic checkpoint guard

The Hook runs in Claude Code and Cowork. It does not write a memory after every
tool call. It marks local activity and asks Claude to continue once when one of
these boundaries is reached:

- a tracked task is completed;
- context is about to be compacted;
- verified implementation work has reached a material stage;
- sustained work crosses the activity or time threshold;
- the previous session ended or failed with unsaved work.

Claude then decides from the current verified context whether `update_state` is
warranted. A successful `update_state` call from any connected XMemo server
clears the pending marker. `record_event` remains reserved for significant
milestones and handoffs. If XMemo is unavailable or no durable change exists,
the Hook fails open and never fabricates a save.

The Hook never opens `transcript_path`, does not inspect prompt, message, or tool
response content, and never persists source contents, credentials, or raw
transcripts.

### When XMemo is not connected

Every Skill checks for XMemo tools before reporting a disconnection. If none are
available, Claude says that nothing was read or written and points to `/mcp` in
Claude Code or the plugin's Connectors tab in the Claude app and Cowork. It
never asks for credentials in the conversation.

### At handoff

1. Preserve what changed and what was actually verified.
2. Include decisions, artifacts, constraints, remaining work, and blockers.
3. Finish with one exact next action another session or agent can execute.

## Tool surface

Claude Code, the Claude app, and Cowork all use the same XMemo Connector,
which exposes 27 tools. A direct MCP configuration of `https://xmemo.dev/mcp`
exposes 35, including all 27. The Skills work with either and call these 17:

| Area | Tools |
|---|---|
| Identity | `get_mcp_identity` |
| Recall and explanation | `recall`, `search_memory`, `recall_context`, `explain_memory`, `read_memory` |
| Memory lifecycle | `remember`, `update_memory`, `forget`, `restore_memory` |
| Project context | `get_project_context`, `project` |
| Decisions | `create_pending_decision`, `resolve_decision` |
| Work tracking | `todo`, `update_state`, `record_event` |

The other tools cover the expense ledger, older TODO tools, memory statistics,
activity, and text analysis. No Skill depends on them; Claude uses them when
the user asks for what they do. The Skills use no MCP resources, widget UI, bulk
TODO deletion, or hidden legacy aliases.

## Capabilities and boundaries

| Capability | Included | Boundary |
|---|:---:|---|
| Hosted XMemo MCP connection | Yes | Requires user OAuth authorization |
| Professional memory Skill suite | Yes | Nine focused workflows activate only for relevant requests |
| Proactive recall and save offers | Yes | Recall only when saved context could change the result; durable saves need a user request or confirmation |
| Automatic checkpoint guard | Yes | Claude Code and Cowork only; lifecycle metadata only; semantic writes remain Skill-governed |
| Recall and search | Yes | Limited to the signed-in account and scopes |
| Durable writes and working state | Yes | Performed only when requested by the user or active workflow |
| Project creation | Yes | Only after an explicit formal-project request |
| Project changes | Yes | Memories, decisions, document and conversation links, and settings of an authorized project; documents can be linked, not created |
| Recoverable deletion | Yes | `forget` is soft delete by default |
| Permanent deletion | Yes | Requires an explicit irreversible request and exact target |
| Cross-agent continuity | Yes | Other agents require their own authorized XMemo connection |
| Custom UI or widgets | No | The plugin is Skill + MCP only |
| Local memory database | No | Memory remains in the XMemo service |
| Private service code | No | This repository is intentionally reviewable |

## Package contents

```text
.claude-plugin/plugin.json                 Claude plugin manifest
.github/workflows/validate.yml             Deterministic package validation
.mcp.json                                  Hosted XMemo OAuth MCP connection
assets/icon.png                            Official XMemo icon
assets/claude-memory-flow.png              Rendered README architecture diagram
assets/claude-memory-flow.svg              Editable architecture diagram source
examples/workflow-prompts.md               Synthetic evaluation prompts
scripts/validate-package.py                Zero-dependency package validator
scripts/checkpoint-hook.js                 Cross-platform checkpoint lifecycle coordinator
scripts/test-checkpoint-hook.js            Deterministic Hook regression tests
hooks/hooks.json                           Claude Code lifecycle Hook configuration
skills/get-started/SKILL.md                First-run connection, seeding, and every-session setup
skills/brainstorm/SKILL.md                 Memory-grounded ideation and convergence
skills/plan-project/SKILL.md               Project and execution-plan design
skills/review-plan/SKILL.md                Formal plan review and acceptance gates
skills/audit-progress/SKILL.md             Evidence-based progress audit
skills/distill-session/SKILL.md            Important-session distillation
skills/resume-work/SKILL.md                Deterministic recovery and continuation
skills/handoff-work/SKILL.md               Cross-session and cross-agent handoff
skills/memory-steward/SKILL.md             Mixed workflow, proactive memory, and lifecycle safety policy
skills/plan-project/assets/                Project and execution-plan templates
skills/plan-project/references/            Plan quality and evidence gates
skills/audit-progress/assets/              Development-progress audit template
skills/memory-steward/references/          Tool routing, connection rule, and focused playbooks
PRIVACY.md                                 Data-flow and user-control summary
SECURITY.md                                Credential and review boundaries
CHANGELOG.md                               Release history
LICENSE                                    MIT license
```

Only `plugin.json` lives inside `.claude-plugin/`. Skills, MCP configuration,
assets, examples, and public documentation remain at the plugin root.

## Validation

Run the repository validator:

```bash
python scripts/validate-package.py
```

It verifies:

- manifest identity, display name, SemVer, and package paths;
- hosted endpoint and exact OAuth scope pin;
- the 17-tool Skill routing contract;
- the exact nine-Skill suite, frontmatter, workflow markers, templates, and referenced playbooks;
- required public documents and parseable assets;
- exact Hook lifecycle events, exec-form command safety, and no transcript/network access;
- common committed-secret patterns.

Run the deterministic Hook tests:

```bash
node scripts/test-checkpoint-hook.js
```

Then run Claude Code's official strict validator from the repository root:

```bash
claude plugin validate . --strict
```

Synthetic evaluation prompts are maintained in
[examples/workflow-prompts.md](examples/workflow-prompts.md).

## Security and privacy

- OAuth tokens stay in Claude's credential storage.
- The repository contains no password, API key, bearer token, OAuth code,
  cookie, reviewer credential, or private memory.
- The plugin pins `memory:read memory:write` rather than relying on broader
  discovered scopes.
- The Hook uses the official exec-form `node` pattern, is fail-open, opens no
  network connection, spawns no subprocess, and keeps only bounded local state.
- The Hook does not inspect or store Claude transcripts or tool responses.
- Retrieved memory is treated as context to verify, not unquestionable truth.
- Hard deletion is never inferred from ambiguous language.
- Demos and review evidence must use synthetic data.

Read the package documents:

- [Privacy](PRIVACY.md)
- [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)

Canonical service policies:

- [Privacy policy](https://xmemo.dev/legal/privacy)
- [Terms of service](https://xmemo.dev/legal/tos)
- [Support](https://xmemo.dev/support)

## Release status

- Plugin: published in the Anthropic Directory.
- XMemo connector: separate listing under review.
- Nine-Skill professional workflow bundle: present.
- Seven-event checkpoint Hook and regression tests: present.
- OAuth MCP configuration: present.
- All 17 tools the Skills call are on the 27-tool XMemo Connector, the same on Claude Code, the Claude app, and Cowork: verified.
- MCP resources and widget UI: absent.
- Package validator and CI: present.
- Synthetic workflow prompts: present.

## Agent-readable metadata

| Field | Value |
|---|---|
| Package repository | `yonro/xmemo-claude-plugin` |
| Runtime | Claude Code, Claude app, Cowork |
| Plugin ID | `xmemo` |
| Display name | `XMemo` |
| Skill commands | `/xmemo:get-started`, `/xmemo:brainstorm`, `/xmemo:plan-project`, `/xmemo:review-plan`, `/xmemo:audit-progress`, `/xmemo:distill-session`, `/xmemo:resume-work`, `/xmemo:handoff-work`, `/xmemo:memory-steward` |
| Role | Professional Skill suite + checkpoint Hook + hosted MCP |
| Service | `https://xmemo.dev` |
| MCP endpoint | `https://xmemo.dev/mcp` |
| Authentication | OAuth 2.0 + Dynamic Client Registration |
| Scopes | `memory:read memory:write` |
| Tools | XMemo Connector: 27 on every Claude surface; direct MCP configuration: 35; Skills call 17 |
| Repository | `https://github.com/yonro/xmemo-claude-plugin` |
| Directory state | Plugin published; connector under review |

## Links

- Product: https://xmemo.dev/product/mcp
- Documentation: https://xmemo.dev/docs
- Support: https://xmemo.dev/support
- Privacy: https://xmemo.dev/legal/privacy
- Terms: https://xmemo.dev/legal/tos

## License

[MIT](LICENSE) © 2026 Yonro.
