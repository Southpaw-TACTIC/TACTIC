###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['WebInit', 'SidebarTrigger', 'StatusLogTrigger', 'DisplayNameTrigger']

from pyasm.common import Common, Config, Environment
from pyasm.command import Trigger
from pyasm.search import SearchType, Search
from pyasm.biz import StatusLog

import os


class SidebarTrigger(Trigger):
    def execute(my):
        sobject = my.get_caller()
        search_type = sobject.get_base_search_type()
        
        all_logins = False
        if search_type == 'config/widget_config':
            category = sobject.get_value("category")
            if not category:
                category = sobject.get_value("search_type")

            if category != 'SideBarWdg':
                return
            user = sobject.get_value('login')
            user = user.strip()
            if not user:
                all_logins = True

        from pyasm.biz import Project
        project = Project.get()
        project_code = project.get_code()

        login = Environment.get_user_name()
        tmp_dir = "%s/cache/side_bar" % Environment.get_tmp_dir()
        project_check = True
        if search_type =='sthpw/login_group':   
            login_objs = sobject.get_logins()
            logins = [x.get_value('login') for x in login_objs]
            project_check = False
        else:
            if all_logins:
                expr = '@GET(sthpw/login.login)'
                logins = Search.eval(expr) 
            else:
                logins = [login]
        
        filenames = []
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
            return
        search = Search('sthpw/project')
        projects = search.get_sobjects()
        project_codes = [x.get_value('code') for x in projects]
        for login in logins:
            if project_check:
                filename = "%s__%s.html" % (project_code, login)
                filenames.append(filename)
            else:
                for project_code in project_codes:
                    filename = "%s__%s.html" % (project_code, login)
                    filenames.append(filename)



            #filenames = os.listdir(tmp_dir)
        for filename in filenames:
            #if not filename.startswith("%s__" % project_code):
            #    print "skip filename ", filename
            
            path = "%s/%s" % (tmp_dir, filename)
            if os.path.exists(path):
                print "Deleting: ", path
                os.unlink(path)

class StatusLogTrigger(Trigger):
    def execute(my):
        sobject = my.get_caller()
        prev_value = sobject.get_prev_value('status')

        value = sobject.get_value('status')
        if not value:
            return
        # record the change if it is different
        if prev_value != value:
            # if this is successful, the store it in the status_log
            StatusLog.create(sobject, value, prev_value)







class DisplayNameTrigger(Trigger):

    def execute(my):
        sobject = my.get_caller()
        first = sobject.get_value('first_name')
        last = sobject.get_value('last_name')
        display = sobject.get_value('display_name')

        if not display:
            if first and last:
                sobject.set_value('display_name', '%s %s'%(first, last))
            elif first:
                sobject.set_value("display_name", first)
            elif last:
                sobject.set_value("display_name", last)
            else:
                sobject.set_value("display_name", sobject.get_value("code"))


        # The admin user may not be committed yet
        if sobject.get_value("code") == 'admin':
            return

        sobject.commit(triggers=False)





class WebInit(Common):

    def execute(my):

        Trigger.clear_db_cache()

        event = "change|config/widget_config"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", "pyasm.web.web_init.SidebarTrigger")
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=True)

        event = "change|sthpw/schema"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", "pyasm.web.web_init.SidebarTrigger")
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=True)

        # when the palette column of the project changes
        event = "change|sthpw/project|palette"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", "pyasm.web.web_init.SidebarTrigger")
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=True)


        # when the palette column of the project changes
        event = "change|sthpw/pref_setting"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", "pyasm.web.web_init.SidebarTrigger")
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=True)




        
        event = "change|sthpw/login_in_group"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", "pyasm.web.web_init.SidebarTrigger")
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=True)


        event = "change|sthpw/login_group"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", "pyasm.web.web_init.SidebarTrigger")
        trigger.set_value("mode", "same process,same transaction")
        
        Trigger.append_static_trigger(trigger, startup=True)



        # FIXME: should this really be a web_init trigger?  This needs
        # to be run even from batch commands
        event = "change|sthpw/task|status"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", "pyasm.web.web_init.StatusLogTrigger")
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=True)



        # FIXME: should this be here??
        from pyasm.command.workflow import Workflow
        Workflow().init(startup=True)




        event = "insert|sthpw/login"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", "pyasm.web.web_init.DisplayNameTrigger")
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=True)



        #from tactic.command.queue import JobTask
        #JobTask.start()

        from pyasm.biz import Snapshot
        Snapshot.add_integral_trigger()










