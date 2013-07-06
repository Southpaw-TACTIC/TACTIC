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


__all__ = ['Application', 'AppException']

import sys, types


class AppException(Exception):
    '''Used by different applications for raising exceptions'''
    pass




class Application(object):
    '''base class defining interface for 3D applications'''
    app = None

    def get(cls):
        if not cls.app:
            from tactic_client_lib.application.maya import Maya
            cls.app = Maya()

        return cls.app
    get = classmethod(get)



