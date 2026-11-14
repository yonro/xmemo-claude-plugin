#!/usr/bin/env python3
"""Offline structural and safety validation for the XMemo Claude plugin."""

from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
MCP_CONFIG = ROOT / ".mcp.json"
SKILLS_ROOT = ROOT / "skills"

# The Anthropic Directory accepts hooks of any type, scripts, and files outside a
# short list of types only from Verified organizations. The plugin ships Skills,
# documents, images, and the MCP configuration only.
ALLOWED_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".json", ".yaml", ".yml",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
ALLOWED_PLAIN_NAMES = {"LICENSE", "README", ".gitignore"}
# Repository-only paths that never reach the release artifact (release-policy.json).
REPO_ONLY_PARTS = {".git", ".github", "docs", "scripts"}
REPO_ONLY_FILES = {".gitattributes", ".gitignore"}
HOOK_MANIFEST_KEYS = {"hooks"}

EXPECTED_SKILLS = {
    "audit-progress",
    "brainstorm",
    "checkpoint",
    "distill-session",
    "get-started",
    "handoff-work",
    "memory-steward",
    "plan-project",
    "resume-work",
    "review-plan",
}

FOCUSED_SKILL_MARKERS = {
    "audit-progress": {"verified", "claimed", "update_state"},
    "brainstorm": {"diverge", "converge", "remember"},
    "checkpoint": {"update_state", "XMemo checkpoint:", "exact next action"},
    "distill-session": {"raw transcript", "preview", "update_memory"},
    "get-started": {"get_mcp_identity", "## XMemo memory", "original task"},
    "handoff-work": {"provenance", "exact next action", "record_event"},
    "plan-project": {"PROJECT_PLAN.md", "EXECUTION_PLAN.md", "acceptance gate"},
    "resume-work": {"Resume Brief", "reconcile", "get_project_context"},
    "review-plan": {"Verdict", "acceptance gate", "approved"},
}

EXPECTED_CLAUDE_TOOLS = {
    "create_pending_decision",
    "explain_memory",
    "forget",
    "get_mcp_identity",
    "get_project_context",
    "project",
    "read_memory",
    "recall",
    "recall_context",
    "record_event",
    "remember",
    "resolve_decision",
    "restore_memory",
    "search_memory",
    "todo",
    "update_memory",
    "update_state",
}

FORBIDDEN_PUBLIC_TOOL_CLAIMS = {
    "forget_memory",
    "forget_current_memory",
    "delete_current_memory",
    "open_ledger",
    "open_project_workspace",
    "open_todo_board",
    "add_expense",
    "analyze_memory_text",
    "complete_memory_todo",
    "create_memory_todo",
    "get_monthly_ledger_summary",
    "list_ledger_transactions",
    "list_memory_todos",
    "memory_activity",
    "memory_overview",
    "memory_stats",
}

REQUIRED_FILES = {
    MANIFEST,
    MCP_CONFIG,
    ROOT / "README.md",
    ROOT / "PRIVACY.md",
    ROOT / "SECURITY.md",
    ROOT / "LICENSE",
    ROOT / "CHANGELOG.md",
    ROOT / "assets" / "icon.png",
    ROOT / "assets" / "claude-memory-flow.png",
    ROOT / "examples" / "workflow-prompts.md",
    ROOT / "skills" / "audit-progress" / "assets" / "progress-audit-template.md",
    ROOT / "skills" / "plan-project" / "assets" / "execution-plan-template.md",
    ROOT / "skills" / "plan-project" / "assets" / "project-plan-template.md",
    ROOT / "skills" / "plan-project" / "references" / "plan-quality-gates.md",
    ROOT / "skills" / "memory-steward" / "references" / "memory-policy.md",
    ROOT / "skills" / "memory-steward" / "references" / "review-playbooks.md",
    ROOT / "skills" / "memory-steward" / "references" / "tool-routing.md",
    ROOT / "skills" / "memory-steward" / "references" / "workflows.md",
} | {SKILLS_ROOT / name / "SKILL.md" for name in EXPECTED_SKILLS}

SECRET_PATTERNS = {
    "OpenAI-style API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub personal access token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "JWT-like bearer token": re.compile(
        r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"
    ),
    "embedded password assignment": re.compile(
        r"(?im)^\s*(?:password|passwd|pwd)\s*[:=]\s*[^<\s][^\r\n]{7,}$"
    ),
}

# Skills use only the plugin's own OAuth connection, never the claude.ai
# Connector's tools (mcp__claude_ai_*) or its credentials.
FOREIGN_CONNECTION_TOOL = re.compile(r"claude_ai_", re.IGNORECASE)

