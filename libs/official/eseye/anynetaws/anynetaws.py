# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2018-04-06 12:31:26
# @Last Modified by:   Lorenzo
# @Last Modified time: 2018-04-13 10:05:14

"""
.. module:: anynetaws

************************
Eseye AnyNet AWS Library
************************

The Zerynth Eseye AnyNet AWS Library allows to easily connect to `AWS IoT platform <https://aws.amazon.com/iot-platform/>`_ thanks to Eseye AnyNet AWS AT modem.

    """

import streams
import threading

new_exception(SocketUsageError, IOError)

_any_ch = None

_subs_handler = None
_urcs_handler = None
_blocks_handler = None

class SubsHandler:

    def __init__(self):
        self._cbks = [None, None]
        self._topics = [None, None]

    def set_callback(self, index, topic, fn):
        self._topics[index] = topic
        self._cbks[index] = fn

    def call(self, index, data):
        return self._cbks[index](index, self._topics[index], data)

# URCs: 
#
#   +AWSPUBOPEN
#   +AWSSUBOPEN
#   +AWS
#   +AWSPUBCLOSE

class URCsHandler:

    def __init__(self):
        self.lock = threading.Lock()
        self.event = threading.Event()
        self.resp = None
        self.current = None

class BlocksCmdsHandler:
    def __init__(self):
        self.lock = threading.Lock()
        self.event = threading.Event()
        self.resp = [None, None]
        self.current = None
        self.prompt = None


def _anynet_readloop():
    while True:
        response = _any_ch.read(1)
        if response[0] == 0:
            # sometimes a leading null byte appears...
            continue
        if response[0] != ord('>'):
            response = response + _any_ch.readline()
        #print(response)
        if response == '\r\n' or response == '\r\r\n':
            continue
        if response.startswith('AT+'):
            # echo
            continue
        if (response == 'OK\r\n' or response == 'SEND OK\r\n') and _blocks_handler.current: 
            _blocks_handler.resp[0] = 0
            _blocks_handler.event.set()
        elif (response == 'ERROR\r\n' or response == 'SEND FAIL\r\n') and _blocks_handler.current:
            _blocks_handler.resp[0] = -1
            _blocks_handler.event.set()
        elif response[0] == ord('+'):
            if _blocks_handler.current and response[1:].startswith(_blocks_handler.current + ':'):
                # response to block_cmd
                # add response skipping "+CMD: " and stripping '\r\n'
                _blocks_handler.resp[1].append(response[1+len(_blocks_handler.current)+2:-2])
            else:
                # unsolicited response
                if response.startswith('+AWS:'):
                    # skip +AWS:, strip \r\n and split
                    urc_resp = response[5:-2].split(',')
                    bin_length = int(urc_resp[1])
                    bin_data = _any_ch.read(bin_length)
                    # call subscribe callback
                    _subs_handler.call(int(urc_resp[0]), bin_data)
                elif response[1:].startswith(_urcs_handler.current):
                    urc_resp = response[1+len(_urcs_handler.current)+1:-2].strip(' ').split(',')
                    _urcs_handler.resp = urc_resp
                    _urcs_handler.event.set()
        elif response[0] == ord('>') and _blocks_handler.current:
            _any_ch.write(_blocks_handler.prompt)
        elif _blocks_handler.current:
            # response to block_cmd without command as prefix, strip '\r\n'
            _blocks_handler.resp[1].append(response[:-2])
        else:
            # unrecognized...
            pass

def _block_cmd(cmdstr, prompt=None, question=False, cmdargs=None):
    _blocks_handler.lock.acquire()
    _blocks_handler.prompt = prompt
    _blocks_handler.current = cmdstr
    _blocks_handler.resp[1] = []
    if question:
        cmdstr += '?'
    if cmdargs is not None:
        cmdstr += '=' + ','.join(cmdargs)
    _any_ch.write('AT+' + cmdstr + '\r\n')
    _blocks_handler.event.wait()
    _blocks_handler.event.clear()
    resp_code = _blocks_handler.resp[0]
    resp_content = _blocks_handler.resp[1]
    _blocks_handler.current = None
    _blocks_handler.lock.release()
    return resp_code, resp_content

def _urc_cmd(cmdstr, cmdargs=None):
    _urcs_handler.lock.acquire()
    _urcs_handler.current = cmdstr
    code, content = _block_cmd(cmdstr, cmdargs=cmdargs)
    if code != 0:
        _urcs_handler.current = None
        _urcs_handler.lock.release()
        raise ValueError
    _urcs_handler.event.wait()
    _urcs_handler.event.clear()
    resp_content = _urcs_handler.resp
    _urcs_handler.current = None
    _urcs_handler.lock.release()
    return resp_content

