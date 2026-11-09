"""Draftroom's file store: Markdown is the source of truth; AI edits are proposals.

Only plugin-owned UUID directories are addressable. Optimistic versions plus a
cross-process POSIX lock prevent lost updates. No network or model calls here.
"""
from __future__ import annotations

import contextlib
import difflib
import fcntl
import hashlib
import json
import os
import re
import stat
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


class StoreError(Exception):
    code = 'invalid'
    status = 400


class Invalid(StoreError):
    pass


class Missing(StoreError):
    code = 'not_found'
    status = 404


class Conflict(StoreError):
    code = 'conflict'
    status = 409


class TooLarge(StoreError):
    code = 'too_large'
    status = 413


_ID = re.compile(r'[0-9a-f]{32}\Z')
_VERSION = re.compile(r'[0-9a-f]{64}\Z')


def _now():
    return datetime.now(timezone.utc).isoformat()


def _hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _review_diff(original, replacement):
    """Frame display lines without ever normalizing the actual Markdown.

    difflib preserves a missing final newline on a selected paragraph. Joining
    those chunks directly glues the '-' and '+' rows together. Use the standard
    unified-diff EOF marker to keep both the line framing and that distinction.
    """
    chunks = difflib.unified_diff(original.splitlines(keepends=True),
                                  replacement.splitlines(keepends=True),
                                  fromfile='Original', tofile='Suggested')
    return ''.join(chunk if chunk.endswith('\n') else
                   chunk + '\n\\ No newline at end of file\n' for chunk in chunks)


def _identifier(value):
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise Invalid('Invalid draft or proposal ID.')
    return value


def _version(value):
    if not isinstance(value, str) or not _VERSION.fullmatch(value):
        raise Invalid('A valid expected_version is required; there is no force save.')
    return value


