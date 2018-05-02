from base import *
from devices import *
import time

class GenuinoZero(Board):
    ids_vendor = {
        "03EB":frozenset(("2157",))
    }

    @staticmethod
    def match(dev):
        return dev["vid"] in GenuinoZero.ids_vendor and dev["pid"] in GenuinoZero.ids_vendor[dev["vid"]]

    def reset(self):
        pass

    def burn(self,bin,outfn=None):
        fname = fs.get_tempfile(bin)
        outfn(fname)
        res,out,err= proc.runcmd("edbg", "-ebpv", "-t", "atmel_cm0p","-s",self.sid,"-f", fname,outfn=outfn)
        fs.del_tempfile(fname)
        if res:
            return False,out
        return True,out