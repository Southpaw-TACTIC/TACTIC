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
__all__ = ['SObjectCreatorWdg', 'SObjectCreatorCmd']

from pyasm.web import *
from pyasm.biz import Project, Schema, ProjectType
from pyasm.widget import *
from pyasm.admin import *
from pyasm.command import *
from pyasm.search import SearchType, Search, WidgetDbConfig, \
    CreateTable, DbContainer, TableUndo, SObjectFactory
from pyasm.common import Xml


class SObjectCreatorWdg(Widget):

    def __init__(my, **kwargs):

        database = kwargs.get("database")
        schema = kwargs.get("schema")

        if not database:
            my.database = Project.get_project_code()
        else:
            my.database = database

        if not schema:
            my.schema = "public"
        else:
            my.schema = schema

        # FIXME: hack this in for now to handle "public"
        if my.schema == "public":
            my.namespace = my.database
        else:
            my.namespace = "%s/%s" % (my.database,my.schema)

        super(SObjectCreatorWdg,my).__init__()

        marshaller = WebContainer.register_cmd("pyasm.admin.creator.SObjectCreatorCmd")
        marshaller.set_option("database", my.database)
        marshaller.set_option("schema", my.schema)


    def init(my):

        div = HtmlElement.div()
        div.add_style("border-style: solid")
        div.add_style("border-width: 1px")
        div.add_style("padding: 10px 0px 10px 0px")

        div.add( my.create_div() )
        div.add( my.get_existing_wdg() )

        my.add(div)


    def get_existing_wdg(my):

        div = DivWdg()
        div.set_class("admin_section")

        title = DivWdg("<h3>Search Types</h3>")
        title.set_class("admin_header")
        div.add(title)

        filter_box = DivWdg(css='filter_box')
        div.add(filter_box)
        
        select = FilterSelectWdg('project_type', label='Project Type: ', css='left')
        select.add_empty_option('-- All --')

        type_search = Search(ProjectType)
        type_search.add_column('type', distinct=True)
        select.set_search_for_options(type_search, 'type' , 'type')
        select.append_option('sthpw','sthpw')
        select.append_option("-- this project only --", my.namespace)    

        filter_box.add(SpanWdg(select, css='med'))
        search_type = SearchType.SEARCH_TYPE

        search = Search( search_type )

        ns = select.get_value()
        if ns:
            search.add_filter("namespace", ns)

        search_types = search.get_sobjects()


        table_wdg = TableWdg( search_type, "simple" )
        table_wdg.set_sobjects(search_types)
        div.add(table_wdg)

        return div



    def create_div(my):

        create_div = HtmlElement.div()
        create_div.set_class("admin_section")

        title = DivWdg("<h3>Create Search Type for Current Project</h3>")
        title.set_class("admin_header")
        create_div.add(title)
        
        name_input = TextWdg("asset_name")

        search = Search( SearchType.SEARCH_TYPE )
        search.add_filter("namespace", my.namespace)

        template_select = SelectWdg("copy_from_template")
        template_select.add_empty_option()
        template_select.set_search_for_options( \
                search, "search_type", "table_name")
        #template_select.set_option("labels", "---|People")

        title = TextWdg("asset_title")
        description = TextAreaWdg("asset_description")

        submit_input = IconSubmitWdg("create_asset", IconWdg.CREATE, long=True)
        submit_input.set_text('Create')
        submit_input.add_style("float: right")

        table = Table()
        table.add_style("margin: 10px 20px")
        table.add_col().set_attr('width','140')
        table.add_col().set_attr('width','400')
       
        table.add_row()
        table.add_header("Search Type: ").set_attr('align','left')
        td = table.add_cell(name_input)
        td.add(HintWdg("e.g. 'sound' or 'mocap'. The created name has the form '(project)/sound'"))
        table.add_row()
        table.add_header("Title: ").set_attr('align','left')
        td = table.add_cell(title)
        td.add(HintWdg("e.g. 'Sound' or 'Mocap'. It is for display."))
        table.add_row()
        table.add_header("Description: ").set_attr('align','left')
        table.add_cell(description)

        # parent
        parent_select = SelectWdg("sobject_parent")
        parent_select.set_option("query", "sthpw/search_object|search_type|search_type")
        parent_select.add_empty_option("-- None --")
        table.add_row()
        table.add_header("Parent Search Type: ").set_attr('align','left')
        table.add_cell(parent_select)

 

        #table.add_row()
        #table.add_header("Copy from template: ").set_attr('align','left')
        #table.add_cell(template_select)

        # determines if this is an instance
        # instances have:
        #   1) parent,
        #   2) relation,
        #   3) code = parent_code + "_" + relation_code
        #   4) short_code??
        """
        instance_checkbox = CheckboxWdg("instance")
        instance_checkbox.add_event("onclick", "toggle_display('instance_options')")
        table.add_row()
        table.add_header("Is Instance? ").set_attr('align','left')
        td = table.add_cell(instance_checkbox)
    
        div = DivWdg()
        div.set_id("instance_options")
        div.add_style("display: none")
        relation_select = SelectWdg("instance_relation")
        div.add("Relation: ")
        div.add(relation_select)
        div.add( HtmlElement.br() )
        td.add(div)
        """


        desc_checkbox = CheckboxWdg("sobject_desc")
        desc_checkbox.set_default_checked()
        table.add_row()
        table.add_header("Has Description? ").set_attr('align','left')
        table.add_cell(desc_checkbox)

        # determines whether sobject has a pipeline
        pipeline_checkbox = CheckboxWdg("sobject_pipeline")
        
        table.add_row()
        table.add_header("Has Pipeline? ").set_attr('align','left')
        table.add_cell(pipeline_checkbox)

        



        # Create a tab widget
        #create_tab = SelectWdg("create_tab")
        #create_tab.set_option("values", "My Tactic|Source Material|Asset Pipeline")
        #create_tab.add_empty_option("-- None --")

        #table.add_row()
        #table.add_header("Create Default View and Tab: ").set_attr('align','left')
        #table.add_cell(create_tab)

        main_table = Table()
        main_table.add_row()
        main_table.add_cell(table)
        main_table.add_cell(submit_input).set_attr('valign','bottom')

        web = WebContainer.get_web()
        hidden = HiddenWdg('search_type_created')
        create_div.add(hidden)
        search_type_val = hidden.get_value()
        if search_type_val:
            main_table.add_row_cell(SpanWdg('Search Type [%s] created...'%search_type_val, css='large message'))
        create_div.add(main_table)

        return create_div






