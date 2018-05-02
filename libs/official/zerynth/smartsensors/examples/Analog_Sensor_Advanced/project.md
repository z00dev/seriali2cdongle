Advanced Analog Sensor
======================

The smartSensors library is a ready to use set of functions that are very useful for managing analog and digital sensors.
Common operations like calculating min, max, average and trends are completely automated by the smartSensors library.
Moreover the smartSensors lib allows user to define calibration functions for analog sensors and to use callback to schedule sampling and acquisition operations.

This examples shows an advanced use of the analogSensor module where a sensor is created attaching it to and ADC and another virtual sensor is created attaching in to the "average" output of the first analog sensor. 
In the example ADC4 is used for instancing an analogSensors running the automatic calculation of min, Max, average, trend and derivative.
Calculated data are printed on the console through a function.
Moreover another sensor is created taking as input the "average" calculated by the first "real" sensor. This trick is used to calculate the Derivative of the average monitoring it through another function in order to notify the user is the derivative of the average is passing a threshold.

In the example the sensorPool module is also used. please refer to the sensorPoll example and documentation for more details.

This example can be used as starting point for very complex analogical data analysis routine where the monitoring of multiple variables is required at different sample rates and with different configurations 

tags: [Smart Sensors Lib, analogSensors]
groups:[Smart Sensors Library]


