from base import *
from devices import *

class STNucleo401RE(Board):
    @staticmethod
    def match(dev):
        return dev["vid"] == "0483" and dev["pid"]=="374B"

    def reset(self):
        pass

    def burn(self,bin,outfn=None):
        import time
        # to be sure to delete previous bytecode, expand the vm to the right size
        # it has to reach at least 8040000, so it must be expanded to 128k (do 130k to erase bytecode too)
        bin=bin+bytes(130*1024-len(bin))  
        fname = fs.get_tempfile(bin)
        if not self.disk:
            return False,"Can't find device disk! Have you mounted the ST Link device?"
        fs.copyfile2(fname,fs.path(self.disk,"stnucleo.bin"))
        fs.del_tempfile(fname)
        time.sleep(6) # sleep to avoid returning before finishing the copy
        return True,"Ok"
