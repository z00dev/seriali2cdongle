################################################################################
# WS2812 LED Strips Advanced
#
# Created by Zerynth Team 2015 CC
# Authors: G. Baldi, D. Mazzei
################################################################################

import threading
from worldsemi.ws2812 import ledstrips as pixel

# create all the needed layers
leds = pixel.LedStrip(D6,16)
layer0 = pixel.LedStrip(D6,16)
layer1 = pixel.LedStrip(D6,16)
layer2 = pixel.LedStrip(D6,16)

# fill layers with their initial values
leds.clear()
layer0[0]=(100,0,0)
layer0[1]=(100,0,0)
layer0[2]=(100,0,0)
layer1[0]=(0,100,0)
layer1[1]=(0,100,0)
layer1[2]=(0,100,0)    
layer2.clear()

# let's define some coefficients for smooth animation (half a sinus wave)
animation_coefficients = [
    0,
    0.2588190451,
    0.5,
    0.7071067812,
    0.8660254038,
    0.9659258263,
    1,
    0.9659258263,
    0.8660254038,
    0.7071067812,
    0.5,
    0.2588190451]

# A Lock is needed to prevent conflicts between threads
lock = threading.Lock()

# Create a function to handle background animation
def animate_background(delay):
    step=0
    while True:
        lock.acquire()
        layer2.setall(0,0,int(50*animation_coefficients[step]))
        lock.release()
        step += 1
        if step >= len(animation_coefficients):
            step=0
        sleep(delay)

def animate_foreground(delay):
    while True:
        lock.acquire()
        layer0.lshift()
        layer1.rshift()
        lock.release()
        sleep(delay)

# start the background animation thread
thread(animate_background,500)
# start the foreground animation thread
thread(animate_foreground,50)


while True:
    # clear leds
    leds.clear()
    # now, acquire the lock
    lock.acquire()
    # merge the first and second layer
    leds.merge(layer0)
    leds.merge(layer1)
    # merge the background layer only where leds is transparent (0,0,0) 
    leds.merge(layer2,pixel.first_color)
    # release the lock
    lock.release()
    # and light it up!
    leds.on()
    sleep(10)
    