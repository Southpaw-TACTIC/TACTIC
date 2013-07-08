###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['SearchTypeHasTableElementWdg']

from pyasm.biz import Project
from pyasm.search import Sql, DatabaseException, DbContainer
from pyasm.web import DivWdg, Widget
from pyasm.widget import SimpleTableElementWdg, IconWdg



class SearchTypeHasTableElementWdg(SimpleTableElementWdg):
    '''Shows a red or green dot depending of there table is present in this
    project or not'''

    def get_display(my):

        widget = DivWdg()
        widget.add_style("text-align: center")

        search_type = my.get_current_sobject()

        project_code = search_type.get_value("database")
        if project_code == "{project}":
            # HACK: assumes database == project_code.  Can't seem to get
            # around the {project} variable ... need to look at this
            # sometime
            project = Project.get()
        else:
            project = Project.get_by_code(project_code)


        if not project:
            widget.add( IconWdg("Exists", IconWdg.ERROR) )
            widget.add( "Project does not exist")
            return widget

        table = search_type.get_table()

        if not table:
            return ""


        try:
            db_resource = project.get_project_db_resource()
            sql = DbContainer.get(db_resource)
            tables = sql.get_tables()
            has_table = table in tables
        except DatabaseException:
            has_table = False


        if has_table:
            widget.add( IconWdg("Exists", IconWdg.DOT_GREEN) )
        else:
            widget.add( IconWdg("Does not Exist", IconWdg.DOT_RED) )

        return widget


