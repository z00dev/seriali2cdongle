"""
.. module:: mpl3115a2

****************
MPL3115A2 Module
****************

This module contains the driver for NXP MPL3115A2 Pressure, Altitude and Temperature sensor.

The MPL3115A2 is capable of direct I2C communication; the pressure and temperature data is fed into
a high resolution ADC to provide fully compensated and digitized outputs for pressure
in Pascals and temperature in °C.

The compensated pressure output can then be
converted to altitude (utilizing the formula stated in Section 8.1.3 "Pressure/altitude" of the `datasheet <http://www.nxp.com/assets/documents/data/en/data-sheets/MPL3115A2.pdf>`_ or putting the sensor in altimeter operating mode)
provided in meters.
    """

import i2c

MPL_I2C_ADDRESS  = 0x60

MPL_OS_SHIFT = 3
MPL_OS_MASK  = 0x7 << MPL_OS_SHIFT

REG_STATUS      = 0x00
OUT_P_MSB       = 0x01
OUT_P_CSB       = 0x02
OUT_P_LSB       = 0x03
OUT_T_MSB       = 0x04
OUT_T_LSB       = 0x05
DR_STATUS       = 0x06
OUT_P_DELTA_MSB = 0x07
OUT_P_DELTA_CSB = 0x08
OUT_P_DELTA_LSB = 0x09
OUT_T_DELTA_MSB = 0x0A
OUT_T_DELTA_LSB = 0x0B
WHO_AM_I        = 0x0C
F_STATUS        = 0x0D
F_DATA          = 0x0E
F_SETUP         = 0x0F
TIME_DLY        = 0x10
SYSMOD          = 0x11
INT_SOURCE      = 0x12
PT_DATA_CFG     = 0x13
BAR_IN_MSB      = 0x14
BAR_IN_LSB      = 0x15
P_TGT_MSB       = 0x16
P_TGT_LSB       = 0x17
T_TGT           = 0x18
P_WND_MSB       = 0x19
P_WND_LSB       = 0x1A
T_WND           = 0x1B
P_MIN_MSB       = 0x1C
P_MIN_CSB       = 0x1D
P_MIN_LSB       = 0x1E
T_MIN_MSB       = 0x1F
T_MIN_LSB       = 0x20
P_MAX_MSB       = 0x21
P_MAX_CSB       = 0x22
P_MAX_LSB       = 0x23
T_MAX_MSB       = 0x24
T_MAX_LSB       = 0x25
MPL_CTRL_REG1   = 0x26
MPL_CTRL_REG2   = 0x27
MPL_CTRL_REG3   = 0x28
MPL_CTRL_REG4   = 0x29
MPL_CTRL_REG5   = 0x2A
OFF_P           = 0x2B
OFF_T           = 0x2C
OFF_H           = 0x2D

#shifts
MPL_TDR_SHIFT  = 1
MPL_PDR_SHIFT  = 2
MPL_PTDR_SHIFT = 3

MPL_SBYB_SHIFT = 0
MPL_OST_SHIFT  = 1
MPL_RST_SHIFT  = 2

#modes
MPL_MODE_PRESSURE    = 0
MPL_MODE_ALTITUDE    = 1
MPL_MODE_TEMPERATURE = 2

