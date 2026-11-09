"""Prepare catalog metadata only after a clean local commit. Never publish it."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def entry_data(repo, sha, maintainer):
    if not isinstance(repo, str):
        raise ValueError('Supply the exact public GitHub repository homepage URL')
    parsed = urlsplit(repo)
    parts = parsed.path.split('/')
    if (parsed.scheme != 'https' or parsed.netloc != 'github.com' or parsed.query or parsed.fragment
        or len(parts) != 3 or any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value) for value in parts[1:])
        or any(value in {'.', '..'} for value in parts[1:]) or parts[-1].endswith('.git')):
        raise ValueError('Use an exact https://github.com/OWNER/REPOSITORY homepage URL, without credentials, .git, query, fragment or trailing slash. Input is never normalized.')
    if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Use the actual full lowercase 40-character Git commit SHA; no branches, tags or repaired pins')
    if not isinstance(maintainer, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', maintainer):
        raise ValueError('Supply the submitting maintainer GitHub handle explicitly')
    version = json.loads((ROOT / 'dashboard/manifest.json').read_text())['version']
    return {
        'name': 'draftroom', 'title': 'Draftroom', 'repo': repo, 'sha': sha,
        'description': 'A Markdown draft beside Hermes chat, with selected-text rewrites and explicit Accept/Reject review. Disclosure: stores drafts, suggestions and retained revisions only in this profile\'s plugin-data; draft content goes through the existing conversation/model; polls its own backend while open; no direct third-party requests, credentials, telemetry, shell commands, background service or self-update.',
        'maintainer': maintainer, 'tier': 'community', 'category': 'desktop',
        'requires_hermes': '>=0.23.0', 'version': version, 'docs_url': repo + '#readme',
        'platforms': ['linux', 'macos'],
        'known_issues': ['Requires both Agent and local Desktop components; Linux/macOS backend with a recent Desktop SDK.',
                         'Unsaved buffers are memory-only and do not survive plugin/window reload or quitting.'],
        'capabilities': {'provides_tools': ['blog_draft'], 'provides_hooks': [],
                         'provides_middleware': [], 'requires_env': []},
    }


def render_entry(data):
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(key + ':')
            lines.extend('  ' + k + ': ' + json.dumps(v, ensure_ascii=False) for k, v in value.items())
        else:
            lines.append(key + ': ' + json.dumps(value, ensure_ascii=False))
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--sha', required=True)
    parser.add_argument('--maintainer', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        data = entry_data(args.repo, args.sha, args.maintainer)
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
        status = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=ROOT, text=True, capture_output=True, check=True).stdout
        if head != args.sha or status:
            raise ValueError('Commit the complete reviewed source first; SHA must equal HEAD and the worktree/index must be clean')
        text = render_entry(data)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8') as stream:
                stream.write(text)
        else:
            print(text, end='')
    except (ValueError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
