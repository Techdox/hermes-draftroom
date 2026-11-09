# Draftroom

<img src="assets/draftroom-logo.png" alt="Draftroom: a paper chat bubble, highlighted passage and fountain pen" width="160" />

**Write beside your Hermes conversation. Keep the draft, not a pile of chat replies.**

Type `/blog My next article` to open a Markdown draft beside chat. Write directly, or select a passage and ask for a rewrite. Compare the original and suggestion, then decide what stays.

Draftroom is deliberately small: **draft → discuss → revise → review → save**. No publishing platform, SEO dashboard or second model service.

## What makes it useful

- **One real draft.** Your article is a UTF-8 `.md` file, not scattered across messages.
- **Your existing agent.** Rewrites use the same Hermes conversation and configured model.
- **Selected changes.** Ask about a passage without replacing the rest of the article.
- **You stay in control.** AI edits remain suggestions until you choose **Accept**. **Reject** keeps the article unchanged.
- **Safe saving.** Autosave and Ctrl/Cmd+S check the saved version before writing. Older edits cannot silently overwrite newer ones. Prior content is kept as a revision.
- **Take it with you.** Copy the Markdown, save it as a `.md` file, browse earlier versions, or ask your agent to commit it to a Git repository.
- **A native workspace.** The editor opens to the right of chat and uses Hermes's public Desktop SDK and UI controls. No core patches.

## Install

### Recommended: the unified Desktop installer

Once this repository is published:

1. Open **Capabilities → Plugins** in Hermes Desktop and select the agent/profile where you want to write.
2. Choose **Install from Git** and paste this repository's HTTPS URL. Review the source and requested components.
3. Select **both Agent and Desktop**. On a remote setup, the Agent half belongs on the server; the Desktop half belongs on the computer running Desktop.
4. Confirm installation and enable both halves. Do not request extra host capabilities; Draftroom declares none.
5. Verify the agent side before the first rewrite: ask the agent to load **`draftroom:blog`** and list drafts with **`blog_draft`**. A Python tool may require a fresh conversation after activation, but check availability first.

After catalog admission, `hermes plugins install draftroom` installs the reviewed, pinned Agent package. A remote Desktop still needs its local UI half; use the combined Desktop installer rather than assuming a server install copied files to your computer.

### Development / local ZIP install

See [INSTALL.md](INSTALL.md) for the explicit two-machine layout, activation checks, updating an existing manual copy, and troubleshooting. Use [TESTING.md](TESTING.md) for the native test checklist before release. No automatic activation workaround or service restart is built into this plugin.

**Requirements:** Hermes **0.23.0 or newer**, a recent Hermes Desktop with the required public SDK doors, and a **Linux or macOS backend**. The Python store uses POSIX `fcntl` locks. The Desktop client can be on another machine; its UI availability depends on that client's SDK version.

## Write together

1. Open a conversation on the profile where Draftroom is enabled.
2. Type `/blog Your article title`, or use **Open Draftroom** in the command palette.
3. Edit the Markdown. Idle edits autosave; **Save** and **Ctrl/Cmd+S** work too.
4. Select a passage, enter a rewrite instruction, and choose **Rewrite**.
5. Review **Original / Suggested** or **Diff**. **Accept** saves only that selected change; **Reject** leaves the draft alone.
6. Close the pane and reopen it from the palette when you want to continue. Saved drafts remain in the library.
7. Under **More**: **Copy Markdown**, **Save .md file** (a download of the editor text), **History** (preview any earlier version and restore it into the editor; restoring saves as a new version), and **Commit to repo…**.

Writing shortcuts: Ctrl/Cmd+S saves; Ctrl/Cmd+Enter in the instruction box requests the rewrite; the preset chips fill in common instructions.

### Commit to a repository

**Commit to repo…** asks *your Hermes agent in this conversation* to write the saved draft to a file path you give and commit it, pushing only if you tick the box. Draftroom itself never runs Git, holds credentials or makes network calls: the agent uses whatever file and Git tools you have enabled, with their normal approval prompts. If your agent has no Git tools, it will say so; use **Save .md file** instead.

If another editor changed the file, a suggestion became stale, or you changed connection/profile, Draftroom pauses instead of force-saving. Compare the saved version, then choose **Use saved version…** or **Keep my version…**. Both need a second confirming click; keeping yours saves against the exact saved version you were shown, and that version stays in revision history. There is no blind force-save.

## Privacy and behaviour disclosure

- Drafts, metadata, proposals and prior revisions live in this backend profile's **own `plugin-data/draftroom/` directory**. The API accepts draft IDs, not arbitrary file paths.
- Draft content and selections go through the **existing Hermes conversation to its configured model**. That model may be hosted remotely. Hermes's normal chat-history and memory-retention settings still apply; Draftroom does not bypass them.
- The plugin makes **no direct third-party network calls**, requests no credentials, starts no external service, runs no shell commands and has no telemetry or self-updater. While the editor is open it polls its own scoped backend for updates.
- Article text is not copied into browser localStorage. Unsaved buffers are held in owner-scoped plugin memory: they survive pane close/reopen and connection/profile switches, but **not** plugin/window reload or quitting Desktop. Saved files survive independently.
- Each draft is limited to **256 KiB** of UTF-8 Markdown. Prior revisions are retained, not silently pruned.
- **Commit to repo…** only sends a chat message to your agent. The Git work, and any credentials or network access it needs, belong to the agent's own tools and approvals, not to Draftroom. Path and commit message are passed as data; the skill refuses Git work that the user didn't explicitly request.
- The `blog_draft` tool can **create, list, read and propose**. It cannot accept, force-save, publish or delete. This is the plugin tool's boundary, not a sandbox around other tools the user separately enables in Hermes.
- Like other native plugins, this is trusted code running with the host user's permissions. Review the source before installing.

## Data layout

```text
<profile-home>/plugin-data/draftroom/drafts/<draft-id>/
  draft.md
  metadata.json
  proposal.json
  revisions/*.md
```

The data directory is outside the installed plugin code, so a code update/removal does not delete the drafts.

## Development

Use an isolated environment, not the one serving your live Hermes:

```sh
uv venv .venv
uv pip install --python .venv/bin/python --exclude-newer '3 days' -r requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q
node --check desktop/plugin.js
node --import ./tests/js/register.mjs --test tests/js/plugin.test.mjs
hermes plugins doctor . --ci
hermes plugins validate . --json
```

The catalog's admission gate also runs `hermes plugins validate . --install-deps`; run it in a disposable compatible Hermes environment before submitting, never by upgrading dependencies in a serving runtime.

Build an allowlisted, checksum-verified runtime ZIP:

```sh
python scripts/build_release.py
```

See [API.md](API.md) for the REST contract, [VERIFICATION.md](VERIFICATION.md) for exact evidence and test boundaries, and [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for remaining release gates. CI runs isolated tests and checks the plain ESM entry point; catalog CI performs the Hermes admission checks.

## Licence

MIT. Prepared test candidate: **0.1.2**. Public hackathon publication follows native user acceptance.

## Official references

- [Python plugins](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)
- [Desktop Plugin SDK](https://hermes-agent.nousresearch.com/docs/developer-guide/desktop-plugin-sdk)
- [Catalog submissions](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins/catalog-submission)
