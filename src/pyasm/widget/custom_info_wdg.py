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

__all__ = ['CustomInfoWdg', 'CustomInfoInputWdg', 'CustomInfoAction', 'CustomTableWdg', 'PrefixParentCodeTrigger']

import types

from pyasm.common import *
from pyasm.search import Search
from pyasm.command import DatabaseAction
from pyasm.web import *
from pyasm.widget import BaseTableElementWdg, BaseInputWdg, TextWdg, WidgetConfig, WidgetConfigView, BaseConfigWdg, EditAllWdg, HintWdg, TableWdg, HiddenWdg



class CustomInfoWdg(BaseTableElementWdg):

    def __init__(my):
        my.columns = []
        super(CustomInfoWdg, my).__init__()

    def preprocess(my):
        sobject = my.get_current_sobject() 
        if not sobject:
            my.columns = []
            return 
        search_type = sobject.get_search_type_obj()
        #config = WidgetConfig.get_by_search_type(search_type, "custom", local_search=True)
        config = WidgetConfigView.get_by_search_type(search_type, "custom")
        if not config:
            my.columns = []
        else:
            my.columns = config.get_element_names()



    def get_display(my):

        sobject = my.get_current_sobject() 


        if not my.columns:
            span = SpanWdg("None")
            span.add_style("color: #ccc")
            return span

        widget = Widget()

        table = Table(css="minimal")
        table.add_style("width: 100%")

        values = []
        for column in my.columns:

            value = sobject.get_value(column, no_exception=True)
            #if not value:
            #    continue
            
            table.add_row()
            title = column.replace("_", " ")
            title = title.capitalize()
            td = table.add_cell("<i>%s</i>: " % title)
            td.add_style("text-align: right")
            td.add_style("width: 85px")

            table.add_cell(value)

        widget.add(table)

        return widget 

    def get_simple_display(my):
        return my.get_display()

class CustomConfigWdg(BaseConfigWdg):
    def get_default_display_handler(my, element_name):
        return "TextWdg"

 
class CustomInfoInputWdg(BaseInputWdg):

    def process_widget(my, idx, widget, sobject):
        pass

    def preprocess(my):
        pass

    def get_display(my):
        my.preprocess()

        sobject = my.get_current_sobject()

        view = my.get_option("view")
        if not view:
            view = "custom_view"

        search_type = sobject.get_search_type_obj()
        config = WidgetConfigView.get_by_search_type(search_type, view)
        widget_config_view = WidgetConfigView(search_type, view, [config])
        if not config:
            span = SpanWdg("None")
            span.add_style("color: #ccc")
            return span
        try:
            base = CustomConfigWdg(search_type, view, \
                config=widget_config_view, input_prefix="edit")
            
        except TacticException, e:
            span = SpanWdg("None")
            span.add_style("color: #ccc")
            return span


        div = DivWdg()

        table = Table()
        table.set_max_width()
        for idx, widget in enumerate(base.widgets):
            # process the widget if necessary
            my.process_widget(idx, widget, sobject)
            widget.set_sobjects([sobject])

            if isinstance(widget, HiddenWdg):
                div.add(widget)
                continue
            table.add_row()
            title = widget.get_title()
            table.add_cell(title)
            hint = widget.get_option("hint")
            if hint:
                table.add_data( HintWdg(hint) ) 
            table.add_cell(widget)

            edit_all = widget.get_option("edit_all")
            #if my.mode == "edit" and edit_all == 'true':
            if edit_all == 'true':
                table.add_cell( EditAllWdg(widget), css="right_content" )
            else:
                table.add_blank_cell()

        div.add(table)
        return div




class CustomInfoAction(DatabaseAction):

    def execute(my):
        sobject = my.sobject


        search_type = sobject.get_search_type_obj()
        config = WidgetConfigView.get_by_search_type(search_type, "custom")
        if not config:
            return

        my.element_names = config.get_element_names()

        # create all of the handlers
        action_handlers = []

        for element_name in (my.element_names):
            action_handler_class = \
                config.get_action_handler(element_name)

            if action_handler_class == "":
                action_handler_class = "DatabaseAction"
        

            action_handler = WidgetConfig.create_widget( action_handler_class )
            action_handler.set_name(element_name)
            action_handler.set_input_prefix("edit")

            action_options = config.get_action_options(element_name)
            for key, value in action_options.items():
                action_handler.set_option(key, value)
            action_handlers.append(action_handler)

        # set the sobject for each action handler
        for action_handler in action_handlers:
            action_handler.set_sobject(sobject)
            if action_handler.check():
                action_handler.execute()




class CustomTableWdg(Widget):
    '''Display a custom table using TableWdg'''
    def get_display(my):
        search_type = my.options.get("search_type")
        view = my.options.get("view")
        filter = my.options.get("filter")
        if type(filter) in types.StringTypes:
            filters = [filter]
        elif not filter:
            filters = []
        else:
            filters = filter

        # create the search
        search = Search(search_type)

        widget = Widget()
        div = DivWdg(css="filter_box")
        widget.add(div)

        for i, filter in enumerate(filters):

            if filter.find("|") != -1:
                filter_name, expression = filter.split("|", 1)
            else:
                filter_name = filter
                expression = None


            span = SpanWdg(css="med")

            filter_wdg = Container.get_dict("widgets", filter_name)
            if not filter_wdg:
                filter_wdg = Common.create_from_class_path(filter_name)
                span.add(filter_wdg)
                div.add(span)
            else:
                span.add("%s: " % filter_wdg.get_name())

            if expression:
                name = filter_wdg.get_name()
                value = filter_wdg.get_value()
                if value != "":
                    expression = expression.replace("{name}", name)
                    expression = expression.replace("{value}", value)
                    search.add_where(expression)
            else:
                filter_wdg.alter_search(search)

            filter_wdg.set_name(filter_name)

            span = SpanWdg(css="med")
            span.add("%s: " % filter_name)
            span.add(filter_wdg)
            div.add(span)


        table = TableWdg(search_type, view)
        table.set_search(search)
        table.do_search()
        
        widget.add(table)
        return widget



from pyasm.command import Trigger
class PrefixParentCodeTrigger(Trigger):
    '''Changes the parent code of all the children of an sobject on change
    of the parent's code'''

    def execute(my):

        delimiter = "."

        # FIXME: how to find the child sobject
        child_search_type = "simple/page"

        #sobject = my.get_sobject()
        sobject = my.get_caller()
        prev_code = sobject.get_prev_value("code")
        code = sobject.get_code()

        # skip if the code hasn't changed
        if prev_code == code:
            return

        # get all of the former children
        sobject.set_value("code", prev_code)
        children = sobject.get_all_children( child_search_type )
        sobject.set_value("code", code)

        foreign_key = sobject.get_foreign_key()
        for child in children:

            # switch the child's parent code to reflect the new code
            child.set_value(foreign_key, code)

            short_code = child.get_value("short_code", no_exception=True)
            if not short_code:
                continue

            new_child_code = "%s%s%s" % ( code, delimiter, short_code )
            child.set_value("code", new_child_code)
            child.commit()




