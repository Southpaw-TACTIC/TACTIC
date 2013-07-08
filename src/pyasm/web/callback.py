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

__all__ = ['Callback']


from pyasm.command import Command


class Callback(Command):
    '''command that is called by interface elements.  It is basically a command
    that is web aware and cannot be run by a script'''
    pass


