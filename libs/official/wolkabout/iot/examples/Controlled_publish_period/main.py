#   Copyright 2018 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from wolkabout.iot import iot

# Import your wifi chip
from wireless import wifi
from stm.spwf01sa import spwf01sa as wifi_driver

# Import streams to enable printing
import streams
streams.serial()


# Insert your WiFi credentials
network_SSID = "INSERT_YOUR_WIFI_SSID"
network_SECURITY = wifi.WIFI_WPA2  # wifi.WIFI_OPEN , wifi.WIFI_WEP, wifi.WIFI_WPA, wifi.WIFI_WPA2
network_password = "INSERT_YOUR_WIFI_PASSWORD"

# Insert your device credentials
device_key = "device_key"
device_password = "some_password"
actuator_references = ["SW"]

# LED4 used as example switch actuator
pinMode(LED4, OUTPUT)
digitalWrite(LED4, HIGH)


# Connect to WiFi network
try:
    print("Initializing WiFi driver..")
    # This setup refers to spwf01sa wi-fi chip mounted on flip n click device slot A
    wifi_driver.init(SERIAL1, D16)
    print("Done")

    print("Establishing connection with WiFi network...")
    wifi.link(network_SSID, network_SECURITY, network_password)
    print("Done")
except Exception as e:
    print("Something went wrong while linking: ", e)
    while True:
        sleep(1000)


# Insert the device credentials received from WolkAbout IoT Platform when creating the device
# List actuator references included on your device
try:
    device = iot.Device(device_key, device_password, actuator_references)
except Exception as e:
    print("Something went wrong while creating the device: ", e)


# Provide implementation of a way to read actuator status if your device has actuators
class ActuatorStatusProviderImpl(iot.ActuatorStatusProvider):

    def get_actuator_status(reference):
        if reference == "SW":
            value = digitalRead(LED4)
            if value == 1:
                return iot.ACTUATOR_STATE_READY, "true"
            else:
                return iot.ACTUATOR_STATE_READY, "false"


# Provide implementation of an actuation handler if your device has actuators
class ActuationHandlerImpl(iot.ActuationHandler):

    def handle_actuation(reference, value):
        print("Setting actuator " + reference + " to value: " + value)
        if reference == "SW":
            current_state = digitalRead(LED4)
            if current_state == 1:
                if value == "false":
                    digitalWrite(LED4, LOW)
            else:
                if value == "true":
                    digitalWrite(LED4, HIGH)


# Pass your device, actuation handler and actuator status provider if you have actuators on your device
try:
    wolk = iot.Wolk(device, ActuationHandlerImpl, ActuatorStatusProviderImpl)
except Exception as e:
    print("Something went wrong while creating the Wolk instance: ", e)

# Establish a connection to the WolkAbout IoT Platform
try:
    print("Connecting to WolkAbout IoT Platform")
    wolk.connect()
    print("Done")
except Exception as e:
    print("Something went wrong while connecting: ", e)

publish_period = 5000


try:
    while True:
        sleep(publish_period)

        print("Publishing sensor readings and actuator statuses")
        temperature = random(15, 40)
        humidity = random(15, 55)
        pressure = random(995, 1020)
        print("T", temperature, "H", humidity, "P", pressure)
        if humidity > 50:
            # Adds an alarm event to the queue
            wolk.add_alarm("HH", "Humidity is over 50%!")
        # Adds a sensor reading to the queue
        wolk.add_sensor_reading("T", temperature)
        wolk.add_sensor_reading("H", humidity)
        wolk.add_sensor_reading("P", pressure)

        # Publishes all sensor readings and alarms from the queue and current actuator statuses to the WolkAbout IoT Platform
        wolk.publish()
except Exception as e:
    print("Something went wrong: ", e)
