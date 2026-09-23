import argparse
import socket
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_URL = "https://192.168.0.64:8080/firmware.bin"
DEFAULT_DEST = Path("./work/device/active.bin")


def download_firmware(
    url: str,
    destination: Path,
    timeout: float,
    insecure: bool,
) -> int:
    context = None
    if insecure:
        context = ssl._create_unverified_context()

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "HINT1-OTA-Downloader/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            blob = response.read()
    except (TimeoutError, socket.timeout, urllib.error.URLError) as exc:
        print("[ERROR] Firmware download failed.")
        print(f"URL: {url}")
        print(f"Reason: {exc}")
        print()
        print("Check these items:")
        print("- Is the firmware server running on 192.168.0.64:8080?")
        print("- Is this PC on the same network as 192.168.0.64?")
        print("- If the server uses HTTP, run with http:// instead of https://.")
        print("- If HTTPS uses a self-signed certificate, add --insecure.")
        print("- Check firewall settings for port 8080.")
        return 1

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(blob)

    print("download:", len(blob), "bytes")
    print("saved:", destination)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Download OTA firmware image.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Firmware download URL.")
    parser.add_argument(
        "--dest",
        default=str(DEFAULT_DEST),
        help="Destination path for downloaded firmware.",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="Network timeout seconds.")
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable HTTPS certificate verification for local test servers.",
    )
    args = parser.parse_args()

    return download_firmware(
        url=args.url,
        destination=Path(args.dest),
        timeout=args.timeout,
        insecure=args.insecure,
    )


if __name__ == "__main__":
    sys.exit(main())
