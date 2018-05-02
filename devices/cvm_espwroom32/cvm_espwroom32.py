from base import *
from devices import *

class ESPWROOM32(Board):

    @classmethod
    def match(cls,dev):
        tmplfile = fs.path(fs.dirname(__file__),cls.__name__[:-6]+".yml")
        try:
            if not hasattr(cls,"tmpl"):
                cls.tmpl = fs.get_yaml(tmplfile)
                cls.vids = cls.tmpl["device"]["vids"]
                cls.pids = cls.tmpl["device"]["pids"]
        except:
            cls.tmpl={}
            cls.vids = []
            cls.pids = []
            
        # add vids and pids to the device template to enable board discovery
        return dev["vid"] in cls.vids and dev["pid"] in cls.pids
    

    def reset(self):
        import time
        conn = ConnectionInfo()
        conn.set_serial(self.port,**self.connection)
        ch = Channel(conn)
        try:
            ch.open(timeout=2)
        except:
            fatal("Can't open serial:",self.port)
        esp32r0_delay=True
        ch.setDTR(False)  # IO0=HIGH
        ch.setRTS(True)   # EN=LOW, chip in reset
        time.sleep(0.1)
        if esp32r0_delay:
            # Some chips are more likely to trigger the esp32r0
            # watchdog reset silicon bug if they're held with EN=LOW
            # for a longer period
            time.sleep(1.2)
        #ch.setDTR(True)   # IO0=LOW
        ch.setRTS(False)  # EN=HIGH, chip out of reset
        if esp32r0_delay:
            # Sleep longer after reset.
            # This workaround only works on revision 0 ESP32 chips,
            # it exploits a silicon bug spurious watchdog reset.
            time.sleep(0.4)  # allow watchdog reset to occur
        time.sleep(0.05)
        ch.setDTR(False)  # IO0=HIGH, done
        ch.close()


    def burn_custom(self,bin,portbin,outfn=None):
        rom = bin[3]    #bootloader
        irom = bin[1]   #app
        brom = bin[2]   #partition
        vrom = bin[0]   #vstore
        romf = fs.get_tempfile(rom)
        iromf = fs.get_tempfile(irom)
        bromf = fs.get_tempfile(brom)
        vromf = fs.get_tempfile(vrom)
        cromf = fs.get_tempfile(portbin) #port.bin
        res,out,err = proc.runcmd("python",tools["esptool32"],
                "--chip", "esp32",
                "--port",self.port,
                "--baud","115200",
                "--before", "default_reset", 
                "--after", "hard_reset",
                "write_flash",
                "-z","--flash_freq","40m",
                "--flash_mode","dio",
                "--flash_size","detect",
                "0x1000",romf, 
                "0x10000",iromf, 
                "0x8000", bromf,
                "0x390000",vromf,
                "0x392000",cromf,
                outfn=outfn)
        fs.del_tempfile(romf)
        fs.del_tempfile(iromf)
        fs.del_tempfile(bromf)
        fs.del_tempfile(vromf)
        fs.del_tempfile(cromf)
        if res:
            return False,out
        return True,out


