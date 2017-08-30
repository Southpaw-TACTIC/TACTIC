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
# Description: Triggers are called periodically in the code based on some event
# These are registered in the global container and listen for events.

__all__ = ["TriggerException", "Trigger", "SampleTrigger", "TimedTrigger", "SampleTimedTrigger"]

import sys, traceback

from pyasm.common import *
#from pyasm.biz import TriggerInCommand
from pyasm.search import ExceptionLog, SearchKey
from pyasm.security import Site

from command import Command, HandlerCmd

class TriggerException(Exception):
    pass


class Trigger(Command):

    KEY = "Trigger:triggers2"
    STATIC_TRIGGER_KEY = "Trigger:static_trigger"
    STATIC_TRIGGER_COUNT = "Trigger:static_trigger_count"
    INTEGRAL_TRIGGER_KEY = "Trigger:integral_trigger"
    NOTIFICATION_KEY = "Trigger:notifications"
    TRIGGER_EVENT_KEY = "triggers:cache"
    NOTIFICATION_EVENT_KEY = "notifications:cache"

    def __init__(my, **kwargs):
        my.caller = None
        my.message = None
        my.trigger_sobj = None
        my.input = {}
        my.output = {}
        my.description = ''
        my.kwargs = kwargs
        super(Trigger,my).__init__()

    def get_title(my):
        print "WARNING: Should override 'get_title' function for %s" % my
        return Common.get_full_class_name(my)


    def set_trigger_sobj(my, trigger_sobj):
        my.trigger_sobj = trigger_sobj

    def get_trigger_sobj(my):
        return my.trigger_sobj

    def get_trigger_data(my):
        data = my.trigger_sobj.get_value("data")
        if not data:
            return {}
        else:
            return jsonloads(data)


    def set_command(my, command):
        my.caller = command

    def set_message(my, message):
        my.message = message

    def get_message(my):
        return my.message

    def set_event(my, event):
        my.message = event

    def get_event(my):
        return my.message
    
    def get_command(my):
        return my.caller

    def set_caller(my, caller):
        my.caller = caller

    def get_caller(my):
        return my.caller

    def get_command_class(my):
        command_class = my.caller.__class__.__name__
        return command_class


    # set inputs and outputs
    def set_input(my, input):
        my.input = input
    
    def get_input(my):
        return my.input

    def set_output(my, output):
        my.output = output
    
    def get_output(my):
        return my.output

    def set_description(my, description):
        my.description = description
    def get_description(my):
        return my.description

    def execute(my):
        raise TriggerException("Must override execute function")


    # static functions

    # DEPRECATED
    def append_trigger(caller, trigger, event):
        '''append to the the list of called triggers'''
        #print "Trigger.append_trigger is DEPRECATED"
        trigger.set_caller(caller)
        trigger.set_event(event)
        triggers = Container.append_seq("Trigger:called_triggers",trigger)
    append_trigger = staticmethod(append_trigger)



    def call_all_triggers():
        '''calls all triggers for events that have occurred'''
        triggers = Container.get("Trigger:called_triggers")
        Container.remove("Trigger:called_triggers")
        if not triggers:
            return

        GlobalContainer.put("KillThreadCmd:allow", "false")
        try:
            
            prev_called_triggers = Container.get_seq("Trigger:prev_called_triggers")
            # run each trigger in a separate transaction
            for trigger in triggers:

                try:
                
                    # prevent recursive triggers shutting down the system
                    input = trigger.get_input()
                    input_json = jsondumps(input)

                    class_name = Common.get_full_class_name(trigger)

                    event = trigger.get_event()

                    if class_name == 'pyasm.command.subprocess_trigger.SubprocessTrigger':
                        class_name = trigger.get_class_name()

                    if (event, class_name, input_json) in prev_called_triggers:
                        # handle the emails, which can have multiple per event
                        if class_name in [
                            "pyasm.command.email_trigger.EmailTrigger",
                            "pyasm.command.email_trigger.EmailTrigger2"
                        ]:
                            pass
                        else:
                            #print("Recursive trigger (event: %s,  class: %s)" % (event, class_name))
                            continue

                    # store previous called triggers
                    prev_called_triggers.append( (event, class_name, input_json) )

                    # set call_trigger to false to prevent infinite loops
                    if not issubclass(trigger.__class__, Trigger):
                        # if this is not a trigger, then wrap in a command
                        handler_cmd = HandlerCmd(trigger)
                        handler_cmd.add_description(trigger.get_description())
                        trigger = handler_cmd


                    # triggers need to run in their own transaction when
                    # they get here.
                    Trigger.execute_cmd(trigger, call_trigger=False)

                except Exception, e:
                    # if there is an error in calling this trigger for some
                    # reason, carry on with the other triggers
                    # print the stacktrace
                    tb = sys.exc_info()[2]
                    stacktrace = traceback.format_tb(tb)
                    stacktrace_str = "".join(stacktrace)
                    print "-"*50
                    print stacktrace_str
                    print str(e)
                    print "-"*50
                    continue

        finally:
            GlobalContainer.remove("KillThreadCmd:allow")

    call_all_triggers = staticmethod(call_all_triggers)



    def _get_triggers(cls, call_event, integral_only=False, project_code=None):

        if integral_only:
            trigger_key = "%s:integral" % cls.TRIGGER_EVENT_KEY
        else:
            trigger_key = cls.TRIGGER_EVENT_KEY

        notification_key = cls.NOTIFICATION_EVENT_KEY 
        trigger_dict = Container.get(trigger_key)
        notification_dict = Container.get(notification_key)
      
        call_event_key = jsondumps(call_event)

        # NOTE: get_db_triggers only get triggers for this project ...
        # need to update so that triggers from other projects
        # are also executed

        # static triggers could grow when more sTypes are searched
        last_static_count = Container.get(cls.STATIC_TRIGGER_COUNT)
        static_trigger_sobjs = cls.get_static_triggers()
        current_static_count = len(static_trigger_sobjs)
        renew = last_static_count != current_static_count and not integral_only

        if trigger_dict == None or renew:
            # assign keys to each trigger
            trigger_dict = {}
            Container.put(trigger_key, trigger_dict)
            
            if integral_only:
                # just get all the integral triggers
                trigger_sobjs = cls.get_integral_triggers()
            else:

                # build a list of site and db of the triggers for current
                # project
                trigger_sobjs = cls.get_db_triggers()

                # append all static triggers
                if static_trigger_sobjs:
                    Container.put(cls.STATIC_TRIGGER_COUNT, current_static_count)
                    trigger_sobjs.extend(static_trigger_sobjs)
                
            
                # append all integral triggers
                integral_trigger_sobjs = cls.get_integral_triggers()
                if integral_trigger_sobjs:
                    trigger_sobjs.extend(integral_trigger_sobjs)


                # append all notifications
                
                #notification_sobjs = cls.get_notifications_by_event()
                #trigger_sobjs.extend(notification_sobjs)


            for trigger_sobj in trigger_sobjs:
                trigger_event = trigger_sobj.get_value("event")

                # The value in the process column can also be the process_code.
                trigger_process = trigger_sobj.get_value("process")
                trigger_stype = trigger_sobj.get_value("search_type", no_exception=True)

                listen_event = {}
                listen_event['event'] = trigger_event
                if trigger_process:
                    listen_event['process'] = trigger_process
                if trigger_stype:
                    listen_event['search_type'] = trigger_stype

                listen_key = jsondumps(listen_event)

                trigger_list = trigger_dict.get(listen_key)
                if trigger_list == None:
                    trigger_list = []
                    trigger_dict[listen_key] = trigger_list

                trigger_list.append(trigger_sobj)

        called_triggers = trigger_dict.get(call_event_key)


        # assign keys to each notification
        if notification_dict == None:
            notification_dict = {}
            Container.put(notification_key, notification_dict)

            # append all notifications without going thru all the logics with project_code
            notification_sobjs = cls.get_notifications_by_event()
            
            for trigger_sobj in notification_sobjs:
                trigger_event = trigger_sobj.get_value("event")
                trigger_process = trigger_sobj.get_value("process")
                trigger_stype = trigger_sobj.get_value("search_type", no_exception=True)
                trigger_project = trigger_sobj.get_value("project_code", no_exception=True)

                listen_event = {}
                listen_event['event'] = trigger_event
                if trigger_process:
                    listen_event['process'] = trigger_process
                if trigger_stype:
                    listen_event['search_type'] = trigger_stype
                # notification specific
                if trigger_project:
                    listen_event['project_code'] = trigger_project

                listen_key = jsondumps(listen_event)

                notification_list = notification_dict.get(listen_key)
                if notification_list == None:
                    notification_list = []
                    notification_dict[listen_key] = notification_list

                notification_list.append(trigger_sobj)
       
       
       
        # we have to call with and without project_code to cover both cases
        key2 = call_event.copy()
       
        if not project_code:
            from pyasm.biz import Project
            project_code = Project.get_project_code()

        key2['project_code'] =  project_code
      
        
        


        call_event_key2 = jsondumps(key2)
        matched_notifications = []
        for call_event_key in [call_event_key, call_event_key2]:
            matched = notification_dict.get(call_event_key)
            if matched:
                matched_notifications.extend(matched)

      
      


        combined_triggers = []
        if called_triggers:
            combined_triggers.extend(called_triggers)
        if matched_notifications:
            combined_triggers.extend(matched_notifications)
        
        
        return combined_triggers

    _get_triggers = classmethod(_get_triggers)


    def clear_db_cache(cls):
        Container.put(cls.KEY, None)

        site = Site.get_site()

        from pyasm.biz import Project
        project_code = Project.get_project_code()
        key = "%s:%s:%s" % (cls.KEY, project_code, site)
        Container.put(key, None)
    clear_db_cache = classmethod(clear_db_cache)

    def get_db_triggers(cls):

        site_triggers = Container.get(cls.KEY)
        if site_triggers == None:
            # find all of the triggers
            search = Search("sthpw/trigger")
            search.add_project_filter()
            site_triggers = search.get_sobjects()
            Container.put(cls.KEY, site_triggers)

        # find all of the project triggers
        from pyasm.biz import Project
        site = Site.get_site()
        project_code = Project.get_project_code()
        key = "%s:%s:%s" % (cls.KEY, project_code, site)
        project_triggers = Container.get(key)
        if project_triggers == None:
            if project_code not in ['admin','sthpw']:
                try:
                    search = Search("config/trigger")
                    project_triggers = search.get_sobjects()
                except SearchException, e:
                    print "WARNING: ", e
                    project_triggers = []
            else:
                project_triggers = []
            Container.put(key, project_triggers)

        triggers = []
        triggers.extend(site_triggers)
        triggers.extend(project_triggers)
        return triggers

    get_db_triggers = classmethod(get_db_triggers)


    def call_by_key(cls, key, caller, output={}, forced_mode='', integral_only=False, project_code=None):
        event = key.get("event")
        #call_event_key = jsondumps(key)
        triggers_sobjs = cls._get_triggers(key, integral_only, project_code=project_code)
        if not triggers_sobjs:
            return
        
        return cls._handle_trigger_sobjs(triggers_sobjs, caller, event, output, forced_mode=forced_mode, project_code=project_code)
    call_by_key = classmethod(call_by_key)



    def call(cls, caller, event, output={}, process=None, search_type=None, project_code=None, forced_mode=''):
        '''message is part of a function name and so should
        not contain spaces '''
        # build the call event key
        call_event = {}
        call_event['event'] = event
        if process:
            call_event['process'] = process
        if search_type:
            call_event['search_type'] = search_type

        #call_event_key = jsondumps(call_event)
        triggers_sobjs = cls._get_triggers(call_event, project_code=project_code)

        if not triggers_sobjs:
            return []

        return cls._handle_trigger_sobjs(triggers_sobjs, caller, event, output, forced_mode=forced_mode, project_code=project_code)

    call = classmethod(call)


    def _handle_trigger_sobjs(cls, triggers_sobjs, caller, event, output, forced_mode='', project_code=None):

        triggers = []

        # go through each trigger and build the trigger sobject
        for trigger_sobj in triggers_sobjs:

            mode = trigger_sobj.get_value("mode", no_exception=True)
            if not mode:
                mode = 'same process,new transaction'
            
            if trigger_sobj.get_base_search_type() == "sthpw/notification":
                if forced_mode:
                    trigger_class = "pyasm.command.EmailTriggerTest"
                else:
                    trigger_class = "pyasm.command.EmailTrigger2"
            else:
                trigger_class = trigger_sobj.get_value("class_name")

            try:
                if trigger_class in ['pyasm.command.EmailTrigger2', 'pyasm.command.EmailTriggerTest']:
                    # allow the trigger handler to know the calling sobj
                    trigger = Common.create_from_class_path(trigger_class)
                    trigger.set_trigger_sobj(trigger_sobj)   
                    if not forced_mode:
                        mode = 'separate process,non-blocking'
                    else:
                        mode = forced_mode

                elif mode in ['same process,same transaction',
                            'same process,new transaction']:
                    script_path = trigger_sobj.get_value("script_path")
                    if trigger_class == '':
                        from tactic.command.python_cmd import PythonTrigger
                        trigger = PythonTrigger()
                        trigger.set_script_path(script_path)
                    elif not isinstance(trigger_class,basestring):
                        trigger = trigger_class()
                    else:
                        trigger = Common.create_from_class_path(trigger_class)

                else:
                    if trigger_class == '':
                        script_path = trigger_sobj.get_value("script_path")

                        trigger_class = "tactic.command.PythonTrigger"
                        kwargs = {
                            "script_path": script_path
                        }
                    else:
                        kwargs = {}

                    from subprocess_trigger import SubprocessTrigger
                    trigger = SubprocessTrigger()
                    trigger.set_mode(mode)
                    if not project_code:
                        from pyasm.biz import Project
                        project_code = Project.get_project_code()
                    data = {
                        "project": project_code,
                        "ticket": Environment.get_ticket(),
                        "class_name": trigger_class,
                        "kwargs": kwargs
                    }
                    trigger.set_data(data)

                trigger.set_event(event)

                if isinstance(trigger, Trigger):
                    trigger.set_trigger_sobj(trigger_sobj)

                triggers.append(trigger)

            except ImportError, e:
                Environment.add_warning("Trigger Not Defined", "Trigger [%s] does not exist" % trigger_class)

                #log = ExceptionLog.log(e)

                # print the stacktrace
                tb = sys.exc_info()[2]
                stacktrace = traceback.format_tb(tb)
                stacktrace_str = "".join(stacktrace)
                print "-"*50
                print stacktrace_str
                print str(e)
                print "-"*50
                raise

            if issubclass( trigger.__class__, Trigger):
                trigger.set_caller(caller)
                trigger.set_message(event)

            # if it is a subclass of client api handler

            # create a package
            # transfer outputs to inputs.  This allows a command to deliver
            # from one process to another
            if output or output == {}:
                input = output.copy()
            else:
                input = caller.get_info()

            trigger.set_input(input)
            # By default, inputs travel through
            trigger.set_output(input)
            # set the description properly for transaction_log
            trigger.set_description(trigger_sobj.get_value('description'))

            # if delayed, then register it to be executed later
            if mode != 'same process,same transaction':
                Container.append_seq("Trigger:called_triggers",trigger)
                continue

            # otherwise call the trigger immediately
            try:
                trigger.execute()
            except Exception, e:
                #log = ExceptionLog.log(e)

                # print the stacktrace
                tb = sys.exc_info()[2]
                stacktrace = traceback.format_tb(tb)
                stacktrace_str = "".join(stacktrace)
                print "-"*50
                print stacktrace_str
                print str(e)
                print "-"*50

                caller.errors.append("Trigger [%s] failed: %s" \
                    %(trigger.get_title(), str(e)))

                raise
           

        return triggers

    _handle_trigger_sobjs = classmethod(_handle_trigger_sobjs)



    def get_by_event(cls, event, process=None):
        '''get a list of triggers by event'''
        
        site_triggers = Container.get(cls.KEY)
        if site_triggers == None:
            # find all of the triggers
            search = Search("sthpw/trigger")
            search.add_project_filter()
            site_triggers = search.get_sobjects()

            Container.put(cls.KEY, site_triggers)

        # find all of the project triggers
        from pyasm.biz import Project
        project_code = Project.get_project_code()
        key = "%s:%s" % (cls.KEY, project_code)
        project_triggers = Container.get(key)
        if project_triggers == None:
            if project_code not in ['admin','sthpw']:
                search = Search("config/trigger")
                project_triggers = search.get_sobjects()
            else:
                project_triggers = []
            Container.put(key, project_triggers)


        triggers = []
        triggers.extend(site_triggers)
        triggers.extend(project_triggers)

        #for trigger in triggers:
        #    print trigger.get_search_key()

        search_type = None

        event_triggers = []
        for trigger in triggers:

            # determin trigger process
            trigger_process = trigger.get_value("listen_process", no_exception=True)
            if not trigger_process:
                trigger_process = trigger.get_value("process", no_exception=True)

            # determine if the process matches the trigger process
            if trigger_process and not process:
                continue
            if process and not trigger_process:
                continue
            if trigger_process and process and trigger_process != process:
                continue


            # determine the search_type
            trigger_stype = trigger.get_value("search_type", no_exception=True)
            if trigger_stype and not search_type:
                continue
            if search_type and not trigger_stype:
                continue
            if trigger_stype and search_type and trigger_stype != search_type:
                continue


            #print event, trigger_process, process,trigger.get_id()

            if trigger.get_value("event") == event:
                event_triggers.append(trigger)

        return event_triggers
    get_by_event = classmethod(get_by_event)



    def get_notifications_by_event(cls, event=None, process=None):
         
        triggers = Container.get(cls.NOTIFICATION_KEY)
        if triggers == None:
            # find all of the triggers
            search = Search("sthpw/notification")
            triggers = search.get_sobjects()
            Container.put(cls.NOTIFICATION_KEY, triggers)

        if event == None:
            return triggers


        from pyasm.biz import Project
        project_code = Project.get_project_code()

        event_triggers = []
        for trigger in triggers:
            trigger_process = trigger.get_value("process")

            # if a process is asked for, then the trigger must have a process
            if process and not trigger_process:
                continue

            # if the trigger has a process, then a process must be asked for
            if trigger_process and not process:
                continue

            # the trigger and trigger process must match
            if process and trigger_process and trigger_process != process:
                continue


            # the project must match
            trigger_project = trigger.get_value("project_code")
            if trigger_project and trigger_project != project_code:
                continue


            if trigger.get_value("event", no_exception=True) == event:
                event_triggers.append(trigger)
        
        return event_triggers
    get_notifications_by_event = classmethod(get_notifications_by_event)



    STATIC_TRIGGERS = []

    def append_static_trigger(cls, trigger, startup=False):
        triggers = Container.get(cls.STATIC_TRIGGER_KEY)
        if triggers == None:
            triggers = []
            Container.put(cls.STATIC_TRIGGER_KEY, triggers)
        triggers.append(trigger)
        # only the startup ones can go to the class variable which stays active before the process exists
        if startup:
            cls.STATIC_TRIGGERS.append(trigger)
    append_static_trigger = classmethod(append_static_trigger)


    def get_static_triggers(cls):
        triggers = Container.get(cls.STATIC_TRIGGER_KEY)
        if triggers == None:
            triggers = []
            Container.put(cls.STATIC_TRIGGER_KEY, triggers)

        # these are all added at start up time
        startup_triggers = cls.STATIC_TRIGGERS

        tmp_triggers = triggers[:]
        tmp_triggers.extend(startup_triggers)
        return tmp_triggers

    get_static_triggers = classmethod(get_static_triggers)


    # NOTE: is this even used?
    def get_static_triggers_by_event(cls, event, process=None):
        triggers = cls.get_static_triggers() 

        event_triggers = []

        for trigger in triggers:
            trigger_process = trigger.get_value("listen_process", no_exception=True)
            if not trigger_process:
                trigger_process = trigger.get_value("process", no_exception=True)
            if trigger_process and not process:
                continue

            if process and not trigger_process:
                continue

            if trigger_process and process and trigger_process != process:
                continue


            if trigger.get_value("event") == event:
                event_triggers.append(trigger)
        return event_triggers
    get_static_triggers_by_event = classmethod(get_static_triggers_by_event)




    # integral triggers: these triggers cannot be shut off because they are
    # integral to the proper functioning of TACTIC

    INTEGRAL_TRIGGERS = []

    def append_integral_trigger(cls, trigger, startup=False):
        triggers = Container.get(cls.INTEGRAL_TRIGGER_KEY)
        if triggers == None:
            triggers = []
            Container.put(cls.INTEGRAL_TRIGGER_KEY, triggers)

        # startup triggersl go to the class variable which stays
        # active through many requests
        if startup:
            cls.INTEGRAL_TRIGGERS.append(trigger)
        else:
            triggers.append(trigger)
    append_integral_trigger = classmethod(append_integral_trigger)



    def get_integral_triggers(cls):
        triggers = Container.get(cls.INTEGRAL_TRIGGER_KEY)
        if triggers == None:
            triggers = []
            Container.put(cls.INTEGRAL_TRIGGER_KEY, triggers)

        # these are all added at start up time
        startup_triggers = cls.INTEGRAL_TRIGGERS

        # make a copy of the array
        tmp_triggers = triggers[:]
        tmp_triggers.extend(startup_triggers)
        return tmp_triggers

    get_integral_triggers = classmethod(get_integral_triggers)




