from base import *
from devices import *

class ElectronDFU(Board):

    @staticmethod
    def match(dev):
        return dev["vid"]=="2B04" and dev["pid"]=="D00A"

    def burn(self,bin,outfn=None):
        #to be sure to delete previous bytecode, expand the vm to the right size
        #it has to reach at least 8040000, so it must be expanded to 128k (do 130k to erase bytecode too)
        if (len(bin)<128*1024):
            bin=bin+bytes(130*1024-len(bin))
        fname = fs.get_tempfile(bin)
        res,out,err = proc.runcmd("dfu","-d",self.vid+":"+self.pid,"-a","0","-s","0x08020000:leave","-D",fname,outfn=outfn)
        fs.del_tempfile(fname)
        if res:
            if "downloaded successfully" in out: # photon makes dfu-util return with exit code != 0 -_-
                return True,out
            return False,out
        return True,out


    def __init__(self,info={},dev={}):
        super().__init__(info,dev)
        self._info["name"] = "Particle Electron DFU"


