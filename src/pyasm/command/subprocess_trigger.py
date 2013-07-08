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

__all__ = ['SubprocessTrigger', 'ScriptTrigger']

import tacticenv

import sys
import subprocess
from subprocess import Popen

from pyasm.common import Config, Common, jsonloads, jsondumps

from tactic_client_lib import TacticServerStub
from tactic_client_lib.interpreter import Handler



class SubprocessTrigger(Handler):
    '''Utility class that calls a trigger by external process'''
    def __init__(my):
        my.mode = "same process,new transaction"
        super(SubprocessTrigger,my).__init__()

    def set_data(my, data):
        my.data = data
        my.class_name = data.get("class_name")

    def get_class_name(my):
        return my.class_name

    def set_mode(my, mode):
        my.mode = mode

    def execute(my):
      
        input_data = my.get_input_data()
        data = my.data

        # input data for the handler
        if my.mode == 'separate process,blocking':
            input_data_str = jsondumps(input_data)
            data_str = jsondumps(data)

            file = __file__
            py_exec = Config.get_value("services", "python")
            if not py_exec:
                py_exec = "python"

            retcode = subprocess.call([py_exec, file, data_str, input_data_str])

        elif my.mode == 'separate process,non-blocking':
            input_data_str = jsondumps(input_data)
            data_str = jsondumps(data)

            file = __file__
            py_exec = Config.get_value("services", "python")
            if not py_exec:
                py_exec = "python"

            retcode = subprocess.Popen([py_exec, file, data_str, input_data_str])
        elif my.mode == 'same process,new transaction':
            # run it inline
            trigger = ScriptTrigger()
            trigger.set_data(data)
            trigger.set_input(input_data)
            trigger.execute()


        # DEPRECATED MMS mode
        elif my.mode == 'MMS':
            # run it inline
            trigger = MMSScriptTrigger()
            trigger.set_data(data)
            trigger.set_input(input_data)
            trigger.execute()





class ScriptTrigger(Handler):

    def set_data(my, data):
        my.data = data

    def execute(my):
        #protocol = 'xmlrpc'
        protocol = 'local'
        if protocol == 'local':
            server = TacticServerStub.get()
        else:
            server = TacticServerStub(protocol=protocol,setup=False)
            TacticServerStub.set(server)

            project = my.data.get("project")
            ticket = my.data.get("ticket")
            assert project
            assert ticket
            server.set_server("localhost")
            server.set_project(project)
            server.set_ticket(ticket)

        my.class_name = my.data.get('class_name')
        assert my.class_name
        my.kwargs = my.data.get('kwargs')
        if not my.kwargs:
            my.kwags = {}


        #trigger = eval("%s(**my.kwargs)" % my.class_name)
        trigger = Common.create_from_class_path(my.class_name, kwargs=my.kwargs)

        input_data = my.get_input_data()
        trigger.set_input(input_data)
        trigger.execute()



class MMSScriptTrigger(Handler):

    def set_data(my, data):
        my.data = data

    def execute(my):
        #protocol = 'xmlrpc'
        protocol = 'local'
        if protocol == 'local':
            server = TacticServerStub.get()
        else:
            server = TacticServerStub(protocol=protocol,setup=False)
            TacticServerStub.set(server)

            project = my.data.get("project")
            ticket = my.data.get("ticket")
            assert project
            assert ticket
            server.set_server("localhost")
            server.set_project(project)
            server.set_ticket(ticket)

        my.class_name = my.data.get('class_name')
        assert my.class_name

        # get the script to run
        script_code = my.data.get("script_code")
        if script_code:
            search_type = "config/custom_script"
            search_key = server.build_search_key(search_type, script_code)
            script_obj = server.get_by_search_key(search_key)
            script = script_obj.get('script')
            my.run_script(script)
        else:
            print "Nothing to run"


    def run_script(my, script):
        # load and compile the file
        script = script.lstrip()
        try:
            exec(script)
        except Exception, e:
            print "-"*20
            print script
            print "-"*20
            raise

        trigger = eval("%s()" % my.class_name)

        input_data = my.get_input_data()

        trigger.set_input(input_data)
        trigger.execute()


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

    from pyasm.security import Batch
    project = data.get("project")
    assert project
    Batch(project_code=project)

    input_data_str = args[1]
    input_data = jsonloads(input_data_str)

    trigger = ScriptTrigger()
    trigger.set_data(data)
    trigger.set_input(input_data)
    trigger.execute()
    sys.exit(0)





