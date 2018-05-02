import time
from base import *
from devices import *

class ArduinoDue(Board):
    ids_vendor = {
        "2341":frozenset(("003D",)),
        "2A03":frozenset(("003D",))
    }

    @staticmethod
    def match(dev):
        return dev["vid"] in ArduinoDue.ids_vendor and dev["pid"] in ArduinoDue.ids_vendor[dev["vid"]]

    def reset(self):
        if env.is_windows():
            proc.runcmd("stty",str(self.port)+":115200,n,8,1")
        else:
            proc.runcmd("stty",self.port,"cs8", "115200")

    def burn(self,bin,outfn=None):
        fname = fs.get_tempfile(bin)
        if env.is_windows():
            proc.runcmd("stty",str(self.port)+":1200,n,8,1")
            time.sleep(3)
            res,out,err= proc.runcmd("bossac","-U", "false" ,"-e" ,"-w",fname,"-R", "--boot=1" ,"-p" ,self.port,outfn=outfn)
        else:
            proc.runcmd("stty",self.port,"cs8", "1200", "hupcl")
            time.sleep(1)
            res,out,err= proc.runcmd("bossac","-U", "false", "-e", "-w",fname,"-R", "--boot=1",outfn=outfn)
        fs.del_tempfile(fname)
        if res or "100%" not in out:
            return False,out
        return True,out


