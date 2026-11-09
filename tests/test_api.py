"""Exercise the shipped FastAPI router and actual agent handlers, not invented responses."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


def load(name, path, package=False):
    spec = importlib.util.spec_from_file_location(name, path, submodule_search_locations=[str(path.parent)] if package else None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def api(tmp_path, monkeypatch):
    module = load('draftroom_test_api', ROOT / 'dashboard' / 'plugin_api.py')
    store = module._core.DraftStore(tmp_path / 'api-data')
    monkeypatch.setattr(module, 'get_store', lambda: store)
    events = []
    monkeypatch.setattr(module, '_event', lambda name, value: events.append((name, value['id'])))
    app = FastAPI()
    app.include_router(module.router, prefix='/api/plugins/draftroom')
    with TestClient(app) as client:
        yield client, store, events


def create(client, title='Test article', session='session-1'):
    response = client.post('/api/plugins/draftroom/drafts', json={'title': title, 'session_id': session})
    assert response.status_code == 201, response.text
    return response.json()


def test_real_rest_workflow_survives_reopen(api):
    client, store, events = api
    status = client.get('/api/plugins/draftroom/status').json()
    d = create(client)
    path = '/api/plugins/draftroom/drafts/' + d['id']
    saved = client.put(path, json={'content': '# Real Markdown\n\nA rough opening.\n', 'expected_version': d['version']})
    assert saved.status_code == 200
    d = saved.json()
    start = d['content'].index('A rough')
    proposed = client.post(path + '/proposals', json={'expected_version': d['version'], 'start': start,
                            'end': len(d['content']), 'original': d['content'][start:],
                            'replacement': 'A clearer opening.\n', 'explanation': 'Be direct.'})
    assert proposed.status_code == 201
    assert client.get(path).json()['content'] == d['content']
    p = proposed.json()['proposal']
    accepted = client.post(path + '/proposals/' + p['id'] + '/accept', json={'expected_version': d['version']})
    assert accepted.status_code == 200
    assert accepted.json()['content'].endswith('A clearer opening.\n')
    assert client.get(path).json()['content'] == (store.root / 'drafts' / d['id'] / 'draft.md').read_text()
    assert events[0] == ('draft.opened', d['id'])
    assert len(events) == 4
    assert client.get('/api/plugins/draftroom/drafts?session_id=session-1').json()['drafts'][0]['id'] == d['id']
    assert client.get('/api/plugins/draftroom/drafts?session_id=another-session').json()['drafts'] == []
    assert status['scope'] == d['scope']


def test_rest_stale_save_is_explicit_409(api):
    client, _, _ = api
    d = create(client)
    path = '/api/plugins/draftroom/drafts/' + d['id']
    assert client.put(path, json={'content': 'Current text', 'expected_version': d['version']}).status_code == 200
    r = client.put(path, json={'content': 'Stale text', 'expected_version': d['version']})
    assert r.status_code == 409
    assert r.json()['detail']['code'] == 'conflict'
    assert client.get(path).json()['content'] == 'Current text'


@pytest.mark.parametrize('body', ['{broken', '[]', 'null', '"text"'])
def test_invalid_json_returns_actionable_400(api, body):
    client, _, _ = api
    response = client.post('/api/plugins/draftroom/drafts', content=body)
    assert response.status_code == 400
    assert response.json()['detail']['code'] == 'invalid'


def test_overlarge_request_is_rejected_before_parsing(api):
    client, _, _ = api
    response = client.post('/api/plugins/draftroom/drafts', content='x' * 1_376_257)
    assert response.status_code == 413


def test_invalid_unknown_id_and_missing_version(api):
    client, _, _ = api
    assert client.get('/api/plugins/draftroom/drafts/not-a-valid-id').status_code == 400
    assert client.get('/api/plugins/draftroom/drafts/' + 'a' * 32).status_code == 404
    d = create(client)
    r = client.put('/api/plugins/draftroom/drafts/' + d['id'], json={'content': 'Do not force save'})
    assert r.status_code == 400


def test_accept_and_reject_are_explicit_editor_actions(api):
    client, _, _ = api
    d = create(client)
    path = '/api/plugins/draftroom/drafts/' + d['id']
    body = {'expected_version': d['version'], 'start': 0, 'end': len(d['content']),
            'original': d['content'], 'replacement': '# A proposed edit\n'}
    pending = client.post(path + '/proposals', json=body).json()['proposal']
    rejected = client.post(path + '/proposals/' + pending['id'] + '/reject', json={})
    assert rejected.status_code == 200
    assert rejected.json()['content'] == d['content']
    assert client.post(path + '/proposals/' + pending['id'] + '/accept', json={'expected_version': d['version']}).status_code == 409


def test_disk_writes_do_not_block_the_gateway_event_loop(api, monkeypatch):
    import threading
    client, store, _ = api
    module = sys.modules['draftroom_test_api']
    body_threads, disk_threads = [], []
    read_body, save = module._body, store.save
    async def body(request):
        body_threads.append(threading.get_ident())
        return await read_body(request)
    def disk(*args, **kwargs):
        disk_threads.append(threading.get_ident())
        return save(*args, **kwargs)
    monkeypatch.setattr(module, '_body', body)
    monkeypatch.setattr(store, 'save', disk)
    d = create(client)
    response = client.put('/api/plugins/draftroom/drafts/' + d['id'],
                          json={'content': 'A filesystem write', 'expected_version': d['version']})
    assert response.status_code == 200
    assert disk_threads[-1] != body_threads[-1]


@pytest.fixture
def plugin(tmp_path, monkeypatch):
    module = load('draftroom_test_plugin', ROOT / '__init__.py', package=True)
    store = module.DraftStore(tmp_path / 'plugin-data')
    monkeypatch.setattr(module, 'get_store', lambda: store)
    events = []
    monkeypatch.setattr(module, 'emit_event', lambda event, draft: events.append((event, draft['id'])))
    return module, store, events


def test_agent_can_propose_but_cannot_apply(plugin):
    module, store, _ = plugin
    d = json.loads(module.blog_draft({'action': 'create', 'title': 'Agent-created post', 'session_id': 'x'}))
    p = json.loads(module.blog_draft({'action': 'propose', 'draft_id': d['id'], 'expected_version': d['version'],
                    'start': 0, 'end': len(d['content']), 'original': d['content'], 'replacement': '# Suggested\n'}))
    assert p['ok'] and p['proposal']['status'] == 'pending'
    assert store.read(d['id'])['content'] == d['content']
    for action in ['accept', 'save', 'publish', 'delete', 'run']:
        result = json.loads(module.blog_draft({'action': action, 'draft_id': d['id']}))
        assert result['ok'] is False
    assert store.read(d['id'])['content'] == d['content']


def test_agent_returns_structured_errors_and_exact_read(plugin):
    module, store, _ = plugin
    assert json.loads(module.blog_draft([]))['ok'] is False
    assert json.loads(module.blog_draft({'action': 'read', 'draft_id': '../outside'}))['error']['code'] == 'invalid'
    d = store.create('Read me', 'chat')
    assert json.loads(module.blog_draft({'action': 'read', 'draft_id': d['id']}))['version'] == d['version']
    assert len(json.loads(module.blog_draft({'action': 'list'}))['drafts']) == 1
    assert json.loads(module.blog_draft({'action': 'propose', 'draft_id': d['id']}))['ok'] is False


def test_blog_slash_opens_or_reopens_calling_sessions_draft(plugin):
    module, store, events = plugin
    assert 'My actual article' in module.handle_blog('My actual article', session_id='chat-1')
    assert len(store.list('chat-1')) == 1
    assert 'My actual article' in module.handle_blog('', session_id='chat-1')
    assert len(store.list('chat-1')) == 1
    assert 'Untitled draft' in module.handle_blog('', session_id='chat-2')
    assert len(store.list('chat-2')) == 1
    assert events[0][0] == 'draft.opened'


def test_real_registration_declares_only_the_frozen_scope(plugin):
    module, _, _ = plugin
    class Context:
        def __init__(self):
            self.tools, self.commands, self.skills = [], [], []
        def register_tool(self, **kwargs): self.tools.append(kwargs)
        def register_command(self, name, **kwargs): self.commands.append((name, kwargs))
        def register_skill(self, name, path): self.skills.append((name, path))
    ctx = Context()
    module.register(ctx)
    assert [tool['name'] for tool in ctx.tools] == ['blog_draft']
    assert [name for name, _ in ctx.commands] == ['blog']
    assert ctx.skills[0][1].is_file()
    assert module.SCHEMA['parameters']['properties']['action']['enum'] == ['list', 'read', 'create', 'propose']
