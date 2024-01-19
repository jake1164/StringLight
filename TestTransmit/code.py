import array
import time, gc, os
#import neopixel
import board
from digitalio import DigitalInOut, Direction, Pull
import bdl
#import bees3
#import adafruit_irremote
import pulseio

# Create a NeoPixel instance
# Brightness of 0.3 is ample for the 1515 sized LED
#pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=True, pixel_order=neopixel.GRB)

# Create a colour wheel index int
#color_index = 0

# Turn on the power to the NeoPixel
#bees3.set_pixel_power(True)

button = DigitalInOut(board.D4)
button.direction = Direction.INPUT
button.pull = Pull.UP

pulse_out = pulseio.PulseOut(board.D10, frequency=38000, duty_cycle=2**15)
pulses = array.array('H', [9098, 4502, 569, 1661, 569, 583, 568, 1660, 569, 582, 569, 1659, 570, 582, 568, 1660, 569, 590, 570, 581, 570, 1659, 570, 580, 570, 1659, 571, 580, 570, 1657, 568, 583, 543, 1692, 542, 1685, 540, 1687, 539, 1689, 539, 613, 538, 1690, 538, 614, 540, 612, 540, 619, 540, 613, 538, 614, 538, 614, 538, 1690, 539, 612, 538, 1689, 539, 1689, 538, 1688, 1662, 65535])

# Rainbow colours on the NeoPixel
button_pressed = False

while True:
    # Get the R,G,B values of the next colour
    #r,g,b = bees3.rgb_color_wheel( color_index )
    # Set the colour on the NeoPixel
    #pixel[0] = ( r, g, b, 0.5)
    # Increase the wheel index
    #color_index += 1
    
    if not button.value:        
        button_pressed = True
        
    if button_pressed:
        button_pressed = False
        print("Sending Signal")
        #emitter.transmit(pulse_out, [85, 170, 23, 232])
        pulse_out.send(pulses)
        time.sleep(0.015)    
        
        
    # Sleep for 15ms so the colour cycle isn't too fast
    #time.sleep(0.015)