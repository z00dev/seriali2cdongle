"""
.. module:: ds1307

*************
DS1307 Module
*************

This module implements the Zerynth driver for the Maxim DS1307 RTC (`datasheet <https://datasheets.maximintegrated.com/en/ds/DS1307.pdf>`_).

Using the module is simple::

    from maxim.ds1307 import ds1307
    import streams
    streams.serial()
    
    ds = ds1307.DS1307(I2C0)
    ds.start()
    
    while True:
        print("%02d:%02d:%02d - %02d/%02d/%d - %d"%ds.get_time())
        sleep(1000)

    """

import i2c

class DS1307(i2c.I2C):
    """
============
DS1307 class
============

.. class:: DS1307(drvname)

        Creates a DS1307 instance using the MCU I2C circuitry *drvname* (one of I2C0, I2C1, ... check pinmap for details). 
        The created instance is configured and ready to communicate.

        DS1307 inherits from i2c.I2C, therefore the method start() must be called to setup the I2C channel
        before the RTC can be used.

    """
    def __init__(self,drvname):
        i2c.I2C.__init__(self,drvname,0x68,100000)
    
    def get_time(self):
        """
.. method:: get_time()
        
        Returns a tuple *(hours,minutes,seconds,day,month,year,day_of_week)* with the current time and date readings.
        
        Current time is always expressed in the 24 hours format.
        
        The time and date readings conversion algorithm assumes that the DS1307 has been previously configured with a call to set_time().
        
        """
        
        rr = self.write_read(0x00,7)
        ss = (rr[0]&0x0f) + ((rr[0]&0x70)>>4)*10
        mm = (rr[1]&0x0f) + ((rr[1]&0x70)>>4)*10
        hh = (rr[2]&0x0f)
        if rr[2]&0x40: #12 hours mode
            hh+=((rr[2]&0x10)>>4)*10 + 12*(rr[2]&0x20)
        else: #24 hours mode
            hh+=((rr[2]&0x30)>>4)*10
        dn = rr[3]&0x07
        dd = (rr[4]&0x0f) + ((rr[4]&0x30)>>4)*10
        mt = (rr[5]&0x0f) + ((rr[5]&0x10)>>4)*10
        yy = (rr[6]&0x0f) + ((rr[6]&0xf0)>>4)*10
        return (hh,mm,ss,dd,mt,yy+2000,dn)


    def set_time(self,hours,minutes,seconds,day,month,year,day_of_week):
        """
.. method:: set_time(hours,minutes,seconds,day,month,year,day_of_week)
        
        Configures the DS1307 with time *hours:minutes:seconds* expressed in 24 hours format.
        The value of *year* must be greater or equal than 2000 and *day_of_week* must be in range 1 to 7 included.
        
        """
        bb = bytearray(8)
        bb[0]=0
        bb[1]=(seconds%10)|(((seconds//10)<<4)&0x70)
        bb[2]=(minutes%10)|(((minutes//10)<<4)&0x70)
        bb[3]=(hours%10)|(((hours//10)<<4)&0x30) # 24 hours mode
        bb[4]=day_of_week&0x07
        bb[5]=(day%10)|(((day//10)<<4)&0x30)
        bb[6]=(month%10)|(((month//10)<<4)&0x10)
        year=year-2000
        bb[7]=(year%10)|(((year//10)<<4)&0xf0)
        self.write(bb)
