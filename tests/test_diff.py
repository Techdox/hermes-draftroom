"""The display diff must be valid even for a selected paragraph without its LF."""
import pytest
from draftroom_store import DraftStore


@pytest.mark.parametrize('original,replacement,missing_newlines', [
    ('A rough opening.', 'A clear opening.', 2),
    ('First line\nA rough opening.', 'First line\nA clear opening.', 2),
    ('An opening.\n', 'An opening.', 1),
    ('An opening.', 'An opening.\n', 1),
    ('An opening.', '', 1),
    ('An opening.\r\n', 'A clear opening.\r\n', 0),
])
def test_diff_preserves_separate_lines_and_marks_missing_eof_newlines(tmp_path, original, replacement, missing_newlines):
    store = DraftStore(tmp_path / 'draftroom')
    draft = store.create('Diff regression', 'test-chat')
    draft = store.save(draft['id'], original, draft['version'])
    proposed = store.propose(draft['id'], expected_version=draft['version'], start=0,
                             end=len(original), original=original, replacement=replacement)
    p = proposed['proposal']
    assert p['original'] == original and p['replacement'] == replacement
    assert proposed['content'] == original, 'Building a diff must not mutate article text'
    assert p['diff'].count('\\ No newline at end of file\n') == missing_newlines
    lines = p['diff'].splitlines()
    assert lines[:2] == ['--- Original', '+++ Suggested']
    assert any(line.startswith('-') and not line.startswith('---') for line in lines)
    if replacement:
        assert any(line.startswith('+') and not line.startswith('+++') for line in lines)
    accepted = store.accept(draft['id'], p['id'], draft['version'])
    assert accepted['content'] == replacement, 'Display normalization must never enter saved Markdown'


def test_equal_selection_has_no_spurious_diff(tmp_path):
    store = DraftStore(tmp_path / 'draftroom')
    draft = store.create('Unchanged', 'test-chat')
    content = draft['content']
    p = store.propose(draft['id'], expected_version=draft['version'], start=0,
                      end=len(content), original=content, replacement=content)['proposal']
    assert p['diff'] == ''
