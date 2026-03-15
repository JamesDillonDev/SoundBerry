from flask import Flask, request, jsonify, render_template
from audio.player import play_stream, stop_audio, set_volume, get_status, play_file
import socket

DEVICE_NAME = "SoundBerry"
HTTP_PORT = 5000

app = Flask(__name__)


def register_routes():

    # ----------------------------
    # Web dashboard
    # ----------------------------
    @app.route("/")
    def dashboard():
        return render_template("index.html")

    # ----------------------------
    # Play audio stream
    # ----------------------------
    @app.route("/play", methods=["POST"])
    def play_audio():
        play_stream(request.stream)
        return "playing"

    # ----------------------------
    # Play file directly
    # ----------------------------
    @app.route("/playfile", methods=["POST"])
    def playfile():
        data = request.json
        path = data.get("path")
        play_file(path)
        return "playing"

    # ----------------------------
    # Stop playback
    # ----------------------------
    @app.route("/stop", methods=["POST"])
    def stop():
        stop_audio()
        return "stopped"

    # ----------------------------
    # Set volume
    # ----------------------------
    @app.route("/volume", methods=["POST"])
    def volume():
        level = request.json.get("level")
        set_volume(level)
        return "ok"

    # ----------------------------
    # Get player status
    # ----------------------------
    @app.route("/status")
    def status():
        return jsonify(get_status())

    # ----------------------------
    # Device description (UPnP)
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