# AWS FOTA 
# Created at 2017-10-03 08:49:48.182639

import streams
import json
from wireless import wifi

# choose a wifi chip supporting secure sockets and client certificates
from espressif.esp32net import esp32wifi as wifi_driver

# import aws iot module
from aws.iot import iot
from aws.iot import jobs
from aws.iot import fota as awsfota

# import helpers functions to easily load keys, certificates and thing configuration
import helpers


# THING KEY AND CERTIFICATE FILE MUST BE PLACED INSIDE PROJECT FOLDER 
new_resource('private.pem.key')
new_resource('certificate.pem.crt')
# SET THING CONFIGURATION INSIDE THE FOLLOWING JSON FILE
new_resource('thing.conf.json')

# Init serial port for debug
streams.serial()

# FIRMWARE VERSION: change this to verify correct FOTA
version = 0

try:
    wifi_driver.auto_init()
    print('connecting to wifi...')
    # place here your wifi configuration
    wifi.link("SSID",wifi.WIFI_WPA2,"password")
    
    # load Thing configuration
    pkey, clicert = helpers.load_key_cert('private.pem.key', 'certificate.pem.crt')
    thing_conf = helpers.load_thing_conf()
    publish_period = 1000
    
    # create aws iot thing instance and connect to mqtt broker
    thing = iot.Thing(thing_conf['endpoint'], thing_conf['mqttid'], clicert, pkey, thingname=thing_conf['thingname'])
    
    print('connecting to mqtt broker...')
    thing.mqtt.connect()
    thing.mqtt.loop()
    
    #show current version firmware
    print("Hello, I am firmware version:",version)
    
    #create an IoT Jobs object
    myjobs = jobs.Jobs(thing)
    # check if there are FOTA jobs waiting to be performed
    # This function executes a FOTA update if possible
    # or confirms an already executed FOTA update
    awsfota.handle_fota_jobs(myjobs,force=True)
    
    
    while True:
        r = random(0,10)
        print('publish random sample...',r)
        thing.mqtt.publish("dev/sample", json.dumps({ 'asample': r }))
        sleep(publish_period)
        # check for new incoming jobs
        # again, FOTA is executed if a correct FOTA job is queued
        awsfota.handle_fota_jobs(myjobs)
        
        
except Exception as e:
    print(e)
    #reset on error!
    awsfota.reset()


