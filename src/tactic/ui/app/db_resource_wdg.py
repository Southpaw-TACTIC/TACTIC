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

__all__ = [ 'DbResourceWdg']

import types
import os

import js_includes

from pyasm.common import Container, Environment
from pyasm.biz import Project
from pyasm.search import Sql, Search, SearchType, DbResource, DbContainer
from pyasm.web import WebContainer, Widget, HtmlElement, DivWdg, Table
from pyasm.widget import IconWdg, RadioWdg, CheckboxWdg, TextWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import WizardWdg
from tactic.ui.widget import ActionButtonWdg


class DbResourceWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_style("padding: 20px")

        wizard = WizardWdg(title="Database Resource Manager")
        top.add(wizard)


        wizard.add(my.get_vendor_wdg(), "Vendor" )
        wizard.add(my.get_connect_wdg(), "Connection" )
        wizard.add(my.get_tables_wdg(), "Tables" )
        

        return top
   


    def get_vendor_wdg(my):
        
        div = DivWdg()
        div.set_name("Vendor")

        vendors = [
            "SQLite",
            "PostgreSQL",
            "MySQL",
            "Oracle",
            "SQLServer",
            "MongoDb"
        ]

        # unfortunately, Sqlite is capitalized incorectly in the code
        vendor_codes = [
            "Sqlite",
            "PostgreSQL",
            "MySQL",
            "Oracle",
            "SQLServer",
            "MongoDb"
        ]

        vendor_icons = [
            "Sqlite",
            "PostgreSQL",
            "MySQL",
            "Oracle",
            "SQLServer",
            "MongoDb"
        ]



        # get 3rd party vendors


        for vendor in vendors:

            vendor_div = DivWdg()
            div.add(vendor_div)
            vendor_div.add_style("margin: 10px")

            radio = RadioWdg("vendor")
            div.add(radio)
            radio.set_option("value", vendor)

            div.add(vendor)


        return div




    def get_connect_wdg(my):
        
        div = DivWdg()
        div.set_name("Connection")


        table = Table()
        div.add(table)

        from tactic.ui.panel import EditWdg
        edit = EditWdg(search_type="sthpw/db_resource", view="edit")

        table.add_row()
        table.add_cell(edit)


        return div




    def get_tables_wdg(my):
        
        div = DivWdg()
        div.set_name("Tables")

        div.add("In order to fully register a database, you must bind it to a TACTIC project")
        div.add("<br/>")



        project_code = "mongodb"
        database = "test_database"

        db_resource = DbResource(
                server='localhost',
                vendor='MongoDb',
                database=database
        )


        try:
            connect = DbContainer.get(db_resource)
        except Exception, e:
            div.add("Could not connect")
            div.add_style("padding: 30px")
            div.add("<br/>"*2)
            div.add(str(e))
            return div



        # Bind project to this resource
        database_text = TextWdg("database")
        div.add("Database: ")
        div.add(database_text)

        div.add("<br/>"*2)

        project_text = TextWdg("project")
        div.add("Project Code: ")
        div.add(project_text)

        div.add("<br/>")
        div.add("<hr/>")



        # connect and introspect the tables in this database
        tables = connect.get_tables()


        table = Table()
        div.add(table)
        table.set_max_width()

        for table_name in tables:
            table.add_row()
            search_type = "table/%s?project=%s" % (table_name, project_code)

            td = table.add_cell()
            icon = IconWdg("View Table", IconWdg.FOLDER_GO)
            td.add(icon)
            icon.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'cbjs_action': '''
                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: bvr.search_type
                }
                spt.panel.load_popup("table", class_name, kwargs);
                '''
            } )


            td = table.add_cell()
            td.add(table_name)

            td = table.add_cell()
            search = Search(search_type)
            count = search.get_count()
            td.add(" %s item/s" % count)

            columns = search.get_columns()
            td = table.add_cell()
            td.add(columns)

            # search_type
            td = table.add_cell()
            text = TextWdg("search_type")
            td.add(text)
            new_search_type = "%s/%s" % (project_code, table_name)
            text.set_value(new_search_type)



        register_div = DivWdg()
        div.add(register_div)
        register_div.add_style("padding: 20px")

        button = ActionButtonWdg(title="Register")
        register_div.add(button)


        return div



    def get_convert_to_project_wgd(my):
        
        div = DivWdg()
        div.set_name("Project")

        return div






