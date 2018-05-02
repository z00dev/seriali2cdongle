from base import *
from devices import *

class ParticleCoreDFU(Board):

    @staticmethod
    def match(dev):
        return dev["vid"]=="1D50" and dev["pid"]=="607F"

    def burn(self,bin,outfn=None):
        #to be sure to delete previous bytecode, expand the vm to the right size
        #it has to reach at least the 1k sector after the vm, so add 3k to be sure
        bin=bin+bytes(3*1024)
        fname = fs.get_tempfile(bin)
        res,out,err = proc.runcmd("dfu","-d",self.vid+":"+self.pid,"-a", "0", "-s" ,"0x08005000:leave", "-D",fname,outfn=outfn)
        fs.del_tempfile(fname)
        if res:
            if "downloaded successfully" in out: # photon makes dfu-util return with exit code != 0 -_-
                return True,out
            return False,out
        return True,out


    def __init__(self,info={},dev={}):
        super().__init__(info,dev)
        self._info["name"] = "Particle Core DFU"


