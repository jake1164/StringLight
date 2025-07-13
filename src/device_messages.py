import json

# MQTT Topic patterns for Home Assistant discovery
# <prefix>/<component>/<nodeid>/<objectid>/topic
# Example: homeassistant/binary_sensor/patio/stringlight1/v_bat/config
BASE_TOPIC = "{}/binary_sensor/{}/{}" 
#TODO: binary_sensor is wrong
DISCOVERY_CONFIG_TOPIC = "{}/binary_sensor/{}/config"
DISCOVERY_CONFIG_DATA = '''
    {"name": null, "device_class": "motion", 
    "state_topic": "{}", "unique_id": "{}",
    "device": {"identifiers": ["{}"], "name": {}}
    }
'''

class Device:
    """Represents a device in the Home Assistant ecosystem with its identifiers."""
    def __init__(self, name: str, model: str = "", sw_version: str = "", device_id: str = "") -> None:
        self.device_id = device_id.lower()
        self.name = name
        self.sw_version = sw_version
        self.model = model
        self.identifiers = self.device_id


class Topic:
    """Represents an MQTT topic with its configuration and message handling."""
    def __init__(self, device_id: str, topic_name: str, callback=None):
        self.device_id = device_id
        self.topic_name = topic_name
        self.callback = callback
        
    @property
    def topic(self) -> str:
        """Get the full topic string"""
        return f"{self.device_id}/{self.topic_name}"
    
    def format_message(self, data):
        """Format a message for this topic"""
        return data


class DiscoveryTopic(Topic):
    """A specialized topic used for Home Assistant MQTT discovery"""
    def __init__(self, discovery_prefix: str, component: str, device_id: str, object_id: str):
        super().__init__(device_id, f"{component}/{object_id}")
        self.discovery_prefix = discovery_prefix
        self.component = component
        self.object_id = object_id
        
    @property
    def config_topic(self) -> str:
        """Get the discovery configuration topic"""
        return f"{self.discovery_prefix}/{self.component}/{self.device_id}/{self.object_id}/config"


class BatteryTopic(DiscoveryTopic):
    """Battery voltage reporting topic"""
    def __init__(self, discovery_prefix: str, device_id: str):
        super().__init__(discovery_prefix, "sensor", device_id, "battery")
        # Keep the exact original topic format
        self.state_topic = f"{device_id}/v_bat"
        
    @property
    def config_topic(self) -> str:
        """Get the discovery configuration topic exactly as before"""
        return f"{self.discovery_prefix}/sensor/{self.device_id}/battery/config"
        
    def get_discovery_payload(self, availability_topic: str):
        """Get the discovery payload for a battery sensor"""
        return {
            'name': f'{self.device_id} Battery',
            'state_topic': self.state_topic,
            'unit_of_measurement': 'V',
            'device_class': 'voltage',
            'unique_id': f'{self.device_id}_battery',
            'availability_topic': availability_topic,
            'device': {
                'identifiers': [self.device_id],
                'name': self.device_id
            }
        }


class SwitchTopic(DiscoveryTopic):
    """Switch/light control topic"""
    def __init__(self, discovery_prefix: str, device_id: str):
        super().__init__(discovery_prefix, "switch", device_id, "main")
        self.command_topic = f"{device_id}/set"
        self.state_topic = f"{device_id}/state"
    
    @property
    def config_topic(self) -> str:
        """Get the discovery configuration topic exactly as before"""
        return f"{self.discovery_prefix}/switch/{self.device_id}/main/config"
        
    def get_discovery_payload(self, availability_topic: str):
        """Get the discovery payload for a switch"""
        return {
            'name': self.device_id,
            'command_topic': self.command_topic,
            'state_topic': self.state_topic,
            'payload_on': 'ON',
            'payload_off': 'OFF',
            'state_off': 'OFF',  # Set initial state to OFF
            'unique_id': f'{self.device_id}_switch',
            'availability_topic': availability_topic,
            'device': {
                'identifiers': [self.device_id],
                'name': self.device_id
            }
        }


