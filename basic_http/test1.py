import http.server
from pathlib import Path


HOST = ""
PORT = 8000
SERVER_IP = "192.168.0.60"
SERVER_DIR = Path(__file__).resolve().parent


def main() -> None:
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args,
        directory=str(SERVER_DIR),
        **kwargs,
    )
    server = http.server.HTTPServer(
        (HOST, PORT),
        handler,
    )
    print(f"serving {SERVER_DIR} on http://{SERVER_IP}:{PORT}")
    print(f"example file: http://{SERVER_IP}:{PORT}/123.txt")
    server.serve_forever()


if __name__ == "__main__":
    main()
