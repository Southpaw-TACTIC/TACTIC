###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


# import tactic.zip
import os, sys
#import inspect
#path = inspect.getfile( inspect.currentframe() )
path = __file__
path, file = os.path.split(path)
#path = path.replace("__init__.py", "")
path = '%s/tactic.zip' % path
if path not in sys.path:
    sys.path.insert(0, path)

from tactic_server_stub import *
from cgapp import *




