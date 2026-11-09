# Native test handoff — Draftroom 0.1.2

This is the user-test gate, not a claim that native acceptance has already passed. Public source/catalog submission stays on hold until Nick is happy with the real workflow.

## Before updating

Save any open drafts first. Saved Markdown and revisions live outside the installed code; do not copy over `plugin-data/draftroom`. Unsaved editor/recovery buffers are memory-only and are lost when the UI plugin/window reloads.

The backend and Mac UI are separate halves. Staging code is not activation, and enabling the wrong gateway is not activation of Desktop's actual backend. The prepared handoff must say which of these steps was actually completed.

## Load the matching build

1. Use the supplied 0.1.2 runtime ZIP. On the Mac, open **Settings → Plugins → Open plugins folder**. Replace only `<that local folder>/draftroom/plugin.js` with the ZIP's `draftroom/desktop/plugin.js`.
2. Run **Reload desktop plugins** from the command palette. For the intended Nova connection/profile, use the signed-in **Agent / Agent + Desktop** Draftroom control to activate the staged backend if the handoff says activation is pending. No unrelated service restart is required by these instructions.
3. Open a fresh test conversation. Confirm the agent can load `draftroom:blog` and list with `blog_draft`. The loaded backend's `/api/plugins/draftroom/status` now reports its imported package version; it must be `0.1.2`, not just a newer manifest on disk.

## Five-minute writing check

- [ ] `/blog Draftroom native test` opens the editor beside the same chat.
- [ ] Enter a short sample with a rough paragraph, save, close/reopen and confirm the text remains.
- [ ] Select only the rough paragraph, without its final newline, and ask: `Make this clearer and more confident, keeping my casual tone.`
- [ ] The real agent produces a suggestion in that conversation. The original draft stays unchanged until Accept.
- [ ] Original / Suggested and Diff are readable. Accept changes only the selection and saves; a second suggestion can be rejected without changing the Markdown.
- [ ] More → History previews earlier versions. Restore is a normal version-checked edit, not deletion of history. Recovery text remains available if local edits were displaced.
- [ ] Copy Markdown and Save .md file work in the actual Mac client. Inspect the downloaded file, rather than relying only on a notification.
- [ ] Make the pane narrow/short and confirm the editor, review actions and scroll regions are usable.

Automated regression tests cover corrupt metadata, revision symlink boundaries, delayed responses, failed saves, repeated restores and commit-intent races. Do not corrupt real draft files or disable shared services just to reproduce those cases manually.

## Optional Commit to repo test

Use only a designated disposable repository on the connected backend machine, with **Also push unchecked**. The Git operation belongs to the agent's ordinary tools and approvals; no plugin code runs Git. Verify that only the requested file is committed and that no network push happens. This is separate from proving draft/rewrite/Accept works, and it is not permission to touch an unrelated existing repository.

## Acceptance and next step

Report any actual native failure with the action, visible error and whether the draft stayed intact. After Nick accepts the working build: freeze the tested source, publish the approved public repository, generate the real catalog pin from its exact commit, raise the catalog PR, record/post the real under-90-second demo and submit both links. None of those publication steps is completed merely by this checklist.
