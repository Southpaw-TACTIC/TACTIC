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

__all__ = ['BaseConfigWdg']


from pyasm.common import Common
from pyasm.search import SearchType
from pyasm.web import HtmlElement
from pyasm.prod.biz import ProdSetting

from pyasm.widget import WidgetConfigView, WidgetConfig

import types

from base_refresh_wdg import BaseRefreshWdg

class BaseConfigWdg(BaseRefreshWdg):

    def __init__(my, search_type, config_base, input_prefix='', config=None):

        if type(search_type) in types.StringTypes:
            my.search_type_obj = SearchType.get(search_type)
            my.search_type = search_type
        elif isinstance(search_type, SearchType):
            my.search_type_obj = search_type
            my.search_type = my.search_type_obj.get_base_key() 
        elif inspect.isclass(search_type) and issubclass(search_type, SObject):
            my.search_type_obj = SearchType.get(search_type.SEARCH_TYPE)
            my.search_type = my.search_type_obj.get_base_key()
        else:
            raise LayoutException('search_type must be a string or an sobject')
        my.config = config
        my.config_base = config_base
        my.input_prefix = input_prefix
        my.element_names = []
        my.element_titles = []

        from pyasm.web import DivWdg
        my.top = DivWdg()

        # Layout widgets compartmentalize their widgets in sections for drawing
        my.sections = {}

        super(BaseConfigWdg,my).__init__() 


    # NEED to add these because this is derived from HtmlElement and not
    # BaseRefreshWdg
    def add_style(my, name, value=None):
        return my.top.add_style(name, value=value)

    def add_class(my, class_name):
        return my.top.add_class(class_name)

    def has_class(my, class_name):
        return my.top.has_class(class_name)

    def add_behavior(my, behavior):
        return my.top.add_behavior(behavior)

    def add_relay_behavior(my, behavior):
        return my.top.add_relay_behavior(behavior)




    def get_default_display_handler(cls, element_name):
        raise Exception("Must override 'get_default_display_handler()'")
    get_default_display_handler = classmethod(get_default_display_handler)


    def get_config_base(my):
        return my.config_base

    def get_config(my):
        return my.config

    def get_view(my):
        return my.config_base


    def remap_display_handler(my, display_handler):
        '''Provide an opportunity to remap a display handler for newer
        layouts engines using older configs'''
        return display_handler
        

    def init(my):

        # create all of the display elements
        if not my.config:
            # it shouldn't use the my.search_type_obj here as it would absorb the project info
            my.config = WidgetConfigView.get_by_search_type(my.search_type, my.config_base)
        my.element_names = my.config.get_element_names()
        my.element_titles = my.config.get_element_titles()  

        # TODO: should probably be all the attrs
        my.element_widths = my.config.get_element_widths()  

       
        simple_view = my.kwargs.get("show_simple_view")
        if simple_view == "true":
            simple_view = True
        else:
            simple_view = False
        

        # go through each element name and construct the handlers
        for idx, element_name in enumerate(my.element_names):

            # check to see if these are removed for this production
            #if element_name in invisible_elements:
            #    continue

            simple_element = None

            display_handler = my.config.get_display_handler(element_name)
            new_display_handler = my.remap_display_handler(display_handler)
            if new_display_handler:
                display_handler = new_display_handler

            if not display_handler:
                # else get it from default of this type
                display_handler = my.get_default_display_handler(element_name)

            # get the display options
            display_options = my.config.get_display_options(element_name)
            try:
                if not display_handler:
                    element = my.config.get_display_widget(element_name)
                else:
                    element = WidgetConfig.create_widget( display_handler, display_options=display_options )
            except Exception, e:
                from tactic.ui.common import WidgetTableElementWdg
                element = WidgetTableElementWdg()
                # FIXME: not sure why this doesn't work
                #from pyasm.widget import ExceptionWdg
                #log = ExceptionWdg(e)
                #element.add(log)
                # FIXME: not sure why this doesn't work
                from pyasm.widget import IconWdg
                icon = IconWdg("Error", IconWdg.ERROR)
                element.add(icon)
                element.add(e)

            # skip the empty elements like ThumbWdg
            if simple_element and not element.is_simple_viewable():
                continue
            # make simple_element the element if it exists
            if simple_element:
                element = simple_element
            # if the element failed to create, then continue
            if element == None:
                continue


            element.set_name(element_name)
            title = my.element_titles[idx]
            element.set_title(title)

            # FIXME: this causes a circular reference which means the
            # Garbage collector can't clean it up
            # make sure the element knows about its layout engine
            element.set_layout_wdg(my)


            # TODO: should convert this to ATTRS or someting like that.  Not
            # just width
            element.width = my.element_widths[idx]

            if my.input_prefix:
                element.set_input_prefix(my.input_prefix)


            # get the display options
            #display_options = my.config.get_display_options(element_name)
            #for key in display_options.keys():
            element.set_options(display_options)

            my.add_widget(element,element_name)

            # layout widgets also categorize their widgets based on type
            if element_name == "Filter":
                section_name = 'filter'
            else:
                section_name = 'default'
            section = my.sections.get(section_name)
            if not section:
                section = []
                my.sections[section_name] = section
            section.append(element)


        # initialize all of the child widgets
        super(BaseConfigWdg,my).init()



    def rename_widget(my,name, new_name):
        widget = my.get_widget(name)
        widget.set_name(new_name)

    def remove_widget(my,name):
        widget = my.get_widget(name)
        try:
            my.widgets.remove(widget)
        except:
            print "WARNING: cannot remove widget"


