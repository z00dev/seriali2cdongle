################################################################################
# bluefruit serial
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
    ble.init(SPI0,D8,D7)
    # initialize BLE
    # pass the spi driver, the chip select pin and the irqpin
    # if you are using a Bluefruit shield, the following parameters should be correct.
    # If you are using a Bluefruit breakout, set them to your wiring

    # do a factory reset, to start fresh
    ble.hard_reset()

    # create a BLE stream instance
    blestream = ble.BLEStream()

    while True:
        # check if some client connected to using
        # otherwise the stream is not usable!
        if ble.gap_is_connected():
            # print some connection info
            print("Connection",ble.addr()," <-> ",ble.peer_addr(),"with RSSI",str(ble.rssi()))
            # send by BLE
            print("Hello BLE! Tell me something...",stream=blestream)
            # receive from BLE
            print("answer:",blestream.readline())
        else:
            print("waiting for connection")
        sleep(1000)

    # you can test the serial over ble with the following app:
    # Android: https://play.google.com/store/apps/details?id=no.nordicsemi.android.nrftoolbox&hl=en
    # iOS: https://itunes.apple.com/us/app/nrf-toolbox/id820906058?mt=8

except Exception as e:
    print(e)