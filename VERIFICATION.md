# Verification — Draftroom 0.1.2 test candidate

## Scope

This candidate preserves the useful independent-review additions and fixes the seven reproduced review findings. It is prepared for Nick's native test, not a claim that the new build is already accepted in Mac Desktop or entered in the hackathon. Earlier 0.1.0/0.1.1 evidence and immutable artifacts remain historical; Git history retains their verification documents.

## Independently exercised source checks

- **177 Python tests passed** on Python 3.14 in the isolated project environment. One existing Starlette/httpx TestClient deprecation warning remains; there were no failures or skipped tests.
- **32 Node controller tests passed**, with no failures or skips, using the declared public-SDK test double. These include delayed saves, approved-content changes, mutable push flags, stored/runtime conversation switches, recovery after failed saves, A→B→A preview ordering, closed/reopened panels and stale failures.
- `node --check desktop/plugin.js` and `git diff --check` passed.
- Public Plugin Doctor passed runtime discovery, manifest parsing, import and registration of one tool for 0.1.2, inside an owned SDK environment.
- Plain Hermes catalog validation returned **`ok: true`, no warnings**, safe security scan, no core override and an SDK-only Desktop surface. This is not the full dependency-install gate.
- Release tests independently assert the exact runtime file set and source bytes, CRC/checksums, regular files, deterministic output, refusal to overwrite artifacts, missing/symlinked-file rejection and matching component versions. The user-provided logo and native test guide are included explicitly; no private data or test runtime is added to the allowlist.
- The loaded backend version is captured when its API imports. A regression proves that replacing a manifest does not make an old router claim new activation.

## Real browser / real backend checks

**20 checks passed**, with no unexpected console/page errors, using the shipped module, real FastAPI API, actual disposable Markdown/revisions and a public-SDK host adapter:

- Thirteen core cases: `/blog`, exact UTF-8 autosave, exact Unicode selected-range requests, proposal-only generation, correct Diff framing, explicit Accept, persisted reopen/reload, Reject, stale/dirty rejection, failed-save recovery, owner switching, focus/connection mismatch and narrow-pane scroll reachability.
- Five feature cases: real History preview/restore, exact file download, clipboard copy, confirmed version-checked conflict recovery and immutable no-push intent with disabled preparation controls.
- Two safety cases: repeated History restores after an injected save failure retain both the original unsaved writing and the next recovery snapshot visibly; delayed A cannot overwrite the newer B selection, and Restore is disabled while selection loads.

The adapter uses labelled deterministic proposal fixtures and captures composer requests; it does not run another model or execute Git. Injected failure/delay cases operate only on task-owned test data. Narrow-pane controls can require scrolling inside the review section; this is not a claim of always-visible Accept/Reject buttons. Captured screenshots were inspected, including both recovery snapshots.

## Exact package and activation gates

The delivered ZIP must independently pass extracted-artifact import/registration with checkout paths excluded and no active import side effects, plus plain Doctor/validation. Its accompanying checksum/verification receipt records the exact bytes. Building/staging files is distinct from activation; confirm the actual Desktop-serving backend reports `version: 0.1.2`, not just a newer manifest on disk.

No serving-runtime dependency upgrade is required by these fixes. Preserve installed code for rollback and never overwrite `plugin-data/draftroom`. The Desktop file must be updated on the Mac separately from the backend.

## Native and publication boundaries

Actual Mac Desktop → existing agent → model proposal → human Accept → exact persisted Markdown was previously verified on **0.1.0**. It does not establish native acceptance of 0.1.2. See `TESTING.md` for the real user test and copy/download check.

The earlier isolated `--install-deps` admission attempt did not prepare its independent PM runtime, despite plain validation returning success. The full dependency-install gate still needs a provisioned disposable environment or catalog CI; inspect stderr as well as JSON. Do not change the serving environment to conceal that prerequisite.

A private Forgejo review/fix branch is not public hackathon publication. Nick's native acceptance comes first; then approve the public repository/author/signing path, freeze its actual full commit pin, raise the catalog PR, record/post the genuine under-90-second native demo and submit the two required links. No public PR, CI success, X post or form receipt is claimed here.
