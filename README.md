# DIPPID-py

Python receiver for the "Data Interchange Protocol for Prototyping Input Devices".

# Sensor

## Instance Variables

`_capabilites`: contains list of CAPABILITES that can be requested from Sensor

`_callbacks`: dictionairy that maps a key with a mapping. a key must be unique, identifies the according mapping and allows multiple capabilites returned in a callback function with one key.

`_data`: contains data from M5Stack or Android Smartphone. Type is defined in T_Data

## Functions

`has_capability(key: CAPABILITIES) -> bool`: returns a boolean value indicating the exisitng of the CAPABILITES in `_capabilties`

`has_capabilities(self, keys: list[CAPABILITES]) -> bool`: returns a boolean value that indicates if keys is a subset of `_capabilties`

`get_capabilities() -> list[CAPABILITES]`: returns `_capabilties`

`get_value(self, keys: list[CAPABILITES]) -> T_Data`: returns T_Data but only keys that are passed in `keys`

`register_callback(self, mapping: Mapping) -> bool`: registers a new callback function. The `Mapping` class contains a unique key mapping a callback function to a list of CAPABILITES. The callback function is called when there is an update to a CAPABILITY that is part of the mapping. The callback function is reused for all CAPABILITES; data can be identified by there Enum name.

`unregister_callback(self, mapping: Mapping) -> bool`: unregisters a callback function. must pass the whole mapping.

## Types

`T_3D`: used for `accelerometer`,
`gyroscope`, `gravitiy`

`T_Rotation`: used for `rotation`

`T_Data`: contains CAPABILITES for M5 and Android

`rotation` and `temperature` are specific to M5 (see `M5_CAPABILITIES`)

`button_4` and `gravity` are specific to Android (see `ANDROID_CAPABILITIES`)

`Mapping`: contains a unique key, a list of CAPABILITES and a callback function

## Note

in some cases, the x-axis for acceleromter is inverted on M5 and Android.
