# Copyright (c) 2017 Zerynth Team <http://www.zerynth.com/>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# and Eclipse Distribution License v1.0 which accompany this distribution.
#
# The Eclipse Public License is available at
#    http://www.eclipse.org/legal/epl-v10.html
# and the Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.

"""
.. module:: mqtt

************
MQTT Library
************

This module contains an implementation of the MQTT protocol (client-side) based on the work
of Roger Light <roger@atchoo.org> from the `paho-project <https://eclipse.org/paho/>`_.

When publishing and subscribing, a client is able to specify a quality of service (QoS) level
for messages which activates procedures to assure a message to be actually delivered or
received, available levels are:

    * 0 - at most once
    * 1 - at least once
    * 2 - exactly once

.. note:: Resource clearly explaining the QoS feature: `mqtt-quality-of-service-levels <http://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels>`_

Back to the implementation Zerynth mqtt.Client class provides methods to:

    * connect to a broker
    * publish
    * subscribe
    * unsubscribe
    * disconnect from the broker


and a system of **callbacks** to handle incoming packets.

    """

import socket
import threading
import timers
import streams

import ssl

MQTTv311 = 4
PROTOCOL_NAMEv311 = "MQTT"

PORT = 1883

# Message types
CONNECT = 0x10
CONNACK = 0x20
PUBLISH = 0x30
PUBACK = 0x40
PUBREC = 0x50
PUBREL = 0x60
PUBCOMP = 0x70
SUBSCRIBE = 0x80
SUBACK = 0x90
UNSUBSCRIBE = 0xA0
UNSUBACK = 0xB0
PINGREQ = 0xC0
PINGRESP = 0xD0
DISCONNECT = 0xE0


# kept from paho-mqtt code even if not used
# CONNACK codes
# CONNACK_ACCEPTED = 0
# CONNACK_REFUSED_PROTOCOL_VERSION = 1
# CONNACK_REFUSED_IDENTIFIER_REJECTED = 2
# CONNACK_REFUSED_SERVER_UNAVAILABLE = 3
# CONNACK_REFUSED_BAD_USERNAME_PASSWORD = 4
# CONNACK_REFUSED_NOT_AUTHORIZED = 5

# Connection state
mqtt_cs_new = 0
mqtt_cs_connected = 1
mqtt_cs_disconnecting = 2
mqtt_cs_disconnected = 3
mqtt_cs_reconnecting = 4

reconnection_max_retry = 25

# Message state
mqtt_ms_invalid = 0
mqtt_ms_publish= 1
mqtt_ms_wait_for_puback = 2
mqtt_ms_wait_for_pubrec = 3
mqtt_ms_resend_pubrel = 4
mqtt_ms_wait_for_pubrel = 5
mqtt_ms_resend_pubcomp = 6
mqtt_ms_wait_for_pubcomp = 7
mqtt_ms_send_pubrec = 8

# Error values
# MQTT_ERR_AGAIN = -1
MQTT_ERR_SUCCESS = 0
# MQTT_ERR_NOMEM = 1
# MQTT_ERR_PROTOCOL = 2
# MQTT_ERR_INVAL = 3
# MQTT_ERR_NO_CONN = 4
# MQTT_ERR_CONN_REFUSED = 5
# MQTT_ERR_NOT_FOUND = 6
# MQTT_ERR_CONN_LOST = 7
# MQTT_ERR_TLS = 8
# MQTT_ERR_PAYLOAD_SIZE = 9
# MQTT_ERR_NOT_SUPPORTED = 10
# MQTT_ERR_AUTH = 11
# MQTT_ERR_ACL_DENIED = 12
# MQTT_ERR_UNKNOWN = 13
# MQTT_ERR_ERRNO = 14

GENERIC_CBK  = 0
SPECIFIC_CBK = 1

# Last activity update
LA_OUT = 0
LA_IN = 1
LA_BOTH = 2

new_exception(MQTTError,Exception)
new_exception(MQTTConnectionError,MQTTError)
new_exception(MQTTProtocolError,MQTTError)

debug = False

def print_d(*args):
    if debug:
        print(*args)


