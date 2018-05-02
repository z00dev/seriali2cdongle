"""

*************
DS1820 Module
*************

This module implements the class DS1820 to read OneWire temperature sensors DS18b20 and DS18s20 connected to a DS2482 I2C-OneWire bridge (`datasheet <http://pdfserv.maximintegrated.com/en/ds/DS18S20.pdf>`_). 

    """
from maxim.ds2482 import ds2482

class DS1820(ds2482.OneWireSensor):
    """

============
DS1820 class
=============

.. class:: DS1820(serial,ow)
        
        Creates a DS1820 instance using the OneWire bridge *ow* with OneWire serial id *serial*.

    """       

    def read(self):
        """
.. method:: read()

        Returns the temperature readings as float applying the correct conversion for different DS1820 models.
        If the serial is wrong, raises *UnsupportedError*.
        """
        if self.owbus.ow_match_rom(self.serial):
            self.owbus.ow_write(b'\x44') # convert temperature command
            sleep(750) # max tconv time
            self.owbus.ow_match_rom(self.serial)
            self.owbus.ow_write(b'\xbe') # read scratchpad command
            sp = self.owbus.ow_read(8)
            #print("%x %x"%(sp[0],sp[1]))
            if sum(sp)==0xff*8:
                # sensor disconnected
                raise InvalidHardwareStatusError
            if self.typeid == 0x28: # ds18b20
                if sp[1]&0xF0: #sign is 1, convert
                    t = (sp[1]<<8)+sp[0] # 16 bit 2-complement
                    t = -(0xffff-t+1)
                else:
                    t = sp[1] & 0x07; # read msb 3 bits
                    t = (t<<8)+sp[0]; # 11 bits of data
                return t*0.0625
            elif self.typeid == 0x10: #d18s20
                sgn = 1
                if sp[1]: # sign is 1, convert
                    t = (0xff-sp[0]+1)
                    sgn=-1
                else:
                    t = sp[0]
                return sgn*(t/2 - (0.25*(sp[7]-sp[6])/sp[7]))
            else:
                raise UnsupportedError
        return None

