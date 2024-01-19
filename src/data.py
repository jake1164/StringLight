import os

class Data:
    def __init__(self, network) -> None:
        ''' Setup the MQTT server here. '''
        self.network = network
        self.MQTT_TOPIC = "test/topic"
        # topics to subscribe
        self.MQTT_IR_REQ_TOGGLE = f"{os.getenv('MQTT_UNIT')}/ir_req_toggle"

        # topics to publish
        self.MQTT_V_BAT = f"{os.getenv('MQTT_UNIT')}/v_bat"
        self.MQTT_IR_TOGGLED = f"{os.getenv('MQTT_UNIT')}/ir_toggled"
        self.MQTT_STATUS = f"{os.getenv('MQTT_UNIT')}/ir_status"




