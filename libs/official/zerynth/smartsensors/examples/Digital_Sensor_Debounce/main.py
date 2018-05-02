################################################################################
# Debounce Digital Sensor Input
#
# Created by Zerynth Team 2015 CC
# Authors: L. Rizzello, G. Baldi,  D. Mazzei
###############################################################################

import streams 

# import digitalSensors module
from smartsensors import digitalSensors

# set a state variable to 0
state = 0

# define a function that changes the value of state global variable from 0 to 1
# or from 1 to 0 and prints the new state value
def changeState():
    global state
    state = state^1
    print("new state: ",state)

streams.serial()  
# initialize a digitalSensor object on pin D7

d = digitalSensors.DigitalSensor(D7)

# set changeState as the function to be executed when the value of the pin changes
# from 0 to 1 ( onRise ) and again from 1 to 0 ( andFall ) respecting the time
# constraint: the value must stay HIGH at least 500 milliseconds (make sure the
# transition is voluntary) and less than 2000 milliseconds
d.onRiseAndFall(500,2000,changeState)
