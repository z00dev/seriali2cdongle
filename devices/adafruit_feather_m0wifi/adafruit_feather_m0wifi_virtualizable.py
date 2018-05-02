from base import *
from devices import *

class AdafruitFeatherM0WifiVirtualizable(Board):
    vendor_pid = [("239A", "000B")]

    @staticmethod
    def match(dev):
        return (dev["vid"], dev["pid"]) in AdafruitFeatherM0WifiVirtualizable.vendor_pid

    def reset(self):
        pass

    def burn(self,bin,outfn=None):
        fname = fs.get_tempfile(bin)
        res,out,err = proc.runcmd("bossac_d21","-i","-d","-e","-w","-v","-R", "-p", self.port,fname,outfn=outfn)
        fs.del_tempfile(fname)
        if res:
            return False,out
        return True,out


    def __init__(self,info={},dev={}):
        super().__init__(info,dev)
        self._info["name"] = "Adafruit Feather M0 Wi-Fi Virtualizable"
