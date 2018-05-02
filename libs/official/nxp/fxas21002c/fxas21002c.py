"""
.. module:: fxas21002c

*****************
FXAS21002C Module
*****************

This module contains the driver for NXP FXAS21002C gyroscope for measuring the angular velocity.
The FXAS21002C provides direct I2C communication and can be set on 4 different full-scale range and 8 different over sample rate values  (`datasheet <http://www.nxp.com/assets/documents/data/en/data-sheets/FXAS21002.pdf>`_).
    """

import i2c

FXAS_I2C_ADDR        = 0x20

FXAS_H_STATUS        = 0x00
FXAS_H_DR_STATUS     = 0x07
FXAS_H_F_STATUS      = 0x08
FXAS_H_OUT_X_MSB     = 0x01
FXAS_H_OUT_X_LSB     = 0x02
FXAS_H_OUT_Y_MSB     = 0x03
FXAS_H_OUT_Y_LSB     = 0x04
FXAS_H_OUT_Z_MSB     = 0x05
FXAS_H_OUT_Z_LSB     = 0x06
FXAS_H_F_SETUP       = 0x09
FXAS_H_F_EVENT       = 0x0A
FXAS_H_INT_SRC_FLAG  = 0x0B
FXAS_H_WHO_AM_I      = 0x0C
FXAS_H_CTRL_REG0     = 0x0D
FXAS_H_RT_CFG        = 0x0E
FXAS_H_RT_SRC        = 0x0F
FXAS_H_RT_THS        = 0x10
FXAS_H_RT_COUNT      = 0x11
FXAS_H_TEMP          = 0x12
FXAS_H_CTRL_REG1     = 0x13
FXAS_H_CTRL_REG2     = 0x14
FXAS_H_CTRL_REG3     = 0x15

GODR_800HZ           = 0
GODR_400HZ           = 1
GODR_200HZ           = 2
GODR_100HZ           = 3
GODR_50HZ            = 4
GODR_25HZ            = 5
GODR_12_5HZ          = 6
GODR_12_5HZ          = 7

GFSR_2000DPS         = 0
GFSR_1000DPS         = 1
GFSR_500DPS          = 2
GFSR_250DPS          = 3

GFS_NOTDOUBLE        = 0
GFS_DOUBLE           = 1

GSENS_COEFF = [
    0.0625,     # 1000 dps (degrees per second)
    0.03125,    # 500  dps
    0.015625,   # 250  dps
    0.0078125   # 125  dps
]

