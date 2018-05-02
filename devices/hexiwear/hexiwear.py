from base import *
from devices import *
import time

class Hexiwear(Board):
    ids_vendor = {
        "0D28":frozenset(("0204",))
    }

    @staticmethod
    def match(dev):
        return dev["vid"] in Hexiwear.ids_vendor and dev["pid"] in Hexiwear.ids_vendor[dev["vid"]]

    def reset(self):
        pass

    def burn(self,bin,outfn=None):
        fname = fs.get_tempfile(bin)
        if not self.disk:
            return False,"Can't find device disk! Have you mounted the DAP Link device?"
        fs.copyfile2(fname,fs.path(self.disk,"hexiwear.bin"))
        fs.del_tempfile(fname)
        # wait some time to allow virtualization
        time.sleep(15/256*(len(bin)/1024))
        return True,"Ok"
