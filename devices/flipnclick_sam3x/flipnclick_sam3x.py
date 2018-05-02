import time
from base import *
from devices import *

class FlipNClickSAM3X(Board):

    @staticmethod
    def match(dev):
        return dev["vid"]=="2341" and dev["pid"]=="003D"
    

    def reset(self):
        if env.is_windows():
            proc.runcmd("stty",str(self.port)+":115200,n,8,1")
        else:
            proc.runcmd("stty",self.port,"cs8", "115200")

    def burn(self,bin,outfn=None):
        fname = fs.get_tempfile(bin)
        if env.is_windows():
            proc.runcmd("stty",str(self.port)+":1200,n,8,1")
            time.sleep(1)
            res,out,err= proc.runcmd("bossac","-U", "false" ,"-e" ,"-w",fname,"-R", "--boot=1" ,"-p" ,self.port,outfn=outfn)
        else:
            proc.runcmd("stty",self.port,"cs8", "1200", "hupcl")
            time.sleep(1)
            res,out,err= proc.runcmd("bossac","-U", "false", "-e", "-w",fname,"-R", "--boot=1",outfn=outfn)

        fs.del_tempfile(fname)
        if res or "100%" not in out:
            return False,out
        return True,out
