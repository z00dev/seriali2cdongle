Debounce Digital Sensor Input
==============================

The smartSensors library is a ready to use set of functions that are very useful for managing analog and digital sensors.
Common operations like calculating min, max, average and trends are completely automated by the smartSensors library.
Moreover the smartSensors lib allows user to define calibration functions for analog sensors and to use callback to schedule sampling and acquisition operations.

In this example the digitalSensors module is used to monitor a DIO and trigger a function only when a state change longer than 500 millisec is detected. This example is very useful for the design of user interfaces where button are included. In this case it is very common to have false detections due to noise or movements and also to have undesired double detection due to a longer press of the button that could be detected by the software as double click.

This example is very useful for improving the usability of the Zerynth Shield Touch sensor 

tags: [digitalSensors, Zerynth Shield, Touch, Button ]
groups:[Smart Sensors Library, Zerynth Shield Driver]  


