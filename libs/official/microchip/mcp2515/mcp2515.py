#   Zerynth - libs - microchip-mcp2515/mcp2515.py
#
#   Zerynth library for mcp2515 component.
#
# @Author: m.cipriani
#
# @Date:   2017-11-24 10:47:11
# @Last Modified by:   m.cipriani
# @Last Modified time: 2018-03-30 12:39:16


import spi

TIMEOUTVALUE    = 50
MCP_SIDH        = 0
MCP_SIDL        = 1
MCP_EID8        = 2
MCP_EID0        = 3

MCP_TXB_EXIDE_M     = 0x08
MCP_DLC_MASK        = 0x0F
MCP_RTR_MASK        = 0x40

# Define SPI Instruction Set
MCP_WRITE           = 0x02
MCP_READ            = 0x03
MCP_BITMOD          = 0x05
MCP_LOAD_TX0        = 0x40
MCP_LOAD_TX1        = 0x42
MCP_LOAD_TX2        = 0x44
MCP_RTS_TX0         = 0x81
MCP_RTS_TX1         = 0x82
MCP_RTS_TX2         = 0x84
MCP_RTS_ALL         = 0x87
MCP_READ_RX0        = 0x90
MCP_READ_RX1        = 0x94
MCP_READ_STATUS     = 0xA0
MCP_RX_STATUS       = 0xB0
MCP_RESET           = 0xC0

# CANCTRL Register Values
MCP_MODE = {
    "NORMAL"    :  0x00,
    "SLEEP"     :  0x20,
    "LOOPBACK"  :  0x40,
    "LISTENONLY":  0x60,
    "CONFIG"    :  0x80,
    "POWERUP"   :  0xE0,
    "ONE_SHOT"  :  0x08
}

MODE_MASK       = 0xE0
ABORT_TX        = 0x10
CLKOUT_ENABLE   = 0x04
CLKOUT_DISABLE  = 0x00
CLKOUT_PS1      = 0x00
CLKOUT_PS2      = 0x01
CLKOUT_PS4      = 0x02
CLKOUT_PS8      = 0x03


# Define MCP2515 register addresses
MCP_RXF0SIDH    = 0x00
MCP_RXF0SIDL    = 0x01
MCP_RXF0EID8    = 0x02
MCP_RXF0EID0    = 0x03
MCP_RXF1SIDH    = 0x04
MCP_RXF1SIDL    = 0x05
MCP_RXF1EID8    = 0x06
MCP_RXF1EID0    = 0x07
MCP_RXF2SIDH    = 0x08
MCP_RXF2SIDL    = 0x09
MCP_RXF2EID8    = 0x0A
MCP_RXF2EID0    = 0x0B
MCP_BFPCTRL     = 0x0C
MCP_TXRTSCTRL   = 0x0D
MCP_CANSTAT     = 0x0E
MCP_CANCTRL     = 0x0F
MCP_RXF3SIDH    = 0x10
MCP_RXF3SIDL    = 0x11
MCP_RXF3EID8    = 0x12
MCP_RXF3EID0    = 0x13
MCP_RXF4SIDH    = 0x14
MCP_RXF4SIDL    = 0x15
MCP_RXF4EID8    = 0x16
MCP_RXF4EID0    = 0x17
MCP_RXF5SIDH    = 0x18
MCP_RXF5SIDL    = 0x19
MCP_RXF5EID8    = 0x1A
MCP_RXF5EID0    = 0x1B
MCP_TEC         = 0x1C
MCP_REC         = 0x1D
MCP_RXM0SIDH    = 0x20
MCP_RXM0SIDL    = 0x21
MCP_RXM0EID8    = 0x22
MCP_RXM0EID0    = 0x23
MCP_RXM1SIDH    = 0x24
MCP_RXM1SIDL    = 0x25
MCP_RXM1EID8    = 0x26
MCP_RXM1EID0    = 0x27
MCP_CNF3        = 0x28
MCP_CNF2        = 0x29
MCP_CNF1        = 0x2A
MCP_CANINTE     = 0x2B
MCP_CANINTF     = 0x2C
MCP_EFLG        = 0x2D

