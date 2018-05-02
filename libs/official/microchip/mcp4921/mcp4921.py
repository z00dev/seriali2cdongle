#   Zerynth - libs - microchip-mcp4921/mcp4921.py
#
#   Zerynth library for mcp4921 component.
#
# @Author: andreabau
#
# @Date:   2017-08-25 12:00:04
# @Last Modified by:   Andrea
# @Last Modified time: 2017-08-28 10:30:41
"""
.. module:: mcp4921

****************
 MCP4921 Module
****************

This module contains the driver for Microchip MCP4921 single channel 12-bit digital to analog converter
with SPI serial interface (`datasheet <http://ww1.microchip.com/downloads/en/DeviceDoc/22248a.pdf>`_).

Example: ::

        from microchip.mcp4921 import mcp4921

        ...

        mcp = mcp4921.MCP4921(SPI0, D17)
        mcp.set_value(1600)

    """
import spi

BUFFERED    = 0x40
GAIN_1      = 0x20
NO_SHDN     = 0x10

class MCP4921(spi.Spi):
    """
===============
 MCP4921 class
===============


.. class:: MCP4921(spidrv, cs, clk = 400000)

    Creates an instance of the MCP4921 class.

    :param spidrv: SPI Bus used '(SPI0, ...)'
    :param cs: Chip select pin
    :param clk: Clock speed, default 400 kHz

    """

    def __init__(self, spidrv, cs, clk=400000):
        spi.Spi.__init__(self, cs, spidrv, clock=clk)

    def set_value(self, v, gain=1, buff=False):
        """
        .. method:: set_value(v, gain = 1, buff = False)

            Sends the 12-bit value *v* to the DAC. The gain of the output amplifier can be set through *gain* parameter,
            valid values are ``1`` and ``2``.

            Analog Output Voltage = ( v / 4096) * Vref * gain 

            If *buff* is ``True``, the device buffers the Voltage Reference input increasing the input impedance but limiting
            the input range and frequency response. If *buff* is ``False`` the input range is wider (from 0V to Vdd) and the 
            typical input impedence is 165 kOhm with 7pF.
            If in Shutdown mode, the device is changed to Active mode. In this case the output settling time
            increases to 10 us.
        """
        
        h_b = NO_SHDN
        if buff:
            h_b |= BUFFERED

        if gain != 2:
            h_b |= GAIN_1

        h_b |= (v >> 8) & 0x0F

        l_b = v & 0xFF

        cmd = bytearray(2)
        cmd[0] = h_b
        cmd[1] = l_b

        self.lock()
        self.select()
        self.write(cmd)
        self.unselect()
        self.unlock()

    def shutdown(self):
        """
        .. method:: shutdown()

            Shutdown the device. During Shutdown mode, most of the internal circuits are turned off for 
            power savings and there will be no analog output.
        """
        cmd = bytearray(2)
        cmd[0] = 0
        cmd[1] = 0
        self.lock()
        self.select()
        self.write(cmd)
        self.unselect()
        self.unlock()
