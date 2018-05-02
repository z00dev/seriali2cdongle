#   Zerynth - libs - bosch-bme280/bme280.py
#
#   Zerynth library for BME280 environmental sensor
#
#   SPI communication is not implemented
#
# @Author: andreabau
#
# @Date:   2017-09-19 11:41:38
# @Last Modified by:   andreabau
# @Last Modified time: 2017-11-28 11:08:49

"""
.. module:: bme280

**************
BME280 Module
**************

.. _datasheet: https://ae-bst.resource.bosch.com/media/_tech/media/datasheets/BST-BME280_DS001-11.pdf

This module contains the Zerynth driver for Bosch BME280 digital environmental sensor. The unit combine high linearity and accuracy sensors for pressure,
humidity and temperature and is designed for low current consumption, long term sability and high EMC robustness. The BME280 features I2C and SPI digital
interfaces, the present library enables I2C only (datasheet_).

"""

import i2c

# two's complement
#
# @param      v      integer value to be converted
# @param      n_bit  number of bits of v's representation
#
# @return     the two's complement of v
#
def _tc(v, n_bit=16):
    mask = 2**(n_bit - 1)
    return -(v & mask) + (v & ~mask)

BME280_I2CADDR = 0x76

BME280_REGISTER_DIG_T1          = 0x88
BME280_REGISTER_DIG_T2          = 0x8A
BME280_REGISTER_DIG_T3          = 0x8C

BME280_REGISTER_DIG_P1          = 0x8E 
BME280_REGISTER_DIG_P2          = 0x90 
BME280_REGISTER_DIG_P3          = 0x92 
BME280_REGISTER_DIG_P4          = 0x94 
BME280_REGISTER_DIG_P5          = 0x96 
BME280_REGISTER_DIG_P6          = 0x98 
BME280_REGISTER_DIG_P7          = 0x9A 
BME280_REGISTER_DIG_P8          = 0x9C 
BME280_REGISTER_DIG_P9          = 0x9E 
                                
BME280_REGISTER_DIG_H1          = 0xA1
BME280_REGISTER_DIG_H2          = 0xE1
BME280_REGISTER_DIG_H3          = 0xE3
BME280_REGISTER_DIG_H4          = 0xE4
BME280_REGISTER_DIG_H5          = 0xE5
BME280_REGISTER_DIG_H6          = 0xE7

BME280_REGISTER_CHIPID          = 0xD0
BME280_REGISTER_VERSION         = 0xD1
BME280_REGISTER_SOFTRESET       = 0xE0

BME280_REGISTER_CONTROLHUMID    = 0xF2
BME280_REGISTER_STATUS          = 0XF3
BME280_REGISTER_CONTROL         = 0xF4
BME280_REGISTER_CONFIG          = 0xF5
BME280_REGISTER_PRESSUREDATA    = 0xF7
BME280_REGISTER_TEMPDATA        = 0xFA
BME280_REGISTER_HUMIDDATA       = 0xFD


