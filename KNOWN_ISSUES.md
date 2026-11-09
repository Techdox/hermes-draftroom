# Known limitations and release gates

## Agent + Desktop activation

The local UI and the Agent backend are separate components. In a multi-process installation, a gateway daemon and the Desktop `serve` process can share a profile directory but not their in-memory tool/skill registrations. Enabling a setting or reloading the wrong process is not proof that the actual chat can use `blog_draft`.

Use the signed-in Desktop's Agent / Agent + Desktop control for the selected profile. Verify the plugin skill/tool before a first rewrite. Do not repeatedly retry, weaken authentication or silently restart shared services. The combined Git installer is the documented recommended route; a clean install from this public repository must still be verified after it is published.

## Unsaved buffers

Owner-scoped in-memory buffers survive pane close/reopen and profile/connection switches. They do not survive disabling/reloading the plugin, reloading the window or quitting Desktop. Save before updating either half. The UI explicitly retains text and pauses automatic retries after a failed save.

## Line endings

The editor is a `<textarea>`, which cannot hold carriage returns. A draft with CRLF line endings (for example, edited outside Draftroom) displays and accepts selected rewrites exactly, but the first edit typed in the pane saves the whole draft with LF endings. The CRLF version is kept in revision history.

## Unreadable drafts

A draft that cannot be read (non-UTF-8, over 256 KiB, damaged metadata) is reported in the library instead of breaking it. Draftroom does not repair or delete it; fix or remove the files by hand.

## Commit to repo

Commit to repo… depends on the agent having file and Git tools enabled; Draftroom cannot check that in advance. Like Rewrite, a composer acknowledgement isn't proof of delivery, and nothing is retried automatically. **Save .md file** uses a standard browser download; how it prompts depends on the Desktop build and has not been checked natively.

## Platforms and retained history

The backend uses POSIX locks, so it requires Linux or macOS. Revision files are retained without automatic pruning. There is no revision-browser, publication workflow or force-save API in this release.

## Diff fix in 0.1.1

New suggestions now frame unified-diff lines correctly when a selected passage lacks its final newline. The original/replacement strings and saved Markdown are not normalized. Historical proposals keep their original recorded preview; the update does not rewrite previously accepted drafts or proposal records.

The 0.1.1 fix has automated regression coverage. It still needs a native Desktop Diff-view smoke test after installing this candidate. The native selection → real model proposal → user Accept → exact persisted Markdown flow was verified on 0.1.0 before this candidate was prepared.
