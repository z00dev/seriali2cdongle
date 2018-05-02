################################################################################
# bluefruit HRM
#
# Created: 2016-01-07 14:11:04.262350
#
################################################################################

import streams
# import the bluefruit driver
from adafruit.bluefruit import bluefruit as ble

streams.serial()


try:
    print("initializing...")
    # initialize BLE
    # pass the spi driver, the chip select pin and the irqpin
    # if you are using a Bluefruit shield, the following parameters should be correct.
    # If you are using a Bluefruit breakout, set them to your wiring

    ble.init(SPI0,D8,D7)

    # do a factory reset, to start fresh
    ble.hard_reset()
    # set the advertised name
    ble.gap_name("Zerynth HRM")

    # prepare a configuration
    # by specifying the service(s)
    # and the corresponding characteristics
    srv = [
        [0,0x180D],
            [0,0x2a37,(0x00,0x40),0x10],
            [0,0x2a38,3,0x02]
    ]
    # set cfg as active
    ble.gatt(srv)
    # set advertising parameters
    ble.gap_adv([0x02,0x01,0x06,0x05,0x02,0x0d,0x18,0x0a,0x18])


    while True:
        sleep(1000)
        # set a random heart rate
        # by using returned handle
        ble.gatt_set(srv[1][0],random(40,150))

    # you can inspect the HRM value with the following app:
    # Android: https://play.google.com/store/apps/details?id=no.nordicsemi.android.nrftoolbox&hl=en
    # iOS: https://itunes.apple.com/us/app/nrf-toolbox/id820906058?mt=8

except Exception as e:
    print(e)