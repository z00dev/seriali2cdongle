# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2017-09-21 16:17:16
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-11-07 10:29:06

"""
.. module:: iot

*****************************
Google Cloud IoT Core Library
*****************************

The Zerynth Google Cloud IoT Core Library can be used to ease the connection to `Google Cloud IoT Core <https://cloud.google.com/iot-core/>`_.

It allows to make your device act as a Google Cloud IoT Core Device which can be registered through Google Cloud tools or Google Cloud web dashboard.

    """

import json
import ssl
import jwt
from mqtt import mqtt
import timers

class GCMQTTClient(mqtt.Client):

    def __init__(self, mqtt_id, endpoint, ssl_ctx, create_jwt, aconnect_cb):
        mqtt.Client.__init__(self, mqtt_id, clean_session=True)
        self.endpoint = endpoint
        self.ssl_ctx = ssl_ctx
        self.create_jwt = create_jwt
        self._aconnect_cb = aconnect_cb

        self.last_reconnection_try = None

    def _breconnect_cb(self, _):
        tnow  = timers.now()
        tdiff = tnow - self.last_reconnection_try
        if tdiff > 10000:
            psw = self.create_jwt() # get timestamp from a reliable source
        else:
            psw = self.create_jwt(timestamp_diff = (tdiff // 1000))

        self.last_reconnection_try = tnow
        mqtt.Client.set_username_pw(self, 'unused', password=psw)

    def connect(self, port=8883):
        self.last_reconnection_try = timers.now()
        mqtt.Client.set_username_pw(self, 'unused', password=self.create_jwt())
        mqtt.Client.connect(self, self.endpoint, 60, port=port, ssl_ctx=self.ssl_ctx, 
            breconnect_cb=self._breconnect_cb, aconnect_cb=self._aconnect_cb)


class Device:
    """
================
The Device class
================

.. class:: Device(project_id, cloud_region, registry_id, device_id, pkey, timestamp_fn, token_lifetime=60)

        Create a Device instance representing a Google Cloud IoT Core Device.

        The Device object will contain an mqtt client instance pointing to Google Cloud IoT Core MQTT broker located at :samp:`mqtt.googleapis.com`.
        The client is configured with an MQTT id composed following Google Cloud IoT Core MQTT id standards ::

            projects/$project_id/locations/$cloud_region/registries/$registry_id/devices/$device_id

        and is able to connect securely through TLS and authenticate through a JWT with a :samp:`token_lifetime` minutes lifespan.
        Valid tokens generation process needs current timestamp which will be obtained calling passed :samp:`timestamp_fn`.
        :samp:`timestamp_fn` has to be a Python function returning an integer timestamp.

        A valid private key :samp:`pkey` is also needed.
        :samp:`pkey` must be an ECDSA private key in hex format.
        If a private key has been generated following `Google Cloud IoT guidelines <https://cloud.google.com/iot/docs/how-tos/credentials/keys?hl=it#generating_an_es256_key>`_ 
        and is consequently stored as a pem file, the needed hex string can be extracted from the OCTET STRING field associated value obtained from ::

            openssl asn1parse -in my_private.pem

        command (since pem is a base64 encoded, plus header, `DER <https://tools.ietf.org/html/rfc5915>`_).

        The client is accessible through :samp:`mqtt` instance attribute and exposes all :ref:`Zerynth MQTT Client methods <lib.zerynth.mqtt>` so that it is possible, for example, to setup
        custom callbacks on MQTT commands.
        The only difference concerns :code:`mqtt.connect` method which does not require broker url and ssl context, taking them from Device configuration::

            def timestamp_fn():
                valid_timestamp = 1509001724
                return valid_timestamp

            pkey = "73801C733697C81604A4A4F7BF36FB84227DA506194A26A864A55B6DE8FF98E0"
            my_device = iot.Device('my-project', 'my-cloud-region', 'my-registry-id', 'my-device-id', pkey, timestamp_fn)
            my_device.mqtt.connect()
            ...
            my_device.mqtt.loop()
    """

    def __init__(self, project_id, cloud_region, registry_id, device_id, pkey, timestamp_fn, token_lifetime=60):
        self.ctx = ssl.create_ssl_context(options=ssl.CERT_NONE) # should add root...
        self.device_id = device_id
        self.project_id = project_id
        self.private_key = pkey
        self.timestamp_fn = timestamp_fn
        self.token_lifetime = token_lifetime
        mqtt_id = 'projects/' + project_id + '/locations/' + cloud_region + '/registries/' + registry_id +'/devices/' + device_id
        self.mqtt = GCMQTTClient(mqtt_id, 'mqtt.googleapis.com', self.ctx, self._create_jwt, self._connect_cb)

        self._config_cbk = None

    def _create_jwt(self, timestamp_diff = None):
        if timestamp_diff is None:
            timestamp = self.timestamp_fn()
        else:
            timestamp = self._last_timestamp + timestamp_diff
        self._last_timestamp = timestamp

        token = {
                # The time that the token was issued at
                'iat': timestamp,
                # The time the token expires.
                'exp': timestamp + 60*self.token_lifetime,
                # The audience field should always be set to the GCP project id.
                'aud': self.project_id
        }
        return jwt.encode(json.dumps(token), self.private_key)

    def _connect_cb(self, _):
        if self._config_cbk is not None:
            self.mqtt.subscribe([['/devices/' + self.device_id + '/config', 1]])

    def publish_event(self, event):
        """
.. method:: publish_event(event)

        Publish a new event :samp:`event`.
        :samp:`event` must be a dictionary and will be sent as json string.

        """
        self.mqtt.publish('/devices/' + self.device_id + '/events', json.dumps(event))

    def publish_state(self, state):
        """
.. method:: publish_state(state)

        Publish a new state :samp:`state`.
        :samp:`state` must be a dictionary and will be sent as json string.

        """
        self.mqtt.publish('/devices/' + self.device_id + '/state', json.dumps(state))

    def _is_config(self, mqtt_data):
        if ('message' in mqtt_data):
            return (mqtt_data['message'].topic == ('/devices/' + self.device_id + '/config'))
        return False

    def _handle_config(self, mqtt_client, mqtt_data):
        state_update = self._config_cbk(json.loads(mqtt_data['message'].payload))
        if state_update is not None:
            self.publish_state(state_update)

    def on_config(self, config_cbk):
        """
.. method:: on_config(config_cbk)

        Set a callback to be called on config updates.

        :samp:`config_cbk` callback will be called passing a dictionary containing requested config as the only parameter::

            def config_callback(config):
                print('requested publish period:', config['publish_period'])
                return {'publish_period': config['publish_period']}

            my_device.on_config(config_cbk)

        If the callback returns a dictionary, it will be immediately sent as updated device state.
        """
        if self._config_cbk is None:
            self.mqtt.subscribe([['/devices/' + self.device_id + '/config', 1]])
        self._config_cbk = config_cbk
        self.mqtt.on(mqtt.PUBLISH, self._handle_config, self._is_config)
