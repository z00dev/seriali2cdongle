################################################################################
# Basic Analog Sensor for SmartSensor Lib
#
# Created by Zerynth Team 2015 CC
# Authors: L. Rizzello, G. Baldi,  D. Mazzei
###############################################################################

import streams
# import analogSensors module 
from smartsensors import analogSensors

# define a function that takes a sensor object as parameter and prints
# the last read sample and all the window parameters
def out(obj):
    print("read sample: ",obj.currentSample())
    print("average: ",obj.currentAverage)
    print("min: ",obj.minSample)
    print("max: ",obj.maxSample)
    print("trend: ",obj.currentTrend)
    print("derivative: ",obj.currentDerivative)
    
# define a 'condition' function that takes a sensor object as parameter 
# and returns True if its current moving average is not None and 
# greater than a fixed threshold
def averageGreaterThanTh(obj):
    if not obj.currentAverage:
        return False
    return (obj.currentAverage > 2000)

# define a function that simply prints a message
def gOut(obj):
    print("average over threshold")

streams.serial()
# initialize an AnalogSensor object on pin A4
a = analogSensors.AnalogSensor(A4)
# set out function as a function to be executed every time a new sample
# is acquired by the sensor
# set averageGreaterThanTh function as a condition to be checked and to
# be verified to execute gOut function every time a new sample is
# acquired by the sensor
a.doEverySample(out).addCheck(averageGreaterThanTh,gOut)
# start sampling at 1000 millis with a window of 4 samples to evaluate
# window parameters
a.startSampling(1000,4)
