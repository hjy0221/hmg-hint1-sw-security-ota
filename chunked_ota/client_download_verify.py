from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


BASE_URL = "http://localhost:8002"
ROOT_DIR = Path(__file__).resolve().parents[1]
DEVICE_DIR = ROOT_DIR / "work" / "chunked_ota_device"
DOWNLOAD_DIR = DEVICE_DIR / "chunks"
MERGED_FILE = DEVICE_DIR / "merged_100MiB.bin"
SOURCE_FILE = ROOT_DIR / "work" / "chunked_ota" / "source_100MiB.bin"


def download(path_or_url: str) -> bytes:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        url = path_or_url
    else:
        url = f"{BASE_URL}/{path_or_url}"

    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hash_signature(public_key: RSA.RsaKey, sha256_hex: str, signature: bytes) -> None:
    digest = SHA256.new(sha256_hex.encode("ascii"))
    pkcs1_15.new(public_key).verify(digest, signature)


def main() -> None:
    manifest = json.loads(download("manifest.json").decode("utf-8"))
    public_key = RSA.import_key(download(manifest["public_key"]))

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if MERGED_FILE.exists():
        MERGED_FILE.unlink()

    with MERGED_FILE.open("ab") as merged:
        for chunk in manifest["chunks"]:
            data = download(chunk["file"])
            expected_hash = download(chunk["sha256"]).decode("ascii").strip()
            signature = download(chunk["signature"])
            actual_hash = sha256_bytes(data)

            verify_hash_signature(public_key, expected_hash, signature)
            if actual_hash != expected_hash:
                raise ValueError(f"chunk {chunk['index']} hash mismatch")

            chunk_path = DOWNLOAD_DIR / Path(chunk["file"]).name
            chunk_path.write_bytes(data)
            merged.write(data)
            print(f"chunk {chunk['index']:04d}: signature ok, hash ok")

    merged_hash = sha256_file(MERGED_FILE)
    print("expected merged sha256:", manifest["source_sha256"])
    print("actual merged sha256:  ", merged_hash)

    if merged_hash != manifest["source_sha256"]:
        raise ValueError("merged file hash mismatch")

    if SOURCE_FILE.exists() and sha256_file(SOURCE_FILE) == merged_hash:
        print("source compare: identical")
    else:
        print("source compare: source file not found or hash differs")

    print("result: all chunks verified and merged")
    print("saved:", MERGED_FILE)


if __name__ == "__main__":
    main()