MCP_TXB0CTRL    = 0x30
MCP_TXB1CTRL    = 0x40
MCP_TXB2CTRL    = 0x50
MCP_TXB = [
  MCP_TXB0CTRL,
  MCP_TXB1CTRL,
  MCP_TXB2CTRL
]

MCP_RXB0CTRL    = 0x60
MCP_RXB0SIDH    = 0x61
MCP_RXB1CTRL    = 0x70
MCP_RXB1SIDH    = 0x71


MCP_TX_INT      = 0x1C #Enable all transmit interrup ts
MCP_TX01_INT    = 0x0C #Enable TXB0 and TXB1 interru pts
MCP_RX_INT      = 0x03 #Enable receive interrupts
MCP_NO_INT      = 0x00 #Disable all interrupts

MCP_TX01_MASK   = 0x14
MCP_TX_MASK     = 0x54

#Bits in the TXBnCTRL registers.
MCP_TXB_TXBUFE_M    = 0x80
MCP_TXB_ABTF_M      = 0x40
MCP_TXB_MLOA_M      = 0x20
MCP_TXB_TXERR_M     = 0x10
MCP_TXB_TXREQ_M     = 0x08
MCP_TXB_TXIE_M      = 0x04
MCP_TXB_TXP10_M     = 0x03
#In TXBnDLC
MCP_TXB_RTR_M       = 0x40                                 
MCP_RXB_IDE_M       = 0x08                                        
MCP_RXB_RTR_M       = 0x40                                        
#In RXBnSIDL, RXBnDLC
MCP_STAT_RXIF_MASK   = (0x03)
MCP_STAT_RX0IF       = (1<<0)
MCP_STAT_RX1IF       = (1<<1)

MCP_EFLG_RX1OVR     = (1<<7)
MCP_EFLG_RX0OVR     = (1<<6)
MCP_EFLG_TXBO       = (1<<5)
MCP_EFLG_TXEP       = (1<<4)
MCP_EFLG_RXEP       = (1<<3)
MCP_EFLG_TXWAR      = (1<<2)
MCP_EFLG_RXWAR      = (1<<1)
MCP_EFLG_EWARN      = (1<<0)
MCP_EFLG_ERRORMASK  = (0xF8)

MCP_BxBFS_MASK    = 0x30
MCP_BxBFE_MASK    = 0x0C
MCP_BxBFM_MASK    = 0x03

MCP_BxRTS_MASK    = 0x38
MCP_BxRTSM_MASK   = 0x07

#CANINTF Register Bits
MCP_RX0IF       = 0x01
MCP_RX1IF       = 0x02
MCP_TX0IF       = 0x04
MCP_TX1IF       = 0x08
MCP_TX2IF       = 0x10
MCP_ERRIF       = 0x20
MCP_WAKIF       = 0x40
MCP_MERRF       = 0x80

MCP_DLC_MASK        = 0x0F                                        
MCP_RTR_MASK        = 0x40                                        

MCP_RXB_RX_ANY      = 0x60
MCP_RXB_RX_EXT      = 0x40
MCP_RXB_RX_STD      = 0x20
MCP_RXB_RX_STDEXT   = 0x00
MCP_RXB_RX_MASK     = 0x60
MCP_RXB_BUKT_MASK   = (1<<2)

#CNF1 Register Values
SJW1            = 0x00
SJW2            = 0x40
SJW3            = 0x80
SJW4            = 0xC0

#CNF2 Register Values
BTLMODE         = 0x80
SAMPLE_1X       = 0x00
SAMPLE_3X       = 0x40

#CNF3 Register Values
SOF_ENABLE      = 0x80
SOF_DISABLE     = 0x00
WAKFIL_ENABLE   = 0x40
WAKFIL_DISABLE  = 0x00

MCPDEBUG        = (0)
MCPDEBUG_TXBUF  = (0)
MCP_N_TXBUFFERS = (3)