#
# Snapshot is latest trigger
#
__all__.append('SnapshotIsLatestTrigger')
class SnapshotIsLatestTrigger(Trigger):

    # Since this trigger is run even on undo and is outside of the transaction
    # is should not be in the transaction log.  It is an inherent property
    # of the check-in
    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)


    def execute(my):
        input = my.get_input()
        mode = input.get("mode")
        # NOTE: this could be run during update and insert of snapshot
        # during insert, for simple snapshot creation like server.create_snaphot()
        # during update, is_latest, is_current and update_versionless are handled together for check-in

        if mode in ['delete','retire']:
            sobject_dict = input.get("sobject")
            context = sobject_dict.get("context")
            search_type = sobject_dict.get("search_type")
            search_code = sobject_dict.get("search_code")
            search_id = sobject_dict.get("search_id")

            search = Search("sthpw/snapshot")
            search.add_filter("context", context)
            search.add_order_by("timestamp desc")

            search.add_filter("search_type", search_type)
            if search_code:
                search.add_filter("search_code", search_code)
            else:
                search.add_filter("search_id", search_id)

            snapshots = search.get_sobjects()
            for i, snapshot in enumerate(snapshots):
                if i == 0:
                    if snapshot.get_value("is_latest") == False:
                        snapshot.set_value("is_latest", True)
                        snapshot.update_versionless("latest")
                        snapshot.commit()
                else:
                    if snapshot.get_value("is_latest") == True:
                        snapshot.set_value("is_latest", False)
                        snapshot.commit()

                # NOTE: not sure what to do with is_current when the
                # current snapshot is deleted

            return
        
        

        sobject_dict = input.get("sobject_dict")
        search_key = input.get("search_key")
        snapshot = Search.get_by_search_key(search_key)
        

        #print "mode: ", mode
        #print "snapshot: ", snapshot.get("version"), snapshot.get("context")
        #print "data: ", input.get("update_data").keys()
        #print


        # if the current snapshot is already the latest, don't do anything
        update_data = input.get("update_data")
        update_versionless = mode == 'update'

        if update_data.get("is_latest") == True:
            snapshot.set_latest(commit=True, update_versionless=update_versionless)


        if update_data.get("is_current") == True:
            snapshot.set_current(commit=True, update_versionless=update_versionless)





