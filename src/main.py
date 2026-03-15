import threading

from network.http_server import app, register_routes
from network.ssdp import ssdp_responder
from config import HTTP_PORT


if __name__ == "__main__":

    register_routes()

    threading.Thread(target=ssdp_responder, daemon=True).start()

    print("Starting HTTP server")

    app.run(host="0.0.0.0", port=HTTP_PORT)