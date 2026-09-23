from __future__ import annotations

import http.server
from pathlib import Path


HOST = ""
PORT = 8002
SERVER_IP = "localhost"
ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT_DIR / "work" / "chunked_ota_server"


def main() -> None:
    if not (SERVER_DIR / "manifest.json").exists():
        raise SystemExit("Run python .\\chunked_ota\\prepare_chunks.py first.")

    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args,
        directory=str(SERVER_DIR),
        **kwargs,
    )
    server = http.server.HTTPServer((HOST, PORT), handler)
    print(f"manifest: http://{SERVER_IP}:{PORT}/manifest.json")
    server.serve_forever()


if __name__ == "__main__":
    main()
