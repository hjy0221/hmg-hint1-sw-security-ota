"""AES encryption example that prints hex output.

Default mode:
    AES-256-CBC with PKCS7 padding

Examples:
    python aes_encrypt_hex.py "hello"
    python aes_encrypt_hex.py "hello" --key-hex 00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff
"""

from __future__ import annotations

import argparse

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad


AES_BLOCK_SIZE = 16
AES_256_KEY_SIZE = 32


def aes_encrypt_to_hex(
    plaintext: str,
    key: bytes | None = None,
    iv: bytes | None = None,
) -> tuple[str, str, str]:
    """Encrypt plaintext with AES-CBC and return key, IV, ciphertext as hex."""
    if key is None:
        key = get_random_bytes(AES_256_KEY_SIZE)
    if iv is None:
        iv = get_random_bytes(AES_BLOCK_SIZE)

    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 16, 24, or 32 bytes.")
    if len(iv) != AES_BLOCK_SIZE:
        raise ValueError("AES CBC IV must be 16 bytes.")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = pad(plaintext.encode("utf-8"), AES_BLOCK_SIZE)
    ciphertext = cipher.encrypt(padded_plaintext)

    return key.hex(), iv.hex(), ciphertext.hex()


def hex_to_bytes(value: str, name: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be valid hex.") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Encrypt text with AES and print hex.")
    parser.add_argument("plaintext", nargs="?", help="Text to encrypt.")
    parser.add_argument("--key-hex", help="AES key in hex. Length: 16, 24, or 32 bytes.")
    parser.add_argument("--iv-hex", help="CBC IV in hex. Length: 16 bytes.")
    args = parser.parse_args()

    plaintext = args.plaintext
    if plaintext is None:
        plaintext = input("Text to encrypt: ")

    key = hex_to_bytes(args.key_hex, "key") if args.key_hex else None
    iv = hex_to_bytes(args.iv_hex, "iv") if args.iv_hex else None

    key_hex, iv_hex, ciphertext_hex = aes_encrypt_to_hex(plaintext, key, iv)

    print(f"key_hex: {key_hex}")
    print(f"iv_hex: {iv_hex}")
    print(f"ciphertext_hex: {ciphertext_hex}")


if __name__ == "__main__":
    main()
