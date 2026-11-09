"""The loaded API reports its packaged version for honest activation checks."""
from pathlib import Path
import importlib.util
import json
import shutil
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


def test_status_reports_the_imported_package_version(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('draftroom_status_version_test', ROOT / 'dashboard/plugin_api.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    store = module._core.DraftStore(tmp_path / 'data')
    monkeypatch.setattr(module, 'get_store', lambda: store)
    app = FastAPI()
    app.include_router(module.router, prefix='/api/plugins/draftroom')
    with TestClient(app) as client:
        response = client.get('/api/plugins/draftroom/status')
        assert response.status_code == 200
        body = response.json()
        expected = json.loads((ROOT / 'dashboard/manifest.json').read_text())['version']
        assert body['version'] == expected == '0.1.2'
        assert body['name'] == 'draftroom' and body['scope'] == store.scope
        assert body['max_content_bytes'] == store.MAX_CONTENT_BYTES


def test_replacing_manifest_does_not_make_an_old_router_claim_new_activation(tmp_path, monkeypatch):
    package = tmp_path / 'package'
    (package / 'dashboard').mkdir(parents=True)
    for name in ('dashboard/plugin_api.py', 'dashboard/manifest.json', 'draftroom_store.py'):
        shutil.copy2(ROOT / name, package / name)
    spec = importlib.util.spec_from_file_location('draftroom_loaded_version_test', package / 'dashboard/plugin_api.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    store = module._core.DraftStore(tmp_path / 'data')
    monkeypatch.setattr(module, 'get_store', lambda: store)
    manifest = package / 'dashboard/manifest.json'
    replacement = json.loads(manifest.read_text())
    replacement['version'] = '0.9.9'
    manifest.write_text(json.dumps(replacement))
    app = FastAPI()
    app.include_router(module.router)
    with TestClient(app) as client:
        assert client.get('/status').json()['version'] == '0.1.2'
