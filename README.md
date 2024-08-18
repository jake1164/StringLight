# StringLight - A project to interactively turn on a solar light string that uses an IR remote control.
![figure 1](/images/stringlights.jpg)
[SunForce](https://sunforceproducts.com/renewable-energy-products-wind-solar-sunforce/our-products/lawn-and-garden/15-led-bulbs-solar-string-lights-with-remote-control/) LED Bulbs Solar String Light w/ Remote Control



## Hardware List (links for reference only)
SmartBee S3 or Data Logger microcontroller (S3 recommended for low power consumption) [smartbee](https://smartbeedesigns.com/)
- JST-PH 2-pin Jumper Cable - 100mm long [adafruit](https://www.adafruit.com/product/4714)
- Lithium Ion Polymer Battery - 3.7v 500mAh [adafruit](https://www.adafruit.com/product/1578)
- Waterproof DC Power Cable Set - 5.5/2.1mm [adafruit](https://www.adafruit.com/product/743)
- Adafruit Universal USB / DC / Solar Lithium Ion/Polymer charger [adafruit](https://www.adafruit.com/product/4755)
-  2.1mm DC Jack Adapter Cable [adafruit](https://www.adafruit.com/product/2788)
- 2x 5MM LED Holder [amazon](https://www.amazon.com/dp/B07WNMNS9P)
- DIY Waterproof Box 3.94 x 2.68 x 1.97 inch (100 x 68 x 50 mm) [amazon](https://www.amazon.com/dp/B08FSNX11Z)
- 12mm Momentary Push Button Waterproof [amazon](https://www.amazon.com/gp/product/B07F9PLSRY)
- IR Infrared LED Diode 5mm Emitter
- 5mm Green LED
- 6in usb-c cable

## Diagram
- todo


## Programming
### Installing on device 
- Install CircuitPython 9.x on Bee S3 or Bee Data Logger
- From root folder install required libraries (circup install -r requirements.txt)
- Copy files from src to device
- Rename (or copy) settings.toml.default to settings.toml
- Update settings in settings.toml file to match your network and mqtt login


#### Dependencies
- Microcontroller: Bee Data Logger (https://www.devboarddb.com/details/QPE0RcornwrYC29O_qsZC)
 NOTE: Will eventually work with a Bee S3 without RTC and no data logging installed (https://www.devboarddb.com/details/8Pr9-73v4cqhcKhvoGybx)
- CircuitPython 9.x (even though its in beta)
- Circup for installing libraries (https://docs.circuitpython.org/projects/circup/en/latest/index)