# The Directory policy check held 1.0.11 for "Uses a credential from the user's
# machine" although the plugin reads none. Shipped text therefore says "sign-in
# details" (defined in memory-policy.md) and never names specific kinds.
SENSITIVE_WORDING = re.compile(
    r"\b(?:tokens?|api[ _-]?keys?|credentials?|secrets?|passwords?|passwd|bearer|"
    r"cookies?|keychain|private keys?|authorization (?:codes?|data)|mfa)\b",
    re.IGNORECASE,
)

# The same check held 1.0.12 (MCP_FORWARDS_CREDENTIAL_ENV) on plugin.json, whose
# only dollar-prefixed name was the editor-only schema key. Shipped files carry
# no dollar-prefixed name at all, so nothing can look like an environment read.
DOLLAR_NAME = re.compile(r"\$(?:\{|\(|[A-Za-z_])")

PROFILE = "repo"


def configure(root: Path, profile: str) -> None:
    """Point the validator at another plugin root, such as a staged release tree.

    The "directory" profile validates the claude-directory artifact, which carries
    the runtime plugin without repository-only development files.
    """
    global ROOT, MANIFEST, MCP_CONFIG, SKILLS_ROOT, REQUIRED_FILES, PROFILE
    old_root = ROOT
    ROOT = root.resolve()
    MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
    MCP_CONFIG = ROOT / ".mcp.json"
    SKILLS_ROOT = ROOT / "skills"
    REQUIRED_FILES = {ROOT / path.relative_to(old_root) for path in REQUIRED_FILES}
    PROFILE = profile


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"Invalid JSON at {path.relative_to(ROOT)}: {exc}")
        return {}


