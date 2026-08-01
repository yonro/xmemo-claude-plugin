<div align="center">
  <a href="https://xmemo.dev/integrations/claude">
    <img src="https://cdn.jsdelivr.net/gh/yonro/xmemo-claude-plugin@main/assets/icon.png" alt="XMemo" width="112" />
  </a>

  <h1>XMemo for Claude</h1>

  <p><strong>Durable project memory and cross-agent continuity for Claude.</strong></p>
  <p>
    Recall the context behind the work, preserve verified decisions and progress,
    and hand projects across sessions without archiving raw conversations.
  </p>

  <p>
    <a href="https://github.com/yonro/xmemo-claude-plugin/actions/workflows/validate.yml"><img alt="Validation" src="https://img.shields.io/github/actions/workflow/status/yonro/xmemo-claude-plugin/validate.yml?branch=main&amp;style=flat-square&amp;logo=githubactions&amp;logoColor=white&amp;label=validation" /></a>
    <img alt="Plugin version" src="https://img.shields.io/badge/plugin-v1.0.0-8B5CF6?style=flat-square" />
    <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/yonro/xmemo-claude-plugin?style=flat-square" /></a>
    <a href="https://github.com/yonro/xmemo-claude-plugin/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/yonro/xmemo-claude-plugin?style=flat-square&amp;logo=github" /></a>
  </p>

  <p>
    <img alt="Claude plugin" src="https://img.shields.io/badge/Claude-plugin%20candidate-D97757?style=flat-square" />
    <img alt="Hosted MCP" src="https://img.shields.io/badge/MCP-hosted-06B6D4?style=flat-square" />
    <img alt="OAuth" src="https://img.shields.io/badge/auth-OAuth%202.0%20%2B%20DCR-10B981?style=flat-square" />
    <img alt="Tool surface" src="https://img.shields.io/badge/tool%20surface-16-8B5CF6?style=flat-square" />
  </p>

  <p>
    <a href="#quick-start">Quick start</a> ·
    <a href="#architecture">Architecture</a> ·
    <a href="#memory-workflow">Memory workflow</a> ·
    <a href="#tool-surface">Tool surface</a> ·
    <a href="#security-and-privacy">Security</a> ·
    <a href="#validation">Validation</a>
  </p>
</div>

---

