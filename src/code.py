import array
import time, gc, os
import neopixel
import board, pulseio
from digitalio import DigitalInOut, Direction, Pull
import keypad
import supervisor

# Project Classes
from network import WifiNetwork
from status import Status
from data import Data

IR_PIN = board.D9
INPUT_BUTTON = board.D5
#STATUS_PIN = board.D3
IR_PULSE = array.array('H', [9098, 4502, 569, 1661, 569, 583, 568, 1660, 569, 582, 569, 1659, 570, 582, 568, 1660, 569, 590, 570, 581, 570, 1659, 570, 580, 570, 1659, 571, 580, 570, 1657, 568, 583, 543, 1692, 542, 1685, 540, 1687, 539, 1689, 539, 613, 538, 1690, 538, 614, 540, 612, 540, 619, 540, 613, 538, 614, 538, 614, 538, 1690, 539, 612, 538, 1689, 539, 1689, 538, 1688, 1662, 65535])

status = Status()

try:
    # network handles functionality for connecting to wifi, connecting to the NTP server.
    network = WifiNetwork()
except Exception as e:
    print('Network Failure. ', e)

pulse_out = pulseio.PulseOut(IR_PIN, frequency=38000, duty_cycle=2**15)
button = keypad.Keys((INPUT_BUTTON,), value_when_pressed=False, pull=True)
last = None

def send_pulse():
    print('Sending IR pulse')
    pulse_out.send(IR_PULSE)
    status.notify_pulse()

data = Data(toggle_callback=send_pulse)

# Rainbow colours on the NeoPixel
while True:
    status.tick()
    data.loop()
    if network.update_required():
        print('Updating rtc')
        network.set_time()

    event = button.events.get()
    
    if event and not event.released:
        press_start = event.timestamp
        
    if event and event.released:
        length = (event.timestamp - press_start) / 1000
        print(f'button pressed for {length} seconds')
        if length <= 1:
            #toggle
            send_pulse()
            data.send_toggle("local")
        else:
            # Long press option: restart controller
            print('Long press detected, restarting controller...')
            supervisor.reload()

    data.send_data() # data will handle if it should send data or not.

    if last is None or time.time() > last + 15:
        status.display_status()
        last = time.time()
