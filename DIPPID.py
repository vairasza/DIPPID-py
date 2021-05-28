import socket
import json
from threading import Thread
from time import sleep

class Sensor():
    def __init__(self, IP, PORT):
        # list of strings which represent capabilites, such as 'buttons' or 'accelerometer'
        self._capabilities = []
        # for each capability, store a list of callback functions
        self._callbacks = {}
        # for each capability, store the last value as an object
        self._data = {}

        self._ip = IP
        self._port = PORT

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self._ip, self._port))
        self._connection_thread = Thread(target=self._update)
        self._connection_thread.start()

    # runs as a thread
    # receives json formatted data from sensor,
    # stores it and notifies callbacks
    def _update(self):
        while True:
            data, addr = self._sock.recvfrom(1024)
            data_decoded = data.decode()
            data_json = json.loads(data_decoded)
            for key, value in data_json.items():
                self._add_capability(key)

                # notify callbacks only if data has changed
                if self._data[key] != value:
                    self._data[key] = value
                    self._notify_callbacks(key)

    def has_capability(self, key):
        return key in self._capabilities

    def _add_capability(self, key):
        if not has_capabilies(key):
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
    IP = "192.168.178.77"
    PORT = 5700
    test = Sensor(IP, PORT)
    test.connect()

    # event
    test.register_callback('buttons', test_sensor)

    # polling
    #while(True):
    #    print(test.get_value('accelerometer'))
    #    sleep(0.1)
