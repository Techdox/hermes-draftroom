"""Release ZIPs are source-only, allowlisted and independently verifiable."""
from pathlib import Path
import hashlib
import json
import zipfile

import pytest
from scripts.build_release import build_release

ROOT = Path(__file__).resolve().parents[1]
# Deliberate second declaration: changing the product allowlist needs review here too.
EXPECTED = {'plugin.yaml', '__init__.py', 'draftroom_store.py', 'README.md', 'INSTALL.md',
            'API.md', 'LICENSE', 'CHANGELOG.md', 'KNOWN_ISSUES.md', 'VERIFICATION.md',
            'desktop/plugin.js', 'desktop/README.md', 'dashboard/manifest.json',
            'dashboard/plugin_api.py', 'skills/blog/SKILL.md'}


def source(tmp_path):
    root = tmp_path / 'source'
    for name in EXPECTED:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    return root


def test_package_is_exact_and_excludes_untracked_private_material(tmp_path):
    root = source(tmp_path)
    (root / '.env').write_text('NOT_A_REAL_SECRET=fixture-only')
    (root / 'private-draft.md').write_text('Fixture must not ship')
    result = build_release(root, tmp_path / 'out')
    archive, checksums = Path(result['archive']), Path(result['checksums'])
    assert archive.name == 'draftroom-0.1.1.zip'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {'draftroom/' + name for name in EXPECTED}
        assert all(z.read('draftroom/' + name) == (root / name).read_bytes() for name in EXPECTED)
        assert all((row.external_attr >> 16) & 0o170000 == 0o100000 for row in z.infolist())
    rows = [line.split('  ', 1) for line in checksums.read_text().splitlines()]
    assert rows[0] == [hashlib.sha256(archive.read_bytes()).hexdigest(), archive.name]
    assert len(rows) == len(EXPECTED) + 1


def test_identical_sources_produce_identical_zip_bytes(tmp_path):
    root = source(tmp_path)
    a = build_release(root, tmp_path / 'a')
    b = build_release(root, tmp_path / 'b')
    assert Path(a['archive']).read_bytes() == Path(b['archive']).read_bytes()


def test_missing_runtime_file_aborts_before_output(tmp_path):
    root = source(tmp_path)
    (root / 'draftroom_store.py').unlink()
    with pytest.raises(ValueError):
        build_release(root, tmp_path / 'out')
    assert not list((tmp_path / 'out').glob('*.zip'))


def test_symlinked_runtime_file_is_refused(tmp_path):
    root = source(tmp_path)
    original = root / 'draftroom_store.py'
    outside = tmp_path / 'outside.py'
    outside.write_text(original.read_text())
    original.unlink()
    original.symlink_to(outside)
    with pytest.raises(ValueError):
        build_release(root, tmp_path / 'out')


def test_existing_artifact_is_never_overwritten(tmp_path):
    root = source(tmp_path)
    result = build_release(root, tmp_path / 'out')
    old = Path(result['archive']).read_bytes()
    with pytest.raises(FileExistsError):
        build_release(root, tmp_path / 'out')
    assert Path(result['archive']).read_bytes() == old


def test_conflicting_versions_are_refused(tmp_path):
    root = source(tmp_path)
    path = root / 'dashboard/manifest.json'
    data = json.loads(path.read_text());data['version'] = '0.9.9';path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        build_release(root, tmp_path / 'out')
