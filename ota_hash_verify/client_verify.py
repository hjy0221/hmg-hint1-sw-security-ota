from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path


SERVER_IP = "192.168.0.60"
PORT = 8001
BASE_URL = f"http://{SERVER_IP}:{PORT}"
FIRMWARE_NAME = "fileA_firmware.bin"
ROOT_DIR = Path(__file__).resolve().parents[1]
DEST_DIR = ROOT_DIR / "work" / "device"
DEST = DEST_DIR / FIRMWARE_NAME


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read()


def main() -> None:
    firmware_url = f"{BASE_URL}/{FIRMWARE_NAME}"
    hash_url = f"{firmware_url}.sha256"

    firmware = download(firmware_url)
    expected_hash = download(hash_url).decode("utf-8").strip()
    actual_hash = sha256_bytes(firmware)

    print("expected:", expected_hash)
    print("actual:  ", actual_hash)

    if actual_hash != expected_hash:
        print("result: hash mismatch")
        return

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(firmware)
    print("result: hash ok")
    print("saved:", DEST)


if __name__ == "__main__":
    main()