MCP_RXBUF_0 = (MCP_RXB0SIDH)
MCP_RXBUF_1 = (MCP_RXB1SIDH)

CANSENDTIMEOUT = (200)

#initial value of gCANAutoProcess
CANAUTOPROCESS = (1)
CANAUTOON  = (1)
CANAUTOOFF = (0)

CAN_STDID = (0)
CAN_EXTID = (1)

CANDEFAULTIDENT    = (0x55CC)
CANDEFAULTIDENTEXT = (CAN_EXTID)

MCP_STDEXT  = 0
MCP_STD     = 1
MCP_EXT     = 2
MCP_ANY     = 3

MAX_CHAR_IN_MESSAGE = 8

CAN_RATE = {
    "8MHZ" : {
        "5KBPS"   : [0xA7, 0xF6, 0x84],
        "10KBPS"  : [0x93, 0xF6, 0x84],
        "20KBPS"  : [0x89, 0xF6, 0x84],
        "31KBPS"  : [0x87, 0xE5, 0x83],
        "33KBPS"  : [0x85, 0xF6, 0x84],
        "40KBPS"  : [0x84, 0xF6, 0x84],
        "50KBPS"  : [0x84, 0xE5, 0x83],
        "80KBPS"  : [0x84, 0xD3, 0x81],
        "100KBPS" : [0x81, 0xF6, 0x84],
        "125KBPS" : [0x81, 0xE5, 0x83],
        "200KBPS" : [0x80, 0xF6, 0x84],
        "250KBPS" : [0x80, 0xE5, 0x83],
        "500KBPS" : [0x00, 0xD1, 0x81],
        "1000KBPS": [0x00, 0xC0, 0x80],
    },
    "16MHZ" : {
        "5KBPS"   : [0x3F, 0xFF, 0x87],
        "10KBPS"  : [0x67, 0xF6, 0x84],
        "20KBPS"  : [0x53, 0xF6, 0x84],
        "33KBPS"  : [0x4E, 0xE5, 0x83],
        "40KBPS"  : [0x49, 0xF6, 0x84],
        "50KBPS"  : [0x47, 0xF6, 0x84],
        "80KBPS"  : [0x44, 0xF6, 0x84],
        "100KBPS" : [0x44, 0xE5, 0x83],
        "125KBPS" : [0x43, 0xE5, 0x83],
        "200KBPS" : [0x41, 0xF6, 0x84],
        "250KBPS" : [0x41, 0xE5, 0x83],
        "500KBPS" : [0x40, 0xE5, 0x83],
        "1000KBPS": [0x00, 0xCA, 0x81],
    },
    "20MHZ" : {
        "40KBPS"  : [0x18, 0xD3, 0x81],
        "50KBPS"  : [0x49, 0xF6, 0x84],
        "80KBPS"  : [0xC4, 0xFF, 0x87],
        "100KBPS" : [0x44, 0xF6, 0x84],
        "125KBPS" : [0x44, 0xE5, 0x83],
        "200KBPS" : [0x44, 0xD3, 0x81],
        "250KBPS" : [0x41, 0xF6, 0x84],
        "500KBPS" : [0x40, 0xF6, 0x84],
        "1000KBPS": [0x00, 0xD9, 0x82],
    }
}

"""
.. module:: mcp2515

***************
 MCP2515 Module
***************
.. _datasheet: http://ww1.microchip.com/downloads/en/DeviceDoc/20001801H.pdf

This module contains the driver for Microchip MCP2515, a second generation 
stand-alone CAN controller. It is pin and function compatible with the MCP2510
and also includes upgraded features like faster throughput, databyte
filtering, and support for time-triggered protocols (datasheet_).

Example: ::
        
        from microchip.mcp2515 import mcp2515
        
        ...
        
        can = mcp2515.MCP2515(SPI0, D17, D16, clk=10000000)
        can.init(mcp2515.MCP_ANY, "500KBPS", "16MHZ")
        can.set_mode("NORMAL")

        ...
        
        can.send(canid, data)
    
    """

