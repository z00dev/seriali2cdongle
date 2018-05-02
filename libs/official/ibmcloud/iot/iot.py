# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2017-09-21 16:17:16
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-12-19 16:23:54

"""
.. module:: iot

****************************
IBM Cloud Watson IoT Library
****************************

The Zerynth IBM Cloud Watson IoT Library can be used to ease the connection to the `IBM Watson IoT Platform <https://internetofthings.ibmcloud.com/>`_.

It allows to make your device act as an IBM Watson IoT Device which can be created through IBM Watson IoT dashboard.

    """

import json
import ssl
from mqtt import mqtt


class WatsonMQTTClient(mqtt.Client):

    def __init__(self, mqtt_id, endpoint, auth_token, ssl_ctx):
        mqtt.Client.__init__(self, mqtt_id, clean_session=False)
        mqtt.Client.set_username_pw(self, 'use-token-auth', password=auth_token)

        self.endpoint = endpoint
        self.ssl_ctx = ssl_ctx

    def connect(self, port=8883):
        mqtt.Client.connect(self, self.endpoint, 60, port=port, ssl_ctx=self.ssl_ctx)


class Device:
    """
================
The Device class
================

.. class:: Device(device_id, device_type, organization, auth_token)

        Create a Device instance representing an IBM Watson IoT Device.

        The Device object will contain an mqtt client instance pointing to IBM Watson IoT MQTT broker located at :samp:`organization.messaging.internetofthings.ibmcloud.com`.
        The client is configured with :samp:`d:organization:device_type:device_id` as MQTT id and is able to connect securely through TLS and to authenticate setting :samp:`auth_token` as client password.

        The client is accessible through :samp:`mqtt` instance attribute and exposes all :ref:`Zerynth MQTT Client methods <lib.zerynth.mqtt>` so that it is possible, for example, to setup
        custom callback on MQTT commands (though the Device class already exposes high-level methods to setup IBM Watson IoT specific callbacks).
        The only difference concerns mqtt.connect method which does not require broker url and ssl context, taking them from Device configuration::

            my_device = iot.Device('my_device_id', 'my_device_type', 'my_organization', 'auth_token')
            my_device.mqtt.connect()
            ...
            my_device.mqtt.loop()

    """

    def __init__(self, device_id, device_type, organization, auth_token):
        self.ctx = ssl.create_ssl_context(options=ssl.CERT_NONE) # TODO: add messaging.pem cert

        mqtt_id = 'd:' + organization + ':' + device_type + ':' + device_id
        endpoint = organization + '.messaging.internetofthings.ibmcloud.com'

        self.mqtt = WatsonMQTTClient(mqtt_id, endpoint, auth_token, self.ctx)

        # self.managed = False
        self._cmd_cbks = {}

    # https://console.bluemix.net/docs/services/IoT/devices/device_mgmt/index.html
    # def manage(self):
    #     self.managed = True

    # def unmanage(self):
    #     self.managed = False

    def publish(self, event_id, event, format_string='json'):
        """
.. method:: publish(event_id, event, format_string='json')

        Publish :samp:`event_id` event with :samp:`event` content.

        :samp:`event` content has to be a dictionary when :samp:`'json'` is chosen as :samp:`format_string`, a string otherwise.

        """
        if format_string == 'json':
            event = json.dumps(event)
        self.mqtt.publish('iot-2/evt/' + event_id + '/fmt/' + format_string, event)

    def _handle_command(self, mqtt_client, mqtt_data):
        tt = mqtt_data['message'].topic.split('/')
        command_id = tt[2]
        if mqtt_data['message'].topic.endswith('/json'):
            command_content = json.loads(mqtt_data['message'].payload)
        else:
            command_content = mqtt_data['message'].payload
        self._cmd_cbks[command_id](command_content)

    def _is_command(self, mqtt_data):
        if ('message' in mqtt_data):
            return mqtt_data['message'].topic.startswith('iot-2/cmd/')
        return False

    def on_cmd(self, command_id, command_cbk, format_string='json'):
        """
.. method:: on_cmd(command_id, command_cbk, format_string='json')

        Set a callback to respond to :samp:`command_id` command.

        :samp:`command_cbk` callback will be called passing a dictionary containing command payload when :samp:`'json'` is chosen as :samp:`format_string`, a string otherwise ::

            def turn_led(cmd_content):
                if cmd_content['dir'] == 'on':
                    led_on()
                else:
                    led_off()

            my_device.on_cmd('turn_led', turn_led)

        """
        if not command_id in self._cmd_cbks:
            self.mqtt.subscribe([['iot-2/cmd/' + command_id + '/fmt/' + format_string, 0]])
        if not len(self._cmd_cbks):
            self.mqtt.on(mqtt.PUBLISH, self._handle_command, self._is_command)
        self._cmd_cbks[command_id] = command_cbk

