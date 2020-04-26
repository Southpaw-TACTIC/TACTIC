###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['LinkElementWdg']

from pyasm.common import TacticException
from pyasm.search import Search, SearchType, SearchKey
from pyasm.web import DivWdg, HtmlElement
from pyasm.command import ColumnAddCmd

from tactic.ui.common import SimpleTableElementWdg


class LinkElementWdg(SimpleTableElementWdg):


    ARGS_KEYS = {
    'icon': 'Icon to display'
    }


    def is_sortable(self):
        return False

    def is_editable(self):
        return 'optional'

    def create_required_columns(self, search_type):
        column_name = self.get_name()
        data_type = "varchar"
        cmd = ColumnAddCmd(search_type, column_name, data_type)
        cmd.execute()



    def get_display(self):
        
        sobject = self.get_current_sobject()

        value = sobject.get_value( self.get_name() )
        if value.startswith("{") and value.endswith("}"):
            value = Search.eval(value)

        if value.startswith("/"):
            new_window = 'false'
        else:
            new_window = 'true'

        top = DivWdg()
        top.add_class("hand")
        top.add_style("width: 0%")

        if value:
            top.add_behavior( {
            'type': 'click_up',
            'link': value,
            'new_window': new_window,
            'cbjs_action': '''
            if (bvr.new_window == 'false') {
                document.location = bvr.link;
            }
            else{
                var new_window = window.open(bvr.link, '_blank');
                new_window.focus();
            }
            '''
            } )


            icon = self.get_option("icon")
            if not icon:
                icon = 'jump'

            from pyasm.widget import IconWdg
            icon = icon.upper()
            icon = IconWdg( value, eval("IconWdg.%s" % icon) )
            top.add(icon)
        

        return top


