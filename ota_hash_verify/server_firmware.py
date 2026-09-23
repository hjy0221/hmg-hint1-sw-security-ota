from __future__ import annotations

import hashlib
import http.server
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util.Padding import pad


HOST = ""
PORT = 8001
SERVER_IP = "192.168.0.60"
ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT_DIR / "work" / "firmware_server"
PLAINTEXT_FIRMWARE = SERVER_DIR / "fileA_firmware.bin"
ENCRYPTED_FIRMWARE = SERVER_DIR / "fileA_firmware.bin.enc"
HASH_FILE = SERVER_DIR / "fileA_firmware.bin.enc.sha256"
SIGNATURE_FILE = SERVER_DIR / "fileA_firmware.bin.enc.sig"
PUBLIC_KEY_FILE = SERVER_DIR / "public_key.pem"
PRIVATE_KEY_FILE = SERVER_DIR / "private_key.pem"

AES_KEY = bytes.fromhex(
    "00112233445566778899aabbccddeeff"
    "00112233445566778899aabbccddeeff"
)
AES_IV = bytes(16)


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def load_or_create_private_key() -> RSA.RsaKey:
    if PRIVATE_KEY_FILE.exists():
        return RSA.import_key(PRIVATE_KEY_FILE.read_bytes())

    private_key = RSA.generate(2048)
    PRIVATE_KEY_FILE.write_bytes(private_key.export_key("PEM"))
    PUBLIC_KEY_FILE.write_bytes(private_key.public_key().export_key("PEM"))
    return private_key


def encrypt_firmware(plaintext: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(plaintext, AES.block_size))


def prepare_firmware() -> None:
    SERVER_DIR.mkdir(parents=True, exist_ok=True)
    private_key = load_or_create_private_key()

    plaintext = (
        b"HINT1 OTA firmware file A\n"
        b"version=1.0.0\n"
        b"content=123\n"
    )
    ciphertext = encrypt_firmware(plaintext)
    digest = sha256_bytes(ciphertext)
    signature = pkcs1_15.new(private_key).sign(SHA256.new(ciphertext))

    PLAINTEXT_FIRMWARE.write_bytes(plaintext)
    ENCRYPTED_FIRMWARE.write_bytes(ciphertext)
    HASH_FILE.write_text(digest.hex(), encoding="utf-8")
    SIGNATURE_FILE.write_bytes(signature)


def main() -> None:
    prepare_firmware()

    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args,
        directory=str(SERVER_DIR),
        **kwargs,
    )
    server = http.server.HTTPServer((HOST, PORT), handler)

    print(f"firmware: http://{SERVER_IP}:{PORT}/{ENCRYPTED_FIRMWARE.name}")
    print(f"sha256:   http://{SERVER_IP}:{PORT}/{HASH_FILE.name}")
    print(f"sig:      http://{SERVER_IP}:{PORT}/{SIGNATURE_FILE.name}")
    print(f"pubkey:   http://{SERVER_IP}:{PORT}/{PUBLIC_KEY_FILE.name}")
    server.serve_forever()


if __name__ == "__main__":
    main()
