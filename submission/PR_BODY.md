# Add Draftroom to the plugin catalog

Draftroom is a Markdown writing companion beside the existing Hermes chat. `/blog` opens a real draft; selected-text rewrites arrive as proposals for Original / Suggested / Diff review. Human Accept applies and saves the change; Reject leaves the Markdown unchanged.

## Source and proposed entry

- Repository: `<PUBLIC_REPO_URL>`
- Pinned commit: `<FULL_40_CHAR_COMMIT_SHA>`
- Release target: **0.1.1**; the pinned manifest and package must match.
- Proposed catalog file: `plugin-catalog/draftroom.yaml`
- Native demo: `<DEMO_X_POST_URL>`
- UI screenshot: `<PUBLIC_PRIVACY_REVIEWED_SCREENSHOT_URL>`

These are pending placeholders, not existing publication links. This local body does not establish a PR or a CI result. Fill the pin and links, and resolve the unchecked release gates before submission.

## Implementation and scope

- Public Python tool/skill and plugin REST surfaces, plus the public Desktop SDK workspace, composer middleware, `ctx.rest` and native controls.
- The current Hermes conversation handles rewrites through `blog_draft`; no second model client or custom provider credentials.
- Version-bound selections, atomic version-checked saves and retained prior Markdown revisions. The agent tool can create/read/propose, not accept or force-save.
- Drafting, selected revision and human review only. No publishing, SEO integration, self-updater or core patching.

## Installation and activation notes

1. Install the pinned backend package into the **intended Hermes profile** and enable `draftroom` with the normal plugin manager. Read any reload/restart requirement; enabled does not necessarily mean loaded.
2. On the Mac, use **Settings → Plugins → Open plugins folder**. Put the package's `desktop/plugin.js` at `draftroom/plugin.js` inside that actual local folder. Reload desktop plugins if needed, then enable Draftroom. A remote backend path is not the Mac's plugin folder.
3. Confirm the backend actually serving Desktop has loaded `blog_draft` and `draftroom:blog`, then open a fresh conversation. A separate gateway and Desktop `serve` process caused an activation mismatch in native testing; enabling the gateway alone did not resolve it. Shared restarts require permission.

Requires a recent compatible public Desktop SDK and a POSIX backend (`fcntl` locking). Confirm the supported version floor against the final release rather than guessing compatibility metadata. No one-command/seamless installation claim is made.

## Data and behaviour disclosures

Drafts, metadata, proposals and retained revisions live in the active backend profile's plugin-data directory. Desktop keeps unsaved buffers in memory, not localStorage; those buffers are lost on app/plugin reload. The UI autosaves and polls through the existing Hermes backend. Rewrites use the configured agent/provider and may leave the host under that provider's normal settings. No new credential store, telemetry, shell commands, unrelated-file access, standalone service or publishing endpoint is added. Prior revisions are not automatically pruned.

## Validation and evidence boundary

- [x] Final 0.1.1 source: 83 Python tests and 13 browser workflow checks passed, including seven Diff regression cases. Plugin doctor, plain validator and JavaScript syntax checks passed. The no-overwrite ZIP's exact runtime files, source bytes, CRC and checksums were verified; extracted-artifact isolated import/registration and plain validation passed with no warnings.
- [x] Separate actual native Mac 0.1.0 acceptance: selected rewrite through the existing agent and `blog_draft`, human Accept, exact backend Markdown verified, only the selected range changed, prior revision preserved.
- [ ] At the exact proposed pin, run `hermes plugins validate <PINNED_CHECKOUT> --install-deps` in an isolated validation environment; review failures and warnings.
- [ ] Install matching 0.1.1 halves and repeat native selection → pending review → human Accept → reopen persistence, including Original / Suggested / Diff. Attach a privacy-reviewed native screenshot and real demo.
- [ ] Public repository, full 40-character SHA, release version and catalog compatibility/capability metadata confirmed against the pinned tree.

The 13 candidate browser checks used a public-SDK host adapter and controlled rewrite fixtures. They prove editor/backend workflows, not a native renderer or live LLM turn. The earlier native acceptance supplies that separate 0.1.0 evidence; it does not establish native acceptance of 0.1.1. The owned dependency-install admission attempt did not complete because its independent PM runtime was not provisioned; plain validation used preprovisioned compatible dependencies. Catalog CI and maintainer review remain unclaimed. See `VERIFICATION.md` for the full boundary.
