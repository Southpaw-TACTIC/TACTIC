###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['DbRegisterWdg']

import tacticenv


from pyasm.common import Common
from pyasm.command import Command
from pyasm.search import DbResource, Search, SearchType
from pyasm.biz import Project
from pyasm.widget import SelectWdg
from pyasm.web import DivWdg, WebContainer

from tactic.ui.common import BaseRefreshWdg



class DbRegisterWdg(BaseRefreshWdg):

    def get_value(my, name):
        web = WebContainer.get_web()
        value = web.get_form_value(name)
        if not value:
            return value
        return my.kwargs.get("value")



    def get_display(my):

        top = my.top
        top.add_style("padding: 20px")
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("width", "500px")

        top.add_class("spt_db_register_top")
        my.set_as_panel(top)


        inner = DivWdg()
        top.add(inner)


        # db resource
        db_resource = my.get_value("db_resource")

        db_resource_wdg = DivWdg()
        inner.add(db_resource_wdg)
        db_resource_wdg.add("Database Resource: ")

        search = Search("sthpw/db_resource")
        db_resources = search.get_sobjects()
        codes = [x.get_code() for x in db_resources]

        select = SelectWdg("db_resource")
        db_resource_wdg.add(select)
        select.set_option("values", codes)
        if db_resource:
            select.set_value(db_resource)
        select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_db_register_top");
            spt.panel.refresh(top);
            '''
        } )

        if db_resource:
            info_wdg = DivWdg()
            db_resource_wdg.add(info_wdg)
            info_wdg.add_border()
            info_wdg.add_style("padding: 20px")
            info_wdg.add_style("margin: 20px")



        inner.add("<br/>")


        # list of databases
        database_wdg = DivWdg()
        inner.add(database_wdg)
        database_wdg.add("Available Databases: ")


        databases = ['test', 'test1', 'test2']

        select = SelectWdg("databases")
        database_wdg.add(select)
        select.set_option("values", databases)



        # list of projects





        if my.kwargs.get('is_refresh') == 'true':
            return inner
        else:
            return top






class RegisterDbResourceCmd(Command):

    def execute(my):

        # create project if it exists
        project_code = "tims"
        project = Project.get_by_code(project_code)
        if not project:
            project = SearchType.create("sthpw/project")
            project.set_value("code", project_code)
            project.set_value("type", "default")
            project.commit()



        sql = project.get_sql()
        tables = sql.get_tables()



        print "Found the following tables: ", tables
        print

        # register all of the tables
        search_types = []

        for table in tables:

            # skip config tables
            if table in [
                    "spt_process",
                    "spt_trigger",
                    "spt_ingest_session",
                    "spt_ingest_rule",
                    "spt_plugin"
            ]:
                continue




            columns = sql.get_columns(table)

            # check if this is a config
            config_type = "config/%s" % table
            search_type_obj = Search.get_by_code("sthpw/search_type", config_type)
            if search_type_obj:
                continue


            # check to see if this is actually registered
            search_type = "%s/%s" % (project_code, table)
            search_types.append(search_type)
            print "search_type: ", search_type
            search_type_obj = Search.get_by_code("sthpw/search_type", search_type)
            if search_type_obj:
                print 'REGISTERED'
                continue

            print "Registering [%s] ..." % search_type
            search_type_obj = SearchType.create("sthpw/search_type")
            search_type_obj.set_value("namespace", project_code)
            search_type_obj.set_value("code", search_type)
            search_type_obj.set_value("search_type", search_type)
            search_type_obj.set_value("table_name", table)
            search_type_obj.set_value("database", "{project}")
            search_type_obj.set_value("class_name", "pyasm.search.SObject")
            search_type_obj.commit()

    
        # create a schema
        schema_xml = []
        schema_xml.append("<schema>")

        for search_type in search_types:
            schema_xml.append('''<search_type name="%s"/>''' % search_type)
        schema_xml.append("</schema>")
        schema_xml = "\n".join(schema_xml)
        print "schema: ", schema_xml

        schema = Search.get_by_code("sthpw/schema", project_code)
        if not schema:
            schema = SearchType.create("sthpw/schema")
            schema.set_value("code", project_code)
            schema.set_value("schema", schema_xml)
            schema.commit()


        
        # import all of the config tables
        database_impl = sql.get_database_impl()
        db_resource = sql.get_db_resource()
        database_impl.import_schema(db_resource, "simple")


if __name__ == '__main__':
    from pyasm.security import Batch
    Batch()
    cmd = RegisterDbResourceCmd()
    Command.execute_cmd(cmd)



