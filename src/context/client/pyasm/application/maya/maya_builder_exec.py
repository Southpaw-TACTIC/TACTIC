#!/usr/bin/python
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

import sys


from .maya_environment import *
from .maya_app import *
from .maya_builder import *



def get_maya_builder_cmd(path, ticket):
    # dynamically import Config.  This can only be done by Tactic (no client)
    from pyasm.common import Config
    python = Config.get_value("services", "python")
    cmd = '%s "%s" %s %s' % (python, __file__, path, ticket)
    return cmd


def maya_builder_exec(path, ticket):
    # run this executable as a separate system process
    cmd = get_maya_builder_cmd(path, ticket)
    print(cmd)
    os.system(cmd)



if __name__ == '__main__':

    executable = sys.argv[0]
    path = sys.argv[1]
    ticket = sys.argv[2]

    # need to add these paths because they not currently in the
    # windows environment
    #sys.path.append("E:/sthpw/tactic/sthpw/src")
    from pyasm.security import Batch
    Batch()

    file = open(path, 'r')
    contents = file.read()
    file.close()

    # set up maya
    from pyasm.application.common import BaseAppInfo
    info = BaseAppInfo("maya")

    from pyasm.common import Environment
    tmpdir = "%s/temp/%s" % (Environment.get_tmp_dir(), ticket)
    info.set_tmpdir(tmpdir)

    info.set_user(Environment.get_user_name() )
    info.set_ticket(ticket)
    

    info.set_up_maya(init=True)

    env = info.get_app_env()

    env.set_tmpdir(tmpdir)


    # create the file builder
    builder = info.get_builder()
    builder.execute(contents)


    # save the file
    filepath = "%s/maya_render.ma" % env.get_tmpdir()
    info.get_app().save(filepath)

    from maya_introspect import MayaIntrospect
    introspect = MayaIntrospect()
    introspect.execute()
    session_xml = introspect.get_session_xml()

    # should reproduce glue!!!
    file = open("%s/session.xml" % env.get_tmpdir(), "w" )
    file.write(session_xml)
    file.close()