class BME280(i2c.I2C):
    """
    
===============
 BME280 class
===============

.. class:: BME280(drvname, addr=0x76, clk=400000)

    Creates an intance of the BME280 class.

    :param drvname: I2C Bus used '( I2C0, ... )'
    :param addr: Slave address, default 0x76
    :param clk: Clock speed, default 400kHz

    Sensor's calibration data are automatically read on object creation and setup method is called with default parameters. Temperature, 
    humidity and pressure values can be easily obtained from the sensor: ::

        from bosch.bme280 import bme280

        ...

        bmp = bme280.BME280(I2C0)
        
        temp, hum, pres = bmp.get_values()
    """
    def __init__(self, drvname, addr=BME280_I2CADDR, clk=400000):
        i2c.I2C.__init__(self,drvname,addr,clk)
        try:
            self.start()
        except PeripheralError as e:
            print(e)
        
        
        self._read_coeff()
        self.setup()


        
        
    def setup(self, mode = 3, os_t = 1, os_h = 1, os_p = 1, t_sb = 6, filter = 1):
        """
.. method:: setup(mode = 3, os_t = 1, os_h = 1, os_p = 1, t_sb = 6, filter = 1)
        
        This method sets the operating mode and the sampling parameters of the module.
        
        **Parameters**:
        
        **mode**: Control the operating mode. Sleep mode is entered by default after power on reset. In sleep 
        mode, no measurement are performed and all registers are accessible.
        In normal mode the sensor cycles between an active measurement period and an inactive standby period.
        In forced mode a single measurement is perfomed in accordance to the selected measurement and filter options,
        after which the sensor enter in sleep mode. 
        
        ======== =====================
         mode        Operating mode
        ======== =====================
         0         Sleep Mode
         1 or 2    Forced Mode
         3         Normal Mode
        ======== =====================
        
        .. note:: See pages 12-13 of the datasheet_ for more details on operating mode and allowed sensor mode transitions.
        
        **os_t**: Oversampling setting for temperature sensor, see *os_p* for details on allowed values.
        
        **os_h**: Oversampling setting for humidity sensor, see *os_p* for details on allowed values.
        
        **os_p**: Oversampling setting for pressure sensor.
        
        ======  ===========================
        os_p     Oversampling setting
        ======  ===========================
         0       Skipped (output set to 0)
         1       oversampling 1x
         2       oversampling 2x
         3       oversampling 4x
         4       oversampling 8x
         5       oversampling 16x
        ======  ===========================
        
        **t_sb**: Control the inactive duration t_standby in normal mode.
        
        ====== =====================
        t_sb    t_standby [ms]
        ====== =====================
         0      0.5
         1      62.5
         2      125
         3      250
         4      500
         5      1000
         6      10
         7      20
        ====== =====================
        
        **filter**: Control the time constant of the internal IIR filter. It reduces the bandwidth of the temperature
        and pressure output signals and increases the resolution of the pressure and temperature output data to 20 bit.
        
        ====== =====================
        filter  Filter coefficient
        ====== =====================
         0      Filter off
         1      2
         2      4
         3      8
         4      16
        ====== =====================
"""
        
        mode = mode & 3
        
        os_t = os_t & 7
        os_h = os_h & 7
        os_p = os_p & 7
        
        t_sb = t_sb & 7
        
        filter = filter & 7
        
        self.write_bytes(BME280_REGISTER_CONTROLHUMID, os_h)
        self.write_bytes(BME280_REGISTER_CONTROL, (os_t << 5) | (os_p << 2) | mode )
        self.write_bytes(BME280_REGISTER_CONFIG, (t_sb << 5) | (filter << 2) )


    ##
    ## @brief      Reads calibration coefficient from the sensor and saves in object attributes
    ##
    ## @param      self
    ##
    ## @return     nothing
    ##
    def _read_coeff(self):
        dig_T1 = self.write_read(BME280_REGISTER_DIG_T1,2)
        dig_T2 = self.write_read(BME280_REGISTER_DIG_T2,2)
        dig_T3 = self.write_read(BME280_REGISTER_DIG_T3,2)

        self.dig_T1 = dig_T1[0] | (dig_T1[1]<<8)
        self.dig_T2 = _tc(dig_T2[0] | (dig_T2[1]<<8))
        self.dig_T3 = _tc(dig_T3[0] | (dig_T3[1]<<8))


        dig_P1 = self.write_read(BME280_REGISTER_DIG_P1,2)
        dig_P2 = self.write_read(BME280_REGISTER_DIG_P2,2)
        dig_P3 = self.write_read(BME280_REGISTER_DIG_P3,2)
        dig_P4 = self.write_read(BME280_REGISTER_DIG_P4,2)
        dig_P5 = self.write_read(BME280_REGISTER_DIG_P5,2)
        dig_P6 = self.write_read(BME280_REGISTER_DIG_P6,2)
        dig_P7 = self.write_read(BME280_REGISTER_DIG_P7,2)
        dig_P8 = self.write_read(BME280_REGISTER_DIG_P8,2)
        dig_P9 = self.write_read(BME280_REGISTER_DIG_P9,2)

        self.dig_P1 = dig_P1[0] | (dig_P1[1]<<8)
        self.dig_P2 = _tc(dig_P2[0] | (dig_P2[1]<<8))
        self.dig_P3 = _tc(dig_P3[0] | (dig_P3[1]<<8))
        self.dig_P4 = _tc(dig_P4[0] | (dig_P4[1]<<8))
        self.dig_P5 = _tc(dig_P5[0] | (dig_P5[1]<<8))
        self.dig_P6 = _tc(dig_P6[0] | (dig_P6[1]<<8))
        self.dig_P7 = _tc(dig_P7[0] | (dig_P7[1]<<8))
        self.dig_P8 = _tc(dig_P8[0] | (dig_P8[1]<<8))
        self.dig_P9 = _tc(dig_P9[0] | (dig_P9[1]<<8))


        dig_H1 = self.write_read(BME280_REGISTER_DIG_H1,1)
        dig_H2 = self.write_read(BME280_REGISTER_DIG_H2,2)
        dig_H3 = self.write_read(BME280_REGISTER_DIG_H3,1)
        dig_H4 = self.write_read(BME280_REGISTER_DIG_H4,2)
        dig_H5 = self.write_read(BME280_REGISTER_DIG_H5,2)
        dig_H6 = self.write_read(BME280_REGISTER_DIG_H6,1)

        self.dig_H1 = dig_H1[0]
        self.dig_H2 = _tc(dig_H2[0] | (dig_H2[1]<<8))
        self.dig_H3 = dig_H3[0]
        self.dig_H4 = _tc((dig_H4[0] << 4) | (dig_H4[1] & 0xF))
        self.dig_H5 = _tc((dig_H5[1] << 4) | (dig_H5[0] >> 4))
        self.dig_H6 = _tc(dig_H6[0],8)


    ##
    ## @brief      Calculates the temperature from ADC output
    ##
    ## @param      self 
    ## @param      adc_t  20-bit temperature raw data 
    ##
    ## @return     measured temperature in Celsius degree
    ##
    def _calc_temp(self,adc_t):
        if adc_t == 0x80000:
            return 0
        var1 = (((adc_t>>3) - (self.dig_T1 <<1)) * self.dig_T2) >> 11
        var2 = (((((adc_t>>4) - (self.dig_T1)) * ((adc_t>>4) - (self.dig_T1))) >> 12) * (self.dig_T3)) >> 14

        t_fine = var1 + var2;
        self.t_fine = t_fine
        T = (t_fine * 5 + 128) >> 8
        return T/100


    ##
    ## @brief      Calculates the humidity from ADC output
    ##
    ## @param      self
    ## @param      adc_h  16-bit humidity raw data
    ##
    ## @return     measured humidity in %rH
    ##
    def _calc_hum(self,adc_h):
        if adc_h == 0x8000:
            return 0

        v_x1_u32r = self.t_fine - 76800
        v_x1_u32r = (((((adc_h << 14) - (self.dig_H4 << 20) -
                        (self.dig_H5 * v_x1_u32r)) + 16384) >> 15) *
                     (((((((v_x1_u32r * self.dig_H6) >> 10) *
                          (((v_x1_u32r * self.dig_H3) >> 11) + 32768)) >> 10) +
                        2097152) * self.dig_H2 + 8192) >> 14))

        v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) *
                                   self.dig_H1) >> 4))

        v_x1_u32r = 0 if v_x1_u32r <0 else v_x1_u32r
        v_x1_u32r = 419430400 if v_x1_u32r >419430400 else v_x1_u32r

        h = (v_x1_u32r>>12)
        return h / 1024.0


    ##
    ## @brief      Calculates the pressure from ADC output
    ##
    ## @param      self   
    ## @param      adc_p  20-bit pressure raw data
    ##
    ## @return     measured pressure in Pa
    ##
    def _calc_pres(self,adc_p):
        if adc_p == 0x80000:
            return 0
        
        var1 = (self.t_fine >> 1) - 64000
        
        var2 = (((var1>>2) * (var1>>2)) >> 11 ) * self.dig_P6
        var2 = var2 + ((var1*self.dig_P5)<<1)
        var2 = (var2>>2)+(self.dig_P4<<16)
        
        var1 = (((self.dig_P3 * (((var1>>2) * (var1>>2)) >> 13 )) >> 3) + ((self.dig_P2 * var1)>>1))>>18
        var1 = ((32768+var1)*(self.dig_P1))>>15
        
        if var1 == 0:
            return 0 # avoid exception caused by division by zero
        
        p = (((1048576-adc_p)-(var2>>12)))*3125
        p = (p //var1 ) << 1
        
        var1 = (self.dig_P9 * (((p>>3) * (p>>3))>>13)) >> 12
        var2 = ((p>>2) * self.dig_P8) >> 13
        
        p = p + ((var1 + var2 + self.dig_P7) >> 4)
        
        return p/100


    ##
    ## @brief      Read the raw temperature data from ADC output register
    ##
    ## @param      self
    ##
    ## @return     20-bit raw temperature value
    ##             
    def get_raw_temp(self):
        r = self.write_read(BME280_REGISTER_TEMPDATA,3)
        adc_t = (r[0]<<16) | (r[1] <<8) | r[2]
        adc_t = adc_t>>4
        return adc_t
        

    ##
    ## @brief      Read the raw humidity data from ADC output register
    ##
    ## @param      self
    ##
    ## @return     16-bit raw humidity value
    ##
    def get_raw_hum(self):
        r = self.write_read(BME280_REGISTER_HUMIDDATA,2)
        adc_h = (r[0]<<8) | r[1]
        return adc_h
    
    ##
    ## @brief      Read the raw pressure data from ADC output register
    ##
    ## @param      self
    ##
    ## @return     20-bit raw pressure value
    ##             
    def get_raw_pres(self):
        r = self.write_read(BME280_REGISTER_PRESSUREDATA,3)
        adc_p = (r[0] << 16) | (r[1] << 8) | r[2]
        adc_p = adc_p >> 4
        return adc_p


    def get_temp(self):
        """
    .. method:: get_temp()
        
        Return the current temperature value in Celsius degree.

        """
        adc_t = self.get_raw_temp()
        t = self._calc_temp(adc_t)
        
        return t


    def get_hum(self):
        """
    .. method:: get_hum()

        Return the current humidity value in %rH.
        
        """
        self.get_temp()
        adc_h = self.get_raw_hum()
        h = self._calc_hum(adc_h)
        
        return h


    def get_press(self):
        """
    .. method:: get_press()

        Return the current pressure value in Pascal.
        
        """
        self.get_temp()
        adc_p = self.get_raw_pres()
        p = self._calc_pres(adc_p)
        
        return p


    def get_values(self):
        """
    .. method:: get_values()

        Return a 3-element tuple containing current temperature, humidity and pressure values.
        
        """
        r = self.write_read(BME280_REGISTER_PRESSUREDATA,8)
        
        adc_t = (r[3]<<16) | (r[4] <<8) | r[5]
        adc_t = adc_t>>4
        
        adc_h = (r[6]<<8) | r[7]
        
        adc_p = (r[0] << 16) | (r[1] << 8) | r[2]
        adc_p = adc_p >> 4
        
        return (self._calc_temp(adc_t), self._calc_hum(adc_h), self._calc_pres(adc_p))


    def soft_reset(self):
        """
    .. method:: soft_reset()

        Reset the device using the complete power-on-reset procedure.

        """
        self.write(BME280_REGISTER_SOFTRESET, 0xB6)


    def get_status(self):
        """
    .. method:: get_status()

        Return a two element long tuple representing the status of the sensor. The first element is equal to ``1`` whenever a conversion is running; it is equal 
        to ``0`` when the results have been transferred to the data register. The second and last element of the returned tuple is euqal to ``1`` when the 
        non-volatile memory data (calibration parameters) are being copied to image registers; it is equal to ``0`` when the copying is done. The data are copied
        at power-on-reset and before every conversion.
        
        """
        r = self.write_read(BME280_REGISTER_STATUS,1)
        measuring = (r[0] >> 3) & 1 
        update = r[0] & 1
        return (measuring,update)


    def get_chip_id(self):
        """
    .. method:: get_chip_id()
    
        Return the device chip id as a single byte integer.
        
        """
        r = self.write_read(BME280_REGISTER_CHIPID,1)
        print(r[0])