class SObjectCreatorCmd(Command):

    def __init__(my):
        my.database = None
        my.schema = None
        my.has_description = True
        super(SObjectCreatorCmd,my).__init__()

    def get_title(my):
        return "SObject Creator"


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
        elif my.asset_name.find("/") != -1:
            my.namespace, my.asset_name = my.asset_name.split("/", 1)



        my.asset_description = web.get_form_value("asset_description")
        if my.asset_description == "":
            my.asset_description == "No description"

        my.asset_title = web.get_form_value("asset_title")
        if my.asset_title == "":
            my.asset_title == "No title"

        copy_from_template = web.get_form_value("copy_from_template")
        search_type = "%s/%s" % (my.namespace, my.asset_name)

        my.register_search_type(search_type)
        my.search_type_obj = SearchType.get(search_type)

        if web.get_form_value("sobject_pipeline"):
            my.has_pipeline = True
        else:
            my.has_pipeline = False

        if web.get_form_value("sobject_desc"):
            my.has_description = True
        else:
            my.has_description = False


        my.parent_type = web.get_form_value("sobject_parent")


        if not copy_from_template:
            my.create_config()
            my.create_table()
        else:
            # FIXME: don't copy config yet ... should really copy all
            # ... or have an option
            #my.copy_template_config(copy_from_template)
            my.copy_template_table(copy_from_template)


        # add this search_type to the schema for this project
        schema = Schema.get_by_code(my.database)
        if schema:
            schema.add_search_type(search_type, my.parent_type)

        
        my.description = "Created Search Type '%s'" % search_type
        web.set_form_value('search_type_created', search_type)


    def register_search_type(my, search_type):
        # first check if it already exists
        search = Search( SearchType.SEARCH_TYPE )
        search.add_filter("search_type", search_type)
        test_sobject = search.get_sobject()
        if test_sobject:
            raise CommandException("Search type [%s] already exists" % search_type)

        
        # create the search type
        sobject = SearchType( SearchType.SEARCH_TYPE )

        sobject.set_value("search_type", search_type)

        sobject.set_value("namespace", my.namespace)
        sobject.set_value("database", my.database)
        sobject.set_value("schema", my.schema)
        sobject.set_value("table_name", "%s.%s" % (my.schema,my.asset_name) )
        sobject.set_value("class_name", "pyasm.search.SObject")
        sobject.set_value("title", my.asset_title)
        sobject.set_value("description", my.asset_description)

        sobject.commit()




    def create_config(my):
        search_type = my.search_type_obj.get_base_key()

        # create the xml document
        view = "definition"
        xml = Xml()
        xml.create_doc("config")
        root = xml.get_root_node()
        view_node = xml.create_element(view)
        #root.appendChild(view_node)
        xml.append_child(root, view_node)

        WidgetDbConfig.create(search_type, view, xml.get_xml() )

 
        # create the edit view
        view = "edit"
        xml = Xml()
        xml.create_doc("config")
        root = xml.get_root_node()
        view_node = xml.create_element(view)
        #root.appendChild(view_node)
        xml.append_child(root, view_node)

        # create code element
        element = xml.create_element("element")
        Xml.set_attribute(element, "name", "code")
        #view_node.appendChild(element)
        xml.append_child(view_node, element)

        if my.has_pipeline:
            # create pipeline_code element
            element = xml.create_element("element")
            Xml.set_attribute(element, "name", "pipeline_code")
            #view_node.appendChild(element)
            xml.append_child(view_node, element)

            # create the sobject for now
            custom_property = SObjectFactory.create("prod/custom_property")
            custom_property.set_value("search_type", search_type)
            custom_property.set_value("name", "pipeline_code")
            custom_property.set_value("description", "Reference to pipelines")
            custom_property.commit()

        if my.has_description:
            # create pipeline_code element
            element = xml.create_element("element")
            Xml.set_attribute(element, "name", "description")
            #view_node.appendChild(element)
            xml.append_child(view_node, element)

            # create the sobject for now
            custom_property = SObjectFactory.create("prod/custom_property")
            custom_property.set_value("search_type", search_type)
            custom_property.set_value("name", "description")
            custom_property.set_value("description", "description_column")
            custom_property.commit()

        if my.parent_type:
            # create pipeline_code element
            element = xml.create_element("element")
            Xml.set_attribute(element, "name", "parent_code")
            #view_node.appendChild(element)
            xml.append_child(view_node, element)
            display_node = xml.create_element("display")
            Xml.set_attribute( display_node, 'class', 'SelectWdg')
            #element.appendChild(display_node)
            xml.append_child(element, display_node)
            query_node = xml.create_text_element("query", "%s|code|code" % my.parent_type)
            #display_node.appendChild(query_node)
            xml.append_child(display_node, query_node)

            custom_property = SObjectFactory.create("prod/custom_property")
            custom_property.set_value("search_type", search_type)
            custom_property.set_value("name", "parent_code")
            custom_property.set_value("description", "Reference to parent")
            custom_property.commit()


        WidgetDbConfig.create(search_type, view, xml.get_xml() )

      



    def _create_element(my, xml, view_node, name):
        element = xml.create_element("element")
        Xml.set_attribute(element, "name", name)
        #view_node.appendChild(element)
        xml.append_child(view_node, element)




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
        if my.schema == "public":
            table = my.asset_name
        else:
            table = "%s.%s" % (my.schema, my.asset_name)
        create.set_table( table )
        create.add("id", "int")
        create.add("code", "varchar")
        if my.has_pipeline:
            create.add("pipeline_code", "varchar")
        if my.has_description:
            create.add("description", "text")

        if my.parent_type:
            create.add("parent_code", "varchar")
            

        create.add("login", "varchar")
        create.add("timestamp", "timestamp")
        create.add("s_status", "varchar")
        create.set_primary_key("id")

        statement = create.get_statement()

        database = my.search_type_obj.get_database()
        sql = DbContainer.get(database)
        sql.do_update(statement)

        TableUndo.log(my.search_type_obj.get_base_key(),  database, table)

        return