class MPL3115A2(i2c.I2C):
    """

.. class:: MPL3115A2(i2cdrv, addr=0x60, clk=400000)

    Creates an intance of a new MPL3115A2.

    :param i2cdrv: I2C Bus used '( I2C0, ... )'
    :param addr: Slave address, default 0x60
    :param clk: Clock speed, default 400kHz

    Example: ::

        from nxp.mpl3115a2 import mpl3115a2

        ...

        mpl = mpl3115a2.MPL3115A2(I2C0)
        mpl.start()
        mpl.init()
        alt = mpl.get_alt()
        pres = mpl.get_pres()

    """

    #Init
    def __init__(self, i2cdrv, addr=MPL_I2C_ADDRESS, clk=400000):
        i2c.I2C.__init__(self,i2cdrv,addr,clk)
        self._addr = addr
        

    def init(self, osr=0):
        """

.. method:: init(osr=0)

        Initialize the MPL3115A2 setting the oversample rate value.

        :param osr: set the oversample rate value (from 0 to 7), default 0

========= ================ ==========
OSR Value Oversample Ratio Data Ready
========= ================ ==========
0         1                6 ms             
1         2                10 ms              
2         4                18 ms      
3         8                34 ms               
4         16               66 ms     
5         32               130 ms     
6         64               258 ms    
7         128              512 ms 
========= ================ ==========

        """
        self.mode = None
        self._standby()
        self._set_mode(MPL_MODE_PRESSURE)
        self._set_oversample_rate(osr)
        self._enable_event_flag()
        self._active()


    def _standby(self):
        ctrl = self.write_read(MPL_CTRL_REG1,1)[0]
        ctrl = ctrl & ~(1 << MPL_SBYB_SHIFT)
        self.write_bytes(MPL_CTRL_REG1, ctrl)
    
    def _active(self):
        ctrl = self.write_read(MPL_CTRL_REG1,1)[0]
        ctrl = ctrl | (1 << MPL_SBYB_SHIFT)
        self.write_bytes(MPL_CTRL_REG1, ctrl)
    
    def _set_mode(self, mode):
        ctrl = self.write_read(MPL_CTRL_REG1,1)[0]
        if mode > 0:
            ctrl = ctrl | (1 <<7)
        else:
            ctrl = ctrl & ~(1 << 7)
        self.write_bytes(MPL_CTRL_REG1, ctrl)
        self.mode = mode
    
    def _set_oversample_rate(self, osr):
        if osr < 0:
            osr = 0
        elif osr > 7:
            osr = 7
        ctrl = self.write_read(MPL_CTRL_REG1,1)[0]
        ctrl = ctrl & ~(MPL_OS_MASK)
        ctrl = ctrl | (osr << MPL_OS_SHIFT)
        self.write_bytes(MPL_CTRL_REG1, ctrl)
    
    def _enable_event_flag(self, flag):
        self.write_bytes(PT_DATA_CFG, 0x07)
        cc = self.write_read(PT_DATA_CFG,1)[0]
        
    def _toggle_one_shot(self):
        ctrl = self.write_read(MPL_CTRL_REG1,1)[0]
        ctrl = ctrl & ~(1 << MPL_OST_SHIFT)
        self.write_bytes(MPL_CTRL_REG1, ctrl)
        ctrl = self.write_read(MPL_CTRL_REG1,1)[0]
        ctrl = ctrl | (1 << MPL_OST_SHIFT)
        self.write_bytes(MPL_CTRL_REG1, ctrl)
    
    def _wait_for_data(self, flag):
        #check PDR/PTR bit
        status_reg = self.write_read(REG_STATUS,1)[0]
        if (status_reg & (1 << flag)) == 0:
            self._toggle_one_shot()
        #wait for PDR/PTR bit
        for i in range(100):
            status_reg = self.write_read(REG_STATUS,1)[0]
            if (status_reg & (1 << flag)) == 0:
                sleep(10)
            else:
                return True
        return False
    
    def get_raw_alt(self):
        """

.. method:: get_raw_alt()

        Retrieves the current altitude data from the sensor as raw value.

        Returns raw_a

        """
        if self.mode != MPL_MODE_ALTITUDE:
            self._standby()
            self._set_mode(MPL_MODE_ALTITUDE)
            self._active()
    
        #wait for data ready
        res = self._wait_for_data(MPL_PDR_SHIFT)
        if res is False:
            return None

        #read sensor data
        data = self.write_read(OUT_P_MSB,3)
        raw = (data[0] << 16 | data[1] << 8 | data[2]) >> 4
        return raw

    def get_raw_pres(self):
        """

.. method:: get_raw_pres()

        Retrieves the current pressure data from the sensor as raw value.

        Returns raw_p

        """
        if self.mode != MPL_MODE_PRESSURE:
            self._standby()
            self._set_mode(MPL_MODE_PRESSURE)
            self._active()
        # #wait for data ready
        res = self._wait_for_data(MPL_PDR_SHIFT)
        if res is False:
            return None
        #read sensor data
        data = self.write_read(OUT_P_MSB,3)
        raw_p = (data[0] << 16 | data[1] << 8 | data[2]) >> 4
        return raw_p
    
    def get_raw_temp(self):
        """

.. method:: get_raw_temp()

        Retrieves the current temperature data from the sensor as raw value.

        Returns raw_t

        """
        if self.mode != MPL_MODE_TEMPERATURE:
            self._standby()
            self._set_mode(MPL_MODE_TEMPERATURE)
            self._active()
        #wait for data ready
        res = self._wait_for_data(MPL_TDR_SHIFT)
        if res is False:
            return None
        #read sensor data
        data = self.write_read(OUT_T_MSB,2)
        raw_t = ((data[0] << 4) | (data[1] >> 4))
        return raw_t
        
    def get_alt(self):
        """

.. method:: get_alt()

        Calculates, from measured pressure, the current altitude data as value in meters.

        Returns altitude

        """
        raw = self.get_raw_alt()
        # signed integer in Q16.4 format 
        alt = raw/16.0
        if alt > 32767:
            alt -= 65536 
        return alt
        
    def get_pres(self):
        """

.. method:: get_pres()

        Retrieves the current pressure data from the sensor as calibrate value in Pa.

        Returns pres

        """
        raw = self.get_raw_pres()
        # unsigned integer in Q18.2 format 
        press = raw/4.0
        return press
        
    def get_temp(self):
        """

.. method:: get_temp()

        Retrieves the current temperature data from the sensor as calibrate value in °C.

        Returns temp

        """
        raw = self.get_raw_temp()
        # signed integer in Q8.4 format 
        temp = raw/16.0
        if temp > 127:
            temp -= 256
        return temp
