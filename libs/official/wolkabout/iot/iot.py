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

"""
.. module:: iot

********************************
WolkAbout IoT Platform Library
********************************

    WolkAbout Python Connector library for connecting Zerynth devices to `WolkAbout IoT Platform <https://wolkabout.com/>`_.
    The `Wolk` class depends upon interfaces, making it possible to provide different implementations.
    The section `Dependencies` contains the documentation of the default implementations, followed by the `Wolk` section that
    contains everything necessary to connect and publish data to the WolkAbout IoT Platform.
    


"""

from wolkabout.iot.WolkCore import WolkCore
from wolkabout.iot.WolkCore import ConnectivityService
from wolkabout.iot.WolkCore import InboundMessage
from wolkabout.iot.WolkCore import OutboundMessageQueue
from wolkabout.iot.WolkCore import OutboundMessage
from wolkabout.iot.WolkCore import OutboundMessageFactory
from wolkabout.iot.WolkCore import ActuatorState
from wolkabout.iot.WolkCore import InboundMessageDeserializer
from wolkabout.iot.WolkCore import ActuatorCommand
from wolkabout.iot.WolkCore import ActuatorCommandType

from mqtt import mqtt
import json
import queue

new_exception(InterfaceNotProvided, Exception)


class ZerynthMQTTConnectivityService(ConnectivityService.ConnectivityService):
    """

========================================
Dependencies
========================================

The following classes are implementations of interfaces on which the Wolk class depends

------------------------------------
MQTT Connectivity Service
------------------------------------


.. class:: ZerynthMQTTConnectivityService(ConnectivityService.ConnectivityService)

This class provides the connection to the WolkAbout IoT Platform by implementing the :samp:`ConnectivityService` interface

* :samp:`device`: Contains device key, device password and actuator references
* :samp:`qos`: Quality of Service for MQTT connection (0,1,2), defaults to 0
* :samp:`host`: The address of the WolkAbout IoT Platform, defaults to the Demo instance
* :samp:`port`: The port to which to send messages, defaults to 1883
* :samp:`connected`: Boolean flag
* :samp:`inbound_message_listener`: Callback method on inbound messages
* :samp:`client`: The MQTT client
    """

    def __init__(self, device,
                 qos=0, host="api-demo.wolkabout.com", port=1883):
        self.device = device
        self.qos = qos
        self.host = host
        self.port = port
        self.connected = False
        self.inbound_message_listener = None
        self.client = None

    def set_inbound_message_listener(self, on_inbound_message):
        """
.. method:: set_inbound_message_listener(on_inbound_message)

Sets the callback method to handle inbound messages

* :samp:`on_inbound_message`:  The method that handles inbound messages
        """
        self.inbound_message_listener = on_inbound_message

    def on_mqtt_message(self, client, data):
        """
.. method:: on_mqtt_message(on_inbound_message)

Method that serializes inbound messages and passes them to the inbound message listener

* :samp:`client`:  The client that received the message
* :samp:`data`: The message received
        """
        if 'message' in data:
            channel = data['message'].topic
            payload = data['message'].payload
            message = InboundMessage.InboundMessage(channel, payload)
            self.inbound_message_listener(message)

    def connect(self):
        """
.. method:: connect(self)

This method establishes the connection to the WolkAbout IoT platform.
If there are actuators it will subscribe to topics that will contain actuator commands and also starts a loop to handle inbound messages.
Raises an exception if the connection failed.

        """
        if self.connected:
            return

        self.client = mqtt.Client(self.device.key, True)
        self.client.set_username_pw(
            self.device.key, self.device.password)
        self.client.set_will(
            "lastwill/" + self.device.key, "Gone offline", 2, False)

        for retry in range(10):
            try:
                self.client.connect(self.host, 60, self.port)
                if self.device.actuator_references:
                    topics = []
                    for actuator_reference in self.device.actuator_references:
                        channel = "actuators/commands/" + self.device.key + "/" + \
                            actuator_reference
                        topic = [channel, self.qos]
                        topics.append(topic)
                    self.client.subscribe(topics)
                self.client.on(mqtt.PUBLISH, self.on_mqtt_message)
                self.client.loop()
                self.connected = True
                break
            except Exception as e:
                raise e

    def disconnect(self):
        """
.. method:: disconnect(self)

Disconnects the device from the WolkAbout IoT Platform

        """
        self.connected = False
        self.client.disconnect()

    def connected(self):
        """
.. method:: connected(self)

Returns the current status of the connection

        """
        return self.connected

    def publish(self, outbound_message):
        """
.. method:: publish(self, outbound_message)

Publishes the :samp:`outbound_message` to the WolkAbout IoT Platform

        """
        self.client.publish(outbound_message.channel,
                            outbound_message.payload, self.qos)
        # TODO: make sure it was actually published
        return True


