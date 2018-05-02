Smoothing Analog Data with Moving Average
==========================================
The smartSensors library is a ready to use set of functions that are very useful for managing analog and digital sensors.
Common operations like calculating min, max, average and trends are completely automated by the smartSensors library.
Moreover the smartSensors lib allows user to define calibration functions for analog sensors and to use callback to schedule sampling and acquisition operations.

In this example the average method is used for smoothing analogical data acquired through the ADC running a moving average filter.
Note that at program starts the average results "None" because the filter window is not yet completely filled and the library verify it avoiding to results wrong data calculation. This feature is very useful in programs where the sampling and analysis routine is stopped and restarted periodically avoiding wrong calculation due to inconsistent incoming data.

tags: [Smart Sensors Lib, analogSensors, Zerynth Shield, sensorPool]
groups:[Smart Sensors Library, Zerynth Shield Driver]


