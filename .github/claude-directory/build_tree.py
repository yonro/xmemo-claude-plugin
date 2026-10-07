#!/usr/bin/env python3
"""Build and gate the claude-directory release tree for the XMemo Claude plugin.

The tree is assembled with git plumbing from an explicit source commit: no checkout,
no merge, and file bytes are the source blobs. Ref updates are left to the workflow.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
POLICY_PATH = HERE / "release-policy.json"
COMPAT_PATH = HERE / "directory-compat.json"
MANIFEST_PATH = ".claude-plugin/plugin.json"

REGULAR_MODES = {"100644", "100755"}
SEMVER = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")
FULL_SHA = re.compile(r"[0-9a-f]{40}")
BINARY_SIGNATURES = (
    ("PNG", lambda b: b.startswith(b"\x89PNG\r\n\x1a\n")),
    ("JPEG", lambda b: b.startswith(b"\xff\xd8\xff")),
    ("GIF", lambda b: b[:6] in (b"GIF87a", b"GIF89a")),
    ("WebP", lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP"),
    ("WOFF", lambda b: b[:4] in (b"wOFF", b"wOF2")),
    ("TrueType/OpenType", lambda b: b[:4] in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"ttcf")),
)
OS_JUNK = {".DS_Store", "Thumbs.db", "desktop.ini"}
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {
    f"LPT{i}" for i in range(1, 10)
}


class GateError(Exception):
    """A release gate failed."""


# --- git helpers ----------------------------------------------------------------


def git(*args: str, data: bytes | None = None, env: dict | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-c", "core.autocrlf=false", "-c", "core.safecrlf=false", *args],
        input=data,
        capture_output=True,
        env=env,
    )
    if result.returncode != 0:
        raise GateError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def git_text(*args: str, env: dict | None = None) -> str:
    return git(*args, env=env).decode().strip()


def resolve_commit(rev: str) -> str:
    return git_text("rev-parse", "--verify", f"{rev}^{{commit}}")


def list_tree(rev: str) -> list[tuple[str, str, str, str]]:
    """Return (mode, type, oid, path) for every entry of a commit or tree."""
    entries = []
    for record in git("ls-tree", "-r", "-z", "--full-tree", rev).split(b"\0"):
        if not record:
            continue
        meta, path = record.split(b"\t", 1)
        mode, kind, oid = meta.decode().split()
        entries.append((mode, kind, oid, path.decode()))
    return entries


# --- policy ---------------------------------------------------------------------


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def compile_patterns(patterns: list[str]) -> list[tuple[str, re.Pattern[str]]]:
    return [(p, glob_to_regex(p)) for p in patterns]


def first_match(path: str, compiled: list[tuple[str, re.Pattern[str]]]) -> str | None:
    for pattern, regex in compiled:
        if regex.match(path):
            return pattern
    return None


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify(entries, policy: dict) -> dict:
    include = compile_patterns(policy["include"])
    exclude = compile_patterns(policy["exclude"])
    forbidden = compile_patterns(policy["forbidden"])
    result = {"included": [], "excluded": [], "forbidden": [], "unclassified": [], "conflicts": []}
    for entry in entries:
        path = entry[3]
        hit_forbidden = first_match(path, forbidden)
        hit_include = first_match(path, include)
        hit_exclude = first_match(path, exclude)
        if hit_forbidden:
            result["forbidden"].append(f"{path} (matches {hit_forbidden})")
        elif hit_include and hit_exclude:
            result["conflicts"].append(f"{path} (include {hit_include} / exclude {hit_exclude})")
        elif hit_include:
            result["included"].append(entry)
        elif hit_exclude:
            result["excluded"].append(path)
        else:
            result["unclassified"].append(path)
    return result


def assert_classified(result: dict) -> None:
    problems = []
    for key, label in (
        ("forbidden", "forbidden file in source"),
        ("conflicts", "path matches both include and exclude"),
        ("unclassified", "path not classified by release-policy.json"),
    ):
        problems += [f"{label}: {item}" for item in result[key]]
    if problems:
        raise GateError("release policy gate failed:\n  " + "\n  ".join(problems))


def write_tree(entries) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(tmp, "index"))
        spec = b"".join(f"{mode} {oid}\t{path}".encode() + b"\0" for mode, _, oid, path in entries)
        git("update-index", "-z", "--index-info", data=spec, env=env)
        return git_text("write-tree", env=env)


def build(source: str, policy: dict) -> tuple[str, dict]:
    result = classify(list_tree(source), policy)
    assert_classified(result)
    return write_tree(result["included"]), result


def export_tree(tree: str, stage: Path) -> None:
    stage.mkdir(parents=True, exist_ok=True)
    if any(stage.iterdir()):
        raise GateError(f"stage directory is not empty: {stage}")
    archive = tarfile.open(fileobj=io.BytesIO(git("archive", "--format=tar", tree)))
    for member in archive.getmembers():
        target = (stage / member.name).resolve()
        if not str(target).startswith(str(stage.resolve())):
            raise GateError(f"refusing to extract outside stage: {member.name}")
    if hasattr(tarfile, "data_filter"):
        archive.extractall(stage, filter="data")
    else:
        archive.extractall(stage)


# --- Anthropic Directory compatibility gates -------------------------------------


def detect_binary(data: bytes) -> str | None:
    """Return a format name for allowed binaries, '' for text, None for disallowed binary."""
    for name, check in BINARY_SIGNATURES:
        if check(data):
            return name
    if b"\0" in data:
        return None
    try:
        data.decode("utf-8")
        return ""
    except UnicodeDecodeError:
        return None


def readme_words(text: str) -> int:
    text = re.sub(r"(?ms)^(```|~~~).*?^\1", " ", text)
    return len(re.findall(r"[^\s|#*>`\-]+", text))


def compat_findings(tree: str, compat: dict) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    rules = compat["rules"]
    entries = list_tree(tree)
    blobs = {path: git("cat-file", "blob", oid) for mode, kind, oid, path in entries if kind == "blob"}

    for mode, kind, oid, path in entries:
        name = PurePosixPath(path).name
        if name == ".gitattributes" and re.search(rb"export-ignore|export-subst|\bfilter\s*=", blobs.get(path, b"")):
            findings.append(("DC-01", f"{path} uses an attribute the Directory rejects"))
        if name in OS_JUNK or "__MACOSX" in PurePosixPath(path).parts:
            findings.append(("DC-02", f"{path} is an OS system file"))
        if kind != "blob" or mode not in REGULAR_MODES:
            findings.append(("DC-03", f"{path} has mode {mode} ({kind}); only regular files are allowed"))
        elif blobs[path].startswith(b"version https://git-lfs.github.com/spec/"):
            findings.append(("DC-03", f"{path} is a Git LFS pointer"))

    seen: dict[str, str] = {}
    for path in [e[3] for e in entries]:
        for part in PurePosixPath(path).parts:
            stem = part.split(".")[0].upper()
            if (
                re.search(r'[<>:"|?*\x00-\x1f]', part)
                or part.endswith((".", " "))
                or stem in WINDOWS_RESERVED
            ):
                findings.append(("DC-04", f"{path}: name {part!r} is not portable"))
        folded = path.lower()
        if folded in seen and seen[folded] != path:
            findings.append(("DC-04", f"{path} collides with {seen[folded]} by case only"))
        seen[folded] = path

    limits = rules["DC-05"]["params"]
    if len(blobs) > limits["max_files"]:
        findings.append(("DC-05", f"{len(blobs)} files exceeds {limits['max_files']}"))
    for path, data in blobs.items():
        kind = detect_binary(data)
        if kind is None:
            findings.append(("DC-06", f"{path} is a binary type the Directory holds for review"))
        if len(data) >= limits["max_file_bytes"]:
            findings.append(("DC-05", f"{path} is {len(data)} bytes (limit {limits['max_file_bytes']})"))
        elif not kind and len(data) >= limits["max_text_bytes"]:
            findings.append(("DC-05", f"{path} is {len(data)} bytes (non-image limit {limits['max_text_bytes']})"))

    if ".mcp.json" in blobs:
        servers = json.loads(blobs[".mcp.json"]).get("mcpServers", {})
        for server, config in servers.items():
            url = config.get("url")
            if url is not None and url != "" and "${user_config." not in url and not url.startswith(("https://", "wss://")):
                findings.append(("DC-07", f".mcp.json server {server!r} url is not https:// or wss://"))

    if "hooks/hooks.json" in blobs:
        hook_text = blobs["hooks/hooks.json"].decode("utf-8")
        for ref in sorted(set(re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)", hook_text))):
            if ref not in blobs:
                findings.append(("DC-08", f"hooks/hooks.json references missing file {ref}"))

    readme = blobs.get("README.md")
    minimum = rules["DC-09"]["params"]["min_readme_words"]
    if readme is None or readme_words(readme.decode("utf-8")) < minimum:
        findings.append(("DC-09", f"README.md must have at least {minimum} words outside code blocks"))
    if "LICENSE" not in blobs:
        manifest = json.loads(blobs.get(MANIFEST_PATH, b"{}"))
        if not manifest.get("license"):
            findings.append(("DC-09", "LICENSE file or plugin.json license is required"))
    return findings


def run_compat(tree: str, compat: dict) -> None:
    findings = compat_findings(tree, compat)
    blocking = []
    for rule_id, message in findings:
        severity = compat["rules"][rule_id]["severity"]
        print(f"[{severity.upper()}] {rule_id} {message}")
        if severity == "block":
            blocking.append(rule_id)
    for rule_id, rule in compat["rules"].items():
        status = "FAIL" if rule_id in blocking else "PASS"
        print(f"{rule_id} {status} - {rule['title']}")
    if blocking:
        raise GateError(f"Directory compatibility gate failed: {sorted(set(blocking))}")


# --- version and release commit --------------------------------------------------


def manifest_version(rev: str) -> str:
    return str(json.loads(git("show", f"{rev}:{MANIFEST_PATH}")).get("version", ""))


def parse_semver(value: str) -> tuple[int, int, int]:
    match = SEMVER.fullmatch(value)
    if not match:
        raise GateError(f"not a semantic version x.y.z: {value!r}")
    return tuple(int(part) for part in match.groups())


def check_version(tree: str, base: str, version: str) -> None:
    requested = parse_semver(version)
    built = manifest_version(tree)
    if built != version:
        raise GateError(f"plugin.json version {built} does not match release version {version}")
    current = manifest_version(base)
    if requested <= parse_semver(current):
        raise GateError(f"release version {version} must be greater than claude-directory version {current}")
    print(f"version gate passed: {current} -> {version}")


def release_message(version: str, source: str, base: str, run_url: str) -> str:
    return (
        f"release(claude): v{version} from main@{source}\n\n"
        f"Source-Commit: {source}\n"
        f"Release-Version: {version}\n"
        f"Base-Head: {base}\n"
        f"Workflow-Run: {run_url}\n"
    )


def trailers(commit: str) -> dict[str, str]:
    body = git_text("log", "-1", "--format=%B", commit)
    return dict(re.findall(r"(?m)^([A-Za-z-]+): (\S+)$", body))


def verify_release(commit: str, base: str, tree: str, source: str, version: str) -> None:
    parents = git_text("rev-list", "--parents", "-n", "1", commit).split()[1:]
    checks = {
        "single parent equal to Base-Head": parents == [base],
        "tree equal to the built tree": git_text("rev-parse", f"{commit}^{{tree}}") == tree,
        "Source-Commit trailer": trailers(commit).get("Source-Commit") == source,
        "Release-Version trailer": trailers(commit).get("Release-Version") == version,
        "Base-Head trailer": trailers(commit).get("Base-Head") == base,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise GateError(f"release commit {commit} failed verification: {failed}")
    print(f"release commit verified: {commit}")


# --- commands --------------------------------------------------------------------


def cmd_build(args) -> None:
    policy = load_json(POLICY_PATH)
    source = resolve_commit(args.source)
    tree, result = build(source, policy)
    print(f"source={source} included={len(result['included'])} excluded={len(result['excluded'])}")
    for path in result["excluded"]:
        print(f"  excluded: {path}")
    print(f"tree={tree}")
    if args.stage:
        export_tree(tree, Path(args.stage))
        print(f"stage={args.stage}")
    if args.output:
        Path(args.output).write_text(
            json.dumps(
                {
                    "source": source,
                    "tree": tree,
                    "files": sorted(entry[3] for entry in result["included"]),
                    "excluded": result["excluded"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def cmd_golden(args) -> None:
    golden = load_json(POLICY_PATH)["golden"]
    tree, _ = build(resolve_commit(golden["source"]), load_json(POLICY_PATH))
    print(f"golden source={golden['source']} built={tree} expected={golden['tree']}")
    if tree != golden["tree"]:
        raise GateError("golden baseline mismatch: builder output changed for the serving source")
    serving_tree = git_text("rev-parse", f"{golden['serving_commit']}^{{tree}}")
    if serving_tree != golden["tree"]:
        raise GateError(f"serving commit tree {serving_tree} does not match the recorded golden tree")
    print("golden baseline passed")


def cmd_compat(args) -> None:
    run_compat(git_text("rev-parse", f"{args.tree}^{{tree}}"), load_json(COMPAT_PATH))


def cmd_version(args) -> None:
    check_version(args.tree, args.base, args.version)


def cmd_changed(args) -> None:
    base_tree = git_text("rev-parse", f"{args.base}^{{tree}}")
    if base_tree == args.tree:
        raise GateError("built tree is identical to claude-directory; nothing to release")
    print(git("diff", "--name-status", base_tree, args.tree).decode().strip())


def cmd_commit(args) -> None:
    for value, label in ((args.source, "source"), (args.base, "base")):
        if not FULL_SHA.fullmatch(value):
            raise GateError(f"{label} must be a full 40-character SHA")
    bot = "github-actions[bot]"
    email = "41898282+github-actions[bot]@users.noreply.github.com"
    env = dict(
        os.environ,
        GIT_AUTHOR_NAME=bot,
        GIT_AUTHOR_EMAIL=email,
        GIT_COMMITTER_NAME=bot,
        GIT_COMMITTER_EMAIL=email,
    )
    message = release_message(args.version, args.source, args.base, args.run_url)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(message)
    try:
        commit = git_text("commit-tree", args.tree, "-p", args.base, "-F", handle.name, env=env)
    finally:
        os.unlink(handle.name)
    verify_release(commit, args.base, args.tree, args.source, args.version)
    print(commit)


def cmd_verify(args) -> None:
    verify_release(args.commit, args.base, args.tree, args.source, args.version)


def cmd_selftest(args) -> None:
    policy = {"include": ["skills/**", "README.md"], "exclude": [".github/**"], "forbidden": ["**/.env"]}
    cases = {
        "skills/a/SKILL.md": "included",
        "README.md": "included",
        ".github/workflows/x.yml": "excluded",
        "skills/a/.env": "forbidden",
        "docs/x.md": "unclassified",
        "READMEx.md": "unclassified",
    }
    result = classify([("100644", "blob", "0" * 40, path) for path in cases], policy)
    got = {e[3] if isinstance(e, tuple) else e.split(" (")[0]: k for k in result for e in result[k]}
    assert got == cases, got
    for bad in ("x/.env", ".env"):
        assert glob_to_regex("**/.env").match(bad), bad
    assert not glob_to_regex(".claude/**").match(".claude-plugin/plugin.json")
    assert detect_binary(b"\x89PNG\r\n\x1a\n....") == "PNG"
    assert detect_binary(b"plain text\n") == ""
    assert detect_binary(b"MZ\x90\x00\x03") is None
    assert readme_words("# T\n\n```\nlots of code words here\n```\none two three") == 4
    assert parse_semver("1.10.0") > parse_semver("1.9.9")
    for bad in ("1.0", "01.0.0", "v1.0.0"):
        try:
            parse_semver(bad)
        except GateError:
            continue
        raise AssertionError(bad)

    # Every compatibility rule must fire on a synthetic tree built to violate it.
    def blob(data: bytes) -> str:
        return git("hash-object", "-w", "--stdin", data=data).decode().strip()

    bad_tree = {
        ".gitattributes": ("100644", blob(b"docs export-ignore\n")),
        "assets/.DS_Store": ("100644", blob(b"junk")),
        "link": ("120000", blob(b"README.md")),
        "con.md": ("100644", blob(b"reserved name\n")),
        "tool.exe": ("100644", blob(b"MZ\x90\x00\x03\x00")),
        "big.md": ("100644", blob(b"a" * 262144)),
        ".mcp.json": ("100644", blob(b'{"mcpServers": {"x": {"type": "http", "url": "http://insecure"}}}')),
        "hooks/hooks.json": ("100644", blob(b'{"hooks": {"Stop": [{"args": ["${CLAUDE_PLUGIN_ROOT}/scripts/missing.js"]}]}}')),
        "README.md": ("100644", blob(b"too short\n")),
    }
    spec = "".join(
        f"{mode} blob {oid}\t{path}\n" for path, (mode, oid) in bad_tree.items() if "/" not in path
    )
    sub_trees = {}
    for path, (mode, oid) in bad_tree.items():
        if "/" in path:
            folder, name = path.split("/", 1)
            sub_trees.setdefault(folder, []).append(f"{mode} blob {oid}\t{name}\n")
    for folder, lines in sub_trees.items():
        oid = git("mktree", data="".join(lines).encode()).decode().strip()
        spec += f"040000 tree {oid}\t{folder}\n"
    tree = git("mktree", data=spec.encode()).decode().strip()
    fired = {rule_id for rule_id, _ in compat_findings(tree, load_json(COMPAT_PATH))}
    expected = set(load_json(COMPAT_PATH)["rules"])
    assert fired == expected, f"rules that did not fire: {sorted(expected - fired)}"
    print("build_tree self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build", help="classify a source commit and write the release tree")
    p.add_argument("--source", required=True)
    p.add_argument("--stage", help="export the tree into this empty directory")
    p.add_argument("--output", help="write a JSON manifest of the build")
    p.set_defaults(func=cmd_build)

    sub.add_parser("golden", help="prove the builder reproduces the serving tree").set_defaults(func=cmd_golden)

    p = sub.add_parser("compat", help="run Anthropic Directory compatibility gates on a tree")
    p.add_argument("--tree", required=True)
    p.set_defaults(func=cmd_compat)

    p = sub.add_parser("version", help="check the release version against the manifest and base")
    p.add_argument("--tree", required=True)
    p.add_argument("--base", required=True)
    p.add_argument("--version", required=True)
    p.set_defaults(func=cmd_version)

    p = sub.add_parser("changed", help="fail when the tree equals the base tree")
    p.add_argument("--tree", required=True)
    p.add_argument("--base", required=True)
    p.set_defaults(func=cmd_changed)

    p = sub.add_parser("commit", help="create the release commit with Base-Head as its only parent")
    for name in ("tree", "base", "source", "version", "run-url"):
        p.add_argument(f"--{name}", required=True)
    p.set_defaults(func=cmd_commit)

    p = sub.add_parser("verify", help="verify a release commit against the build record")
    for name in ("commit", "base", "tree", "source", "version"):
        p.add_argument(f"--{name}", required=True)
    p.set_defaults(func=cmd_verify)

    sub.add_parser("selftest", help="run builder unit checks").set_defaults(func=cmd_selftest)

    args = parser.parse_args()
    try:
        args.func(args)
    except GateError as exc:
        print(f"GATE FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
