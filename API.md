# Draftroom MVP contract

Plugin ID: `draftroom`. One Python/desktop package. No publishing, SEO, external services, custom model credentials, or core changes.

## State

Every draft is a real UTF-8 `draft.md` under `plugin_data_dir('draftroom')/drafts/<id>/`. IDs are lowercase UUID hex. `version` is the SHA-256 of the exact UTF-8 Markdown. All writes require the current version, are atomic, and retain the previous Markdown as an immutable revision. Titles and creation/session metadata are separate. No agent tool accepts or saves a proposal: acceptance belongs to the editor user.

## REST (`ctx.rest`, already rooted at `/api/plugins/draftroom`)

- `GET /status` → `{name:'draftroom', scope:<opaque profile data-root hash>, max_content_bytes:262144}`.
- `GET /drafts?session_id=<optional>` → `{drafts:[{id,title,session_id,version,created_at,updated_at}], unavailable:[{id,code,message}], scope}`. A draft that cannot be read (non-UTF-8, over the size limit, damaged metadata) is listed in `unavailable` instead of failing the whole list; its files are never repaired or deleted.
- `POST /drafts` JSON `{title, session_id?}` → full draft. Creates `# <title>\n\n` (not AI-generated filler).
- `GET /drafts/<id>` → full draft.
- `PUT /drafts/<id>` JSON `{content, expected_version}` → full draft.
- `GET /drafts/<id>/revisions` → `{id, revisions:[{id,version,bytes,created_at}], total, scope}`, newest first, up to 100. Read-only.
- `GET /drafts/<id>/revisions/<revision_id>` → `{id, draft_id, content, version, created_at, scope}`. `revision_id` is `<time_ns>-<sha256>`; anything else is 400. There is no restore route: the editor loads a revision as ordinary text and saves it through `PUT` with a version check.
- `POST /drafts/<id>/proposals` JSON `{expected_version, start, end, original, replacement, explanation?}` → full draft. For testing and agent integration. Indices count Unicode code points, NOT UTF-16 code units. The exact original selection and version are checked.
- `POST /drafts/<id>/proposals/<proposal_id>/accept` JSON `{expected_version}` → full draft.
- `POST /drafts/<id>/proposals/<proposal_id>/reject` JSON `{}` → full draft.

Full draft: `{id,title,session_id,content,version,created_at,updated_at,proposal:null|{id,base_version,start,end,original,replacement,explanation,status:'pending'|'accepted'|'rejected',diff,created_at},scope}`.

Errors: `{detail:{code,message}}`, HTTP 400 invalid input, 404 unknown draft/proposal, 409 stale version or pending-review conflict, 413 over size limit. No force-save/force-apply route. A stale pending proposal remains visible but cannot be applied. A duplicate identical proposal is idempotent. A retried accept is idempotent and does not add another revision.

## Agent

`blog_draft` actions: `list` (same `drafts`/`unavailable` shape as REST), `read`, `create`, `propose`. Never `save`, `accept`, `publish`, or arbitrary filesystem paths. Proposals use the REST shape above. `/blog <topic>` reopens the calling session's draft with that exact title, or creates one; `/blog` alone reopens its most recent draft; emits `plugin.draftroom.draft.opened` with `{scope,draft_id,session_id}`. Tool proposals emit `plugin.draftroom.draft.updated` with the same identifiers, never article text.

## Editor

A right-hand pane, preserving chat. Plain Markdown editor, optional native Markdown preview, saved/dirty/error status, list/reopen drafts, Ctrl/Cmd+S, and a selection + instruction control. Before asking chat for a rewrite, save the current editor text and send the exact draft ID, version, code-point range, original text and instruction. Ask the active Hermes agent to use `blog_draft(action='propose', ...)`, not write a file. Display original/replacement or unified diff; explicit Accept and Reject. Never accept while dirty or stale. A conflict offers Use saved version or Keep my version, each confirmed; Keep my version saves with `expected_version` equal to the saved version shown, never a blind overwrite. Never overwrite dirty editor text after polling, session/profile/connection changes, or an arriving suggestion. Failed saves retain the text. Cancel requests and clear profile/connection-scoped caches on scope change. No localStorage copy of private article text. Copy Markdown and Save .md file (a Blob download) export the editor text. Commit to repo… saves, re-reads, then submits a `Draftroom commit request.` chat message with the draft ID, version and a JSON `{target_path, commit_message, push}`; the agent does any Git work with its own tools. Normal writing still uses the current configured Hermes agent, not a separate provider call.
