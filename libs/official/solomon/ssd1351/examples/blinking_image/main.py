################################################################################
# Draw a blinking image Example
#
# Created: 2017-03-10 15:12:44.433654
#
################################################################################

import streams
streams.serial()

print("import")
sleep(1000)

from solomon.ssd1351 import ssd1351

print("start")
sleep(1000)

import zLogo

try:
    # Setup display 
    # This setup is referred to ssd1351 mounted on Hexiwear device 
    ssd = ssd1351.SSD1351(SPI0,D57,D58,D59,D71)
    ssd.init(96,96)
    ssd.on()
    ssd.fill_screen(color=0x4471, encode=False)
    
    #draw zlogo
    ssd.draw_img(zLogo.zz, 8,8,80,80)
except Exception as e:
    print("Error1", e)

while True:
    #blink the screen
    ssd.set_contrast(0)
    sleep(1000)
    ssd.set_contrast(255)
    sleep(1000)