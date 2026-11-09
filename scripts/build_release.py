"""Build a source-only runtime ZIP. No network, installs, Git writes or overwrites."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = (
    'plugin.yaml', '__init__.py', 'draftroom_store.py', 'README.md', 'INSTALL.md',
    'API.md', 'LICENSE', 'CHANGELOG.md', 'KNOWN_ISSUES.md', 'VERIFICATION.md',
    'desktop/plugin.js', 'desktop/README.md', 'dashboard/manifest.json',
    'dashboard/plugin_api.py', 'skills/blog/SKILL.md',
)


def _version(root):
    manifest = (root / 'plugin.yaml').read_text(encoding='utf-8')
    match = re.search(r'^version: [\"\x27]?([0-9]+\.[0-9]+\.[0-9]+)[\"\x27]?\s*$', manifest, re.M)
    if not match:
        raise ValueError('plugin.yaml needs a release SemVer version')
    version = match.group(1)
    dashboard = json.loads((root / 'dashboard/manifest.json').read_text())
    if dashboard.get('name') != 'draftroom' or dashboard.get('version') != version:
        raise ValueError('Dashboard and Agent versions/identities disagree')
    skill = (root / 'skills/blog/SKILL.md').read_text(encoding='utf-8')
    if not re.search(r'^version: ' + re.escape(version) + r'\s*$', skill, re.M):
        raise ValueError('Bundled skill version disagrees with Agent version')
    return version


def build_release(root=ROOT, output=None):
    root = Path(root).resolve()
    output = Path(output) if output is not None else root / 'dist'
    if output.is_symlink():
        raise ValueError('Output must not be a symlink')
    output = output.resolve()
    source = {}
    for name in RUNTIME_FILES:
        path = root / name
        if not path.is_file() or path.is_symlink() or path.resolve() != path:
            raise ValueError('Missing, non-regular or linked runtime file: ' + name)
        source[name] = path.read_bytes()
    version = _version(root)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'draftroom-{version}.zip'
    checksums = output / f'draftroom-{version}.SHA256SUMS'
    if archive.exists() or checksums.exists():
        raise FileExistsError('A versioned artifact exists; do not overwrite it. Use a fresh output directory or a new version.')
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(source):
            item = zipfile.ZipInfo('draftroom/' + name, date_time=(1980, 1, 1, 0, 0, 0))
            item.create_system = 3
            item.external_attr = (stat.S_IFREG | 0o644) << 16
            item.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(item, source[name], compresslevel=9)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or set(z.namelist()) != {'draftroom/' + name for name in source}:
            raise ValueError('ZIP membership or CRC verification failed')
        if any(z.read('draftroom/' + name) != value for name, value in source.items()):
            raise ValueError('ZIP bytes do not match the reviewed source')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    rows = [digest + '  ' + archive.name]
    rows += [hashlib.sha256(source[name]).hexdigest() + '  draftroom/' + name for name in sorted(source)]
    with checksums.open('x', encoding='utf-8') as stream:
        stream.write('\n'.join(rows) + '\n')
    return {'archive': str(archive), 'checksums': str(checksums), 'sha256': digest,
            'version': version, 'files': len(source), 'bytes': archive.stat().st_size,
            'crc_and_source_bytes_verified': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(build_release(output=args.output_dir), indent=2))


if __name__ == '__main__':
    main()
