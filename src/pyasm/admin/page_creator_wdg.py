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

__all__ = ['PageCreatorWdg', 'AssetCreatorWdg', 'AssetEditorWdg', 'PageCreatorCmd']

from pyasm.common import Xml
from pyasm.command import Command, CommandException, CommandExitException
from pyasm.search import *
from pyasm.web import *
from pyasm.widget import *

from retire_wdg import *
from site_creator_wdg import *
from security_manager_wdg import *
from admin_object_wdg import *



class PageCreatorWdg(Widget):
    def __init__(my, database, schema):
        my.database = database
        my.schema = schema
        super(PageCreatorWdg,my).__init__()


    def init(my):

        # FIXME: hack this in for now to handle "public"
        if my.schema == "public":
            my.namespace = my.database
        else:
            my.namespace = "%s/%s" % (my.database,my.schema)

        marshaller = WebContainer.register_cmd("pyasm.admin.PageCreatorCmd")
        marshaller.set_option("database", my.database)
        marshaller.set_option("schema", my.schema)

        tab = TabWdg()
        tab.set_tab_key("asset_editor")

        tab_value = tab.get_tab_value()

        asset = None
        edit = None
        retire = None
        site = None
        login = None
        groups = None
        security = None

        if tab_value == "Assets":
            asset = AssetCreatorWdg(my.database, my.schema)
        elif tab_value == "Edit":
            edit = AssetEditorWdg(my.database, my.schema)
        elif tab_value == "Site":
            site = SiteCreatorWdg(my.database, my.schema)
        elif tab_value == "Login":
            login = LoginWdg()
        elif tab_value == "Groups":
            groups = LoginGroupWdg()
        elif tab_value == "Security":
            security = SecurityManagerWdg()



        tab.add( site, "Site")
        tab.add( asset, "Assets")
        tab.add( edit, "Edit" )
        tab.add( login, "Login" )
        tab.add( groups, "Groups" )
        tab.add( security, "Security" )

        my.add(tab)



class AssetCreatorWdg(Widget):

    def __init__(my, database, schema):
        my.database = database
        my.schema = schema

        # FIXME: hack this in for now to handle "public"
        if schema == "public":
            my.namespace = my.database
        else:
            my.namespace = "%s/%s" % (my.database,my.schema)
        super(AssetCreatorWdg,my).__init__()


    def init(my):

        div = HtmlElement.div()
        div.add_style("border-style: solid")
        div.add_style("border-width: 1px")
        div.add_style("padding: 10px 0px 10px 0px")

        div.add( my.get_existing_wdg() )
        div.add( my.create_div() )

        my.add(div)


    def get_existing_wdg(my):

        div = DivWdg()
        div.set_class("admin_section")

        title = DivWdg("Existing Assets Types")
        title.set_class("admin_header")
        div.add(title)

        search_type = SearchType.SEARCH_TYPE

        search = Search( search_type )
        search.add_filter("namespace", my.namespace)

        table_wdg = TableWdg( search_type, "simple" )
        table_wdg.set_search(search)
        div.add(table_wdg)

        return div



    def create_div(my):

        create_div = HtmlElement.div()
        create_div.set_class("admin_section")

        title = DivWdg("Create New Asset Type")
        title.set_class("admin_header")
        create_div.add(title)

        submit_input = SubmitWdg("create_asset", "Create")
        submit_input.add_style("float: right")
        submit_input.add_style("margin: 5px")
        create_div.add(submit_input)



        name_input = TextWdg("asset_name")

        search = Search( SearchType.SEARCH_TYPE )
        search.add_filter("namespace", my.namespace)

        template_select = SelectWdg("copy_from_template")
        template_select.add_empty_option()
        template_select.set_search_for_options( \
                search, "search_type", "table_name")
        #template_select.set_option("labels", "---|People")

        description = TextAreaWdg("asset_description")


        table = Table()
        table.set_max_width()
        table.set_class("edit")
        table.add_row()
        table.add_header("New Asset Name: ")
        table.add_cell(name_input)
        table.add_row()
        table.add_header("Copy from template: ")
        table.add_cell(template_select)
        table.add_row()
        table.add_header("Description: ")
        table.add_cell(description)

        create_div.add(table)

        return create_div








