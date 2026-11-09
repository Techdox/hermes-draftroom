"""Fixture-only catalog schema tests. No fixture URL/SHA is claimed published."""
import json
import pytest
import yaml
from scripts.catalog_entry import entry_data, render_entry


def test_entry_matches_actual_registered_capabilities():
    data = entry_data('https://github.com/example/draftroom', 'a' * 40, 'example')
    assert data['name'] == 'draftroom' and data['title'] == 'Draftroom'
    assert data['repo'] == 'https://github.com/example/draftroom'
    assert data['sha'] == 'a' * 40 and data['version'] == '0.1.1'
    assert data['requires_hermes'] == '>=0.23.0'
    assert data['tier'] == 'community' and data['category'] == 'desktop'
    assert data['platforms'] == ['linux', 'macos']
    assert data['capabilities'] == {'provides_tools': ['blog_draft'], 'provides_hooks': [],
                                    'provides_middleware': [], 'requires_env': []}
    assert yaml.safe_load(render_entry(data)) == data


@pytest.mark.parametrize('sha', ['main', 'v0.1.1', 'abcdef0', '', 'a' * 39, 'a' * 41, 'A' * 40])
def test_invalid_source_pin_is_rejected_not_normalized(sha):
    with pytest.raises(ValueError):
        entry_data('https://github.com/example/draftroom', sha, 'example')


@pytest.mark.parametrize('repo', ['http://github.com/example/draftroom', 'git@github.com:example/draftroom',
    'https://user:password@github.com/example/draftroom', 'https://github.com/example/draftroom?token=fixture',
    'https://github.com/example/draftroom#main', 'https://github.com/example/draftroom/',
    'https://github.com/example/../draftroom', 'https://github.com/example/draftroom.git'])
def test_unsafe_or_noncanonical_repo_url_is_rejected(repo):
    with pytest.raises(ValueError):
        entry_data(repo, 'a' * 40, 'example')


@pytest.mark.parametrize('maintainer', ['', None, 'name with spaces', '../owner'])
def test_maintainer_must_be_explicit(maintainer):
    with pytest.raises(ValueError):
        entry_data('https://github.com/example/draftroom', 'a' * 40, maintainer)
