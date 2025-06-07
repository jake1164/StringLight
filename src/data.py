import os
import ssl
import socketpool
import wifi
import time
import json
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from beeboard import BeeBoard

# <prefix>/<component>/<nodeid>/<objectid>/topic
# homeassistant/binary_sensor/patio/stringlight1/v_bat/config
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
    def __init__(self, toggle_callback=None) -> None:
        ''' Setup the MQTT server here.
            toggle_callback is called when a command to toggle the light is
            received via MQTT.
        '''

        BROKER = os.getenv('MQTT_BROKER')
        PORT = int(os.getenv('MQTT_PORT', 1883))
        USERNAME = os.getenv('MQTT_USER')
        PASSWORD = os.getenv('MQTT_PASSWORD')

        self._toggle_callback = toggle_callback

        # Device details
        self.device_id = os.getenv('MQTT_DEVICE', 'string_light')
        self.discovery_prefix = os.getenv('MQTT_DISCOVERY_UNIT', 'homeassistant')

        # TODO: Check that values have been provided

        self._bee_board = BeeBoard()

        self.MQTT_BASE_TOPIC = BASE_TOPIC.format(
                self.discovery_prefix,
                os.getenv('MQTT_LOCATION_UNIT', 'location'),
                self.device_id)

        # How often to send data. Can eventually be updated by an MQTT data message.
        self._mqtt_data_interval = os.getenv('MQTT_SEND_DATA', 300)
        self._mqtt_deep_sleep_interval = os.getenv('MQTT_DEEP_SLEEP', 0)

        # topics to publish/subscribe
        self.command_topic = f"{self.device_id}/set"
        self.state_topic = f"{self.device_id}/state"
        self.availability_topic = f"{self.device_id}/availability"
        self.MQTT_TOPIC_V_BAT = f"{self.device_id}/v_bat"
        self.MQTT_TOPIC_IR_TOGGLED = f"{self.device_id}/ir_toggled"
        self.MQTT_IR_REQ_TOGGLE = f"{self.MQTT_BASE_TOPIC}/ir_req_toggle"
        self._state = "OFF"

        # TODO: make a topic a class.
        self.SUBSCRIPTION_TOPICS = [
            (self.command_topic, self._on_set),
            (f"{self.MQTT_BASE_TOPIC}/req_toggle", self._on_req_toggle),
            (f"{self.MQTT_BASE_TOPIC}/req_send_data", self._on_send_data),
            (f"{self.device_id}/req_debug", self._on_debug),
        ]

        ssl_context = ssl.create_default_context()
        # SSL Secrets get loaded here?

        # TODO: Nice to not require socketpool in here
        pool = socketpool.SocketPool(wifi.radio)
        self.timeout = 5
        self._mqtt_client = MQTT.MQTT(
            #broker=f'"{broker}"',
            broker=BROKER,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
            socket_pool=pool,
            ssl_context=ssl_context,
            socket_timeout=self.timeout
        )
        self._mqtt_client.will_set(self.availability_topic, "offline", retain=True)


        self._mqtt_client.on_connect = self._on_connected
        self._mqtt_client.on_disconnected = self._on_disconnected
        self._last = 0

        print(f'Connecting to MQTT Server {self._mqtt_client.broker}')
        self.connect()


    def connect(self) -> None:
        ''' Used to connect to the mqtt server. '''
        try:
            self._mqtt_client.connect()
            self._send_data(self.availability_topic, 'online')
            self._send_discovery()
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
        #TODO: Need to catch a timeout or we bring the whole thing down.
        self._mqtt_client.loop(self.timeout + 1)


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


    def send_toggle(self, mode: str) -> None:
        '''Sent anytime the IR pulse was sent. mode indicates source.'''
        self._state = 'ON' if self._state == 'OFF' else 'OFF'
        self._send_data(self.state_topic, self._state)
        self._send_data(self.MQTT_TOPIC_IR_TOGGLED, mode)


    def _send_data(self, topic, data):
        try:
            print(f'Attempting to publish {topic} with {data}')
            self._mqtt_client.publish(topic, data)
        except Exception as ex:
            print(f'Unable to send {topic}')

    def _send_discovery(self):
        '''Publish Home Assistant discovery messages.'''
        battery_config_topic = f"{self.discovery_prefix}/sensor/{self.device_id}/battery/config"
        battery_payload = {
            'name': f'{self.device_id} Battery',
            'state_topic': self.MQTT_TOPIC_V_BAT,
            'unit_of_measurement': 'V',
            'device_class': 'voltage',
            'unique_id': f'{self.device_id}_battery',
            'availability_topic': self.availability_topic,
            'device': {
                'identifiers': [self.device_id],
                'name': self.device_id
            }
        }
        self._mqtt_client.publish(battery_config_topic, json.dumps(battery_payload), retain=True)

        switch_config_topic = f"{self.discovery_prefix}/switch/{self.device_id}/main/config"
        switch_payload = {
            'name': self.device_id,
            'command_topic': self.command_topic,
            'state_topic': self.state_topic,
            'payload_on': 'ON',
            'payload_off': 'OFF',
            'unique_id': f'{self.device_id}_switch',
            'availability_topic': self.availability_topic,
            'device': {
                'identifiers': [self.device_id],
                'name': self.device_id
            }
        }
        self._mqtt_client.publish(switch_config_topic, json.dumps(switch_payload), retain=True)


        # THESE NEED TO BE EVENTS subscribed and raised.
    def _on_connected(self, client, userdata, flags, rc) -> None:
        print(f"Connected to MQTT server")

        self._send_data(self.availability_topic, 'online')
        self._send_discovery()
        
        for msg in self.SUBSCRIPTION_TOPICS:
            print(f'subscribing to: {msg[0]}')
            self._mqtt_client.subscribe(msg[0])
            self._mqtt_client.add_topic_callback(msg[0], msg[1])


    def _on_disconnected(self, userdata, rc) -> None:
        print("Disconnected from MQTT server")
        for msg in self.SUBSCRIPTION_TOPICS:
            self._mqtt_client.unsubscribe(msg[0])
        self._send_data(self.availability_topic, 'offline')

    def _on_set(self, client, topic, message):
        '''Handle on/off commands from Home Assistant.'''
        print(f'Received set command: {message}')
        if self._toggle_callback:
            self._toggle_callback()
        if message.upper() == 'ON':
            self._state = 'ON'
        elif message.upper() == 'OFF':
            self._state = 'OFF'
        else:
            # unknown payload just toggle
            self._state = 'ON' if self._state == 'OFF' else 'OFF'
        self._send_data(self.state_topic, self._state)
        self._send_data(self.MQTT_TOPIC_IR_TOGGLED, 'mqtt')


    def _on_req_toggle(self, client, topic, message):
        '''
        When a request toggle message comes in via MQTT we need to validate that its authentic
        which will hopefully be accomplished via a list of authorized users.
        '''
        print('Received subscribed request toggle command')
        if self._toggle_callback:
            self._toggle_callback()
        self._state = 'ON' if self._state == 'OFF' else 'OFF'
        self._send_data(self.state_topic, self._state)
        self._send_data(self.MQTT_TOPIC_IR_TOGGLED, 'mqtt')


    def _on_send_data(self, client, topic, message):
        ''' 
            Client requested sending of data
        '''
        print('Recieved request to send data')
        self.send_data()


    def _on_debug(self, client, topic, message):
        '''
            Client requested going into / out of debug mode
        '''
        print("debug request sent")


    @property
    def is_connected(self) -> bool:
        return self._mqtt_client.is_connected

