#   Zerynth - zerynth-libs - semtech-sx1503/sx1503.py
#
#   Zerynth library for Semtech SX1503
#
#   Interrupt handling and programmable logic functions are not implemented
#
# @Author: andreabau
#
# @Date:   2017-11-09 12:19:23
# @Last Modified by:   andreabau
# @Last Modified time: 2018-01-12 16:26:20
"""
.. module:: sx1503

**************
SX1503 Module
**************

.. _datasheet: http://www.semtech.com/images/datasheet/sx150x.pdf

This module contains the Zerynth driver for Semtech SX1503 low voltage General Purpose parallel Input/Output.
The unit allows easy serial expansion of I/O through a standard 400kHz I2C interface.
Interrupt handling and programmable logic functions are not implemented (datasheet_).

"""
import i2c


REG_DATA_B  = 0x00
# REG_DATA_A  = 0x01
REG_DIR_B   = 0x02
# REG_DIR_A   = 0x03
REG_PU_B    = 0x04
# REG_PU_A    = 0x05
REG_PD_B    = 0x06
# REG_PD_A    = 0x07
# REG_INT_M_B = 0x08
# REG_INT_M_A = 0x09
# REG_SEN_H_B = 0x0A
# REG_SEN_H_A = 0x0B
# REG_SEN_L_B = 0x0C
# REG_SEN_L_A = 0x0D
# REG_INT_S_B = 0x0E
# REG_INT_S_A = 0x0F
# REG_EVT_B   = 0x10
# REG_EVT_A   = 0x11
# REG_PLD_M_B = 0x20
# REG_PLD_M_A = 0x21
# REG_PLD_T0B = 0x22
# REG_PLD_T0A = 0x23
# REG_PLD_T1B = 0x24
# REG_PLD_T1A = 0x25
# REG_PLD_T2B = 0x26
# REG_PLD_T2A = 0x27
# REG_PLD_T3B = 0x28
# REG_PLD_T3A = 0x29
# REG_PLD_T4B = 0x2A
# REG_PLD_T4A = 0x2B

REG_ADV     = 0xAD


class SX1503(i2c.I2C):
    """
    
===============
 SX1503 class
===============

.. class:: SX1503(drvname, clk=400000)

    Creates an intance of the SX1503 class.

    :param drvname: I2C Bus used '( I2C0, ... )'
    :param clk: Clock speed, default 400kHz
    
    Example: ::
        
        from semtech.sx1503 import sx1503
        
        ...
        
        port_expander = sx1503.SX1503(I2C1)
        port_expander.pinMode(10,INPUT_PULLUP)
        
        state = port_expander.digitalRead(10)
        
        port_expander.pinMode(0,OUTPUT)
        port_expander.digitalWrite(0,HIGH)
        
        
    """
    def __init__(self,i2cdrv, addr = 0x20, clk=400000):
        i2c.I2C.__init__(self, i2cdrv, 0x20, clk)
        self.start()
    
    
    def _safe_change(self,reg,bitn,val):
        o_reg = self.write_read(reg,1)[0]
        bit_mask = 1 << bitn
        n_reg = ((o_reg & (~bit_mask)) | (val << bitn))
        self.write_bytes(reg, n_reg)
    
    
    def pinMode(self,pin,mode):
        """
    .. method:: pinMode(pin, mode)
        
        Select a mode for a pin.
        Valid *pin* values are from ``0`` to ``15`` included.
        Available modes are:
        
            * ``INPUT``
            * ``INPUT_PULLUP``
            * ``INPUT_PULLDOWN``
            * ``OUTPUT``
        
        
        """
        if pin>7:
            # pins from 8 to 15 are in bank B
            delta_addr = 0
        else:
            # pins from 0 to 7 are in bank A
            delta_addr = 1
        
        pin = pin%8
        
        # set direction
        if mode == OUTPUT:
            self._safe_change(REG_DIR_B+delta_addr,pin,0)
        else:
            self._safe_change(REG_DIR_B+delta_addr,pin,1)
        
            # set pullup
            if mode == INPUT_PULLUP:
                self._safe_change(REG_PU_B+delta_addr,pin,1)
            else:
                self._safe_change(REG_PU_B+delta_addr,pin,0)
            
            # set pulldown
            if mode == INPUT_PULLDOWN:
                self._safe_change(REG_PD_B+delta_addr,pin,1)
            else:
                self._safe_change(REG_PD_B+delta_addr,pin,0)

    
    def get_port(self,port):
        """
    .. method:: get_port(port)

        Returns the state of all pins on port *port*.
        As a consequence of having 8 pins for port, returned value can be between ``0`` and ``255``.
        
        ===== ======== =========
        port  I/O bank  pins
        ===== ======== =========
        0     A         0 to 7
        1     B         8 to 15
        ===== ======== =========
        
        
        """
        if port == 0:
            # I/O bank A
            delta_addr = 1
        else:
            # I/O bank B
            delta_addr = 0
        
        return self.write_read(REG_DATA_B+delta_addr,1)[0]
        
    
    def digitalRead(self,pin):
        """
    .. method:: digitalRead(pin)

        Returns the state of pin *pin*. The state can be ``0`` or ``1``.

        """
        if pin>7:
            # pins from 8 to 15 are in bank B
            port = 1
        else:
            # pins from 0 to 7 are in bank A
            port = 0
        
        pin = pin%8
        
        pins = self.get_port(port)
        return ((pins  >>pin) & 1)
    
    def digitalWrite(self,pin,val):
        """
    .. method:: digitalWrite(pin, val)

        Set pin *pin* to value *val*. Value can be ``0`` or ``1``.

        """
        if pin>7:
            # I/O bank B
            delta_addr = 0
        else:
            # I/O bank A
            delta_addr = 1

        pin = pin%8

        self._safe_change(REG_DATA_B+delta_addr,pin,val)

    def set_port(self,port,val):
        """
    .. method:: set_port(port, val)
        
        Set all pins on port *port* to value *val*.
        *val* MUST be between ``0`` and ``255``.

        """
        if port == 0:
            # I/O bank A
            delta_addr = 1
        else:
            # I/O bank B
            delta_addr = 0
        
        self.write_bytes(REG_DATA_B+delta_addr,val)
    
    def set_boost(self,mode):
        """
    .. method:: set_boost(mode)
    
        Set the boost mode (cfr. par 2.2.1 of the datasheet).
        
        ===== ============
        mode   boost mode
        ===== ============
        0       OFF
        1       ON
        ===== ============

        """
        reg = (mode&1) << 1
        
        self.write_bytes(REG_ADV,reg)