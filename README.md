<div align="center">
  <a href="https://xmemo.dev">
    <img src="https://cdn.jsdelivr.net/gh/yonro/xmemo-claude-plugin@main/assets/icon.png" alt="XMemo" width="112" />
  </a>

  <h1>XMemo</h1>

  <p><strong>Durable project memory and cross-agent continuity for Claude.</strong></p>
  <p>
    Recall the context behind the work, preserve verified decisions and progress,
    and hand projects across sessions without archiving raw conversations.
  </p>

  <p>
    <a href="https://github.com/yonro/xmemo-claude-plugin/actions/workflows/validate.yml"><img alt="Validation" src="https://img.shields.io/github/actions/workflow/status/yonro/xmemo-claude-plugin/validate.yml?branch=main&amp;style=flat-square&amp;logo=githubactions&amp;logoColor=white&amp;label=validation" /></a>
    <img alt="Plugin version" src="https://img.shields.io/badge/plugin-v0.1.0-8B5CF6?style=flat-square" />
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
| Skill | `/xmemo:memory-steward` |
| Version | `0.1.0` |
| Bundle | Claude Skill + hosted MCP configuration |
| MCP endpoint | `https://xmemo.dev/mcp` |
| Authentication | OAuth 2.0 with Dynamic Client Registration |
| Requested scopes | `memory:read memory:write` |
| Tool profile | Signed Claude Code profile, exactly 16 tools |
| MCP resources | None |
| Local memory storage | None in this repository |
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
- **Cross-agent handoff** — preserve provenance, blockers, remaining work, and
  one exact next action for another compatible agent.
- **User-controlled lifecycle** — search, update, soft-delete, restore, and
  explicitly hard-delete eligible memories.

## Quick start

### Local review

Prerequisites:

- Claude Code 2.1.143 or later.
- An XMemo account.
- A browser for the OAuth authorization flow.

Clone and launch the plugin:

```powershell
git clone https://github.com/yonro/xmemo-claude-plugin.git
claude --plugin-dir D:\repos\xmemo-claude-plugin
```

Inside Claude Code:

1. Run `/mcp` and select XMemo.
2. Complete browser-based OAuth authorization for `memory:read` and
   `memory:write`.
3. Invoke `/xmemo:memory-steward`, or ask naturally:

```text
Bring me up to speed on this project using XMemo. Show the latest verified
state, active decisions, open TODOs, blocker, and exact next action.
```

After local plugin changes, run `/reload-plugins` or restart Claude Code.
Claude Code manages OAuth tokens outside this repository; no API key, client
secret, reviewer credential, or bearer token belongs in the package.

## Architecture

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/yonro/xmemo-claude-plugin@main/assets/claude-memory-flow.svg" alt="XMemo Claude plugin architecture" width="980" />
</p>

The plugin has two complementary components:

| Component | Responsibility |
|---|---|
| `skills/memory-steward/SKILL.md` | Teaches Claude when to recall, distill, checkpoint, review, resume, and hand off work |
| `.mcp.json` | Declares the hosted XMemo endpoint and pins the minimum OAuth scopes |

### Data path

1. Claude loads the `memory-steward` Skill when the request benefits from
   durable context or the user invokes it directly.
2. Claude Code connects to `https://xmemo.dev/mcp` over HTTPS.
3. The server advertises OAuth metadata and Claude Code performs Dynamic Client
   Registration plus browser authorization.
4. The signed OAuth client identity selects XMemo's isolated 16-tool Claude
   Code profile.
5. Each tool reads or writes only data authorized for the signed-in XMemo
   account and requested scope.
6. Claude reports the useful result without exposing tokens, internal traces,
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
| Memory workflow Skill | Yes | Activates only for relevant requests |
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
assets/claude-memory-flow.svg              README architecture diagram
examples/workflow-prompts.md               Synthetic evaluation prompts
scripts/validate-package.py                Zero-dependency package validator
skills/memory-steward/SKILL.md             Memory workflow and safety policy
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
- Skill frontmatter and referenced playbooks;
- required public documents and parseable assets;
- common committed-secret patterns.

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
- Skill bundle: present;
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
| Skill command | `/xmemo:memory-steward` |
| Role | Skill + hosted MCP |
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
