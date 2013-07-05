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

print "function: ", function
print "kwargs: ", kwargs, type(kwargs)
print "protocol: ", protocol
print "server: ", server
kwargs = jsonloads(kwargs)

# convert the args to a dict
method = eval('''server.%s''' % function)
ret_val = method(**kwargs)
ret_val = jsondumps(ret_val)


