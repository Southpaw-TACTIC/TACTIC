############################################################
#
#    Copyright (c) 2005, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

import os

os.environ['PYCHECKER'] = '--self=self --stdlib --no-shadowbuiltin --blacklist=Ft,expat' 
import pychecker.checker


import tacticenv


from pyasm.common import *
#from pyasm.security import *
#from pyasm.widget import *

#if __name__ == '__main__':
#    Batch(login_code="remko")

