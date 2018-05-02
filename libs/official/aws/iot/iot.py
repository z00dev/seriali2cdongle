# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2017-09-21 16:17:16
# @Last Modified by:   Lorenzo
# @Last Modified time: 2018-01-18 15:04:16

"""
.. module:: iot

*******************************
Amazon Web Services IoT Library
*******************************

The Zerynth AWS IoT Library can be used to ease the connection to the `AWS IoT platform <https://aws.amazon.com/iot-platform/>`_.

It allows to make your device act as an AWS IoT Thing which can be registered through AWS tools or directly from the :ref:`Zerynth Toolchain <ztc-cmd-aws>`.

Check this video for a live demo:

.. raw:: html

    <div style="margin-top:10px;">
  <iframe width="100%" height="480" src="https://www.youtube.com/embed/IZzZF3DGWkY?ecver=1" frameborder="0" gesture="media" allow="encrypted-media" allowfullscreen></iframe>
      </div>


    """

import json
import ssl
from mqtt import mqtt

import mcu



class AWSMQTTClient(mqtt.Client):

    def __init__(self, mqtt_id, endpoint, ssl_ctx):
        mqtt.Client.__init__(self, mqtt_id, clean_session=True)
        self.endpoint = endpoint
        self.ssl_ctx = ssl_ctx

    def connect(self, port=8883):
        mqtt.Client.connect(self, self.endpoint, 60, port=port, ssl_ctx=self.ssl_ctx)


class Thing:
    """
===============
The Thing class
===============

.. class:: Thing(endpoint, mqtt_id, clicert, pkey, thingname=None, cacert=None)

        Create a Thing instance representing an AWS IoT Thing.

        The Thing object will contain an mqtt client instance pointing to AWS IoT MQTT broker located at :samp:`endpoint` endpoint.
        The client is configured with :samp:`mqtt_id` as MQTT id and is able to connect securely through AWS authorized :samp:`pkey` private key and :samp:`clicert` certificate (an optional :samp:`cacert` CA Certificate can also be passed).

        The client is accessible through :samp:`mqtt` instance attribute and exposes all :ref:`Zerynth MQTT Client methods <lib.zerynth.mqtt>` so that it is possible, for example, to setup
        custom callback on MQTT commands.
        The only difference concerns mqtt.connect method which does not require broker url and ssl context, taking them from Thing configuration::

            my_thing = iot.Thing('my_ep_id.iot.my_region.amazonaws.com', 'my_thing_id', clicert, pkey)
            my_thing.mqtt.connect()
            ...
            my_thing.mqtt.loop()

        A :samp:`thingname` different from chosen MQTT id can be specified, otherwise :samp:`mqtt_id` will be assumed also as Thing name.
    """

    def __init__(self, endpoint, mqtt_id, clicert, pkey, thingname=None, cacert=None):
        if cacert is None:
            cacert = __lookup(SSL_CACERT_VERISIGN_CLASS_3_PUBLIC_PRIMARY_CERTIFICATION_AUTHORITY___G5)
        self.ctx = ssl.create_ssl_context(cacert=cacert,clicert=clicert,pkey=pkey,options=ssl.CERT_REQUIRED|ssl.SERVER_AUTH)
        self.mqtt = AWSMQTTClient(mqtt_id, endpoint, self.ctx)
        self.thingname = (thingname or mqtt_id)

        self._shadow_cbk = None
        self._client_token = ''.join([ str(xx) for xx in mcu.uid()])

    def update_shadow(self, state):
        """
.. method:: update_shadow(state)

        Update thing shadow with reported :samp:`state` state.

        :samp:`state` must be a dictionary containing only custom state keys and values::

            my_thing.update_shadow({'publish_period': 1000})

        """
        shadow_rep = { 'state': { 'reported': state }}
        self.mqtt.publish('$aws/things/' + self.thingname + '/shadow/update', json.dumps(shadow_rep))

    def _is_shadow_delta(self, mqtt_data):
        if ('message' in mqtt_data):
            return (mqtt_data['message'].topic == ('$aws/things/' + self.thingname + '/shadow/update/delta'))
        return False

    def _handle_shadow_request(self, mqtt_client, mqtt_data):
        reported = self._shadow_cbk(json.loads(mqtt_data['message'].payload)['state'])
        if reported is not None:
            self.update_shadow(reported)

    def on_shadow_request(self, shadow_cbk):
        """
.. method:: on_shadow_request(shadow_cbk)

        Set a callback to be called on shadow update requests.

        :samp:`shadow_cbk` callback will be called with a dictionary containing requested state as the only parameter::

            def shadow_callback(requested):
                print('requested publish period:', requested['publish_period'])

            my_thing.on_shadow_request(shadow_callback)

        If a dictionary is returned, it is automatically published as reported state.
        """
        if self._shadow_cbk is None:
            self.mqtt.subscribe([['$aws/things/' + self.thingname + '/shadow/update/delta',0]])
        self._shadow_cbk = shadow_cbk
        self.mqtt.on(mqtt.PUBLISH, self._handle_shadow_request, self._is_shadow_delta)


