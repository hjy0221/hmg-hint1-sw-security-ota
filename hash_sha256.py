"""Small SHA-256 hashing helpers."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256_text(text: str) -> str:
    """Return the SHA-256 hex digest for a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 hex digest for a file."""
    digest = hashlib.sha256()
    file_path = Path(path)

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a SHA-256 hash.")
    parser.add_argument(
        "value",
        nargs="?",
        help="Text to hash, or a file path with --file.",
    )
    parser.add_argument(
        "-f",
        "--file",
        action="store_true",
        help="Hash the contents of the given file path.",
    )
    args = parser.parse_args()

    if args.value is None:
        if args.file:
            args.value = input("File path to hash: ")
        else:
            args.value = input("Text to hash: ")

    if args.file:
        print(sha256_file(args.value))
    else:
        print(sha256_text(args.value))


if __name__ == "__main__":
    main()
