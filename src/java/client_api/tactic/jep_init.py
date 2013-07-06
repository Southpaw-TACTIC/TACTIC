###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


import tacticenv

try:
    import json
except:
    import simplejson as json

print "function: ", function
print "kwargs: ", kwargs, type(kwargs)
print "protocol: ", protocol

if protocol == 'local':
    from pyasm.security import Batch
    Batch()

from tactic_client_lib import TacticServerStub
server = TacticServerStub.get(protocol=protocol)

def delegate():
    global function
    global kwargs
    global ret_val
    kwargs = json.loads(kwargs)
    # remap to ensure that kwargs does not have unicode keywords
    kwargs2 = {}
    for name, value in kwargs.items():
        kwargs2[name.encode("UTF8")] = value

    method = eval('''server.%s''' % function)
    ret_val = method(**kwargs2)
    ret_val = json.dumps(ret_val)


