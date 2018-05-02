from base import *
from devices import *

class S_PhotonDFU(Board):

    @staticmethod
    def match(dev):
        return dev["vid"]=="2B04" and dev["pid"]=="D008"

    def burn(self,bin,outfn=None):
        #to be sure to delete previous bytecode, expand the vm to the right size
        #it has to reach at least 8040000, so it must be expanded to 128k (do 130k to erase bytecode too)
        if (len(bin)<128*1024):
            bin=bin+bytes(130*1024-len(bin))
        fname = fs.get_tempfile(bin)
        res,out,err = proc.runcmd("dfu","-d",self.vid+":"+self.pid,"-a","0","-s","0x08020000:leave","-D",fname,outfn=outfn)
        fs.del_tempfile(fname)
        if res:
            if "downloaded successfully" in out: # sparkfun photon makes dfu-util return with exit code != 0 -_-
                return True,out
            return False,out
        return True,out


    def __init__(self,info={},dev={}):
        super().__init__(info,dev)
        self._info["name"] = "SparkFun Photon RedBoard DFU"


#memory map
#Region     Start Address       End Address     Size
#Bootloader 0x8000000           0x8004000       16 KB
#DCT1       0x8004000           0x8008000       16 KB
#DCT2       0x8008000           0x800C000       16 KB
#EEPROM1    0x800C000           0x8010000       16 KB
#EEPROM2    0x8010000           0x8020000       64 KB

#Memory Map (Modular Firmware - default)
#Region     Start Address       End Address     Size
#System 1   0x8020000           0x8060000       256 KB
#System 2   0x8060000           0x80A0000       256 KB
#User Part  0x80A0000           0x80C0000       128 KB
#OTA backup 0x80C0000           0x80E0000       128 KB
#Factory backup  0x80E0000      0x8100000       128 KB


