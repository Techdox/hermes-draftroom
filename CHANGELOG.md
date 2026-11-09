# Changelog

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
