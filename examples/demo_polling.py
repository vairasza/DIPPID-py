from time import sleep

from DIPPID import SensorUDP, M5_CAPA

# use UPD (via WiFi) for communication
PORT = 5700
sensor = SensorUDP(PORT)

example_counter = 0
example_counter_end = 10

# Example 1 for M5 Stack for one capability

while True:
    # print all capabilities of the sensor
    print("capabilities: ", sensor.get_capabilities())

    # check if the sensor has the 'accelerometer' capability
    if sensor.has_capabilities([M5_CAPA.ACCELEROMETER]):
        data = sensor.get_value([M5_CAPA.ACCELEROMETER])

        # print whole accelerometer object (dictionary)
        # values from dictionary can be autocompleted with intellisense
        print("accelerometer data: ", data["accelerometer"])

        # print only one accelerometer axis
        print("accelerometer X: ", data["accelerometer"]["x"])

    sleep(0.1)
    example_counter += 1
    if example_counter == example_counter_end:
        example_counter = 0
        break

# Example 2 for M5 Stack for two capabilities

while True:
    # print all capabilities of the sensor
    print("capabilities: ", sensor.get_capabilities())

    # check if the sensor has the 'accelerometer' capability
    if sensor.has_capabilities([M5_CAPA.ACCELEROMETER, M5_CAPA.BUTTON_1]):
        data = sensor.get_value([M5_CAPA.ACCELEROMETER, M5_CAPA.BUTTON_1])

        # print whole accelerometer object (dictionary)
        print("accelerometer data: ", data["accelerometer"])

        # print only one accelerometer axis
        print("accelerometer X: ", data["accelerometer"]["x"])

        print("accelerometer last update: ", data["accelerometer"]["last_update"])

        print("button_1 value: ", data["button_1"]["pressed"])

        print("button_1 last update: ", data["button_1"]["last_update"])

    sleep(0.1)
    example_counter += 1
    if example_counter == example_counter_end:
        break
