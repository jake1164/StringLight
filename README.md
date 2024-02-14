# StringLight - A project to interactively turn on an string that uses an IR remote control.

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