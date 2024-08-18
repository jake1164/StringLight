

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

class Device:
    def __init__(self, name: str, model: str, sw_version: str, device_id: str) -> None:
        self.device_id = device_id.lower()
        self.name = name
        self.sw_version = sw_version
        self.model = model
        self.identifiers = self.device_id


class Message:
    def __init__(self, topic, state, unique_id, ) -> None:
        pass

    @property 
    def topic(self) -> str:
        return ""

    @property
    def discovery(self) -> object:
        return {}

    @property
    def message(self, value) -> object:
        return {}


#    @property
#    def is_connected(self) -> bool:
#        return self._mqtt_client.is_connected
    


# Get topic from config?
MQTT_TOPIC_V_BAT = "v_bat"
MQTT_TOPIC_V_BAT_CONFIG = { 
    'device_class': 'voltage',
    'state_topic': '{}/v_bat',
    'unit_of_measurement': 'v',
    'value_template': '{{ }}',
    'unique_id': '{}',
    'device': {
        'name': '{}',
        'identifiers': [ '{}'],
    }    
    }

