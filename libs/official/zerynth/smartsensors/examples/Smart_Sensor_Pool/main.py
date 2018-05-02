################################################################################
# Smart Sensor Pool
#
# Created by Zerynth Team 2015 CC
# Authors: L. Rizzello, G. Baldi,  D. Mazzei
###############################################################################

import streams

# import analogSensors, digitalSensors and sensorPool modules
from smartsensors import analogSensors
from smartsensors import digitalSensors
from smartsensors import sensorPool   

# define two functions that take a sensor object as parameter and print its
# last read value

def outA(obj):
    print("a: ",obj.currentSample())

def outD(obj):
    print("d: ",obj.currentSample())

# define a function that takes a value and a sensor object as parameters and
# returns a 'normalized' version of the value
def normA(val,obj):
    return val//100
    
streams.serial()

# initialize an analog and a digital sensor on pins A4 and D7
a = analogSensors.AnalogSensor(A4)
d = digitalSensors.DigitalSensor(D7)   

# set a normalization function 'normA' to sensor 'a' to normalize every acquired
# sample and 'outA' as the function to be executed every time a new sample is read
a.setNormFunc(normA).doEverySample(outA)

# set 'outD' as the function to be executed every time a new sample is read by
# sensor 'd'
d.doEverySample(outD)

# initialize a sensorPool object that contains 'a' and 'd' sensors
pool = sensorPool.SensorPool([a,d])

# start sampling process for the objects in the pool specifying different
# sampling parameters:
#
#           sampling time | window size | type of acquisition
#  object a     1000      |    None     |       normalized
#  object b     2000      |    None     |          raw
# 
# window size is set to None because window parameters (moving average,trend...)
# are not needed in this example
pool.startSampling([1000,2000],[None,None],["norm","raw"])