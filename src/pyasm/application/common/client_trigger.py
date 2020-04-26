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

__all__ = ['ClientTrigger']

import sys, types

from app_environment import AppEnvironment


class ClientTrigger(object):
    '''Simple implementation of a trigger allowing for custom actions to
    occur on the client side'''
    def __init__(self):
        self.event = ""

    def set_event(self, event):
        self.event = event

    def execute(self):
        pass


    # static functions


    def register(event, trigger):
        trigger_list = ClientTrigger.get(event)
        trigger_list.append(trigger)
    register = staticmethod(register)


    def call(event):
        trigger_list = ClientTrigger.get(event)
        for trigger in trigger_list:
            trigger.set_event(event)
            trigger.execute()
    call = staticmethod(call)


    triggers = {}

    def get(event):
        trigger_list = ClientTrigger.triggers.get(event)
        if not trigger_list:
            trigger_list = []
            ClientTrigger.triggers[event] = trigger_list
        return trigger_list
    get = staticmethod(get)





class TestCheckinTrigger(ClientTrigger):
    '''sample trigger'''
    def execute(self):
        # get the maya session
        env = AppEnvironment.get()
        app = env.get_app()

        # do some checks
        print "event: ", self.event


# register the trigger to just before asset is exported
ClientTrigger.register("pre_asset_export", TestCheckinTrigger() )

