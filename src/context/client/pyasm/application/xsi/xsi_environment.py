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

all = ['XSIEnvironment']

import os

from pyasm.application.common import AppEnvironment


class XSIEnvironment(AppEnvironment):

    def set_up(info, application, toolkit):
        assert application
        assert info

        env = AppEnvironment.get()
    
        from xsi import XSI
        app = XSI(application, toolkit)
        info.app = app

        env.set_app(app)
        env.set_info(info)

    set_up = staticmethod(set_up)

    def get_save_dir(self):
        dir = self.app.get_project()
        dir = '%s/TacticTemp' % dir
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

