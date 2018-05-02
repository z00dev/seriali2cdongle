################################################################################
# Draw a fading image Example
#
# Created: 2017-08-28 11:26:15.598712
#
################################################################################

import streams
streams.serial()

print("import")
sleep(1000)

from solomon.ssd1306 import ssd1306

print("start")
sleep(1000)

import zLogo

try:
    # Setup display 
    # This setup is referred to ssd1306 mounted on slot A of a Flip n Click device
    ssd = ssd1306.SSD1306(SPI0,D17,D16,D6)
    ssd.init()
    ssd.on()
    ssd.clear()
    
    #draw zlogo
    ssd.draw_img(zLogo.zz,32,4,32,32)
except Exception as e:
    print("Error1", e)

while True:
    try:
        #fade the screen
        for i in range(0,256):
            ssd.set_contrast(i)
            sleep(2)
        for i in range(0,256):
            ssd.set_contrast(255-i)
            sleep(2)
    except Exception as e:
        print(e)