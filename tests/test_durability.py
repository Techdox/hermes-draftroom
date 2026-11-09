"""Storage interruption and maximum-size proposal regressions."""
import pytest
from draftroom_store import DraftStore


@pytest.fixture
def store(tmp_path):
    return DraftStore(tmp_path / 'data')


def draft(store):
    return store.create('Test draft', 'chat-1')


def proposal(store, d, **kwargs):
    values = dict(expected_version=d['version'], start=0, end=len(d['content']),
                  original=d['content'], replacement='# Clearer draft\n')
    values.update(kwargs)
    return store.propose(d['id'], **values)


def test_large_line_diff_is_still_a_valid_proposal(store):
    d = draft(store)
    old = 'a\n' * 110000
    d = store.save(d['id'], old, d['version'])
    pending = proposal(store, d, original=old, end=len(old), replacement='b\n' * 110000)
    assert pending['proposal']['status'] == 'pending'
    assert pending['content'] == old
    assert store.read(d['id'])['proposal']['id'] == pending['proposal']['id']


def test_accept_recovers_after_markdown_written_but_status_write_interrupted(store, monkeypatch):
    d = draft(store)
    p = proposal(store, d)['proposal']
    write_json = store._write_json
    interrupted = [False]
    def write(path, value):
        if path.name == 'proposal.json' and value.get('status') == 'accepted' and not interrupted[0]:
            interrupted[0] = True
            raise OSError('Simulated interrupted metadata write')
        return write_json(path, value)
    monkeypatch.setattr(store, '_write_json', write)
    with pytest.raises(OSError):
        store.accept(d['id'], p['id'], d['version'])
    assert store.read(d['id'])['content'] == p['replacement']
    recovered = store.accept(d['id'], p['id'], d['version'])
    assert recovered['proposal']['status'] == 'accepted'
    assert len(list(store.root.rglob('revisions/*.md'))) == 1


def test_failed_markdown_replace_preserves_original(store, monkeypatch):
    d = draft(store)
    atomic = store._atomic
    def write(path, content):
        if path.name == 'draft.md':
            raise OSError('Simulated disk-full before replace')
        return atomic(path, content)
    monkeypatch.setattr(store, '_atomic', write)
    with pytest.raises(OSError):
        store.save(d['id'], 'Must not partially write', d['version'])
    assert store.read(d['id'])['content'] == d['content']