def validate_manifest(errors: list[str]) -> None:
    manifest = load_json(MANIFEST, errors)
    expected = {
        "name": "xmemo",
        "displayName": "XMemo",
        "license": "MIT",
        "skills": "./skills/",
        "mcpServers": "./.mcp.json",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            fail(errors, f"plugin.json {key!r} must be {value!r}")

    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
        fail(errors, "plugin.json version must be semantic x.y.z")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    version = str(manifest.get("version", ""))
    if not re.search(rf"(?m)^## {re.escape(version)}(?:\s|$)", changelog):
        fail(errors, f"CHANGELOG.md must contain a release heading for {version}")

    author = manifest.get("author")
    if not isinstance(author, dict) or author.get("email") != "support@xmemo.dev":
        fail(errors, "plugin.json author.email must be support@xmemo.dev")


def validate_mcp(errors: list[str]) -> None:
    config = load_json(MCP_CONFIG, errors)
    server = config.get("mcpServers", {}).get("xmemo", {})
    expected_config = {"mcpServers": {"xmemo": {
        "type": "http", "url": "https://xmemo.dev/mcp",
        "oauth": {"scopes": "memory:read memory:write knowledge:read"},
    }}}
    if config != expected_config:
        fail(errors, ".mcp.json must contain only the approved OAuth server fields")
    if server.get("type") != "http":
        fail(errors, ".mcp.json xmemo.type must be 'http'")
    if server.get("url") != "https://xmemo.dev/mcp":
        fail(errors, ".mcp.json must use the production XMemo MCP endpoint")
    if server.get("oauth", {}).get("scopes") != "memory:read memory:write knowledge:read":
        fail(errors, ".mcp.json must request exactly memory:read memory:write knowledge:read")

    encoded = json.dumps(config).lower()
    for forbidden in ("api_key", "xmemokey", "bearer ", "client_secret", "password"):
        if forbidden in encoded:
            fail(errors, f".mcp.json must not contain credential field/text {forbidden!r}")


def candidate_files() -> list[Path]:
    """Tracked files in a repository checkout; every file in a staged artifact."""
    if PROFILE == "repo":
        try:
            listed = subprocess.run(
                ["git", "-C", str(ROOT), "ls-files", "-z"],
                check=True, capture_output=True,
            ).stdout.decode("utf-8")
            return sorted(ROOT / name for name in listed.split("\0") if name)
        except (OSError, subprocess.CalledProcessError):
            pass
    return sorted(ROOT.rglob("*"))


def runtime_files() -> list[Path]:
    """Every file that ships in the plugin, skipping repository-only paths."""
    files = []
    for path in candidate_files():
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative.parts[0] == ".git":
            continue
        if PROFILE == "repo" and (
            relative.parts[0] in REPO_ONLY_PARTS or str(relative) in REPO_ONLY_FILES
        ):
            continue
        files.append(path)
    return files


def validate_no_hooks(errors: list[str]) -> None:
    manifest = load_json(MANIFEST, errors)
    for key in sorted(HOOK_MANIFEST_KEYS & set(manifest)):
        fail(errors, f"plugin.json must not declare {key!r}: the plugin ships no hooks")
    for path in runtime_files():
        relative = path.relative_to(ROOT)
        if relative.parts[0] == "hooks" or path.name in ("hooks.json", "monitors.json"):
            fail(
                errors,
                f"{relative.as_posix()} defines hooks; the Anthropic Directory accepts "
                "hooks of any type only from Verified organizations",
            )


def validate_file_types(errors: list[str]) -> None:
    for path in runtime_files():
        relative = path.relative_to(ROOT).as_posix()
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS and path.name not in ALLOWED_PLAIN_NAMES:
            fail(errors, f"{relative} is not an allowed file type for the Anthropic Directory")
        data = path.read_bytes()
        if data.startswith(b"#!"):
            fail(errors, f"{relative} must not start with #!")
        if suffix not in IMAGE_EXTENSIONS:
            if b"\0" in data:
                fail(errors, f"{relative} must not contain NUL bytes")
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                fail(errors, f"{relative} must be UTF-8 text")
        if relative.startswith(".claude-plugin/") and relative != ".claude-plugin/plugin.json":
            fail(errors, f"{relative}: .claude-plugin may hold only plugin.json")


def validate_neutral_wording(errors: list[str]) -> None:
    for path in runtime_files():
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            continue
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            match = SENSITIVE_WORDING.search(line)
            if match:
                fail(
                    errors,
                    f"{relative}:{number} names {match.group(0)!r}; "
                    "say 'sign-in details' instead",
                )
            if DOLLAR_NAME.search(line):
                fail(
                    errors,
                    f"{relative}:{number} has a dollar-prefixed name, which the "
                    "Directory can read as an environment variable",
                )


def validate_connection_ownership(errors: list[str]) -> None:
    runtime_files = [
        MANIFEST,
        MCP_CONFIG,
        ROOT / "README.md",
        ROOT / "PRIVACY.md",
        ROOT / "SECURITY.md",
        *sorted(SKILLS_ROOT.rglob("*.md")),
        *sorted((ROOT / "examples").rglob("*.md")),
    ]
    for path in runtime_files:
        if FOREIGN_CONNECTION_TOOL.search(path.read_text(encoding="utf-8")):
            fail(
                errors,
                f"{path.relative_to(ROOT)} must not route through the claude.ai "
                "Connector (claude_ai_*); use only the plugin's own connection",
            )


def parse_frontmatter(path: Path, errors: list[str]) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        fail(errors, f"{path.relative_to(ROOT)} must start with YAML frontmatter")
        return {}, text

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            fail(errors, f"Invalid frontmatter line in {path.relative_to(ROOT)}: {line!r}")
            continue
        fields[key.strip()] = value.strip()
    return fields, text


def validate_skills(errors: list[str]) -> None:
    actual_skills = {
        path.parent.name for path in SKILLS_ROOT.glob("*/SKILL.md") if path.is_file()
    }
    if actual_skills != EXPECTED_SKILLS:
        fail(
            errors,
            "skills/ must contain the exact professional Skill suite; "
            f"expected={sorted(EXPECTED_SKILLS)}, actual={sorted(actual_skills)}",
        )

    combined_skill_text = ""
    for name in sorted(EXPECTED_SKILLS):
        path = SKILLS_ROOT / name / "SKILL.md"
        fields, text = parse_frontmatter(path, errors)
        combined_skill_text += "\n" + text

        if set(fields) != {"name", "description"}:
            fail(
                errors,
                f"{path.relative_to(ROOT)} frontmatter must contain only name and description",
            )
        if fields.get("name") != name:
            fail(errors, f"{path.relative_to(ROOT)} frontmatter name must be {name}")
        if not fields.get("description"):
            fail(errors, f"{path.relative_to(ROOT)} requires a non-empty description")
        if re.search(r"(?mi)^\s*(?:[-*]\s*)?TODO(?:\s*[:\[])\s*", text):
            fail(errors, f"{path.relative_to(ROOT)} contains an unfinished TODO marker")

        for reference in re.findall(r"`((?:\.\./|references/)[^`]+\.md)`", text):
            resolved = (path.parent / reference).resolve()
            if not resolved.is_file():
                fail(
                    errors,
                    f"{path.relative_to(ROOT)} references missing file: {reference}",
                )

        for marker in FOCUSED_SKILL_MARKERS.get(name, set()):
            if marker.lower() not in text.lower():
                fail(errors, f"{path.relative_to(ROOT)} is missing workflow marker {marker!r}")

    routing = (
        SKILLS_ROOT / "memory-steward" / "references" / "tool-routing.md"
    ).read_text(encoding="utf-8")
    routed = set(re.findall(r"`([a-z][a-z0-9_]*)`", routing))
    missing = EXPECTED_CLAUDE_TOOLS - routed
    if missing:
        fail(errors, f"tool-routing.md is missing Claude tools: {sorted(missing)}")

    forbidden_routing_claims = FORBIDDEN_PUBLIC_TOOL_CLAIMS & routed
    if forbidden_routing_claims:
        fail(
            errors,
            "tool-routing.md must not route to tools outside the Skill set: "
            f"{sorted(forbidden_routing_claims)}",
        )

    forbidden_skill_claims = {
        name
        for name in FORBIDDEN_PUBLIC_TOOL_CLAIMS
        if re.search(rf"`{re.escape(name)}`", combined_skill_text)
    }
    if forbidden_skill_claims:
        fail(
            errors,
            "Skill suite must not route to tools outside the Skill set: "
            f"{sorted(forbidden_skill_claims)}",
        )


def validate_assets_and_readme(errors: list[str]) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    icon = ROOT / "assets" / "icon.png"
    diagram_png = ROOT / "assets" / "claude-memory-flow.png"

    png = icon.read_bytes()
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        fail(errors, "assets/icon.png must be a valid PNG")
    elif len(png) < 24:
        fail(errors, "assets/icon.png is truncated")
    else:
        width, height = struct.unpack(">II", png[16:24])
        if width != height:
            fail(errors, "assets/icon.png must be square")

    rendered_diagram = diagram_png.read_bytes()
    if rendered_diagram[:8] != b"\x89PNG\r\n\x1a\n" or len(rendered_diagram) < 24:
        fail(errors, "assets/claude-memory-flow.png must be a valid PNG")
    else:
        width, height = struct.unpack(">II", rendered_diagram[16:24])
        if (width, height) != (1200, 420):
            fail(errors, "assets/claude-memory-flow.png must be 1200 x 420 px")

    required_readme_references = {
        "assets/icon.png",
        "assets/claude-memory-flow.png",
        "examples/workflow-prompts.md",
        "PRIVACY.md",
        "SECURITY.md",
        "CHANGELOG.md",
    } | {f"skills/{name}/SKILL.md" for name in EXPECTED_SKILLS}
    for removed in ("scripts/checkpoint-hook.js", "hooks/hooks.json", "claude-memory-flow.svg"):
        if removed in readme:
            fail(errors, f"README.md must not reference {removed}, which the plugin no longer ships")
    for reference in sorted(required_readme_references):
        if reference not in readme:
            fail(errors, f"README.md is missing required reference: {reference}")

    expected_cdn = "cdn.jsdelivr.net/gh/yonro/xmemo-claude-plugin@main/assets/"
    if expected_cdn not in readme:
        fail(errors, "README.md must use the public CDN asset path")


def validate_secrets(errors: list[str]) -> None:
    text_extensions = {".json", ".js", ".md", ".py", ".yml", ".yaml"}
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file() or path.suffix not in text_extensions:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                fail(errors, f"Potential {label} in {path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="plugin root to validate (default: this repository)")
    parser.add_argument(
        "--profile",
        choices=("repo", "directory"),
        default="repo",
        help="repo validates the development repository; directory validates the release artifact",
    )
    args = parser.parse_args()
    if args.root is not None or args.profile != "repo":
        configure(args.root or ROOT, args.profile)

    errors: list[str] = []

    for path in sorted(REQUIRED_FILES):
        if not path.is_file():
            fail(errors, f"Missing required file: {path.relative_to(ROOT)}")

    if not errors:
        validate_manifest(errors)
        validate_mcp(errors)
        validate_no_hooks(errors)
        validate_file_types(errors)
        validate_neutral_wording(errors)
        validate_connection_ownership(errors)
        validate_skills(errors)
        validate_assets_and_readme(errors)
        validate_secrets(errors)

    if errors:
        print("XMemo Claude plugin validation FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("XMemo Claude plugin validation passed.")
    print(f"- manifest: {MANIFEST.relative_to(ROOT)}")
    print("- MCP endpoint: https://xmemo.dev/mcp")
    print(f"- professional Skill suite documented: {len(EXPECTED_SKILLS)} skills")
    print("- hooks: none; checkpoints come from the Skills")
    print("- shipped file types: Markdown, text, JSON, YAML, and allowed images only")
    print(f"- Skill tool routing documented: {len(EXPECTED_CLAUDE_TOOLS)} tools")
    print("- credential scan: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
