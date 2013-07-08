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

__all__ = ['SObjectDefaultConfig']


from pyasm.common import Base, Xml, Environment
from pyasm.search import DbContainer, SearchType, SqlException, Sql


class SObjectDefaultConfig(Base):
    '''An artificial config file is made if none are found'''

    def __init__(my, search_type, view, config_base=None, mode="columns"):

        my.search_type = search_type

        if view:
            my.view = view
        else:
            my.view = config_base
        if not my.view:
            my.view = "table"

        # bit of protection ... : have been known to show up in view names
        my.view = my.view.replace(":", '_')

        #mode = "basic"

        my.xml = Xml()

        if mode == 'columns':
            my.handle_columns_mode()
        else:
            my.handle_basic_mode()


    def get_columns(my, required_only=False):
        if my.search_type == 'sthpw/virtual':
            return []

        search_type_obj = SearchType.get(my.search_type)
        table = search_type_obj.get_table()

        from pyasm.biz import Project
        db_resource = Project.get_db_resource_by_search_type(my.search_type)
        database_name = db_resource.get_database()
        db = DbContainer.get(db_resource)

        # table may not exist
        try:
            all_columns = db.get_columns(table)
            columns = []
            if required_only:
                nullables = db.get_column_nullables(table)
                for column in all_columns:
                    null_ok = nullables.get(column)
                    if not null_ok:
                        columns.append(column)

                # if there are no required columns
                if not columns:
                    columns = all_columns 
                
            else:
                columns = all_columns 
        except SqlException:
            Environment.add_warning('missing table', 'Table [%s] does not exist in database [%s]' %(table, database_name))
            return  []

        return columns




    def handle_basic_mode(my):

        doc = my.xml.create_doc("config")
        root = my.xml.get_root_node()
        
        db_columns = my.get_columns()

        if "code" in db_columns:
            columns = ["preview", "code"]
        elif "name" in db_columns:
            columns = ["preview", "name"]
        elif "name" in db_columns:
            columns = ["preview", "id"]


        table = my.xml.create_element("table")
        #root.appendChild(table)
        Xml.append_child(root, table)
        for column in ["preview", "code"]:
            element = my.xml.create_element("element")
            Xml.set_attribute(element, "name", column)
            #table.appendChild(element)
            Xml.append_child(table, element)

        # create the edit
        edit = my.xml.create_element("edit")
        #root.appendChild(edit)
        Xml.append_child(root, edit)

        for column in ["preview", "code"]:
            element = my.xml.create_element("element")
            Xml.set_attribute(element, "name", column)
            #edit.appendChild(element)
            Xml.append_child(edit, element)


        # create the manual publish view
        publish = my.xml.create_element("publish")
        #root.appendChild(publish)
        Xml.append_child(root, publish)
        element = my.xml.create_element("element")
        Xml.set_attribute(element, "name", "image")
        #publish.appendChild(element)
        Xml.append_child(publish, element)
        dis_element = my.xml.create_element("display")
        Xml.set_attribute(dis_element, "class", "ThumbInputWdg")
        act_element = my.xml.create_element("action")
        Xml.set_attribute(act_element, "class", "NullAction")
        #element.appendChild(dis_element)
        Xml.append_child(element, dis_element)
        #element.appendChild(act_element)
        Xml.append_child(element, act_element)

        element = my.xml.create_element("element")
        Xml.set_attribute(element, "name", "publish_files")
        #publish.appendChild(element)
        Xml.append_child(publish, element)
        dis_element = my.xml.create_element("display")
        Xml.set_attribute(dis_element, "class", "UploadWdg")
        # add options
        option = my.xml.create_text_element('names','publish_icon|publish_main')
        #dis_element.appendChild(option)
        Xml.append_child(dis_element, option)
        option = my.xml.create_text_element('required','false|true')
        #dis_element.appendChild(option)
        Xml.append_child(dis_element, option)

        act_element = my.xml.create_element("action")
        Xml.set_attribute(act_element, "class", "MultiUploadAction")
        # add options
        option = my.xml.create_text_element('names','publish_icon|publish_main')
        #act_element.appendChild(option)
        Xml.append_child(act_element, option)
        option = my.xml.create_text_element('types','icon_main|main')
        #act_element.appendChild(option)
        Xml.append_child(act_element, option)
        #element.appendChild(dis_element)
        Xml.append_child(element, dis_element)
        #element.appendChild(act_element)
        Xml.append_child(element, act_element)

        value = my.xml.to_string()
        my.xml = Xml()
        my.xml.read_string(value)




    def handle_columns_mode(my):

        doc = my.xml.create_doc("config")
        root = my.xml.get_root_node()
        
        columns = my.get_columns()
        if len(columns) == 1 and columns[0] == "id":
            columns = my.get_columns(required_only=False)

        # create the table
        # search is a special view for SearchWdg and it should not be created
        if my.view not in ['search','publish']:
            table = my.xml.create_element(my.view)
            my.xml.append_child(root, table)
            for column in columns:
                if column in ["id", "oid", "s_status"]:
                    continue
                element = my.xml.create_element("element")
                Xml.set_attribute(element, "name", column)
                my.xml.append_child(table, element)

            # add history, input and output for the load view (designed for app loading)
            if my.view == 'load':
                element = my.xml.create_element("element")
                Xml.set_attribute(element, "name", "checkin")
                my.xml.append_child(table, element)
                for column in ['input', 'output']:
                    element = my.xml.create_element("element")
                    Xml.set_attribute(element, "name", column)
                    Xml.set_attribute(element, "edit", "false")
                    display_element = my.xml.create_element("display")
                    
                    Xml.set_attribute(display_element, "class", "tactic.ui.cgapp.LoaderElementWdg")
                    my.xml.append_child(element, display_element)

                    stype, key = SearchType.break_up_key(my.search_type)
                    op1 = my.xml.create_text_element("search_type", stype)
                    op2 = my.xml.create_text_element("mode", column)

                    
                    #display_element.appendChild(op1)
                    my.xml.append_child(display_element, op1)
                    #display_element.appendChild(op2)
                    my.xml.append_child(display_element, op2)

                    my.xml.append_child(table, element)
                
        value = my.xml.to_string()
        
        my.xml = Xml()
        my.xml.read_string(value)


    def get_type(my, element_name):
        xpath = "config/%s/element[@name='%s']/@type" % (my.view,element_name)
        type = my.xml.get_value(xpath)

        if not type:
            xpath = "config/%s/element[@name='%s']/@type" % ("definition",element_name)
            type = my.xml.get_value(xpath)

        return type




       
    def get_xml(my):
        return my.xml