class ZerynthOutboundMessageQueue(OutboundMessageQueue.OutboundMessageQueue):
    """

----------------------
Outbound Message Queue
----------------------


.. class:: ZerynthOutboundMessageQueue(OutboundMessageQueue.OutboundMessageQueue)

This class provides the means of storing messages before they are sent to the WolkAbout IoT Platform.

* :samp:`maxsize`: Int - The maximum size of the queue, effectively limiting the number of messages to persist in memory

    """

    def __init__(self, maxsize):
        self.queue = queue.Queue(maxsize=maxsize)

    def put(self, message):
        """
.. method:: put(self, message)

Adds the :samp:`message` to :samp:`self.queue`

        """
        if self.queue.full():
            return

        self.queue.put(message)

    def get(self):
        """
.. method:: get(self)

Takes the first :samp:`message` from :samp:`self.queue`

        """
        if self.queue.empty():
            return None

        return self.queue.get()

    def peek(self):
        """
.. method:: peek(self)

Returns the first :samp:`message` from :samp:`self.queue` without removing it from the queue

        """
        if self.queue.empty():
            return None

        return self.queue.peek()


class ZerynthOutboundMessageFactory(OutboundMessageFactory.OutboundMessageFactory):
    """

---------------------------------
Outbound Message Factory
---------------------------------

.. class:: ZerynthOutboundMessageFactory(OutboundMessageFactory.OutboundMessageFactory)

This class serializes sensor readings, alarms and actuator statuses so that they can be properly sent to the WolkAbout IoT Platform

* :samp:`device_key` - The key used to serialize messages
    """

    def __init__(self, device_key):
        self.device_key = device_key

    def make_from_sensor_reading(self, reading):
        """
.. method:: make_from_sensor_reading(self, reading)

Serializes the :samp:`reading` to be sent to the WolkAbout IoT Platform

* :samp:`reading`: Sensor reading to be serialized
        """
        if reading.timestamp is None:
            return OutboundMessage.OutboundMessage(
                "readings/" + self.device_key + "/" + reading.reference, "{ \"data\" : \"" + str(reading.value) + "\" }")
        else:
            return OutboundMessage.OutboundMessage("readings/" + self.device_key + "/" + reading.reference,
                                                   "{ \"utc\" : \"" + str(reading.timestamp) + "\", \"data\" : \"" + str(reading.value) + "\" }")

    def make_from_alarm(self, alarm):
        """
.. method:: make_from_alarm(self, alarm)

Serializes the :samp:`alarm` to be sent to the WolkAbout IoT Platform

* :samp:`alarm`: Alarm event to be serialized
        """
        if alarm.timestamp is None:
            return OutboundMessage.OutboundMessage(
                "events/" + self.device_key + "/" + alarm.reference, "{ \"data\" : \"" + str(alarm.message) + "\" }")
        else:
            return OutboundMessage.OutboundMessage("events/" + self.device_key + "/" + alarm.reference,
                                                   "{ \"utc\" : \"" + str(alarm.timestamp) + "\", \"data\" : \"" + str(alarm.message) + "\" }")

    def make_from_actuator_status(self, actuator):
        """
.. method:: make_from_actuator_status(self, actuator)

Serializes the :samp:`actuator` to be sent to the WolkAbout IoT Platform

* :samp:`actuator`: Actuator status to be serialized
        """
        if actuator.state == ActuatorState.ACTUATOR_STATE_READY:
            actuator.state = "READY"
        elif actuator.state == ActuatorState.ACTUATOR_STATE_BUSY:
            actuator.state = "BUSY"
        elif actuator.state == ActuatorState.ACTUATOR_STATE_ERROR:
            actuator.state = "ERROR"
        return OutboundMessage.OutboundMessage("actuators/status/" + self.device_key + "/" + actuator.reference,
                                               "{ \"status\" : \"" + actuator.state + "\" , \"value\" : \"" + str(actuator.value) + "\" }")


