# Independent review: Draftroom

This is the 0.1.1 candidate for a small Hermes Agent + Desktop writing plugin. The private Forgejo branch is for independent model/human review, not a published hackathon entry or a deployed update. Read `README.md`, `API.md`, `VERIFICATION.md` and `KNOWN_ISSUES.md` first.

## Product boundary

`/blog` opens real Markdown beside the existing Hermes conversation. The user selects a passage, requests a rewrite through the same agent, reviews Original / Suggested / Diff, and explicitly Accepts or Rejects. The agent can propose but cannot accept. Preserve that narrow workflow; do not turn it into a publishing platform, add SEO, a second model client, new cloud services or Hermes core patches.

## Review request

Please independently review this branch. Prioritise reproducible correctness, data-loss/security risks and practical UX improvements over a rewrite or speculative features. Do not edit files or deploy anything during the initial review.

For each finding, include:

- Severity and exact file/line reference.
- A realistic reproduction or failing test, expected behaviour and actual behaviour.
- Why it matters to the user, and the smallest appropriate fix.
- Whether it is a confirmed bug, an unverified SDK assumption, a known limitation, or a preference.

Do not claim that source inspection, an SDK adapter or a controlled rewrite fixture proves native Desktop/model behaviour. Mark tests you did not run as unrun. If suggesting a dependency or SDK change, cite the actual supported API/version; do not invent one.

## Useful review areas

- `draftroom_store.py`: optimistic versions, exact selected-range checks, Unicode code-point offsets, POSIX cross-process locking, atomic writes, retained revisions, interrupted-write behaviour and path boundaries.
- `dashboard/plugin_api.py`: existing Hermes auth/profile namespace, threaded filesystem mutations and conflicts. No arbitrary-path or force-save API should appear.
- `__init__.py` and `skills/blog/SKILL.md`: actual tool registration and proposal-only boundaries. Draft text and rewrite instructions are untrusted content, not authority to run tools, accept a proposal or edit files directly.
- `desktop/plugin.js`: debounced/explicit saves, dirty-buffer recovery, pending/stale proposal handling, profile/connection/session ownership, selection offsets, human Accept/Reject, narrow-pane accessibility and controls.
- Diff presentation: selections without a final newline, CRLF, newline-only edits and deletion. Rendering must not normalise the canonical original/replacement or saved Markdown.
- Installation: Agent/backend and local Desktop UI are separate halves. The actual Desktop-serving process must load the tool/skill; a separate gateway reporting enabled is insufficient.
- Release/catalog tooling: explicit file allowlist, no-overwrite ZIPs and exact source bytes, real full commit pins and strict public repository identifiers. The public-GitHub catalog template deliberately remains a template; do not replace its placeholders with this private Forgejo URL or a made-up SHA.

## Run checks safely

Use an isolated development environment, never the environment serving a live Hermes session:

```sh
uv venv .venv
uv pip install --python .venv/bin/python --exclude-newer '3 days' -r requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q
node --check desktop/plugin.js
```

Hermes doctor/validator checks require a compatible, separately provisioned host SDK; see `VERIFICATION.md`. Do not modify live profiles, drafts, databases, runtime packages or credentials to make a test pass. Never commit `.env`, credentials, plugin-data, local caches, a test environment or private acceptance evidence.

## Evidence already available

- Candidate 0.1.1: **83 Python tests** and **13 browser workflow checks** passed. Packaged bytes/checksums, isolated import/registration and plain Hermes validation passed. The Python suite also passed from the extracted source kit.
- Browser checks used the real plugin UI/backend through a public-SDK host adapter with controlled proposal fixtures. They are not a native model demo.
- Native 0.1.0: actual Mac Desktop selected rewrite through the existing conversation/agent, real proposal, human Accept, exact selected replacement persisted and prior revision retained.
- Still pending: native 0.1.1 Diff/clean-install acceptance and recording, full dependency-install admission, public source/catalog PR, X demo and form submission. The independent PM runtime was unavailable for the owned `--install-deps` attempt; successful plain validation does not make that installation gate pass.

Return a prioritised findings list first. Keep optional polish separate from blocking bugs. Any requested implementation belongs on a new feature branch; do not amend this review baseline, force-push or update an installed copy without approval.
