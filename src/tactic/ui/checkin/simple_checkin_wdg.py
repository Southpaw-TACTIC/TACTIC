###########################################################
#
# Copyright (c) 2011, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['SimpleCheckinWdg']

from pyasm.common import Environment, jsonloads, jsondumps
from pyasm.biz import Project
from pyasm.web import DivWdg, Table, WidgetSettings
from tactic.ui.common import BaseRefreshWdg
from pyasm.widget import IconWdg, RadioWdg
from tactic.ui.widget import IconButtonWdg
from pyasm.search import SearchKey

class SimpleCheckinWdg(BaseRefreshWdg):


    def get_display(my):
        my.context = ''

        search_key = my.kwargs.get("search_key")
        msg = None
        base_search_type = SearchKey.extract_search_type(search_key)
        if base_search_type  in ['sthpw/task', 'sthpw/note']:
            sobject = SearchKey.get_by_search_key(search_key)
            my.process = sobject.get_value('process')
            my.context = sobject.get_value('context')
            if not my.process:
                my.process = ''

            parent = sobject.get_parent()
            if parent:
                search_key = SearchKey.get_by_sobject(parent)
            else:
                msg = "Parent for [%s] not found"%search_key
        else:
            my.process = my.kwargs.get('process')

        top = my.top
        #top.add_color("background", "background")
        #top.add_border()
        top.add_style("min-width: 600px")
        top.add_style("width: 100%")

        content = DivWdg(msg)
        top.add(content)
        #content.add_border()
        #content.add_color("background", "background3")
        #content.add_color("color", "background3")
        content.add_style("width: 600px")
        content.add_style("margin: 30px auto 30px auto")

        from tactic.ui.widget import CheckinWdg
        content.add_behavior( {
            'type': 'load',
            'cbjs_action': CheckinWdg.get_onload_js()
        } )


        button_div = DivWdg()
        content.add(button_div)
        button = IconWdg(title="Check-In", icon=IconWdg.CHECK_IN_3D_LG)
        button_div.add(button)
        button_div.set_box_shadow("1px 1px 1px 1px")
        button_div.add_style("width: 60px")
        button_div.add_style("height: 60px")
        button_div.add_style("float: left")
        button_div.add_style("background: white")
        button_div.add_class("hand")

        button_div.add_style("padding: 2px 3px 0 0")
        button_div.add_style("margin: 20px 60px 20px 200px")


        button.add_behavior( {
            'type': 'click_up',
            'search_key': search_key,
            'process': my.process,
            'context': my.context,
            'cbjs_action': '''
            var class_name = 'tactic.ui.widget.CheckinWdg';
            var applet = spt.Applet.get();


            spt.app_busy.show("Choose file(s) to check in")


            var current_dir = null;
            var is_sandbox = false;
            var refresh = false
            var values = spt.checkin.browse_folder(current_dir, is_sandbox, refresh);

            var file_paths = values.file_paths;
            if (file_paths.length == 0) {
                spt.alert("You need to select files(s) to check in.");
                spt.app_busy.hide();
                return;
            }

            spt.app_busy.hide();

            var args = {
                'search_key': bvr.search_key,
                'show_links': false,
                'show_history': false,
                'close_on_publish': true
            }
            if (bvr.process) args.process = bvr.process;
            if (bvr.context) args.context = bvr.context;

            var kwargs = {};
            kwargs.values = values;
            spt.panel.load_popup("Check-in", class_name, args, kwargs);
            /*
            var options=  {
                title: "Check-in Widget",
                class_name: 'tactic.ui.widget.CheckinWdg',
                popup_id: 'checkin_widget'
            };
            var bvr2 = {};
            bvr2.options = options;
            bvr2.values = values;
            bvr2.args = args;
            spt.popup.get_widget({}, bvr2)

            */

            '''
        } )


        button_div = DivWdg()
        content.add(button_div)
        button = IconWdg(title="Check-Out", icon=IconWdg.CHECK_OUT_3D_LG)
        button_div.add(button)
        button_div.set_box_shadow("1px 1px 1px 1px")
        button_div.add_style("width: 60px")
        button_div.add_style("height: 60px")
        button_div.add_style("float: left")
        button_div.add_style("margin: 20px")
        button_div.add_style("padding: 2px 3px 0 0")
        button_div.add_style("background: white")
        button_div.add_class("hand")



        button.add_behavior( {
            'type': 'click_up',
            'search_key': search_key,
            'cbjs_action': '''
            var class_name = 'tactic.ui.checkin.SObjectDirListWdg';
            var kwargs = {
                search_keys: [bvr.search_key]
            };
            spt.panel.load_popup("Check-out", class_name, kwargs);
            '''
        } )

 

        content.add("<br clear='all'/>")
        return top

