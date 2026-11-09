"""The same scoped REST namespace serves native Desktop through ctx.rest.

Authentication and active-profile scoping are owned by Hermes' plugin mount.
Do not add a second port, token scheme, permissive CORS, or arbitrary-path API.
"""
from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from starlette.concurrency import run_in_threadpool

# Dashboard backends are loaded by file, not as children of their Python plugin.
# Load our own adjacent store without mutating global sys.path or importing host internals.
_spec = importlib.util.spec_from_file_location('draftroom_backend_store', Path(__file__).resolve().parents[1] / 'draftroom_store.py')
if _spec is None or _spec.loader is None:
    raise ImportError('Draftroom store could not be loaded from the plugin package.')
_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)

router = APIRouter()
log = logging.getLogger(__name__)
MAX_REQUEST_BYTES = 1_376_256


def get_store():
    from plugins.plugin_storage import plugin_data_dir
    return _core.DraftStore(plugin_data_dir('draftroom'))


def _event(event, draft):
    try:
        from hermes_cli.plugin_events import broadcast_plugin_event
        broadcast_plugin_event('draftroom', event, {'scope': draft['scope'], 'draft_id': draft['id'], 'session_id': draft['session_id']})
    except Exception:
        log.debug('Draftroom notification unavailable; clients can refetch.', exc_info=True)


def _run(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except _core.StoreError as exc:
        raise HTTPException(exc.status, detail={'code': exc.code, 'message': str(exc)}) from exc


async def _body(request):
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_REQUEST_BYTES:
            raise HTTPException(413, detail={'code': 'too_large', 'message': 'Request exceeds the draft size limit.'})
        chunks.append(chunk)
    try:
        result = json.loads(b''.join(chunks) or b'{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(400, detail={'code': 'invalid', 'message': 'Expected a JSON object.'}) from None
    if not isinstance(result, dict):
        raise HTTPException(400, detail={'code': 'invalid', 'message': 'Expected a JSON object.'})
    return result


@router.get('/status')
def status():
    store = get_store()
    return {'name': 'draftroom', 'scope': store.scope, 'max_content_bytes': store.MAX_CONTENT_BYTES}


@router.get('/drafts')
def list_drafts(session_id: str | None = None):
    store = get_store()
    return {'drafts': _run(store.list, session_id), 'scope': store.scope}


@router.post('/drafts', status_code=201)
async def create_draft(request: Request):
    body = await _body(request)
    store = get_store()
    draft = await run_in_threadpool(_run, store.create, body.get('title'), body.get('session_id', ''))
    _event('draft.opened', draft)
    return draft


@router.get('/drafts/{draft_id}')
def read_draft(draft_id: str):
    return _run(get_store().read, draft_id)


@router.put('/drafts/{draft_id}')
async def save_draft(draft_id: str, request: Request):
    body = await _body(request)
    draft = await run_in_threadpool(_run, get_store().save, draft_id, body.get('content'), body.get('expected_version'))
    _event('draft.updated', draft)
    return draft


@router.post('/drafts/{draft_id}/proposals', status_code=201)
async def propose(draft_id: str, request: Request):
    body = await _body(request)
    fields = ('expected_version', 'start', 'end', 'original', 'replacement')
    draft = await run_in_threadpool(_run, get_store().propose, draft_id, **{key: body.get(key) for key in fields}, explanation=body.get('explanation', ''))
    _event('draft.updated', draft)
    return draft


@router.post('/drafts/{draft_id}/proposals/{proposal_id}/accept')
async def accept(draft_id: str, proposal_id: str, request: Request):
    body = await _body(request)
    draft = await run_in_threadpool(_run, get_store().accept, draft_id, proposal_id, body.get('expected_version'))
    _event('draft.updated', draft)
    return draft


@router.post('/drafts/{draft_id}/proposals/{proposal_id}/reject')
async def reject(draft_id: str, proposal_id: str, request: Request):
    await _body(request)
    draft = await run_in_threadpool(_run, get_store().reject, draft_id, proposal_id)
    _event('draft.updated', draft)
    return draft
