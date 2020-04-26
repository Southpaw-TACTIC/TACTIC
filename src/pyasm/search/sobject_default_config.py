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

    def __init__(self, search_type, view, config_base=None, mode="columns"):

        self.search_type = search_type

        if view:
            self.view = view
        else:
            self.view = config_base
        if not self.view:
            self.view = "table"

        # bit of protection ... : have been known to show up in view names
        self.view = self.view.replace(":", '_')

        #mode = "basic"

        self.xml = Xml()

        if mode == 'columns':
            self.handle_columns_mode()
        else:
            self.handle_basic_mode()


    def get_columns(self, required_only=False):
        if self.search_type == 'sthpw/virtual':
            return []

        search_type_obj = SearchType.get(self.search_type)
        table = search_type_obj.get_table()

        from pyasm.biz import Project
        db_resource = Project.get_db_resource_by_search_type(self.search_type)
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




    def handle_basic_mode(self):

        doc = self.xml.create_doc("config")
        root = self.xml.get_root_node()
        
        db_columns = self.get_columns()

        if "code" in db_columns:
            columns = ["preview", "code"]
        elif "name" in db_columns:
            columns = ["preview", "name"]
        elif "id" in db_columns:
            columns = ["preview", "id"]


        table = self.xml.create_element("table")
        Xml.append_child(root, table)
        for column in ["preview", "code"]:
            element = self.xml.create_element("element")
            Xml.set_attribute(element, "name", column)
            Xml.append_child(table, element)

        # create the edit
        edit = self.xml.create_element("edit")
        Xml.append_child(root, edit)

        for column in ["preview", "code"]:
            element = self.xml.create_element("element")
            Xml.set_attribute(element, "name", column)
            Xml.append_child(edit, element)


        # create the manual publish view
        publish = self.xml.create_element("publish")
        Xml.append_child(root, publish)
        element = self.xml.create_element("element")
        Xml.set_attribute(element, "name", "image")
        Xml.append_child(publish, element)
        dis_element = self.xml.create_element("display")
        Xml.set_attribute(dis_element, "class", "ThumbInputWdg")
        act_element = self.xml.create_element("action")
        Xml.set_attribute(act_element, "class", "NullAction")
        Xml.append_child(element, dis_element)
        Xml.append_child(element, act_element)

        element = self.xml.create_element("element")
        Xml.set_attribute(element, "name", "publish_files")
        Xml.append_child(publish, element)
        dis_element = self.xml.create_element("display")
        Xml.set_attribute(dis_element, "class", "UploadWdg")
        # add options
        option = self.xml.create_text_element('names','publish_icon|publish_main')
        Xml.append_child(dis_element, option)
        option = self.xml.create_text_element('required','false|true')
        Xml.append_child(dis_element, option)

        act_element = self.xml.create_element("action")
        Xml.set_attribute(act_element, "class", "MultiUploadAction")
        # add options
        option = self.xml.create_text_element('names','publish_icon|publish_main')
        Xml.append_child(act_element, option)
        option = self.xml.create_text_element('types','icon_main|main')
        Xml.append_child(act_element, option)
        Xml.append_child(element, dis_element)
        Xml.append_child(element, act_element)

        value = self.xml.to_string()
        self.xml = Xml()
        self.xml.read_string(value)




    def handle_columns_mode(self):

        doc = self.xml.create_doc("config")
        root = self.xml.get_root_node()
        
        columns = self.get_columns()
        if len(columns) == 1 and columns[0] == "id":
            columns = self.get_columns(required_only=False)

        # create the table
        # search is a special view for SearchWdg and it should not be created
        if self.view not in ['search','publish']:
            if self.view.find('@') != -1:
                table = self.xml.create_element('view', attrs={'name': self.view})
            else:
                table = self.xml.create_element(self.view)
            self.xml.append_child(root, table)
            for column in columns:
                if column in ["_id", "id", "oid", "s_status"]:
                    continue
                element = self.xml.create_element("element")
                Xml.set_attribute(element, "name", column)
                self.xml.append_child(table, element)

            # add history, input and output for the load view (designed for app loading)
            if self.view == 'load':
                element = self.xml.create_element("element")
                Xml.set_attribute(element, "name", "checkin")
                self.xml.append_child(table, element)
                for column in ['input', 'output']:
                    element = self.xml.create_element("element")
                    Xml.set_attribute(element, "name", column)
                    Xml.set_attribute(element, "edit", "false")
                    display_element = self.xml.create_element("display")
                    
                    Xml.set_attribute(display_element, "class", "tactic.ui.cgapp.LoaderElementWdg")
                    self.xml.append_child(element, display_element)

                    stype, key = SearchType.break_up_key(self.search_type)
                    op1 = self.xml.create_text_element("search_type", stype)
                    op2 = self.xml.create_text_element("mode", column)

                    
                    self.xml.append_child(display_element, op1)
                    self.xml.append_child(display_element, op2)

                    self.xml.append_child(table, element)
                
        value = self.xml.to_string()
        
        self.xml = Xml()
        self.xml.read_string(value)


    def get_type(self, element_name):
        xpath = "config/%s/element[@name='%s']/@type" % (self.view,element_name)
        type = self.xml.get_value(xpath)

        if not type:
            xpath = "config/%s/element[@name='%s']/@type" % ("definition",element_name)
            type = self.xml.get_value(xpath)

        return type




       
    def get_xml(self):
        return self.xml









