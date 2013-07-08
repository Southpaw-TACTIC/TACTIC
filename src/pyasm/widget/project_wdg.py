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

__all__ = ['ProjectWdg', 'ProjectClassWdg', 'ProjectSummaryWdg']

import os

from pyasm.common import Environment
from pyasm.search import DbContainer, Search
from pyasm.web import Widget, Table, HtmlElement, WebContainer
from pyasm.widget import IconWdg, ButtonWdg

from table_element_wdg import BaseTableElementWdg

#TODO: to be replaced by the same file in tactic.ui.table

class ProjectWdg(BaseTableElementWdg):

    def get_title(my):
        return "Database"

    def preprocess(my):
        my.version = Environment.get_release_version()

    def get_display(my):

        widget = Widget()

        project = my.get_current_sobject()

        table = Table()
        widget.add(table)
        table.add_style("width: 140px")

        table.add_row()
        table.add_cell("Exists: ")
        table.add_cell("&nbsp;")


        try:
            exists = project.database_exists()
        except:
            #print "Error checking if database exists for project [%s]" % project.get_code()
            exists = False

        if exists:
            table.add_cell( IconWdg("database", IconWdg.DOT_GREEN) )
        else:
            table.add_cell( IconWdg("database", IconWdg.DOT_RED) )


        table.add_row()
        table.add_cell("Version: ")
        last_version_update = project.get_value("last_version_update")
        table.add_cell( last_version_update)
        if last_version_update >= my.version:
            table.add_cell( IconWdg("database", IconWdg.DOT_GREEN) )
        else:
            table.add_cell( IconWdg("database", IconWdg.DOT_RED) )

        widget.add("<br/>")
 
        """
        widget.add("Schema: ")
        widget.add("<br/>")

        widget.add("Context: ")
        widget.add("<br/>")

        widget.add("Data: ")
        widget.add("<br/>")
        """

        return widget


class ProjectClassWdg(BaseTableElementWdg):


    def get_display(my):

        widget = Widget()

        project = my.get_current_sobject()

        table = Table()
        table.set_class("minimal")
        for setting in ('dir_naming_cls', 'file_naming_cls', 'code_naming_cls', 'node_naming_cls', 'sobject_mapping_cls'):

            table.add_row()
            td = table.add_cell("<i>%s</i>: " % setting)
            td.add_style("text-align: right")
            value = project.get_value(setting)
            table.add_cell(value)

        widget.add(table)
        return widget




class ProjectSummaryWdg(BaseTableElementWdg):


    def get_display(my):

        widget = Widget()


        web = WebContainer.get_web()
        args = web.get_form_args()
        search_type = args['search_type']
        search_id = args['search_id']
        project = Search.get_by_id(search_type, search_id)

        #project = my.sobject
        project_code = project.get_code()
        project_type = project.get_type()

        widget.add("<h3>Summary: %s</h3>" % project_code)

        last_db_update = project.get_value("last_db_update")
        widget.add("Last Database Update: %s" % last_db_update)


        install_dir = Environment.get_install_dir()
        summary_exec = "%s/src/pyasm/search/upgrade/summary.py" % install_dir
        cmd = 'python "%s" %s %s' % (summary_exec, project_code, project_type)
        pre = my.get_results_wdg(cmd)
        widget.add(pre)

        if project_type == "prod":
            pass
        elif project_type == "flash":
            pass
        else:
            data_exec = "%s/src/pyasm/search/upgrade/data_summary.py" % install_dir
            for table in ['search_object', 'notification']:
                cmd = 'python "%s" %s %s %s' % (data_exec, project_code, project_type, table)
                print cmd
                pre = my.get_results_wdg(cmd)
                widget.add(pre)

        return widget

    def get_results_wdg(my, cmd):
        '''get results from a piped command'''
        pipe = os.popen(cmd)
        result = pipe.readlines()
        pipe.close()
        pre = HtmlElement.pre()
        pre.add( "".join(result) )
        return pre
       


        return widget

    def get_results_wdg(my, cmd):
        '''get results from a piped command'''
        pipe = os.popen(cmd)
        result = pipe.readlines()
        pipe.close()
        pre = HtmlElement.pre()
        pre.add( "".join(result) )
        return pre
       


