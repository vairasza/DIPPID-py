import json, signal, sys, time
from typing import Callable, Union, TypedDict
from threading import Thread
from enum import Enum


class M5_CAPA(Enum):
    BUTTON_1 = "button_1"
    BUTTON_2 = "button_2"
    BUTTON_3 = "button_3"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    ROTATION = "rotation"
    TEMPERATURE = "temperature"


class ANDROID_CAPA(Enum):
    BUTTON_1 = "button_1"
    BUTTON_2 = "button_2"
    BUTTON_3 = "button_3"
    BUTTON_4 = "button_4"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    GRAVITY = "gravity"


CAPABILITES = Union[ANDROID_CAPA, M5_CAPA]


class T_3D(TypedDict):
    x: float
    y: float
    z: float
    last_update: float


class T_Rotation(TypedDict):
    pitch: float
    roll: float
    yaw: float
    last_update: float


# 0 / "down"; 1 / "up"
class T_Button(TypedDict):
    pressed: int
    last_update: float


class T_Temperature(TypedDict):
    degree: float
    last_update: float


class T_Data(TypedDict, total=False):
    button_1: T_Button
    button_2: T_Button
    button_3: T_Button
    button_4: T_Button
    accelerometer: T_3D
    gyroscope: T_3D
    rotation: T_Rotation
    temperature: T_Temperature
    gravity: T_3D


class Mapping:
    key: str = None
    capabilites: list[CAPABILITES] = []
    func: Callable[[T_Data], None] = None


class Sensor:
    # class variable that stores all instances of Sensor
    instances = []

    def __init__(self) -> None:
        # list of strings which represent capabilites, such as 'buttons' or 'accelerometer'
        self._capabilities: list[CAPABILITES] = []
        # for each capability, store a list of callback functions
        self._callbacks: dict[str, Mapping] = {}
        # for each capability, store the last value as an object
        self._data: T_Data = {}
        self._receiving: bool = False
        self._last_update: float = time.time()  # TODO: implement heartbeat
        Sensor.instances.append(self)

    # stops the loop in _receive() and kills the thread
    # so the program can terminate smoothly
    def disconnect(self) -> None:
        self._receiving = False
        Sensor.instances.remove(self)
        if self._connection_thread:
            self._connection_thread.join()

    # runs as a thread
    # receives json formatted data from sensor,
    # stores it and notifies callbacks
    def _update(self, data: str | bytes | bytearray) -> None:
        try:
            data_json: dict[str, any] = json.loads(data)
        except json.decoder.JSONDecodeError:
            # incomplete data
            return

        self._last_update = time.time()

        for key, value in data_json.items():
            key_type: CAPABILITES = CAPABILITES[key.upper()]
            self._add_capability(key_type)

            if type(value) == dict:
                value["last_update"] = time.time()
            else:
                value = {"value": value, "last_update": time.time()}

            # do not notify callbacks on initialization
            if self._data[key] == []:
                self._data[key] = value
                continue

            # notify callbacks only if data has changed
            if self._data[key] != value:
                self._data[key] = value
                self._notify_callbacks(key_type)

    # checks if capability is available
    def has_capability(self, key: CAPABILITES) -> bool:
        return key in self._capabilities

    def has_capabilities(self, keys: list[CAPABILITES]) -> bool:
        return set(keys).issubset(self._capabilities)

    def _add_capability(self, key: CAPABILITES) -> None:
        if not self.has_capability(key):
            self._capabilities.append(key)
            self._data[key.name] = []

    # returns a list of all current capabilities
    def get_capabilities(self) -> list[CAPABILITES]:
        return self._capabilities

    # get last value for specified capability
    def get_value(self, keys: list[CAPABILITES]) -> T_Data:
        result = {}

        for key in keys:
            result[key.name] = self._data[key.name]

        return result

    # register a callback function for a change in specified capability
    def register_callback(self, mapping: Mapping) -> bool:
        if mapping.key in self._callbacks:
            return False

        for capability in mapping.capabilites:
            self._add_capability(capability)

        self._callbacks[mapping.key].append(mapping)

        return True

    # remove already registered callback function for specified capability
    def unregister_callback(self, mapping: Mapping) -> bool:
        if mapping.key in self._callbacks:
            self._callbacks[mapping.key].remove(mapping)
            return True

        else:
            # in case somebody wants to check if the callback was present before
            return False

    def _notify_callbacks(self, key: str) -> None:
        for callback in self._callbacks.values():
            if not CAPABILITES[key.upper()] in callback.capabilites:
                continue

            callback.func({[key]: self._data[key]})


