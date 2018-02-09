###########################################################
#
# Copyright (c) 2005-2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['UpdateWdg']

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.biz import Project
from pyasm.command import Command
from pyasm.web import DivWdg, Table

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg

import os


class UpdateWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_style("padding: 10px")
        top.add_color("background", "background")
        top.add_style("width: 400px")

        inner = DivWdg()
        top.add(inner)

        inner.add("The following projects have databases that are out of date with this version of TACTIC")


        server_version = Environment.get_release_version() 

        server_div = DivWdg()
        inner.add(server_div)
        server_div.add("Installed TACTIC Version: ")
        server_div.add(server_version)
        server_div.add_style("padding: 20px")
        server_div.add_style("font-weight: bold")

        search = Search("sthpw/project")
        projects = search.get_sobjects()


        projects_div = DivWdg()
        inner.add(projects_div)

        table = Table()
        projects_div.add(table)
        table.add_style("margin: 20px")
        table.set_max_width()

        for project in projects:
            project_code = project.get_code()
            if project_code == 'admin':
                continue

            table.add_row()

            project_version = project.get_value("last_version_update")
            if project_version < server_version:

                td = table.add_cell()
                td.add(project_code)
                td = table.add_cell()

                if not project_version:
                    td.add("-")
                else:
                    td.add(project_version)








        button = ActionButtonWdg(title="Update")
        inner.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var server = TacticServerStub.get();
            var cmd = 'tactic.ui.app.update_wdg.UpdateCbk';
            server.execute_cmd(cmd);
            '''
        } )


        return top





class UpdateCbk(Command):

    def execute(self):
        install_dir = Environment.get_install_dir()
        python = Environment.get_python_exec()
        upgrade = "%s %s/src/bin/upgrade_db.py -f --yes" % (python, install_dir)

        os.system(upgrade)





