## You need this on your Bee Data Logger in order for the other example programs to work.
# This is a helper library.

# Import required libraries
import time
import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
import adafruit_ds3231


i2c = board.I2C()
rtc = adafruit_ds3231.DS3231(i2c)

days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


# Setup the NeoPixel power pin
pixel_power = DigitalInOut(board.NEOPIXEL_POWER)
pixel_power.direction = Direction.OUTPUT
pixel_power.value = True

vbus_sense = DigitalInOut(board.VBUS_SENSE)
vbus_sense.direction = Direction.INPUT
# Setup the BATTERY voltage sense pin
vbat_voltage = AnalogIn(board.BATTERY)

def get_adc_voltage(pin):
    return (pin.value * 3.3) / 65536     
# Helper functions
def set_pixel_power(state):
    """Enable or Disable power to the onboard NeoPixel to either show colour, or to turn off to reduce current consumption."""
    global pixel_power
    pixel_power.value = state

def set_ldo2_power(state):
    """Enable or Disable power to the onboard NeoPixel to either show colour, or to turn off to reduce current consumption."""
    global ldo2
    ldo2.value = state


def get_vbus_present():
    """Detect if VBUS (5V) power source is present"""
    global vbus_sense
    return vbus_sense.value
    
def get_battery_voltage():
    """Get the approximate battery voltage."""
    # This formula should show the nominal 4.2V max capacity (approximately) when 5V is present and the
    # VBAT is in charge state for a 1S LiPo battery with a max capacity of 4.2V   
    global vbat_voltage
    ADC_RESOLUTION = 2 ** 16 -1
    AREF_VOLTAGE = 3.3
    R1 = 442000
    R2 = 160000
    return (vbat_voltage.value/ADC_RESOLUTION*AREF_VOLTAGE*(R1+R2)/R2)

def rgb_color_wheel(wheel_pos):
    """Color wheel to allow for cycling through the rainbow of RGB colors."""
    wheel_pos = wheel_pos % 255

    if wheel_pos < 85:
        return 255 - wheel_pos * 3, 0, wheel_pos * 3
    elif wheel_pos < 170:
        wheel_pos -= 85
        return 0, wheel_pos * 3, 255 - wheel_pos * 3
    else:
        wheel_pos -= 170
        return wheel_pos * 3, 255 - wheel_pos * 3, 0
    