__all__.append('SearchTypeCacheTrigger')
from tactic_client_lib.interpreter import Handler
class SearchTypeCacheTrigger(Handler):

    def execute(my):
        from pyasm.biz import CacheContainer
        print "running cache trigger"
        search_type = my.input.get("search_type")
        assert search_type
        cache = CacheContainer.get(search_type)
        cache.make_dirty()





class SampleTrigger(Trigger):
    def execute(my):
        # filter this to the specific command
        command_class = my.get_command_class()
        if command_class != "SimpleStatusCmd":
            return

        print "Executing sample trigger"

    


import time

class TimedTrigger(Base):

    def __init__(my):
        # start the clock on creation time
        my.start_interval = time.time()
        my.interval = 0
        my.is_executing = False


    def get_execute_interval(my):
        '''return number of seconds between execution'''
        return 

    def get_execute_time(my):
        '''return time of day this needs to be executed'''
        return


    def get_time(my):
        '''return time when this should be executed'''
        pass

    def is_in_separate_thread(my):
        '''determines whether this trigger should be run in an independent
        separate thread'''
        return False


    def is_ready(my):

        if my.is_executing:
            return False

        execute_interval = my.get_execute_interval()

        current = time.time()
        my.interval = current - my.start_interval

        # check if the execute interval is exceeded
        if execute_interval and my.interval >= execute_interval:
            return True

        # check time of day
        execute_time = my.get_execute_time()
        if execute_time:
            execute_hour, execute_minute = execute_time.split(":")

            date = Date()
            current_time = date.get_time()
            current_hour, current_minute, current_second = current_time.split(":")

            if current_hour == execute_hour:
                if execute_minute == current_minute:
                    print "time of day!!!"
                    return True

        return False



    def _do_execute(my):
        current = time.time()
        my.is_executing = True
        my.execute()
        my.is_executing = False
        my.start_interval = current
       

    def execute(my):
        raise TriggerException("Must override execute function")



