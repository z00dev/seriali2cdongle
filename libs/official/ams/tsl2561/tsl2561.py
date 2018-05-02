"""
.. module:: tsl2561

**************
TSL2561 Module
**************

This module contains the driver for AMS TSL2561 Luminosity sensor integrating both infrared and full-spectrum photodiodes.
The TSL2561 is capable of direct I2C communication and is able to conduct specific light ranges from 0.1 - 40k+ Lux easily. Additionally, it contains two integrating analog-to-digital converters (ADC) that convert currents from the two photodiodes, simultaneously (`datasheet <http://ams.com/eng/content/download/250094/975485/file/TSL2560-61_DS000110_2-00.pdf>`_).
    """

import i2c

TSL_I2C_ADDRESS = {
    "LOW": 0x29,
    "NORMAL": 0x39,
    "HIGH": 0x49
}
 
TSL_COMMAND_BIT   = 0x80    # Must be 1
TSL_CLEAR_BIT     = 0x40    # Clears any pending interrupt = write 1 to clear
TSL_WORD_BIT      = 0x20    # read/write word = rather than byte
TSL_BLOCK_BIT     = 0x10    # using block read/write

TSL_CONTROL_POWERON  = 0x03
TSL_CONTROL_POWEROFF = 0x00

TSL_LUX_SCALE        = 14      # Scale by 2^14
TSL_RATIO_SCALE      = 9       # Scale ratio by 2^9
TSL_CHSCALE          = 10      # Scale channel values by 2^10
TSL_CHSCALE_TINT0    = 0x7517  # 322/11 * 2^TSL_LUX_CHSCALE
TSL_CHSCALE_TINT1    = 0x0FE7  # 322/81 * 2^TSL_LUX_CHSCALE

# T, FN and CL package coefficients
TSL_K1T = 0x0040  # 0.125 * 2^RATIO_SCALE
TSL_B1T = 0x01f2  # 0.0304 * 2^LUX_SCALE
TSL_M1T = 0x01be  # 0.0272 * 2^LUX_SCALE
TSL_K2T = 0x0080  # 0.250 * 2^RATIO_SCALE
TSL_B2T = 0x0214  # 0.0325 * 2^LUX_SCALE
TSL_M2T = 0x02d1  # 0.0440 * 2^LUX_SCALE
TSL_K3T = 0x00c0  # 0.375 * 2^RATIO_SCALE
TSL_B3T = 0x023f  # 0.0351 * 2^LUX_SCALE
TSL_M3T = 0x037b  # 0.0544 * 2^LUX_SCALE
TSL_K4T = 0x0100  # 0.50 * 2^RATIO_SCALE
TSL_B4T = 0x0270  # 0.0381 * 2^LUX_SCALE
TSL_M4T = 0x03fe  # 0.0624 * 2^LUX_SCALE
TSL_K5T = 0x0138  # 0.61 * 2^RATIO_SCALE
TSL_B5T = 0x016f  # 0.0224 * 2^LUX_SCALE
TSL_M5T = 0x01fc  # 0.0310 * 2^LUX_SCALE
TSL_K6T = 0x019a  # 0.80 * 2^RATIO_SCALE
TSL_B6T = 0x00d2  # 0.0128 * 2^LUX_SCALE
TSL_M6T = 0x00fb  # 0.0153 * 2^LUX_SCALE
TSL_K7T = 0x029a  # 1.3 * 2^RATIO_SCALE
TSL_B7T = 0x0018  # 0.00146 * 2^LUX_SCALE
TSL_M7T = 0x0012  # 0.00112 * 2^LUX_SCALE
TSL_K8T = 0x029a  # 1.3 * 2^RATIO_SCALE
TSL_B8T = 0x0000  # 0.000 * 2^LUX_SCALE
TSL_M8T = 0x0000  # 0.000 * 2^LUX_SCALE