def init(serdrv, serbaud=9600):
    """
.. function:: init(serdrv, serbaud=9600)

    :param serdrv: serial communication driver (e.g., :samp:`SERIAL0`, :samp:`SERIAL1`, ...)
    :param serbaud: serial communication baudrate

    Initialize serial communication with the Eseye AWS AT modem.

    """
    global _any_ch, _blocks_handler, _urcs_handler, _subs_handler
    _blocks_handler = BlocksCmdsHandler()
    _urcs_handler = URCsHandler()
    _subs_handler = SubsHandler()
    _any_ch = streams.serial(serdrv, baud=serbaud, set_default=False)
    thread(_anynet_readloop)

def state(string_format=True):
    """
.. function:: state(string_format=True)

    :param string_format: :samp:`True` or :samp:`False` to select string or integer output format respectively

    Retrieve modem state, returned as an integer in the range :samp:`0`,:samp:`8` or a string in the list::

        [
            'Idle',
            'Waiting Keys',
            'Connecting to Network',
            'Establishing SSL',
            'SSL Connected',
            'Connecting MQTT',
            'Ready: MQTT Connected',
            'Ready: Subscribed',
            'Error'
        ]
    """
    code, content = _block_cmd('AWSSTATE', question=True)
    if code == 0 and len(content) == 1:
        state = int(content[0])
        if string_format:
            states = ['Idle', 'Waiting Keys', 'Connecting to Network',
                      'Establishing SSL', 'SSL Connected', 'Connecting MQTT', 
                      'Ready: MQTT Connected', 'Ready: Subscribed', 'Error']
            return states[state]
        return state
    raise ValueError

def qccid():
    """
.. function:: qccid()

    Retrieve the ICCD of AnyNet Secure SIM.
    """
    code, content = _block_cmd('QCCID')
    if code == 0 and len(content) == 1:
        return content[0]
    raise ValueError

def version():
    """
.. function:: version()

    Retrieve the version of the Eseye AWS AT modem firmware.
    """
    code, content = _block_cmd('AWSVER')
    if code == 0 and len(content) == 1:
        return content[0]
    raise ValueError

def reset():
    """
.. function:: reset()

    Force a reload of parameters from the SIM card, forcing the modem to reset
    """
    code, content = _block_cmd('AWSRESET')
    if code != 0:
        raise ValueError

def _open_index(cmd, topic):
    code, content = _block_cmd(cmd, question=True)
    if code != 0:
        raise ValueError
    for resp_topic in content:
        awstopic = '/'.join(resp_topic.split('/')[:-1]) # -1 is thingname
        awspindex, awstopic = awstopic.split(':')
        if awstopic[1:] == topic:
            return int(awspindex)
    return None

def _open(cmd, topic, sock_index):
    response_code = int(_urc_cmd(cmd, cmdargs=(str(sock_index), '"'+topic+'"'))[1])
    if response_code == -2:
        raise SocketUsageError
    if response_code == -1:
        raise ValueError

def _close(cmd, sock_index):
    response_code = int(_urc_cmd(cmd, cmdargs=(str(sock_index, )))[1])
    if response_code == -2:
        raise SocketUsageError
    if response_code == -1:
        raise ValueError

def pubopen(topic, sock_index):
    """
.. function:: pubopen(topic, sock_index)

    :param topic: a string representing a valid mqtt topic (note that the modem firmware automatically appends AWS IoT Thing name to chosen topic)
    :param sock_index: an integer representing a valid modem socket index :samp:`(0,1)`

    Open a publish *channel* to topic :samp:`topic` through socket index :samp:`sock_index`.
    Eseye AWS AT modem needs a publish *channel* to be open before starting publishing on a selected topic.
    A publish *channel* is open on top of an available socket represented by a socket index.
    Only one *channel* can be open on a single socket index, when trying to open a *channel* on an already used socket a :samp:`SocketUsageError` exception is raised.

    """
    _open('AWSPUBOPEN', topic, sock_index)

def pubopen_index(topic):
    """
.. function:: pubopen_index(topic)

    :param topic: a string representing a valid mqtt topic (note that the modem firmware automatically appends AWS IoT Thing name to chosen topic)

    Check if a publish *channel* for topic :samp:`topic` is already open on any of the available modem sockets, returning :samp:`None` if none is found, socket index otherwise.
    """
    return _open_index('AWSPUBOPEN', topic)

