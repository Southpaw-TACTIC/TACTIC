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

    def __init__(self, policy=None):
        self.sobject = None
        self.snapshot = None
        self.policy = policy

        self.options = {}

        # by default, just render the first frame
        self.frame_range = FrameRange(1,1,1)


    def set_policy(self, policy):
        self.policy = policy

    def get_policy(self):
        return self.policy

    def set_sobject(self, sobject):
        '''set the sobject that is being rendered'''
        self.sobject = sobject

    def get_sobject(self):
        return self.sobject


    def set_snapshot(self, snapshot):
        '''set the snapshot that is being rendered'''
        self.snapshot = snapshot

    def get_snapshot(self):
        return self.snapshot


    def set_option(self, name, value):
        self.options[name] = str(value)

    def get_option(self, name, no_exception=False):
        value = self.options.get(name)
        if not no_exception and not value:
            raise TacticException("Mandatory option [%s] not found in render package" % name)

        return value
        
    def set_options(self, options):
        self.options = options

    def get_options(self):
        return self.options



    def set_frame_range(self, frame_range):
        self.frame_range = frame_range

        # if the policy sets a frame by, then use it
        frame_by = self.policy.get_value("frame_by")
        if frame_by:
            self.frame_range.set_frame_by(int(frame_by))
            

    def set_frame_range_values(self, start, end, by):
        frame_range = FrameRange(start, end, by)
        self.set_frame_range(frame_range)
            
    def get_frame_range(self):
        return self.frame_range






