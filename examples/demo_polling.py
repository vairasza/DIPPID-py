from time import sleep

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

while(True):
    # print all capabilities of the sensor
    print('capabilities: ', sensor.get_capabilities())

    # check if the sensor has the 'accelerometer' capability
    if(sensor.has_capability('accelerometer')):
        # print whole accelerometer object (dictionary)
        print('accelerometer data: ', sensor.get_value('accelerometer'))

        # print only one accelerometer axis
        print('accelerometer X: ', sensor.get_value('accelerometer')['x'])

    sleep(0.1)
