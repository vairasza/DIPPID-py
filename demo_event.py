from DIPPID import SensorUDP
#from DIPPID import SensorSerial
#from DIPPID import SensorWiimote

# use UPD (via WiFi) for communication
PORT = 5700
sensor = SensorUDP(PORT)

# use the serial connection (USB) for communication
#TTY = '/dev/ttyUSB0'
#sensor = SensorSerial(TTY)

# use a Wiimote (via Bluetooth) for communication
#BTADDR = '18:2A:7B:F4:BC:65'
#sensor = SensorWiimote(BTADDR)

def handle_button_press(data):
    if int(data) == 0:
        print('button released')
    else:
        print('button pressed')

sensor.register_callback('button_1', handle_button_press)
