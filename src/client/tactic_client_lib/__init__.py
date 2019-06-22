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


# Python3 - This is not support ... not even sure if we need this anymore

import os, sys
if sys.version_info[0] < 3:
    path = __file__
    path, file = os.path.split(path)
    path = '%s/tactic.zip' % path
    if path not in sys.path:
        sys.path.insert(0, path)

from .tactic_server_stub import *
from .cgapp import *




