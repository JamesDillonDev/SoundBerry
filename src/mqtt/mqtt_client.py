import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT

client = mqtt.Client()

def start():

    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()