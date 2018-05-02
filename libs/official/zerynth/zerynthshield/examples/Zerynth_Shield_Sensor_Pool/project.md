Shield Pool
===========
The smartSensors library is a ready to use set of functions that are very useful for managing analog and digital sensors.
Common operations like calculating min, max, average and trends are completely automated by the smartSensors library.
Moreover the smartSensors lib allows user to define calibration functions for analog sensors and to use callback to schedule sampling and acquisition operations.

In this example a sensor pool of analog sensors is created to acquire data from the Light and Temperature sensors of the Zerynth Shield. The examples shows how to set a calibration function for the temperature sensor while leaving raw the data coming from the light sensor.
Both normalized ans raw sensors are included in a sensorPool and the acquisition triggered simultaneously.

tags: [Smart Sensors Lib, analogSensors, Zerynth Shield, sensorPool]
groups:[Smart Sensors Library, Zerynth Shield Driver]    