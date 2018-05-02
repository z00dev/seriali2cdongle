################################################################################
# CAN Communication Example
#
# Created: 2018-03-05 11:25:41.189984
#
################################################################################

from microchip.mcp2515 import mcp2515
import streams

streams.serial()
print("start...")
try:
    # This setup is referred to CAN SPI click mounted on flip n click device slot A 
    can = mcp2515.MCP2515(SPI0, D17, D16, clk=10000000)
    print("...done")
    print("init...")
    can.init(mcp2515.MCP_ANY, "500KBPS", "16MHZ")
    can.set_mode("NORMAL")
    print("...done")
    print("ready!")
    print("--------------------------------------------------------")
except Exception as e:
    print(e)
    sleep(1000) 

##################################################
# Copy and Paste transmitter.py/receiver.py here #
# To obtain the Transmitter/receiver code to be  #
# uploaded                                       #
##################################################