class AssetEditorWdg(Widget):

    def __init__(my, database, schema):
        my.database = database
        my.schema = schema
        super(AssetEditorWdg,my).__init__()

    def init(my):

        # FIXME: hack this in for now to handle "public"
        if my.schema == "public":
            my.namespace = my.database
        else:
            my.namespace = "%s/%s" % (my.database,my.schema)


        WebContainer.register_cmd("pyasm.admin.SObjectAddAttrCmd")

        # create the select widget for the asset type
        select = SelectWdg("current_search_type")
        select.set_persistence()
        search = Search( SearchType.SEARCH_TYPE )
        search.add_filter("namespace", my.namespace)
        select.set_search_for_options(search,"search_type","table_name")

        title = DivWdg()
        title.add_style("text-align: center")
        title.add("<b>Current Asset Type:</b> ")
        title.add(select)
        title.add(IconRefreshWdg())

        my.add(title)




        # create the config
        search_type = select.get_value()
        if search_type == "":
            return

        try:
            search_type_obj = SearchType.get(search_type)
            my.widget_config = WidgetConfig.get_by_search_type(search_type_obj,"table")
        except SearchException:
            # if there is a search exception, then this search_type does not
            # exist
            return



        my.add( my._get_category_wdg() )



        attr_div = HtmlElement.div()
        attr_div.set_class("admin_section")


        # display all of the templates
        table = Table()
        table.set_max_width()
        table.set_class("table")
        table.add_row()
        table.add_header("&nbsp;")
        table.add_header("Attribute")
        table.add_header("Filter")
        table.add_header("Visible")
        table.add_header( IconSubmitWdg("Remove", IconWdg.DELETE, True) )

        my.widget_config.set_view("table")
        attr_names = my.widget_config.get_element_names("default")
        for attr_name in attr_names:

            # suppress certain attributes
            if attr_name in ['update', 'history', 's_status']:
                continue

            table.add_row()
            icon = IconSubmitWdg("Move_Down_%s" % attr_name, "/context/icons/oo/stock_effects-object-hide-16.png")
                    # need to replace (above)!
            icon.set_text(attr_name)

            td = table.add_cell(icon)
            td.set_style("width: 1px")

            td = table.add_cell(attr_name.capitalize() )

            checkbox = CheckboxWdg("add_filter")
            checkbox.set_option("value", attr_name)
            td = table.add_cell(checkbox)

            checkbox = CheckboxWdg("visible")
            checkbox.set_option("value", attr_name)
            td = table.add_cell(checkbox)


            checkbox = CheckboxWdg("remove_attr")
            checkbox.set_option("value", attr_name)
            td = table.add_cell(checkbox)


        attr_div.add(table)


        name_input = TextWdg("attr_name")

        # Template attributes
        templates = ['title','images','status','discussion']
        template_input = SelectWdg("attr_type")
        template_input.set_option("values", "|".join(templates) )



        # custom attributes
        type_input = SelectWdg("attr_type")
        type_input.set_option("values", "Text|Number|Date|Status|Upload|Discussion|Snapshot")

        submit_input = SubmitWdg("Add")

        attr_div.add("Attribute Name: ")
        attr_div.add(name_input)
        attr_div.add("Type: ")
        attr_div.add(type_input)
        attr_div.add(submit_input)

        #attr_div.add("<br/>")
        #attr_div.add("Add Asset Type: ")
        #sobject_input = SelectWdg("add_search_type")
        #sobject_input.set_option("labels", "---|Shot|Layer|Instance")
        #sobject_input.set_option("values", "|bell/production/shot|bell/production/layer|/bell/production/instance")
        #attr_div.add(sobject_input)


        my.add(attr_div)







    def _get_category_wdg(my):

        div = DivWdg()
        div.set_class("admin_section")


        # display all of the categories
        table = Table()
        table.set_max_width()
        table.set_class("table")
        table.add_row()
        table.add_header("&nbsp;")
        table.add_header("Name")
        table.add_header( IconSubmitWdg("Remove", IconWdg.DELETE, True) )


        my.widget_config.set_view("edit")
        categories = my.widget_config.get_element_names("category")

        for category in categories:
            table.add_row()
            icon = IconSubmitWdg("Move_Down_%s" % category, "/context/icons/oo/stock_effects-object-hide-16.png")
                        # need to replace (above)!
            td = table.add_cell(icon)
            td.set_style("width: 1px")

            table.add_cell(category.capitalize())
            table.add_cell(CheckboxWdg())

        div.add(table)



        # custom categories
        category_input = TextWdg("category_name")
        submit_input = SubmitWdg("Add Category")

        div.add("Category Name: ")
        div.add(category_input)
        div.add(submit_input)



        return div





