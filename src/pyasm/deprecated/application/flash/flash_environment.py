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

__all__ = ['FlashEnvironment']

import os

from flash import *
from pyasm.application.common import AppEnvironment


class FlashEnvironment(AppEnvironment):
    '''Sets up the flash environment.  Because all of the flash code can be
    run on both the server and the client, this package must be independent
    of all other Tactic software.  This class allows the poplulation of
    the necessary information for the proper functions of these classes
    in this package'''

    def set_up(info):

        env = AppEnvironment.get()

        from flash import Flash

        app = Flash()

        info.app = app
        env.set_app(app)

        env.set_info(info)

    set_up = staticmethod(set_up)


