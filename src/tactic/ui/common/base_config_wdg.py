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


from pyasm.common import Common, jsonloads
from pyasm.search import SearchType
from pyasm.web import HtmlElement
from pyasm.prod.biz import ProdSetting

from pyasm.widget import WidgetConfigView, WidgetConfig

import types

from base_refresh_wdg import BaseRefreshWdg

class BaseConfigWdg(BaseRefreshWdg):

    def __init__(self, search_type, config_base, input_prefix='', config=None):

        if type(search_type) in types.StringTypes:
            self.search_type_obj = SearchType.get(search_type)
            self.search_type = search_type
        elif isinstance(search_type, SearchType):
            self.search_type_obj = search_type
            self.search_type = self.search_type_obj.get_base_key() 
        elif inspect.isclass(search_type) and issubclass(search_type, SObject):
            self.search_type_obj = SearchType.get(search_type.SEARCH_TYPE)
            self.search_type = self.search_type_obj.get_base_key()
        else:
            raise LayoutException('search_type must be a string or an sobject')
        self.config = config
        self.config_base = config_base
        self.input_prefix = input_prefix
        self.element_names = []
        self.element_titles = []

        from pyasm.web import DivWdg
        self.top = DivWdg()

        # Layout widgets compartmentalize their widgets in sections for drawing
        self.sections = {}

        super(BaseConfigWdg,self).__init__() 


    # NEED to add these because this is derived from HtmlElement and not
    # BaseRefreshWdg
    def add_style(self, name, value=None):
        return self.top.add_style(name, value=value)

    def add_class(self, class_name):
        return self.top.add_class(class_name)

    def has_class(self, class_name):
        return self.top.has_class(class_name)

    def add_behavior(self, behavior):
        return self.top.add_behavior(behavior)

    def add_relay_behavior(self, behavior):
        return self.top.add_relay_behavior(behavior)




    def get_default_display_handler(cls, element_name):
        raise Exception("Must override 'get_default_display_handler()'")
    get_default_display_handler = classmethod(get_default_display_handler)


    def get_config_base(self):
        return self.config_base

    def get_config(self):
        return self.config

    def get_view(self):
        return self.config_base


    def remap_display_handler(self, display_handler):
        '''Provide an opportunity to remap a display handler for newer
        layouts engines using older configs'''
        return display_handler
        

    def init(self):

        # create all of the display elements
        if not self.config:
            # it shouldn't use the self.search_type_obj here as it would absorb the project info
            self.config = WidgetConfigView.get_by_search_type(self.search_type, self.config_base)
        self.element_names = self.config.get_element_names()
        self.element_titles = self.config.get_element_titles()  

        # TODO: should probably be all the attrs
        self.element_widths = self.config.get_element_widths()  

       
        simple_view = self.kwargs.get("show_simple_view")
        if simple_view == "true":
            simple_view = True
        else:
            simple_view = False


        self.extra_data = self.kwargs.get("extra_data")
        if self.extra_data and isinstance(self.extra_data, basestring):
            try:
                self.extra_data = jsonloads(self.extra_data)
            except:
                self.extra_data = self.extra_data.replace("'", '"')
                self.extra_data = jsonloads(self.extra_data)



        # go through each element name and construct the handlers
        for idx, element_name in enumerate(self.element_names):

            # check to see if these are removed for this production
            #if element_name in invisible_elements:
            #    continue

            simple_element = None

            display_handler = self.config.get_display_handler(element_name)
            new_display_handler = self.remap_display_handler(display_handler)
            if new_display_handler:
                display_handler = new_display_handler

            if not display_handler:
                # else get it from default of this type
                display_handler = self.get_default_display_handler(element_name)

            # get the display options
            display_options = self.config.get_display_options(element_name)

            # add in extra_data
            if self.extra_data:
                for key, value in self.extra_data.items():
                    display_options[key] = value

            try:
                if not display_handler:
                    element = self.config.get_display_widget(element_name)
                else:
                    display_options['element_name'] = element_name
                    element = WidgetConfig.create_widget( display_handler, display_options=display_options )
            except Exception as e:
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
            title = self.element_titles[idx]
            element.set_title(title)

            # FIXME: this causes a circular reference which means the
            # Garbage collector can't clean it up
            # make sure the element knows about its layout engine
            element.set_layout_wdg(self)


            # TODO: should convert this to ATTRS or someting like that.  Not
            # just width
            if idx >= len(self.element_widths):
                element.width = 150
            else:
                element.width = self.element_widths[idx]

            if self.input_prefix:
                element.set_input_prefix(self.input_prefix)


            # get the display options
            #display_options = self.config.get_display_options(element_name)
            #for key in display_options.keys():
            element.set_options(display_options)

            self.add_widget(element,element_name)

            # layout widgets also categorize their widgets based on type
            if element_name == "Filter":
                section_name = 'filter'
            else:
                section_name = 'default'
            section = self.sections.get(section_name)
            if not section:
                section = []
                self.sections[section_name] = section
            section.append(element)


        # go through each widget and pass them the filter_data object
        from tactic.ui.filter import FilterData
        filter_data = FilterData.get()
        if not filter_data:
            filter_data = {}
        for widget in self.widgets:
            widget.set_filter_data(filter_data)



        # initialize all of the child widgets
        super(BaseConfigWdg,self).init()



    def rename_widget(self,name, new_name):
        widget = self.get_widget(name)
        widget.set_name(new_name)

    def remove_widget(self,name):
        widget = self.get_widget(name)
        try:
            self.widgets.remove(widget)
        except:
            print "WARNING: cannot remove widget"


