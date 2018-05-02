################################################################################
# Zerynth Shield IR Basic
#
# Created: 2015-07-26 18:36:22.346367
#
################################################################################

import streams
from zerynthshield import zerynthshield

streams.serial()
while True:
    print("Capturing...")
    # starts capturing from the zerynthshield IR receiver setting max_samples
    # number of samples (a sample represents the interval in microseconds
    # passed between a change from a LOW to a HIGH value on the pin or
    # viceversa) to be acquired and a maximum time window of time_window ms.
    # Values chosen for this example come from NEC IR ( used by LG )
    # specification.
    max_samples, time_window = 67,68
    x = zerynthshield.irreceiver.capture(max_samples,time_window)
    print("Captured:",len(x),"samples\n", x)