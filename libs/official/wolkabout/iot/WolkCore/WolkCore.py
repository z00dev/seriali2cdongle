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

from wolkabout.iot.WolkCore import SensorReading
from wolkabout.iot.WolkCore import Alarm
from wolkabout.iot.WolkCore import ActuatorCommandType
from wolkabout.iot.WolkCore import ActuatorStatus

"""
    WolkCore Class
"""


class WolkCore:
    """
        WolkCore Class
    """

    def __init__(self, outbound_message_factory,
                 outbound_message_queue, connectivity_service,
                 actuation_handler, actuator_status_provider, inbound_message_deserializer):
        """
        :param outbound_message_factory: Implementation of the OutboundMessageFactory interface
        :type outbound_message_factory: OutboundMessageFactory
        :param outbound_message_queue: Implementation of the OutboundMessageQueue interface
        :type outbound_message_queue: OutboundMessageQueue
        :param connectivity_service: Implementation of the ConnectivityService interface
        :type connectivity_service: ConnectivityService
        :param actuation_handler: Implementation of the ActuationHandler interface
        :type actuation_handler: ActuationHandler
        :param actuator_status_provider: Implementation of the ActuatorStatusProvider interface
        :type actuator_status_provider: ActuatorStatusProvider
        :param inbound_message_deserializer: Implementation of the InboundMessageDeserializer interface
        :type inbound_message_deserializer: InboundMessageDeserializer
        """

        self.outbound_message_factory = outbound_message_factory
        self.outbound_message_queue = outbound_message_queue
        self.connectivity_service = connectivity_service
        self.inbound_message_deserializer = inbound_message_deserializer
        self.actuation_handler = actuation_handler
        self.actuator_status_provider = actuator_status_provider
        self.connectivity_service.set_inbound_message_listener(self._on_inbound_message)

    def connect(self):
        self.connectivity_service.connect()

    def disconnect(self):
        self.connectivity_service.disconnect()

    def add_sensor_reading(self, reference, value, timestamp=None):
        """
        Publish a sensor reading to the platform
        :param reference: The reference of the sensor
        :type reference: str
        :param value: The value of the sensor reading
        :type value: int, float, str
        :param timestamp: (optional) Unix timestamp - if not provided, platform will assign one upon reception
        :type timestamp: int
        """
        reading = SensorReading.SensorReading(reference, value, timestamp)
        outbound_message = self.outbound_message_factory.make_from_sensor_reading(reading)
        self.outbound_message_queue.put(outbound_message)

    def add_alarm(self, reference, message, timestamp=None):
        """
        Publish an alarm to the platform
        :param reference: The reference of the alarm
        :type reference: str
        :param message: Description of the event that occurred
        :type message: str
        :param timestamp: (optional) Unix timestamp - if not provided, platform will assign one upon reception
        :type timestamp: int
        """
        alarm = Alarm.Alarm(reference, message, timestamp)
        outbound_message = self.outbound_message_factory.make_from_alarm(alarm)
        self.outbound_message_queue.put(outbound_message)

    def publish(self):
        """
        Publishes all currently stored messages to the platform
        """
        while True:
            outbound_message = self.outbound_message_queue.peek()
            if outbound_message is None:
                break

            if self.connectivity_service.publish(outbound_message) is True:
                self.outbound_message_queue.get()
            else:
                break

    def publish_actuator_status(self, reference):
        """
        Publish the current actuator status to the platform
        :param reference: The reference of the actuator
        :type reference: str
        """
        state, value = self.actuator_status_provider.get_actuator_status(reference)
        actuator_status = ActuatorStatus.ActuatorStatus(reference, state, value)
        outbound_message = self.outbound_message_factory.make_from_actuator_status(actuator_status)
        if not self.connectivity_service.publish(outbound_message):
            self.outbound_message_queue.put(outbound_message)

    def _on_inbound_message(self, message):
        """
        Callback function to handle inbound messages
        .. note:: Pass this function to the implementation of ConnectivityService
        :param message:  The message received from the platform
        :type message: InboundMessage
        """
        if message.channel.startswith("actuators/commands/"):
            actuation = self.inbound_message_deserializer.deserialize_actuator_command(message)
            if actuation.command == ActuatorCommandType.ACTUATOR_COMMAND_TYPE_SET:
                self.actuation_handler.handle_actuation(actuation.reference, actuation.value)

                state, value = self.actuator_status_provider.get_actuator_status(actuation.reference)
                actuator_status = ActuatorStatus.ActuatorStatus(actuation.reference, state, value)

                outbound_message = self.outbound_message_factory.make_from_actuator_status(actuator_status)
                if not self.connectivity_service.publish(outbound_message):
                    self.outbound_message_queue.put(outbound_message)
            elif actuation.command == ActuatorCommandType.ACTUATOR_COMMAND_TYPE_STATUS:
                state, value = self.actuator_status_provider.get_actuator_status(actuation.reference)

                actuator_status = ActuatorStatus.ActuatorStatus(actuation.reference, state, value)

                outbound_message = self.outbound_message_factory.make_from_actuator_status(actuator_status)
                if not self.connectivity_service.publish(outbound_message):
                    self.outbound_message_queue.put(outbound_message)
            elif actuation.command == ActuatorCommandType.ACTUATOR_COMMAND_TYPE_UNKNOWN:
                print("Received unsupported actuation command")

        else:
            print("Received unsupported message: \n" +
                  message.channel + "\n" + message.payload)
