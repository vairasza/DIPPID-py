import sys
import socket
import json
from threading import Thread
from time import sleep

class Sensor():
    USAGE = """
    can be used in wifi, serial or wiimote mode
    connection param depends on mode
    wifi: UDP port, e.g. 5700
    serial: path to tty, e.g. /dev/ttyUSB0
    bluetooth: bluetooth address, e.g. ab:cd:12:34:ef
    """
    def __init__(self, connection, mode='wifi', baudrate=115200):
        # list of strings which represent capabilites, such as 'buttons' or 'accelerometer'
        self._capabilities = []
        # for each capability, store a list of callback functions
        self._callbacks = {}
        # for each capability, store the last value as an object
        self._data = {}

        self._mode = mode

        if(mode == 'wifi'):
            # listens to all incoming connections for now
            # TODO check if this could be a security issue
            self._ip = '0.0.0.0'
            self._port = connection
        elif(mode == 'serial'):
            self._baudrate = baudrate
            self._tty = connection
        elif(mode == 'wiimote'):
            self._bt_addr = connection
        else:
            # TODO: try to recognize connection type automatically
            print(self.USAGE)
            pass

    def connect(self):
        if(self._mode == 'wifi'):
            self._connect_wifi()
        elif(self._mode  == 'serial'):
            self._connect_serial()
        elif(self._mode  == 'wiimote'):
            self._connect_wiimote() 
        else:
            print(f'invalid mode: {self._mode} - allowed modes: wifi, serial, wiimote')
            pass

    def _connect_wifi(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self._ip, self._port))
        self._connection_wifi = Thread(target=self._receive_wifi)
        self._connection_wifi.start()

    def _connect_serial(self):
        if 'serial' not in sys.modules:
            import serial
        self._serial = serial.Serial(self._tty)
        self._serial.baudrate = self._baudrate
        self._connection_serial = Thread(target=self._receive_serial)
        self._connection_serial.start()

    def _connect_wiimote(self):
        # todo
        pass

    def _receive_wifi(self):
        while True:
            data, addr = self._sock.recvfrom(1024)
            try:
                data_decoded = data.decode()
            except UnicodeDecodeErro:
                continue
            self._update(data_decoded)

    def _receive_serial(self):
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
            self._connect_serial()

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

def test_sensor(arg):
    print('the value is ', arg)

if __name__ == '__main__':
    PORT = 5700
    TTY = '/dev/ttyUSB0'
    test = Sensor(TTY, mode='serial')
    test.connect()

    # event
    test.register_callback('button_1', test_sensor)

    # polling
    while(True):
        print(test.get_value('accelerometer'))
        sleep(0.1)
