################################################################################
# CAN Transmitter
#
# Created: 2018-03-05 11:25:41.189984
#
################################################################################

canid = bytearray([0x00, 0x00, 0x01, 0x00])
data = [0x98, 0xBB, 0x40, 0xAC, 0x58, 0x33, 0x12, 0x00]

while True:
    try:        
        for i in range(1,11):
            data[7] += 1
            print("sending msg...",i)
            can.send(canid, data)
            print("...done")
            sleep(50)
        if data[7] == 240:
            data[7] = 0
        sleep(1000)
    except TimeoutError:
        print("no one listening")
        sleep(1000)
    except Exception as e:
        print(e)
        sleep(1000)

