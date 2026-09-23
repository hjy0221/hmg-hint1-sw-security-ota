from __future__ import annotations

import socket
import ssl
import threading
from pathlib import Path


HOST = ""
PORT = 8002
SERVER_IP = "localhost"
ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT_DIR / "work" / "chunked_ota_server"
CERT_FILE = SERVER_DIR / "server_cert.pem"
PRIVATE_KEY_FILE = ROOT_DIR / "work" / "firmware_server" / "private_key.pem"


def resolve_request_path(request_path: str) -> Path:
    clean_path = request_path.strip().replace("\\", "/").lstrip("/")
    file_path = (SERVER_DIR / clean_path).resolve()
    server_root = SERVER_DIR.resolve()

    if server_root not in file_path.parents and file_path != server_root:
        raise ValueError("path escapes server directory")
    if not file_path.is_file():
        raise FileNotFoundError(clean_path)
    return file_path


def handle_client(conn: ssl.SSLSocket, address: tuple[str, int]) -> None:
    print(f"client connected: {address[0]}:{address[1]}")
    with conn:
        reader = conn.makefile("rb")
        while True:
            line = reader.readline()
            if not line:
                break

            request_path = line.decode("utf-8").strip()
            if request_path == "QUIT":
                break

            try:
                file_path = resolve_request_path(request_path)
                data = file_path.read_bytes()
            except Exception as exc:
                message = f"ERR {exc}\n".encode("utf-8")
                conn.sendall(message)
                continue

            conn.sendall(f"OK {len(data)}\n".encode("ascii"))
            conn.sendall(data)


def main() -> None:
    if not (SERVER_DIR / "manifest.json").exists():
        raise SystemExit("Run python .\\chunked_ota\\prepare_chunks.py first.")
    if not CERT_FILE.exists():
        raise SystemExit("TLS certificate is missing. Run prepare_chunks.py first.")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=PRIVATE_KEY_FILE)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"TLS socket server: {SERVER_IP}:{PORT}")
        print("request path example: manifest.json")

        while True:
            client_socket, address = server.accept()
            tls_conn = context.wrap_socket(client_socket, server_side=True)
            thread = threading.Thread(target=handle_client, args=(tls_conn, address), daemon=True)
            thread.start()


if __name__ == "__main__":
    main()
