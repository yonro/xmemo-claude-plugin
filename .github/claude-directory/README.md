# claude-directory release artifact

`main` is the only development branch. `claude-directory` is the branch the Claude
Directory tracks, and it is generated from `main` by the
[Release Claude Directory artifact](../workflows/release-claude-directory.yml) workflow.

Never push, merge, or force-push `claude-directory` by hand. The workflow refuses to
publish when the branch moved unexpectedly, and a manual change has to be investigated
before the next release.

## Files

| File | Purpose |
| --- | --- |
| `release-policy.json` | XMemo artifact definition: which source files are included, excluded, or forbidden. Every tracked file must be classified. `golden` records the serving baseline. |
| `directory-compat.json` | Anthropic Directory compatibility gates. They inspect the built artifact and never change what is included. |
| `build_tree.py` | Builds the release tree with git plumbing and runs the gates. Standard library only. |

## Release

1. On `main`, raise `version` in `.claude-plugin/plugin.json` and add a matching
   `## x.y.z` heading to `CHANGELOG.md`.
2. Run the workflow with `version`, the full `source_sha` on `main`, and `dry_run: true`.
   Review the job summary: release commit, tree, and changes against `claude-directory`.
3. Run it again with `dry_run: false`. Approve the `claude-directory-release` environment
   when the build job has passed.
4. The publish job verifies the frozen release commit, checks that `claude-directory`
   still points at the recorded base, and fast-forwards it with a plain push.
5. Confirm the Anthropic webhook delivered the push, then select **Publish update** in
   the Claude developer portal.

## Gates

| Gate | Check |
| --- | --- |
| G0 | Inputs: `x.y.z` version and a full SHA reachable from `main` |
| G1 | Release policy: no forbidden, conflicting, or unclassified files |
| G2 | Anthropic Directory compatibility rules DC-01 to DC-09 |
| G3 | `validate-package.py --profile directory` on the staged artifact, including the credential scan |
| G4 | `claude plugin validate --strict` on the staged artifact with a pinned Claude Code version |
| G5 | Checkpoint hook tests against the staged hook through `XMEMO_HOOK_PATH` |
| G6 | `plugin.json` version equals the input and is greater than the `claude-directory` version |
| G7 | The artifact differs from the current `claude-directory` tree |
| G8 | `claude-directory` did not move during the build, and again before the push |
| G9 | Builder self-test and golden baseline: `5d0d280` rebuilds tree `5ccc440` |

## Local checks

```bash
python .github/claude-directory/build_tree.py selftest
python .github/claude-directory/build_tree.py golden
python .github/claude-directory/build_tree.py build --source HEAD --stage /tmp/stage
```
