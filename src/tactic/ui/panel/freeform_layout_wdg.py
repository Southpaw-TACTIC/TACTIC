###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["FreeFormLayoutWdg"]

from pyasm.common import Common, jsonloads
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table, WebContainer
from pyasm.widget import WidgetConfig

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg

import random



class FreeFormLayoutWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'search_type': {
        'description': 'Search Type for Free Form layout',
        'type': 'TextWdg',
        'order': 1,
        'category': 'Options'
    },
    'view': {
        'description': 'Freeform view',
        'type': 'TextWdg',
        'order': 1,
        'category': 'Options'
    },
    'css': {
        'description': 'Top level style',
        'type': 'TextAreaWdg',
        'order': 2,
        'category': 'Options'
    },
    }
 




    def get_input_value(self, name):
        value = self.kwargs.get(name)
        if value == None:
            web = WebContainer.get_web()
            value = web.get_form_value(name)

        return value



    def get_default_background(self):
        return DivWdg().get_color("background")



    def get_display(self):

        category = "FreeformWdg"
        view = self.get_input_value("view")

        sobject = self.get_input_value("sobject")
        if not sobject and self.sobjects:
            sobject = self.sobjects[0]
        if not view:
            view = 'freeform'

        if sobject:
            search_key = sobject.get_search_key()
            search_type = sobject.get_base_search_type()

        else:
            search_key = self.get_input_value("search_key")
            search_type = self.get_input_value("search_type")

        if sobject:
            pass
        elif search_key:
            sobject = Search.get_by_search_key(search_key)
        elif search_type:
            search = Search(search_type)
            search.add_limit(1)
            sobject = search.get_sobject()
        else:
            sobject = None


        top = DivWdg()
        top.add_class("spt_freeform_top")


        search = Search("config/widget_config")
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        config_sobj = search.get_sobject()
        if config_sobj:
            config_xml = config_sobj.get_value("config")
        else:
            config_xml = ""

        if not config_xml:
            top.add("No definition found")
            return top

        config = WidgetConfig.get(view=view, xml=config_xml)
        view_attrs = config.get_view_attributes()


        bgcolor = view_attrs.get("bgcolor")
        if not bgcolor:
            bgcolor = self.get_default_background()

        if bgcolor:
            top.add_style("background", bgcolor)


        # draw the layout
        freeform_layout = self.get_canvas_display(search_type, view, config, sobject) 
        top.add(freeform_layout)

        return top


    def get_canvas_display(self, search_type, view, config, sobject):

        top = DivWdg()
        top.add_class("spt_freeform_layout_top")
        self.set_as_panel(top)
        #top.add_color("background", "background")
        #top.add_color("color", "color")
        #top.add_style("height: 100%")
        #top.add_style("width: 100%")
        #border_color = top.get_color("border")
        #top.add_border()

        css = self.kwargs.get("css")
        if css:
            css = jsonloads(css)
            for name, value in css.items():
                top.add_style(name, value)


        # define canvas
        canvas = top
        canvas.add_class("spt_freeform_canvas")
        canvas.add_style("position: relative")
        canvas.add_style("overflow: hidden")

        self.kwargs['view'] = view


        element_names = config.get_element_names()
        view_attrs = config.get_view_attributes()

        canvas_height = view_attrs.get("height")
        if not canvas_height:
            canvas_height = '400px'
        canvas.add_style("height: %s" % canvas_height)

        canvas_width = view_attrs.get("width")
        if not canvas_width:
            canvas_width = '400px'
        canvas.add_style("width: %s" % canvas_width)

        for element_name in element_names:

            widget_div = DivWdg()
            canvas.add(widget_div)
            widget_div.add_style("position: absolute")
            widget_div.add_style("vertical-align: top")

            widget_div.add_class("SPT_ELEMENT_SELECT")


            el_attrs = config.get_element_attributes(element_name)
            height = el_attrs.get("height")
            if height:
                widget_div.add_style("height: %s" % height)

            width = el_attrs.get("width")
            if width:
                widget_div.add_style("width: %s" % width)

            display_handler = config.get_display_handler(element_name)
            display_options = config.get_display_options(element_name)
            widget_div.add_attr("spt_display_handler", display_handler)

            try:
                widget = config.get_display_widget(element_name)
            except:
                continue
            widget.set_sobject(sobject)
            widget_div.add_attr("spt_element_name", element_name)
            widget_div.add_class("spt_element")

            #widget_div.add(widget)

            try:
                widget_div.add(widget.get_buffer_display())
            except:
                widget_div.add("Error")
                raise

            try:
                is_resizable = widget.is_resizable()
            except:
                is_resizable = False
            if is_resizable:
                widget.add_style("width: 100%")
                widget.add_style("height: 100%")
                widget.add_style("overflow: hidden")


            xpos = el_attrs.get("xpos")
            if not xpos:
                xpos = '100px'
            widget_div.add_style("left: %s" % xpos)

            ypos = el_attrs.get("ypos")
            if not ypos:
                ypos = '100px'
            widget_div.add_style("top: %s" % ypos)


        return top


__all__.append("FreeFormElementWdg")
from tactic.ui.common import BaseTableElementWdg
class FreeFormElementWdg(BaseTableElementWdg):

    ARGS_KEYS = {
    'view': {
        'description': 'Freeform view',
        'type': 'TextWdg',
        'order': 1,
        'category': 'Options'
    },
    }
 

    def preprocess(self):
        self.layout = FreeFormLayoutWdg(**self.kwargs)

    def is_editable(self):
        return False

    def get_display(self):

        sobject = self.get_current_sobject()
        self.layout.set_sobject(sobject)

        top = self.top
        top.add(self.layout.get_buffer_display())

        return top







