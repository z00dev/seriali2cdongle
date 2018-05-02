"""
.. module:: bmp180

*************
BMP180 Module
*************

This module contains the driver for BOSCH BMP180 Digital Barometric Pressure Sensor. The ultra-low power, low voltage electronics of the BMP180 is optimized for use in mobile devices and the I2C interface allows for easy
system integration with a microcontroller. The BMP180 is based on piezo-resistive technology for EMC robustness, high accuracy and linearity as
well as long term stability (`datasheet <https://ae-bst.resource.bosch.com/media/_tech/media/datasheets/BST-BMP180-DS000-121.pdf>`_).
    """


import i2c

# BMP180 default address.
BMP180_I2CADDR           = 0x77

# Operating Modes
BMP180_ULTRALOWPOWER     = 0
BMP180_STANDARD          = 1
BMP180_HIGHRES           = 2
BMP180_ULTRAHIGHRES      = 3

# BMP180 Calibration coefficient contained in the internal eeprom
BMP180_CAL_AC1_MSB       = 0xAA
BMP180_CAL_AC1_LSB       = 0xAB  
BMP180_CAL_AC2_MSB       = 0xAC  
BMP180_CAL_AC2_LSB       = 0xAD  
BMP180_CAL_AC3_MSB       = 0xAE  
BMP180_CAL_AC3_LSB       = 0xAF  
BMP180_CAL_AC4_MSB       = 0xB0
BMP180_CAL_AC4_LSB       = 0xB1  
BMP180_CAL_AC5_MSB       = 0xB2  
BMP180_CAL_AC5_LSB       = 0xB3  
BMP180_CAL_AC6_MSB       = 0xB4  
BMP180_CAL_AC6_LSB       = 0xB5  
BMP180_CAL_B1_MSB        = 0xB6  
BMP180_CAL_B1_LSB        = 0xB7  
BMP180_CAL_B2_MSB        = 0xB8 
BMP180_CAL_B2_LSB        = 0xB9 
BMP180_CAL_MB_MSB        = 0xBA 
BMP180_CAL_MB_LSB        = 0xBB 
BMP180_CAL_MC_MSB        = 0xBC
BMP180_CAL_MC_LSB        = 0xBD
BMP180_CAL_MD_MSB        = 0xBE
BMP180_CAL_MD_LSB        = 0xBF

# Register Address
BMP180_CONTROL           = 0xF4
BMP180_TEMPDATA          = 0xF6
BMP180_PRESSUREDATA      = 0xF6

# Commands
BMP180_READ_T_CMD        = 0x2E
BMP180_READ_P_CMD        = [0x34, 0x74, 0xB4, 0xF4]

