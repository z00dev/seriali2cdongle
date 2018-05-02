################################################################################
# IR Capture, Decode and Send
#
# Created by Zerynth Team 2015 CC
# Authors: D. Mazzei, G. Baldi,  
###############################################################################

import streams
from infrared import infrared

s=streams.serial()

#create an instance of the IR receiver class passing it the pin where the IR demodulator is connected specifiying the ICU feature
receiver = infrared.IRReceiver(D2.ICU)

#Create a IR packet sender specifying the pin where the IR LED is connected specifying the PWM feature 
sender = infrared.IRSender(D6.PWM)                

while True:
    print("Capturing...")
    packet=receiver.captureAndDecode()
    packet.printPacket(s)
    print("Wait 3 secs before sending the captured packet")
    sleep(3000)
    for i in range(3):
        print("Sending...", i)
        sender.send(packet)
        sleep(1500)
    
        
        