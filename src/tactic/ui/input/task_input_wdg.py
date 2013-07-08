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


__all__ = ['TaskSObjectInputWdg']

from pyasm.biz import Project
from pyasm.search import Search, SearchKey
from pyasm.web import WebContainer, Widget, SpanWdg
from pyasm.widget import BaseInputWdg, SelectWdg, TextWdg, IconButtonWdg, IconWdg, HiddenWdg 
from pyasm.common import TacticException


class TaskSObjectInputWdg(BaseInputWdg):
    ''' This is mostly used in EditWdg only, for display purpose rather than editing.
    When used in insert, it will insert the parent_key '''

    def get_display(my):
        current = my.get_current_sobject()

        if current.is_insert():
            widget = Widget()
            parent_key = my.get_option('parent_key')
            if parent_key:
                parent = SearchKey.get_by_search_key(parent_key)
                if parent:
                    widget.add(SpanWdg(parent.get_code()))
            else:

                # use the project as the parent
                parent = Project.get()
                widget.add(SpanWdg("Project: %s" % parent.get_code()))

                #raise TacticException('Task creation aborted since parent is undetermined. Please check the configuration that generates this table.')

            text = HiddenWdg(my.get_input_name())
            text.set_option('size','40')
            text.set_value(parent_key)

            widget.add(text)
            return widget

        else:
           

            search_type = current.get_value('search_type')
            if not search_type:
                return "No parent type"
            
            widget = Widget()
            parent = current.get_parent()
            if parent:
                widget.add(parent.get_code())
                return widget
        
        # What is this look up code for?
        text = TextWdg(my.get_input_name())
        behavior = {
            'type': 'keyboard',
            'kbd_handler_name': 'DgTableMultiLineTextEdit'
        }
        text.add_behavior(behavior)



        widget.add(text)

        icon = IconButtonWdg("Look up", IconWdg.ZOOM)
        icon.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
                var options = {
                    title: '%s',
                    class_name: 'tactic.ui.panel.ViewPanelWdg'
                };
                var args = {
                    search_type: '%s',
                    view: 'list'
                };
                spt.popup.get_widget( {}, {options: options, args: args} );
            ''' % (search_type, search_type)
        } )
        widget.add(icon)

        return widget