class ZerynthInboundMessageDeserializer(InboundMessageDeserializer.InboundMessageDeserializer):
    """

-----------------------
Inbound Message Factory
-----------------------

.. class:: ZerynthInboundMessageDeserializer(InboundMessageDeserializer.InboundMessageDeserializer)

This class deserializes messages that the device receives from the WolkAbout IoT Platform from the topics it is subscribed to.

    """

    def deserialize_actuator_command(self, inbound_message):
        """
.. method:: deserialize_actuator_command(self, inbound_message)

Deserializes the :samp:`inbound_message` that was received from the WolkAbout IoT Platform

* :samp:`inbound_message`: The message to be deserialized
        """
        reference = inbound_message.channel.split("/")[-1]
        bytearray_payload = bytearray(inbound_message.payload)
        payload = json.loads(bytearray_payload)
        command = payload.get("command")
        if str(command) == "SET":
            command_type = ActuatorCommandType.ACTUATOR_COMMAND_TYPE_SET
            value = payload.get("value")
            actuation = ActuatorCommand.ActuatorCommand(
                reference, command_type, value)
            return actuation
        elif str(command) == "STATUS":
            command_type = ActuatorCommandType.ACTUATOR_COMMAND_TYPE_STATUS
            actuation = ActuatorCommand.ActuatorCommand(
                reference, command_type)
            return actuation
        else:
            command_type = ActuatorCommandType.ACTUATOR_COMMAND_TYPE_UNKNOWN
            actuation = ActuatorCommand.ActuatorCommand(
                reference, command_type)
            return actuation


