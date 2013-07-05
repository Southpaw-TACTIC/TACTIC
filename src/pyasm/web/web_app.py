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

__all__ = ['WebAppException', 'WebApp', 'ConfigWebApp']


import types, time

from pyasm.common import *
from pyasm.search import SearchType, Sql
from widget import *
from html_wdg import *
from web_container import *



class WebAppException(Exception):
    pass



class WebApp(Base):
    """Defines a pipeline for displaying a web application"""
    def __init__(my):
        pass


    def get_display(my, widget):
        """run through the full web app pipeline"""

        if widget == None:
            raise WebAppException("No top level widget defined")

        # add to the access log
        # FIXME: this does not get committed if there is an exception.  The
        # transaction will back out.
        access_log_flag = False
        access_log = None
        if access_log_flag:
            access_log = SearchType.create("sthpw/access_log")
            access_log.set_value("url", "www.yahoo.com")
            access_log.set_value("start_time", Sql.get_timestamp_now(), quoted=False)
            access_log.commit()

            start = time.time()


        # do a security check on the widget
        # DEPRECATED
        widget.check_security()

        # draw all of the widgets
        widget = widget.get_display()
        if widget:
            Widget.get_display(widget)


        if access_log_flag:
            access_log.set_value("end_time", Sql.get_timestamp_now(), quoted=False)
            duration = time.time() - start
            duration = float(int(duration * 1000)) / 1000
            access_log.set_value("duration", str(duration) )
            access_log.commit()





# DEPRECATED: not being used at all.

class ConfigWebApp(Widget):
    """Web application that reads in a configuration file description
    of the widgets for an application"""
    def __init__(my,app_file=None):
        my.app_file = app_file
        super(ConfigWebApp,my).__init__()

    def init(my):

        if my.app_file == None:
            my.app_file = "/home/apache/tactic/sites/testsite/config/widget/test-wdg.xml"

        if my.app_file == None:
            user = WebContainer.get_user_name()
            base = "/home/remko/sthpw/src/config/webapp" 
            my.app_file = "%s/%s-wdg.xml" % (base, user)

        my.current_widget_type = ""

        my.app_xml = Xml()
        my.app_xml.read_file(my.app_file)

        #my.remove_widget_from_config("left",2)
        #my.add_widget_to_config("pyasm.widget.MyBoomSampleContentWdg", "right")
        #my.write_config()

        # parse_node
        base_widget_node = my.app_xml.get_node("widget")

        my.current_widget = None

        for child in base_widget_node.childNodes:
            my._parse_node(child)

        my.add_widget(my.current_widget)



    def _parse_node(my, node):

        # ignore this node because it, for some reason cDomlette does not have
        # a __class__ variable
        node_type = "%s" % type(node)
        if node_type == "<type 'cDomlette.Text'>": return
        if node_type == "<type 'cDomlette.Comment'>": return

        # ignore Text nodes
        #node_type = node.__class__.__name__
        #if node_type == "Text":
        #    return

        node_name = node.nodeName
        if node_name == "widget":
            my._handle_widget(node)
        elif node_name == "search":
            my._handle_search(node)
        elif node_name == "widgets":
            my._handle_widgets(node)


    def _handle_widgets(my, node):
        my.current_widget_type = Xml.get_attribute(node,"type")

        # recurse down
        for child in node.childNodes:
            my._parse_node(child)


    def _handle_widget(my, node):

        class_name = Xml.get_attribute( node, "class")
        args = Xml.get_attribute( node, "args")

        if class_name == "":
            class_name = "StringWidget"

        components = class_name.split(".")
        length = len(components)
        module_name = ".".join( components[0:(length-1)])

        # import the module
        if module_name != "":
            exec("import %s" % module_name)

        # instantiate the widget
        widget = None
        if args != "":
            widget = eval("%s(\"%s\")" % (class_name, args))
        else:
            widget = eval("%s()" % (class_name))

       
        # some special code for html element
        if isinstance(widget,HtmlElement):
            type = Xml.get_attribute( node, "html_type")
            if type != "":
                widget.set_type(type)

            # set the style if there is one defined
            style = Xml.get_attribute( node, "css_style")
            if style != "":
                widget.set_style(style)


        widget_name = Xml.get_attribute(node, "name")
        widget_type = Xml.get_attribute(node, "type")
        if widget_type == "":
            widget_type = my.current_widget_type

        # add this widget to the current widget
        if my.current_widget == None:
            my.current_widget = widget
        else:
            my.current_widget.add_widget(widget,widget_name,widget_type)



        # recurse down
        for child in node.childNodes:
            my._parse_node(child)



    def _handle_search(my, node):
        #search = Search("photo")
        #my.current_widget.set_search(search)
        pass



    def remove_widget_from_config(my, type, index):
        nodes = my.app_xml.get_nodes("application//widgets[@type='%s']/widget" % type)
        node = nodes[index]
        parent_node = node.parentNode
        parent_node.removeChild(node)


    def add_widget_to_config(my, class_name, type):
        type = my.app_xml.get_node("application//widgets[@type='%s']" % type)
        new_node = my.app_xml.create_element("widget")
        Xml.set_attribute(new_node, "class", class_name)
        type.appendChild(new_node)


    def write_config(my):

        xml = my.app_xml.get_xml()

        file = open(my.app_file, "w")
        file.write(xml)
        file.close()








