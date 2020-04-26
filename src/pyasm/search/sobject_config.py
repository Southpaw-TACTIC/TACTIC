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

__all__ = [ 'SObjectConfigException', 'SObjectConfig', 'SObjectAttr', 'DecoratorAttr', 'DateAttr']


import string, os, re, time

from pyasm.common import *



class SObjectConfigException(Exception):
    pass





class SObjectConfig(Base):
    "base class for all widgets that use the config file for parameters"""
    def __init__(self, file_path):
        self.xml = Xml()
        self.xml.read_file(file_path)

    # search related functions

    def get_order_by(self):
        xpath = "config/search/order-by"
        return self.xml.get_value(xpath)

    def get_directory(self):
        xpath = "config/search/directory"
        return self.xml.get_value(xpath)


    def get_property(self, property):
        '''get arbitrary attributes'''
        xpath = "config/properties/%s" % property
        return self.xml.get_value(xpath)



    # attributes related functions

    def get_attr_names(self):
        xpath = "config/attrs/attr/@name"
        attr_list = self.xml.get_values(xpath)
        return attr_list

    def _get_attr_options(self, attr_name):
        xpath = "config/attrs/attr[@name='%s']/*" % attr_name
        option_nodes = self.xml.get_nodes(xpath)
        return option_nodes





    def create_attr(self, attr_name, sobject=None):
        """dynamically create the widget"""
        xpath = "config/attrs/attr[@name='%s']/@class" % attr_name
        class_path = self.xml.get_value(xpath)

        if class_path == "":
            class_path = "SObjectAttr"

        args = [attr_name, sobject]
        attr = Common.create_from_class_path(class_path, args)

        # get all of the options
        option_nodes = self._get_attr_options(attr_name)
        for node in option_nodes:
            option_name = Xml.get_node_name(node)
            option_value = Xml.get_node_value(node)
            attr.set_option(option_name, option_value)

        # initialize the attr
        attr.init()

        # give a chance to the newly created attr to check
        # for security
        if not attr.check_security():
            return None

        return attr



    ####
    # static methods
    ####

    # cache xml files in a globa data structure
    def get_by_search_type(search_type_obj, database):

        search_type = search_type_obj.get_base_key()

        # This is here to prevent an infinite loop
        if search_type == "sthpw/search_object":
            return

        if search_type == None:
            search_type = "sthpw/search_object"
            

        # if it already exists, then get the cached data
        cache_name = "SObjectConfig:sobject_configs_list"
        config_list = Container.get(cache_name)
        if config_list == None:
            config_list = {}
            Container.put(cache_name, config_list)

        if config_list.has_key(search_type):
            return config_list[search_type]


        # get the real search_type implementation to find the paths
        tmp = search_type.split("/")
        if len(tmp) == 2:
            sub_dir = tmp[0]
            search_key = tmp[1]
        else:
            sub_dir = tmp[0]
            search_key = tmp[2]

        filename = "%s-conf.xml" % search_key

        config = None


        # start with the site directory for overrides
        env = Environment.get_env_object()
        site_dir = env.get_site_dir()


        # This assumes that the context and the database are the same
        #context = search_type_obj.get_database()
        context = database
        # build up the file path and load in the config file
        if context == "sthpw":
            #from search import SearchType
            #project = SearchType.get_global_project()
            from pyasm.biz import Project
            project_code = Project.get_global_project_code()
            conf_path = "%s/sites/%s/config/sthpw/sobject/%s" \
                % (site_dir,project_code,filename)
        else:
            conf_path = "%s/sites/%s/config/sobject/%s" \
                % (site_dir,context,filename)


        if os.path.exists(conf_path):
            # load in the config path
            config = SObjectConfig( conf_path );

        else:

            # build the path from the site directory
            env = Environment.get_env_object()
            site_dir = env.get_site_dir()
            conf_path = "%s/sites/%s/config/sobject/%s" \
                % (site_dir,sub_dir,filename)


        if os.path.exists(conf_path):
            # load in config file
            config = SObjectConfig( conf_path );

        else:
            base_dir = Environment.get_install_dir()
            conf_path = "%s/src/config/%s/sobject/%s" \
                % (base_dir, sub_dir,  filename)

            if os.path.exists(conf_path):
                # load in config file
                config = SObjectConfig( conf_path );

    
        # store in container
        config_list[search_type] = config

        return config

    get_by_search_type = staticmethod(get_by_search_type)







class SObjectAttr(Base):
    '''defines the base class for all attributes that sobjects contain'''

    def __init__(self, name, sobject):
        self.name = name
        self.sobject = sobject
        self.options = {}

    
    def init(self):
        '''initialization function called after all the options have been
        set.  Implementations should override this if needed'''
        pass


    def set_name(self, name):
        self.name = name


    def set_sobject(self, sobject):
        '''all attributes know about their parent sobject and make use of
        the data as needed'''
        self.sobject = sobject


    def set_value(self, value):
        self.sobject.set_value( self.name, value )

    def get_value(self):
        return self.sobject.get_value( self.name )

    def get_xml_value(self):
        if self.sobject.has_value(self.name):
            return self.sobject.get_xml_value( self.name )
        else:
            from pyasm.biz import Snapshot
            return Snapshot.get_latest_by_sobject(\
                    self.sobject).get_xml_value( self.name )


    def get_web_display(self):
        '''function that gets display for viewing on the web'''
        return self.get_value().capitalize()


    def set_option(self,name,value):
        self.options[name] = value

    def get_option(self,name):
        value = self.options.get(name)
        if not value:
            return ""
        else:
            return value



    def check_security(self):
        return True





class DecoratorAttr(SObjectAttr):

    def get_value(self):
        original_attr_name = self.get_option("original")
        attr = self.sobject.attr(original_attr_name)
        return attr.get_value()




class DateAttr(SObjectAttr):

    def get_value(self):
        timestamp = self.sobject.get_value(self.name)
        timestamp = str(timestamp)
        if not timestamp:
            return ""

        date = Date(db_date=timestamp)
        return date.get_display_time()



