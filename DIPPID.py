import sys
import json
from threading import Thread
from time import sleep

# those modules are imported dynamically during runtime
# they are imported only if the corresponding class is used
#import socket
#import serial

class Sensor():
    def __init__(self):
        # list of strings which represent capabilites, such as 'buttons' or 'accelerometer'
        self._capabilities = []
        # for each capability, store a list of callback functions
        self._callbacks = {}
        # for each capability, store the last value as an object
        self._data = {}

    # runs as a thread
    # receives json formatted data from sensor,
    # stores it and notifies callbacks
    def _update(self, data):
        try:
            data_json = json.loads(data)
        except json.decoder.JSONDecodeError:
            # incomplete data
            return

        for key, value in data_json.items():
            self._add_capability(key)
            
            # do not notify callbacks on initialization
            if self._data[key] == []:
                self._data[key] = value
                continue

            # notify callbacks only if data has changed
            if self._data[key] != value:
                self._data[key] = value
                self._notify_callbacks(key)

    def has_capability(self, key):
        return key in self._capabilities

    def _add_capability(self, key):
        if not self.has_capability(key):
            self._capabilities.append(key)
            self._callbacks[key] = []
            self._data[key] = []

    def get_capabilities(self):
        return self._capabilities

    # get last value for specified capability
    def get_value(self, key):
        try:
            return self._data[key]
        except KeyError:
            print(f'"{key}" is not a capability of this sensor.')
            return None

    # register a callback function for a change in specified capability
    def register_callback(self, key, func):
        self._add_capability(key)
        self._callbacks[key].append(func)

    # remove already registered callback function for specified capability
    def unregister_callback(self, key, func):
        try:
            self._callbacks[key].remove(func)
        except KeyError:
            print(f'Could not unregister callback "{func}" for key "{key}": Callback not found.')

    def _notify_callbacks(self, key):
        for func in self._callbacks[key]:
            func(self._data[key])

class SensorUDP(Sensor):
    def __init__(self, port):
        Sensor.__init__(self)
        self._ip = '0.0.0.0'
        self._port = port
        self._connect()

    def _connect(self):
        if 'socket' not in sys.modules:
            import socket

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self._ip, self._port))
        self._connection_thread = Thread(target=self._receive)
        self._connection_thread.start()

    def _receive(self):
        while True:
            data, addr = self._sock.recvfrom(1024)
            try:
                data_decoded = data.decode()
            except UnicodeDecodeErro:
                continue
            self._update(data_decoded)

class SensorSerial(Sensor):
    def __init__(self, tty, baudrate=115200):
        Sensor.__init__(self)
        self._tty = tty
        self._baudrate = baudrate
        self._connect()

    def _connect(self):
        if 'serial' not in sys.modules:
            import serial

        self._serial = serial.Serial(self._tty)
        self._serial.baudrate = self._baudrate
        self._connection_thread = Thread(target=self._receive)
        self._connection_thread.start()

    def _receive(self):
        try:
            while True:
                data = self._serial.readline()
                try:
                    data_decoded = data.decode()
                except UnicodeDecodeErro:
                    continue
                self._update(data)
        except:
            # connection lost, try again
            self._connect()

def test_sensor(arg):
    print('the value is ', arg)

if __name__ == '__main__':
    PORT = 5700
    TTY = '/dev/ttyUSB0'
    test = SensorUDP(PORT)

    # event
    test.register_callback('button_1', test_sensor)

    # polling
    while(True):
        print(test.get_value('accelerometer'))
        sleep(0.1)