class DraftStore:
    MAX_CONTENT_BYTES = 262144

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.drafts = self.root / 'drafts'
        self._directory(self.drafts, create=True)
        self.scope = hashlib.sha256(str(self.root).encode()).hexdigest()[:24]

    @staticmethod
    def _directory(path, *, create=False):
        if path.is_symlink():
            raise Invalid('Symlinked data directories are not supported.')
        if create:
            path.mkdir(exist_ok=True, mode=0o700)
        if not path.is_dir():
            raise Missing('Draft not found.')
        return path

    def _folder(self, draft_id):
        return self._directory(self.drafts / _identifier(draft_id))

    @staticmethod
    def _read_text(path, limit):
        if path.is_symlink():
            raise Invalid('Symlinked data files are not supported.')
        flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
        try:
            fd = os.open(path, flags)
        except FileNotFoundError:
            raise Missing('Draft data not found.') from None
        except OSError as exc:
            raise Invalid('Draft data could not be opened safely.') from exc
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise Invalid('Draft data must be a regular file.')
            with os.fdopen(fd, 'rb') as stream:
                fd = -1
                data = stream.read(limit + 1)
            if len(data) > limit:
                raise TooLarge('Draft data exceeds its size limit.')
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                raise Invalid('Draft data must be valid UTF-8; original file preserved.') from None
        finally:
            if fd != -1:
                os.close(fd)

    @classmethod
    def _json(cls, path, limit):
        try:
            value = json.loads(cls._read_text(path, limit))
        except json.JSONDecodeError:
            raise Invalid('Draft metadata is damaged; original file preserved.') from None
        if not isinstance(value, dict):
            raise Invalid('Draft metadata must be a JSON object; original file preserved.')
        return value

    @staticmethod
    def _atomic(path, content):
        if path.is_symlink():
            raise Invalid('Symlinked data files are not supported.')
        fd, temporary = tempfile.mkstemp(prefix='.draftroom-', suffix='.tmp', dir=path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8', newline='') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            dir_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    @classmethod
    def _write_json(cls, path, value):
        cls._atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')

    @contextlib.contextmanager
    def _locked(self, folder):
        lock = folder / '.lock'
        if lock.is_symlink():
            raise Invalid('Symlinked lock files are not supported.')
        try:
            fd = os.open(lock, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        except OSError as exc:
            raise Invalid('Could not lock the draft safely.') from exc
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    @classmethod
    def _content(cls, content):
        if not isinstance(content, str):
            raise Invalid('Markdown must be a string.')
        try:
            size = len(content.encode('utf-8'))
        except UnicodeEncodeError:
            raise Invalid('Markdown must contain valid Unicode.') from None
        if size > cls.MAX_CONTENT_BYTES:
            raise TooLarge('This draft exceeds the 256 KiB Markdown limit.')
        return content

    def create(self, title, session_id=''):
        if not isinstance(title, str):
            raise Invalid('A title is required.')
        title = title.strip()
        if not title or len(title) > 240 or any(ord(c) < 32 or ord(c) == 127 for c in title):
            raise Invalid('Use a single-line title between 1 and 240 characters.')
        if not isinstance(session_id, str) or len(session_id) > 256:
            raise Invalid('Invalid session ID.')
        draft_id = uuid.uuid4().hex
        folder = self.drafts / draft_id
        folder.mkdir(mode=0o700)
        metadata = {'id': draft_id, 'title': title, 'session_id': session_id, 'created_at': _now()}
        with self._locked(folder):
            self._write_json(folder / 'metadata.json', metadata)
            self._atomic(folder / 'draft.md', '# ' + title + '\n\n')
        return self.read(draft_id)

    def _read(self, folder):
        metadata = self._json(folder / 'metadata.json', 8192)
        if metadata.get('id') != folder.name or not isinstance(metadata.get('title'), str):
            raise Invalid('Draft metadata does not match its directory; original preserved.')
        content = self._read_text(folder / 'draft.md', self.MAX_CONTENT_BYTES)
        proposal_path = folder / 'proposal.json'
        proposal = self._json(proposal_path, self.MAX_CONTENT_BYTES * 32 + 65536) if proposal_path.exists() or proposal_path.is_symlink() else None
        return {**metadata, 'content': content, 'version': _hash(content), 'proposal': proposal,
                'updated_at': datetime.fromtimestamp((folder / 'draft.md').stat().st_mtime, timezone.utc).isoformat(),
                'scope': self.scope}

    def read(self, draft_id):
        folder = self._folder(draft_id)
        with self._locked(folder):
            return self._read(folder)

    def list(self, session_id=None):
        if session_id is not None and (not isinstance(session_id, str) or len(session_id) > 256):
            raise Invalid('Invalid session ID.')
        results = []
        for path in self.drafts.iterdir():
            if not _ID.fullmatch(path.name):
                continue
            draft = self.read(path.name)
            if session_id is None or draft['session_id'] == session_id:
                results.append({key: draft[key] for key in ['id', 'title', 'session_id', 'version', 'created_at', 'updated_at']})
        return sorted(results, key=lambda value: value['updated_at'], reverse=True)

    @staticmethod
    def _check_version(draft, expected):
        _version(expected)
        if draft['version'] != expected:
            raise Conflict('This draft changed elsewhere. Your text has not been overwritten; reload or copy it before reconciling.')

    def _commit(self, folder, draft, content):
        if draft['content'] == content:
            return
        revisions = self._directory(folder / 'revisions', create=True)
        revision = revisions / (str(time.time_ns()) + '-' + draft['version'] + '.md')
        self._atomic(revision, draft['content'])
        self._atomic(folder / 'draft.md', content)

    def save(self, draft_id, content, expected_version):
        content = self._content(content)
        folder = self._folder(draft_id)
        with self._locked(folder):
            draft = self._read(folder)
            self._check_version(draft, expected_version)
            self._commit(folder, draft, content)
            return self._read(folder)

    def propose(self, draft_id, *, expected_version, start, end, original, replacement, explanation=''):
        replacement = self._content(replacement)
        if not isinstance(original, str) or not isinstance(explanation, str) or len(explanation) > 2000:
            raise Invalid('Original text and a short explanation must be strings.')
        if type(start) is not int or type(end) is not int or start < 0 or end <= start:
            raise Invalid('Select a non-empty range using Unicode code-point indices.')
        folder = self._folder(draft_id)
        with self._locked(folder):
            draft = self._read(folder)
            self._check_version(draft, expected_version)
            if end > len(draft['content']):
                raise Invalid('Selected range is outside the draft.')
            if draft['content'][start:end] != original:
                raise Conflict('The selected text no longer matches the draft. Select it again.')
            new_content = self._content(draft['content'][:start] + replacement + draft['content'][end:])
            pending = draft['proposal']
            if pending and pending['status'] == 'pending':
                signature = ('base_version', 'start', 'end', 'original', 'replacement')
                values = dict(base_version=expected_version, start=start, end=end, original=original, replacement=replacement)
                if all(pending.get(k) == values[k] for k in signature):
                    return draft
                raise Conflict('Review or reject the pending suggestion before requesting another.')
            proposal = {'id': uuid.uuid4().hex, 'base_version': expected_version,
                        'start': start, 'end': end, 'original': original, 'replacement': replacement,
                        'explanation': explanation, 'status': 'pending', 'created_at': _now(),
                        'result_version': _hash(new_content),
                        'diff': _review_diff(original, replacement)}
            self._write_json(folder / 'proposal.json', proposal)
            return self._read(folder)

    @staticmethod
    def _proposal(draft, proposal_id):
        _identifier(proposal_id)
        proposal = draft['proposal']
        if not proposal or proposal.get('id') != proposal_id:
            raise Missing('Suggestion not found.')
        return proposal

    def accept(self, draft_id, proposal_id, expected_version):
        _version(expected_version)
        folder = self._folder(draft_id)
        with self._locked(folder):
            draft = self._read(folder)
            proposal = self._proposal(draft, proposal_id)
            if proposal['status'] == 'rejected':
                raise Conflict('This suggestion was rejected. Request a new suggestion.')
            if proposal['status'] == 'accepted':
                return draft  # Transport retries must not reapply or create another revision.
            if draft['version'] == proposal['result_version']:
                # A crash after replacing Markdown but before marking the proposal is recoverable.
                proposal['status'] = 'accepted'
                self._write_json(folder / 'proposal.json', proposal)
                return self._read(folder)
            self._check_version(draft, expected_version)
            if proposal['base_version'] != draft['version']:
                raise Conflict('This suggestion is out of date. Your edits are safe; reject it and ask again.')
            if draft['content'][proposal['start']:proposal['end']] != proposal['original']:
                raise Conflict('Selected text changed. The suggestion was not applied.')
            content = draft['content'][:proposal['start']] + proposal['replacement'] + draft['content'][proposal['end']:]
            self._commit(folder, draft, self._content(content))
            proposal['status'] = 'accepted'
            self._write_json(folder / 'proposal.json', proposal)
            return self._read(folder)

    def reject(self, draft_id, proposal_id):
        folder = self._folder(draft_id)
        with self._locked(folder):
            draft = self._read(folder)
            proposal = self._proposal(draft, proposal_id)
            if proposal['status'] == 'accepted':
                raise Conflict('Already applied. The prior Markdown is retained in revisions.')
            proposal['status'] = 'rejected'
            self._write_json(folder / 'proposal.json', proposal)
            return self._read(folder)