class FXAS21002C(i2c.I2C):
    """

.. class:: FXAS21002C(i2cdrv, addr=0x20, clk=400000)

    Creates an intance of a new FXAS21002C.

    :param i2cdrv: I2C Bus used '( I2C0, ... )'
    :param addr: Slave address, default 0x20
    :param clk: Clock speed, default 400kHz

    Example: ::

        from nxp.fxas21002c import fxas21002c

        ...

        fxas = fxas21002c.FXAS21002C(I2C0)
        fxas.start()
        fxas.init()
        gyro = fxas.get_gyro()

    """
    def __init__(self, i2cdrv, addr=FXAS_I2C_ADDR, clk=400000):
        i2c.I2C.__init__(self, i2cdrv, addr, clk)
        self._addr = addr

    def init(self, fsr=GFSR_2000DPS, odr=GODR_200HZ, fs_exp=GFS_NOTDOUBLE):
        """

.. method:: init(fsr=0, odr=2, fs_exp=0)

        Initialize the FXAS21002C setting the mode value.

        :param fsr: select the full-scale range (from 0 to 3 - refer to page 39 of the FXAS21002C datasheet), default 0
        :param odr: set the over sample rate (from 0 to 7 - refer to page 46 of the FXAS21002C datasheet), default 2
        :param fs_exp: Full-scale range expansion enable (allowed values 0,1 - refer to page 49 of the FXAS21002C datasheet), default 0

========= ============ ==================
FSR Value FS_EXP Value Degrees per Second
========= ============ ==================
0         0            2000 dps          
1         0            1000 dps          
2         0            500  dps          
3         0            250  dps          
0         1            4000 dps          
1         1            2000 dps          
2         1            1000 dps          
3         1            500  dps          
========= ============ ==================

========= =========
ODR Value Frequency
========= =========
0         800  Hz
1         400  Hz
2         200  Hz
3         100  Hz
4         50   Hz
5         25   HZ
6         12.5 Hz
7         12.5 Hz
========= =========
        """
        self.fsr = fsr
        self.odr = odr
        self.fs_exp = fs_exp
        self._standby()
        self._set_fs_exp(self.fs_exp)
        self._set_fsr(self.fsr)
        self._set_odr(self.odr)
        self._set_ctrl_reg2()
        self._set_rate_threshold()
        self._active()

    def _standby(self):
        reg = self.write_read(FXAS_H_CTRL_REG1, 1)[0]
        reg = reg & ~0x03
        self.write_bytes(FXAS_H_CTRL_REG1, reg)

    def _set_fs_exp(self, fs_exp):
        # increases the dynamic range for each fsr selection by a factor of two
        # from ±250/500/1000/2000°/s to ±500/1000/2000/4000°/s.
        if fs_exp not in (0,1):
            fs_exp = 0
        self.write_bytes(FXAS_H_CTRL_REG3, fs_exp)
        self.fs_exp = fs_exp

    def _set_fsr(self, fsr):
        if fsr < 0 | fsr > 3:
            fsr = GFSR_2000DPS
        self.write_bytes(FXAS_H_CTRL_REG0, fsr)
        self.fsr = fsr

    def _set_odr(self, odr):
        if odr < 0 | odr > 7:
            odr = GODR_200HZ
        self.write_bytes(FXAS_H_CTRL_REG1, (odr<<2))
        self.odr = odr

    def _set_ctrl_reg2(self):
        # disable FIFO, route FIFO and rate threshold interrupts to INT2
        # enable data ready interrupt, route to INT1 
        # active HIGH, push-pull output driver on interrupts 
        self.write_bytes(FXAS_H_CTRL_REG2, 0x0E)

    def _set_rate_threshold(self):
        # set up rate threshold detection; at max rate threshold = FSR; rate threshold = THS*FSR/128
        # enable rate threshold detection on all axes
        self.write_bytes(FXAS_H_RT_CFG, 0x07)
        # unsigned 7-bit THS, set to one-tenth FSR; set clearing debounce counter
        self.write_bytes(FXAS_H_RT_THS, (0x00 | 0x0D))
        # set to 4 (can set up to 255)
        self.write_bytes(FXAS_H_RT_COUNT, 0x04)

    def _active(self):
        reg = self.write_read(FXAS_H_CTRL_REG1, 1)[0]
        # clear bits 0 and 1; standby mode
        reg = reg & ~0x03
        self.write_bytes(FXAS_H_CTRL_REG1, reg)
        # set bit 1 to 1; active mode, data acquisition enabled
        reg = reg | 0x02
        self.write_bytes(FXAS_H_CTRL_REG1, reg)

    def get_raw_gyro(self):
        """

.. method:: get_raw_gyro()

        Retrieves the current gyroscope data as a tuple of X, Y, Z, raw values 

        Returns [gyro_x, gyro_y, gyro_z]

        """
        data = self.write_read(FXAS_H_OUT_X_MSB, 6)
        gx = (data[0] << 8 | data[1])
        gy = (data[2] << 8 | data[3])
        gz = (data[4] << 8 | data[5])
        return [gx, gy, gz]
    
    def get_raw_int_temp(self):
        """

.. method:: get_raw_int_temp()

        Retrieves the current device internal temperature data as raw value.

        Returns raw_t

        """
        raw_t = self.write_read(FXAS_H_TEMP, 1)[0]
        return raw_t
    
    def get_gyro(self, axis=None):
        """

.. method:: get_gyro(axis=None)

        Retrieves the current gyroscope data in degrees per second as a tuple of X, Y, Z values or single axis value if axis argument is provided.

        :param axis: select the axis (allowed values: "x" for x-axis, "y" for y-axis, "z" for z-axis); default None for all values

        Returns [gyro_x, gyro_y, gyro_z] or gyro_x or gyro_y or gyro_z

        """
        raw_gyro = self.get_raw_gyro()
        if raw_gyro[0] >= 32769:
            raw_gyro[0] -= 65535
        if raw_gyro[1] >= 32769:
            raw_gyro[1] -= 65535
        if raw_gyro[2] >= 32769:
            raw_gyro[2] -= 65535
        gyro = [((g*GSENS_COEFF[self.fsr])*(self.fs_exp+1)) for g in raw_gyro]
        # in degrees per second
        if axis in ("x", "X"):
            return gyro[0]
        elif axis in ("y", "Y"):
            return gyro[1]
        elif axis in ("z", "Z"):
            return gyro[2]
        else:
            return gyro
    
    def get_int_temp(self, unit="C"):
        """

.. method:: get_int_temp(unit="C")

        Retrieves the current device internal temperature value in Celtius, Kelvin or Fahrenheit degrees.

        :param unit: select the unit of measure for internal temperature (allowed values: "C" for Celtius degrees, "K" for Kelvin degrees, "F" Fahrenheit degrees); default "C"

        Returns int_temp

        """
        raw_t = self.get_raw_int_temp()
        if raw_t >= 128:
            temp_cels = raw_t - 256
        else:
            temp_cels = raw_t

        if unit in ("c", "C"):
            return temp_cels
        elif unit in ("k", "K"):
            temp_kelv = temp_cels + 273.15
            return temp_kelv
        elif unit in ("f", "F"):
            temp_fahr = (temp_cels * 1.8) + 32
            return temp_fahr
        else:
            return None

