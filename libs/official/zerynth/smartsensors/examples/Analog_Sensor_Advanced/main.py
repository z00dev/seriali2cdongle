################################################################################
# Advanced Analog Sensor for SmartSensor Lib
#
# Created by Zerynth Team 2015 CC
# Authors: L. Rizzello, G. Baldi,  D. Mazzei
###############################################################################

import streams
# import analogSensors and sensorPool
from smartsensors import analogSensors
from smartsensors import sensorPool

# define a function that takes a sensor object as parameter and prints its last
# read sample and the current moving average
def out(obj):
    print("current sample: ",obj.currentSample())
    print("average: ",obj.currentAverage)
    
# define a 'condition' function that takes a sensor object as parameter 
# and returns True if its current derivative is not None and 
# greater than a fixed threshold
def derivativeOfAverageGreaterThanTh(obj):
    if type(obj.currentDerivative) == PNONE:
        return False
    return (obj.currentDerivative > 10)

# define a function that simply prints a message
def gOut(obj):
    print("derivative of average over threshold!")


streams.serial()
# initialize an AnalogSensor object on pin A4 and set 'out' as the function to be
# applied to every acquired sample
a = analogSensors.AnalogSensor(A4)
a.highPrecision = True
a.doEverySample(out)

# initialize an AnalogSensor object on currentAverage of 'a' sensor
# a_avg sensor allows to easily monitor 'a' currentAverage but also to handle new
# parameters like its min a max value and derivative for example.
# set detrivativeOfAverageGreaterThanTh function as a condition to be checked and to
# be verified to execute gOut function every time a new sample is acquired by the 'sensor
# of the sensor'
a_avg = analogSensors.AnalogSensor((a,"currentAverage"))   #this is a new sensor that takes as input the average of the a sensor
a_avg.addCheck(derivativeOfAverageGreaterThanTh,gOut)

# to start sampling both sensors are put in a pool, see Pool Example for details
pool = sensorPool.SensorPool([a,a_avg])
pool.startSampling([1000,1000],[5,5],["raw","raw"])