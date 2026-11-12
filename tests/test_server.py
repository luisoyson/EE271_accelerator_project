"""HTTP API: routes, input validation at the boundary, and error codes."""

import json
import shutil
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from viz.server import make_server

SAMPLE = Path(__file__).resolve().parent.parent / "traces" / "sample.json"


@pytest.fixture
def base_url(tmp_path: Path) -> Iterator[str]:
    traces = tmp_path / "traces"
    traces.mkdir()
    shutil.copy(SAMPLE, traces / "sample.json")
    (traces / "broken.json").write_text(json.dumps({**json.loads(SAMPLE.read_text()), "schema_version": 9}))
    server = make_server("127.0.0.1", 0, traces_dir=traces)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def get(url: str, method: str = "GET") -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as err:
        return err.code, dict(err.headers), err.read()


def get_json(url: str) -> tuple[int, Any]:
    status, _headers, body = get(url)
    return status, json.loads(body)


def test_index_is_served(base_url: str) -> None:
    status, headers, body = get(base_url + "/")
    assert status == 200
    assert headers["Content-Type"].startswith("text/html")
    assert b"app.js" in body


def test_static_allowlist(base_url: str) -> None:
    assert get(base_url + "/static/app.js")[0] == 200
    assert get(base_url + "/static/style.css")[0] == 200
    assert get(base_url + "/static/../schema.py")[0] == 404
    assert get(base_url + "/static/server.py")[0] == 404


def test_security_headers(base_url: str) -> None:
    _status, headers, _body = get(base_url + "/api/presets")
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "default-src 'self'" in headers["Content-Security-Policy"]


def test_presets(base_url: str) -> None:
    status, body = get_json(base_url + "/api/presets")
    assert status == 200
    assert body["default"] == "demo-4pe"
    assert {p["name"] for p in body["presets"]} >= {"demo-4pe", "test-int8-9pe"}


def test_config_default_and_named(base_url: str) -> None:
    assert get_json(base_url + "/api/config")[1]["pe_count"] == 4
    status, body = get_json(base_url + "/api/config?preset=test-int8-9pe")
    assert status == 200
    assert body["pe_count"] == 9
    assert body["modes"]["8"]["acc_lane_bits"] == 16


def test_config_unknown_preset_is_400(base_url: str) -> None:
    status, body = get_json(base_url + "/api/config?preset=evil")
    assert status == 400
    assert "preset" in body["error"]


def test_trace_list(base_url: str) -> None:
    assert get_json(base_url + "/api/traces") == (200, {"traces": ["broken", "sample"]})


def test_trace_valid(base_url: str) -> None:
    status, body = get_json(base_url + "/api/traces/sample")
    assert status == 200
    assert body["trace"]["synthetic"] is True
    assert body["config"]["pe_count"] == 4


def test_trace_invalid_is_422_with_reason(base_url: str) -> None:
    status, body = get_json(base_url + "/api/traces/broken")
    assert status == 422
    assert "schema_version" in body["error"]


def test_trace_missing_is_404(base_url: str) -> None:
    assert get_json(base_url + "/api/traces/nope")[0] == 404


@pytest.mark.parametrize("name", ["..%2Fetc", "UPPER", "a.json", "x" * 65])
def test_trace_bad_name_is_400(base_url: str, name: str) -> None:
    assert get_json(base_url + f"/api/traces/{name}")[0] == 400


def test_isa_pe(base_url: str) -> None:
    status, body = get_json(base_url + "/api/isa/pe")
    assert status == 200
    assert {op["name"] for op in body["ops"]} == {"MAC", "NOP", "OUT", "PASS", "CLR", "RND"}


def test_unknown_route_is_404(base_url: str) -> None:
    assert get_json(base_url + "/api/nothing")[0] == 404


def test_post_not_allowed(base_url: str) -> None:
    assert get(base_url + "/api/presets", method="POST")[0] == 405
