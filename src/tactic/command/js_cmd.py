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
__all__ = ['JsCmd']

import tacticenv

from pyasm.common import TacticException, Environment, Config, jsondumps, jsonloads, JsWrapper
from pyasm.command import Command, CommandExitException
from pyasm.biz import Project
from pyasm.search import Search
from python_cmd import PythonCmd, PythonTrigger

from tactic_client_lib import TacticServerStub


import os

class JsCmd(PythonCmd):

    def get_results(my):
        code = my.kwargs.get("code")
        script_path = my.kwargs.get("script_path")
        file_path = my.kwargs.get("file_path")


        # if a script path is specified, then get it from the custom_script
        # table
        if script_path:

            folder = os.path.dirname(script_path)
            title = os.path.basename(script_path)

            search = Search("config/custom_script")
            search.add_filter("folder", folder)
            search.add_filter("title", title)
            custom_script = search.get_sobject()
            if not custom_script:
                raise TacticException("Custom script with path [%s/%s] does not exist" % (folder, title) )
            code = custom_script.get_value("script")

        elif file_path:
            f = open(file_path)
            code = f.read()
            f.close()


        wrapper = JsWrapper.get()
        results = wrapper.execute_func(code, my.kwargs)


        return results


    def run(code, kwargs):
        code = jsondumps(code)
        kwargs = jsondumps(kwargs)

        install_dir = tacticenv.get_install_dir()
        cmd = '%s/src/tactic/command/js_cmd.py' % install_dir

        python_exec = Config.get_value("services", "python")
        cmd_list = [python_exec, cmd, code, kwargs]



        import subprocess
        program = subprocess.Popen(cmd_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret_val, error = program.communicate()

        lines = []
        start = False
        for line in ret_val.split("\n") :
            if line.startswith("~"*20):
                start = True
                continue

            if not start:
                continue

            lines.append(line)

        value = jsonloads("\n".join(lines))


        return value

    run = staticmethod(run)






if __name__ == '__main__':

    project_code = "vfx"
    site = "vfx_test"

    import sys
    args = sys.argv[1:]

    code = args[0]
    code = jsonloads(code)

    kwargs = args[1]
    kwargs = jsonloads(kwargs)


    from pyasm.security import Batch
    Batch(site=site, project_code=project_code)

    cmd = JsCmd(code=code, input=kwargs)
    Command.execute_cmd(cmd)

    ret_val = cmd.info.get("spt_ret_val")
    print "~"*20
    print ret_val







