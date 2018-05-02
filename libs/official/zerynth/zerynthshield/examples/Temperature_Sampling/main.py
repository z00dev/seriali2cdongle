################################################################################
# Temperature Sampling
#
# Created by Zerynth Team 2015 CC
# Authors: L. Rizzello, G. Baldi,  D. Mazzei
###############################################################################

# This example is based on the Basic Analog Sensor example of the Smart Sensor Library

import streams
from zerynthshield import zerynthshield

def out(obj):
    print("----------------")
    print("last 10 minutes:")
    print("max temperature: ",obj.maxSample)
    print("min temperature: ",obj.minSample)
    print("average temperature: ",obj.currentAverage)   

streams.serial()

zerynthshield.temperature.doEverySample(out)
zerynthshield.temperature.setNormFunc(zerynthshield.toCelsius)
zerynthshield.temperature.startSampling(30000,20,"norm")
