import os
import ssl
import socketpool
import wifi
import time
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from beeboard import BeeBoard

# <prefix>/<component>/<nodeid>/<objectid>/topic
# homeassistant/binary_sensor/patio/stringlight1
BASE_TOPIC = "{}/binary_sensor/{}/{}" 
#TODO: binary_sensor is wrong
DISCOVERY_CONFIG_TOPIC = "{}/binary_sensor/{}/config"
DISCOVERY_CONFIG_DATA = '''
    {"name": null, "device_class": "motion", 
    "state_topic": "{}", "unique_id": "{}",
    "device": {"identifiers": ["{}"], "name": {}}
    }
'''

class Data:
    def __init__(self) -> None:
        ''' Setup the MQTT server here. '''

        BROKER = os.getenv('MQTT_BROKER')
        PORT=int(os.getenv('MQTT_PORT', 1883))
        USERNAME=os.getenv('MQTT_USER')
        PASSWORD=os.getenv('MQTT_PASSWORD')

        # TODO: Check that values have been provided

        self._bee_board = BeeBoard()
        self.MQTT_BASE_TOPIC = BASE_TOPIC.format(
                os.getenv('MQTT_DISCOVERY_UNIT', 'homeassistant'), 
                os.getenv('MQTT_LOCATION_UNIT', 'location'), 
                os.getenv('MQTT_UNIT', 'string_light'))

        # How often to send data. Can eventually be updated by an MQTT data message.
        self._mqtt_data_interval = os.getenv('MQTT_SEND_DATA', 300)
        self._mqtt_deep_sleep_interval = os.getenv('MQTT_DEEP_SLEEP', 0)
        # topics to subscribe
        self.MQTT_IR_REQ_TOGGLE = f"{self.MQTT_BASE_TOPIC}/ir_req_toggle"

        # topics to publish
        self.MQTT_TOPIC_V_BAT = f"{self.MQTT_BASE_TOPIC}/v_bat"
        self.MQTT_TOPIC_IR_TOGGLED = f"{self.MQTT_BASE_TOPIC}/ir_toggled"
        self.MQTT_TOPIC_STATUS = f"{self.MQTT_BASE_TOPIC}/ir_status"

        ssl_context = ssl.create_default_context()
        # SSL Secrets get loaded here?

        # TODO: Nice to not require socketpool in here
        pool = socketpool.SocketPool(wifi.radio)

        self._mqtt_client = MQTT.MQTT(
            #broker=f'"{broker}"',
            broker=BROKER,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
            socket_pool=pool,
            ssl_context=ssl_context,
        )
        self._mqtt_client.on_connect = self.connected
        self._mqtt_client.on_disconnected = self.disconnected
        self._mqtt_client.on_message = self.message

        print(f'Connecting to MQTT Server {self._mqtt_client.broker}')
        self.connect()
        self._last = 0

    def connect(self) -> None:
        ''' Used to connect to the mqtt server. '''
        try:
            self._mqtt_client.connect()
            self._send_data(self.MQTT_TOPIC_STATUS, 'connected')
            self._last = time.time() 
        except Exception as ex:
            print("Unable to connect to MQTT Server")


    def loop(self) -> None:
        ''' Loop to process sending / receiving data when not in deep sleep '''
        #TODO: Loop every time??
        # Attempt to connect
        if not self._mqtt_client.is_connected:
            self.connect()

        #catch connect exception and not send unless connected.
        self._mqtt_client.loop()


    def send_data(self) -> None:
        if time.time() > self._last + self._mqtt_data_interval:
            if not self._mqtt_client.is_connected:
                self.connect()
            
            if self._mqtt_client.is_connected:
                # TODO: hook up logging
                print('Publishing data')
                self._send_data(self.MQTT_TOPIC_V_BAT, self._bee_board.get_battery())
                print('finished publishing data')
                self._last = time.time()
            else:
                print('Unable to publish - mqtt client not connected')


    def send_toggle(self) -> None:
        pass


    def _send_data(self, topic, data):
        try:
            print(f'Attempting to publish {topic} with {data}')
            self._mqtt_client.publish(topic, data)
        except Exception as ex:
            print(f'Unable to send {topic}')


        # THESE NEED TO BE EVENTS subscribed and raised.
    def connected(self, client, userdata, flags, rc) -> None:
        print(f"Connected to MQTT server {self.BROKER} at {client.broker}")


    def disconnected(self, userdata, rc) -> None:
        print("Disconnected from MQTT server")


    def message(self, client, message) -> None:
        print(f"New message on topic: {message}")

    @property
    def is_connected(self) -> bool:
        return self._mqtt_client.is_connected