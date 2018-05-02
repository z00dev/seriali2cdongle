from base import *
from devices import *

class AdafruitFeatherM0Wifi(Board):
    vendor_pid = [("239A", "800B"), ("2341", "824E")]

    @staticmethod
    def match(dev):
        return (dev["vid"], dev["pid"]) in AdafruitFeatherM0Wifi.vendor_pid

    def reset(self):
        pass

    def burn(self,bin):
        return False,"Must be put in virtualization mode first!"
