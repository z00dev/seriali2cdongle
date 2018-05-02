from base import *
from devices import *

class ParticleCore(Board):

    @staticmethod
    def match(dev):
        return dev["vid"]=="1D50" and dev["pid"]=="607D"

    def reset(self):
        pass

    def burn(self,bin,outfn=None):
        return False,"Must be put in DFU mode first!"

