################################################################################
# Servo Motor Animation 
#
# Created by Zerynth Team 2015 CC
# Authors: D. Mazzei, G. Baldi,  
###############################################################################


from servo import servo
# WARNING! for this example to work the community floyd.animator must be installed!
from community.floyd.animator import animator
import streams

s=streams.serial()

# creates a list of points to be reached by the servo motor using tuples (position, millisecond)
# The first tuple has to be set with time=0: (desired_pos,0). This is the value from which the animation will start
# In this case servo motor positions in degrees are scheduled
pointList= [(0,0),(180,10000),(90,3000),(0,5000),(180,5000)] 

print("scheduled positions at times (ms):",pointList)

# create a servo motor attaching it to the pin D11. Specification of the PWM feature using the Zerynth pin mapping signature is required. 
# min max defaults in this case are selected for working with Hitech servomotors
MyServo=servo.Servo(D11.PWM,500,2500)

# create an animator that runs at 10Hz passing data to  MyServo.moveToDegree
# don't set too high frequency, 10-30 Hz are fine. The Servo is controlled with a period of 20ms, frequancy higher than 45Hz will block the motor! 
anim=animator.Animator(25,MyServo.moveToDegree)

# start the animations using the defined point list
anim.animate(pointList)
    
while True:
#just print the animator position and interpolated value
    print(anim.currentPosition())
    sleep(500)