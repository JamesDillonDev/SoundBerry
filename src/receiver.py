import socket
import threading
import subprocess
import queue
from flask import Flask, request, jsonify

DEVICE_NAME = "SoundBerry"
HTTP_PORT = 5000

app = Flask(__name__)

audio_queue = queue.Queue()
current_process = None
volume = 100


# ----------------------------
# Audio worker thread
# ----------------------------
def audio_worker():
    global current_process

    while True:
        stream = audio_queue.get()

        current_process = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-volume", str(volume), "-"],
            stdin=subprocess.PIPE
        )

        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            current_process.stdin.write(chunk)

        current_process.stdin.close()
        current_process.wait()
        current_process = None


# ----------------------------
# Play endpoint
# ----------------------------
@app.route("/play", methods=["POST"])
def play_audio():
    audio_queue.put(request.stream)
    return "queued"


# ----------------------------
# Stop playback
# ----------------------------
@app.route("/stop", methods=["POST"])
def stop_audio():
    global current_process

    if current_process:
        current_process.kill()
        current_process = None

    return "stopped"


# ----------------------------
# Volume control
# ----------------------------
@app.route("/volume", methods=["POST"])
def set_volume():
    global volume
    data = request.json
    volume = int(data.get("level", 100))
    return jsonify({"volume": volume})


# ----------------------------
# Status endpoint
# ----------------------------
@app.route("/status")
def status():
    return jsonify({
        "playing": current_process is not None,
        "queue": audio_queue.qsize(),
        "volume": volume
    })


# ----------------------------
# Device description
# ----------------------------
@app.route("/desc.xml")
def device_description():
    ip = socket.gethostbyname(socket.gethostname())

    return f"""<?xml version="1.0"?>
<root>
<device>
<deviceType>urn:schemas-upnp-org:device:MediaRenderer:1</deviceType>
<friendlyName>{DEVICE_NAME}</friendlyName>
<manufacturer>SoundBerry</manufacturer>
<modelName>Network Audio Receiver</modelName>
<serialNumber>0001</serialNumber>
<UDN>uuid:soundberry</UDN>
</device>
</root>
"""


# ----------------------------
# SSDP discovery
# ----------------------------
def ssdp_responder():

    MCAST_GRP = "239.255.255.250"
    MCAST_PORT = 1900

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind(("", MCAST_PORT))

    mreq = socket.inet_aton(MCAST_GRP) + socket.inet_aton("0.0.0.0")
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("SSDP discovery active")

    while True:
        data, addr = sock.recvfrom(1024)

        if b"M-SEARCH" in data:

            ip = socket.gethostbyname(socket.gethostname())

            response = f"""HTTP/1.1 200 OK
CACHE-CONTROL: max-age=1800
EXT:
LOCATION: http://{ip}:{HTTP_PORT}/desc.xml
SERVER: SoundBerry/1.0 UPnP/1.1
ST: urn:schemas-upnp-org:device:MediaRenderer:1
USN: uuid:soundberry::urn:schemas-upnp-org:device:MediaRenderer:1

"""

            sock.sendto(response.encode(), addr)


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":

    threading.Thread(target=ssdp_responder, daemon=True).start()
    threading.Thread(target=audio_worker, daemon=True).start()

    print("Starting HTTP server")
    app.run(host="0.0.0.0", port=HTTP_PORT)