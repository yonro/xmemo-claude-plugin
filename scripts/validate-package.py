#!/usr/bin/env python3
"""Offline structural and safety validation for XMemo for Claude."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
MCP_CONFIG = ROOT / ".mcp.json"
SKILL = ROOT / "skills" / "xmemo-memory-steward" / "SKILL.md"

REQUIRED_FILES = {
    MANIFEST,
    MCP_CONFIG,
    SKILL,
    ROOT / "README.md",
    ROOT / "PRIVACY.md",
    ROOT / "SECURITY.md",
    ROOT / "LICENSE",
    ROOT / "CHANGELOG.md",
    ROOT / "assets" / "icon.png",
    ROOT / "skills" / "xmemo-memory-steward" / "references" / "memory-policy.md",
    ROOT / "skills" / "xmemo-memory-steward" / "references" / "review-playbooks.md",
    ROOT / "skills" / "xmemo-memory-steward" / "references" / "tool-routing.md",
    ROOT / "skills" / "xmemo-memory-steward" / "references" / "workflows.md",
}

EXPECTED_CLAUDE_TOOLS = {
    "add_expense",
    "analyze_memory_text",
    "complete_memory_todo",
    "create_memory_todo",
    "explain_memory",
    "forget",
    "get_mcp_identity",
    "get_monthly_ledger_summary",
    "list_ledger_transactions",
    "list_memory_todos",
    "memory_activity",
    "memory_overview",
    "memory_stats",
    "recall",
    "recall_context",
    "remember",
    "restore_memory",
    "search_memory",
    "update_memory",
}

FORBIDDEN_PUBLIC_TOOL_CLAIMS = {
    "forget_memory",
    "forget_current_memory",
    "delete_current_memory",
    "open_ledger",
    "open_project_workspace",
    "open_todo_board",
}

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
        "name": "xmemo-claude-plugin",
        "displayName": "XMemo for Claude",
        "version": "0.1.0",
        "license": "MIT",
        "skills": "./skills/",
        "mcpServers": "./.mcp.json",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            fail(errors, f"plugin.json {key!r} must be {value!r}")

    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
        fail(errors, "plugin.json version must be semantic x.y.z")

    author = manifest.get("author")
    if not isinstance(author, dict) or author.get("email") != "support@xmemo.dev":
        fail(errors, "plugin.json author.email must be support@xmemo.dev")


def validate_mcp(errors: list[str]) -> None:
    config = load_json(MCP_CONFIG, errors)
    server = config.get("mcpServers", {}).get("xmemo", {})
    if server.get("type") != "http":
        fail(errors, ".mcp.json xmemo.type must be 'http'")
    if server.get("url") != "https://xmemo.dev/mcp":
        fail(errors, ".mcp.json must use the production XMemo MCP endpoint")
    if server.get("oauth", {}).get("scopes") != "memory:read memory:write":
        fail(errors, ".mcp.json must request exactly memory:read memory:write")

    encoded = json.dumps(config).lower()
    for forbidden in ("api_key", "xmemokey", "bearer ", "client_secret", "password"):
        if forbidden in encoded:
            fail(errors, f".mcp.json must not contain credential field/text {forbidden!r}")


def validate_skill(errors: list[str]) -> None:
    text = SKILL.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        fail(errors, "SKILL.md must start with YAML frontmatter")
        return

    frontmatter = match.group(1)
    if not re.search(r"(?m)^name:\s*xmemo-memory-steward\s*$", frontmatter):
        fail(errors, "SKILL.md frontmatter name must be xmemo-memory-steward")
    if not re.search(r"(?m)^description:\s*\S", frontmatter):
        fail(errors, "SKILL.md frontmatter requires a non-empty description")

    routing = (
        ROOT
        / "skills"
        / "xmemo-memory-steward"
        / "references"
        / "tool-routing.md"
    ).read_text(encoding="utf-8")
    routed = set(re.findall(r"`([a-z][a-z0-9_]*)`", routing))
    missing = EXPECTED_CLAUDE_TOOLS - routed
    if missing:
        fail(errors, f"tool-routing.md is missing Claude tools: {sorted(missing)}")

    forbidden_claims = FORBIDDEN_PUBLIC_TOOL_CLAIMS & routed
    if forbidden_claims:
        fail(
            errors,
            "tool-routing.md must not advertise hidden/retired tools: "
            f"{sorted(forbidden_claims)}",
        )

    for reference in re.findall(r"`(references/[^`]+\.md)`", text):
        path = SKILL.parent / reference
        if not path.is_file():
            fail(errors, f"SKILL.md references missing file: {reference}")


def validate_secrets(errors: list[str]) -> None:
    text_extensions = {".json", ".md", ".py", ".yml", ".yaml"}
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file() or path.suffix not in text_extensions:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                fail(errors, f"Potential {label} in {path.relative_to(ROOT)}")


def main() -> int:
    errors: list[str] = []

    for path in sorted(REQUIRED_FILES):
        if not path.is_file():
            fail(errors, f"Missing required file: {path.relative_to(ROOT)}")

    if not errors:
        validate_manifest(errors)
        validate_mcp(errors)
        validate_skill(errors)
        validate_secrets(errors)

    if errors:
        print("XMemo Claude plugin validation FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("XMemo Claude plugin validation passed.")
    print(f"- manifest: {MANIFEST.relative_to(ROOT)}")
    print(f"- MCP endpoint: https://xmemo.dev/mcp")
    print(f"- Claude public tool contract documented: {len(EXPECTED_CLAUDE_TOOLS)} tools")
    print("- credential scan: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
