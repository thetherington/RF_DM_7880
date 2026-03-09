#!/usr/bin/env python3
"""Simple HTTP simulator for frame/card dump responses.

Maps request paths to files in a dump directory where:
- filenames begin with "<ip>_"
- remaining filename uses underscores instead of path separators

Example:
  file: 172.16.185.22_slot_8_htdocs_cgi-bin_cfgjsonrpc
  path: /slot/8/htdocs/cgi-bin/cfgjsonrpc
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict
from urllib.parse import urlsplit


def build_route_map(dump_dir: Path, ip: str) -> Dict[str, Path]:
    """Build route-to-file mapping for a selected IP."""
    prefix = f"{ip}_"
    routes: Dict[str, Path] = {}

    if not dump_dir.exists() or not dump_dir.is_dir():
        raise FileNotFoundError(f"Dump directory not found: {dump_dir}")

    for file_path in dump_dir.iterdir():
        if not file_path.is_file() or not file_path.name.startswith(prefix):
            continue

        route_part = file_path.name[len(prefix) :]
        route = "/" + route_part.replace("_", "/")
        routes[route] = file_path

    return routes


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Serve dump files as HTTP endpoints for a selected frame IP"
    )
    parser.add_argument("--ip", required=True, help="IP prefix used in dump filenames")
    parser.add_argument(
        "--dump-dir",
        default="dump",
        help="Directory containing dump files (default: extra/dump)",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Listen address (default: 0.0.0.0)"
    )
    parser.add_argument("--port", type=int, default=8080, help="Listen port")
    return parser.parse_args()


def create_handler(routes: Dict[str, Path]):
    """Create a request handler bound to route mappings."""

    class SimulatorHandler(BaseHTTPRequestHandler):
        server_version = "DumpSimulator/1.0"

        def do_GET(self) -> None:  # pylint: disable=invalid-name
            self._serve_mapped_file()

        def do_POST(self) -> None:  # pylint: disable=invalid-name
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 0:
                self.rfile.read(content_length)
            self._serve_mapped_file()

        def _serve_mapped_file(self) -> None:
            path = urlsplit(self.path).path
            file_path = routes.get(path)

            if file_path is None:
                self.send_error(404, f"No dump file mapped for path: {path}")
                return

            body = file_path.read_bytes()
            content_type = "application/json"
            if file_path.suffix and file_path.suffix != ".json":
                content_type = "text/plain; charset=utf-8"

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return SimulatorHandler


def main() -> None:
    """Run simulator HTTP server."""
    args = parse_args()
    dump_dir = Path(args.dump_dir).resolve()

    routes = build_route_map(dump_dir=dump_dir, ip=args.ip)
    if not routes:
        raise SystemExit(
            f"No files found for IP '{args.ip}' in {dump_dir}. "
            "Expected files named like '<ip>_slot_8_...'."
        )

    print(f"Loaded {len(routes)} route(s) for IP {args.ip} from {dump_dir}")
    print("Available routes:")
    for route in sorted(routes):
        print(f"  {route}")

    handler_cls = create_handler(routes)
    server = ThreadingHTTPServer((args.host, args.port), handler_cls)

    print(f"Serving on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down simulator...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
