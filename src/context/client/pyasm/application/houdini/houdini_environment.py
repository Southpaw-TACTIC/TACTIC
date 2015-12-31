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

all = ['HoudiniEnvironment']

import os

from pyasm.application.common import AppEnvironment


class HoudiniEnvironment(AppEnvironment):


    def set_up(info):

        env = AppEnvironment.get()

        from houdini import Houdini

        app = Houdini()

        info.app = app
        env.set_app(app)

        env.set_info(info)

    set_up = staticmethod(set_up)
