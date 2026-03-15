import socket
from config import DEVICE_NAME, HTTP_PORT

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
SERVER: SoundBerry/1.0
ST: urn:schemas-upnp-org:device:MediaRenderer:1
USN: uuid:soundberry::urn:schemas-upnp-org:device:MediaRenderer:1

"""

            sock.sendto(response.encode(), addr)