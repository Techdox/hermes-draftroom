# Changelog

## Unreleased — independent review pass

- Fix: one unreadable draft (non-UTF-8 or oversized after an external edit, damaged metadata, or a crash mid-create) no longer breaks the whole library, `/blog` and the agent's `list`. Unreadable drafts are reported as `unavailable` and left untouched.
- Fix: draft creation is atomic (staged then renamed), so a 2-second poll can no longer see a half-created draft and fail.
- Fix: selections in drafts with CRLF line endings now produce exact code-point ranges, so Rewrite works on them. The textarea is given the line-break-normalised text so React no longer resets the caret on every render.
- Add **Keep my version…** to the conflict panel: a confirmed save pinned to the exact saved version on screen. The replaced version is retained as a revision. There is still no blind force-save.
- Server `/blog <title>` reopens the conversation's same-titled draft instead of creating a duplicate, matching Desktop.
- Error notes say when autosave is paused. The draft list polls every 10 s instead of 2 s; the open draft still polls every 2 s.
- Add **More** actions: **Copy Markdown**, **Save .md file** (download), **History** (read-only revision endpoints; restore loads a version into the editor and saves it normally) and **Commit to repo…**, which asks the user's own agent to commit the saved draft. Draftroom itself still runs no Git and makes no network calls. The skill documents the narrow, user-initiated commit exception.
- UI polish: status dot, word count and reading time, a coloured Diff, a selected state on the review toggle, instruction preset chips, Ctrl/Cmd+Enter to rewrite, a selected-passage quote, relative times and a filter in the library, and a profile chip. While a suggestion is pending, the rewrite box is hidden.
- Fix: in a short pane, the review, footer and library sections could together exceed the height and clip controls (including Accept). They now shrink and scroll.
- Add Node controller tests for `desktop/plugin.js` (public-SDK test double, no new dependencies) and run them in CI.

## 0.1.1 — prepared release candidate

- Fix unified Diff previews for selected passages without a final newline. Added/removed lines no longer run together, and a standard EOF-newline marker preserves the distinction without changing the saved text.
- Add regressions for a single paragraph, multiline text, adding/removing a final newline, deletion, CRLF and unchanged selections.
- Clarify the combined Agent + Desktop install path, remote/local ownership, live registration checks and safe manual updates.
- Add reproducible allowlisted packaging, development checks and submission preparation assets.

The live 0.1.0 native co-writing test passed before this candidate was prepared. Do not claim the 0.1.1 Diff display has been rechecked in the user's Desktop until the candidate is installed and that check is actually performed.

## 0.1.0 — initial native slice

- `/blog` and an on-demand Markdown editor beside the existing conversation.
- Exact-selection rewrite requests, Original/Suggested/Diff review, human Accept/Reject and version-checked saving.
- Private profile-scoped files, prior revisions, Unicode code-point ranges, safe failure/conflict handling and owner-scoped dirty buffers.
- Real Native Desktop → agent proposal → user Accept → persisted Markdown acceptance completed.
