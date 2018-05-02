from wireless import wifi
# this example is based on Particle Photon
# change the following line to use a different wifi driver
from broadcom.bcm43362 import bcm43362 as wifi_driver
import streams

# Import the Zerynth APP library
from zerynthapp import zerynthapp

streams.serial()

sleep(1000)
print("STARTING...")

# define a RPC function: generate a random number
def do_random(a,b):
    return random(a,b)

# send events on button pressed
def on_btn():
    zapp.event({"my_button":"pressed"})

onPinFall(BTN0,on_btn,debounce=1000)


# Device UID and TOKEN can be created in the ADM panel
zapp = zerynthapp.ZerynthApp("DEVICE UID HERE", "DEVICE TOKEN HERE", log=True)

# link "random" to do_random
zapp.on("random",do_random)

try:
    # connect to the wifi network (Set your SSID and password below)
    wifi_driver.auto_init()
    for i in range(0,5):
        try:
            wifi.link("NETWORK SSID",wifi.WIFI_WPA2,"NETWORK PASSWORD")
            break
        except Exception as e:
            print("Can't link",e)
    else:
        print("Impossible to link!")
        while True:
            sleep(1000)

    # Start the Zerynth app instance!
    # Remember to create a template with the files under the "template" folder you just cloned
    # upload it to the ADM and associate it with the connected device
    zapp.run()
    
    # Do whatever you need here
    while True:
        print(".")
        sleep(5000)
        
except Exception as e:
    print(e)
