from __future__ import annotations

import hashlib
import http.server
from pathlib import Path


HOST = ""
PORT = 8001
SERVER_IP = "192.168.0.60"
SERVER_DIR = Path("./work/firmware_server")
FIRMWARE = SERVER_DIR / "fileA_firmware.bin"
HASH_FILE = SERVER_DIR / "fileA_firmware.bin.sha256"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_firmware() -> None:
    SERVER_DIR.mkdir(parents=True, exist_ok=True)
    FIRMWARE.write_bytes(
        b"HINT1 OTA firmware file A\n"
        b"version=1.0.0\n"
        b"content=123\n"
    )
    HASH_FILE.write_text(sha256_file(FIRMWARE), encoding="utf-8")


def main() -> None:
    prepare_firmware()

    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args,
        directory=str(SERVER_DIR),
        **kwargs,
    )
    server = http.server.HTTPServer((HOST, PORT), handler)

    print(f"firmware: http://{SERVER_IP}:{PORT}/{FIRMWARE.name}")
    print(f"sha256:   http://{SERVER_IP}:{PORT}/{HASH_FILE.name}")
    server.serve_forever()


if __name__ == "__main__":
    main()
