#   Zerynth - libs - microchip-mcp3201/mcp3201.py
#
#   Zerynth library for mcp3201 component.
#
# @Author: andreabau
#
# @Date:   2017-06-19 13:18:43
# @Last Modified by:   andreabau
# @Last Modified time: 2017-08-28 11:37:31
"""
.. module:: mcp3201

****************
 MCP3201 Module
****************

This module contains the driver for Microchip MCP3201 analog to digital converter with
SPI serial interface (`datasheet <http://ww1.microchip.com/downloads/en/DeviceDoc/21290F.pdf>`_).

Example: ::
        
        from microchip.mcp3201 import mcp3201
        
        ...
        
        mcp = mcp3201.MCP3201(SPI0, D17)
        value = mcp.get_raw_data()
    
    """

import spi

class MCP3201(spi.Spi):
    """
===============
 MCP3201 class
===============


.. class:: MCP3201(spidrv, cs, clk = 400000)

    Creates an instance of the MCP3201 class.
    
    :param spidrv: SPI Bus used '(SPI0, ...)'
    :param cs: Chip select pin
    :param clk: Clock speed, default 400 kHz
    
    """
    def __init__(self, spidrv, cs, clk=400000 ):
        spi.Spi.__init__(self, cs, spidrv, clock=clk)
    
    
    def get_raw_data(self):
        """
        
    .. method:: get_raw_data()
        
        Return the conversion result as an integer between 0 and 4095 (12 bit).
        The digital output code is determined by the reference voltage *Vref* and the analog input voltage *Vin*:
        
        Digital output code = 4096 * *Vin* / *Vref*
        
        """
        self.lock()
        self.select()
        res = self.read(2)
        self.unselect()
        self.unlock()
        raw = ((res[0] & 0x1F)<<8 | res[1])>>1
        return raw
    
