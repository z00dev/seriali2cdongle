# Eseye Anynet AWS Get info example
# Created at 2018-04-11 14:41:54.157523

import streams
from eseye.anynetaws import anynetaws as aws

streams.serial()
aws.init(SERIAL2) # select the serial driver the modem is connected to

while True:
    print('> aws state:', aws.state())
    print('> firmware version:', aws.version())
    print('> qccid:', aws.qccid())
    sleep(5000)
