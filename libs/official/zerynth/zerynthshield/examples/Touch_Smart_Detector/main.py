################################################################################
# Touch Smart Detector
#
# Created by Zerynth Team 2015 CC
# Authors: L. Rizzello, G. Baldi,  D. Mazzei
###############################################################################

import streams

# import zerynthshield module
from zerynthshield  import zerynthshield

# define three functions that print three different messages

def single():
    print("touch")
    
def double():
    print("double")
    
def loong():
    print("loong")
        
streams.serial()

# set 'single' as the function to be executed after the first touch of the Zerynth Shield
# touch sensor and 'double' after the second. To really execute these functions touch
# has to respect some time constraints: first touch must be of at least 50 milliseconds
# to be considered voluntary and must not be longer than 1500 milliseconds, furthermore
# not more than 1000 milliseconds shall pass between the first and second touch to consider
# two single touches a real double touch.
# The 'loong' function is executed if the 1500 milliseconds constraint is not respected.
zerynthshield.touch.onDoubleTouch(50,1500,1000,single,double,loong)
