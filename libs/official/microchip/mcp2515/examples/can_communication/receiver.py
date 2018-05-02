################################################################################
# CAN Receiver
#
# Created: 2018-03-05 11:25:41.189984
#
################################################################################

# interrupt pin
pinMode(D21, INPUT)

while True:
    try:
        if not digitalRead(D21):
            id_rx, msg_rx = can.recv()
            if id_rx[3] & 0x80 == 0x80:
                print("Ext ID:", [e for e in id_rx], "DLC:", len(msg_rx))
            else:
                print("Std ID:", [e for e in id_rx], "DLC:", len(msg_rx))

            if id_rx[3] & 0x40 == 0x40:
                print("remote request frame")
            else:
                print("Data:", [x for x in msg_rx])
        else:
            sleep(50)
    except Exception as e:
        print(e)
        sleep(1000)