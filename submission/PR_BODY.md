# Add Draftroom to the plugin catalog

Draftroom is a Markdown writing companion beside the existing Hermes conversation. `/blog` opens a real draft; selected-text rewrites arrive as proposals for Original / Suggested / Diff review. Human Accept applies and saves a change; Reject leaves the Markdown unchanged.

This is a working early release for the plugin hackathon, not a finished editor. The core co-writing workflow works. Further development is focused on making it clearer and more comfortable to use.

## Source

- Repository: <PUBLIC_REPO_URL>
- Exact source pin: <FULL_40_CHAR_COMMIT_SHA>
- Version: **0.1.2**
- Catalog change: `plugin-catalog/draftroom.yaml`

## Implementation and scope

- Public Python tool/skill and plugin REST surfaces, plus the public Desktop SDK workspace, composer middleware, `ctx.rest` and native controls.
- Reuses the current Hermes conversation and configured model. No separate model client, service or provider credentials.
- Version-bound selections, optimistic saves, atomic writes and retained prior Markdown revisions. The agent proposes; the editor user alone accepts.
- Includes History preview/restore, Markdown export and an optional explicit handoff to the agent for committing to a user-designated repository.
- Requires both Agent and Desktop components, a compatible public Desktop SDK, and a Linux/macOS backend (`fcntl` locking). No Hermes core patches or self-updater.

## Validation

- **177 Python tests**, **32 Node controller tests** and **20 browser checks** passed. Browser checks use the real module/backend through a labelled SDK adapter with controlled proposal fixtures, not a native model demo.
- The exact runtime ZIP passed source-byte/CRC checks, isolated import and registration, Plugin Doctor and plain validation with no warnings.
- Native writing was tested in Desktop with the real configured agent. A selected rewrite remained unapplied until human Accept; a subsequent tool read confirmed the accepted replacement persisted exactly. This is not a claim that every UX case or platform has been tested.
- Full dependency-install admission: <VALIDATION_RESULT>

## Data and behaviour disclosures

Drafts, metadata, proposals and retained revisions live in the active backend profile's plugin-data directory. Unsaved buffers/recovery snapshots are memory-only and are lost on plugin/window reload or app quit. Prior revisions are not automatically pruned.

The UI autosaves and polls its own Hermes backend while open. Rewrites use the existing agent/provider and may leave the host under that provider's normal settings. Optional **Commit to repo** sends a frozen, user-initiated request to the same agent; any file/Git/network activity uses its existing tools and approvals. The plugin does not execute Git itself. No new credential store, telemetry, direct third-party requests, background service or publishing endpoint is added.

## UI/UX roadmap

- Refine pane layout, spacing and typography, particularly at narrower sizes.
- Make selections, pending suggestions and review actions easier to follow.
- Improve save, connection and error-state feedback, plus first-run setup guidance.
- Continue keyboard-navigation and accessibility testing in the real Desktop client.

These are planned refinements, not completed features or promised delivery dates. Draftroom remains a focused writing companion rather than a publishing platform.