class SampleTimedTrigger(TimedTrigger):

    def get_execute_interval(my):
        '''return number of seconds between execution'''
        return 3600

    def execute(my):
        print "doing a bunch of stuff"
        print "sleeping"
        time.sleep(15)
        print ".... done"

        

__all__.extend( ['BurnDownTimedTrigger', 'BurnDownEmailHandler'] )

from pyasm.search import Search, SObject, SearchException
from email_handler import EmailHandler


class BurnDownTimedTrigger(TimedTrigger):

    def __init__(my):
        my.notified = {}
        my.keyed = {}
        super(BurnDownTimedTrigger, my).__init__()

    def get_execute_interval(my):
        '''return number of seconds between execution'''
        return 5
        #pass

    def get_execute_time(my):
        #return "00:20"
        pass

    def is_in_separate_thread(my):
        return False


    def execute(my):
        date = Date()
        cur_time = date.get_utc()

        print "Burn down"

        #first = 8 * 60 * 60
        first = 30
        next = 10
       
        # search for all of the tasks that are pending
        search = Search("sthpw/task")
        search.add_filter("status", "Pending")
        sobjects = search.get_sobjects()

        # get the time when this was set to pending
        search = Search("sthpw/status_log")
        search.add_filter("from_status", "Assignment")
        search.add_filter("to_status", "Pending")
        logs = search.get_sobjects()

        logs_dict = SObject.get_dict(logs, ["search_type", "search_id"] )

        # analyze tasks
        ready_sobjects = []

        for sobject in sobjects:
            search_key = sobject.get_search_key()

            
            # get the logs
            log = logs_dict.get(search_key)
            if not log:
                continue

            log_date = Date(db=log.get_value("timestamp"))
            log_time = log_date.get_utc()

            interval = cur_time - log_time


            # if we haven't passed the first marker, then just skip
            if interval < first:
                continue

            # put an upper limit where it doesn't make anymore sense
            if interval > 21*24*60*60:
                continue


            # once we've reached the first marker, email next interval
            start = (interval - first) / next
            print "start: ", interval, first, start

            continue

            parent = sobject.get_parent()
            if not parent:
                print "WARNING: parent does not exist [%s]" % sobject.get_search_key()
                continue

            process = sobject.get_value("process")
            assigned = sobject.get_value("assigned")
            status = sobject.get_value("status")
            code = parent.get_code()

            print (code, assigned, process, status, interval/3600)
            ready_sobjects.append( sobject )





        # TODO: problem how to prevent emails from happening every iteration?

        # this is run every minute, so remember the last time an email has been
        # sent for a particular 
 
        if not ready_sobjects:
            return

        from pyasm.command import Command
        class BurnDownCmd(Command):
            def get_title(my):
                return "Burn Down Command"
            def set_sobjects(my, sobjects):
                my.sobjects = [sobject]
            def execute(my):
                # call email trigger
                from email_trigger import EmailTrigger
                email_trigger = EmailTrigger()
                email_trigger.set_command(my)
                email_trigger.execute()


        # call email trigger
        #cmd = BurnDownCmd()
        #cmd.set_sobjects(ready_sobjects)
        #Command.execute_cmd(cmd)

        # remember the time of each email
        for sobject in ready_sobjects:
            search_key = sobject.get_search_key()
            my.notified[search_key] = cur_time
            



    
class BurnDownEmailHandler(EmailHandler):

    def get_subject(my):
        parent = my.sobject.get_parent()
        search_type_obj = parent.get_search_type_obj()
        title = search_type_obj.get_title()

        process = my.sobject.get_value("process")
        assigned = my.sobject.get_value("assigned")

        return "Task In Progress: %s, %s, %s, %s" % (title, parent.get_code(), process, assigned )






