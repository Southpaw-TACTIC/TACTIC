############################################################
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

__all__ = ['WidgetConfigException', 'WidgetConfig', 'WidgetConfigView', 'WidgetConfigTestCmd']

import sys, os, types

from pyasm.common import *
from pyasm.search import WidgetDbConfig, SObjectDefaultConfig, SearchType, Search, DbResource
from pyasm.web import *
from pyasm.command import Command

class WidgetConfigException(TacticException):
    pass


class WidgetConfig(Base):
    '''Class for all widgets that use the config file for parameters.
    It encapsulates where the file should be located.  This could be either
    the filesystem or the database, depending on the sobject.
    '''


    #def __del__(my):
    #    print "DELETING config: ", my


    
    def __init__(my, view=None, file_path=None, xml=None, __get__=False, use_cache=True, state=None):
        if not __get__:
            raise WidgetConfigException("Do not instantiate WidgetConfig directly.  Use WidgetConfig.get()")

        my.file_path = file_path

        if file_path != None:
            my.xml = Xml()
            my.xml.read_file(file_path, cache=use_cache)

        elif xml:
            if type(xml) in types.StringTypes:
                my.xml = Xml()
                my.xml.read_string(xml)
            else:
                my.xml = xml
        else:
            raise WidgetConfigException("Must supply either file_path or xml")

        my.view = view
        if view and view.find('@') != -1:
            my.view_as_attr = True
            my.view_xpath = "view[@name='%s']"%view
        else:
            my.view_as_attr = False
            my.view_xpath = view

        my.state = state



    def get(view=None, file_path=None, xml=None, use_cache=True):
        '''FIXME: should view be allowed to equal None?'''
        if xml:
            config = WidgetConfig(view, file_path, xml, __get__=True)
            return config

        config_cache = Container.get("WidgetConfig:config_cache")
        if config_cache == None:
            config_cache = {}
            Container.put("WidgetConfig:config_cache", config_cache)


        key = "%s:%s" % (view, file_path)
        config = config_cache.get(key)
        if config:
            return config

        
        config = WidgetConfig(view, file_path, xml, __get__=True, use_cache=use_cache)
        config_cache[key] = config

        return config
    get = staticmethod(get)


    def get_file_path(my):
        return my.file_path

    def set_file_path(my, file_path):
        my.file_path = file_path


    def has_view(my, view=None):
        # check that this view actually exists in this file

        if not view:
            view = my.view
        if view.find('@') !=-1:
            xpath = "config/view[@name='%s']"%view
        else:
            xpath = "config/%s"%view
        node = my.xml.get_node(xpath)
        if node is not None:
            return True
        else:
            return False

    def set_view(my, view):
        my.view = view
        if view and view.find('@') != -1:
            my.view_as_attr = True
            my.view_xpath = "view[@name='%s']"%view
        else:
            my.view_as_attr = False
            my.view_xpath = view


    def get_view(my):
        return my.view

    def get_xml(my):
        return my.xml

    def to_string(my):
        return my.xml.get_xml()


    def get_all_views(my):
        '''get all of the view defined in this config xml'''
        xpath = "config/*"
        view_nodes = my.xml.get_nodes(xpath)
        views = []
        for view in view_nodes:
            views.append( my.xml.get_node_name(view) )
        return views


    def get_view_node(my, view=None):
        if not view:
            view = my.view

        if view.find('@') != -1:
            return my.get_view_attr_node(view)

        xpath = "config/%s" % view

        node = my.xml.get_node(xpath)
        return node

    def get_view_attr_node(my, view=None):
        if not view:
            view = my.view

        xpath = "config/view[@name='%s']" %view 
        node = my.xml.get_node(xpath)
        return node



    def get_view_attributes(my):
        node = my.get_view_node()
        if node is not None:
            # get all of the attributes
            node_attrs = Xml.get_attributes(node)
            return node_attrs
        else:
            return {}


    def get_view_attribute(my, name):
        attrs = my.get_view_attributes()
        return attrs.get(name)



    def get_element_attributes(my, element_name):
        '''get the name of each element in a list '''
        # we have a list of configs ... go through each to find the element
        node_attrs = {}
        node = my.get_element_node(element_name)
        if node != None:
            node_attrs = Xml.get_attributes(node)
        return node_attrs





    def get_element_node(my, element_name):
        xpath = "config/%s/element[@name='%s']" % (my.view_xpath, element_name)
        node = my.xml.get_node(xpath)
        return node

    def import_element_node(my, element_name):
        node = my.get_element_node(element_name)
        imported_node = None
        if node is not None:
            imported_node = my.xml.get_doc().importNode(node)
        return imported_node 

    def get_element_xml(my, element_name):
        node = my.get_element_node(element_name)
        if node is None:
            return ''
        return my.xml.to_string(node)



    def get_element_titles(my):
        '''get the title of each element in a list. If not specified, 
        it defaults to the name of the element'''
        # the order dictates the order of preference
        return my.get_element_names(type='', attrs=['title'])

    def get_element_widths(my):
        '''get the width of each element in a list.'''
        # the order dictates the order of preference
        return my.get_element_names(type='', attrs=['width','name'])

    def get_element_descriptions(my):
        '''get the descriptions of each element in a list'''
        # the order dictates the order of preference
        return my.get_element_names(type='', attrs=['description'])



    def get_element_names(my, type='', attrs=['name']):
        '''get the name of each element in a list '''
        # NOTE: have to do this long winded logic because 4Suite doesn't
        # appear to support the != operator
        xpath = "config/%s/element" % my.view_xpath
        nodes = my.xml.get_nodes(xpath)
        ordered_names = []

        # get them all
        for node in nodes:
            for attr_name in attrs:
                name = Xml.get_attribute(node, attr_name)
                if name:
                    ordered_names.append(name)
                    break
            else:
                ordered_names.append("")


        
        return ordered_names


    def get_default_base(my):
        '''gets the default base that this view is based on'''
        xpath = "config/%s/@default" % my.view_xpath;
        default_base = my.xml.get_value(xpath)
        if default_base == "":
            # defining the main types of config snippet
            if my.view == "edit":
                return "edit"
            elif my.view == "insert":
                return "insert"
            else:
                return "table"
        else:
            return default_base


    def get_handler(my, element_name, type):
        assert type != None
        assert element_name != None

        xpath = "config/%s/element[@name='%s']/%s/@class" % (my.view_xpath, element_name, type)
        value = my.xml.get_value(xpath)
        if not value:
            xpath = "config/%s/element[@name='%s']/%s/@widget" % (my.view_xpath, element_name, type)
            key = my.xml.get_value(xpath)
            if key:
                from tactic.ui.common import WidgetClassHandler
                handler = WidgetClassHandler()
                value = handler.get_display_handler(key)
        return value

  

    def get_widget_key(my, element_name, type='display'):
        assert element_name != None

        xpath = "config/%s/element[@name='%s']/%s/@widget" % (my.view_xpath, element_name, type)
        return my.xml.get_value(xpath)



   
    def get_display_handler(my, element_name):
        assert element_name != None

        xpath = "config/%s/element[@name='%s']/display/@class" % (my.view_xpath, element_name)
        value = my.xml.get_value(xpath)
        if not value:
            xpath = "config/%s/element[@name='%s']/display/@widget" % (my.view_xpath, element_name)

           
            key = my.xml.get_value(xpath)
            
            if key:
                from tactic.ui.common import WidgetClassHandler
                handler = WidgetClassHandler()
                value = handler.get_display_handler(key)
                
        return value


    def get_action_handler(my, element_name):
        assert element_name != None

        xpath = "config/%s/element[@name='%s']/action/@class" % (my.view_xpath, element_name)
        return my.xml.get_value(xpath)


    def get_display_options(my, element_name):
        return my.get_options(element_name, 'display')

    def get_web_options(my, element_name):
        return my.get_options(element_name, 'web')



    # NOTE: Leaving old implementation until we can reproduce get_options()
    # perfectly
    def get_options(my, element_name, element_child_name):
        assert element_name != None

        xpath = "config/%s/element[@name='%s']/%s" \
                % (my.view_xpath,element_name, element_child_name)

        node = my.xml.get_node(xpath)
        if node == None:
            return {}

        # NOTE: special case for custom layout widget
        handler = my.xml.get_attribute(node, "class")


        has_config = False
        if handler:
            try:
                from pyasm.common import Common
                statement = Common.get_import_from_class_path(handler)
                exec(statement)

                has_config = eval("%s.has_config()" % handler)
            except:
                pass


        if handler == 'tactic.ui.panel.CustomLayoutWdg':
            children = my.xml.get_children(node)
            values = {}
            for child in children:
                name = my.xml.get_node_name(child)
                if name == 'html':
                    value = my.xml.to_string(child)
                    value = value.replace("<html>", "")
                    value = value.replace("</html>", "")
                    value = value.strip()
                else:
                    value = my.xml.get_node_value(child)
                    value = value.replace("&amp;", "&")
                values[name] = value
                 
        elif has_config or handler in ['tactic.ui.container.TabWdg', 'tactic.ui.panel.EditWdg', 'tactic.ui.container.ContentBoxWdg']:
            children = my.xml.get_children(node)
            values = {}
            for child in children:
                name = my.xml.get_node_name(child)
                if name == 'config':
                    value = my.xml.to_string(child)
                    if handler.endswith(".EditWdg"):
                        value = value.replace("<config>", "<config><tab layout='%s'>" % handler)
                    else:
                        value = value.replace("<config>", "<config><tab>")
                    value = value.replace("</config>", "</tab></config>")
                    value = value.strip()
                    name = 'config_xml'

                    # convert all & back to &amp;
                    value = value.replace("&", "&amp;")
                else:
                    value = my.xml.get_node_value(child)
                    value = value.replace("&amp;", "&")
                values[name] = value
        else:
            values = my.xml.get_recursive_node_values(node)
        #print xpath
        return values




    def get_action_options(my, element_name):
        assert element_name != None

        xpath = "config/%s/element[@name='%s']/action/*" % (my.view_xpath, element_name)
        option_nodes = my.xml.get_nodes(xpath)
        
        values = {}

        for node in option_nodes:
            #value = node.firstChild.nodeValue
            value = Xml.get_node_value(node)
            name = Xml.get_node_name(node)
            values[name] = value

        return values



    def get_type(my, element_name):
        xpath = "config/%s/element[@name='%s']/@type" % (my.view_xpath, element_name)
        type = my.xml.get_value(xpath)
        if not type:
            xpath = "config/%s/element[@name='%s']/@type" % ("definition", element_name)
            type = my.xml.get_value(xpath)

        return type


    #def get_dependent_attr(my, element_name):
    #    '''get dependent attribute(s) of an element for an sobject. Delimited by commas'''
    #    xpath = "config/%s/element[@name='%s']/@depend" % (my.view,element_name)
    #    type = my.xml.get_value(xpath)
    #    if not type:
    #        xpath = "config/%s/element[@name='%s']/@depend" % ("definition",element_name)
    #        type = my.xml.get_value(xpath)
    #    return type


    def get_display_widget(my, element_name, extra_options={}):
        display_handler = my.get_display_handler(element_name)
        if not display_handler:
            return None

        display_options = my.get_display_options(element_name)
        for name, value in extra_options.items():
            display_options[name] = value


        widget = Common.create_from_class_path(display_handler, [], display_options)
        from input_wdg import BaseInputWdg
        if isinstance(widget, BaseInputWdg):
            widget.set_options(display_options)

        widget.set_name(element_name)
        return widget



    def alter_xml_element(my, element_name, config_xml=None, node=None):
        '''alter an element with the config_xml to current doc's view.  If it
        does not exist, append it
        '''
        if config_xml:
            xml = Xml(string = config_xml)
            new_root_node = xml.get_root_node()
        elif node != None:
            new_root_node = node
        else:
            raise SetupException()
        view_node = my.get_view_node()
        if view_node == None:
            raise SetupException("The view node is not found for [%s]" %my.view)

        target_node = my.get_element_node(element_name)
        if target_node != None:
            my.xml.replace_child(view_node, target_node, new_root_node)
        else:
            my.xml.append_child(view_node, new_root_node)
        #print my.xml.to_string()



    def remove_xml_element(my, element_name):
        ''' remove node (remember to commit it in the db entry yourself)'''
        view_node = my.get_view_node()
        target_node = my.get_element_node(element_name)
        if target_node != None:
            my.xml.remove_child(view_node, target_node)

    def append_xml_element(my, element_name, config_xml=None, node=None):
        '''append an element with the config_xml to current doc's view
        
        DEPRECATED: use alter_xml_element 
        '''
        my.alter_xml_element(element_name, config_xml=config_xml, node=node)



    def create_widget(class_path, display_options={} ):
        '''dynamically create the widget'''
        element = Common.create_from_class_path(class_path, [], display_options)
        return element

    create_widget = staticmethod(create_widget)



