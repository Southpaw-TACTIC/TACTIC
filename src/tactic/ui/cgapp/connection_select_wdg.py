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
__all__ = ['ConnectionSelectWdg']

from pyasm.common import Xml
from pyasm.web import Widget, DivWdg, HtmlElement, SpanWdg, WebContainer, Table
from pyasm.widget import SelectWdg, FilterSelectWdg, WidgetConfig, HiddenWdg, IconWdg


from tactic.ui.common import BaseRefreshWdg


class ConnectionSelectWdg(Widget):

    def get_display(my):

        widget = DivWdg(id='AppSelectWdg', css='spt_panel')
        widget.add_style('padding-left','6px')
        #widget.set_attr('spt_class_name', 'tactic.ui.cgapp.ConnectionSelectWdg') 
        #widget.add_style("float: right")
       

        from tactic.ui.activator import ButtonForDropdownMenuWdg

        menu_data = []
        menu_id = "app_select_menu"
        apps = ['Maya','XSI','Houdini']
        
        for app in apps:
            
            menu_data.append( {
                "type": "action",
                "label": app,
                "bvr_cb": {
                
                    'cbjs_action': '''spt.api.Utility.save_widget_setting('app|select','%s');
                                    var activator =spt.ctx_menu.get_activator(bvr);  var top = spt.get_parent_panel(activator); 
                                    spt.panel.refresh(top, {}, true);''' %app 
                }
            } )

        menu = {
            'menu_id': menu_id,
            'width': 160,
            'allow_icons': False,
            'opt_spec_list': menu_data
        }


        button = ButtonForDropdownMenuWdg( id = "%s_Btn" % menu_id,
                                          title = "Select Connection Type",
                                          menus = [menu],
                                          width =160,
                                          match_w = True)
        #widget.add(app_select)
        widget.add(button)

        return widget


