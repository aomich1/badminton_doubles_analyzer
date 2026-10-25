"""Local browser based desktop launcher for the badminton doubles analyzer."""
from __future__ import annotations

import http.server
import mimetypes
import subprocess
import threading
import webbrowser
from pathlib import Path
import sys


def resource_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "web"
    return Path(__file__).resolve().parent / "web"


class AppServer(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> None:
    root = resource_dir()
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            path = "/index.html" if self.path == "/" else self.path.split("?", 1)[0]
            target = (root / path.lstrip("/")).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                self.send_error(404)
                return
            body = target.read_bytes()
            self.send_response(200)
            content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            if target.suffix in (".mjs", ".js"):
                content_type = "text/javascript; charset=utf-8"
            elif target.suffix == ".task":
                content_type = "application/octet-stream"
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; media-src 'self' blob:; connect-src 'self' blob:; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != "/shutdown":
                self.send_error(404)
                return
            self.send_response(204)
            self.end_headers()
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, _format, *_args):
            pass

    server = AppServer(("127.0.0.1", 0), Handler)
    url = "http://127.0.0.1:{}/".format(server.server_address[1])
    def open_browser():
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["/usr/bin/open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif not webbrowser.open(url):
                raise RuntimeError("既定のブラウザーを開けませんでした")
        except Exception:
            server.shutdown()

    threading.Timer(0.8, open_browser).start()
    try:
        server.serve_forever(poll_interval=0.25)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
