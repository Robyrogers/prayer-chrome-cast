import threading
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.1', 1))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'


class AudioServer:
    def __init__(self, directory: str = ".", port: int = 8000):
        self.directory = directory
        self.port = port
        self.server = None
        self.thread = None

    def start(self) -> str:
        handler = lambda *args: SimpleHTTPRequestHandler(*args, directory=self.directory)
        self.server = HTTPServer(("0.0.0.0", self.port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        ip = get_local_ip()
        return f"http://{ip}:{self.port}/"

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.thread.join()