class WidgetConfigView(Base):
    '''Abstracts all the sources of configurations for a particular view'''
    def __init__(my, search_type, view, configs, state=None):
        my.search_type = search_type
        my.view = view
        my.configs = configs

        my.type_cache = {}

        my.state = state
        my.hash_id = Common.generate_random_key()

    def get_view(my):
        return my.view

    def get_xml(my):
        '''returns the raw xml of the first config'''
        if my.configs:
            return my.configs[0].get_xml()
        else:
            return None

    def get_configs(my):
        return my.configs

    def get_config(my):
        '''get first config'''
        if my.configs:
            return my.configs[0]

    def add_config(my, config):
        my.configs.append(config)

    def insert_config(my, index, config):
        my.configs.insert(index, config)

    def get_views(my, layout="TableWdg"):

        views = []

        # list the views from the database
        search = Search("config/widget_config")
        search.add_filter("search_type", my.search_type)
        db_configs = search.get_sobjects()

        # look in the database for the view
        for db_config in db_configs:
            xml = db_config.get_xml_value("config", root='config')
            view_node = xml.get_node("config/*")

            if view_node is None:
                print ("WARNING: Widget config with id [%s] has no view defined" % db_config.get_id())
                continue

            # make a special case for "edit" and "table"
            if view_node is None:
                continue
            node_name = xml.get_node_name(view_node)
            if layout in ["TableLayoutWdg", "TableWdg"] and node_name == "table":
                views.append(node_name)
                continue
            if layout == "EditWdg" and node_name in ["edit","insert","preview"]:
                views.append(node_name)
                continue

            # make sure the node layout matches
            view_layout = xml.get_attribute(view_node, "layout")
            if layout != view_layout:
                continue

            view = db_config.get_value("view")
            views.append(view)


        # look at the first config
        for config in my.configs:
            xml = config.get_xml()
            view_nodes = xml.get_nodes("config/*")
            for view_node in view_nodes:
                # make a special case for "edit" and "table"
                node_name = xml.get_node_name(view_node)
                if layout == "TableWdg" and node_name == "table":
                    views.append(node_name)
                    continue
                if layout == "EditWdg" and node_name in ["edit","insert","preview"]:
                    views.append(node_name)
                    continue

                # make sure the node layout matches
                view_layout = xml.get_attribute(view_node, "layout")

                if layout != view_layout:
                    continue

                views.append(node_name)

            break

        
        return views



    def get_view_attributes(my):
        '''get all the view level attributes'''
        attrs = {}

        for config in my.configs:
            # config could be WidgetConfigView and causes an exception
            # check for it and then continue if that's needed
            node = config.get_view_node()
            if node is not None:
                # get all of the attributes
                node_attrs = Xml.get_attributes(node)
                for name, value in node_attrs.items():
                    # only add if the name is not already set
                    if not attrs.has_key(name):
                        attrs[name] = value

        return attrs

  


    def get_element_widths(my):
        '''get the width of each element in a list.'''
        # the order dictates the order of preference
        return my.get_element_names(type='', attrs=['width'], include_definition=True)




    def get_element_titles(my):
        '''get the title of each element in a list. If not specified, 
        it defaults to the name of the element'''
        #return my.get_element_names(type='', attrs=['title'])
        # the following retrieves titles recursively instead of just getting the current level
        titles = []
        element_names = my.get_element_names(type='')
        for element_name in element_names:
            title = ''
            for config in my.configs:
                # get the element node
                node = config.get_element_node(element_name)
                if node is None:
                    continue

                title = Xml.get_attribute(node, 'title')
                if title:
                    titles.append(title)
                    break
            if not title:     
                title = Common.get_display_title(element_name)
                titles.append(title)
      
        #titles = [_(x) for x in titles]
        return titles

        


    def get_element_descriptions(my):
        '''get the title of each element in a list.'''
        titles = []
        element_names = my.get_element_names(type='')
        for element_name in element_names:
            title = ''
            for config in my.configs:
                # get the element node
                node = config.get_element_node(element_name)
                if node is None:
                    continue

                title = Xml.get_attribute(node, 'description')
                if title:
                    titles.append(title)
                    break
            if not title:     
                title = element_name.replace("_", " ")
                title = title.capitalize()
                titles.append(title)
        
        return titles

        



    def get_element_names(my, type='', attrs=['name'], include_definition=False):
        if not my.configs:
            return []

        # if this view is a definition view, then the element names are those
        # of the definition
        if my.view in ["definition", 'default_definition']:
            for config in my.configs:
                if config.get_view() in ['definition', 'default_definition']:
                    element_names = config.get_element_names(type, attrs)
                    if element_names:
                        return element_names
            return []

        # look at the first config
        element_names = []
        for config in my.configs:

            # to get the element names, skip all of the definition configs
            if not include_definition and config.get_view() in ["definition", 'default_definition']:
                continue

            #element_names = WidgetConfig.get_element_names(config, type, attrs)
            element_names = config.get_element_names(type, attrs)
            if element_names:
                break

            if config.has_view():
                break


        return element_names


    def get_element_xml(my, element_name):
        for config in my.configs:
            element_xml = config.get_element_xml(element_name)
            if element_xml:
                return element_xml




    def get_definition_config(my):
        '''gets the first definition config'''
        for config in my.configs:
            if config.get_view() == "definition":
                return config
        else:
            # if no definition has been found, use the default
            #config = SObjectDefaultConfig(my.search_type, my.view)
            #return config
            return None


    def get_layout_handler(my):
        attributes = my.get_view_attributes()
        layout = attributes.get('layout')
        if not layout:
            # handle some hard coded defaults
            if my.view in ["edit", "insert", "preview"]:
                layout = 'tactic.ui.panel.EditWdg'
            else:
                layout = 'tactic.ui.panel.TableLayoutWdg'

        # Some backward compatibility
        else:
            if layout == "EditWdg":
                layout = 'tactic.ui.panel.EditWdg'
            elif layout == 'TableWdg':
                layout = 'tactic.ui.panel.TableLayoutWdg'
            elif layout == 'TableLayoutWdg':
                layout = 'tactic.ui.panel.TableLayoutWdg'
            elif layout == 'OldTableLayoutWdg':
                layout = 'tactic.ui.panel.OldTableLayoutWdg'
        return layout



    #
    # Generalized methods for building defined handlers in an element
    #

    def get_handler(my, element_name, type):
        '''for the handler, go through each config file and
        look for a definition.  Each config file may also have a "definition"
        view as well.'''
        assert element_name

        # we have a list of configs ... go through each to find the element
        handler = ""
        for config in my.configs:

            # get the handler
            handler = config.get_handler(element_name)
            if handler:
                break

        '''
        if not handler:
            layout = my.get_layout_handler()

            import_expr = Common.get_import_from_class_path(layout)
            exec( import_expr)
            handler = eval('%s.get_default_display_handler(element_name)'% layout)
        '''
        return handler

    

   
    def get_options(my, element_name, type):
        '''generic function to get the options for the widget'''
        assert element_name

        cache = Container.get("WidgetConfigView:%s_options_cache" % type)
        if cache == None:
            cache = {}
            Container.put("WidgetConfigView:%s_options_cache" % type, cache)

        key = "%s|%s" % (my, element_name)
        options = cache.get(key)
        if options != None:
            return options


        # we have a list of configs ... go through each to find the element
        options = {}
        for config in my.configs:

            # special consideration for edit and edit defintion views
            # for backwards compatibility
            if type == 'edit' and config.get_view() in ['edit','edit_definition', 'default_definition']:
                options = config.get_options(element_name, "display")
            else:
                options = config.get_options(element_name, type)

            if options:
                break

        cache[key] = options
        return options



    #
    # Specialized methods for getting specific handlers in an element.
    # Eventually, these will make use of the above generalized methods
    #
    def get_display_handler(my, element_name):
        '''for the display handler, go through each config file and
        look for a definition.  Each config file may also have a "definition"
        view as well.'''
        assert element_name

        # we have a list of configs ... go through each to find the element
        display_handler = ""
        for config in my.configs:
            display_handler = config.get_display_handler(element_name)
            if display_handler:
                break

        if not display_handler:
            layout = my.get_layout_handler()

            import_expr = Common.get_import_from_class_path(layout)
            exec( import_expr)
            display_handler = eval('%s.get_default_display_handler(element_name)'% layout)

        return display_handler



    def get_widget_key(my, element_name, type='display'):
        '''get the short for of the display widget.  This is often used
        instead of a full python class.  This method does not translate the
        name into a python class, but returns the actual value in the definition
        '''
        assert element_name

        # we have a list of configs ... go through each to find the element
        widget_key = ""
        for config in my.configs:
            widget_key = config.get_widget_key(element_name, type)
            if widget_key:
                break
            display_handler = config.get_handler(element_name, type)
            if display_handler:
                break

        return widget_key


    

    def get_web_options(my, element_name):
        web_options = {}
        for config in my.configs:
            # get the web handler
            web_options = config.get_web_options(element_name)
            if web_options:
                break

        return web_options

    def get_display_options(my, element_name):
        '''for the display handler, go through each config file and
        look for a definition.  Each config file may also have a "definition"
        view as well.'''
        assert element_name

        cache = Container.get("WidgetConfigView:display_options_cache")
        if cache == None:
            cache = {}
            Container.put("WidgetConfigView:display_options_cache", cache)

        key = "%s|%s" % (my.hash_id, element_name)
        display_options = cache.get(key)
        if display_options != None:
            return display_options


        # we have a list of configs ... go through each to find the element
        display_options = {}
        for config in my.configs:
            # get the display handler
            display_options = config.get_display_options(element_name)
            
            # if there is a state defind, then replace any expressions
            # DEPRECATED
            """
            if my.state:
                for name, value in display_options.items():
                    if isinstance(value, basestring):
                        if value.startswith("{") and value.endswith("}"):
                            value = Search.eval(value, single=True, state=my.state)
                            display_options[name] = value

                    else:
                        display_options[name] = value
            """


            if display_options:
                break

        cache[key] = display_options
        return display_options





    def get_edit_handler(my, element_name):
        '''for the edit handler, go through each config file and
        look for a definition.
        '''
        assert element_name

        # we have a list of configs ... go through each to find the element
        edit_handler = ""
        for config in my.configs:

            edit_handler = config.get_handler(element_name, "edit")
            # old method where we use the display tag in both "edit" and
            # "edit_definition" views
            if not edit_handler and my.get_view() in ['edit','edit_definition','default_definition']:
                edit_handler = config.get_handler(element_name, "display")

            if edit_handler:
                break

        if not edit_handler:
            layout = my.get_layout_handler()

            import_expr = Common.get_import_from_class_path(layout)
            exec( import_expr)
            # NOTE: this stays as get_default_display_handler for now
            edit_handler = eval('%s.get_default_display_handler(element_name)'% layout)

        return edit_handler



    def get_handler(my, element_name, type):
        assert type in ['edit', 'table']
        if type == 'edit':
            return my.get_edit_handler(element_name)
        elif type == 'display':
            return my.get_display_handler(element_name)

 



    def get_element_node(my, element_name, prefer_child_nodes=False):
        '''get the element_node that has a definition. 
         @param: prefer_child_nodes - If set to True, it would prefer a node with childNodes
            like <display/>'''
        # we have a list of configs ... go through each to find the element
        assert element_name
        second_choices = []
        for config in my.configs:
            # get the element node
            node = config.get_element_node(element_name)
            if node is None:
                continue


            attributes = config.get_element_attributes(element_name)
            keys = attributes.keys()
            # this condition is questionable. Sometimes an element with a width attribute does
            # not actually have the desired definition
            xml = config.get_xml()
            child_nodes = xml.get_children(node)
            #if len(node.childNodes):
            if len(child_nodes):
                return node
            if len(keys) > 1:
                if prefer_child_nodes: 
                    second_choices.append(node)
                else:
                    return node
        # return the first node with more than 1 attribute
        if second_choices:
            return second_choices[0]

        # just return the first one
        if my.configs:       
            return my.configs[0].get_element_node(element_name)
        else:
            return None



    def get_element_attributes(my, element_name):
        '''get the name of each element in a list '''
        # we have a list of configs ... go through each to find the element
        attrs = {}
        for config in my.configs:
            # get the element node
            node = config.get_element_node(element_name)
            if node is not None:
                # get all of the attributes
                node_attrs = Xml.get_attributes(node)
                for name, value in node_attrs.items():
                    # only add if the name is not already set
                    if not attrs.has_key(name):
                        attrs[name] = value

        return attrs

    def get_element_title(my, element_name):
        '''get the name of each element in a list '''
        # we have a list of configs ... go through each to find the element
        node_title = ''
        for config in my.configs:
            # get the element node
            node = config.get_element_node(element_name)
            if node is not None:
                # get all of the attributes
                node_title = Xml.get_attribute(node, 'title')
                if not node_title:
                    node_title = Common.get_display_title(element_name)
                else:
                    break
            else:
                node_title = Common.get_display_title(element_name)

        return node_title


    def get_element_description(my, element_name):
        '''get the name of each element in a list '''
        # we have a list of configs ... go through each to find the element
        node_desc = ''
        for config in my.configs:
            # get the element node
            node = config.get_element_node(element_name)
            if node is not None:
                # get all of the attributes
                node_desc = Xml.get_attribute(node, 'description')
                if node_desc:
                    break
            else:
                node_desc = Common.get_display_title(element_name)

        return node_desc



    def get_action_handler(my, element_name):
        '''for the action handler, go through each config file and
        look for a definition.'''
        assert element_name

        # we have a list of configs ... go through each to find the element
        action_handler = ""
        for config in my.configs:
            # get the action handler
            action_handler = config.get_action_handler(element_name)
            if action_handler:
                break

        return action_handler


    def get_action_options(my, element_name):
        '''for the action handler, go through each config file and
        look for a definition.'''
        assert element_name

        # we have a list of configs ... go through each to find the element
        action_handler = ""
        for config in my.configs:
            # get the action options
            action_options = config.get_action_options(element_name)
            if action_options:
                break

        return action_options


    def get_type(my, element_name):
        type = my.type_cache.get(element_name)
        if type != None:
            return type

        for config in my.configs:
            # get the action options
            type = config.get_type(element_name)
            if type:
                break
      
        my.type_cache[element_name] = type
        
        return type

    def get_dependent_attr(my, element_name):
        '''get dependent attribute(s) of an element for an sobject'''
        #type = my.type_cache.get(element_name)
        #if type != None:
        #    return type

        for config in my.configs:
            # get the action options
            attr = config.get_dependent_attr(element_name)
            if attr:
                break
      
        #my.type_cache[element_name] = type
        
        return attr

    def get_display_widget(my, element_name, recurse=False, extra_options=None, kbd_handler=True):
        #if not recurse and element_name not in my.get_element_names():
        #    return None
        display_handler = my.get_display_handler(element_name)
        display_options = my.get_display_options(element_name)
        if extra_options:
            for name, value in extra_options.items():
                display_options[name] = value

        # if a display handler is defined in the config, the build it.
        if display_handler:
            try:
                widget = Common.create_from_class_path(display_handler, [], display_options)
                # backward compatible
                from input_wdg import BaseInputWdg
                from file_wdg import ThumbWdg
                if isinstance(widget, BaseInputWdg) or isinstance(widget, ThumbWdg):
                    widget.set_options(display_options)
            except Exception, e:
                print "widget error: ", e
                # TableLayoutwdg can't be created in 2 steps like this
                # should raise the error in this case
                if display_handler in ['tactic.ui.panel.TableLayoutWdg','tactic.ui.panel.FastTableLayoutWdg', 'tactic.ui.panel.OldTableLayoutWdg']:
                    raise
                widget = Common.create_from_class_path(display_handler)
                from input_wdg import BaseInputWdg
                if isinstance(widget, BaseInputWdg):
                    widget.set_options(display_options)

        elif my.search_type == "CustomLayoutWdg":
            raise WidgetConfigException("No display handler defined")
        else:
            # have the layout build it (ie EditWdg or TableLayoutWdg)
            element_type = my.get_type(element_name)
            if not element_type:
                #search_type_obj = SearchType.get(my.search_type)
                element_type = SearchType.get_tactic_type(my.search_type, element_name)

            layout = my.get_layout_handler()
            import_expr = Common.get_import_from_class_path(layout)
            exec( import_expr)
            widget = eval('%s.get_default_display_wdg(element_name, display_options, element_type, kbd_handler)'% layout)

        if widget:
            widget.set_name(element_name)

        return widget


    def get_widget(my, element_name, type="display", extra_options=None):
        '''more generalized function to build a widget from a config'''

        handler = my.get_handler(element_name, type)
        options = my.get_options(element_name, type)
        if extra_options:
            for name, value in extra_options.items():
                options[name] = value

        # if a handler is defined in the config, then build it.
        if handler:
            try:
                widget = Common.create_from_class_path(handler, [], options)
                # backward compatible
                from input_wdg import BaseInputWdg
                if isinstance(widget, BaseInputWdg):
                    widget.set_options(options)
            except:
                # FIXME: why is this necessary??
                # TableLayoutwdg can't be created in 2 steps like this
                # should raise the error in this case
                if handler =='tactic.ui.panel.TableLayoutWdg':
                    raise
                widget = Common.create_from_class_path(handler)
                widget.set_options(options)

        elif my.search_type == "CustomLayoutWdg":
            raise WidgetConfigException("No handler defined")
        else:
            # have the layout build it (ie EditWdg or TableLayoutWdg)
            element_type = my.get_type(element_name)
            if not element_type:
                #search_type_obj = SearchType.get(my.search_type)
                #element_type = search_type_obj.get_tactic_type(element_name)
                element_type = SearchType.get_tactic_type(my.search_type, element_name)

            layout = my.get_layout_handler()
            import_expr = Common.get_import_from_class_path(layout)
            exec( import_expr)
            widget = eval('%s.get_default_display_wdg(element_name, options, element_type)'% layout)

        if widget:
            widget.set_name(element_name)

        return widget





    #
    # Static functions
    #


    #
    # TEST!!!! This is not for use!!!  Trying to prototype simplifying the
    # logic to find the config definition
    #
    def get_by_edit_search_type(search_type, view, use_cache=True):

        # get the search type
        if isinstance(search_type, SearchType):
            search_type_obj = search_type
        else:
            search_type_obj = SearchType.get(search_type)
        search_type = search_type_obj.get_base_key()


        # see if there is a cache
        config_cache = {}
        if use_cache:
            config_cache = Container.get("WidgetConfigView:config_cache")
            if config_cache == None:
                config_cache = {}
                Container.put("WidgetConfigView:config_cache", config_cache)
            widget_config_view = config_cache.get("%s:%s" % (search_type, view) ) 
            if widget_config_view:
                return widget_config_view



        # get all the configs relevant to this search_type
        configs = []


        # Look in the database for the views
        for v in [view, "definition", "edit_definition"]:
            db_config = WidgetDbConfig.get_by_search_type(search_type,v)
            if db_config:
                xml = db_config.get_xml_value("config")
                config = WidgetConfig.get(v, xml=xml)
                if config.has_view():
                    configs.append(config)



        # build name of the files to look in
        sub_dir = search_type_obj.get_value('namespace')
        tmp = search_type_obj.get_base_key().split("/")
        if len(tmp) == 2:
            search_key = tmp[1]
        else:
            # ignore the schema for config files for now
            search_key = tmp[2]

        filename = "%s-conf.xml" % search_key
        default_filename = "DEFAULT-conf.xml"


        # look in the following paths
        conf_paths = []
        conf_paths.append( "%s/src/config2/search_type/widget/%s/%s" \
            % (base_dir, sub_dir, filename) )
        conf_paths.append( "%s/src/config2/search_type/widget/%s/%s" \
            % (base_dir, sub_dir, default_file_name) )
        conf_paths.append( "%s/src/config2/search_type/widget/prod/%s" \
            % (base_dir, default_file_name) )

        for conf_path in conf_paths:
            if os.path.exists(conf_path):
                # load in config file
                config = WidgetConfig.get(view, internal_conf_path)
                if config.has_view():
                    configs.append(config)

        # make a default one. Needed for custom made search type
        default = SObjectDefaultConfig(search_type, view)
        xml = default.get_xml()
        config = WidgetConfig.get(view, xml=xml)





    
    def get_by_search_type(search_type, view, use_cache=True, local_search=False):
        '''gets all the widget configs that have the view asked for
        @keyparam: 
        use_cache - enable caching
        local_search - if True, it skips the initial db search'''
        assert search_type
        assert view

        #assert search_type.startswith("sthpw/") or search_type.find("?") != -1

        full_search_type = search_type
        if isinstance(search_type, SearchType):
            search_type_obj = search_type
        else:
            search_type_obj = SearchType.get(search_type)
        base_search_type = search_type_obj.get_base_key()
        from pyasm.biz import Project
        search_type = Project.get_full_search_type(full_search_type)

        # see if there is a cache
        config_cache = {}
        
        if use_cache:
            config_cache = Container.get("WidgetConfigView:config_cache")
            if config_cache == None:
                config_cache = {}
                Container.put("WidgetConfigView:config_cache", config_cache)
            widget_config_view = config_cache.get("%s:%s" % (search_type, view) ) 
            if widget_config_view:
                return widget_config_view


        sub_dir = search_type_obj.get_value('namespace')
        tmp = search_type_obj.get_base_key().split("/")
        if len(tmp) == 2:
            #sub_dir = tmp[0]
            search_key = tmp[1]
        else:
            # ignore the schema for config files for now
            #sub_dir = tmp[0]
            search_key = tmp[2]


        # get all the configs relevant to this search_type
        configs = []
       

        # build the standard name
        filename = "%s-conf.xml" % search_key
        default_filename = "DEFAULT-conf.xml"



        #
        # DEPRECATED: this should be deprectated, but it is still heavily
        # used
        #


        # temp addition starts
        # start with the site directory for overrides
        env = Environment.get_env_object()
        site_dir = env.get_site_dir()


        # This assumes that the context and the database are the same
        context = search_type_obj.get_database()

        # build up the file path and load in the config file
        # DEPRECATED: looking in the sites folder is deprecated
        conf_path = ''
        if context == "sthpw":
            from pyasm.biz import Project
            project = Project.get_global_project_code()
            conf_path = "%s/sites/%s/config/sthpw/widget/%s" \
                % (site_dir,project,filename)
        else:
            conf_path = "%s/sites/%s/config/widget/%s" \
                % (site_dir,context,filename)
        if os.path.exists(conf_path):
            # load in config file
            print "WARNING: using deprecated sites folder to store config file"
            config = WidgetConfig.get(view, conf_path)
            if config.has_view():
                configs.append(config)


        # look in the TACTIC directory
        base_dir = Environment.get_install_dir()
        internal_conf_path = "%s/src/config2/search_type/widget/%s/%s" \
            % (base_dir, sub_dir, filename)


        default_definition = "definition"
        # this determines at what point we need to append the default defnition config and ALL config
        # it auto switches between defintion or edit_definition, there is no need to hardcode edit_definition

        db_definition_found = False
        # look in the database for the view
        if not local_search:
            db_config = WidgetDbConfig.get_by_search_type(search_type,view)
            # if no insert defined in db or internal conf, resort to edit
            if not db_config and view =='insert':
                if os.path.exists(internal_conf_path):
                    config = WidgetConfig.get(view, internal_conf_path, use_cache=use_cache)
                    if not config.has_view():
                        view = 'edit'
                        db_config = WidgetDbConfig.get_by_search_type(search_type,view)
                else:
                    view = 'edit'
                    db_config = WidgetDbConfig.get_by_search_type(search_type,view)


            if db_config:
                xml = db_config.get_xml_value("config")
                config = WidgetConfig.get(view, xml=xml)
                if config.has_view():
                    configs.append(config)

                    # look at config xml for layout definition
                    attributes = config.get_view_attributes()
                    layout = attributes.get("layout")
                    if layout in ["EditWdg",'tactic.ui.panel.EditWdg'] or view in ['edit','insert','edit_item']:
                        default_definition = 'edit_definition'


            
                    # only add a definition if the db config actualy exists
                    def_db_config = WidgetDbConfig.get_by_search_type(search_type, default_definition)
                    if def_db_config:
                        xml = def_db_config.get_xml_value("config")
                        config = WidgetConfig.get(default_definition, xml=xml)
                        if config.has_view():
                            configs.append(config)
                    

                    # global db definition for all search types
                    def_db_config = WidgetDbConfig.get_by_search_type("ALL", default_definition)
                    if def_db_config:
                        xml = def_db_config.get_xml_value("config")
                        config = WidgetConfig.get(default_definition, xml=xml)
                        if config.has_view():
                            configs.append(config)

                    db_definition_found = True

  

        if os.path.exists(internal_conf_path):
            # load in config file
            config = WidgetConfig.get(view, internal_conf_path, use_cache=use_cache)
            if config.has_view():
                configs.append(config)

            # FIXME: little had to have add_item default to table for now
            """
            if view == 'add_item':
                config = WidgetConfig.get("table", internal_conf_path)
                if config.has_view():
                    configs.append(config)

            """
            if view == 'edit_item':
                config = WidgetConfig.get("edit",  internal_conf_path)
                if config.has_view():
                    configs.append(config)

            # look at config xml for layout definition
            attributes = config.get_view_attributes()
            layout = attributes.get("layout")
            if layout in ["EditWdg",'tactic.ui.panel.EditWdg'] or view in ['edit','insert', 'edit_item']:
                default_definition = 'edit_definition'

            # add db definiition if it hasn't been searched yet
            if not db_definition_found  and not local_search:
                def_db_config = WidgetDbConfig.get_by_search_type(search_type, default_definition)
                if def_db_config:
                    xml = def_db_config.get_xml_value("config")
                    def_db_config = WidgetConfig.get(default_definition, xml=xml)
                    #if def_db_config.has_view():
                    configs.append(def_db_config)

               
            # the internal default definition comes in at this point since it complements the db one
            def_config = WidgetConfig.get(default_definition, xml=config.get_xml())
            def_config.set_file_path( config.get_file_path() )
            if def_config.has_view():
                
                configs.append(def_config)
            
            if not db_definition_found:
                # global db definition for all search types
                def_db_config = WidgetDbConfig.get_by_search_type("ALL", default_definition)
                if def_db_config:
                    xml = def_db_config.get_xml_value("config")
                    config = WidgetConfig.get(default_definition, xml=xml)
                    if config.has_view():
                        configs.append(config)



        # create a definition based on custom widgets
        # NOTE: this is likely too limiting and it messes up the default table
        # This should be added to the default definition
        if view in ['tablex']:

            search = Search("config/widget_config")
            search.add_filter("widget_type", "column")
 
            db_configs = search.get_sobjects()

            if db_configs:
                config = []
                config.append("<config>")
                config.append("<%s>" % view)

                for db_config in db_configs:
                    config_view = db_config.get_value("view")
                    config.append( """
                    <element name="%s">
                      <display class="tactic.ui.table.CustomLayoutElementWdg">
                        <view>%s</view>
                      </display>
                    </element>
                    """ % (config_view, config_view) )
                config.append("</%s>" % view)
                config.append("</config>")

                config = "\n".join(config)

                xml = Xml()
                xml.read_string(config)
                config = WidgetConfig.get(view, xml=xml)
                configs.append(config)




        # make a default one. Needed for custom made search type
        default = SObjectDefaultConfig(search_type, view)
        xml = default.get_xml()
        config = WidgetConfig.get(view, xml=xml)
        config.set_file_path("generated")
        configs.append(config)

        # look at the database for definitions
        if view not in ['edit', 'insert', 'preview']:
            db_config = WidgetDbConfig.get_by_search_type(search_type,default_definition)
            if db_config:
                xml = db_config.get_xml_value("config")
                config = WidgetConfig.get("definition", xml=xml)
                if config.has_view():
                    configs.append(config)

        # look for the default file (for definitions)
        base_dir = Environment.get_install_dir()
        #default_conf_path = "%s/src/config/%s/widget/%s" \
        default_conf_path = "%s/src/config2/search_type/widget/%s/%s" \
            % (base_dir, sub_dir, default_filename)

        if os.path.exists(default_conf_path):
            # load in config file
            config = WidgetConfig.get(view, default_conf_path)
            if config.has_view():
                configs.append(config)

            config = WidgetConfig.get("default_definition", default_conf_path)

            if config.has_view():
                configs.append(config)


        # NOTE: this should be deprecated at some point in the future ... 
        # however, currently there are still a number of definitions used here
        # ultimately look for the default file in prod
        base_dir = Environment.get_install_dir()
        #default_prod_conf_path = "%s/src/config/prod/widget/%s" \
        #    % (base_dir, default_filename)
        default_prod_conf_path = "%s/src/config2/search_type/widget/prod/%s" \
            % (base_dir, default_filename)
        if default_prod_conf_path != default_conf_path and  \
                os.path.exists(default_prod_conf_path):
            # load in config file
            config = WidgetConfig.get(view, default_prod_conf_path)
            if config.has_view():
                configs.append(config)

            config = WidgetConfig.get("default_definition", default_prod_conf_path)
            if config.has_view():
                configs.append(config)


        widget_config_view = WidgetConfigView(search_type,view,configs)


        # add search_type to all of the configs
        for config in configs:
            config.search_type = search_type

        # cache the config
        if use_cache:
            config_cache["%s:%s" % (search_type, view)] = widget_config_view

        return widget_config_view


    get_by_search_type = staticmethod(get_by_search_type)


    def get_by_type(cls, type):

        # Add some more definitions from widget_config table
        # that are specific custom layouts
        search = Search("config/widget_config")
        # we have no way determine ...
        #search.add_filter("view", "column.%", op="like")
        search.add_filter("widget_type", "column")
        #search.add_filter("search_type", search_type)


        db_configs = search.get_sobjects()

        configs = []

        if db_configs:
            config_xml = []
            config_xml.append("<config>")
            config_xml.append("<custom>")

            for db_config in db_configs:
                db_config_view = db_config.get_value("view")
                parts = db_config_view.split(".")
                title = parts[-1]
                title = Common.get_display_title(title)

                config_xml.append( """
                <element name="%s" title="%s">
                  <display class="tactic.ui.table.CustomLayoutElementWdg">
                    <view>%s</view>
                  </display>
                </element>
                """ % (db_config_view, title, db_config_view) )
            config_xml.append("</custom>")
            config_xml.append("</config>")

            config_xml = "\n".join(config_xml)

            from pyasm.common import Xml
            xml = Xml()
            xml.read_string(config_xml)
            tmp_config = WidgetConfig.get("custom", xml=xml)
            configs.append(tmp_config)

        return configs

    get_by_type = classmethod(get_by_type)



    def get_configs_from_file(cls, search_type, view):
        '''biased towards the edit and potentially edit_definition view of the search_type'''
        full_search_type = search_type
        if isinstance(search_type, SearchType):
            search_type_obj = search_type
        else:
            search_type_obj = SearchType.get(search_type)
        base_search_type = search_type_obj.get_base_key()
        from pyasm.biz import Project
        search_type = Project.get_full_search_type(full_search_type)

        # build name of the files to look in
        sub_dir = search_type_obj.get_value('namespace')
        tmp = search_type_obj.get_base_key().split("/")
        if len(tmp) == 2:
            table = tmp[1]
        else:
            # ignore the schema for config files for now
            table = tmp[2]

        filename = "%s-conf.xml" % table
        default_filename = "DEFAULT-conf.xml"
        base_dir = Environment.get_install_dir()


        configs = []

        internal_conf_path = "%s/src/config2/search_type/widget/%s/%s" \
            % (base_dir, sub_dir, filename)
        if os.path.exists(internal_conf_path):
            # load in config file
            config = WidgetConfig.get(view, internal_conf_path)
            if config.has_view():
                configs.append(config)



        # look for the default file (for definitions)
        default_conf_path = "%s/src/config2/search_type/widget/%s/%s" \
            % (base_dir, sub_dir, default_filename)

        if os.path.exists(default_conf_path):
            # load in config file
            config = WidgetConfig.get(view, default_conf_path)
            if config.has_view():
                configs.append(config)

        # finally, look at prod default
        default_conf_path = "%s/src/config2/search_type/widget/prod/%s" \
            % (base_dir, default_filename)

        if os.path.exists(default_conf_path):
            config = WidgetConfig.get(view, default_conf_path)
            if config.has_view():
                configs.append(config)

        return configs

 


    get_configs_from_file = classmethod(get_configs_from_file)



    """
    def get_views(search_type):
        '''get all the views for this search_type'''
        if isinstance(search_type, SearchType):
            search_type_obj = search_type
        else:
            search_type_obj = SearchType.get(search_type)
        search_type = search_type_obj.get_base_key()
        context = search_type_obj.get_database()

        # build up the file path and load in the config file
        conf_path = ''
        if context == "sthpw":
            project = SearchType.get_project()
            conf_path = "%s/sites/%s/config/sthpw/widget/%s" \
                % (site_dir,project,filename)
        else:
            conf_path = "%s/sites/%s/config/widget/%s" \
                % (site_dir,context,filename)
        if os.path.exists(conf_path):
            config = WidgetConfig.get(file_path=conf_path)


        xpath = "config/"
        nodes = my.xml.get_nodes(xpath)
        node_names = [x.nodeName for x in nodes]
        return node_names
    get_view = staticmethod(get_view)
    """

    def get_by_element_names(search_type, element_names, base_view="edit_definition"):
        '''Get a config view that is dynamically created by a list of element
        names.  The definitions are those as defined in the "definition" view"
        The element_names argument just defines a list of elements to create
        the dynamic view
        UPDATE: since this is primarily used for EditCmd, it inserts an edit definition to it
        '''
        config = WidgetConfigView.get_by_search_type(search_type=search_type, view=base_view)
        if type(element_names) == types.StringType:
            element_names = element_names.split(",")

        config_xml = "<config><custom layout='TableLayoutWdg'>"
        for element_name in element_names:
            config_xml += "<element name='%s'/>" % element_name
        config_xml += "</custom></config>"

        # insert edit def config found in db
        edit_def_config = WidgetDbConfig.get_by_search_type(search_type, "edit_definition")
        if edit_def_config:
            config.get_configs().insert(0, edit_def_config)
        
        view = "custom"
        extra_config = WidgetConfig.get(view=view, xml=config_xml)
        config.get_configs().insert(0, extra_config)
        return config

    get_by_element_names = staticmethod(get_by_element_names)


    def get_default_view_node(view, project_code=None):
        '''get the xml node of the default view in the xml file'''
        from pyasm.biz import Project
        if project_code:
            project = Project.get_by_code(project_code)
        else:
            project = Project.get()
        project_type = project.get_base_type()
        view_node = None
        if project_type:
            base_dir = Environment.get_install_dir()
            file_path="%s/src/tactic/ui/config/%s-conf.xml" % (base_dir, project_type)
            if os.path.exists(file_path):
                widget_config = WidgetConfig.get(file_path=file_path, view=view)
                
                view_node = widget_config.get_view_node(view)
        return view_node
    get_default_view_node = staticmethod(get_default_view_node)




class WidgetConfigTestCmd(Command):
    '''This is used for Client API testing only'''

    def execute(my):
        search_type = my.kwargs.get('search_type')
        element_name = my.kwargs.get('element_name')
        view = my.kwargs.get('view')
        match = my.kwargs.get('match')
        
        from tactic.ui.panel import SideBarBookmarkMenuWdg
        config_view = SideBarBookmarkMenuWdg.get_config(search_type, view)
        expected = config_view.get_display_handler(element_name)
        display_options = config_view.get_display_options(element_name)
        
        if match != expected:
            from pyasm.common import TacticException
            raise TacticException('Match falied ', match, expected)
        
        # send some info back for further assertion
        my.info['display_options'] = display_options
        my.info['display_handler'] = expected
