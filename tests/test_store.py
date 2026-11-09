"""Real filesystem tests: the Markdown file is authoritative."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from draftroom_store import Conflict, DraftStore, Invalid, Missing, TooLarge


@pytest.fixture
def store(tmp_path):
    return DraftStore(tmp_path / 'plugin-data')


def draft(store, title='A useful blog post', session='chat-1'):
    return store.create(title, session)


def proposal(store, d, **overrides):
    values = dict(expected_version=d['version'], start=0, end=len(d['content']),
                  original=d['content'], replacement='# A clearer title\n\nBetter words.\n',
                  explanation='Tighter opening.')
    values.update(overrides)
    return store.propose(d['id'], **values)


def test_create_is_real_markdown_and_reopens(store):
    d = draft(store)
    assert d['content'] == '# A useful blog post\n\n'
    assert (store.root / 'drafts' / d['id'] / 'draft.md').read_text() == d['content']
    assert d['version'] == hashlib.sha256(d['content'].encode()).hexdigest()
    assert DraftStore(store.root).read(d['id']) == d


def test_list_filters_sessions_and_never_contains_other_profile(tmp_path):
    a, b = DraftStore(tmp_path / 'a'), DraftStore(tmp_path / 'b')
    d = draft(a)
    draft(a, 'Another post', 'chat-2')
    assert [x['id'] for x in a.list('chat-1')] == [d['id']]
    assert len(a.list()) == 2
    assert b.list() == []
    assert a.scope != b.scope


def test_atomic_save_keeps_prior_revision(store):
    d = draft(store)
    saved = store.save(d['id'], '# Changed\n\nLocal edits.\n', d['version'])
    assert saved['content'].endswith('Local edits.\n')
    revisions = list((store.root / 'drafts' / d['id'] / 'revisions').glob('*.md'))
    assert [p.read_text() for p in revisions] == [d['content']]
    assert not list(store.root.rglob('*.tmp'))


def test_same_content_save_is_noop(store):
    d = draft(store)
    assert store.save(d['id'], d['content'], d['version'])['version'] == d['version']
    assert not list((store.root / 'drafts' / d['id'] / 'revisions').glob('*.md'))


def test_stale_save_preserves_both_disk_and_no_extra_history(store):
    d = draft(store)
    current = store.save(d['id'], 'A newer human edit', d['version'])
    with pytest.raises(Conflict):
        store.save(d['id'], 'Stale text must not win', d['version'])
    assert store.read(d['id'])['content'] == current['content']
    assert len(list(store.root.rglob('revisions/*.md'))) == 1


def test_external_editor_change_is_detected(store):
    d = draft(store)
    (store.root / 'drafts' / d['id'] / 'draft.md').write_text('Edited outside Hermes')
    with pytest.raises(Conflict):
        store.save(d['id'], 'Wrong', d['version'])
    assert store.read(d['id'])['content'] == 'Edited outside Hermes'


def test_concurrent_writers_only_one_wins(store):
    d = draft(store)
    def write(text):
        try:
            return store.save(d['id'], text, d['version'])['content']
        except Conflict:
            return 'conflict'
    with ThreadPoolExecutor(2) as pool:
        values = list(pool.map(write, ['First competing edit', 'Second competing edit']))
    assert values.count('conflict') == 1
    assert store.read(d['id'])['content'] in values


def test_proposal_never_changes_markdown_until_accepted(store):
    d = draft(store)
    pending = proposal(store, d)
    assert pending['content'] == d['content']
    assert pending['proposal']['status'] == 'pending'
    assert '-# A useful blog post' in pending['proposal']['diff']
    assert store.read(d['id'])['content'] == d['content']
    accepted = store.accept(d['id'], pending['proposal']['id'], d['version'])
    assert accepted['content'] == pending['proposal']['replacement']
    assert accepted['proposal']['status'] == 'accepted'


def test_reject_keeps_content(store):
    d = draft(store)
    p = proposal(store, d)['proposal']
    result = store.reject(d['id'], p['id'])
    assert result['content'] == d['content']
    assert result['proposal']['status'] == 'rejected'
    with pytest.raises(Conflict):
        store.accept(d['id'], p['id'], d['version'])


def test_stale_proposal_cannot_overwrite_human_edits(store):
    d = draft(store)
    p = proposal(store, d)['proposal']
    edited = store.save(d['id'], 'Human changed it first', d['version'])
    with pytest.raises(Conflict):
        store.accept(d['id'], p['id'], edited['version'])
    assert store.read(d['id'])['content'] == edited['content']
    assert store.read(d['id'])['proposal']['status'] == 'pending'


def test_selection_must_match_exactly(store):
    d = draft(store)
    with pytest.raises(Conflict):
        proposal(store, d, original='Not the selected text')
    with pytest.raises(Conflict):
        proposal(store, d, expected_version='0' * 64)
    assert store.read(d['id'])['proposal'] is None


def test_unicode_ranges_use_codepoints(store):
    d = draft(store)
    text = 'Hello 👩🏽‍💻 — tēnā koe.\n'
    d = store.save(d['id'], text, d['version'])
    start, end = text.index('tēnā'), text.index('tēnā') + len('tēnā koe')
    p = proposal(store, d, start=start, end=end, original='tēnā koe', replacement='kia ora')['proposal']
    assert store.accept(d['id'], p['id'], d['version'])['content'] == text.replace('tēnā koe', 'kia ora')


def test_identical_proposal_and_accept_retries_are_idempotent(store):
    d = draft(store)
    first, second = proposal(store, d), proposal(store, d)
    assert first['proposal']['id'] == second['proposal']['id']
    pid = first['proposal']['id']
    one = store.accept(d['id'], pid, d['version'])
    two = store.accept(d['id'], pid, d['version'])
    assert one['version'] == two['version']
    assert len(list(store.root.rglob('revisions/*.md'))) == 1


def test_pending_proposal_cannot_be_silently_replaced(store):
    d = draft(store)
    first = proposal(store, d)
    with pytest.raises(Conflict):
        proposal(store, d, replacement='A completely different rewrite')
    assert store.read(d['id'])['proposal']['id'] == first['proposal']['id']


@pytest.mark.parametrize('bad', ['../outside', 'a/b', '', 'A' * 32, 'a' * 31, 'a' * 33, None])
def test_ids_reject_traversal_and_malformed_tokens(store, bad):
    with pytest.raises(Invalid):
        store.read(bad)


def test_unknown_valid_id_is_missing(store):
    with pytest.raises(Missing):
        store.read('0' * 32)


@pytest.mark.parametrize('values', [dict(start=-1), dict(end=999), dict(start=True),
                                     dict(replacement=12), dict(end=0), dict(original=None)])
def test_invalid_selection_and_replacement_are_rejected(store, values):
    d = draft(store)
    with pytest.raises((Invalid, Conflict)):
        proposal(store, d, **values)


def test_oversized_save_and_proposal_rejected_without_data_loss(store):
    d = draft(store)
    with pytest.raises(TooLarge):
        store.save(d['id'], 'x' * (store.MAX_CONTENT_BYTES + 1), d['version'])
    with pytest.raises(TooLarge):
        proposal(store, d, replacement='x' * (store.MAX_CONTENT_BYTES + 1))
    assert store.read(d['id'])['content'] == d['content']


def test_symlink_file_and_directory_cannot_escape_data_root(store, tmp_path):
    d = draft(store)
    external = tmp_path / 'private.md'
    external.write_text('Private outside content')
    target = store.root / 'drafts' / d['id'] / 'draft.md'
    target.unlink()
    target.symlink_to(external)
    with pytest.raises(Invalid):
        store.read(d['id'])
    target.unlink()
    outside_dir = tmp_path / 'outside'
    outside_dir.mkdir()
    (outside_dir / 'draft.md').write_text('Outside')
    folder = store.root / 'drafts' / ('f' * 32)
    folder.symlink_to(outside_dir, target_is_directory=True)
    with pytest.raises(Invalid):
        store.read('f' * 32)
    assert external.read_text() == 'Private outside content'


def test_corrupt_metadata_preserved_and_reported(store):
    d = draft(store)
    p = store.root / 'drafts' / d['id'] / 'metadata.json'
    p.write_text('{not valid JSON')
    with pytest.raises(Invalid):
        store.read(d['id'])
    assert p.read_text() == '{not valid JSON'


def test_private_permissions(store):
    d = draft(store)
    folder = store.root / 'drafts' / d['id']
    assert folder.stat().st_mode & 0o077 == 0
    assert (folder / 'draft.md').stat().st_mode & 0o077 == 0


def test_empty_or_multiline_titles_rejected(store):
    for title in ['', '   ', 'Hello\nWorld', 123, 'x' * 241]:
        with pytest.raises(Invalid):
            store.create(title, 'chat-1')


@pytest.mark.parametrize('damage', ['invalid_utf8', 'oversized', 'corrupt_metadata', 'missing_markdown'])
def test_one_damaged_draft_does_not_hide_the_library(store, damage):
    good = draft(store, 'Readable draft')
    bad = draft(store, 'Edited elsewhere')
    folder = store.root / 'drafts' / bad['id']
    if damage == 'invalid_utf8':
        (folder / 'draft.md').write_bytes('caf\xe9'.encode('latin-1'))
    elif damage == 'oversized':
        (folder / 'draft.md').write_text('x' * (store.MAX_CONTENT_BYTES + 1))
    elif damage == 'corrupt_metadata':
        (folder / 'metadata.json').write_text('{not json')
    else:
        (folder / 'draft.md').unlink()
    before = sorted((p.name, p.read_bytes()) for p in folder.iterdir() if p.is_file())
    listing = store.catalog()
    assert [row['id'] for row in listing['drafts']] == [good['id']]
    assert [row['id'] for row in listing['unavailable']] == [bad['id']]
    assert listing['unavailable'][0]['code'] in {'invalid', 'too_large', 'not_found'}
    assert [row['id'] for row in store.list()] == [good['id']]
    # Reported, never repaired or deleted.
    assert sorted((p.name, p.read_bytes()) for p in folder.iterdir() if p.is_file()) == before


def test_create_is_atomic_for_concurrent_listing(store, monkeypatch):
    seen = []
    atomic = store._atomic
    def observe(path, content):
        seen.append(store.catalog())  # A poll landing in the middle of create.
        return atomic(path, content)
    monkeypatch.setattr(store, '_atomic', observe)
    created = draft(store)
    assert seen and all(view == {'drafts': [], 'unavailable': []} for view in seen)
    assert [row['id'] for row in store.list()] == [created['id']]
    assert sorted(p.name for p in store.drafts.iterdir()) == [created['id']]


def test_failed_create_leaves_no_partial_draft(store, monkeypatch):
    atomic = store._atomic
    def fail(path, content):
        if path.name == 'draft.md':
            raise OSError('Simulated disk full')
        return atomic(path, content)
    monkeypatch.setattr(store, '_atomic', fail)
    with pytest.raises(OSError):
        draft(store)
    assert list(store.drafts.iterdir()) == []
    assert store.catalog() == {'drafts': [], 'unavailable': []}


def test_revisions_list_newest_first_and_read_exact_bytes(store):
    d = draft(store)
    first = store.save(d['id'], 'Second version\r\n', d['version'])
    store.save(d['id'], 'Third version', first['version'])
    listing = store.revisions(d['id'])
    assert listing['total'] == 2
    assert [row['version'] for row in listing['revisions']] == [first['version'], d['version']]
    assert store.revision(d['id'], listing['revisions'][0]['id'])['content'] == 'Second version\r\n'
    assert store.revision(d['id'], listing['revisions'][1]['id'])['content'] == d['content']
    assert store.read(d['id'])['content'] == 'Third version'  # Listing/reading never restores.


def test_revisions_empty_and_limit(store):
    d = draft(store)
    assert store.revisions(d['id']) == {'id': d['id'], 'revisions': [], 'total': 0}
    current = d
    for n in range(4):
        current = store.save(d['id'], f'v{n}', current['version'])
    assert len(store.revisions(d['id'], limit=2)['revisions']) == 2
    assert store.revisions(d['id'], limit=2)['total'] == 4


@pytest.mark.parametrize('bad', ['../draft', '1-' + 'a' * 63, 'x-' + 'a' * 64, '', None, '1-' + 'a' * 64 + '/../x'])
def test_revision_ids_reject_traversal(store, bad):
    d = draft(store)
    with pytest.raises(Invalid):
        store.revision(d['id'], bad)


def test_unknown_revision_is_missing_and_symlinked_revision_refused(store, tmp_path):
    d = draft(store)
    store.save(d['id'], 'Next', d['version'])
    with pytest.raises(Missing):
        store.revision(d['id'], '1-' + 'b' * 64)
    secret = tmp_path / 'secret.md'
    secret.write_text('outside')
    (store.root / 'drafts' / d['id'] / 'revisions' / ('2-' + 'c' * 64 + '.md')).symlink_to(secret)
    assert all(row['id'] != '2-' + 'c' * 64 for row in store.revisions(d['id'])['revisions'])
    with pytest.raises(Invalid):
        store.revision(d['id'], '2-' + 'c' * 64)
