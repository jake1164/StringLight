import board
import supervisor

from digitalio import DigitalInOut, Direction, Pull

PATTERNS = {
    "NORMAL":
    {
        "type": "NORMAL", # RENAME ME FFS
        "flashes": 1,
        "led_duration":  1000, # in ms?
        "flash_pause": 500 # in ms pause between flashes
    },
    "PULSE":
    {
        "type": "PULSE", 
        "flashes": 2,
        "led_duration":  1000, # in seconds?
        "flash_pause": 300 # pause between flashes
    },
    "NETWORK_ERROR":
    {
        "type": "NETWORK_ERROR", # RENAME ME FFS
        "flashes": 5,
        "led_duration":  500, # in seconds?
        "flash_pause": 200 # pause between flashes
    }
}

class Status:
    def __init__(self) -> None:
        STATUS_PIN = board.D3
        self._status_led = DigitalInOut(STATUS_PIN)
        self._status_led.direction = Direction.OUTPUT
        self._status_led.value = False
        self._flash = None


    def tick(self):
        ''' Tick is called every time so the LED value can be updated '''
        if self._flash and self._flash.led_duration_time > 0 and supervisor.ticks_ms() > self._flash.led_duration_time:
            self._status_led.value = False # turn off LED
            # evaluate if we have to pause for a flashing pattern
            if self._flash.flashes > 0:
                self._flash.led_pause_time = supervisor.ticks_ms()
            else:
                self._flash = None # no more time, shut down.
        elif self._flash and self._flash.led_pause_time > 0 and supervisor.ticks_ms() > self._flash.led_pause_time:
            # pause over, set flash duration.
            self._status_led.value = True
            self._flash.led_duration_time = supervisor.ticks_ms()


    def display_status(self):
        ''' Normal is 1 slow led flash '''
        if not self._flash: # Only toggle if not in a current pattern
            self._flash = self.Pattern(PATTERNS["NORMAL"])
            self._flash.led_duration_time = supervisor.ticks_ms()
            self._status_led.value = True


    def notify_pulse(self):
        ''' Pulse notify is 2 quick flashes '''
        self._flash = self.Pattern(PATTERNS["PULSE"])
        self._flash.led_duration_time = supervisor.ticks_ms()
        self._status_led.value = True


    def network_error(self):
        ''' Network Error is 5 quick flashes '''
        self._flash = self.Pattern(PATTERNS["NETWORK_ERROR"])
        self._flash.led_duration_time = supervisor.ticks_ms()
        self._status_led.value = True


    class Pattern:
        def __init__(self, pattern) -> None:
            # Durations
            self._led_duration = pattern["led_duration"]
            self._flash_pause = pattern["flash_pause"]
            self._flashes = pattern["flashes"]
            # time holders
            self._flashes_left = self._flashes
            self._led_duration_time = 0
            self._led_pause_time = 0


        @property
        def led_pause_time(self):
            return self._led_pause_time

        @led_pause_time.setter
        def led_pause_time(self, value):
            self._led_duration_time = 0
            self._led_pause_time = value + self._flash_pause


        @property
        def led_duration_time(self):
            return self._led_duration_time

        @led_duration_time.setter
        def led_duration_time(self, value):
            self._led_pause_time = 0
            self._led_duration_time = value + self._led_duration
            self._decrement_flash()


        @property
        def flashes(self):
            return self._flashes_left

        def _decrement_flash(self):
            self._flashes_left = 0 if self._flashes_left == 1 else self._flashes_left - 1