debug = False

class MCP2515(spi.Spi):
    """
===============
 MCP2515 class
===============


.. class:: MCP2515(dvr, cs, rst=None, clk=800000):

    Creates an instance of the MCP2515 class. This class allows the control of MCP2515 devices.
    
    :param drv: SPI Driver used '(SPI0, ...)'
    :param cs: Chip select of the SPI driver
    :param rst: Reset pin (default None)
    :param clk: Clock speed, default 800 kHz


    """
    def __init__(self, dvr, cs, rst=None, clk=800000):

        spi.Spi.__init__(self,cs,dvr,clock=clk)
        if rst:
            self.rst = rst
            pinMode(self.rst, OUTPUT)
            self._reset()
        sleep(100)
        #Identifier Type
        self.ext = 0
        #CAN ID - Extended (29 bit) or Standard (11 bit)
        self.canid = bytearray([0x00, 0x00, 0x00, 0x00])
        #Data Length Code
        self.dlc = 0
        #Data array
        self.data = bytearray(MAX_CHAR_IN_MESSAGE)
        #Remote request flag
        self.rtr = 0
        self.mcpmode = MCP_MODE["LOOPBACK"]
        self.buf = bytearray(1)

    def _reset(self):
        digitalWrite(self.rst,0)
        sleep(20)
        digitalWrite(self.rst,1)
        sleep(500)

    def _sw_reset(self):
        self.select()
        sleep(10)
        self.buf[0] = MCP_RESET
        self.write(self.buf)
        sleep(10)
        self.unselect()
        sleep(10)

    def _read_regs(self, addr,n=1):
        self.buf = bytearray(2)
        self.buf[0] = MCP_READ
        self.buf[1] = addr
        self.select()
        self.write(self.buf)
        res = self.read(n)
        self.unselect()
        self.buf = bytearray(1)
        return res

    def _set_regs(self, addr, data):
        if type(data) != PLIST:
            data = [data]
        self.buf = bytearray(len(data)+2)
        self.buf[0] = MCP_WRITE
        self.buf[1] = addr
        for i,elem in enumerate(data):
            self.buf[i+2] = elem
        self.select()
        self.write(self.buf)
        self.unselect()
        self.buf = bytearray(1)

    def _read_status(self):
        self.buf[0] = MCP_READ_STATUS
        self.select()
        self.write(self.buf)
        res = self.read(1)[0]
        # print(res)
        self.unselect()
        return res

    def _modify_register(self, addr, mask, value):
        self.buf = bytearray(4)
        self.select()
        for i,elem in enumerate([MCP_BITMOD, addr, mask, value]):
            self.buf[i] = elem
        self.write(self.buf)
        self.unselect()
        self.buf = bytearray(1)

    def _set_canctrl_mode(self, mode):
        self._modify_register(MCP_CANCTRL, MODE_MASK, mode)
        if debug:
            print("debug")
            i = self._read_regs(MCP_CANCTRL)[0]
            i &= MODE_MASK
            if i == mode:
                print("ok")
            else:
                raise InvalidHardwareStatusError

    def _config_rate(self, spd, clk):
        if clk not in CAN_RATE or spd not in CAN_RATE[clk]:
            raise ValueError
        self._set_regs(MCP_CNF1, CAN_RATE[clk][spd][0])
        self._set_regs(MCP_CNF2, CAN_RATE[clk][spd][1])
        self._set_regs(MCP_CNF3, CAN_RATE[clk][spd][2])

    def _write_masks_and_filters(self, addr, ext, canid):
        # print(canid)
        data = [0]*4
        idl = canid[0] + (canid[1] << 8)
        idh = canid[2] + (canid[3] << 8)
        data[MCP_EID0] = idl & 0xFF
        data[MCP_EID8] = idl >> 8 & 0xFF
        if ext:
            data[MCP_SIDL] = (idh & 0x03) & 0xFF
            data[MCP_SIDL] += ((idh & 0x1C) << 3) & 0xFF
            data[MCP_SIDL] |= MCP_TXB_EXIDE_M
            data[MCP_SIDH] = (idh >> 5 ) & 0xFF
        else:
            data[MCP_SIDL] = ((idh & 0x07) << 5) & 0xFF
            data[MCP_SIDH] = (idh >> 3 ) & 0xFF
        self._set_regs(addr, data)

    def _init_can_buffers(self):
        
        std = 0
        ext = 1
        #set both mask to 0
        self._write_masks_and_filters(MCP_RXM0SIDH, ext, self.canid)
        self._write_masks_and_filters(MCP_RXM1SIDH, ext, self.canid)
        #set all filters to 0
        self._write_masks_and_filters(MCP_RXF0SIDH, ext, self.canid)
        self._write_masks_and_filters(MCP_RXF1SIDH, std, self.canid)
        self._write_masks_and_filters(MCP_RXF2SIDH, ext, self.canid)
        self._write_masks_and_filters(MCP_RXF3SIDH, std, self.canid)
        self._write_masks_and_filters(MCP_RXF4SIDH, ext, self.canid)
        self._write_masks_and_filters(MCP_RXF5SIDH, std, self.canid)

        #clear, deactivate the three transmit buffers
        self._set_regs(MCP_TXB0CTRL, [0]*14)
        self._set_regs(MCP_TXB1CTRL, [0]*14)
        self._set_regs(MCP_TXB2CTRL, [0]*14)

        self._set_regs(MCP_RXB0CTRL, 0)
        self._set_regs(MCP_RXB1CTRL, 0)

    def _write_id(self, addr, ext, canid):
        idl = canid[0] + (canid[1] << 8)
        idh = canid[2] + (canid[3] << 8)
        data = [0]*4
        if ext:
              data[MCP_EID0] = idl & 0xFF
              data[MCP_EID8] = (idl >> 8) & 0xFF
              data[MCP_SIDL] = (idh & 0x03) & 0xFF
              data[MCP_SIDL] += ((idh & 0x1C) << 3) & 0xFF
              data[MCP_SIDL] |= MCP_TXB_EXIDE_M
              data[MCP_SIDH] = (idh >> 5 ) & 0xFF
        else:
              data[MCP_EID0] = 0
              data[MCP_EID8] = 0
              data[MCP_SIDL] = ((idh & 0x07) << 5) & 0xFF
              data[MCP_SIDH] = (idh >> 3) & 0xFF
        self._set_regs(addr, data)

    def _read_id(self, addr):
        buf = self._read_regs(addr, n=4)
        self.ext = 0
        idl = 0
        idh = ((buf[MCP_SIDH]<<3) + (buf[MCP_SIDL]>>5)) & 0xFFFF
        if (buf[MCP_SIDL] & MCP_TXB_EXIDE_M) ==  MCP_TXB_EXIDE_M:
            #extended id
            idh = (idh<<2) + (buf[MCP_SIDL] & 0x03)
            idl = buf[MCP_EID8]
            idl = idl<<8 + buf[MCP_EID0]
            self.ext = 1
        self.canid = bytearray([idl & 0xFF, (idl >> 8) & 0xFF, idh & 0xFF, (idh >> 8) & 0xFF])

    def _write_can_msg(self, sidh_addr):
        self._set_regs(sidh_addr+5, self.data, self.dlc)
        if self.rtr:
            self.dlc |= MCP_RTR_MASK
        self._set_regs(sidh_addr+4, self.dlc)
        self._write_id(sidh_addr, self.ext, self.canid)

    def _read_can_msg(self, sidh_addr):
        self._read_id(sidh_addr)
        ctrl = self._read_regs(sidh_addr-1)[0]
        self.dlc = self._read_regs(sidh_addr+4)[0]
        self.rtr = 0
        if ctrl == 0x08:
            self.rtr = 1
        self.dlc &= MCP_DLC_MASK
        return self._read_regs(sidh_addr+5, self.dlc)

    def _find_empty_transmit_buffer(self):
        res = None #ALLTXB_BUSY
        for elem in MCP_TXB:
            ctrlval = self._read_regs(elem)[0]
            if ctrlval & MCP_TXB_TXREQ_M == 0:
                res = elem+1
                break
        return res

    def _set_msg(self, canid, rtr, ext, data):
        self.canid = canid
        self.rtr = rtr
        self.ext = ext
        self.dlc = len(data)
        self.data = data

    def _clear_msg(self):
        self.canid = bytearray(4)
        self.dlc = 0
        self.ext = 0
        self.rtr = 0
        self.data = bytearray(MAX_CHAR_IN_MESSAGE)

    def _send_msg(self):
        attempts = 0
        txbuf = None
        while txbuf == None and attempts < 100:
            txbuf = self._find_empty_transmit_buffer()
            attempts += 1
        
        if attempts >= 100:
            raise TimeoutError

        self._write_can_msg(txbuf)
        self._modify_register(txbuf-1, MCP_TXB_TXREQ_M, MCP_TXB_TXREQ_M)

        attempts = 0
        full = 1
        while full and attempts < 100:
            full = self._read_regs(txbuf-1)[0]
            full = full & MCP_TXB_TXREQ_M
            attempts += 1
        
        # print(full,attempts,full & MCP_TXB_TXREQ_M)

        if attempts >= 150:
            raise TimeoutError

    def _read_msg(self):
        msg = None
        status = self._read_status()
        # print("status",status)
        if status & MCP_STAT_RX0IF:
            # print("ch0")
            msg = self._read_can_msg(MCP_RXBUF_0)
            self._modify_register(MCP_CANINTF, MCP_RX0IF, 0)
        elif status & MCP_STAT_RX1IF:
            # print("ch1")
            msg = self._read_can_msg(MCP_RXBUF_1)
            self._modify_register(MCP_CANINTF, MCP_RX1IF, 0)
        return msg

    def init(self, idmode, speed, clock):
        """
.. method:: init(idmode, speed, clock)       

    Initializes the MCP2515 chip 
    
    :param idmode: set the RX buffer id mode (selectable from mcp2515.MCP_STDEXT, mcp2515.MCP_STD, mcp2515.MCP_EXT, or mcp2515.MCP_ANY
    :param speed: set the speed of the CAN communication 
    :param clock: set the click of the CAN Communication

    Possible combination of values for Clock and Speed are:

    * Clock --> 8MHZ
            
        =========== ================
        Clock       Speed
        =========== ================
        "8MHZ"      "5KBPS"           
        "8MHZ"      "10KBPS"           
        "8MHZ"      "20KBPS"           
        "8MHZ"      "31KBPS"           
        "8MHZ"      "33KBPS"           
        "8MHZ"      "40KBPS"           
        "8MHZ"      "50KBPS"           
        "8MHZ"      "80KBPS"           
        "8MHZ"      "100KBPS"           
        "8MHZ"      "125KBPS"           
        "8MHZ"      "200KBPS"           
        "8MHZ"      "250KBPS"           
        "8MHZ"      "500KBPS"
        "8MHZ"      "1000KBPS"
        =========== ================

    * Clock --> 16MHZ
        
        =========== ================
        Clock       Speed
        =========== ================
        "16MHZ"     "5KBPS"           
        "16MHZ"     "10KBPS"           
        "16MHZ"     "20KBPS"           
        "16MHZ"     "33KBPS"           
        "16MHZ"     "40KBPS"           
        "16MHZ"     "50KBPS"           
        "16MHZ"     "80KBPS"           
        "16MHZ"     "100KBPS"           
        "16MHZ"     "125KBPS"           
        "16MHZ"     "200KBPS"           
        "16MHZ"     "250KBPS"           
        "16MHZ"     "500KBPS"           
        "16MHZ"     "1000KBPS"
        =========== ================

    * Clock --> 20MHZ
        
        =========== ================
        Clock       Speed
        =========== ================
        "20MHZ"     "40KBPS"   
        "20MHZ"     "50KBPS"   
        "20MHZ"     "80KBPS"   
        "20MHZ"     "100KBPS"   
        "20MHZ"     "125KBPS"   
        "20MHZ"     "200KBPS"   
        "20MHZ"     "250KBPS"   
        "20MHZ"     "500KBPS"   
        "20MHZ"     "1000KBPS"   
        =========== ================

        """
        self._sw_reset()
        self._set_canctrl_mode(MCP_MODE["CONFIG"])
        self._config_rate(speed, clock)
        self._init_can_buffers()
        #interrupt mode
        self._set_regs(MCP_CANINTE, MCP_RX0IF | MCP_RX1IF)
        #set BF pins as GPO
        self._set_regs(MCP_BFPCTRL, MCP_BxBFS_MASK | MCP_BxBFE_MASK)
        #set RTS pin as GPI
        self._set_regs(MCP_TXRTSCTRL,0x00)

        #set mode
        if idmode == MCP_ANY:
            self._modify_register(MCP_RXB0CTRL, MCP_RXB_RX_MASK | MCP_RXB_BUKT_MASK, MCP_RXB_RX_ANY | MCP_RXB_BUKT_MASK)
            self._modify_register(MCP_RXB1CTRL, MCP_RXB_RX_MASK, MCP_RXB_RX_ANY)
        elif idmode == MCP_STD:
            self._modify_register(MCP_RXB0CTRL, MCP_RXB_RX_MASK | MCP_RXB_BUKT_MASK, MCP_RXB_RX_STD | MCP_RXB_BUKT_MASK)
            self._modify_register(MCP_RXB1CTRL, MCP_RXB_RX_MASK, MCP_RXB_RX_STD)
        elif idmode == MCP_EXT:
            self._modify_register(MCP_RXB0CTRL, MCP_RXB_RX_MASK | MCP_RXB_BUKT_MASK, MCP_RXB_RX_EXT | MCP_RXB_BUKT_MASK)
            self._modify_register(MCP_RXB1CTRL, MCP_RXB_RX_MASK, MCP_RXB_RX_EXT)
        elif idmode == MCP_STDEXT:
            self._modify_register(MCP_RXB0CTRL, MCP_RXB_RX_MASK | MCP_RXB_BUKT_MASK, MCP_RXB_RX_STDEXT | MCP_RXB_BUKT_MASK)
            self._modify_register(MCP_RXB1CTRL, MCP_RXB_RX_MASK, MCP_RXB_RX_STDEXT)
        else:
            raise ValueError

        self._set_canctrl_mode(MCP_MODE["LOOPBACK"])

    def set_mode(self, mode):
        """
.. method:: set_mode(mode)       

    Sets the operation mode of the MCP2515
    
    :param mode: operation mode ("NORMAL", "SLEEP", "LOOPBACK", "LISTENONLY", "CONFIG", "POWERUP", "ONE_SHOT")
        
        """
        if mode not in MCP_MODE:
            raise ValueError
        self.mcpmode = mode
        self._set_canctrl_mode(MCP_MODE[mode])

    def init_mask(self, num, data, ext):
        """
.. method:: init_mask(num, data, ext)      

    Initializes Masks
    
    :param num: 0 to set mask 0 on RX buffer, 1 to set mask 1 on RX buffer
    :param data: Data Mask
    :param ext:  0 for standard ID, 1 for Extended ID 
        
        """
        res = self._set_canctrl_mode(MCP_MODE["CONFIG"])
        if res > 0:
            raise HardwareInitializationError

        if num == 0:
            self._write_masks_and_filters(MCP_RXM0SIDH, ext, data)
        elif num == 1:
            self._write_masks_and_filters(MCP_RXM1SIDH, ext, data)
        else:
            raise ValueError

        self._set_canctrl_mode(self.mcpmode)

    def init_filter(self, num, data, ext):
        """
.. method:: init_filter(num, data, ext)      

    Initializes Filters
    
    :param num: number of filter to be set in RX buffer (from 0 to 5)
    :param data: Data Filter
    :param ext:  0 for standard ID, 1 for Extended ID 
        
        """
        res = self._set_canctrl_mode(MCP_MODE["CONFIG"])
        if res > 0:
            raise HardwareInitializationError

        if num == 0:
            self._write_masks_and_filters(MCP_RXF0SIDH, ext, data);
        elif num == 1:
            self._write_masks_and_filters(MCP_RXF1SIDH, ext, data);
        elif num == 2:
            self._write_masks_and_filters(MCP_RXF2SIDH, ext, data);
        elif num == 3:
            self._write_masks_and_filters(MCP_RXF3SIDH, ext, data);
        elif num == 4:
            self._write_masks_and_filters(MCP_RXF4SIDH, ext, data);
        elif num == 5:
            self._write_masks_and_filters(MCP_RXF5SIDH, ext, data);
        else:
            raise ValueError

        self._set_canctrl_mode(self.mcpmode)

    def send(self, canid, data, ext=None):
        """
.. method:: send(canid, data, ext=None)      

    Sends CAN messages
    
    :param canid: ID of the CAN message (bytearray of 4 bytes)
    :param data: Data to be sent (list of 8 bytes)
    :param ext:  0 for standard ID, 1 for Extended ID (default None - auto detected) 
        
        """
        if type(canid) != PBYTEARRAY:
            raise TypeError
        elif len(canid) != 4:
            raise ValueError
        if type(data) != PLIST:
            raise TypeError
        if len(data) > 8:
            raise IndexError
        rtr = 0
        if ext is None:
            ext = 0
            if canid[3] & 0x80 == 0x80:
                ext = 1
            if canid[3] & 0x40 == 0x40:
                rtr = 1
        self._set_msg(canid, rtr, ext, data)
        self._send_msg()

    def recv(self):
        """
.. method:: recv()      

    Receives CAN messages returnung CAN id value and related data message
    
    Returns canid, msg    
        """
        msg = self._read_msg()
        canid = self.canid
        if msg is not None:
            if self.ext:
                canid[3] |= 0x80
            if self.rtr:
                canid[3] |= 0x40
        return canid, msg

    def check_recv(self):
        status = self._read_status()
        if status & MCP_STAT_RXIF_MASK:
            return True
        return None

    def check_error(self):
        eflag = self._read_regs(MCP_EFLG)[0]
        if eflag & MCP_EFLG_ERRORMASK:
            return True
        return None

    def get_error(self):
        return self._read_regs(MCP_EFLG)[0]

    def error_count_rx(self):
        return self._read_regs(MCP_REC)[0]

    def error_count_tx(self):
        return self._read_regs(MCP_TEC)[0]

    def enable_one_shot_tx(self):
        self._modify_register(MCP_CANCTRL, MCP_MODE["ONE_SHOT"], MCP_MODE["ONE_SHOT"])
        if (self._read_regs(MCP_CANCTRL)[0] & MCP_MODE["ONE_SHOT"]) != MCP_MODE["ONE_SHOT"]:
            return False
        return True

    def disable_one_shot_tx(self):
        self._modify_register(MCP_CANCTRL, MCP_MODE["ONE_SHOT"], 0)
        if (self._read_regs(MCP_CANCTRL)[0] & MCP_MODE["ONE_SHOT"]) != 0:
            return False
        return True

    def abort_tx(self):
        self._modify_register(MCP_CANCTRL, ABORT_TX, ABORT_TX)
        if(self._read_regs(MCP_CANCTRL)[0] & ABORT_TX) != ABORT_TX:
            return False
        return True

    def set_GPO(self, data):
        self._modify_register(MCP_BFPCTRL, MCP_BxBFS_MASK, (data<<4))

    def set_GPI(self):
        res = self.read_regs(MCP_TXRTSCTRL) & MCP_BxRTS_MASK
        return res
  





