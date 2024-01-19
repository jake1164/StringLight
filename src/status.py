import board
import time

from digitalio import DigitalInOut, Direction, Pull

PATTERNS = {
    "NORMAL":
    {
        "type": "NORMAL", # RENAME ME FFS
        "flashes": 1,
        "led_duration":  1, # in seconds?
        "flash_pause": 1 # pause between flashes
    },
    "PULSE":
    {
        "type": "PULSE", 
        "flashes": 2,
        "led_duration":  1, # in seconds?
        "flash_pause": 1 # pause between flashes
    },
    "NETWORK_ERROR":
    {
        "type": "NETWORK_ERROR", # RENAME ME FFS
        "flashes": 5,
        "led_duration":  1, # in seconds?
        "flash_pause": 1 # pause between flashes
    }
}

class Status:
    def __init__(self) -> None:
        
        STATUS_PIN = board.D3

        self._status_led = DigitalInOut(STATUS_PIN)
        self._status_led.direction = Direction.OUTPUT
        self._status_led.value = False

        self._flash = None
#        self._flashes = 0 # number of times to repeat
#        self._led_duration = 0  # How long do we leave LED on for
#        self._flash_pause = 0 # how long between flashes


    def tick(self):
        ''' Tick is called every time so the LED value can be updated '''
        #print(f'tick? {self._flash} - LED: {self._status_led.value}')
        if self._flash and time.time() > self._flash.led_off_time:
            # when reaches 0 turn off led
            self._status_led.value = False
            self._flash = None


    def display_status(self):
        ''' Normal is 1 slow led flash '''
        if not self._flash: # Only toggle if not in a current pattern
            self._flash = self.Pattern(PATTERNS["NORMAL"])
            self._status_led.value = True
        print(f'Flash? {self._flash} - LED: {self._status_led.value}')


    def notify_pulse(self):
        ''' Pulse notify is 2 quick flashes '''
        self._flash = self.Pattern(PATTERNS["PULSE"])
        self._flash.flashes = 0 if self._flash.flashes <= 1 else self._flash.flashes - 1
        self._status_led.value = True        


    def network_error(self):
        ''' Network Error is 5 quick flashes '''
        pass


    class Pattern:
        def __init__(self, pattern) -> None:
            self.flashes = pattern["flashes"]
            self.led_off_time = time.time() + pattern["led_duration"]
            self.flash_pause = pattern["flash_pause"]

        