class BMP180(i2c.I2C):
    """
.. class:: BMP180(i2cdrv, addr=0x77, clk=100000)

    Creates an intance of a new BMP180.

    :param i2cdrv: I2C Bus used '( I2C0, ... )'
    :param addr: Slave address, default 0x77
    :param clk: Clock speed, default 100kHz

    Example: ::

        from bosch.bmp180 import bmp180

        ...

        bmp = bmp180.BMP180(I2C0)
        bmp.start()
        bmp.init()
        temp, pres = bmp.get_temp_pres()

    """

    #Init
    def __init__(self, drvname, addr=BMP180_I2CADDR, clk=400000):
        i2c.I2C.__init__(self,drvname,addr,clk)
        self._addr = addr
        self._oss = 0
        try:
            self.start()
        except PeripheralError as e:
            print(e)        

    def init(self, oss=0):
        """

.. method:: init(oss=0)

        Initialize the BMP180 calibrating the sensor and setting the oss value.

        :param oss: OverSampling Setting value (from 0 to 4), default 0

        """
        self._calibrate()
        self.set_over_sampling_setting(oss) #default oss

    #Write on register
    def _write(self, addr, data):
        buffer = bytearray(2)
        buffer[0] = addr
        buffer[1] = data

        self.write(buffer)

    #Read raw pressure
    def _read_uint_from_16_to_19(self, reg):
        data = self.write_read(reg, 3) #data[0] --> MSB, data[1] --> LSB, data[2] --> XLSB
        res = (((data[0] << 16) + (data[1] << 8) + data[2]) >> (8-self._oss))
        return res

    #Read raw temperature or uint16 register
    def _read_uint16(self, reg):
        data = self.write_read(reg, 2) #data[0] --> MSB, data[1] --> LSB
        res = ((data[0] << 8 | (data[1])) & 0xFFFF)
        return res

    #Read int16 register
    def _read_int16(self, reg):
        res = self._read_uint16(reg)
        if res > 32767:
            res -= 65536
        return res

    #Calilbrate the sensor
    def _calibrate(self):
        self.cal_AC1 = self._read_int16(BMP180_CAL_AC1_MSB)   # INT16
        self.cal_AC2 = self._read_int16(BMP180_CAL_AC2_MSB)   # INT16
        self.cal_AC3 = self._read_int16(BMP180_CAL_AC3_MSB)   # INT16
        self.cal_AC4 = self._read_uint16(BMP180_CAL_AC4_MSB)  # UINT16
        self.cal_AC5 = self._read_uint16(BMP180_CAL_AC5_MSB)  # UINT16
        self.cal_AC6 = self._read_uint16(BMP180_CAL_AC6_MSB)  # UINT16
        self.cal_B1 = self._read_int16(BMP180_CAL_B1_MSB)     # INT16
        self.cal_B2 = self._read_int16(BMP180_CAL_B2_MSB)     # INT16
        self.cal_MB = self._read_int16(BMP180_CAL_MB_MSB)     # INT16
        self.cal_MC = self._read_int16(BMP180_CAL_MC_MSB)     # INT16
        self.cal_MD = self._read_int16(BMP180_CAL_MD_MSB)     # INT16
        
    #Set oversampling parameter
    def set_over_sampling_setting(self, oss):
        """

.. method:: set_over_sampling_setting(oss)

        Sets the OverSampling Setting value of the BMP180.

        :param oss: OverSampling Setting value (from 0 to 4 allowed)

.. note:: The OverSampling Setting parameter selects different operating modes according to give the possibility for findind the optimum compromise between power consumption, speed, and resolution; in the table below allowed values are reported with related operating modes.

========= ===================== ============ =============== ======================
OSS param     Operating Mode    N of samples Conversion time Avg Current 1 sample/s
========= ===================== ============ =============== ======================
    0        Ultra Low Power         1           4.5 ms                3 uA
    1           Standard             2           7.5 ms                5 uA
    2        High Resolution         4          13.5 ms                7 uA
    3     Ultra High Resolution      8          25.5 ms               12 uA
========= ===================== ============ =============== ======================
                     
        """
        if oss in range(4):
            self._oss = oss

    #Get raw temperature
    def get_raw_temp(self):
        """

.. method:: get_raw_temp()

        Retrieves the current temperature data from the sensor as raw value.

        Returns raw_t

        """
        self._write(BMP180_CONTROL, BMP180_READ_T_CMD)
        sleep(5)  # p.21 max conversion time for temp reading
        raw_t = self._read_uint16(BMP180_TEMPDATA)
        return raw_t

    #Get raw pressure
    def get_raw_pres(self):
        """

.. method:: get_raw_pres()

        Retrieves the current pressure data from the sensor as raw value; according to the OverSampling Setting value this measure can be
        faster but less accurate or more precise but slower. (see :func:`set_over_sampling_setting()`)

        Returns raw_p

        """
        self._write(BMP180_CONTROL, BMP180_READ_P_CMD[self._oss])
        if self._oss == BMP180_ULTRALOWPOWER:
            sleep(5)
        elif self._oss == BMP180_STANDARD:
            sleep(8)
        elif self._oss == BMP180_HIGHRES:
            sleep(14)
        elif self._oss == BMP180_ULTRAHIGHRES:
            sleep(26)
        raw_p = self._read_uint_from_16_to_19(BMP180_PRESSUREDATA)
        return raw_p

    #Get Temperature in °C
    def get_temp(self):
        """

.. method:: get_temp()

        Retrieves the current temperature data from the sensor as calibrate value in °C.

        Returns temp

        """
        rt = self.get_raw_temp()
        # p.15 datasheet - calculate true temperature
        x1 = ((rt - self.cal_AC6) * self.cal_AC5) >> 15
        x2 = (self.cal_MC << 11) // (x1 + self.cal_MD)
        xx = x1 + x2
        temp = ((xx + 8) >> 4) / 10.0
        return temp

    #Get pressure in Pa
    def get_pres(self):
        """

.. method:: get_pres()

        Retrieves the current pressure data from the sensor as calibrate value in Pa; according to the OverSampling Setting value this measure can be
        faster but less accurate or more precise but slower. (see :func:`set_over_sampling_setting()`)

        Returns pres

        """
        rt = self.get_raw_temp()
        rp = self.get_raw_pres()
        # p.15 datasheet - calculate true pressure
        x1 = ((rt - self.cal_AC6) * self.cal_AC5) >> 15
        x2 = (self.cal_MC << 11) // (x1 + self.cal_MD)
        xx = x1 + x2
        
        # Pressure Calculations
        yy = xx - 4000
        x1 = (self.cal_B2 * (yy * yy) >> 12) >> 11
        x2 = (self.cal_AC2 * yy) >> 11
        x3 = x1 + x2
        vv = (((self.cal_AC1 * 4 + x3) << self._oss) + 2) // 4
        x1 = (self.cal_AC3 * yy) >> 13
        x2 = (self.cal_B1 * ((yy * yy) >> 12)) >> 16
        x3 = ((x1 + x2) + 2) >> 2
        ww = (self.cal_AC4 * (x3 + 32768)) >> 15
        zz = float(rp - vv) * float(50000 >> self._oss)
        pres = (zz * 2) // ww
        pres = int(pres)
        x1 = (pres >> 8) * (pres >> 8)
        x1 = (x1 * 3038) >> 16
        x2 = (-7357 * pres) >> 16
        pres = pres + ((x1 + x2 + 3791) >> 4)
        return pres

    #Get both temp and pres
    def get_temp_pres(self):
        """

.. method:: get_temp_pres()

        Retrieves the current temperature (in °C) and pressure (in Pa) data from the sensor as calibrate values in one call.

        Returns temp

        """
        t = self.get_temp()
        p = self.get_pres()
        return t, p

    #Get altitude in m
    def get_altitude(self):
        """

.. method:: get_altitude()

        Calculates, from measured pressure, the current altitude data as value in meters.

        Returns altitude

        """
        # p.16 datasheet - Calculating absolute altitude
        pres = float(self.get_pres())
        p0 = 101325.0 # pressure at sea leve in Pa
        altitude = 44330.0 * (1.0 - ((pres / p0)**(1.0/5.255)))
        return altitude

    #Get pressure at sea level in Pa
    def get_sea_level_pres(self, altitude_m=0.0):
        """

.. method:: get_sea_level_pres()

        Calculates, from measured pressure, the pressure (in Pa) at sea level when given a known altitude in meters.

        Returns p0 (pressure at sea level)

        """
        # p.17 datasheet - Calculating pressure at sea level
        pres = float(self.get_pres())
        p0 = pres / ((1.0 - altitude_m/44330.0)**(5.255))
        return p0