class PageCreatorCmd(Command):

    def __init__(my):
        my.database = None
        my.schema = None
        super(PageCreatorCmd,my).__init__()

    def get_title(my):
        return "Asset Creator"


    def set_database(my, database):
        my.database = database

    def set_schema(my, schema):
        my.schema = schema

    def execute(my):

        if not my.database or not my.schema:
            raise CommandException("Neither database nor schema is defined")

        # FIXME: hack this in for now to handle "public"
        if my.schema == "public":
            my.namespace = my.database
        else:
            my.namespace = "%s/%s" % (my.database,my.schema)

        web = WebContainer.get_web()
        if web.get_form_value("create_asset") == "":
            raise CommandExitException("Add button not pressed")

        my.asset_name = web.get_form_value("asset_name")
        if my.asset_name == "":
            raise CommandExitException("No asset name supplied")

        my.asset_description = web.get_form_value("asset_description")
        if my.asset_description == "":
            my.asset_description == "No description"


        copy_from_template = web.get_form_value("copy_from_template")
        search_type = "%s/%s" % (my.namespace, my.asset_name)

        my.register_search_type(search_type)
        my.search_type_obj = SearchType.get(search_type)


        if copy_from_template == "":
            my.create_config()
            my.create_table()
        else:
            my.copy_template_config(copy_from_template)
            my.copy_template_table(copy_from_template)
        
        my.description = "Created Asset Type '%s'" % my.asset_name



    def register_search_type(my, search_type):

        sobject = SearchType( SearchType.SEARCH_TYPE )

        sobject.set_value("search_type", search_type)

        sobject.set_value("namespace", my.namespace)
        sobject.set_value("database", my.database)
        sobject.set_value("schema", my.schema)
        sobject.set_value("table_name", "%s.%s" % (my.schema,my.asset_name) )
        sobject.set_value("class_name", "pyasm.search.search.SObject")
        sobject.set_value("description", my.asset_description)

        sobject.commit()




    def create_config(my):
        # create the xml document
        my.xml = Xml()
        my.xml.create_doc("config")
        root = my.xml.get_root_node()

        # handle the table config
        mode = my.xml.create_element("table")
        my._create_element(mode,"history")
        my._create_element(mode,"update")
        root.appendChild(mode)

        # handle the edit config
        mode = my.xml.create_element("edit")
        root.appendChild(mode)

        search_type = my.search_type_obj.get_full_key()
        SObjectDbConfig.create(search_type, "default", my.xml.get_xml() )


    def _create_element(my, mode, name):
        element = my.xml.create_element("element")
        Xml.set_attribute(element, "name", name)
        mode.appendChild(element)




    def copy_template_config(my, template):
        # copy a template from another search type
        template_type_obj = SearchType.get(template)
        template_config = WidgetConfig.get_by_search_type(template_type_obj)
        xml = template_config.get_xml()

        search_type = my.search_type_obj.get_full_key()
        SObjectDbConfig.create(search_type, xml.get_xml() )


    def copy_template_table(my, template):
        template_type_obj = SearchType.get(template)
        template_table = template_type_obj.get_table()
        table = my.search_type_obj.get_table()

        database = my.search_type_obj.get_database()

        sql = DbContainer.get(database)
        sql.copy_table_schema(template_table, table)

        # log that this table was creatd
        TableUndo.log(my.search_type_obj.get_base_key(), database, table)




    def create_table(my):

        create = CreateTable()
        table = "%s.%s" % (my.schema, my.asset_name)
        create.set_table( table )
        create.add_column("id", "serial")
        create.add_column("s_status", "varchar(30)")
        create.set_primary_key("id")

        statement = create.get_statement()

        database = my.search_type_obj.get_database()
        sql = DbContainer.get(database)
        sql.do_update(statement)

        TableUndo.log(my.search_type_obj.get_base_key(), database, table)

        return



