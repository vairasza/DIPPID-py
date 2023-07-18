from DIPPID import SensorUDP, M5_CAPA, Mapping, T_Data

# use UPD (via WiFi) for communication
PORT = 5700
sensor = SensorUDP(PORT)


# Example for M5 Stack


def callback(data: T_Data):
    if M5_CAPA.BUTTON_1.value in data:
        if data["button_1"]["pressed"] == 0:
            print("button released")
        else:
            print("button pressed")

    elif M5_CAPA.ROTATION.value in data:
        # read values from data
        print("rotation pitch angle: ", data["rotation"]["pitch"])
        print("rotation pitch last update: ", data["rotation"]["last_update"])


mapping = Mapping()
mapping.key = "test"
mapping.capabilites = [M5_CAPA.BUTTON_1, M5_CAPA.ROTATION, M5_CAPA.TEMPERATURE]
mapping.func = callback

success = sensor.register_callback(mapping)
print(f"registering callback function worked: {success}")

success = sensor.register_callback(mapping)
print(
    f"registering callback function worked: {success}"
)  # key already exists => function not added

success = sensor.unregister_callback(mapping)
print(
    f"unregistering callback function worked: {success}"
)  # key already exists => function not added
