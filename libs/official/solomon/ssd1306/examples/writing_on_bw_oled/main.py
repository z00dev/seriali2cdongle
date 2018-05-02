################################################################################
# Print string on bw oled display Example
#
# Created: 2017-08-28 12:21:52.459874
#
################################################################################

import streams
streams.serial()

print("import")
sleep(1000)

from solomon.ssd1306 import ssd1306

print("start")
sleep(1000)

try:
    # Setup display 
    # This setup is referred to ssd1306 mounted on slot A of a Flip n Click device
    ssd = ssd1306.SSD1306(SPI0,D17,D16,D6)
    ssd.init()
    ssd.on()
except Exception as e:
    print("Error1", e)

while True:
    try:
        ssd.clear()
        sleep(1000)
        count = 0
        for i in [3,2,1]:
            ssd.draw_text("Zerynth",0,14*count,96,12, align=i)
            sleep(1000)
            count += 1
        ssd.fill_screen()
        sleep(1000)
        count = 0
        for i in [1,2,3]:
            ssd.draw_text("Hello Zerynth",0,14*count,96,12, align=i, fill=False)
            sleep(1000)
            count += 1
        ssd.invert()
        sleep(1000)
        ssd.normal()
        sleep(1000)
    except Exception as e:
        print(e)