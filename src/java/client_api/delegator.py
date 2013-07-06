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
from pyasm.common import jsonloads, jsondumps
from tactic_client_lib import TacticServerStub
from pyasm.biz import Project

# The variables "function" and "kwargs" are autofilled by Jepp
print "function: ", function
print "kwargs: ", kwargs
kwargs_dict = jsonloads(kwargs)
# remap keys so that they are strings
kwargs = {}
for key,value in kwargs_dict.items():
    kwargs[key.encode('utf-8')] = value


#server = TacticServerStub.get(protocol='xmlrpc')
server = TacticServerStub.get()

# convert the args to a dict
method = eval('''server.%s''' % function)
ret_val = method(**kwargs)
ret_val = jsondumps(ret_val)


