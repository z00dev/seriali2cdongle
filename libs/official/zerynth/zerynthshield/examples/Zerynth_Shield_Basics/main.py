
################################################################################
# Zerynth Shield basic
#
# Created by Zerynth Team 2015 CC
# Authors: L. Rizzello, G. Baldi,  D. Mazzei
###############################################################################

import streams
import adc
from zerynthshield import zerynthshield

streams.serial()

# zerynthshield defines pin names in a device indipendent manner
# let's use them to read raw sensors values

while True:
    print(" Microphone:",adc.read(zerynthshield.microphone_pin))
    print("      Light:",adc.read(zerynthshield.light_pin))
    print("Temperature:",adc.read(zerynthshield.temperature_pin))
    print("      Touch:",digitalRead(zerynthshield.touch_pin))
    # aux pins are also accessible!
    print("       AUX1:",adc.read(zerynthshield.aux1.ADC))
    print("-"*40)
    sleep(500)
    
# this scripts runs on every supported device, without a single change...cool isn't it? :)