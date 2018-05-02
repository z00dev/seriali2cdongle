###############################################################################
# Smoothing
#
# Created by Zerynth Team 2015 CC
# Authors: L. Rizzello, G. Baldi,  D. Mazzei
###############################################################################

import streams

# import analogSensors module
from smartsensors import analogSensors

# define a function that takes a sensor object as parameter and prints
# its moving average automatically evaluated
def out(obj):
    print(obj.currentAverage)

streams.serial()
# initialize an analogSensor object on pin A4
s = analogSensors.AnalogSensor(A4)
# set highPrecision to True to evaluate the moving average more precisely
s.highPrecision = True
# set out function as a function to be executed every time a new sample
# is acquired by the sensor
s.doEverySample(out)
# start sampling at 1000 millis with a window of 10 samples to evaluate
# window parameters
s.startSampling(1000,10)