# CS package values
TSL_K1C = 0x0043  # 0.130 * 2^RATIO_SCALE
TSL_B1C = 0x0204  # 0.0315 * 2^LUX_SCALE
TSL_M1C = 0x01ad  # 0.0262 * 2^LUX_SCALE
TSL_K2C = 0x0085  # 0.260 * 2^RATIO_SCALE
TSL_B2C = 0x0228  # 0.0337 * 2^LUX_SCALE
TSL_M2C = 0x02c1  # 0.0430 * 2^LUX_SCALE
TSL_K3C = 0x00c8  # 0.390 * 2^RATIO_SCALE
TSL_B3C = 0x0253  # 0.0363 * 2^LUX_SCALE
TSL_M3C = 0x0363  # 0.0529 * 2^LUX_SCALE
TSL_K4C = 0x010a  # 0.520 * 2^RATIO_SCALE
TSL_B4C = 0x0282  # 0.0392 * 2^LUX_SCALE
TSL_M4C = 0x03df  # 0.0605 * 2^LUX_SCALE
TSL_K5C = 0x014d  # 0.65 * 2^RATIO_SCALE
TSL_B5C = 0x0177  # 0.0229 * 2^LUX_SCALE
TSL_M5C = 0x01dd  # 0.0291 * 2^LUX_SCALE
TSL_K6C = 0x019a  # 0.80 * 2^RATIO_SCALE
TSL_B6C = 0x0101  # 0.0157 * 2^LUX_SCALE
TSL_M6C = 0x0127  # 0.0180 * 2^LUX_SCALE
TSL_K7C = 0x029a  # 1.3 * 2^RATIO_SCALE
TSL_B7C = 0x0037  # 0.00338 * 2^LUX_SCALE
TSL_M7C = 0x002b  # 0.00260 * 2^LUX_SCALE
TSL_K8C = 0x029a  # 1.3 * 2^RATIO_SCALE
TSL_B8C = 0x0000  # 0.000 * 2^LUX_SCALE
TSL_M8C = 0x0000  # 0.000 * 2^LUX_SCALE

TSL_REG_CONTROL = 0x00
TSL_REG_TIMING = 0x01
TSL_REG_THRESHHOLDL_LOW = 0x02
TSL_REG_THRESHHOLDL_HIGH = 0x03
TSL_REG_THRESHHOLDH_LOW = 0x04
TSL_REG_THRESHHOLDH_HIGH = 0x05
TSL_REG_INTERRUPT = 0x06
TSL_REG_CRC = 0x08
TSL_REG_ID = 0x0A
TSL_REG_CHAN0_LOW = 0x0C
TSL_REG_CHAN0_HIGH = 0x0D
TSL_REG_CHAN1_LOW = 0x0E
TSL_REG_CHAN1_HIGH = 0x0F

TSL_CHANNEL_VISIBLE = 2    # channel 0 - channel 1
TSL_CHANNEL_INFRARED = 1    # channel 1
TSL_CHANNEL_FULL = 0    # channel 0

TSL_INTEGRATION_TIME_13MS  = 0x00    # 13.7ms
TSL_INTEGRATION_TIME_101MS = 0x01    # 101ms
TSL_INTEGRATION_TIME_402MS = 0x02    # 402ms

TSL_GAIN_0X = 0x00    # No gain
TSL_GAIN_16X = 0x10   # 16x gain

TSL_DELAY_INTTIME = [15, 120, 450]
TSL_GAIN = [TSL_GAIN_0X, TSL_GAIN_16X]

# Auto-gain thresholds
TSL_AGC_THI_13MS = 485     # Max value at Ti 13ms = 5047
TSL_AGC_TLO_13MS = 100
TSL_AGC_THI_101MS = 36000   # Max value at Ti 101ms = 37177
TSL_AGC_TLO_101MS = 200
TSL_AGC_THI_402MS = 63000   # Max value at Ti 402ms = 65535
TSL_AGC_TLO_402MS = 500

# Clipping thresholds
TSL_CLIPPING_13MS = 4900
TSL_CLIPPING_101MS = 37000
TSL_CLIPPING_402MS = 65000

# packages
TSL_PACKAGE_CS = 0
TSL_PACKAGE_T_FN_CL = 1


