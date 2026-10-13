import threading
import webview

from werkzeug.serving import make_server
from server import app


class FlaskServer(threading.Thread):

    def __init__(self):
        super().__init__()
        self.server = make_server("127.0.0.1", 3000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


server = FlaskServer()
server.start()


window = webview.create_window(
    "Gestalt Lens",
    "http://127.0.0.1:3000",
    width=1100,
    height=800,
    min_size=(800, 600)
)


def on_closed():
    print("Closing Gestalt Lens...")
    server.shutdown()


window.events.closed += on_closed

webview.start()