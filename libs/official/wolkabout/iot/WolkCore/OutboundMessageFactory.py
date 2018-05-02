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
    Outbound Message Factory should be implemented to serialize messages
    in a format that is expected to be received from the platform.
"""


class OutboundMessageFactory:
    """
        Outbound Message Factory Interface
    """

    def make_from_sensor_reading(self, reading):
        """
        :param reading: The reading to be serialized
        :type reading: SensorReading
        :returns: message
        :rtype: OutboundMessage
        """
        pass

    def make_from_alarm(self, alarm):
        """
        :param alarm: The alarm to be serialized
        :type alarm: Alarm
        :returns: message
        :rtype: OutboundMessage
        """
        pass

    def make_from_actuator_status(self, actuator):
        """
        :param actuator: The actuator status to be serialized
        :type actuator: ActuatorStatus
        :returns: message
        :rtype: OutboundMessage
        """
        pass
