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

__all__ = ["PickupTrigger"]



from command import CommandException

from pyasm.common import *
from pyasm.biz import CommandSObj
from pyasm.security import *
from pyasm.search import SObject, Search
from trigger import *

class PickupTrigger(Trigger):
    ''' A trigger for setting the status of a pickup request 'closed' 
        when a Nat Pause is published under the pickup context'''

    def __init__(self):
        super(PickupTrigger, self).__init__()
        self.cmd_attrs = {}


    def get_title(self):
        return "PickupTrigger"

       
    def execute(self):
        # get command sobject and the notification code associated with it
        class_name = self.get_command().__class__.__name__
        cmd_sobj = CommandSObj.get_by_class_name(class_name)
        if not cmd_sobj:
            return
        self.notification_code = cmd_sobj.get_value('notification_code')


        # get the search objects operated on by the command and iterate
        # through them
        command = self.get_command()
        sobjects = command.get_sobjects()
        if not sobjects:
            msg = "Command '%s' has no sobjects.  Triggers cannot be called" % class_name
            Environment.add_warning("Command has no sobjects", msg)

        for sobject in sobjects:
            self.handle_sobject(sobject, command)



    def handle_sobject(self, sobject, command):
        search_type = sobject.get_search_type_obj().get_base_key()
        command = self.get_command()
        if command.get_info('context') == 'pickup':
            search = Search('flash/pickup_request')
            search.add_filter('episode_code', sobject.get_value('episode_code'))
            request = search.get_sobject()
            request.set_value('status','closed')
            request.commit()
            self.add_description('Changed pickup request status to [closed]')

    def handle_done(self):
        pass
        
        


   




        



