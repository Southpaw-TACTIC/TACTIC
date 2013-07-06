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

__all__ = ["StatusTrigger"]




from pyasm.common import *
from pyasm.biz import CommandSObj, Task
from pyasm.security import *
from pyasm.search import SObject, Search
from trigger import *

class StatusTrigger(Trigger):
    ''' A trigger for changing the compositing task status to Pending when
        the rendering task status is set to Review'''

    def __init__(my):
        super(StatusTrigger, my).__init__()
        my.cmd_attrs = {}


    def get_title(my):
        return "StatusTrigger"

    def check(my, sobject):
        # this is needed since this command is used on other search types as well
        if not isinstance(sobject, Task):
            return False
        if sobject.get_value('status') == 'Review' and sobject.get_process()=='rendering':
            return True
        else:
            return False
       
    def execute(my):
        # get command sobject and the notification code associated with it
        class_name = my.get_command().__class__.__name__
        cmd_sobj = CommandSObj.get_by_class_name(class_name)
        if class_name != 'SimpleStatusCmd':
            return
        if not cmd_sobj:
            return

        # get the search objects operated on by the command and iterate
        # through them
        command = my.get_command()
        sobjects = command.get_sobjects()
        if not sobjects:
            msg = "Command '%s' has no sobjects.  Triggers cannot be called" % class_name
            Environment.add_warning("Command has no sobjects", msg)

        for sobject in sobjects:
            my.handle_sobject(sobject, command)



    def handle_sobject(my, sobject, command):
        # the sobject here is a task
        if not my.check(sobject):
            return
       
        # the parent is the asset or shot
        parent = sobject.get_parent()
       
        print "Check finished"
        tasks = Task.get_by_sobject(parent, 'compositing')
        # about to commit
        task_ids = []
        for task in tasks:
            if task.get_value('status') != 'Pending':
                task.set_value('status','Pending')
                task.commit()
                task_ids.append(task.get_id())
        print "Changed task status to [Pending] for task id %s'" %str(task_ids)

    def handle_done(my):
        pass
        
        


   




        