class TSL2561(i2c.I2C):
    """
.. class:: TSL2561(i2cdrv, addr=0x49, clk=400000)

    Creates an intance of a new TSL2561.

    :param i2cdrv: I2C Bus used '( I2C0, ... )'
    :param addr: Slave address, default 0x49
    :param clk: Clock speed, default 400kHz

    Example: ::

        from ams.tsl2561 import tsl2561

        ...

        tsl = tsl2561.TSL2561(I2C0, addr=tsl2561.TSL_I2C_ADDRESS["LOW"])
        tsl.start()
        tsl.init()
        lux = tsl.get_lux()

    .. note:: This sensor has a dedicaded "Address" pin that allows to select 1 of 3 available address as shown in the table below.

======================= =========== ========================================
ADDR SEL Terminal Level I2C Address Zerynth Define 
======================= =========== ========================================
    GND                    0x29     addr = tsl2561.TSL_I2C_ADDRESS["LOW"]      
    Float                  0x39     addr = tsl2561.TSL_I2C_ADDRESS["NORMAL"]   
    Vdd                    0x49     addr = tsl2561.TSL_I2C_ADDRESS["HIGH"]    
======================= =========== ========================================

    """
    # Init
    def __init__(self, i2cdrv, addr=TSL_I2C_ADDRESS["HIGH"], clk=400000):
        i2c.I2C.__init__(self, i2cdrv, addr, clk)
        self._addr = addr

    def init(self, gain=TSL_GAIN_16X, timing=TSL_INTEGRATION_TIME_13MS, pack=TSL_PACKAGE_T_FN_CL):
        """

.. method:: init(gain=1, timing=0, pack=1)

        Initialize the TSL2561 setting the gain, timing and kind of package.

        :param gain: set the gain of the sensor (values allowed: 0 for gain=1x and 1 for gain=16x), default 1
        :param timing: set the integration time value (from 0 to 2 - 0 for 13 ms, 1 for 101 ms, 2 for 402 ms), default 0
        :param pack: set the kind of package for the correct lux calculation (values allowed: 0 for CS package and 1 for T,FN,CL package), default 1

        """
        self.gain = gain
        self.timing = timing
        self.delay = TSL_DELAY_INTTIME[int(timing)]
        self.pack = pack

        self._disable()
        self._enable()
        self._set_gain(gain)
        self._set_timing(timing)

    def _enable(self):
        self.write_bytes((TSL_COMMAND_BIT | TSL_REG_CONTROL), TSL_CONTROL_POWERON)

    def _disable(self):
        self.write_bytes((TSL_COMMAND_BIT | TSL_REG_CONTROL), TSL_CONTROL_POWEROFF)

    def _set_gain(self, gain):
        if gain == 0 or gain == 1:
            gain = TSL_GAIN[gain]
        if gain in (0x00, 0x10):
            self.write_bytes((TSL_COMMAND_BIT | TSL_REG_TIMING), (gain | self.timing))
            self.gain = gain
        else:
            print("gain error")

    def _set_timing(self, timing):
        if timing in (0x00, 0x01, 0x02):
            self.write_bytes((TSL_COMMAND_BIT | TSL_REG_TIMING), (self.gain | timing))
            self.timing = timing
            self.delay = TSL_DELAY_INTTIME[timing]
        else:
            print("timing error")

    def _wait(self):
        sleep(self.delay)

    def get_raw_fullspectrum(self):
        """

.. method:: get_raw_fullspectrum()

        Retrieves the current raw value read on channel0 (full-spectrum photodiode).

        Returns raw_fs

        """
        self._enable()
        self._wait()
        data = self.write_read(TSL_COMMAND_BIT | TSL_WORD_BIT | TSL_REG_CHAN0_LOW, 2)
        self._disable()
        raw_fs = (data[1] << 8) | data[0]
        return raw_fs

    def get_raw_infrared(self):
        """

.. method:: get_raw_infrared()

        Retrieves the current raw value read on channel1 (infrared photodiode).

        Returns raw_ir

        """
        self._enable()
        self._wait()
        data = self.write_read(TSL_COMMAND_BIT | TSL_WORD_BIT | TSL_REG_CHAN1_LOW, 2)
        self._disable()
        raw_ir = (data[1] << 8) | data[0]
        return raw_ir

    def get_raw_visible(self):
        """

.. method:: get_raw_visible()

        Retrieves the difference between the current raw value read on channel0 and raw value on channel1 (visible spectrum).

        Returns raw_vis = (raw_fs - raw_ir)

        """
        full = self.get_raw_fullspectrum()
        ir = self.get_raw_infrared()
        return full - ir

    def get_lux(self):
        """

.. method:: get_lux()

        Converts the raw sensor values to the standard SI lux equivalent (according to the sensor settings - gain, timing and kind of package).

        Returns lux value or 0 if the sensor is saturated and the values are unreliable.

        """
        full = self.get_raw_fullspectrum()
        ir = self.get_raw_infrared()

        if self.timing == TSL_INTEGRATION_TIME_13MS:
            sat = TSL_CLIPPING_13MS
        elif self.timing == TSL_INTEGRATION_TIME_101MS:
            sat = TSL_CLIPPING_101MS
        else:
            sat = TSL_CLIPPING_402MS

        # Return 0 lux if the sensor is saturated
        if full > sat or ir > sat:
            print("sensor is saturated")
            return 0

        # Get the correct scale depending on the integration time
        if self.timing == TSL_INTEGRATION_TIME_13MS:
            scale = TSL_CHSCALE_TINT0
        elif self.timing == TSL_INTEGRATION_TIME_101MS:
            scale = TSL_CHSCALE_TINT1
        else:
            scale = 1 << TSL_CHSCALE

        # Scale for gain (1x or 16x)
        if not self.gain:
            scale = scale << 4

        # Scale the channel values
        full_scaled = (full * scale) >> TSL_CHSCALE
        ir_scaled = (ir * scale) >> TSL_CHSCALE

        # Find the ratio of the channel values (Channel1/Channel0)
        ratio1 = 0
        if full_scaled != 0:
            ratio1 = (ir_scaled << (TSL_RATIO_SCALE + 1)) / full_scaled

        # round the ratio value
        ratio = (int(ratio1) + 1) >> 1

        b = 0
        m = 0

        if self.pack == TSL_PACKAGE_T_FN_CL:
            if ratio >= 0 and ratio <= TSL_K1T:
                b = TSL_B1T
                m = TSL_M1T
            elif ratio <= TSL_K2T:
                b = TSL_B2T
                m = TSL_M2T
            elif ratio <= TSL_K3T:
                b = TSL_B3T
                m = TSL_M3T
            elif ratio <= TSL_K4T:
                b = TSL_B4T
                m = TSL_M4T
            elif ratio <= TSL_K5T:
                b = TSL_B5T
                m = TSL_M5T
            elif ratio <= TSL_K6T:
                b = TSL_B6T
                m = TSL_M6T
            elif ratio <= TSL_K7T:
                b = TSL_B7T
                m = TSL_M7T
            elif ratio > TSL_K8T:
                b = TSL_B8T
                m = TSL_M8T
        else:
            # PACKAGE_CS otherwise
            if (ratio >= 0) and (ratio <= TSL_K1C):
                b = TSL_B1C
                m = TSL_M1C
            elif ratio <= TSL_K2C:
                b = TSL_B2C
                m = TSL_M2C
            elif ratio <= TSL_K3C:
                b = TSL_B3C
                m = TSL_M3C
            elif ratio <= TSL_K4C:
                b = TSL_B4C
                m = TSL_M4C
            elif ratio <= TSL_K5C:
                b = TSL_B5C
                m = TSL_M5C
            elif ratio <= TSL_K6C:
                b = TSL_B6C
                m = TSL_M6C
            elif ratio <= TSL_K7C:
                b = TSL_B7C
                m = TSL_M7C
            elif ratio <= TSL_K8C:
                b = TSL_B8C
                m = TSL_M8C

        temp = (full_scaled * b) - (ir_scaled * m)

        # Do not allow negative lux value
        if temp < 0:
            temp = 0

        # Round lsb (2^(LUX_SCALE-1))
        temp += 1 << (TSL_LUX_SCALE - 1)

        # Strip off fractional portion
        lux = temp >> TSL_LUX_SCALE
        return lux
