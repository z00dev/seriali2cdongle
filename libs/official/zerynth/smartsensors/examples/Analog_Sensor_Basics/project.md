Basic Analog Sensor 
=======================

The smartSensors library is a ready to use set of functions that are very useful for managing analog and digital sensors.
Common operations like calculating min, max, average and trends are completely automated by the smartSensors library.
Moreover the smartSensors lib allows user to define calibration functions for analog sensors and to use callback to schedule sampling and acquisition operations.

This examples shows the basic use of the analogSensor module of the smartSensors library.
In the example ADC4 is used for instancing an analogSensors running the automatic calculation of min, Max, average, trend and derivative.
Calculated data are printed on the console through a function that is called by the library every-time a new sample is acquired.

The sampling rate and the parameter calculation window size (expressed in samples) are set through the startSampling function integrated n the library that automates the entire acquisition and calculation process.

tags: [Smart Sensors Lib, analogSensors]
groups:[Smart Sensors Library]