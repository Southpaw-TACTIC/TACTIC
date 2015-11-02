############################################################
#
#    Copyright (c) 2012, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#
__all__ = ['BaseCmd', 'DelegateCmd']

from subversion import *
from perforce import *

import os, sys, traceback
try:
    import json
except:
    import simplejson as json
import pprint



from subversion import Subversion
from perforce import PerforceImpl

class BaseCmd():

    def __init__(my, **kwargs):
        my.kwargs = kwargs
        my.ret_val = {}

        # the the scm user and password
        user = my.kwargs.get("user")
        password = my.kwargs.get("password")
        root = my.kwargs.get("root")
        sync_dir = my.kwargs.get("sync_dir")
        branch = my.kwargs.get("branch")

        sync_path = my.kwargs.get("sync_path")

        #my.scm = Subversion(user=user, password=password)
        my.scm = PerforceImpl(**kwargs)
        my.scm.set_root(root)
        my.scm.set_branch(branch)
        my.scm.set_sync_dir(sync_dir)


    def get_log(my):
        return my.scm.get_log()


class DelegateCmd(BaseCmd):
    def execute(my):
        method = my.kwargs.get("method")
        args = my.kwargs.get("args")
        if args:
            ret_val = eval("my.scm.%s(*args)" % method)
        else:
            ret_val = eval("my.scm.%s()" % method)

        return {
           "value": ret_val,
           "error": None,
           "log": my.scm.get_log()
        }



__all__.append('CmdWrapper')
class CmdWrapper():
    def __init__(my, **kwargs):
        my.kwargs = kwargs


    def execute(my):
        return run( my.kwargs)



def run(kwargs=None):

    if os.name == "nt":
        tactic_data = "C:/ProgramData/Tactic"
    else:
        tactic_data = "/tmp/perforce"

    cmd = None

    try:
        from tactic_client_lib import scm


        base = "%s/temp/output" % tactic_data
        if not os.path.exists(base):
            os.makedirs(base)

        kwargs_path = "%s/kwargs.json" % base
        output_path = "%s/output.json" % base
        pretty_output_path = "%s/pretty_output.json" % base


        if kwargs == None:
            f = open(kwargs_path, 'r')
            kwargs_json = f.read()
            f.close()

            kwargs = json.loads(kwargs_json)

        kwargs2 = {}
        for key, value in kwargs.items():
            kwargs2[key.encode("UTF8")] = value


        class_name = kwargs.get("class_name")
        if not class_name:
            class_name = "DelegateCmd"

        cmd = eval("%s(**kwargs2)" % class_name)
        ret_val = cmd.execute()

        ret_val['status'] = 'OK'
        ret_val_json = json.dumps(ret_val)

        f = open(output_path, 'w')
        f.write(ret_val_json)
        f.close()

        f = open(pretty_output_path, 'w')
        pp = pprint.PrettyPrinter(indent=4, stream=f)
        pp.pprint(ret_val)
        f.close()


    except Exception, e:
        error = str(e)
        print error
        f = open(output_path, 'w')


        tb = sys.exc_info()[2]
        stacktrace = traceback.format_tb(tb)
        stacktrace_str = "".join(stacktrace)

        ret_val = {
            "status": "error" ,
            "msg": "%s" % e,
            "stack_trace": stacktrace_str
        }

        if cmd:
            ret_val['log'] = cmd.get_log()

        ret_val_json = json.dumps(ret_val)
        f.write(ret_val_json);
        f.close()

        f = open(pretty_output_path, 'w')
        pp = pprint.PrettyPrinter(indent=4, stream=f)
        pp.pprint(ret_val)
        f.close()


    finally:
        if not os.path.exists(output_path):
            f = open(output_path, 'w')
            ret_val = {
                "status": "error" ,
                "msg": "%s" % e,
                "stack_trace": "unkown"
            }
            f.close()


        return ret_val



if __name__ == '__main__':
    run()
