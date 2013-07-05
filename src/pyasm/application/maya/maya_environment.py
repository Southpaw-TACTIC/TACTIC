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

__all__ = ['MayaEnvironment']


import os

from pyasm.application.common import AppEnvironment


class MayaEnvironment(AppEnvironment):
    '''Sets up the maya environment.  Because all of the maya code can be
    run on both the server and the client, this package must be independent
    of all other Tactic software.  This class allows the poplulation of
    the necessary information for the proper functions of these classes
    in this package'''


    def set_up(info):
        # set up application environment, by getting information from the info
        # object.  This info object, contains data retrieved from some
        # external source

        # get the environment and application
        env = AppEnvironment.get()

        from maya_app import Maya, Maya85

        # detect if this is Maya 8.5 or later
        app = None
        try:
            import maya
            app = Maya85()
        except ImportError:
            from pyasm.application.maya import Maya
            app = Maya()

        info.app = app
        env.set_app(app)


        env.set_info(info)

        # DEPRECATED: info object shouldn't know anything about 
        # populate the info object with this information
        info.env = env


    set_up = staticmethod(set_up)





