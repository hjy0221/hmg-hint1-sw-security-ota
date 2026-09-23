from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util.Padding import unpad


SERVER_IP = "192.168.0.60"
PORT = 8001
BASE_URL = f"http://{SERVER_IP}:{PORT}"
FIRMWARE_NAME = "fileA_firmware.bin.enc"
ROOT_DIR = Path(__file__).resolve().parents[1]
DEST_DIR = ROOT_DIR / "work" / "device"
DEST_ENCRYPTED = DEST_DIR / FIRMWARE_NAME
DEST_DECRYPTED = DEST_DIR / "fileA_firmware.bin"

AES_KEY = bytes.fromhex(
    "00112233445566778899aabbccddeeff"
    "00112233445566778899aabbccddeeff"
)
AES_IV = bytes(16)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read()


def verify_signature(public_key_pem: bytes, data: bytes, signature: bytes) -> bool:
    public_key = RSA.import_key(public_key_pem)
    digest = SHA256.new(data)

    try:
        pkcs1_15.new(public_key).verify(digest, signature)
    except (ValueError, TypeError):
        return False
    return True


def decrypt_firmware(ciphertext: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return unpad(cipher.decrypt(ciphertext), AES.block_size)


def main() -> None:
    firmware_url = f"{BASE_URL}/{FIRMWARE_NAME}"
    hash_url = f"{firmware_url}.sha256"
    signature_url = f"{firmware_url}.sig"
    public_key_url = f"{BASE_URL}/public_key.pem"

    encrypted_firmware = download(firmware_url)
    expected_hash = download(hash_url).decode("utf-8").strip()
    signature = download(signature_url)
    public_key_pem = download(public_key_url)
    actual_hash = sha256_bytes(encrypted_firmware)

    print("expected:", expected_hash)
    print("actual:  ", actual_hash)

    if actual_hash != expected_hash:
        print("result: hash mismatch")
        return

    if not verify_signature(public_key_pem, encrypted_firmware, signature):
        print("result: rsa signature mismatch")
        return

    decrypted_firmware = decrypt_firmware(encrypted_firmware)

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    DEST_ENCRYPTED.write_bytes(encrypted_firmware)
    DEST_DECRYPTED.write_bytes(decrypted_firmware)
    print("result: hash ok, rsa signature ok, decrypt ok")
    print("encrypted saved:", DEST_ENCRYPTED)
    print("decrypted saved:", DEST_DECRYPTED)


if __name__ == "__main__":
    main()
