################################################################################
# Zerynth Shield Sensor Pool
#
# Created by Zerynth Team 2015 CC
# Authors: L. Rizzello, G. Baldi,  D. Mazzei
###############################################################################

import streams
from zerynthshield import zerynthshield
from smartsensors import sensorPool

# see Pool Example for sensorPool details

def out_l(obj):
    print("light: ",obj.currentSample())

def out_t(obj):
    print("temperature: ",obj.currentSample())
    
streams.serial()
zerynthshield.light.doEverySample(out_l)  

# to be noticed the use of a preset normalization function 'zerynthshield.toCelsius'
# included in the zerynthshield module
zerynthshield.temperature.setNormFunc(zerynthshield.toCelsius).doEverySample(out_t)
pool = sensorPool.SensorPool([zerynthshield.light,zerynthshield.temperature])
pool.startSampling([1000,1000],[None,None],["raw","norm"])