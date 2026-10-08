#!/usr/bin/env python3
"""Create a synthetic release source commit for the success-path integration test.

The commit bumps the plugin patch version above the claude-directory version and adds
a matching CHANGELOG heading on top of a parent commit. It is created with plumbing,
is not attached to any branch, and is never pushed.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile

from build_tree import MANIFEST_PATH, git, git_text, manifest_version, parse_semver


def replace_blob(env: dict, path: str, data: bytes) -> None:
    oid = git("hash-object", "-w", "--stdin", data=data).decode().strip()
    git("update-index", "--cacheinfo", f"100644,{oid},{path}", env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", required=True, help="commit to build the fixture on")
    parser.add_argument("--base", required=True, help="claude-directory head whose version must be exceeded")
    args = parser.parse_args()

    major, minor, patch = parse_semver(manifest_version(args.base))
    version = f"{major}.{minor}.{patch + 1}"

    manifest = json.loads(git("show", f"{args.parent}:{MANIFEST_PATH}"))
    manifest["version"] = version
    changelog = git("show", f"{args.parent}:CHANGELOG.md").decode("utf-8")
    heading = f"## {version}\n\n- Integration-test fixture. Never released.\n\n"
    first = changelog.find("\n## ")
    changelog = changelog[: first + 1] + heading + changelog[first + 1 :] if first >= 0 else changelog + "\n" + heading

    with tempfile.TemporaryDirectory() as tmp:
        env = dict(
            os.environ,
            GIT_INDEX_FILE=os.path.join(tmp, "index"),
            GIT_AUTHOR_NAME="release-fixture",
            GIT_AUTHOR_EMAIL="release-fixture@invalid",
            GIT_COMMITTER_NAME="release-fixture",
            GIT_COMMITTER_EMAIL="release-fixture@invalid",
        )
        git("read-tree", args.parent, env=env)
        replace_blob(env, MANIFEST_PATH, (json.dumps(manifest, indent=2) + "\n").encode())
        replace_blob(env, "CHANGELOG.md", changelog.encode())
        tree = git_text("write-tree", env=env)
        commit = git(
            "commit-tree", tree, "-p", args.parent, data=f"test: release fixture {version}\n".encode(), env=env
        ).decode().strip()
    print(f"version={version}")
    print(f"commit={commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
