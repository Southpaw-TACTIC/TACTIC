##########################################################
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

__all__ = ['WidgetDbConfig', 'WidgetDbConfigCache']

from pyasm.common import *
from sql import *
from search import *


class WidgetDbConfig(SObject):
    '''represents an sobject configuration in the database'''
    SEARCH_TYPE = "config/widget_config"

    # NOTE: search_type is not used here!!! Fix
    def __init__(my, search_type=None, columns=None, result=None, **kwargs):

        if not search_type:
            search_type = my.SEARCH_TYPE

        super(WidgetDbConfig,my).__init__(search_type, columns, result, **kwargs)

        my._init()



    """
    def get_value(my, name, no_exception=False, auto_convert=True):
        value = super(WidgetDbConfig, my).get_value(name, no_exception, auto_convert)
        if name == "config" and value.startswith("PATH"):
            path = "/tmp/config_test-%s" % my.get_id()

            import os
            if not os.path.exists(path):
                value = ""
            else:
                f = open(path, "r")
                value = f.read()
                f.close()

        return value


    def set_value(my, name, value, quoted=1, temp=False):
        if name == "config" and my.data.get("config").startswith("PATH"):
            path = "/tmp/config_test-%s" % my.get_id()
            f = open(path, "w")
            f.write(value)
            f.close()

            value = "PATH"


        return super(WidgetDbConfig, my).set_value(name, value, quoted, temp)
    """







    def _init(my):
        test = my.get_value("config", no_exception=True)
        my.view = my.get_value("view")
        my.view_xpath = my.view
        my.view_as_attr = False 
        if not test:
            if my.view:
                my.set_value("config", '''
                <config>
                <%s/>
                </config>
                ''' % my.view)


        # cache this value so it doesn't have to be parsed every time
        if test.startswith("html"):
            my.html = test
            my.xml = None
            my.type = "html"
        else:
            my.html = None

            # try getting the xml value:
            my.xml = my.get_xml_value("config", "config")

            my.type = "xml"
            
            if my.view.find('@') != -1:
                my.view_as_attr = True
                my.view_xpath = "view[@name='%s']"%my.view
            # if config is empty, then this is a newly created xml, so have to
            # add the view node
            if my.view and not test:
                try:
                    view_node = my.xml.create_element(my.view)
                except Exception, e:
                    if e.__str__().find('tag name') != -1:
                        
                        view_node = my.xml.create_element('view', attrs={'name': my.view})
                        my.view_as_attr = True 
                        
                    else:
                        raise TacticException('Cannot create view node with name [%s]'%my.view)

                root_node = my.xml.get_root_node()
                my.xml.append_child(root_node, view_node)



    def validate(my):
        if my.get_view() == 'definition':
            # renew the cached xml first
            my.xml = my.get_xml_value('config','config')
            element_names = my.get_element_names()
            unique_element_names = Common.get_unique_list(element_names)
            if len(element_names) > len(unique_element_names):
                for x in unique_element_names:
                    element_names.remove(x)
                raise SObjectException('This element [%s] is not unique in definition view.'  %','.join(element_names))

        xml = my.get_xml_value('config')
        node = xml.get_node("config")
        if node is None:
            raise SObjectException('It has to begin and end with the <config> </config> tag')

        # insert may involve get_unique_sobject's <config/> which we want to ignore now
        view = my.update_data.get('view')
        if not view:
            view = my.get_view()
       
        if xml.to_string().strip() != '<config/>':
            if view and not view.startswith('link_search'):
                if view.find('@') != -1:
                    view_node = xml.get_node("config/view[@name='%s']" %view)
                    
                else:
                    view_node = xml.get_node("config/%s" %view)
                if view_node is None:
                    raise SObjectException('The config xml has to begin and end with the <config><%s> </%s></config> tag' %(view, view))   
        return True



    def get_defaults(my):
        defaults = {}
        search_type = my.get_value("search_type")
        if search_type == "SideBarWdg":
            defaults['category'] = 'SideBarWdg'

        return defaults
            



    # for backwards compatibility
    def has_view(my, view=None):
        # check that this view actually exists in this file

        if not view:
            view = my.view

        node = my.xml.get_node("config/%s" % view)
        if node is not None:
            return True
        else:
            return False


    def set_view(my, view):
        my.view = view

    def get_view(my):
        return my.view

    def get_xml(my):
        return my.xml


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
        return my.xml.get_node(xpath)


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
        attrs = {}
        node = my.get_element_node(element_name)
        if node is None:
            return {}
        node_attrs = Xml.get_attributes(node)
        return node_attrs


    def get_element_attribute(my, element_name, name):
        attrs = my.get_ellement_attributes(element_name)
        return attrs.get(name)



    def get_element_title(my, element_name):
        return my.get_element_attributes(element_name).get("title")



    def get_element_names(my, type=None, attrs=[]):
        '''get all of the element names'''
        if my.view.find("@") != -1:
            xpath = "config/view[@name='%s']/element" % my.view
        else:
            xpath = "config/%s/element" % my.view
        nodes = my.xml.get_nodes(xpath)

        ordered_nodes = []

        for node in nodes:
            name = Xml.get_attribute(node,"name")
            ordered_nodes.append(name)

        return ordered_nodes


    def get_element_xml(my, element_name):
        node = my.get_element_node(element_name)
        if node is None:
            return ''
        return my.xml.to_string(node)



    def get_element_node(my, element_name):
        xpath = "config/%s/element[@name='%s']" % (my.view_xpath, element_name)
        node = my.xml.get_node(xpath)
        return node

    def create_element(my, elem_name):
        '''create a new element or replace the existing one'''
        view_node = my.xml.get_node("config/%s" % my.view_xpath)
        old_element_node = my.xml.get_node("config/%s/element[@name='%s']" % (my.view_xpath, elem_name))
        assert view_node != None


        # create the element
        element_node = my.xml.create_element("element")
        my.xml.set_attribute(element_node, "name", elem_name)
        if old_element_node is not None:
            my.xml.replace_child(view_node, old_element_node, element_node)
        else:
            my.xml.append_child(view_node, element_node)
        return element_node
    

    def import_element_node(my, element_name, deep=True):
        node = my.get_element_node(element_name)
        imported_node = None
        if node is not None:
            imported_node = my.xml.import_node(node, deep=deep)
        return imported_node 


    # convenience access functions
    def get_widget_key(my, element_name, type='display'):
        assert element_name != None

        xpath = "config/%s/element[@name='%s']/%s/@widget" % (my.view, type, element_name)
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

    def get_handler(my, element_name, type):
        # get the display handler regardless of type
        return my.get_display_handler(element_name)




    def get_action_handler(my, element_name):
        xpath = "config/%s/element[@name='%s']/action/@class" \
            % (my.view,element_name)
        return my.xml.get_value(xpath)


    def get_type(my, element_name):
        xpath = "config/%s/element[@name='%s']/@type" % (my.view_xpath, element_name)
        type = my.xml.get_value(xpath)
        if not type:
            xpath = "config/%s/element[@name='%s']/@type" % ("definition", element_name)
            type = my.xml.get_value(xpath)

        return type


    def get_action_options(my, element_name):
        return my.get_options(element_name, 'action')

    def get_web_options(my, element_name):
        return my.get_options(element_name, 'web')

    def get_display_options(my, element_name):
        return my.get_options(element_name, 'display')

    def get_options(my, element_name, element_child_name):
        xpath = "config/%s/element[@name='%s']/%s/*" \
            % (my.view_xpath, element_name, element_child_name)
        option_nodes = my.xml.get_nodes(xpath)

        values = {}

        for node in option_nodes:
            value = my.xml.get_node_value(node)
            name = my.xml.get_node_name(node)
            #first_child = my.xml.get_first_child(node)
            #if not first_child:
            #    continue
            #value = my.xml.get_node_value(first_child)
            #name = my.xml.get_node_name(node)
            values[name] = value

        return values



    def get_display_widget(my, element_name, extra_options={}):
        display_handler = my.get_display_handler(element_name)
        display_options = my.get_display_options(element_name)

        if not display_handler:
            raise Exception("No display handler found for [%s]" % element_name)

        for name, value in extra_options.items():
            display_options[name] = value

        try:
            widget = Common.create_from_class_path(display_handler, [], display_options)
        except:
            # put in a bit of a hack for TableElementWdg
            args = [element_name, None]
            widget = Common.create_from_class_path(display_handler, args, display_options)


        widget.set_name(element_name)
        return widget





    def append_xml_element(my, element_name, config_xml):
        '''append an element with the config_xml to current doc's view'''
        xml = Xml()
        xml.read_string(config_xml)
        new_root_node = xml.get_root_node()
       
        view_node = my.get_view_node()
        if view_node is None:
            print "View Node does not exist"
            return
        node = my.get_element_node(element_name)
        if node is not None:
            xml.replace_child(view_node, node, new_root_node)
        else:
            element = my.get_element_node("code")
            if element is None:
                element = my.get_element_node("name")
            if element is not None:
                xml.insert_before(new_root_node, element)
            else:
                xml.append_child(view_node, new_root_node)
        #print my.xml.to_string()



    def insert_xml_element(my, element_name, config_xml, ref_element_name):
        '''append an element with the config_xml to current doc's view'''
        xml = Xml()
        xml.read_string(config_xml)
        new_root_node = xml.get_root_node()
       
        view_node = my.get_view_node()
        if view_node is None:
            print "View Node does not exist"
            return
        node = my.get_element_node(element_name)
        if node is not None:
            xml.replace_child(view_node, node, new_root_node)
        else:
            element = my.get_element_node(ref_element_name)
            if element is not None:
                xml.insert_before(view_node, new_root_node)
            else:
                xml.append_child(view_node, new_root_node)

        #print my.xml.to_string()




    def append_display_element(my, elem_name, cls_name=None, options=None, element_attrs=None, action_cls_name=None, action_options=None, view_as_attr=False):
        '''create and manipulate the config file. It handles display and action node as well.'''
       
        if view_as_attr:
            view_node = my.xml.get_node("config/view[@name='%s']" % my.view)
            old_element_node = my.xml.get_node("config/view[@name='%s']/element[@name='%s']" % (my.view, elem_name))
        else:
            view_node = my.xml.get_node("config/%s" % my.view)
            # find out if the element already exists
            old_element_node = my.xml.get_node("config/%s/element[@name='%s']" % (my.view, elem_name))
        
        assert view_node != None


        # create the element
        element_node = my.xml.create_element("element")
        my.xml.set_attribute(element_node, "name", elem_name)
        if old_element_node is not None:
            my.xml.replace_child(view_node, old_element_node, element_node)
        else:
            my.xml.append_child(view_node, element_node)
      
        if element_attrs:
            for name, value in element_attrs.items():
                if value:
                    my.xml.set_attribute(element_node, name, value)


        # add the class name
        if cls_name:
            display_node = my.xml.create_element("display")
            my.xml.set_attribute(display_node, "class", cls_name)
            my.xml.append_child(element_node, display_node)

            # add any display options
            if options:
                for name, value in options.items():
                    option_node = my.xml.create_text_element(name, value)
                    my.xml.append_child(display_node, option_node)

        if action_cls_name:
            action_node = my.xml.create_element("action")
            my.xml.set_attribute(action_node, "class", action_cls_name)
            my.xml.append_child(element_node, action_node)

            # add any display options
            if action_options:
                for name, value in action_options.items():
                    option_node = my.xml.create_text_element(name, value)
                    my.xml.append_child(action_node, option_node)





    def remove_display_element(my, elem_name, cls_name=None, options=None):
        '''FIXME: this one is badly named.. pretty much doing remove_node(), I suggest removing this method'''
        view_node = my.xml.get_node("config/%s" % my.view)

        # find out if the element already exists
        element_node = my.xml.get_node("config/%s/element[@name='%s']" % (my.view,elem_name))
        if element_node is not None:
            #view_node.removeChild(element_node)
            my.xml.remove_child(view_node, element_node)

    def remove_node(my, element_name):
        view_node = my.get_view_node()
        element_node = my.get_element_node(element_name)
        if element_node is not None:
            my.xml.remove_child(view_node, element_node)

    def alter_xml_element(my, element_name, config_xml=None, node=None):
        '''alter an element with the config_xml to current doc's view.  If it
        does not exist, append it. Alternatively, pass in an actual node
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
     
        if target_node is not None:
            #view_node.replaceChild(new_root_node, target_node )
            my.xml.replace_child(view_node, target_node, new_root_node)
        else:
            #view_node.appendChild(new_root_node)
            my.xml.append_child(view_node, new_root_node)


    def move_element_left(my, elem_name):
        nodes = my.xml.get_nodes("config/%s/element" % my.view)
        node = None
        index = -1
        for i, node in enumerate(nodes):
            print i, node
            if Xml.get_attribute(node, "name") == elem_name:
                node = node
                index = i
                break

        if node is None:
            raise Exception("Node [%s] does not exist" % my.elem_name)

        if index == 0:
            return

        prev = nodes[index-1]

        #parent = node.parentNode
        #parent.removeChild(node)
        parent = my.xml.get_parent(node)
        my.xml.remove_child(parent, node)

        # FIXME: this does not use XML class
        parent.insertBefore(node, prev)



    def move_element_right(my, elem_name):
        nodes = my.xml.get_nodes("config/%s/element" % my.view)
        node = None
        index = -1
        for i, node in enumerate(nodes):
            if Xml.get_attribute(node, "name") == elem_name:
                node = node
                index = i
                break

        if node is None:
            raise Exception("Node [%s] does not exist" % my.elem_name)

        #parent = node.parentNode
        #parent.removeChild(node)
        parent = my.xml.get_parent(node)
        my.xml.remove_child(parent, node)
        
        if index+2 >= len(nodes):
            #parent.appendChild(node)
            my.xml.append_child(parent, node)
        else:
            next = nodes[index+2]

            # FIXME: this does not use XML class
            parent.insertBefore(node, next)



    def clear(my):
        # make a basic xml document for configs
        my.xml = Xml()
        my.xml.create_doc("config")
        root = my.xml.get_root_node()
        view_node = my.xml.create_element(my.view)
        #root.appendChild(view_node)
        my.xml.append_child(root, view_node)



    def commit_config(my):
        '''commits the current config xml to the database'''
        my.set_value("config", my.xml.to_string() )
        my.commit()


    # static methods

    def get_by_search_type(cls, search_type, view, project_code=None):

        # NOTE: this will cause TACTIC to look at the current project
        # for the widget_config
        has_project = False
        orig_search_type = search_type
        if search_type.find("?") != -1:
            parts = search_type.split("?")
            search_type = parts[0]
            has_project = True

        if not project_code:
            base_search_type, data = SearchKey._get_data(search_type)
            project_code = data.get("project")
        else:
            base_search_type = search_type

        try:
            search = Search( WidgetDbConfig.SEARCH_TYPE, project_code=project_code )
        # if there is no Widget config table
        except SearchException, e:
            return None


        data = SearchType.breakup_search_type(orig_search_type)
        from pyasm.biz import Project
        current_project_code = Project.get_project_code()

        if data.get('project') and current_project_code != data.get('project'):
            search.add_filter("search_type", orig_search_type)
        else:
            search.add_filter("search_type", base_search_type)

        search.add_filter("view", view)
        #search.add_project_filter(project_code)
        #key = '%s:%s:%s' %(search_type, view, project_code)

        # use the full search_type in the key
        key = '%s:%s' %(search_type, view)
        if search.column_exists("priority"):
            search.add_order_by("priority desc")
        widget_db_configs = SObject.get_by_search(search, key, is_multi=True)
        if widget_db_configs:
            widget_db_config = cls.merge_configs(widget_db_configs)
        else:
            widget_db_config = None

        # if no config is found:
        if has_project and not widget_db_config and not project_code:
            from pyasm.biz import Project
            current_project_code = Project.get_project_code()
            if project_code != current_project_code:
                try:
                    parts = orig_search_type.split("=")
                    project_code = parts[-1]
                    widget_db_config = cls.get_by_search_type(search_type, view, project_code=project_code)
                except Exception, e:
                    print "ERROR: ", e
                    # No widget config found in the other project of the stype
                    pass

        return widget_db_config

    get_by_search_type = classmethod(get_by_search_type)




    def merge_configs(cls, configs):
        # since we only return one widget config, we will merge these
        # by cascading.  The rules are as follows:
        # 1: element display and kwargs cascade in their entirety
        # 2: attributes of the bubble up individually
        if not configs:
            return None

        if len(configs) == 1:
            return configs[0]

        # annoyingly NULL is always higher than any number, so we have
        # put them at the end
        if configs[0].column_exists("priority"):
            configs = sorted(configs, key=lambda x: x.get("priority"))
            configs.reverse()

        # the element names are determined by the first one
        main_config = configs[0]
        element_names = main_config.get_element_names()
        main_xml = main_config.get_xml()

        for element_name in element_names:
            main_attrs = main_config.get_element_attributes(element_name)

            xpath = "config//element[@name='%s']" % (element_name)
            node = main_xml.get_node(xpath)

            # if there is a display node
            display_xpath = "config//element[@name='%s']/display" % (element_name)
            main_display_node = main_xml.get_node(display_xpath)


            for config in configs[1:]:
                # copy the attrs
                attrs = config.get_element_attributes(element_name)
                keys = attrs.keys()
                for key in keys:
                    if not main_attrs.has_key(key):
                        main_xml.set_attribute(node, key, attrs.get(key))

                if main_display_node is not None:
                    continue

                xml = config.get_xml()
                display_node = xml.get_node(display_xpath)
                if display_node is None:
                    continue

                class_name = xml.get_attribute(display_node, "class")
                options = config.get_display_options(element_name)

                main_config.append_display_element(element_name, class_name, options)
                
        return main_config

    merge_configs = classmethod(merge_configs)





    def get_all_by_search_type(search_type):
        '''get all of the views for this search type'''
        search = Search( WidgetDbConfig.SEARCH_TYPE )
        search.add_filter("search_type", search_type)
        search.add_order_by("view")
        return search.get_sobjects()
    get_all_by_search_type = staticmethod(get_all_by_search_type)



    def get_global_default(view):
        search_type = "__DEFAULT__"
        # TODO: hard code this for now
        view = "table"
        return WidgetDbConfig.get_by_search_type(search_type,view)
    get_global_default = staticmethod(get_global_default)





    def create(cls, search_type, view,  data=None, layout=None, project_code=None):
        '''will only create if it does not exist, otherwise it just updates'''
        sobject = WidgetDbConfig.get_by_search_type(search_type, view, project_code)
        if sobject == None:
            sobject = WidgetDbConfig( WidgetDbConfig.SEARCH_TYPE )

        sobject.set_value("search_type", search_type)
        sobject.set_user()
        sobject.set_value("view", view)
        if data == None:
            # make a basic xml document for configs
            xml = Xml()
            xml.create_doc("config")
            root = xml.get_root_node()
            view_node = xml.create_element(view)
            #xml.set_attribute(view_node, "layout", "TableWdg")
            #root.appendChild(view_node)
            xml.append_child(root, view_node)
            data = xml.to_string()

        sobject.set_value("config", data)

        sobject.commit()

        # make sure some member variables exist in the newly created object
        sobject._init()

        # clear previous caches
        #key = '%s:%s' %(search_type, view)
        #print "clearing cache: ", key
        cls.clear_cache()
        return sobject
    create = classmethod(create)

    def append(cls, search_type, view, name, class_name=None, display_options={}, element_attrs={}, config_xml=None, login=None):
        '''append an element with display class and options to the specified widget config'''
        assert view
        config_search_type = "config/widget_config"

        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        search.add_filter("login", login)
        db_config = search.get_sobject()
        config_exists = True
        view_node = None
        if not db_config:
            db_config = SearchType.create(config_search_type)
            db_config.set_value("search_type", search_type )
            db_config.set_value("view", view )
            if login:
                db_config.set_value("login", login)

            config_exists = False

        # maintain the config variable here to mean WidgetConfig
        from pyasm.widget import WidgetConfigView
        if not config_exists and search_type not in ["SideBarWdg"]:
            config_view = WidgetConfigView.get_by_search_type(search_type, view)            
            #xml = config.get_xml()
            configs = config_view.get_configs()
            if configs:
                config = configs[0]
                view_node = config.get_view_node()
                config_exists = True
        
        if not config_exists:
            xml = db_config.get_xml_value("config", "config")
            db_config._init()
            root = xml.get_root_node()
            # build a new config
            view_node = xml.create_element(view)
            #root.appendChild(view_node)
            xml.append_child(root, view_node)
        else:   
            xml = db_config.get_xml_value("config", "config")
            root = xml.get_root_node()
            # it could be passed in thru a widget_config already
            if view_node is None:
                view_node = db_config.get_view_node()
            #root.appendChild(view_node)
            xml.append_child(root, view_node)

            db_config._init()

        if config_xml:
            db_config.append_xml_element( name, config_xml)
        else:
            db_config.append_display_element(name, class_name, options=display_options, element_attrs=element_attrs)
        db_config.commit_config()

        return db_config

    append = classmethod(append)



    def build_xml_definition(cls, class_name, display_options):
        xml = Xml()
        xml.create_doc("element")
        root = xml.get_root_node()

        display_node = xml.create_element("display")
        xml.append_child(root, display_node)
        xml.set_attribute(display_node, "class", class_name)
      
        # add any display options
        if display_options:
            for name, value in display_options.items():
                if name == "class_name":
                    continue
                option_node = xml.create_text_element(name, value)
                xml.append_child(display_node, option_node)

        xml = xml.to_string()
        return xml
    build_xml_definition = classmethod(build_xml_definition)


 






class WidgetDbConfigCache(Base):

    def __init__(my, search_type, view):
        my.view = view

        # cache this value so it doesn't have to be parsed every time
        my.config = WidgetDbConfig.get_by_search_type(search_type, view)
        if my.config == None:
            my.xml = Xml()
            my.xml.create_doc()
            my.view_xpath = view
        else:
            my.xml = my.config.get_xml_value("config")
            my.view_xpath = my.config.view_xpath

        # get the default sobject corresponding to this view
        my.default_config = WidgetDbConfig.get_global_default(my.view)
        if not my.default_config:
            my.default_xml = Xml()
            my.default_xml.read_string("<config/>")
        else:
            my.default_xml = my.default_config.get_xml_value("config")
        



    def get_element_names(my):
        '''get all of the element names'''
        xpath = "config/%s/element" % my.view
        nodes = my.xml.get_nodes(xpath)

        ordered_nodes = []

        for node in nodes:
            name = Xml.get_attribute(node,"name")
            ordered_nodes.append(name)

        return ordered_nodes



    # convenience functions
    def get_display_handler(my, element_name):
        xpath = "config/%s/element[@name='%s']/display/@class" \
            % (my.view_xpath, element_name)
        display_handler = my.xml.get_value(xpath)

        if display_handler == "":
            xpath = "config/default/element[@name='%s']/display/@class" \
                % (element_name)
            display_handler = my.default_xml.get_value(xpath)

        return display_handler



    def get_action_handler(my, element_name):
        xpath = "config/%s/element[@name='%s']/action/@class" \
            % (my.view_xpath, element_name)

        handler = my.xml.get_value(xpath)

        if handler == "":
            xpath = "config/default/element[@name='%s']/action/@class" \
                % (element_name)
            handler = my.default_xml.get_value(xpath)

        return handler


    """
    def get_display_options(my, element_name):
        
        xpath = "config/default/element[@name='%s']/display/*" \
            % (element_name)
        # get the default options and add
        option_nodes = my.default_xml.get_nodes(xpath)
        values = {}
        for node in option_nodes:
            value = node.firstChild.nodeValue
            values[node.nodeName] = value

        xpath = "config/%s/element[@name='%s']/display/*" \
            % (my.view,element_name)
        # get the override options and add
       
        option_nodes = my.xml.get_nodes(xpath)
        values = {}
        for node in option_nodes:
            value = node.firstChild.nodeValue
            values[node.nodeName] = value

        return values
    """



