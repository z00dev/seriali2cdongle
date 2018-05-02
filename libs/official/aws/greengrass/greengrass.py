# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2018-01-16 11:03:57
# @Last Modified by:   Lorenzo
# @Last Modified time: 2018-01-18 10:04:17

"""
.. module:: greengrass

**************************************
Amazon Web Services Greengrass Library
**************************************

The Zerynth AWS Greengrass Library contains helper functions for IoT devices to retrieve info about an `AWS Greengrass Core <https://aws.amazon.com/greengrass/>`_.


.. note:: to connect to an AWS Greengrass Core after info retrieval use :ref:`Zerynth AWS IoT Core Library <lib.aws.iot>`

    """

import requests
import ssl

new_exception(GreengrassDiscoveryInfoException, Exception)

class DiscoveryInfo:
    """
=======================
The DiscoveryInfo class
=======================

.. class:: DiscoveryInfo(raw_info)

        A DiscoveryInfo instance is returned by :func:`greengrass.discover` function.

        It exposes the following attributes and methods:

            * :attr:`DiscoveryInfo.raw` dictionary containing raw `discovery response <https://docs.aws.amazon.com/greengrass/latest/developerguide/gg-discover-api.html#gg-discover-response-doc>`_.
            * :meth:`DiscoveryInfo.CA`
            * :meth:`DiscoveryInfo.connectivity`

    """
    def __init__(self, raw_info):
        self.single_connectivity = False
        self.single_ca = False

        if len(raw_info['GGGroups']) == 1:
            if (len(raw_info['GGGroups'][0]['Cores']) == 1 and
                len(raw_info['GGGroups'][0]['Cores'][0]['Connectivity']) == 1):

                self.single_connectivity = True

            if len(raw_info['GGGroups'][0]['CAs']) == 1:
                self.single_ca = True

        self.raw = raw_info

    def CA(self):
        """
.. method:: CA()

    Returns Greengrass Core CA Certificate if only one Server Certificate is returned by discover call.
    Raises :code:`GreengrassDiscoveryInfoException` if more than one certificate is returned.

        """
        if not self.single_ca:
            raise GreengrassDiscoveryInfoException
        return bytes(self.raw['GGGroups'][0]['CAs'][0].replace('\\n','\n') + '\x00')

    def connectivity(self):
        """
.. method:: connectivity()

    Returns a tuple :code:`(core_address, core_port)` with Greengrass Core address and port if only one Core is returned by discover call.
    Raises :code:`GreengrassDiscoveryInfoException` if more than one Core is returned.        

        """
        if not self.single_connectivity:
            raise GreengrassDiscoveryInfoException
        cinfo = self.raw['GGGroups'][0]['Cores'][0]['Connectivity'][0]
        return (cinfo['HostAddress'], cinfo['PortNumber'])

def discover(endpoint, thingname, clicert, pkey, cacert=None):
    """
================
Helper Functions
================

.. function:: discover(endpoint, thingname, clicert, pkey, cacert=None)

        :param endpoint: AWS server where to retrieve Greengrass core info
        :param thingname: AWS IoT Core or AWS Greengrass Device name
        :param clicert: client certificate
        :param pkey: client private key

    Discover info about own group Greengrass Core.
    Returns a :class:`DiscoveryInfo` object.

    """
    if cacert is None:
        cacert = __lookup(SSL_CACERT_VERISIGN_CLASS_3_PUBLIC_PRIMARY_CERTIFICATION_AUTHORITY___G5)
    ctx = ssl.create_ssl_context(cacert=cacert,clicert=clicert,pkey=pkey,options=ssl.CERT_REQUIRED|ssl.SERVER_AUTH)
    rr = requests.get('https://' + endpoint + ':8443/greengrass/discover/thing/' + thingname, ctx=ctx)
    return DiscoveryInfo(rr.json())