class TopicManager:
    """Manages MQTT topics and discovery configurations for a device"""
    def __init__(self, device_id: str, discovery_prefix: str = "homeassistant", location: str = "location"):
        self.device_id = device_id
        self.discovery_prefix = discovery_prefix
        self.location = location
        
        # Standard device topics - maintain exact original format
        self.command_topic = f"{device_id}/set"  # Original format
        self.state_topic = f"{device_id}/state"  # Original format
        self.availability_topic = f"{device_id}/availability"  # Original format
        self.v_bat_topic = f"{device_id}/v_bat"  # Original format
        self.ir_toggled_topic = f"{device_id}/ir_toggled"  # Original format
        
        # Base topic for requests
        self.base_topic = BASE_TOPIC.format(discovery_prefix, location, device_id)
        self.ir_req_toggle_topic = f"{self.base_topic}/ir_req_toggle"  # Original format
        
        # Discovery topics
        self.battery_topic = BatteryTopic(discovery_prefix, device_id)
        self.switch_topic = SwitchTopic(discovery_prefix, device_id)
    
    def get_subscription_topics(self, callbacks):
        """
        Get a list of subscription topics with their callbacks
        
        Args:
            callbacks: Dictionary mapping topic names to callback functions
                       {'command': function, 'req_toggle': function, 'req_reset': function, ...}
        
        Returns:
            List of tuples (topic, callback)
        """
        # Use the exact original topic formats
        topics = [
            (self.command_topic, callbacks.get('command')),
            (f"{self.base_topic}/req_toggle", callbacks.get('req_toggle')),
            (f"{self.base_topic}/req_send_data", callbacks.get('req_send_data')),
            (f"{self.device_id}/req_debug", callbacks.get('req_debug')),
            (f"{self.device_id}/req_reset", callbacks.get('req_reset')),
        ]
        return [(topic, cb) for topic, cb in topics if cb is not None]
    
    def get_discovery_messages(self):
        """Get all discovery configuration messages for this device"""
        # Create the exact same discovery messages as the original code
        battery_payload = self.battery_topic.get_discovery_payload(self.availability_topic)
        switch_payload = self.switch_topic.get_discovery_payload(self.availability_topic)
        
        messages = [
            (self.battery_topic.config_topic, battery_payload),
            (self.switch_topic.config_topic, switch_payload),
        ]
        
        # Ensure the payload is formatted exactly as before
        return [(topic, json.dumps(payload)) for topic, payload in messages]
    
    def print_all_topics(self):
        """Print all topics for verification purposes"""
        print("=== Topic Manager Topics ===")
        print(f"command_topic: {self.command_topic}")
        print(f"state_topic: {self.state_topic}")
        print(f"availability_topic: {self.availability_topic}")
        print(f"v_bat_topic: {self.v_bat_topic}")
        print(f"ir_toggled_topic: {self.ir_toggled_topic}")
        print(f"base_topic: {self.base_topic}")
        print(f"ir_req_toggle_topic: {self.ir_req_toggle_topic}")
        print(f"battery_topic.config_topic: {self.battery_topic.config_topic}")
        print(f"switch_topic.config_topic: {self.switch_topic.config_topic}")
        print("=== End Topics ===")
    
    def get_reset_state_message(self):
        """Get a message to reset the device state to OFF"""
        return (self.state_topic, "OFF")


# Standard topics used by the device
DEVICE_TOPICS = {
    'command': 'set',               # Topic for receiving commands
    'state': 'state',               # Topic for reporting state
    'availability': 'availability', # Topic for reporting availability
    'v_bat': 'v_bat',               # Topic for reporting battery voltage
    'ir_toggled': 'ir_toggled',     # Topic for reporting IR toggle events
    'req_toggle': 'req_toggle',     # Topic for requesting toggle
    'req_send_data': 'req_send_data', # Topic for requesting data update
    'req_debug': 'req_debug',       # Topic for requesting debug mode
    'req_reset': 'req_reset'        # Topic for requesting state reset to OFF
}