The XMemo Claude plugin combines a reusable memory workflow with a hosted
[Model Context Protocol](https://code.claude.com/docs/en/mcp) connection.
Claude continues to reason, inspect, implement, and validate from the live
workspace; XMemo carries only the durable context that should survive the
current conversation.

> [!IMPORTANT]
> This repository is a public plugin review candidate. It does not claim
> approval or availability in Anthropic's official plugin directory.

## At a glance

| | |
|---|---|
| Display name | `XMemo` |
| Plugin ID | `xmemo` |
| Skills | Eight professional workflows under `/xmemo:*` |
| Automation | Fail-open lifecycle checkpoint Hook |
| Version | `1.0.0` |
| Bundle | Claude Skill suite + checkpoint Hook + hosted MCP configuration |
| MCP endpoint | `https://xmemo.dev/mcp` |
| Authentication | OAuth 2.0 with Dynamic Client Registration |
| Requested scopes | `memory:read memory:write` |
| Tool profile | Signed Claude Code profile, exactly 16 tools |
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
| [`/xmemo:brainstorm`](skills/brainstorm/SKILL.md) | Recall constraints, generate distinct options, challenge assumptions, converge, and preserve only approved outcomes |
| [`/xmemo:plan-project`](skills/plan-project/SKILL.md) | Design evidence-gated `PROJECT_PLAN.md` and `EXECUTION_PLAN.md` artifacts from XMemo context and the live project |
| [`/xmemo:review-plan`](skills/review-plan/SKILL.md) | Review a proposal against saved decisions and return a formal verdict plus acceptance gate |
| [`/xmemo:audit-progress`](skills/audit-progress/SKILL.md) | Separate verified work from partial, claimed, stale, conflicting, or blocked progress and optionally write a formal Markdown audit |
| [`/xmemo:distill-session`](skills/distill-session/SKILL.md) | Extract retrieval-ready decisions, context, TODOs, unresolved items, and checkpoints without archiving the transcript |
| [`/xmemo:resume-work`](skills/resume-work/SKILL.md) | Reconcile the latest checkpoint with current evidence and continue from one exact next action |
| [`/xmemo:handoff-work`](skills/handoff-work/SKILL.md) | Prepare or receive evidence-based handoffs across Claude sessions and compatible agents |
| [`/xmemo:memory-steward`](skills/memory-steward/SKILL.md) | Coordinate mixed workflows and memory lifecycle operations under the shared safety policy |

## Quick start

### Local review

Prerequisites:

- A current Claude Code release with plugin lifecycle Hooks and `PostToolBatch`.
- Node.js available as `node`; the official exec-form Hook pattern works across
  Windows, macOS, and Linux.
- An XMemo account.
- A browser for the OAuth authorization flow.

Clone and launch the plugin:

```bash
git clone https://github.com/yonro/xmemo-claude-plugin.git
claude --plugin-dir ./xmemo-claude-plugin
```

Inside Claude Code:

1. Run `/mcp` and select XMemo.
2. Complete browser-based OAuth authorization for `memory:read` and
   `memory:write`.
3. Invoke a focused workflow such as `/xmemo:resume-work`, use
   `/xmemo:memory-steward` for mixed memory work, or ask naturally:

```text
Bring me up to speed on this project using XMemo. Show the latest verified
state, active decisions, open TODOs, blocker, and exact next action.
```

After local plugin changes, run `/reload-plugins` or restart Claude Code.
Claude Code manages OAuth tokens outside this repository; no API key, client
secret, reviewer credential, or bearer token belongs in the package.

### Versioning

Marketplace releases use semantic versions from
`.claude-plugin/plugin.json`. Because an explicit version pins Claude Code's
plugin cache, every published update must increment that value. Git tags and
GitHub Releases use the same version; the first stable public release is `v1.0.0`.

Every tag matching `v*.*.*` runs the release workflow. The workflow rejects a
tag that does not match the manifest version, reruns the official and package
validators plus Hook tests, then publishes an immutable plugin ZIP and SHA-256
checksum to the corresponding GitHub Release. Release archives are generated by
CI; local ZIP files under `dist/` are disposable and must not be committed.

## Architecture

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/yonro/xmemo-claude-plugin@main/assets/claude-memory-flow.png" alt="XMemo Claude plugin architecture" width="980" />
</p>

The plugin has three complementary components:

| Component | Responsibility |
|---|---|
| `skills/*/SKILL.md` | Eight focused professional workflows sharing one XMemo safety and routing contract |
| `hooks/hooks.json` + `scripts/checkpoint-hook.js` | Detects checkpoint boundaries and interrupted work without reading or persisting transcripts |
| `.mcp.json` | Declares the hosted XMemo endpoint and pins the minimum OAuth scopes |

### Data path

1. Claude loads the focused Skill whose description matches the workflow, or
   `memory-steward` for mixed memory and lifecycle work.
2. The local lifecycle Hook records only bounded activity metadata under
   `CLAUDE_PLUGIN_DATA` and asks Claude to checkpoint only at a material boundary.
3. Claude Code connects to `https://xmemo.dev/mcp` over HTTPS.
4. The server advertises OAuth metadata and Claude Code performs Dynamic Client
   Registration plus browser authorization.
5. The signed OAuth client identity selects XMemo's isolated 16-tool Claude
   Code profile.
6. Each tool reads or writes only data authorized for the signed-in XMemo
   account and requested scope.
7. Claude reports the useful result without exposing tokens, internal traces,
   or unnecessary identifiers.

The package contains no XMemo service implementation, production credentials,
private memories, deployment scripts, or internal runbooks.

## Memory workflow

### At task start

1. Recall only context that could materially change the current work.
2. Prefer bounded project context or a restart checkpoint over broad history.
3. Treat the live workspace and current evidence as canonical when memory is
   stale or conflicts with reality.

### During work

1. Separate tentative ideas from confirmed decisions.
2. Save durable conclusions, not verbose reasoning or raw transcripts.
3. Record unresolved choices as pending decisions.
4. Maintain the active objective, verified state, blocker, and next action.
5. Update existing memory instead of creating near-duplicates.

### Automatic checkpoint guard

The Hook does not write a memory after every tool call. It marks local activity
and asks Claude to continue once when one of these boundaries is reached:

- a tracked task is completed;
- context is about to be compacted;
- verified implementation work has reached a material stage;
- sustained work crosses the activity or time threshold;
- the previous session ended or failed with unsaved work.

Claude then decides from the current verified context whether `update_state` is
warranted. A successful `update_state` clears the pending marker. `record_event`
remains reserved for significant milestones and handoffs. If XMemo is unavailable
or no durable change exists, the Hook fails open and never fabricates a save.

The Hook never opens `transcript_path`, does not inspect prompt, message, or tool
response content, and never persists source contents, credentials, or raw
transcripts.

### At handoff

1. Preserve what changed and what was actually verified.
2. Include decisions, artifacts, constraints, remaining work, and blockers.
3. Finish with one exact next action another session or agent can execute.

## Tool surface

The signed Claude Code profile exposes exactly 16 tools:

| Area | Tools |
|---|---|
| Identity | `get_mcp_identity` |
| Recall and explanation | `recall`, `search_memory`, `recall_context`, `explain_memory` |
| Memory lifecycle | `remember`, `update_memory`, `forget`, `restore_memory` |
| Project context | `get_project_context`, `project` |
| Decisions | `create_pending_decision`, `resolve_decision` |
| Work tracking | `todo`, `update_state`, `record_event` |

The profile exposes zero MCP resources and no widget UI. It excludes Ledger,
aggregate analytics, ChatGPT widgets, bulk TODO deletion, and hidden legacy
aliases. The separately submitted Claude Directory Connector has an independent
19-tool contract and is not changed by this plugin.

## Capabilities and boundaries

| Capability | Included | Boundary |
|---|:---:|---|
| Hosted XMemo MCP connection | Yes | Requires user OAuth authorization |
| Professional memory Skill suite | Yes | Eight focused workflows activate only for relevant requests |
| Automatic checkpoint guard | Yes | Lifecycle metadata only; semantic writes remain Skill-governed |
| Recall and search | Yes | Limited to the signed-in account and scopes |
| Durable writes and working state | Yes | Performed only when requested by the user or active workflow |
| Project creation | Yes | Only after an explicit formal-project request |
| Recoverable deletion | Yes | `forget` is soft delete by default |
| Permanent deletion | Yes | Requires an explicit irreversible request and exact target |
| Cross-agent continuity | Yes | Other agents require their own authorized XMemo connection |
| Custom UI or widgets | No | The plugin is Skill + MCP only |
| Local memory database | No | Memory remains in the XMemo service |
| Private service code | No | This repository is intentionally reviewable |
| Official directory approval | No | Pending official review |

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
skills/brainstorm/SKILL.md                 Memory-grounded ideation and convergence
skills/plan-project/SKILL.md               Project and execution-plan design
skills/review-plan/SKILL.md                Formal plan review and acceptance gates
skills/audit-progress/SKILL.md             Evidence-based progress audit
skills/distill-session/SKILL.md            Important-session distillation
skills/resume-work/SKILL.md                Deterministic recovery and continuation
skills/handoff-work/SKILL.md               Cross-session and cross-agent handoff
skills/memory-steward/SKILL.md             Mixed workflow and lifecycle safety policy
skills/plan-project/assets/                Project and execution-plan templates
skills/plan-project/references/            Plan quality and evidence gates
skills/audit-progress/assets/              Development-progress audit template
skills/memory-steward/references/          Tool routing and focused playbooks
PRIVACY.md                                 Data-flow and user-control summary
SECURITY.md                                Credential and review boundaries
CHANGELOG.md                               Release history
LICENSE                                    MIT license
```

Only `plugin.json` lives inside `.claude-plugin/`. Skills, MCP configuration,
assets, examples, and public documentation remain at the plugin root.

## Validation

Run the repository validator:

```powershell
python scripts/validate-package.py
```

It verifies:

- manifest identity, display name, SemVer, and package paths;
- hosted endpoint and exact OAuth scope pin;
- the signed 16-tool routing contract;
- the exact eight-Skill suite, frontmatter, workflow markers, templates, and referenced playbooks;
- required public documents and parseable assets;
- exact Hook lifecycle events, exec-form command safety, and no transcript/network access;
- common committed-secret patterns.

Run the deterministic Hook tests:

```powershell
node scripts/test-checkpoint-hook.js
```

Then run Claude Code's official strict validator:

```powershell
claude plugin validate D:\repos\xmemo-claude-plugin --strict
```

Synthetic evaluation prompts are maintained in
[examples/workflow-prompts.md](examples/workflow-prompts.md).

## Security and privacy

- OAuth tokens stay in Claude Code's credential storage.
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

## Review status

This repository is prepared for public validation and future official plugin
review. Release claims remain evidence-based:

- plugin manifest: present;
- eight-Skill professional workflow bundle: present;
- seven-event checkpoint Hook and regression tests: present;
- OAuth MCP configuration: present;
- isolated 16-tool server contract: verified;
- MCP resources and widget UI: absent;
- package validator and CI: present;
- synthetic workflow prompts: present;
- official directory approval: **not claimed**.

## Agent-readable metadata

| Field | Value |
|---|---|
| Package repository | `yonro/xmemo-claude-plugin` |
| Runtime | Claude Code |
| Plugin ID | `xmemo` |
| Display name | `XMemo` |
| Skill commands | `/xmemo:brainstorm`, `/xmemo:plan-project`, `/xmemo:review-plan`, `/xmemo:audit-progress`, `/xmemo:distill-session`, `/xmemo:resume-work`, `/xmemo:handoff-work`, `/xmemo:memory-steward` |
| Role | Professional Skill suite + checkpoint Hook + hosted MCP |
| Service | `https://xmemo.dev` |
| MCP endpoint | `https://xmemo.dev/mcp` |
| Authentication | OAuth 2.0 + Dynamic Client Registration |
| Scopes | `memory:read memory:write` |
| Tool profile | `claude-plugin` — 16 tools, 0 resources |
| Repository | `https://github.com/yonro/xmemo-claude-plugin` |
| Review state | Candidate; no official approval claim |

## Links

- Product: https://xmemo.dev/product/mcp
- Documentation: https://xmemo.dev/docs
- Support: https://xmemo.dev/support
- Privacy: https://xmemo.dev/legal/privacy
- Terms: https://xmemo.dev/legal/tos

## License

[MIT](LICENSE) © 2026 Yonro.
