import http.server


HOST = ""
PORT = 8000


def main() -> None:
    server = http.server.HTTPServer(
        (HOST, PORT),
        http.server.SimpleHTTPRequestHandler,
    )
    print(f"serving current folder on http://192.168.0.60:{PORT}")
    print("example file: http://192.168.0.60:8000/123.txt")
    server.serve_forever()


if __name__ == "__main__":
    main()
