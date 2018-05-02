"""
.. module:: bluefruit

****************
Bluefruit Module
****************

This module implements the driver for the Adafruit Bluefruit LE SPI products family, based on Bluefruit firmware v0.6.7 or higher (`link <https://www.adafruit.com/products/2746>`_).

Data between the mcu and the Bluefruit hardware is exchanged by SPI or serial communication. However, this module has support for SPI only.


    """


from adafruit.bluefruit import sdep
import spi
import streams
import fifo

blsp=None


def init(spidrv,nss,irqpin):
    """
.. function:: init(spidrv,nss,irqpin)

    Manually initializes the Bluefruit peripheral by activating the following communication setup:
       
       * *spidrv* is the SPI peripheral to use (usually SPI0 for devices with an Arduino compatible layout)
       * *nss* is the chip select pin (usually D8)
       * *irqpin* is the pin used by the Bluefruit hardware to signal incoming messages (usually D7)

    The SPI driver is started and the Bluefruit initialization sequence is sent.

    """
    global blsp
    blsp = spi.Spi(nss,SPI0,4000000)
    blsp.start()
    pinMode(irqpin,INPUT)
    sdep.init(blsp,irqpin)
    sdep.send_packet(0xBEEF,bytes())
    sleep(1000)

err=0

def _at(cmd):
    global err
    sdep.at(cmd+"\n")
    try:
        res = sdep.ta()
        err=0
        return str(res)
    except TimeoutError:
        err=1
    except Exception:
        err=2
    return None

def _check(res):
    if res is None:
        return (False,"")
    elif res.endswith("OK\r\n"):
        return (True,res[:-4])
    elif res.endswith("ERROR\r\n"):
        return (False,res[:-7])
    else:
        return (False,"")

def hard_reset():
    """
.. function:: hard_reset()

    Performs a factory reset. Returns True on success.

    """
    st,res = _check(_at("AT+FACTORYRESET"))
    sleep(1500)
    return st

def reset():
    """
.. function:: reset()

    Performs a software reset. Returns True on success.

    """
    st,res = _check(_at("ATZ"))
    sleep(1500)
    return st

def data_to_ascii(uuid):
    if type(uuid)==PSMALLINT:
        if uuid<256:
            return hex(uuid)
        elif uuid<65536:
            uuid = [uuid&0xff,uuid>>8]
        else:
            uuid = [uuid&0xff,(uuid>>8)&0xff,(uuid>>16)&0xff,(uuid>>24)&0xff]
    elif type(uuid)==PSTRING:
        uuid=bytes(uuid)
    if len(uuid)==1:
        return hex(uuid[0])
    lst = [hex(c,"") for c in uuid]
    return "-".join(lst)

def ascii_to_data(data):
    if data.startswith("0x"):
        return int(data,16)
    flds = data.split("-")
    res = bytearray(len(flds))
    for i,f in enumerate(flds):
        res[i]=int(f,16)
    return res

def gap_name(name=None):
    """
.. function:: gap_name(name=None)

    If *name* is None, returns the current Bluefruit device name. Otherwise changes the current name to *name*.
    Returns True on success.

    """
    if name is None:
        st,res = _check(_at("AT+GAPDEVNAME"))
        if st:
            return res
        return False
    else:
        st,res = _check(_at("AT+GAPDEVNAME="+str(name)))
        if st:
            return reset()
        return False

