"""Local HTTP server for the visualizer (standard library only).

Routes (GET only):
    /                     the viewer page
    /static/<file>        viewer assets, from a fixed allowlist
    /api/presets          available configurations and the default
    /api/config?preset=   one configuration with lane geometry
    /api/isa/pe           PE instruction format and what each instruction does
    /api/starter          map of the starter code, read live (progress, Python idioms)
    /api/traces           names of traces in the traces folder
    /api/traces/<name>    one validated trace plus its configuration

Every value the viewer shows comes from these routes. The frontend formats and
draws; it does not compute.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

from viz.configs import DEFAULT_PRESET, UnknownPresetError, preset_config, preset_list
from viz.isa import pe_isa
from viz.starter import starter_map
from viz.schema import TraceError, load_trace

log = logging.getLogger("viz.server")

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_FILES = {
    "app.js": "text/javascript; charset=utf-8",
    "style.css": "text/css; charset=utf-8",
}
TRACE_NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}")
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


class ApiError(Exception):
    """An error with an HTTP status and a message safe to show the client."""

    def __init__(self, status: HTTPStatus, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


class VizServer(ThreadingHTTPServer):
    """HTTP server that knows where the traces live."""

    daemon_threads = True

    def __init__(self, address: tuple[str, int], traces_dir: Path) -> None:
        super().__init__(address, Handler)
        self.traces_dir = traces_dir


class Handler(BaseHTTPRequestHandler):
    """Routes GET requests; every other method gets 405."""

    server: VizServer
    server_version = "ee271-viz"
    sys_version = ""

    # ------------------------------------------------------------ dispatch

    def do_GET(self) -> None:  # noqa: N802 (name fixed by http.server)
        url = urlsplit(self.path)
        try:
            if url.path in ("/", "/index.html"):
                self._send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            elif url.path.startswith("/static/"):
                self._static(url.path.removeprefix("/static/"))
            elif url.path == "/api/presets":
                self._json({"default": DEFAULT_PRESET, "presets": preset_list()})
            elif url.path == "/api/config":
                self._json(self._config(parse_qs(url.query)))
            elif url.path == "/api/isa/pe":
                self._json(pe_isa())
            elif url.path == "/api/starter":
                self._json(starter_map())
            elif url.path == "/api/traces":
                self._json({"traces": self._trace_names()})
            elif url.path.startswith("/api/traces/"):
                self._json(self._trace(url.path.removeprefix("/api/traces/")))
            else:
                raise ApiError(HTTPStatus.NOT_FOUND, "no such route")
        except ApiError as err:
            self._json({"error": err.message}, err.status)
        except Exception:
            log.exception("unhandled error serving %s", self.path)
            self._json({"error": "internal server error (see server log)"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _method_not_allowed(self) -> None:
        self._json({"error": "only GET is supported"}, HTTPStatus.METHOD_NOT_ALLOWED, {"Allow": "GET"})

    do_POST = do_PUT = do_PATCH = do_DELETE = _method_not_allowed  # noqa: N815

    # -------------------------------------------------------------- routes

    def _static(self, name: str) -> None:
        if name not in STATIC_FILES:
            raise ApiError(HTTPStatus.NOT_FOUND, "no such file")
        self._send_file(STATIC_DIR / name, STATIC_FILES[name])

    @staticmethod
    def _config(query: dict[str, list[str]]) -> dict[str, Any]:
        name = query.get("preset", [DEFAULT_PRESET])[0]
        try:
            return preset_config(name)
        except UnknownPresetError:
            raise ApiError(HTTPStatus.BAD_REQUEST, "unknown preset (see /api/presets)") from None

    def _trace_names(self) -> list[str]:
        return sorted(
            p.stem for p in self.server.traces_dir.glob("*.json") if TRACE_NAME.fullmatch(p.stem)
        )

    def _trace(self, name: str) -> dict[str, Any]:
        if not TRACE_NAME.fullmatch(name):
            raise ApiError(HTTPStatus.BAD_REQUEST, "trace names are lowercase letters, digits, - and _")
        path = self.server.traces_dir / f"{name}.json"
        if not path.is_file():
            raise ApiError(HTTPStatus.NOT_FOUND, "no such trace")
        try:
            trace = load_trace(path)
        except TraceError as err:
            raise ApiError(HTTPStatus.UNPROCESSABLE_ENTITY, f"invalid trace: {err}") from err
        return {"trace": trace, "config": preset_config(trace["preset"])}

    # ------------------------------------------------------------ responses

    def _send(self, body: bytes, content_type: str, status: HTTPStatus, extra: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in {**SECURITY_HEADERS, **(extra or {})}.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data: Any, status: HTTPStatus = HTTPStatus.OK, extra: dict[str, str] | None = None) -> None:
        self._send(json.dumps(data).encode("utf-8"), "application/json", status, extra)

    def _send_file(self, path: Path, content_type: str) -> None:
        self._send(path.read_bytes(), content_type, HTTPStatus.OK)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 (signature fixed by http.server)
        log.info("%s %s", self.address_string(), format % args)


def make_server(host: str, port: int, traces_dir: Path = REPO_ROOT / "traces") -> VizServer:
    """Create (but do not start) the server. ``port=0`` picks a free port."""
    return VizServer((host, port), traces_dir)


def main() -> None:
    """Command-line entry point: ``python -m viz.server [--host H] [--port P]``."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    server = make_server(args.host, args.port)
    log.info("serving on %s:%d (open http://127.0.0.1:%d on the host)", args.host, args.port, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
