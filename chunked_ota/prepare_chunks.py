from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT_DIR / "work" / "chunked_ota" / "source_100MiB.bin"
SERVER_DIR = ROOT_DIR / "work" / "chunked_ota_server"
CHUNK_DIR = SERVER_DIR / "chunks"
PRIVATE_KEY_FILE = ROOT_DIR / "work" / "firmware_server" / "private_key.pem"
PUBLIC_KEY_FILE = SERVER_DIR / "public_key.pem"
TLS_CERT_FILE = SERVER_DIR / "server_cert.pem"
MANIFEST_FILE = SERVER_DIR / "manifest.json"

FILE_SIZE = 100 * 1024 * 1024
CHUNK_SIZE = 1 * 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_or_create_private_key() -> RSA.RsaKey:
    PRIVATE_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if PRIVATE_KEY_FILE.exists():
        return RSA.import_key(PRIVATE_KEY_FILE.read_bytes())

    private_key = RSA.generate(2048)
    PRIVATE_KEY_FILE.write_bytes(private_key.export_key("PEM"))
    return private_key


def create_tls_certificate() -> None:
    if TLS_CERT_FILE.exists():
        return

    subprocess.run(
        [
            "openssl",
            "req",
            "-new",
            "-x509",
            "-key",
            str(PRIVATE_KEY_FILE),
            "-out",
            str(TLS_CERT_FILE),
            "-days",
            "365",
            "-subj",
            "/CN=localhost",
            "-addext",
            "subjectAltName=DNS:localhost,IP:127.0.0.1",
        ],
        check=True,
    )


def create_source_file() -> None:
    SOURCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if SOURCE_FILE.exists() and SOURCE_FILE.stat().st_size == FILE_SIZE:
        return

    block = bytes(range(256)) * 4096
    remaining = FILE_SIZE
    with SOURCE_FILE.open("wb") as file:
        while remaining:
            data = block[: min(len(block), remaining)]
            file.write(data)
            remaining -= len(data)


def sign_sha256_hex(private_key: RSA.RsaKey, sha256_hex: str) -> bytes:
    digest = SHA256.new(sha256_hex.encode("ascii"))
    return pkcs1_15.new(private_key).sign(digest)


def split_and_sign() -> None:
    private_key = load_or_create_private_key()
    SERVER_DIR.mkdir(parents=True, exist_ok=True)
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_KEY_FILE.write_bytes(private_key.public_key().export_key("PEM"))
    create_tls_certificate()

    chunks = []
    with SOURCE_FILE.open("rb") as source:
        index = 0
        while True:
            data = source.read(CHUNK_SIZE)
            if not data:
                break

            name = f"chunk_{index:04d}.bin"
            chunk_path = CHUNK_DIR / name
            hash_path = CHUNK_DIR / f"{name}.sha256"
            sig_path = CHUNK_DIR / f"{name}.sha256.sig"
            sha256_hex = sha256_bytes(data)

            chunk_path.write_bytes(data)
            hash_path.write_text(sha256_hex, encoding="ascii")
            sig_path.write_bytes(sign_sha256_hex(private_key, sha256_hex))

            chunks.append(
                {
                    "index": index,
                    "file": f"chunks/{name}",
                    "sha256": f"chunks/{name}.sha256",
                    "signature": f"chunks/{name}.sha256.sig",
                    "size": len(data),
                }
            )
            index += 1

    manifest = {
        "source_file": SOURCE_FILE.name,
        "file_size": SOURCE_FILE.stat().st_size,
        "chunk_size": CHUNK_SIZE,
        "chunk_count": len(chunks),
        "source_sha256": sha256_file(SOURCE_FILE),
        "public_key": "public_key.pem",
        "tls_certificate": "server_cert.pem",
        "chunks": chunks,
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    create_source_file()
    split_and_sign()
    print("source:", SOURCE_FILE)
    print("server:", SERVER_DIR)
    print("manifest:", MANIFEST_FILE)
    print("tls_cert:", TLS_CERT_FILE)
    print("source_sha256:", sha256_file(SOURCE_FILE))


if __name__ == "__main__":
    main()
