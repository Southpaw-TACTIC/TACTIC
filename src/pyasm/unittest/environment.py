###########################################################
#
# Copyright (c) 2013, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import tacticenv

from pyasm.common import TacticException
from pyasm.biz import Project
from pyasm.security import Batch
from pyasm.command import Command

from tactic.command import CreateProjectCmd, PluginInstaller
from tactic.ui.tools import DeleteProjectCmd

class UnittestEnvironment(object):

    def __init__(my, **kwargs):
        my.project_code = kwargs.get('project_code')
        if not my.project_code:
            my.project_code = 'unittest'

    def create(my):

        project = Project.get_by_code(my.project_code)
        if project:

            my.delete()

        print "Setting up clean Unittest project"

        # create the project
        create_cmd = CreateProjectCmd(project_code=my.project_code, project_title="Unittest") #, project_type="unittest")
        create_cmd.execute()

        # install the unittest plugin
        installer = PluginInstaller(relative_dir="TACTIC/internal/unittest", verbose=False)
        installer.execute()



    def delete(my):
        print "Deleting existing Unittest project"
        related_types = ["sthpw/schema"]
        delete_cmd = DeleteProjectCmd(project_code=my.project_code, related_types=related_types)
        delete_cmd.execute()

class Sample3dEnvironment(UnittestEnvironment):

    def create(my):

        project = Project.get_by_code(my.project_code)
        if project:

            my.delete()

        print "Setting up a basic Sample3d project"

        # create the project
        create_cmd = CreateProjectCmd(project_code=my.project_code, project_title="Sample 3D") #, project_type="unittest")
        create_cmd.execute()

        # install the unittest plugin
        installer = PluginInstaller(relative_dir="TACTIC/internal/sample3d", verbose=False)
        installer.execute()


if __name__ == '__main__':
    Batch(project_code="unittest")
    
    cmd = UnittestEnvironment()
    cmd.create()

    #cmd.delete()

