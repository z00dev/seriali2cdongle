################################################################################
# Servo Motor Basics
#
# Created by Zerynth Team 2015 CC
# Authors: D. Mazzei, G. Baldi,  
###############################################################################

from servo import servo
import streams

s=streams.serial()

# create a servo motor attaching it to the pin D11. D11.PWM notation must be used. 
# min max are left to defaults 500-2500. they need to be properly set to the servo specifications
# control signal period is left to default 20ms
MyServo=servo.Servo(D11.PWM)
  
    
while True:
    print("Servo ON")
    MyServo.attach()
    sleep(3000)
    
    print("Servo controlled in pulse width")
    for i in range (500,2500,10):
        MyServo.moveToPulseWidth(i)
        print(MyServo.getCurrentPulseWidth())
        # Very important: servo default control signal period is 20ms, don't update the controlling PWM faster than that!
        sleep (100) 
    
    print("Servo controlled in degrees")
    for i in range(0,180,1):
        # Very important: degree accuracy depends by the min max pulse width setup. Refer to the servo specifications for proper configuration
        MyServo.moveToDegree(i)
        print(MyServo.getCurrentDegree())
        sleep(100)
    
    print("servo OFF")
    MyServo.detach()
    sleep(3000)