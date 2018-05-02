################################################################################
# WS2812 LED Strips
#
# Created by Zerynth Team 2015 CC
# Authors: G. Baldi, D. Mazzei
################################################################################

# Be sure to open the serial console, otherwise the program will halt if the console buffer is full. 
import streams
from worldsemi.ws2812 import ledstrips as pixel
streams.serial()

num_leds = 16                     # adjust this to match the number of LEDs on your strip
led_pin = D9                      # this should match the data pin of the LED strip
switch_pin = D2                   # this should match the pin to which the button is connected

leds = pixel.LedStrip(led_pin, num_leds) # create a new WS2812 RGB LED strip composed of <num_leds> LEDs and connected to pin led_pin
leds.set_fading(100, 0, 0)        # create a fade effect that starts from red=100 and goes to RGB=0,0,0 
                                  # along all the available strip LEDs. This is a static setup of the LEDs
pos=0
  
def touch():    
    #function to be called when a button is touched  
    r = random(20, 100)    # choose a random colour for RED
    g = random(20, 100)    # choose a random colour for GREEN
    b = random(20, 100)    # choose a random colour for BLUE
    print(r, g, b)
    leds.set_fading(r, g, b, num_leds-1-pos) 


# attach a button to pin <switch_pin> and set an interrupt to call the touched function. The button should connect the pin to Vcc.
pinMode(switch_pin, INPUT_PULLDOWN)
onPinRise(switch_pin, touch)    
    
while True:
    leds.on()       # refresh the LEDs colour imposed by the animation
    leds.lshift()   # shift the LED colours of one position towards
    pos = (pos+1) % num_leds
    sleep(500)

