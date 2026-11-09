# Draftroom submission checklist

## Deadline and exactly three required deliverables

**Wednesday 11 November 2026, 5:00 PM EST (UTC−05:00)** = **11 November, 22:00 UTC** = **Thursday 12 November, 11:00 AM NZDT (UTC+13:00)**. Timezone conversion checked programmatically.

1. [ ] **Open a catalog PR** adding the plugin to `NousResearch/hermes-agent`.
2. [ ] **Post a working demo video on X, under 90 seconds, tagging `@NousResearch`.**
3. [ ] **Submit both links** (catalog PR + X demo post) through https://form.typeform.com/to/FwJLvOln.

Once the PR and demo post exist, the form can be submitted without waiting for catalog CI, review or merge. Those may follow. Source repo and screenshots support the submission; they are not substitutes for the three deliverables.

Official [announcement](https://x.com/NousResearch/status/2118094256438936062) and [catalog guidance](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins/catalog-submission) were retrieved live for these assets.

## Established gates

- [x] Scope frozen: `/blog`, real Markdown beside existing chat, selected rewrite, Original / Suggested / Diff review, human Accept/Reject and safe local saving. No publishing/SEO platform, second LLM client or core patches.
- [x] Final 0.1.2 candidate: 177 Python tests, 32 Node controller tests and 20 browser checks passed, covering the no-final-newline fix and all seven reviewed issues. Adapter/fixture checks are not represented as native model evidence.
- [x] Actual native Mac 0.1.0 co-writing accepted: real agent/tool proposal, human Accept, exact Markdown verified, selection-only change and prior revision retained.
- [x] Four local submission assets prepared. Private Forgejo review/fix work is separate from the still-pending public repository, catalog PR, demo post and form submission.

## Release and native recording gates: not yet signed off

- [x] 0.1.2 fixes/regressions, installation/test docs and no-overwrite packaging prepared. Source Doctor/plain validation passed with no warnings; earlier snapshots/evidence retained.
- [x] Exact delivered ZIP membership/bytes/checksums, isolated import/registration and plain validation verified against the 0.1.2 candidate; the actual accompanying receipt remains separate from activation/native acceptance.
- [ ] Full `--install-deps` admission completes in an owned, fully provisioned environment or catalog CI. The independent PM runtime was unavailable in the local admission attempt; this is not a pass for dependency preparation. Do not change the serving runtime to make this gate pass.
- [ ] Both backend and Mac UI use the final matching 0.1.2 release. Verify the actual Desktop-serving process loads the tool/skill; do not infer this from gateway enablement.
- [ ] Native 0.1.2: select a paragraph without its final newline; use the real configured agent; verify pending review does not change the file; compare Original / Suggested / Diff; actually Accept; verify only the selection changed and a prior revision exists; close/reopen and confirm persistence.
- [ ] Rehearse once, then record the continuous **78-second** native path in `DEMO_SCRIPT.md`. No fixture rewrite, adapter recording, hidden wait or fabricated acceptance.
- [ ] Inspect the actual export: readable UI, clear narration, duration **under 90 seconds**, and privacy checklist passed frame by frame.

## Identity, repository and publication approvals

- [ ] Confirm the public repository author/signing path. Private feature commits reuse the established Nova identity; do not invent a public identity or bypass required production signing.
- [ ] User approves the public repository owner/name and first commit, remote creation and push. No owner, URL or SHA is assumed.
- [ ] Final public tree is reviewed for private data, local paths, caches and credentials. No credentials/access search is part of this task.
- [ ] Full 40-character commit pin, matching 0.1.2 version, truthful compatibility/capability metadata and public cloneability verified. Release owner prepares the catalog entry separately.
- [ ] Final pinned checkout passes isolated catalog validation; release checks and native evidence are attached with their actual version/scope.
- [ ] User approves the exact public repo contents, catalog PR body/screenshots, X caption/video and form submission **before** each external write.
- [ ] Replace every pending token below and in the copy. X draft is **250 literal / 263 two-link-weighted characters**; recheck the final caption after replacement.

## Link handoff: all pending

| Item | Value |
| --- | --- |
| Public source | `<PUBLIC_REPO_URL>` |
| Exact pin | `<FULL_40_CHAR_COMMIT_SHA>` |
| Catalog PR | `<CATALOG_PR_URL>` |
| Native demo post | `<DEMO_X_POST_URL>` |
| Form receipt | `<FORM_CONFIRMATION>` |

After authorized publication, read back each exact public target and verify the form confirmation before marking the three deliverables complete. An open PR is not a merged listing; a successful upload is not a verified playable demo.
