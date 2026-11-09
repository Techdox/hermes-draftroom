# Verification — Draftroom 0.1.1 release candidate

## Scope and result

The candidate fixes the selected-paragraph Diff preview and adds release/submission preparation. The running installation was not overwritten during this work. Do not confuse the successful native 0.1.0 baseline with a native smoke test of the newly staged 0.1.1 candidate.

## Automated source checks

- **83 Python tests passed** on Python 3.14 in the isolated project environment. Its newer Starlette TestClient emits one deprecation warning about httpx; there were no test failures.
- The same **83 tests pass** with the installed Hermes-compatible FastAPI **0.133.1** and Starlette **1.9.0** dependencies, without that warning. No serving-runtime packages were changed.
- The Diff regression was first observed failing: five cases failed and two passed. After the fix, all seven passed, including missing final newlines, multiline text, newline-only changes, deletion, CRLF and identical selections. The tests also verify that preview framing never changes saved Markdown.
- Release tests independently verify the exact ZIP allowlist, source bytes, CRC, checksums, regular-file entries, deterministic output, no-overwrite behaviour, rejected symlinks/missing files and matching component versions.
- Catalog-generator tests use explicitly labelled fixture URLs/SHAs, reject malformed pins and unsafe URLs without normalization, and compare the generated declaration with the actual single registered tool. No fixture pin is presented as a real publication.
- `node --check desktop/plugin.js` and Git whitespace checks pass.
- Plugin Doctor confirms runtime discovery, manifest parsing, import and registration of one tool for 0.1.1.
- The normal Hermes plugin validator reports **`ok: true`, no warnings**, security scan safe, no core override, the public Desktop SDK surface, and matching declarations.

## Browser acceptance of 0.1.1

**13 browser workflow checks passed**, with zero console/page errors, using the shipped Desktop module, the real FastAPI router and the real agent proposal handler against disposable files:

1. `/blog` opens beside chat and creates real Markdown.
2. Debounced autosave writes exact UTF-8 content.
3. Rewrite requests preserve the exact session, version, original and Unicode code-point range.
4. A proposal appears without changing the article.
5. Unified Diff correctly separates removed/added lines and marks a selection's absent final newline.
6. Accept changes only the selected passage and retains prior content.
7. Close/reopen and a full page reload recover saved text.
8. Reject leaves Markdown unchanged.
9. UI and API refuse dirty/stale acceptance.
10. Failed saves retain text, pause automatic retries and recover explicitly.
11. Profile switches do not leak private text or write to the wrong profile.
12. A focused-chat/ambient-connection mismatch fails closed.
13. A 380px-wide pane has no horizontal overflow and keeps review controls visible.

This browser environment uses an explicit **public-SDK host adapter** and labelled proposal fixtures. It is not an Electron recording or a model-generated native demo. The tests are not the submission video.

## Real native baseline already verified on 0.1.0

The user installed the UI in Mac Hermes Desktop and enabled the Agent component in the actual serving backend. A selected rewrite reached the existing conversation, the real `blog_draft` tool created a pending model-authored suggestion, and the user chose Accept. Readback confirmed accepted status, only the requested selection changed, the exact resulting Markdown was on disk, and the previous version remained in revision history.

No direct draft-file edit, authentication bypass or alternate model client was used to make that native test pass.

## Dependency-install admission boundary

`hermes plugins validate --install-deps --json` was attempted inside an owned copy of the SDK and its dependency environment, not the serving installation. The validator checks returned `ok: true` and no warnings, **but dependency preparation did not complete**: the independent PM runtime was not installed and lazy installs were disabled. This is not a pass for the dependency-install phase. The plain validator and import checks ran with preprovisioned compatible dependencies.

Run the complete dependency-install gate in a properly provisioned disposable Hermes environment, and require catalog CI after the source is published. Do not upgrade the serving runtime just to satisfy this preparation check.

## Pending release gates

- Install/reload the candidate and recheck the native Diff view.
- Verify a clean combined Agent + Desktop install from the eventual public repository.
- Record a real, privacy-reviewed native demo under 90 seconds.
- Configure the approved Git author/signing path, make the initial commit and publish the chosen repository. No author identity or commit SHA was invented.
- Generate the catalog YAML from that exact clean commit, verify the public source/pin, open the catalog PR and inspect its actual CI.
- Post the demo on X tagging `@NousResearch`, then submit the PR and X links through the official form, with publication approval.

The prepared GitHub Actions workflow has not run remotely: there is no published repository/PR yet. This file records local evidence, not a CI badge or completed hackathon submission.