def _append16(b_array, val):
    if val < 256:
        b_array.append(0)
    else:
        b_array.append(val // 256)
    b_array.append(val % 256)

def _unpack16(b_array, index):
    t = b_array[index+1] + b_array[index]
    return (t, index+2)

class inpacket:
    def __init__(self):
        self.reset()

    def reset(self):
        self.command = 0
        self.have_remaining = 0
        self.remaining_count = []
        self.remaining_mult = 1
        self.remaining_length = 0
        self.packet = bytearray()
        self.to_process = 0
        self.pos = 0
        self.data = {}

class MQTTMessage:
    """
=================
MQTTMessage class
=================

.. class:: MQTTMessage

    This is a class that describes an incoming message. It is passed to
    callbacks as *message* field in the *data* dictionary.

    Members:

    * topic : String. topic that the message was published on.
    * payload : String. the message payload.
    * qos : Integer. The message Quality of Service 0, 1 or 2.
    * retain : Boolean. If true, the message is a retained message and not fresh.
    * mid : Integer. The message id.
    """
    def __init__(self):
        self.timestamp = 0
        self.state = mqtt_ms_invalid
        self.dup = False
        self.mid = 0
        self.topic = ""
        self.payload = ""
        self.qos = 0
        self.retain = False

class Client():
    """
============
Client class
============

.. class:: Client

    This is the main module class.
    After connecting to a broker it is suggested to subscribe to some channels
    and configure callbacks.
    Then, a non-blocking loop function, starts a separate thread to handle incoming
    packets.

    Example::

        my_client = mqtt.Client("myId",True)
        for retry in range(10):
            try:
                my_client.connect("test.mosquitto.org", 60)
                break
            except Exception as e:
                print("connecting...")
        my_client.subscribe([["cool/channel",1]])
        my_client.on(mqtt.PUBLISH, print_cool_stuff, is_cool)
        my_client.loop()

        # do something else...

    Details about the callback system under :func:`~mqtt.Client.on` method.
    """

    def __init__(self, client_id, clean_session=True, logfn=None):
        """
.. method:: __init__(client_id, clean_session=True)

    * *client_id* is the unique client id string used when connecting to the
      broker.

    * *clean_session* is a boolean that determines the client type. If True,
      the broker will remove all information about this client when it
      disconnects. If False, the client is a persistent client and
      subscription information and queued messages will be retained when the
      client disconnects.
      Note that a client will never discard its own outgoing messages if
      accidentally disconnected: calling reconnect() will cause the messages to
      be resent.
        """
        self._client_id = client_id
        self.clean_session = clean_session

        self._state = mqtt_cs_new

        # self._last_msg_in = None
        # self._last_msg_out = None
        self._last_activity_in = 0
        self._last_activity_out = 0

        self._will_topic = None
        self._will_payload = None
        self._will_qos = None
        self._will_retain = None

        self._username = None
        self._password = None

        self._out_lock = threading.Lock()
        self._last_activity_lock = threading.Lock()

        self._last_mid = 0

        self._in_packet = inpacket()

        self._in_messages = []
        self._in_message_lock = threading.Lock()

        self._out_messages = []
        self._out_message_lock = threading.Lock()

        self._callbacks = [ {}, [] ]

        self._message_retry = 20000

        self._reconnection_event = threading.Event()
        self._reconnection_retry = reconnection_max_retry

        self.logfn = self._nolog
        if logfn is not None:
            self.logfn = logfn

        self._is_closed = False

    # def _nolog(self,*args):
    #     pass

    def _nolog(self,logstr):
        pass

    def on(self,command,function,condition=None, priority=0):
        """
.. method:: on(command, function, condition=None, priority=0)

    Set a callback in response to an MQTT received command.

    * *command* is a constant referring to which MQTT command call the callback on, can be one of::

        mqtt.PUBLISH
        mqtt.PUBACK
        mqtt.PUBREC
        mqtt.PUBREL
        mqtt.PUBCOMP
        mqtt.SUBACK
        mqtt.UNSUBACK
        mqtt.PINGREQ
        mqtt.PINGRESP

    * *function* is the function to execute if *condition* is respected.
      It takes both the client itself and a *data* dictionary as parameters.
      The *data* dictionary may contain the following fields:

        * *message*: MQTTMessage present only on PUBLISH packets for messages
          with qos equal to 0 or 1, or on PUBREL packets for messages with
          qos equal to 2

    * *condition* is a function taking the same *data* dictionary as parameter
      and returning True or False if the packet respects a certain condition.
      *condition* parameter is optional because a generic callback can be set without
      specifying a condition, only in response to a command.
      A callback of this type is called a 'low priority' callback meaning that it
      is called only if all the more specific callbacks (the ones with condition)
      get a False condition response.

        Example::

            def is_cool(data):
                if ('message' in data):
                    return (data['message'].topic == "cool")
                # N.B. not checking if 'message' is in data could lead to Exception
                # on PUBLISH packets for messages with qos equal to 2
                return False

            def print_cool_stuff(client, data):
                print("cool: ", data['message'].payload)

            def print_generic_stuff(client, data):
                if ('message' in data):
                    print("not cool: ", data['message'].payload)

            my_client.on(mqtt.PUBLISH, print_cool_stuff, is_cool)
            my_client.on(mqtt.PUBLISH, print_generic_stuff)


        In the above example for every PUBLISH packet it is checked if the topic
        is *cool*, only if this condition fails, *print_generic_stuff* gets executed.
        """
        # generic => no condition, lowest priority
        if condition:
            self._callbacks[SPECIFIC_CBK].append([command,condition,function,priority])
        else:
            self._callbacks[GENERIC_CBK][command] = function

    def set_will(self, topic, payload, qos, retain):
        """
.. method:: set_will(topic, payload, qos, retain)

    Set client will.
        """
        self._will_topic = topic
        self._will_payload = payload
        self._will_qos = qos
        self._will_retain = retain

    def set_username_pw(self, username, password=None):
        """
.. method:: set_username_pw(username, password = None)

    Set connection username and password.
        """
        self._username = username
        self._password = password

    def connect(self, host, keepalive, port=PORT, ssl_ctx=None, breconnect_cb=None, aconnect_cb=None, sock_keepalive=None):
        """
.. method:: connect(host, keepalive, port=1883)

    Connects to a remote broker.

    * *host* is the hostname or IP address of the remote broker.
    * *port* is the network port of the server host to connect to. Defaults to
      1883.
    * *keepalive* is the maximum period in seconds between communications with the
      broker. If no other messages are being exchanged, this controls the
      rate at which the client will send ping messages to the broker.
    * *ssl_ctx* is an optional ssl context (:ref:`Zerynth SSL module <stdlib.ssl>`) for secure mqtt channels.
    * *sock_keepalive* is a list of int values (3 elements) representing in order count (pure number), idle (in seconds) and interval (in seconds) of the keepalive socket option (default None - disabled). 
        """
        # to allow defining inherited clients with different connect 
        # functions but preserving reconnection functionality
        self._connect(host, keepalive, port=port, ssl_ctx=ssl_ctx, breconnect_cb=breconnect_cb, aconnect_cb=aconnect_cb)

    def _connect(self, host, keepalive, port=PORT, ssl_ctx=None, breconnect_cb=None, aconnect_cb=None, sock_keepalive=None):
        self._before_reconnect = breconnect_cb
        self._after_connect  = aconnect_cb

        self._host = host
        self._port = port
        ip = __default_net["sock"][0].gethostbyname(host)

        self._ssl_ctx = ssl_ctx
        if ssl_ctx is None:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self._sock = ssl.sslsocket(ctx=ssl_ctx)

        try:
            self._sock.settimeout(keepalive*1000)
        except Exception as e:
            print(e)
            # no timeout
            pass

        if sock_keepalive and len(sock_keepalive) == 3:
            try:
                self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            except Exception as e:
                print(e)
                # no keepalive
                pass

            try:
                self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, sock_keepalive[0])
            except Exception as e:
                print(e)
                # no keepalive
                pass

            try:
                self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, sock_keepalive[1])
            except Exception as e:
                print(e)
                # no keepalive
                pass

            try:
                self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, sock_keepalive[2])
            except Exception as e:
                print(e)
                # no keepalive
                pass

        try:
            self._sock.connect((ip,port))
        except Exception as e:
            self._sock.close()
            raise e

        # protocol_name(str) + protocol_level + flags + keepalive + client_id(str)
        remaining_length = 2+4 + 1+1+2 + 2+len(self._client_id)

        connect_flags = 0
        if self.clean_session:
            connect_flags = connect_flags | 0x02

        if self._will_topic:
            if self._will_payload is not None:
                remaining_length = remaining_length + 2+len(self._will_topic) + 2+len(self._will_payload)
            else:
                remaining_length = remaining_length + 2+len(self._will_topic) + 2

            connect_flags = connect_flags | 0x04 | ((self._will_qos & 0x03) << 3) | ((self._will_retain & 0x01) << 5)

        if self._username:
            remaining_length = remaining_length + 2+len(self._username)
            connect_flags = connect_flags | 0x80
            if self._password:
                connect_flags = connect_flags | 0x40
                remaining_length = remaining_length + 2+len(self._password)

        packet = bytearray()

        #fixed header
        packet.append(CONNECT)
        self._pack_remaining_length(packet, remaining_length)

        # variable header
        self._pack_str16(packet,PROTOCOL_NAMEv311) # protocol name
        packet.append(MQTTv311) # protocol level
        packet.append(connect_flags)
        _append16(packet, keepalive)
        self._pack_str16(packet, self._client_id)

        if self._will_topic:
            self._pack_str16(packet, self._will_topic)
            # CHECK!!
            if self._will_payload:
                self._pack_str16(packet, self._will_payload)

        if self._username:
            self._pack_str16(packet, self._username)

            if self._password:
                self._pack_str16(packet, self._password)

        self.keepalive = keepalive

        self._sock.sendall(packet)

        self._handle_connack()
        self._update_last_activity(LA_BOTH)

        if self._after_connect is not None:
            self._after_connect(self)

        rc = 0

        # code below for reconnection

        # at the moment rc is always set to None by self._send_publish: useless

        self._out_message_lock.acquire()
        for m in self._out_messages:
            m.timestamp = timers.now()

            if m.qos == 0:
                rc = self._send_publish(m.mid, m.topic, m.payload, m.qos, m.retain, m.dup)
                if rc != 0:
                    self._out_message_lock.release()
                    return rc
            elif m.qos == 1:
                if m.state == mqtt_ms_publish:
                    m.state = mqtt_ms_wait_for_puback
                    rc = self._send_publish(m.mid, m.topic, m.payload, m.qos, m.retain, m.dup)
                    if rc != 0:
                        self._out_message_lock.release()
                        return rc
            elif m.qos == 2:
                if m.state == mqtt_ms_publish:
                    m.state = mqtt_ms_wait_for_pubrec
                    rc = self._send_publish(m.mid, m.topic, m.payload, m.qos, m.retain, m.dup)
                    if rc != 0:
                        self._out_message_lock.release()
                        return rc
                elif m.state == mqtt_ms_resend_pubrel:
                    m.state = mqtt_ms_wait_for_pubcomp
                    rc = self._send_pubrel(m.mid, m.dup)
                    if rc != 0:
                        self._out_message_lock.release()
                        return rc
        self._out_message_lock.release()
        return MQTT_ERR_SUCCESS

    def reconnect(self):
        """
.. method:: reconnect()

    Reconnects the client if accidentally disconnected.
        """
        if self._is_closed:
            while True:
                # DO NOT DIE FOR ESP32, REMOVE!
                sleep(1000)
        self._sock.close()
        while True:

            if self._reconnection_retry < 0:
                self._reconnection_event.set()
                raise MQTTConnectionError

            self._reconnection_event.clear()
            self._state = mqtt_cs_reconnecting

            self._reset_in_packet()
            self._update_last_activity(LA_BOTH)

            self._messages_reconnect_reset()

            if self._before_reconnect is not None:
                self._before_reconnect(self)

            try:
                self._connect(self._host,self.keepalive,self._port, ssl_ctx=self._ssl_ctx,
                    breconnect_cb=self._before_reconnect, aconnect_cb=self._after_connect)
                self._reconnection_retry = reconnection_max_retry
                self._reconnection_event.set()

                self._send_pingreq()
                break
            except Exception as e:
                self._state = mqtt_cs_disconnected
                self._reconnection_retry -= 1

    def subscribe(self,topics):
        """
.. method:: subscribe(topics)

    Subscribes to one or more topics.

    * *topis* a list structured this way::

      [[topic1,qos1],[topic2,qos2],...]

      where topic1,topic2,... are strings and qos1,qos2,... are integers for
      the maximum quality of service for each topic
        """
        remaining_length = 2
        for t in topics:
            remaining_length = remaining_length + 2+len(t[0])+1

        command = SUBSCRIBE | 2
        packet = bytearray()
        packet.append(command)
        self._pack_remaining_length(packet, remaining_length)
        local_mid = self._mid_generate()
        _append16(packet,local_mid)
        for t in topics:
            self._pack_str16(packet, t[0])
            packet.append(t[1])
        self._safe_send(packet)

    def unsubscribe(self, topics):
        """
.. method:: unsubscribe(topics)

    Unsubscribes the client from one or more topics.

    * *topics* is list of strings that are subscribed topics to unsubscribe from.
        """
        remaining_length = 2
        for t in topics:
            remaining_length = remaining_length + 2+len(t)

        command = UNSUBSCRIBE | 2
        packet = bytearray()
        packet.append(command)
        self._pack_remaining_length(packet, remaining_length)
        local_mid = self._mid_generate()
        _append16(packet,local_mid)
        for t in topics:
            self._pack_str16(packet, t)
        self._safe_send(packet)

    def publish(self, topic, payload=None, qos=0, retain=False):
        """
.. method:: publish(topic, payload=None, qos=0, retain=False)

    Publishes a message on a topic.

    This causes a message to be sent to the broker and subsequently from
    the broker to any clients subscribing to matching topics.

    * *topic* is the topic that the message should be published on.
    * *payload* is the actual message to send. If not given, or set to None a
      zero length message will be used.
    * *qos* is the quality of service level to use.
    * *retain*: if set to true, the message will be set as the "last known
      good"/retained message for the topic.

    It returns the mid generated for the message to give the possibility to
    set a callback precisely for that message.
    """
        local_mid = self._mid_generate()

        if qos == 0:
            self._send_publish(local_mid, topic, payload, qos, retain, False)
            return local_mid
        else:
            message = MQTTMessage()
            message.timestamp = timers.now()

            message.mid = local_mid
            message.topic = topic
            if payload is None or len(payload) == 0:
                message.payload = None
            else:
                message.payload = payload

            message.qos = qos
            message.retain = retain
            message.dup = False

            self._out_message_lock.acquire()
            self._out_messages.append(message)
            if qos == 1:
                message.state = mqtt_ms_wait_for_puback
            elif qos == 2:
                message.state = mqtt_ms_wait_for_pubrec
            self._out_message_lock.release()

            self._send_publish(message.mid, message.topic, message.payload, message.qos, message.retain, message.dup)

            return local_mid

    def disconnect(self):
        """
.. method:: reconnect()

    Sends a disconnect message.
        """
        # self._state_lock.acquire()
        # self._state = mqtt_cs_disconnecting
        # self._state_lock.release()

        # if self._sock is None and self._ssl is None:
        #     return MQTT_ERR_NO_CONN

        return self._send_disconnect()

    def close(self):
        self._is_closed = True
        self._sock.close()

    def loop(self, on_message=None, th_size=-1):
        """
.. method:: loop(on_message = None)

    Non blocking loop method that starts a thread to handle incoming packets.

    * *on_message* is an optional argument to set a generic callback on messages
      with qos equal to 0, 1 or 2
        """
        if on_message:
            self.on(PUBREL,on_message)
            def qos_not_2(data):
                # data['message'] is not present if publish handled has qos = 2
                return ('message' in data)
            self.on(PUBLISH,on_message,qos_not_2,-1)
        thread(self._do_loop, size=th_size)


    def _do_loop(self):
        should_reconnect = False
        while True:
            try:
                self._read_packet()

                self._message_retry_check()

                if timers.now() > self._last_activity_out + self.keepalive*1000:
                    print_d("send ping tim_out")
                    self._send_pingreq()
            except TimeoutError:
                if timers.now() > self._last_activity_in + self.keepalive*1500:
                    print_d("la + ka", self._last_activity_in + self.keepalive)
                    # reconnect
                    should_reconnect = True
                else:
                    print_d("send ping tim_in")
                    self._send_pingreq()
            except IOError:
                # reconnect
                should_reconnect = True

            if should_reconnect:
                should_reconnect = False

                if self._state == mqtt_cs_reconnecting:
                    self._reconnection_event.wait()
                else:
                    self._state = mqtt_cs_disconnected
                    self.reconnect()


    def _handle_connack(self):
        pack_type = self._sock.recv(1)[0]
        if pack_type != CONNACK:
            raise MQTTProtocolError
        remaining_length = self._sock.recv(1)[0]
        if remaining_length != 2:
            raise MQTTProtocolError
        flags = self._sock.recv(1)[0]
        if not self.clean_session:
            session_present = flags & 0x01
        rc = self._sock.recv(1)[0]
        if rc == 0:
            self._state = mqtt_cs_connected
        elif rc > 0 and rc < 6:
            raise MQTTConnectionError
        else:
            raise MQTTProtocolError

    def _read_packet(self):
        self.logfn('receiving command')
        self._in_packet.command = self._sock.recv(1)[0]
        self.logfn('command: ' + str(self._in_packet.command))

        while True:
            byte = self._sock.recv(1)[0]
            self._in_packet.remaining_count.append(byte)
            # Max 4 bytes length for remaining length as defined by protocol.
            # Anything more likely means a broken/malicious client.
            if len(self._in_packet.remaining_count) > 4:
                raise MQTTProtocolError

            self._in_packet.remaining_length = self._in_packet.remaining_length + (byte & 127)*self._in_packet.remaining_mult
            self._in_packet.remaining_mult = self._in_packet.remaining_mult * 128

            if (byte & 128) == 0:
                break

        self._in_packet.have_remaining = 1
        self._in_packet.to_process = self._in_packet.remaining_length

        self._in_packet.packet = bytearray(self._in_packet.to_process)
        cur_process = 0
        while self._in_packet.to_process > 0:
            data = self._sock.recv(self._in_packet.to_process)
            self._in_packet.to_process = self._in_packet.to_process - len(data)
            self._in_packet.packet[cur_process:cur_process+len(data)] = data
            cur_process += len(data)

        self.logfn('ready to handle packet')
        # All data for this packet is read.
        self._in_packet.pos = 0
        try:
            self._handle_packet()
        except Exception as e:
            print_d(e)
        self.logfn('packet handled')
        self._update_last_activity(LA_IN)

        ######
        try:
            to_execute = None
            exe_priority = -100
            for c in self._callbacks[SPECIFIC_CBK]:
                # c is a list [command,condition,function,priority]
                if exe_priority >= c[3]:
                    continue
                if (self._in_packet.command & 0xF0) == c[0]:
                    if c[1](self._in_packet.data):
                        # if succeeds executing a specific, skips generic
                        # e.g. condition: data['message'].mid == my_mid => execute specific
                        # callback for this mid
                        to_execute = c[2]
                        exe_priority = c[3]

            if to_execute != None:
                to_execute(self, self._in_packet.data)
            else:
                for cmd,callback in self._callbacks[GENERIC_CBK].items():
                    if (self._in_packet.command & 0xF0) == cmd:
                        callback(self, self._in_packet.data)
        except Exception as ex:
            print_d(ex)
        ######

        # Free data and reset values
        self._reset_in_packet()

        # self._msgtime_lock.acquire()
        # self._last_msg_in = time.time()
        # self._msgtime_lock.release()
        # return rc

    def _handle_packet(self):
        cmd = self._in_packet.command & 0xF0
        if cmd == PINGREQ:
            self._handle_pingreq()
        elif cmd == PINGRESP:
            self._handle_pingresp()
        elif cmd == PUBACK:
            self._handle_pubackcomp()
        elif cmd == PUBCOMP:
            self._handle_pubackcomp()
        elif cmd == PUBLISH:
            self._handle_publish()
        elif cmd == PUBREC:
            self._handle_pubrec()
        elif cmd == PUBREL:
            self._handle_pubrel()
        elif cmd == SUBACK:
            self._handle_suback()
        elif cmd == UNSUBACK:
            self._handle_unsuback()
        else:
            # If we don't recognise the command, return an error straight away.
            raise MQTTProtocolError

    def _handle_pingresp(self):
        print_d("reading response...")
        if self._in_packet.remaining_length != 0:
            raise MQTTProtocolError
        self._in_packet.data['return_code'] = MQTT_ERR_SUCCESS

    def _handle_publish(self):
        header = self._in_packet.command
        message = MQTTMessage()
        message.dup = (header & 0x08)>>3
        message.qos = (header & 0x06)>>1
        message.retain = (header & 0x01)

        message.topic, c_pos = self._unpack_str16(0)

        if len(message.topic) == 0:
            raise MQTTProtocolError

        if message.qos > 0:
            message.mid, c_pos = _unpack16(self._in_packet.packet, c_pos)

        message.payload = str(self._in_packet.packet[c_pos:])
        message.timestamp = timers.now()
        if message.qos == 0:
            self._in_packet.data['message'] = message
            self._in_packet.data['return_code'] = MQTT_ERR_SUCCESS
        elif message.qos == 1:
            self._send_puback(message.mid)
            self._in_packet.data['message'] = message
            self._in_packet.data['return_code'] = MQTT_ERR_SUCCESS
        elif message.qos == 2:
            self._send_pubrec(message.mid)
            print_d("pubrec sent",message.mid)
            message.state = mqtt_ms_wait_for_pubrel
            self._in_message_lock.acquire()
            self._in_messages.append(message)
            self._in_message_lock.release()
            self._in_packet.data['return_code'] = MQTT_ERR_SUCCESS
        else:
            raise MQTTProtocolError

    def _handle_pubrel(self):
        if self._in_packet.remaining_length != 2:
            raise MQTTProtocolError

        if len(self._in_packet.packet) != 2:
            raise MQTTProtocolError

        mid,z = _unpack16(self._in_packet.packet,0)
        print_d("rec PUBREL (mid: "+str(mid)+")")

        self._in_message_lock.acquire()
        sel_i = None
        m = None
        for i in range(len(self._in_messages)):
            if self._in_messages[i].mid == mid:
                sel_i = i
        if sel_i != None:
            m = self._in_messages[sel_i]
            del self._in_messages[sel_i]
        self._in_message_lock.release()
        if sel_i != None:
            self._in_packet.data['message'] = m
            print_d("send pubcomp")
            self._send_pubcomp(mid)
        self._in_packet.data['return_code'] = MQTT_ERR_SUCCESS

    def _handle_pubackcomp(self):
        if self._in_packet.remaining_length != 2:
            raise MQTTProtocolError

        mid, z = _unpack16(self._in_packet.packet,0)

        self._out_message_lock.acquire()
        sel_i = None
        m = None
        for i in range(len(self._out_messages)):
            if self._out_messages[i].mid == mid:
                sel_i = i
        if sel_i:
            m = self._out_messages[sel_i]
            del self._out_messages[sel_i]
        self._out_message_lock.release()

        self._in_packet.data['return_code'] = MQTT_ERR_SUCCESS

    def _handle_pubrec(self):
        if self._in_packet.remaining_length != 2:
            raise MQTTProtocolError
        mid, z = _unpack16(self._in_packet.packet,0)
        print_d("Rec PUBREC mid:",mid)
        self._out_message_lock.acquire()
        for m in self._out_messages:
            if m.mid == mid:
                m.state = mqtt_ms_wait_for_pubcomp
                m.timestamp = timers.now()
                self._out_message_lock.release()
                return self._send_pubrel(mid, False)

        self._out_message_lock.release()
        self._in_packet.data['return_code'] = MQTT_ERR_SUCCESS

    def _handle_suback(self):
        print_d("Rec SUBACK")
        mid, c_pos = _unpack16(self._in_packet.packet,0)
        granted_qos = self._in_packet.packet[c_pos]

        print_d("rec mid:", mid)
        self._in_packet.data['mid'] = mid
        self._in_packet.data['granted_qos'] = granted_qos
        self._in_packet.data['return_code'] = MQTT_ERR_SUCCESS

    def _handle_unsuback(self):
        if self._in_packet.remaining_length != 2:
            raise MQTTProtocolError

        mid, z = _unpack16(self._in_packet.packet,0)
        self._in_packet.data['mid'] = mid
        self._in_packet.data['return_code'] = MQTT_ERR_SUCCESS

    def _safe_send(self, packet):
        if self._state == mqtt_cs_reconnecting:
            self._reconnection_event.wait()
        if self._state != mqtt_cs_connected:
            raise MQTTConnectionError

        self._out_lock.acquire()
        try:
            self._sock.sendall(packet)
        except IOError:
            print_d("ioerror")
            self._state = mqtt_cs_disconnected
            # try reconnecting
            self.reconnect()
        self._out_lock.release()
        self._update_last_activity(LA_OUT)
        print_d("last activity out:", self._last_activity_out)

    def _send_publish(self, mid, topic, payload=None, qos=0, retain=False, dup=False):
        command = PUBLISH | ((dup&0x1)<<3) | (qos<<1) | retain
        packet = bytearray()
        packet.append(command)
        if payload is None:
            remaining_length = 2+len(topic)
        else:

            remaining_length = 2+len(topic) + len(payload)

        if qos > 0:
            # For message id
            remaining_length = remaining_length + 2

        self._pack_remaining_length(packet, remaining_length)
        self._pack_str16(packet, topic)

        if qos > 0:
            # For message id
            _append16(packet,mid)

        if payload is not None:
            packet.extend(payload)

        self._safe_send(packet)

    def _send_simple_command(self, command):
        # For DISCONNECT, PINGREQ and (???) PINGRESP
        print_d("cmd:",command)
        remaining_length = 0
        packet = bytearray([command, remaining_length])

        self._safe_send(packet)

    def _send_disconnect(self):
        self._send_simple_command(DISCONNECT)

    def _send_pingreq(self):
        self._send_simple_command(PINGREQ)

    def _send_command_with_mid(self, command, mid, dup):
        # For PUBACK, PUBCOMP, PUBREC, and PUBREL
        if dup:
            command = command | 8

        remaining_length = 2
        packet = bytearray([command, remaining_length])
        _append16(packet,mid)
        self._safe_send(packet)

    def _send_puback(self, mid):
        self._send_command_with_mid(PUBACK, mid, False)

    def _send_pubrec(self, mid):
        self._send_command_with_mid(PUBREC, mid, False)

    def _send_pubcomp(self, mid):
        self._send_command_with_mid(PUBCOMP, mid, False)

    def _send_pubrel(self, mid, dup=False):
        self._send_command_with_mid(PUBREL|2, mid, dup)

    def _message_retry_check_actual(self, messages, lock):
        lock.acquire()
        now = timers.now()
        for m in messages:
            if m.timestamp + self._message_retry < now:
                if m.state == mqtt_ms_wait_for_puback or m.state == mqtt_ms_wait_for_pubrec:
                    m.timestamp = now
                    m.dup = True
                    self._send_publish(m.mid, m.topic, m.payload, m.qos, m.retain, m.dup)
                elif m.state == mqtt_ms_wait_for_pubrel:
                    m.timestamp = now
                    m.dup = True
                    self._send_pubrec(m.mid)
                elif m.state == mqtt_ms_wait_for_pubcomp:
                    m.timestamp = now
                    m.dup = True
                    self._send_pubrel(m.mid, True)
        lock.release()

    def _message_retry_check(self):
        self._message_retry_check_actual(self._out_messages, self._out_message_lock)
        self._message_retry_check_actual(self._in_messages, self._in_message_lock)

    def _messages_reconnect_reset_out(self):
        self._out_message_lock.acquire()
        for m in self._out_messages:
            m.timestamp = 0
            # if m.qos == 0:
            #     m.state = mqtt_ms_publish # not possible in my implementation
            if m.qos == 1:
                if m.state == mqtt_ms_wait_for_puback:
                    m.dup = True
                m.state = mqtt_ms_publish
            elif m.qos == 2:
                if m.state == mqtt_ms_wait_for_pubcomp:
                    m.state = mqtt_ms_resend_pubrel
                    m.dup = True
                else:
                    if m.state == mqtt_ms_wait_for_pubrec:
                        m.dup = True
                    m.state = mqtt_ms_publish
        self._out_message_lock.release()

    def _messages_reconnect_reset_in(self):
        self._in_message_lock.acquire()
        to_del = []
        for i in range(len(self._in_messages)):
            self._in_messages[i].timestamp = 0
            if self._in_messages[i].qos != 2:
                to_del.append(i)
            else:
                # Preserve current state
                pass
        for td in to_del:
            del self._in_messages[td]
        self._in_message_lock.release()

    def _messages_reconnect_reset(self):
        self._messages_reconnect_reset_out()
        self._messages_reconnect_reset_in()

    def _update_last_activity(self, direction):
        self._last_activity_lock.acquire()
        if direction == LA_OUT or direction == LA_BOTH:
            self._last_activity_out = timers.now()
        elif direction == LA_IN or direction == LA_BOTH:
            self._last_activity_in = timers.now()
        self._last_activity_lock.release()

    def _mid_generate(self):
        self._last_mid = (self._last_mid + 1) % 65536
        print_d("generated: ",self._last_mid)
        return self._last_mid

    def _pack_remaining_length(self, packet, remaining_length):
        while True:
            byte = remaining_length % 128
            remaining_length = remaining_length // 128
            # If there are more digits to encode, set the top bit of this digit
            if remaining_length > 0:
                byte = byte | 0x80

            packet.append(byte)
            if remaining_length == 0:
                # FIXME - this doesn't deal with incorrectly large payloads
                return packet

    def _pack_str16(self, packet, data):
        _append16(packet,len(data))
        packet.extend(data)

    def _unpack_str16(self, index):
        str_length = self._in_packet.packet[index+1]
        str_length += self._in_packet.packet[index]
        string = str(self._in_packet.packet[index+2:index+2+str_length])
        return (string, index+2+str_length)


    def _reset_in_packet(self):
        self._in_packet.reset()
