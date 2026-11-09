# Install and verify Draftroom

Draftroom has **two halves**. The Agent package supplies the `blog_draft` tool, bundled skill and file-backed API. The Desktop file supplies the editor. Both must be enabled for the conversation's actual backend/profile.

## Combined install from a published repository

Use **Capabilities → Plugins → Install from Git**, select the intended agent/profile, review this repository's source, and check **Agent + Desktop**. The installer coordinates the remote Agent install and local Desktop clone. Accept only the components you intend to install. Nothing in Draftroom auto-installs itself or broadens host permissions.

This is the recommended end-user path. The commands below are for development or an unpacked local ZIP.

## Local Agent package

Copy the unpacked `draftroom` directory into the intended profile's plugin directory:

```text
<profile-home>/plugins/draftroom/
  plugin.yaml
  __init__.py
  draftroom_store.py
  desktop/plugin.js
  dashboard/manifest.json
  dashboard/plugin_api.py
  skills/blog/SKILL.md
```

Do not copy another profile's configuration, `.venv`, secrets, caches or draft data. Enable **draftroom** through that profile's normal plugin manager. CLI users can run `hermes -p <profile> plugins enable draftroom`.

An enabled setting is not proof of live chat registration. A machine can have both a canonical gateway daemon and a separate Desktop `serve` process. A CLI reload of one does not prove the other loaded the tool. Use the **Agent / Agent + Desktop** control in the signed-in Desktop's Plugins page for the actual profile being used.

## Local Desktop file

On the computer running Desktop:

1. Use **Settings → Plugins → Open plugins folder** to find the app's real local desktop-plugin root. Do not substitute the remote server's home path.
2. Copy the package's `desktop/plugin.js` into a subdirectory named `draftroom`:

   ```text
   <local-desktop-plugin-root>/draftroom/plugin.js
   ```

3. Run **Reload desktop plugins** from the command palette and enable Draftroom if it is off.

The local file must not sit loose in the root. Recent Desktop versions keep this root app-level rather than profile-scoped.

## Verify once, then write

Before a first rewrite, confirm these separately:

- **UI:** the **Open Draftroom** palette command opens an editor beside chat.
- **Agent:** the actual conversation can load `draftroom:blog` and call `blog_draft(action="list")`.
- **Storage:** creating a harmless draft and reopening it shows saved Markdown.
- **Review:** a real model proposal leaves the article unchanged until the user chooses **Accept**.

If the skill/tool is missing, do **not** repeatedly retry Rewrite or create new conversations without changed registration state. Check the correct Agent/Both plugin entry and its activation result. Python tools can be deferred until the next session, but probe availability first. A shared backend restart needs its operator's approval.

If a rewrite has already been handed to a conversation, inspect that chat before retrying. **Retry request** remains bound to the original conversation. To intentionally move a new request to another chat, clear the old waiting state in the editor, focus the new chat, reselect the passage and submit a fresh rewrite. Clearing the UI wait does not cancel an already running agent turn; any late proposal still needs review.

## Updating

Prefer Hermes's normal reviewed catalog or Git update flow. A catalog version label is not the trust boundary: installs pin an exact commit and updates require a reviewed new pin.

For a manual local copy, save work first, update the Agent code in its install directory, and activate that package in the actual Desktop backend's Agent/Both control. Replace the local Desktop file only if it changed. A marker-less file installed by hand is not necessarily replaced by the unified installer; do not silently overwrite it.

Never overwrite `plugin-data/draftroom`, delete drafts, copy another profile's configuration, weaken authentication, or restart unrelated services to update this plugin.

## Compatibility / limitations

- Backend: POSIX Linux or macOS; file locking uses `fcntl`.
- Hermes Agent: `>=0.23.0`.
- Desktop: the public `host.openWorkspace`, focused-owner/session atoms, `host.composer.submit`, `ctx.rest`, composer middleware, React Query and native UI controls. Missing APIs should produce an update message rather than a private-core fallback.
- Native REST requests already dispatched cannot be physically cancelled through this SDK; ownership and result fences prevent stale responses from overwriting another owner's editor or issuing follow-up writes there.
- A composer acknowledgement means the visible chat surface claimed the request, not that a model completed it. Unknown delivery is never auto-retried.
- Unsaved memory does not survive plugin/window reload or quitting. Save before updating or disabling either half.
