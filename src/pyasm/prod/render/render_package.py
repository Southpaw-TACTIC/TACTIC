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

__all__ = ['RenderPackage']

import os

from pyasm.common import *
from pyasm.prod.biz import FrameRange



class RenderPackage(Base):
    '''A package that is delivered to render submissions which contains
    all the information needed to render'''

    def __init__(my, policy=None):
        my.sobject = None
        my.snapshot = None
        my.policy = policy

        my.options = {}

        # by default, just render the first frame
        my.frame_range = FrameRange(1,1,1)


    def set_policy(my, policy):
        my.policy = policy

    def get_policy(my):
        return my.policy

    def set_sobject(my, sobject):
        '''set the sobject that is being rendered'''
        my.sobject = sobject

    def get_sobject(my):
        return my.sobject


    def set_snapshot(my, snapshot):
        '''set the snapshot that is being rendered'''
        my.snapshot = snapshot

    def get_snapshot(my):
        return my.snapshot


    def set_option(my, name, value):
        my.options[name] = str(value)

    def get_option(my, name, no_exception=False):
        value = my.options.get(name)
        if not no_exception and not value:
            raise TacticException("Mandatory option [%s] not found in render package" % name)

        return value
        
    def set_options(my, options):
        my.options = options

    def get_options(my):
        return my.options



    def set_frame_range(my, frame_range):
        my.frame_range = frame_range

        # if the policy sets a frame by, then use it
        frame_by = my.policy.get_value("frame_by")
        if frame_by:
            my.frame_range.set_frame_by(int(frame_by))
            

    def set_frame_range_values(my, start, end, by):
        frame_range = FrameRange(start, end, by)
        my.set_frame_range(frame_range)
            
    def get_frame_range(my):
        return my.frame_range






