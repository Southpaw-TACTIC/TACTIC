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

    def create(my):


        project = Project.get_by_code("unittest")
        if project:

            my.delete()

        print "Setting up clean Unittest project"

        # create the project
        create_cmd = CreateProjectCmd(project_code="unittest", project_title="Unittest") #, project_type="unittest")
        create_cmd.execute()

        # install the unittest plugin
        installer = PluginInstaller(relative_dir="TACTIC/unittest", verbose=False)
        installer.execute()



    def delete(my):
        print "Deleting existing Unittest project"
        delete_cmd = DeleteProjectCmd(project_code="unittest")
        delete_cmd.execute()




if __name__ == '__main__':
    Batch(project_code="unittest")
    
    cmd = UnittestEnvironment()
    cmd.create()

    cmd.delete()