def gap_adv(data):
    """
.. function:: gap_adv(data)

    Setup advertising data. Please refer to `this resource <https://www.bluetooth.org/DocMan/handlers/DownloadDoc.ashx?doc_id=302735&_ga=1.4683440.245686596.1452259520>`_ for 
    a list of possible values accepted by the BLE standard.

    *data* is an iterable containing blocks of data in the following format:
    
        * byte 1: length of the block (n)
        * byte 2: type of the block
        * byte 3 to n: value of the block

    Usually *data* is made of a flag block, followed by blocks advertising BLE services.
    
    For example the sequence [0x02, 0x01, 0x06, 0x05, 0x02, 0x0d, 0x18, 0x0a, 0x18] is an encoding of the following info:
    
        * 0x02: length of block 1
        * 0x01: type of the block ("Flag")
        * 0x06: value of the block
        * 0x05: length of block 2
        * 0x02: type of block ("List of 16-bit Service UUID")
        * 0x180d, 0x180a: two 16 bit uuids. The first one is for a "Heart rate" service, the second for "Device Info" service.

    Refer to `this <https://www.bluetooth.org/en-us/specification/assigned-numbers/generic-access-profile>`_ for a list of block types.

    Returns True on success.
    
    """
    st,res = _check(_at("AT+GAPSETADVDATA="+data_to_ascii(data)))
    if st:
        return reset()
    return False

def gap_is_connected():
    """
.. function:: gap_is_connected()

    Returns 1 if Bluefruit hardware is connected to a client, 0 if not connected. Returns None on failure.

    """
    st,res = _check(_at("AT+GAPGETCONN"))
    if st:
        return int(res)
    return None

def gatt(cfg=None):
    """
.. function:: gatt(cfg=None)

    If *cfg* is None returns the current `GATT <https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gatt>`_ configuration.
    
    Otherwise BLuefruit configuration is cleared first and then changed to *cfg*.
    
    The format of *cfg* is a list of lists: ::
    
        cfg = [
            [0,0x180D],                     # Service with UUID 0x180D = Heart Rate
              [1,0x2a37,(0x00,0x40),0x10],  # Characteristic of last defined service
              [2,0x2a38,3,0x02]             # another characteristic
        ]
    
    In the main list, a service is identified by a two elements list where the first element is an id (can be set to zero)
    and the second element is the UUID of the service. If the UUID of the service is more than 32 bit, it can be passed as a tuple of bytes or as a bytearray.
    
    Every list of 4 elements identifies a characteristic of the previously defined service. Characteristics are made of:
    
        * a handle at position 0: can be set to zero
        * a characteristic UUID: can be 16, 32 or 128 bits
        * a default value for the characteristic: can be a string, an integer or an iterable of bytes.
        * a permission flag: refer to `this <https://learn.adafruit.com/introducing-the-adafruit-bluefruit-spi-breakout/ble-gatt>`_ for reference

    
    Returns the configuration activated on the device or None on failure. After a configuration is successfully set, the return value
    contains handles modified to the actual ones choosen by the device.
    
    """
    if cfg is None:
        st,res = _check(_at("AT+GATTLIST"))
        if st:
            lines = res.split("\r\n")
            cc = []
            for line in lines:
                ll = line.split(",")
                if len(ll)==2:
                    #service
                    tt = ll[0].split("=")
                    rr = ll[1].split("=")
                    cc.append([int(tt[1],16),int(rr[1],16)])
                elif len(ll)==6:
                    #characteristic
                    tt = ll[0].split("=")
                    rr = ll[1].split("=")
                    pp = ll[2].split("=")
                    vv = ll[5].split("=")
                    cc.append([int(tt[1],16),int(rr[1],16),ascii_to_data(vv[1]),int(pp[1],16)])
            return cc
        return []
    else:
        st,res = _check(_at("AT+GATTCLEAR"))
        last_service = 0
        if st:
            for lst in cfg:
                if len(lst)==2:
                    handle,value = lst
                    if type(value)==PSMALLINT:
                        ss,tr = _check(_at("AT+GATTADDSERVICE=UUID="+hex(value)))
                    else:
                        ss,tr = _check(_at("AT+GATTADDSERVICE=UUID128="+data_to_ascii(value)))
                    if not ss:
                        return None
                    last_service = int(tr,16)
                    lst[0]=last_service
                else:
                    handle,uuid, value, perm = lst
                    data = data_to_ascii(value)
                    l = (len(data)+1)//3
                    if type(uuid)==PSMALLINT:
                        ss,tr = _check(_at("AT+GATTADDCHAR=UUID="+hex(uuid)+",PROPERTIES="+hex(perm)+",MIN_LEN=1,MAX_LEN="+str(l)+",VALUE="+data))
                    else:
                        ss,tr = _check(_at("AT+GATTADDCHAR=UUID128="+data_to_ascii(uuid)+",PROPERTIES="+hex(perm)+",MIN_LEN=1,MAX_LEN="+str(l)+",VALUE="+data))
                    if not ss:
                        return None
                    lst[0]=int(tr,16)
            return cfg
        return None

