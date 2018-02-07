############################################################
#
#    Copyright (c) 2008, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

__all__ = ['SubprocessTrigger', 'QueueTrigger', 'ScriptTrigger']

import tacticenv

import sys
import subprocess
from subprocess import Popen

from pyasm.common import Config, Common, jsonloads, jsondumps
from pyasm.security import Site
from tactic_client_lib import TacticServerStub
from tactic_client_lib.interpreter import Handler

from trigger import Trigger
from command import Command




class SubprocessTrigger(Handler):
    '''Utility class that calls a trigger by external process'''
    def __init__(self):
        self.mode = "same process,new transaction"
        self.info = {}
        super(SubprocessTrigger,self).__init__()

    def set_data(self, data):
        self.data = data
        self.class_name = data.get("class_name")

        # Since the trigger will run separate somewhere else, we do not
        # know if the the workflow should stop of not.  The trigger
        # can define a result in the data
        kwargs = data.get("kwargs")
        if kwargs and kwargs.get("result"):
            self.info['result'] = kwargs.get("result")




    def get_info(self):
        return self.info


    def get_class_name(self):
        return self.class_name

    def set_mode(self, mode):
        self.mode = mode

    def execute(self):
      
        input_data = self.get_input_data()
        data = self.data


        # add site info to the data object
        site = Site.get_site()
        if site and not data.get("site"):
            data['site'] = site

        result = True


        # input data for the handler
        if self.mode == 'separate process,blocking':
            input_data_str = jsondumps(input_data)
            data_str = jsondumps(data)

            file = __file__
            py_exec = Config.get_value("services", "python")
            if not py_exec:
                py_exec = "python"


            retcode = subprocess.call([py_exec, file, data_str, input_data_str])



        elif self.mode == 'separate process,non-blocking':
            input_data_str = jsondumps(input_data)
            data_str = jsondumps(data)

            file = __file__
            py_exec = Config.get_value("services", "python")
            if not py_exec:
                py_exec = "python"

            retcode = subprocess.Popen([py_exec, file, data_str, input_data_str])

            result = "wait"

        elif self.mode == 'separate process,queued':

            kwargs = data.get("kwargs")
            priority = kwargs.get("priority") or 99999
            description = kwargs.get("description") or "Trigger"
            queue_type = kwargs.get("trigger") or "trigger"

            class_name = "pyasm.command.QueueTrigger"
            kwargs = {
                'input_data': input_data,
                'data': data,
            }

            from tactic.command import Queue
            queue_item = Queue.add(class_name, kwargs, queue_type=queue_type, priority=priority, description=description)

            result = "wait"


        elif self.mode == 'same process,new transaction':
            # run it inline
            trigger = ScriptTrigger()
            trigger.set_data(data)
            trigger.set_input(input_data)
            trigger.execute()


        # if it was not overridden by the trigger, the return default for the mode
        if not self.info.has_key("result"):
            self.info['result'] = result


 
class QueueTrigger(Command):
    '''Simple command which is executed from a queue'''
    def execute(self):
        # start workflow engine
        from pyasm.command import Workflow
        Workflow().init()

        input_data = self.kwargs.get("input_data")
        data = self.kwargs.get("data")

        trigger = ScriptTrigger()
        trigger.set_input(input_data)
        trigger.set_data(data)

        trigger.execute()

        info = trigger.get_info()
        result = info.get("result")
        if result in "error":
            message = info.get("message")
            raise Exception(message)




class ScriptTrigger(Handler):
    '''Utility class that calls a trigger by external process'''
    # NOTE: this is not really a trigger'''

    def __init__(self):
        self.mode = "same process,new transaction"
        self.info = {}
        super(ScriptTrigger,self).__init__()


    def get_info(self):
        return self.info


    def set_data(self, data):
        self.data = data

    def execute(self):
        #protocol = 'xmlrpc'


        protocol = 'local'
        if protocol == 'local':
            server = TacticServerStub.get()
        else:
            server = TacticServerStub(protocol=protocol,setup=False)
            TacticServerStub.set(server)

            project = self.data.get("project")
            ticket = self.data.get("ticket")
            assert project
            assert ticket
            server.set_server("localhost")
            server.set_project(project)
            server.set_ticket(ticket)

        self.class_name = self.data.get('class_name')
        assert self.class_name
        self.kwargs = self.data.get('kwargs')
        if not self.kwargs:
            self.kwags = {}


        #trigger = eval("%s(**self.kwargs)" % self.class_name)
        trigger = Common.create_from_class_path(self.class_name, kwargs=self.kwargs)

        input_data = self.get_input_data()
        trigger.set_input(input_data)

        try:
            trigger.execute()

            info = trigger.get_info()
            result = info.get("result")
            if result is not None:

                # map booleans to a message
                if result in ['true', True]:
                    result = 'complete'

                elif result in ['false', False]:
                    result = 'revise'

                self.set_pipeline_status(result)
                self.info['result'] = result
            else:
                self.set_pipeline_status("complete")
                self.info['result'] = "complete"


        except Exception as e:
            #self.set_pipeline_status("error", {"error": str(e)})
            self.set_pipeline_status("revise", {"error": str(e)})

            import sys,traceback

            print("Error: ", e)
            # print the stacktrace
            tb = sys.exc_info()[2]
            stacktrace = traceback.format_tb(tb)
            stacktrace_str = "".join(stacktrace)
            print("-"*50)
            print(stacktrace_str)
            print(str(e))
            print("-"*50)

            self.info['result'] = "error"
            self.info['message'] = str(e)

 



    def set_pipeline_status(self, status, data={}):

        input = self.get_input_data()
        sobject = input.get("sobject")
        search_key = sobject.get("__search_key__")

        process = input.get("process")
        if not process:
            return

        server = TacticServerStub.get()
        print "set_pipeline_event: ", search_key, process, status
        server.call_pipeline_event(search_key, process, status, data )


#
# This main function is called from the SubprocessTrigger class defined in
# this module
#
if __name__ == '__main__':

    executable = sys.argv[0]
    args = sys.argv[1:]

    # load in the passed in data
    data_str = args[0]
    data = jsonloads(data_str)

    site = data.get("site")

    from pyasm.security import Batch
    project = data.get("project")
    assert project
    Batch(project_code=project, site=site)

    from pyasm.command import Workflow
    Workflow().init()
 

    input_data_str = args[1]
    input_data = jsonloads(input_data_str)

    # TODO: should this be in a Command?
    trigger = ScriptTrigger()
    trigger.set_data(data)
    trigger.set_input(input_data)
    trigger.execute()

    sys.exit(0)





