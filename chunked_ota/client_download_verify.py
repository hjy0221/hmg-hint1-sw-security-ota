from __future__ import annotations

import hashlib
import json
import socket
import ssl
from pathlib import Path

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


HOST = "localhost"
PORT = 8002
ROOT_DIR = Path(__file__).resolve().parents[1]
DEVICE_DIR = ROOT_DIR / "work" / "chunked_ota_device"
DOWNLOAD_DIR = DEVICE_DIR / "chunks"
MERGED_FILE = DEVICE_DIR / "merged_100MiB.bin"
SOURCE_FILE = ROOT_DIR / "work" / "chunked_ota" / "source_100MiB.bin"
TLS_CERT_FILE = ROOT_DIR / "work" / "chunked_ota_server" / "server_cert.pem"


class TlsChunkClient:
    def __init__(self, host: str, port: int, cafile: Path) -> None:
        context = ssl.create_default_context(cafile=str(cafile))
        raw_socket = socket.create_connection((host, port), timeout=30)
        self.conn = context.wrap_socket(raw_socket, server_hostname="localhost")
        self.reader = self.conn.makefile("rb")

    def close(self) -> None:
        try:
            self.conn.sendall(b"QUIT\n")
        finally:
            self.reader.close()
            self.conn.close()

    def download(self, path: str) -> bytes:
        self.conn.sendall(f"{path}\n".encode("utf-8"))
        status = self.reader.readline().decode("utf-8").strip()

        if not status.startswith("OK "):
            raise RuntimeError(status)

        size = int(status.split(" ", 1)[1])
        data = self.reader.read(size)
        if len(data) != size:
            raise RuntimeError(f"incomplete download for {path}")
        return data

    def __enter__(self) -> "TlsChunkClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


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
    if not TLS_CERT_FILE.exists():
        raise SystemExit("TLS certificate is missing. Run prepare_chunks.py first.")

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if MERGED_FILE.exists():
        MERGED_FILE.unlink()

    with TlsChunkClient(HOST, PORT, TLS_CERT_FILE) as client:
        manifest = json.loads(client.download("manifest.json").decode("utf-8"))
        public_key = RSA.import_key(client.download(manifest["public_key"]))

        with MERGED_FILE.open("ab") as merged:
            for chunk in manifest["chunks"]:
                data = client.download(chunk["file"])
                expected_hash = client.download(chunk["sha256"]).decode("ascii").strip()
                signature = client.download(chunk["signature"])
                actual_hash = sha256_bytes(data)

                verify_hash_signature(public_key, expected_hash, signature)
                if actual_hash != expected_hash:
                    raise ValueError(f"chunk {chunk['index']} hash mismatch")

                chunk_path = DOWNLOAD_DIR / Path(chunk["file"]).name
                chunk_path.write_bytes(data)
                merged.write(data)
                print(f"chunk {chunk['index']:04d}: tls ok, signature ok, hash ok")

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
