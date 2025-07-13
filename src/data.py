import os
import ssl
import socketpool
import wifi
import time
import json
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from beeboard import BeeBoard
from device_messages import TopicManager

class Data:
    """Handles MQTT data communication for the device."""
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
        self.location = os.getenv('MQTT_LOCATION_UNIT', 'location')

        # TODO: Check that values have been provided

        self._bee_board = BeeBoard()

        # Create the topic manager
        self.topic_manager = TopicManager(
            device_id=self.device_id,
            discovery_prefix=self.discovery_prefix,
            location=self.location
        )
        
        # Print all topics for verification
        self.topic_manager.print_all_topics()

        # How often to send data. Can eventually be updated by an MQTT data message.
        self._mqtt_data_interval = os.getenv('MQTT_SEND_DATA', 300)
        self._mqtt_deep_sleep_interval = os.getenv('MQTT_DEEP_SLEEP', 0)

        # Get topics from the topic manager
        self.command_topic = self.topic_manager.command_topic
        self.state_topic = self.topic_manager.state_topic
        self.availability_topic = self.topic_manager.availability_topic
        self.MQTT_TOPIC_V_BAT = self.topic_manager.v_bat_topic
        self.MQTT_TOPIC_IR_TOGGLED = self.topic_manager.ir_toggled_topic
        self.MQTT_IR_REQ_TOGGLE = self.topic_manager.ir_req_toggle_topic
        self._state = "OFF"

        # Get subscription topics
        callbacks = {
            'command': self._on_set,
            'req_toggle': self._on_req_toggle,
            'req_send_data': self._on_send_data,
            'req_debug': self._on_debug,
            'req_reset': self._on_reset
        }
        self.SUBSCRIPTION_TOPICS = self.topic_manager.get_subscription_topics(callbacks)

        ssl_context = ssl.create_default_context()
        # SSL Secrets get loaded here?

        # TODO: Nice to not require socketpool in here
        pool = socketpool.SocketPool(wifi.radio)
        # NOTE: the socket_timeout default is 10 seconds, the loop() method will block for the duration of the timeout.
        self._mqtt_client = MQTT.MQTT(
            #broker=f'"{broker}"',
            broker=BROKER,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
            socket_pool=pool,
            ssl_context=ssl_context,
            socket_timeout=0.1
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
            print("Connected to MQTT server, sending availability")
            self._mqtt_client.publish(self.availability_topic, 'online', retain=True)
            print("Sending discovery messages")
            self._send_discovery()
            self._last = time.time()
        except Exception as ex:
            print(f"Unable to connect to MQTT Server: {ex}")


    def loop(self) -> None:
        ''' Loop to process sending / receiving data when not in deep sleep '''
        if not self._mqtt_client.is_connected:
            self.connect()

        self._mqtt_client.loop(timeout=0.1)


    def send_data(self) -> None:
        if time.time() > self._last + self._mqtt_data_interval:
            if not self._mqtt_client.is_connected:
                self.connect()
            
            if self._mqtt_client.is_connected:
                # TODO: hook up logging
                print('Publishing data')
                self._send_data(self.MQTT_TOPIC_V_BAT, self._bee_board.get_battery_voltage())
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
            print(f'Successfully published to {topic}')
        except Exception as ex:
            print(f'Unable to send {topic}: {ex}')

    def _send_discovery(self):
        '''Publish Home Assistant discovery messages.'''
        discovery_messages = self.topic_manager.get_discovery_messages()
        
        print("Publishing discovery messages:")
        for topic, payload in discovery_messages:
            print(f"  Topic: {topic}")
            print(f"  Payload: {payload}")
            # Ensure the payload is valid JSON before sending
            try:
                # Verify the JSON payload
                test_json = json.loads(payload)
                print(f"  Payload is valid JSON: {test_json}")
                # Send with retain=True to ensure Home Assistant picks it up
                self._mqtt_client.publish(topic, payload, retain=True)
                print(f"  Published to {topic}")
            except json.JSONDecodeError as e:
                print(f"  ERROR: Invalid JSON payload: {e}")
        
        # After discovery, explicitly set the state to OFF to ensure sync
        print("Setting initial state to OFF")
        self._state = "OFF"
        self._send_data(self.state_topic, self._state)


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


    def _on_reset(self, client, topic, message):
        '''
            Client requested resetting the state to OFF
        '''
        print("Reset request received - setting state to OFF")
        self._state = "OFF"
        self._send_data(self.state_topic, self._state)
        self._send_data(self.MQTT_TOPIC_IR_TOGGLED, 'reset')


    @property
    def is_connected(self) -> bool:
        return self._mqtt_client.is_connected

