"""
.. module:: tmp112

*************
TMP112 Module 
*************

The TMP112 is device is a digital temperature sensor with high accuracy from Texas Instrument (`datasheet <http://www.ti.com/lit/ds/symlink/tmp112.pdf>`_).

The default communication protocol is I2C. To use this module create a TMP112 instance by passing the I2C peripheral name to which it is connected to. Using the module is simple::

    from texas.tmp112 import tmp112
    import streams
    streams.serial()
    tmp = tmp112.TMP112(I2C0)
    while True:
        print("Temperature:",tmp.temperature())
        sleep(1000)

    """

import i2c

class TMP112(i2c.I2C):
    """
============
TMP112 class
============

.. class:: TMP112(drvname,clock=100000,addr=0x49)

        Creates a TMP112 instance using the MCU I2C circuitry *drvname* (one of I2C0, I2C1, ... check pinmap for details). 
        The created instance is configured and ready to communicate. 
        *clock* is configured by default in slow mode.

        TMP112 inherits from i2c.I2C, therefore the method start() must be called to setup the I2C channel
        before any temperature can be read.

        The TMP112 can have 4 different I2C addresses determined by the wiring:

            * A0 connected to GND: 0x48
            * A0 connected to Vdd: 0x49
            * A0 connected to SDA: 0x4A
            * A0 connected to SCL: 0x4B

    """
    def __init__(self,drvname,addr=0x49):
        i2c.I2C.__init__(self,drvname,addr,100000)

    def temperature(self):
        """
.. method:: temperature()
        
        Returns the object temperature in Celsius.
        
        """
        rx=self.write_read(0x00,2)
        tmp = (rx[0]<<4)|(rx[1]>>4)
        if tmp>=0x800:
            tmp-=0x0FFF+1
        return 0.0625*tmp