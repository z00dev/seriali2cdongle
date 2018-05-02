# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2017-10-12 17:03:35
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-11-13 16:01:46

"""
.. module:: 

******************************
Azure Shared Access Signatures
******************************


This module allows handling `Azure Shared Access Signatures <https://docs.microsoft.com/en-us/azure/storage/common/storage-dotnet-shared-access-signature-part-1>`_ from Zerynth programs.

    """

import urlparse
import base64
from crypto.hash import sha2 as sha2
from crypto.hash import hmac as hmac

def generate(uri, key, ttl, policy_name=None):
    """
.. function:: generate(uri, key, ttl, policy_name=None)

    Generate a SAS for target :samp:`uri` signed with :samp:`key` valid till :samp:`ttl` (passed as epoch) and with optional :samp:`policy_name`.

    """
    sign_key = urlparse.quote_plus(uri) + '\n' + str(int(ttl))
    hh = hmac.HMAC(base64.standard_b64decode(key), sha2.SHA2(hashtype=sha2.SHA256))
    hh.update(sign_key)
    signature = base64.standard_b64encode(hh.digest())

    rawtoken = {
        'sr' :  uri,
        'sig': signature,
        'se' : str(int(ttl))
    }
    if policy_name is not None:
        rawtoken['skn'] = policy_name

    return 'SharedAccessSignature ' + urlparse.urlencode(rawtoken)