class Wolk:
    """
==========
Wolk class
==========

.. class:: Wolk

This class is a wrapper for the WolkCore class that passes the Zerynth compatible implementation of interfaces to the constructor

* :samp:`device`: Contains device key and password, and actuator references
* :samp:`actuation_handler`: Implementation of the :samp:`ActuationHandler` interface
* :samp:`actuator_status_provider`: Implementation of the :samp:`ActuatorStatusProvider` interface
* :samp:`outbound_message_queue`: Implementation of the :samp:`OutboundMessageQueue` interface

    """

    def __init__(self, device, actuation_handler=None, actuator_status_provider=None,
                 outbound_message_queue=ZerynthOutboundMessageQueue(30)):
        self.device = device
        self.outbound_message_factory = ZerynthOutboundMessageFactory(device.key)
        self.outbound_message_queue = outbound_message_queue
        self.connectivity_service = ZerynthMQTTConnectivityService(device)
        self.deserializer = ZerynthInboundMessageDeserializer()

        if device.actuator_references and (actuation_handler is None or actuator_status_provider is None):
            raise InterfaceNotProvided

        self._wolk = WolkCore.WolkCore(
            self.outbound_message_factory,
            self.outbound_message_queue,
            self.connectivity_service,
            actuation_handler,
            actuator_status_provider,
            self.deserializer)

    def connect(self):
        """
.. method:: connect()

Connects the device to the WolkAbout IoT Platform by calling the provided connectivity_service's :samp:`connect` method

        """
        try:
            self._wolk.connect()
        except Exception as e:
            raise e

    def disconnect(self):
        """
.. method:: disconnect()

Disconnects the device from the WolkAbout IoT Platform by calling the provided connectivity_service's :samp:`disconnect` method

        """
        self._wolk.disconnect()

    def add_sensor_reading(self, reference, value, timestamp=None):
        """
.. method:: add_sensor_reading(reference, value, timestamp=None)

Publish a sensor reading to the platform

* :samp:`reference`: String - The reference of the sensor
* :samp:`value`: Int, Float - The value of the sensor reading
* :samp:`timestamp`: (optional) Unix timestamp - if not provided, platform will assign one upon reception
        """
        self._wolk.add_sensor_reading(reference, value, timestamp)

    def add_alarm(self, reference, message, timestamp=None):
        """
.. method:: add_alarm(reference, message, timestamp=None)

Publish an alarm to the platform

* :samp:`reference`: String - The reference of the alarm
* :samp:`message`: String - Description of the event that occurred
* :samp:`timestamp`: (optional) Unix timestamp - if not provided, platform will assign one upon reception
        """
        self._wolk.add_alarm(reference, message, timestamp)

    def publish(self):
        """
.. method:: publish()

Publishes all currently stored messages and current actuator statuses to the platform
        """
        if self.device.actuator_references:
            for reference in self.device.actuator_references:
                self.publish_actuator_status(reference)
        self._wolk.publish()

    def publish_actuator_status(self, reference):
        """
.. method:: publish_actuator_status(reference)

Publish the current actuator status to the platform

* :samp:`reference`: String - The reference of the actuator
        """
        self._wolk.publish_actuator_status(reference)

    def _on_inbound_message(self, message):
        """
.. method:: _on_inbound_message(message)

Callback method to handle inbound messages

.. note:: Pass this method to the implementation of :samp:`ConnectivityService` interface

* :samp:`message`: The message received from the platform
        """
        self._wolk._on_inbound_message(message)


class Device:
    """

------
Device
------


.. class:: Device

    The :samp:`Device` class contains all the required information for connecting to the WolkAbout IoT Platform.

    * :samp:`key` - The device key obtained when creating the device on WolkAbout IoT platform
    * :samp:`password` - The device password obtained when creating the device on WolkAbout IoT platform
    * :samp:`actuator_references` - A list of actuator references defined on in the device manifest on WolkAbout IoT Platform

    """

    def __init__(self, key, password, actuator_references=None):
        self.key = key
        self.password = password
        self.actuator_references = actuator_references


class ActuationHandler:
    """

-----------------
Actuation Handler
-----------------

.. class:: ActuationHandler

    This interface must be implemented in order to execute actuation commands issued from WolkAbout IoT Platform.

.. method:: handle_actuation(self, reference, value)

    This method will try to set the actuator, identified by :samp:`reference`, to the :samp:`value` specified by WolkAbout IoT Platform

    """

    def handle_actuation(self, reference, value):
        pass


class ActuatorStatusProvider:
    """

------------------------
Actuator Status Provider
------------------------

.. class:: ActuatorStatusProvider


    This interface must be implemented in order to provide information about the current status of the actuator to the WolkAbout IoT Platform


.. method:: get_actuator_status(self, reference)


    This method will return the current actuator :samp:`state` and :samp:`value`, identified by :samp:`reference`, to the WolkAbout IoT Platform.
    The possible `states` are:

    The method should return something like this::

    Returns ACTUATOR_STATE_READY, value

    """

    def get_actuator_status(self, reference):
        pass


# "Enum" of actuator states
ACTUATOR_STATE_READY = 0
ACTUATOR_STATE_BUSY = 1
ACTUATOR_STATE_ERROR = 2

# "Enum" of version number
VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0