# sensor connected via WiFi/UDP
# initialized with a UDP port
# listens to all IPs by default
# requires the socket module
class SensorUDP(Sensor):
    def __init__(self, port: int, ip: str = "0.0.0.0") -> None:
        Sensor.__init__(self)
        self._ip = ip
        self._port = port
        self._connect()

    def _connect(self) -> None:
        import socket

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self._ip, self._port))
        self._connection_thread = Thread(target=self._receive)
        self._connection_thread.start()

    def _receive(self) -> None:
        self._receiving = True
        while self._receiving:
            data, *_ = self._sock.recvfrom(1024)
            try:
                data_decoded = data.decode()
            except UnicodeDecodeError:
                continue
            self._update(data_decoded)


# sensor connected via serial connection (USB)
# initialized with a path to a TTY (e.g. /dev/ttyUSB0)
# default baudrate is 115200
# requires pyserial
class SensorSerial(Sensor):
    def __init__(self, tty, baudrate=115200):
        Sensor.__init__(self)
        self._tty = tty
        self._baudrate = baudrate
        self._connect()

    def _connect(self):
        import serial

        self._serial = serial.Serial(self._tty)
        self._serial.baudrate = self._baudrate
        self._connection_thread = Thread(target=self._receive)
        self._connection_thread.start()

    def _receive(self):
        self._receiving = True
        try:
            while self._receiving:
                data = self._serial.readline()
                try:
                    data_decoded = data.decode()
                except UnicodeDecodeError:
                    continue
                self._update(data)
        except:
            # connection lost, try again
            self._connect()


# uses a Nintendo Wiimote as a sensor (connected via Bluetooth)
# initialized with a Bluetooth address
# requires wiimote.py (https://github.com/RaphaelWimmer/wiimote.py)
# and pybluez
class SensorWiimote(Sensor):
    def __init__(self, btaddr):
        Sensor.__init__(self)
        self._btaddr = btaddr
        self._connect()

    def _connect(self):
        import wiimote

        self._wiimote = wiimote.connect(self._btaddr)
        self._connection_thread = Thread(target=self._receive)
        self._connection_thread.start()

    def _receive(self):
        self._receiving = True
        buttons = self._wiimote.buttons.BUTTONS.keys()
        while self._receiving:
            x = self._wiimote.accelerometer[0]
            y = self._wiimote.accelerometer[1]
            z = self._wiimote.accelerometer[2]
            data_string = f'{{"x":{x},"y":{y},"z":{z}}}'
            self._update("accelerometer", data_string)

            for button in buttons:
                state = int(self._wiimote.buttons[button])
                self._update(f"button_" + button.lower(), state)
            time.sleep(0.001)

    def _update(self, key, value):
        self._add_capability(key)

        # do not notify callbacks on initialization
        if self._data[key] == []:
            self._data[key] = value
            return

        # notify callbacks only if data has changed
        if self._data[key] != value:
            self._data[key] = value
            self._notify_callbacks(key)


# close the program softly when ctrl+c is pressed
def handle_interrupt_signal(signal, frame):
    for sensor in Sensor.instances:
        sensor.disconnect()
        sys.exit(0)


signal.signal(signal.SIGINT, handle_interrupt_signal)
