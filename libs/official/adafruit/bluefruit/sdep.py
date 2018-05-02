
spi=None
pin=0


__define(SDEP_CMDTYPE_INITIALIZE, 0xBEEF)
__define(SDEP_CMDTYPE_AT_WRAPPER, 0x0A00)
__define(SDEP_CMDTYPE_BLE_UARTTX, 0x0A01)
__define(SDEP_CMDTYPE_BLE_UARTRX, 0x0A02)

__define(SDEP_MSGTYPE_COMMAND,0x10)
__define(SDEP_MSGTYPE_RESPONSE,0x20)
__define(SDEP_MSGTYPE_ALERT,0x40)
__define(SDEP_MSGTYPE_ERROR,0x80)

def init(spidrv,irqpin):
    global spi,pin,pkgin
    spi=spidrv
    pin=irqpin
    pinMode(irqpin,INPUT)

    
def send_packet(command, data):
    packet = bytearray(3)
    packet[0]=command&0xff
    packet[1]=(command>>8)&0xff
    packet[2]=min(16,len(data))
    if len(data)>0:
        packet.extend(data[0:packet[2]])
    if len(data)>16:
        packet[2]+=0x80
    spi.select()
    probe = bytearray(1)
    probe[0] = SDEP_MSGTYPE_COMMAND

    cnt=0
    while cnt<100:
        res = spi.exchange(probe)
        if res[0]==0xfe:
            spi.unselect()
            sleep(1)
            cnt+=1
            spi.select()
            continue
        res = spi.write(packet)
        spi.unselect()
        return res
    spi.unselect()
    raise TimeoutError


def get_packet():

    cnt=0
    while not digitalRead(pin):
        cnt=cnt+1
        sleep(5)
        if cnt>100:
            raise TimeoutError
    
    spi.select()

    cnt=0
    while cnt<100:
        res = spi.read(1)
        if res[0]>=0xfe:
            spi.unselect()
            sleep(1)
            cnt+=1
            spi.select()
            continue
        header = bytearray(3)
        res = spi.exchange(header)
        command = res[0]+(res[1]<<8)
        #print(".---",hex(command),res[2]&0x7f,res[2]&0x80)
        if command!=SDEP_CMDTYPE_BLE_UARTRX and command!=SDEP_CMDTYPE_BLE_UARTTX and command!=SDEP_CMDTYPE_AT_WRAPPER:
            spi.unselect()
            return (-1,command)
        data = spi.read(res[2]&0x7f)
        spi.unselect()
        return (res[2]&0x80,data)
    spi.unselect()
    raise TimeoutError

def at(cmd):
    for x in range(0,len(cmd),16):
        send_packet(SDEP_CMDTYPE_AT_WRAPPER,cmd[x:])

def ta():
    res = bytearray()
    while True:
        status,data = get_packet()
        if status<0:
            raise IOError
        #print(str(data))
        res.extend(data)
        if status==0:
            break
    return res