def gatt_set(handle,value):
    """
.. function:: gatt_set(handle,value)

    Sets the *value* of a characteristic given its *handle* (as returned after a successfull configuration). Value can be an integer, a string or an iterable of bytes.
    Returns False on failure.

    """
    st,res = _check(_at("AT+GATTCHAR="+str(handle)+","+data_to_ascii(value)))
    return st

def gatt_get(handle):
    """
.. function:: gatt_get(handle)

    Returns the value of the characteristic identified by *handle* (as returned after a successfull configuration).
    
    Returns None on failure.

    """
    st,res = _check(_at("AT+GATTCHAR="+str(handle)))
    if st:
        return res
    return None

def addr():
    """
.. function:: addr()

    Returns the 48bit mac address of the device as an hex string. Returns None on failure.

    """
    st,res = _check(_at("AT+BLEGETADDR"))
    if st:
        return res
    return None

def peer_addr():
    """
.. function:: peer_addr()

    Returns the 48bit mac address of the client connected device as an hex string. Returns None on failure.

    """
    st,res = _check(_at("AT+BLEGETPEERADDR"))
    if st:
        return res
    return None

def rssi():
    """
.. function:: addr()

    Returns the RSSI level id dBm. Returns None on failure.

    """
    st,res = _check(_at("AT+BLEGETRSSI"))
    if st:
        return int(res)
    return None

def tx_power(dbm=None):
    """
.. function:: tx_power(dbm=None)

    If *dbm* is None, returns the current transmission power level. Otherwise sets the power level to *dbm* (in the range -40 to 4).
    
    Returns None on failure.

    """
    if dbm is None:
        st,res = _check(_at("AT+BLEPOWERLEVEL"))
        if not st:
            return None
        return int(res)
    else:
        txp = (-40,-20,-16,-12,-8,-3,0,4)
        mx = txp[-1]
        for i in range(len(txp)-1):
            if dbm>txp[i] and dbm<txp[i+1]:
                mx=txp[i+1]
                break
        st,res = _check(_at("AT+BLEPOWERLEVEL="+str(mx)))
        if not st:
            return None
        return mx

class BLEStream(streams.stream):
    """
===============
BLEStream class
===============
    
.. class:: BLEStream(fifosize=1024)

    This class implements a serial stream on the Bluefruit peripheral. The internal implementation uses
    a fifo buffer of *fifosize* bytes.

    The BLEStream is not automatically set as the global serial stream. 

    Read and write methods are the same of any stream with the difference that they raise IOError if the BLEStream is
    not connected (namely, the Bluefruit peripheral is not paired with a BLE client).

    Also, due to the features of the Bluefruit firmware, read methods use a polling mechanism to check for incoming data.
    
    """
    def __init__(self,fifosize=1024):
        self.fifo=fifo.Fifo(fifosize,only_bytes=True)

    def _readbuf(self,buf,size=1,ofs=0):
        ss=size
        while True:
            while size>0 and not self.fifo.is_empty():
                buf[ofs]=self.fifo.get()
                ofs+=1
                size-=1
            if size>0:
                st,res = _check(_at("AT+BLEUARTRX"))
                if not st:
                    raise IOError
                if not res:
                    sleep(5)
                else:
                    self.fifo.put_all(bytes(res))
            else:
                return ss

    def write(self,buf):
        for i in range(0,len(buf),32):
            kk=buf[i:i+32]
            kk= kk.replace("\n","\\n").replace("\r","\\r").replace("\t","\\t").replace("\b","\\b").replace("\\","\\\\")
            st,res=_check(_at("AT+BLEUARTTX="+str(kk)))
            if not st:
                raise IOError
        return len(buf)


