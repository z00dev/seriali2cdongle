################################################################################
# Find and Set Baud Example
#
# Created: 2018-02-08 16:44:15.135468
# Author: M. Cipriani
################################################################################

import streams
from stm.spwf01sa import spwf01sa as wifi_driver

streams.serial()
print("scanning serial bauds")

# This setup is referred to spwf01sa mounted on Wi-Fi 4 Click in slot A of a Flip n Click device 

#DEFINES
ser = SERIAL1    # serial of the spwf01sa
rst = D16        # reset pin of the spwf01sa
tobaud = 9600    # baud rate to be set
end = False

def waiting():
    while True:
        if not end:
            print(".")
        sleep(1000)

thread(waiting)

try:
    baud = wifi_driver.get_baud(ser, rst)
    print("found baud", baud)
    
    if baud != tobaud:
        wifi_driver.set_baud(ser, rst, baud, tobaud)
        print("baud set to", tobaud)
    else:
        print("baud already set to", baud)
    end = True
except Exception as e:
    print(e)