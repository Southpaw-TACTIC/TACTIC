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

from pyasm.common import Environment, jsonloads, jsondumps, Common
from pyasm.biz import Project
from pyasm.web import SpanWdg, DivWdg, FloatDivWdg, Table, WidgetSettings, HtmlElement
from tactic.ui.common import BaseRefreshWdg
from pyasm.widget import IconWdg, RadioWdg
from tactic.ui.widget import IconButtonWdg, CheckinSandboxListWdg, ButtonNewWdg
from tactic.ui.input import TextInputWdg
from pyasm.search import SearchKey, Search

class SimpleCheckinWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        'checkout_action': {
            'description': 'Predefined Check-out action',
            'type': 'SelectWdg',
            'values': 'latest|latest (version_omitted)|latest versionless|open file browser',
            'order': 1,
            'category': 'Options'
        },
      
        'checkin_action': {
            'description': 'Predefined check-in action',
            'type': 'SelectWdg',
            'values': 'browse_and_checkin',
            'order': 2,
            'category': 'Options'
        }
  
    }

    def init(self):
        self.checkin_action = self.kwargs.get('checkin_action') 
        if not self.checkin_action:
            self.checkin_action = 'browse_and_checkin'
        self.checkout_action = self.kwargs.get('checkout_action') 
        if not self.checkout_action:
            self.checkout_action = 'latest'
        self.process = '' 
        self.context = ''

    def get_display(self):

        search_key = self.kwargs.get("search_key")
        msg = None
        base_search_type = SearchKey.extract_search_type(search_key)
        sobject = SearchKey.get_by_search_key(search_key)
        process_div = DivWdg()
        process_div.add_style('padding-top: 10px')

        if base_search_type  in ['sthpw/task', 'sthpw/note']:
            self.process = sobject.get_value('process')
            self.context = sobject.get_value('context')
            if not self.process:
                self.process = ''

            parent = sobject.get_parent()
            if parent:
                search_key = SearchKey.get_by_sobject(parent)
            else:
                msg = "Parent for [%s] not found"%search_key
            
        else:
            self.process = self.kwargs.get('process')

        
        top = self.top
        top.add_class('spt_simple_checkin')
        top.add_color("background", "background")
        top.add_styles("position: relative")

        content = DivWdg(msg)
        top.add(content)
        #content.add_border()
        #content.add_color("background", "background3")
        #content.add_color("color", "background3")
        content.add_style("width: 600px")
        content.add_styles("margin-left: auto; margin-right: auto;")
        content.add_style("height: 200px")

        from tactic.ui.widget import CheckinWdg
        content.add_behavior( {
            'type': 'load',
            'cbjs_action': CheckinWdg.get_onload_js()
        } )


        button_div = DivWdg()
        
        content.add(process_div)

        content.add(button_div)
        button = IconWdg(title="Check-In", icon=IconWdg.CHECK_IN_3D_LG)

        title = Common.get_display_title(self.checkin_action)
        button.add_attr('title', title)


        button_div.add(button)
        button_div.set_box_shadow("1px 1px 1px 1px")
        button_div.add_style("width: 60px")
        button_div.add_style("height: 60px")
        button_div.add_style("float: left")
        button_div.add_style("background: white")
        button_div.add_class("hand")

        button_div.add_style("padding: 2px 3px 0 0")
        button_div.add_style("margin: 20px 60px 20px 200px")
        button_div.add_style("text-align: center")

        button_div.add("Check-in")

        # to be consistent with Check-in New File
        if self.process:
            checkin_process = self.process
        else:
            # Dont' specify, the user can choose later in check-in widget
            checkin_process = ''
        button.add_behavior( {
            'type': 'click_up',
            'search_key': search_key,
            'process': checkin_process,
            'context': self.context,
            'cbjs_action': '''
            var class_name = 'tactic.ui.widget.CheckinWdg';
            var applet = spt.Applet.get();


            spt.app_busy.show("Choose file(s) to check in")


            var current_dir = null;
            var is_sandbox = false;
            var refresh = false
            var values = spt.checkin.browse_folder(current_dir, is_sandbox, refresh);
            if (!values) {
                spt.app_busy.hide();
                return;
            }

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

        button_div.add_style("text-align: center")
        button_div.add("Check-out")

       
        sobject = SearchKey.get_by_search_key(search_key)

        # snapshot is retrieved for getting the process informatoin, they are not being used
        # for loading as real_time snapshot query option is used. 
        search = Search("sthpw/snapshot")
        search.add_sobject_filter(sobject)
        if self.process:
            search.add_filter("process", self.process)
        search.add_filter("is_latest", True)
        snapshot = search.get_sobject()

        if not self.process and snapshot:
            self.process = snapshot.get_value('process')
            # for old process-less snapshots
            if not self.process:
                self.process = snapshot.get_value('context')

        process_wdg = DivWdg(HtmlElement.b(checkin_process))
        if checkin_process:
            width = len(checkin_process)*10
        else:
            width = 10
        process_wdg.add_styles('margin-left: auto; margin-right: auto; text-align: center; width: %s'%width)
        process_div.add(process_wdg)
        # DO NOT pass in snapshot_code, get it in real time

        snapshot_codes = []
   
        show_status = True
        if self.checkout_action == 'latest':
            cbjs_action = CheckinSandboxListWdg.get_checkout_cbjs_action(self.process, show_status)
            bvr = {'snapshot_codes': snapshot_codes,
                    'real_time': True,
                    'file_types': ['main'],
                    'filename_mode': 'repo',
                    'cbjs_action': cbjs_action}

        elif self.checkout_action == 'latest (version_omitted)':
            cbjs_action = CheckinSandboxListWdg.get_checkout_cbjs_action(self.process, show_status)
            bvr = {'snapshot_codes':snapshot_codes,
                    'real_time': True,
                    'file_types': ['main'],
                    'filename_mode': 'versionless',
                    'cbjs_action': cbjs_action}

        elif self.checkout_action == 'latest versionless':
            cbjs_action = CheckinSandboxListWdg.get_checkout_cbjs_action(self.process, show_status)
            bvr = {'snapshot_codes':snapshot_codes,
                    'real_time': True,
                    'versionless': True,
                    'file_types': ['main'],
                    'filename_mode': 'versionless',
                    'cbjs_action': cbjs_action}
       
        elif self.checkout_action == 'open file browser':
            bvr =  {
           
            'cbjs_action': '''
            var class_name = 'tactic.ui.checkin.SObjectDirListWdg';
            var kwargs = {
                search_keys: [bvr.search_key],
                process: '%s' 
            };
            spt.panel.load_popup("Check-out", class_name, kwargs);
            '''%self.process
            }
        bvr.update({ 'type': 'click_up', 'search_key': search_key})
        button.add_behavior(bvr)
        title = Common.get_display_title(self.checkout_action)
        button.add_attr('title', title)


        
        #TODO: remove these margin-top which is used to compensate all the ButtonNewWdg top extra white space
        
        content.add("<br clear='all'/>")
        status_div = DivWdg()
        status_div.add_style('margin: 20px 0 0 10px')
        status_div.add_style('width: 100%')
        text_info = FloatDivWdg()
        text_info.add_styles('padding: 4px; width: 500px')
        text_info.add_style('margin-top: 8px')
        text_info.add_attr('title','Displays the last checked out file path')

        text_info.add_border()
        text_info.set_round_corners()

        text_content = DivWdg()
        text_content.add('&nbsp;')
        text_content.add_class('spt_status_area')

        text_info.add(text_content)
        label = FloatDivWdg('path:')
        label.add_style('margin: 12px 6px 0 6px')

        # button
        button = ButtonNewWdg(title="Explore", icon=IconWdg.FOLDER_GO)
        button.add_style('padding-bottom: 15px')
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
            var applet = spt.Applet.get();
            var status_div = bvr.src_el.getParent('.spt_simple_checkin').getElement('.spt_status_area');
            var value = status_div.get('text');

            var dir_name = spt.path.get_dirname(value);
            if (dir_name)
                applet.open_explorer(dir_name);
        '''
        } )

        status_div.add(label)
        status_div.add(text_info)
        content.add(status_div)
        content.add(button)
    

        content.add_behavior({'type':'load',
            'cbjs_action': ''' 
            
            if (!spt.Applet.applet) {
                spt.api.app_busy_show('Initializing Java', 'Please wait...');
                var exec = function() {var applet = spt.Applet.get()};
                spt.api.app_busy_hide(exec);
            }'''})
        
        return top