class SObjectAddAttrCmd(Command):

    ADD_ATTR = "Add Attribute"    
    def get_title(my):
        return "Alter Attribute"

    def execute(my):
        web = WebContainer.get_web()

        my.search_type = web.get_form_value("current_search_type")
        if my.search_type == "":
            raise CommandExitException()

        if web.get_form_value(my.ADD_ATTR) != "":
            attr_name = web.get_form_value("attr_name")
            attr_type = web.get_form_value("attr_type")
            my._add_attr(attr_name, attr_type)

            search_type = web.get_form_value("_add_search_type")
            my._add_search_type(search_type)

        elif web.get_form_value("Remove") != "":
            my._remove_attr()

        elif web.get_form_value("Add Category") != "":
            attr_name = web.get_form_value("category_name")
            attr_type = "Category"
            my._add_attr(attr_name, attr_type)

        else:
            my._switch_attr()


    def _add_search_type(my, search_type):
        #my._add_attr()
        pass





    def _add_attr(my, attr_name, attr_type):

        if attr_name == "" or attr_type == "":
            raise CommandExitException("attr_name or attr_type is empty")

        config = SObjectDbConfig.get_by_search_type(my.search_type,"default")
        xml = config.get_xml_value("config")

        # find the node that has this attr_name
        node = xml.get_node("config/table/element[@name='%s']" % attr_name)

        # if it doesn't exist, then add it
        if node != None:
            raise CommandExitException()

        # create a new element for the table
        table = xml.get_node("config/table")
        element = xml.create_element("element")
        Xml.set_attribute(element,"name", attr_name)

        if attr_type == 'Category':
            Xml.set_attribute(element,"type", 'category')

        last_child = table.lastChild
        last_child = last_child.previousSibling
        table.insertBefore(element, last_child )


        # create a new element for the edit
        if attr_type not in ['Discussion','Status','Detail','Snapshot']:
            edit = xml.get_node("config/edit")
            element = xml.create_element("element")
            Xml.set_attribute(element,"name", attr_name)

            if attr_type == 'Category':
                Xml.set_attribute(element,"type", 'category')

            edit.appendChild(element)


        # commit the changes
        config.set_value("config", xml.get_xml())
        config.commit()


        # alter the table
        search_type_obj = SearchType.get(my.search_type)
        database = search_type_obj.get_database()
        table = search_type_obj.get_table()
        sql = DbContainer.get(database)


        type = None
        if attr_type == "Number":
            type = "int4"
        elif attr_type == "Text":
            type = "varchar(256)"
        elif attr_type == "Date":
            type = "timestamp"
        elif attr_type == "Upload":
            type = "text"
        elif attr_type == "Discussion":
            type = "text"
        elif attr_type == "Status":
            type = "text"
        elif attr_type == "Category":
            type = "varchar(256)"
        elif attr_type == "Snapshot":
            type = "text"


        from pyasm.search.sql import Sql
        if Sql.get_database_type() == 'SQLServer':
            statement = 'ALTER TABLE [%s] ADD "%s" %s' % \
                (table, attr_name, type)
        else:
            statement = "ALTER TABLE %s ADD COLUMN %s %s" % \
                (table, attr_name, type)
        sql.do_update(statement)
        AlterTableUndo.log_add(database,table,attr_name,type)


        my.add_description("Added attribute '%s' of type '%s'" % (attr_name, attr_type) )




    def _remove_attr(my):

        web = WebContainer.get_web()

        attr_names = web.get_form_values("remove_attr")
        if not attr_names:
            raise CommandExitException("No attrs selected to remove")

        config = SObjectDbConfig.get_by_search_type(my.search_type,"table")
        xml = config.get_xml_value("config")

        for attr_name in attr_names:

            # find the node that has this attr_name
            node = xml.get_node("config/table/element[@name='%s']" % attr_name)
            if node != None:
                # create a new element
                table = xml.get_node("config/table")
                table.removeChild(node)

            # find the node that has this attr_name
            node = xml.get_node("config/edit/element[@name='%s']" % attr_name)
            if node != None:
                # create a new element
                table = xml.get_node("config/edit")
                table.removeChild(node)



            # alter the table
            search_type_obj = SearchType.get(my.search_type)
            database = search_type_obj.get_database()
            table = search_type_obj.get_table()
            sql = DbContainer.get(database)


            from pyasm.search.sql import Sql
            if Sql.get_database_type() == 'SQLServer':
                statement = 'ALTER TABLE [%s] DROP "%s" %s' % \
                    (table, attr_name)
            else:
                statement = "ALTER TABLE %s DROP COLUMN %s" % \
                    (table, attr_name)

            sql.do_update(statement)
            AlterTableUndo.log_drop(database,table,attr_name)



        config.set_value("config", xml.get_xml() )
        config.commit()





    def _switch_attr(my):

        web = WebContainer.get_web()

        keys = web.get_form_keys()
        attr_name = ""
        for key in keys:
            if key.startswith("Move_Down") and web.get_form_value(key) != "":
                attr_name = web.get_form_value(key)

        if attr_name == "":
            return CommandExitException("No attrs selected to remove")

        config = SObjectDbConfig.get_by_search_type(my.search_type)
        xml = config.get_xml_value("config")

        sibling_name = ""

        # find the node an switch the one specified
        nodes = xml.get_nodes("config/table/element")
        for node in nodes:
            if Xml.get_attribute(node, "name") == attr_name:
                sibling = node.nextSibling.nextSibling
                sibling_name = Xml.get_attribute(sibling,"name")

                parent = node.parentNode
                parent.replaceChild(node, sibling)
                parent.insertBefore(sibling, node)
                break

        config.set_value("config", xml.get_xml() )
        config.commit()

        my.add_description("Order switch for attributes '%s' and '%s'" % \
            (attr_name,sibling_name) )












