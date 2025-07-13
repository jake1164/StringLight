import board
from digitalio import DigitalInOut, Direction
from analogio import AnalogIn

ADC_RESOLUTION = 2 ** 16 -1
AREF_VOLTAGE = 3.3
R1 = 442000
R2 = 160000

class BeeBoard:
    '''
        Methods used by the detected processor.  
    '''
    def __init__(self) -> None:
        self.vbus_sense = DigitalInOut(board.VBUS_SENSE)
        self.vbus_sense.direction = Direction.INPUT
        self.vbat_voltage = AnalogIn(board.BATTERY)


    def get_battery_voltage(self):
        """Get the approximate battery voltage."""
        # This formula should show the nominal 4.2V max capacity (approximately) when 5V is present and the
        # VBAT is in charge state for a 1S LiPo battery with a max capacity of 4.2V
        return (self.vbat_voltage.value/ADC_RESOLUTION*AREF_VOLTAGE*(R1+R2)/R2)


    def get_vbus_present():
        """Detect if VBUS (5V) power source is present"""
        return self.vbus_sense.value