def publish(topic, payload, sock_index=0, qos=1, mode=2):
    """
.. function:: publish(topic, payload, sock_index=0, qos=1, mode=2)

    :param topic: a string representing a valid mqtt topic (note that the modem firmware automatically appends AWS IoT Thing name to chosen topic)
    :param payload: a string, bytes or bytearray object to be sent
    :param sock_index: an integer representing a valid modem socket index :samp:`(0,1)`
    :param qos: an integer representing the qos level to send the mqtt message with :samp:`(1,2,3)`
    :param mode: an integer representing a valid publish mode :samp:`(0,1,2)`

    Publish a message on a chosen topic in one of the following modes:

        0. publish the message without opening a publish *channel*, which must be already open when calling this function
        1. open (:func:`pubopen`) a publish *channel* and publish the message without checking if a publish *channel* is already open on that topic
        2. open (:func:`pubopen`) a publish *channel* and publish the message checking if a *channel* is already open on chosen topic, if so the socket index on which the *channel* is already open overwrites passed one

    """
    if mode == 2:
        pindex = pubopen_index(topic)
        if pindex is not None:
            sock_index = pindex
    if mode == 1 or (mode == 2 and pindex is None):
        pubopen(topic, sock_index)
        # response[1] == 1 Success
    _block_cmd('AWSPUBLISH', cmdargs=(str(sock_index), str(len(payload)), str(qos)), prompt=payload)

def pubclose(sock_index):
    """
.. function:: pubclose(sock_index)

    :param sock_index: an integer representing a valid modem socket index :samp:`(0,1)`

    Close a publish *channel* open on socket :samp:`sock_index`.
    """
    _close('AWSPUBCLOSE')

def subopen(topic, sock_index):
    """
.. function:: subopen(topic, sock_index)

    :param topic: a string representing a valid mqtt topic (note that the modem firmware automatically appends AWS IoT Thing name to chosen topic)
    :param sock_index: an integer representing a valid modem socket index :samp:`(0,1)`

    Open a subscription *channel* for topic :samp:`topic` through socket index :samp:`sock_index`.
    A subscription *channel* is open on top of an available socket represented by a socket index.
    Only one *channel* can be open on a single socket index, when trying to open a *channel* on an already used socket a :samp:`SocketUsageError` exception is raised.

    Refer to :func:`subscribe` function to associate a callback function to chosen subscription.
    """
    _open('AWSSUBOPEN', topic, sock_index)

def subopen_index(topic):
    """
.. function:: subopen_index(topic)

    :param topic: a string representing a valid mqtt topic (note that the modem firmware automatically appends AWS IoT Thing name to chosen topic)

    Check if a subscription *channel* for topic :samp:`topic` is already open on any of the available modem sockets, returning :samp:`None` if none is found, socket index otherwise.
    """
    return _open_index('AWSSUBOPEN', topic)


def subclose(sock_index):
    """
.. function:: subclose(sock_index)

    :param sock_index: an integer representing a valid modem socket index :samp:`(0,1)`

    Close a subscription open on socket :samp:`sock_index`
    """
    _close('AWSSUBCLOSE', sock_index)

def subscribe(topic, callback, sock_index=0, mode=1):
    """
.. function:: subscribe(topic, callback, sock_index=0, mode=1)

    :param topic: a string representing a valid mqtt topic (note that the modem firmware automatically appends AWS IoT Thing name to chosen topic)
    :param callback: a function to be called when a message arrives on chosen topic
    :param sock_index: an integer representing a valid modem socket index :samp:`(0,1)`
    :param mode: an integer representing a valid subscription mode :samp:`(0,1)`

    Subscribe to topic :samp:`topic` calling :samp:`callback` function whenever a new message arrives on chosen topic.
    Example callback function::

        def my_callback(sock_index, topic, data):
            print('> callback from', topic)
            print('> on socket ', sock_index)
            print('> with content:', data)
    
    As reported, a callback function must accept three arguments.

    Depending on selected mode, the following actions are executed calling the :func:`subscribe` function:

        0. open (:func:`subopen`) a subscription *channel*, setting a callback, without checking if a *channel* is already open on chosen topic
        1. open (:func:`subopen`) a subscription *channel*, setting a callback, checking if a *channel* is already open on chosen topic, if so the socket index on which the *channel* is already open overwrites passed one
    """
    if mode == 1:
        pindex = subopen_index(topic)
        if pindex is not None:
            sock_index = pindex
    if mode == 0 or (mode == 1 and pindex is None):
        subopen(topic, sock_index)
    _subs_handler.set_callback(sock_index, topic, callback)
