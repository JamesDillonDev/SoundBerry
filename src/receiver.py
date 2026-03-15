import socket
import threading
import subprocess
from flask import Flask, request

DEVICE_NAME = "Pi-Audio-Speaker"
HTTP_PORT = 5000

app = Flask(__name__)

# ----------------------------
# Audio playback endpoint
# ----------------------------
@app.route("/play", methods=["POST"])
def play_audio():
    file_path = "/tmp/berryaudio"

    with open(file_path, "wb") as f:
        f.write(request.data)

    subprocess.run(["ffplay", "-nodisp", "-autoexit", file_path])

    return "playing"


# ----------------------------
# Device description (UPnP)
# ----------------------------
@app.route("/desc.xml")
def device_description():
    ip = socket.gethostbyname(socket.gethostname())

    response = f"""
    <?xml version="1.0"?>
    <root>
    <device>
    <deviceType>urn:schemas-upnp-org:device:MediaRenderer:1</deviceType>
    <friendlyName>{DEVICE_NAME}</friendlyName>
    <manufacturer>Raspberry Pi</manufacturer>
    <modelName>Pi Audio Receiver</modelName>
    <serialNumber>0001</serialNumber>
    <UDN>uuid:pi-audio-renderer</UDN>
    </device>
    </root>
    """
    return response


# ----------------------------
# SSDP discovery responder
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

            response = f"""
            HTTP/1.1 200 OK
            CACHE-CONTROL: max-age=1800
            EXT:
            LOCATION: http://{ip}:{HTTP_PORT}/desc.xml
            SERVER: RaspberryPi/1.0 UPnP/1.1 PiAudio/1.0
            ST: urn:schemas-upnp-org:device:MediaRenderer:1
            USN: uuid:pi-audio-renderer::urn:schemas-upnp-org:device:MediaRenderer:1
            """

            sock.sendto(response.encode(), addr)


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    threading.Thread(target=ssdp_responder, daemon=True).start()
    print("Starting HTTP server")
    app.run(host="0.0.0.0", port=HTTP_PORT)