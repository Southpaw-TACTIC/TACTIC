###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
 
__all__ = [ 'SystemInfoWdg', 'LinkLoadTestWdg' ,'ClearSideBarCache']

import os, platform, sys

from pyasm.common import Environment, Config, Common
from pyasm.security import Login
from tactic.ui.common import BaseRefreshWdg
from pyasm.web import DivWdg, Table, WebContainer, Widget, SpanWdg
from pyasm.search import Search
from pyasm.biz import Project
from pyasm.widget import CheckboxWdg, TextWdg
from pyasm.command import Command
from tactic.ui.widget import ActionButtonWdg

class SystemInfoWdg(BaseRefreshWdg):

    
    def get_display(my):

        top = DivWdg()
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("min-width: 600px")

        os_name = os.name

        top.set_unique_id()
        top.add_smart_style("spt_info_title", "background", my.top.get_color("background3"))
        top.add_smart_style("spt_info_title", "padding", "3px")
        top.add_smart_style("spt_info_title", "font-weight", "bold")




        # server
        title_div = DivWdg()
        top.add(title_div)
        title_div.add("Server")
        title_div.add_class("spt_info_title")


        os_div = DivWdg()
        top.add(os_div)

        os_info = platform.uname()
        try:
            os_login = os.getlogin()
        except Exception:
            os_login = os.environ.get("LOGNAME")

        table = Table()
        table.add_color("color", "color")
        table.add_style("margin: 10px")
        os_div.add(table)

        for i, title in enumerate(['OS','Node Name','Release','Version','Machine']):
            table.add_row()
            td = table.add_cell("%s: " % title)
            td.add_style("width: 150px")
            table.add_cell( os_info[i] )

        table.add_row()
        table.add_cell("CPU Count: ")
        try :
            import multiprocessing
            table.add_cell( multiprocessing.cpu_count() )
        except (ImportError,  NotImplementedError):
            table.add_cell( "n/a" )


        table.add_row()
        table.add_cell("Login: ")
        table.add_cell( os_login )
            
        # python
        title_div = DivWdg()
        top.add(title_div)
        title_div.add("Python")
        title_div.add_class("spt_info_title")


        table = Table()
        table.add_color("color", "color")
        table.add_style("margin: 10px")
        top.add(table)
        table.add_row()
        td = table.add_cell("Version: ")
        td.add_style("width: 150px")
        table.add_cell( sys.version )


        # client
        title_div = DivWdg()
        top.add(title_div)
        title_div.add("Client")
        title_div.add_class("spt_info_title")

        web = WebContainer.get_web()
        user_agent = web.get_env("HTTP_USER_AGENT")

        table = Table()
        table.add_color("color", "color")
        table.add_style("margin: 10px")
        top.add(table)
        table.add_row()
        td = table.add_cell("User Agent: ")
        td.add_style("width: 150px")
        table.add_cell( user_agent )

        table.add_row()
        td = table.add_cell("TACTIC User: ")
        table.add_cell( web.get_user_name() )


        top.add('<br>')
        my.handle_load_balancing(top)

 
        # performance test
        top.add('<br>')
        title_div = DivWdg()
        top.add(title_div)
        title_div.add("Performance Test")
        title_div.add_class("spt_info_title")

        performance_wdg = PerformanceWdg()
        top.add(performance_wdg)

      
        top.add('<br>')

        # mail server
        title_div = DivWdg()
        top.add(title_div)
        title_div.add("Mail Server")
        title_div.add_class("spt_info_title")

        table = Table(css='email_server')
        table.add_color("color", "color")
        table.add_style("margin: 10px")
        top.add(table)
        table.add_row()
        td = table.add_cell("Server: ")
        td.add_style("width: 150px")
        mailserver = Config.get_value("services", "mailserver")
        has_mailserver = True
        if mailserver:
            table.add_cell( mailserver )
        else:
            table.add_cell("None configured")
            has_mailserver = False

        login = Login.get_by_login('admin')
        login_email = login.get_value('email')
        table.add_row()
        td = table.add_cell("From: ")
        td.add_style("width: 150px")
        text = TextWdg('email_from')
        text.set_attr('size', '40')
        text.set_value(login_email)
        text.add_class('email_from')
        table.add_cell(text)
        
        table.add_row()
        td = table.add_cell("To: ")
        td.add_style("width: 150px")
        text = TextWdg('email_to')
        text.set_attr('size', '40')
        text.add_class('email_to')
        text.set_value(login_email)
        table.add_cell(text)


        button = ActionButtonWdg(title='Email Send Test')
        table.add_row_cell('<br>')
        table.add_row()

        table.add_cell(button)
        button.add_style("float: right")
        button.add_behavior( {
        'type': 'click_up',
        'has_mailserver': has_mailserver,
        'cbjs_action': '''
             if (!bvr.has_mailserver) {
                spt.alert('You have to fill in mailserver and possibly other mail related options in the TACTIC config file to send email.');
                return;
            }
             var s = TacticServerStub.get();
             try {

                spt.app_busy.show('Sending email'); 
                var from_txt = bvr.src_el.getParent('.email_server').getElement('.email_from');
                var to_txt = bvr.src_el.getParent('.email_server').getElement('.email_to');
                
                var rtn = s.execute_cmd('pyasm.command.EmailTriggerTestCmd', 
                {'sender_email': from_txt.value,
                 'recipient_emails': to_txt.value.split(','),
                 'msg': 'Simple Email Test by TACTIC'}
                 );
                 if (rtn.status == 'OK') {
                    spt.info("Email sent successfully to " + to_txt.value)
                 }
             } catch(e) {
                spt.alert(spt.exception.handler(e));
             }
             spt.app_busy.hide();


        '''
        })

    
    
        top.add('<br>')
        my.handle_directories(top)


        #table.add_row()
        #td = table.add_cell("TACTIC User: ")
        #table.add_cell( web.get_user_name() )

        top.add('<br>')
        top.add(DivWdg('Link Test', css='spt_info_title'))
        top.add('<br>')
        top.add(LinkLoadTestWdg())

        top.add('<br>')
        my.handle_python_script_test(top)
        top.add('<br>')
        my.handle_sidebar_clear(top)



        return top



    def handle_directories(my, top):
        # deal with asset directories
        top.add(DivWdg('Asset Folders', css='spt_info_title'))
        mailserver = Config.get_value("services", "mailserver")
        table = Table()
        table.add_color("color", "color")
        table.add_style("margin: 10px")
        top.add(table)
        table.add_row()
        td = table.add_cell("asset_base_dir: ")
        td.add_style("width: 150px")
        asset_base_dir = Config.get_value("checkin", "asset_base_dir")
        if asset_base_dir:
            table.add_cell( asset_base_dir )
            tr = table.add_row()
            tr.add_style('border-bottom: 1px #bbb solid')
            # check if it is writable
            is_writable = os.access(asset_base_dir, os.W_OK)
            span = SpanWdg("writable:")
            span.add_style('padding-left: 20px')
            td = table.add_cell(span)
            td = table.add_cell(str(is_writable))
        else:
            table.add_cell( "None configured")

        client_os = Environment.get_env_object().get_client_os()
        if os.name == 'nt':
            os_name = 'win32'
        else:
            os_name = 'linux'
        if client_os == 'nt':
            client_os_name = 'win32'
        else:
            client_os_name = 'linux'

        env = Environment.get()
        client_handoff_dir = env.get_client_handoff_dir(include_ticket=False, no_exception=True)
        client_asset_dir = env.get_client_repo_dir()

        table.add_row()
        td = table.add_cell("%s_server_handoff_dir: " % os_name)
        td.add_style("width: 150px")
        handoff_dir = Config.get_value("checkin", "%s_server_handoff_dir" % os_name)
        
        if handoff_dir:
            table.add_cell( handoff_dir )
            table.add_row()
            # check if it is writable
            is_writable = os.access(handoff_dir, os.W_OK)
            span = SpanWdg("writable:")
            span.add_style('padding-left: 20px')
            td = table.add_cell(span)
            td = table.add_cell(str(is_writable))
        else:
            table.add_cell( "None configured")

        table.add_row()
        td = table.add_cell("%s hand-off test: " % client_os_name)
        td.add_style("width: 150px")

        button = ActionButtonWdg(title='Test')
        button.add_behavior( {
            'type': 'click_up',
            'handoff_dir': client_handoff_dir,
            'asset_dir': client_asset_dir,
            'cbjs_action': '''
            
            var env = spt.Environment.get();


            var applet = spt.Applet.get();
            var handoff_state = applet.exists(bvr.handoff_dir);
            var asset_state = applet.exists(bvr.asset_dir);
            if (asset_state == false) {
                env.set_transfer_mode("web");
                spt.error('client repo directory is not accessible: ' + bvr.asset_dir);
            }
            else if (handoff_state == false) {
                env.set_transfer_mode("web");
                spt.error('client handoff directory is not accessible: ' + bvr.handoff_dir);
            }
            else {
                env.set_transfer_mode("copy");
                spt.info('<div>client handoff directory: ' + bvr.handoff_dir + '</div><br><div>client repo directory :' + bvr.asset_dir +  '</div><br><div> can be successfully accessed.</div>', {type:'html'});
            }
            '''
            } )

        table.add_cell( button )
     


    def handle_python_script_test(my, top):
        top.add(DivWdg('Python Script Test', css='spt_info_title'))
        table = Table(css='script')
        table.add_color("color", "color")
        table.add_style("margin: 10px")
        table.add_style("width: 100%")
        top.add(table)
        table.add_row()
        td = table.add_cell("Script Path: ")
        td.add_style("width: 150px")
        text = TextWdg('script_path')
        td = table.add_cell(text)
        button = ActionButtonWdg(title='Run')
        table.add_cell(button)
        button.add_style("float: right")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
             var s = TacticServerStub.get();
             try {
                var path =  bvr.src_el.getParent('.script').getElement('.spt_input').value;
                if (! path)
                    throw('Please enter a valid script path');
                s.execute_cmd('tactic.command.PythonCmd', {script_path: path});
             } catch(e) {
                spt.alert(spt.exception.handler(e));
             }

        '''
        })
    
  
    
    
    def handle_load_balancing(my, top):
        # deal with asset directories
        top.add(DivWdg('Load Balancing', css='spt_info_title'))
        table = Table()
        table.add_class("spt_loadbalance")
        table.add_color("color", "color")
        table.add_style("margin: 10px")
        top.add(table)
        table.add_row()
        td = table.add_cell("Load Balancing: ")
        td.add_style("width: 150px")

        button = ActionButtonWdg(title='Test')
        td = table.add_cell(button)
        message_div = DivWdg()
        message_div.add_class("spt_loadbalance_message")
        table.add_cell(message_div)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var server = TacticServerStub.get()
        var ports = {};
        var count = 0;
        for (var i = 0; i < 50; i++) {
          var info = server.get_connection_info();
          var port = info.port;
          var num = ports[port];
          if (!num) {
            ports[port] = 1;
            count += 1;
          }
          else {
            ports[port] += 1;
          }
          // if there are 10 requests and still only one, then break
          if (i == 10 && count == 1)
            break;
        }


        // build the ports string
        x = [];
        for (i in ports) {
            x.push(i);
        }
        x.sort();
        x = x.join(", ");

        var loadbalance_el = bvr.src_el.getParent(".spt_loadbalance");
        var message_el = loadbalance_el.getElement(".spt_loadbalance_message");
        if (count > 1) {
            var message = "Yes (found " + count + " ports: "+x+")";
        }
        else {
            var message = "<blink style='background: red; padding: 3px'>Not enabled (found only port " + x + ")</blink>";
        }
        message_el.innerHTML = message
        '''
        } )

    def handle_sidebar_clear(my, top):
        top.add(DivWdg('Clear Side Bar Cache ', css='spt_info_title'))
        table = Table()
        table.add_color("color", "color")
        table.add_style("margin: 10px")
        top.add(table)
        table.add_row()
        td = table.add_cell("Clear the Side Bar Cache for all users")
        td.add_style("width: 250px")
        button = ActionButtonWdg(title='Run')
        table.add_cell(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
            try {
            var s = TacticServerStub.get();
            s.execute_cmd('tactic.ui.app.ClearSideBarCache');
            
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }
            spt.info('Side Bar cache cleared.')
        '''
        })

class ClearSideBarCache(Command):

    def execute(my):
        tmp_dir = Environment.get_tmp_dir()
        # remove the sidebar cache
        sidebar_cache_dir = "%s/cache/side_bar" % tmp_dir
        if os.path.exists(sidebar_cache_dir):
            import shutil
            shutil.rmtree(sidebar_cache_dir)

class LinkLoadTestWdg(BaseRefreshWdg):
    '''Load Pages in popup as part of a testing process'''

    def get_display(my):

        config_search_type = "config/widget_config"
         
        configs = []
	all_element_names = []
        from tactic.ui.panel import SideBarBookmarkMenuWdg
        SideBarBookmarkMenuWdg.add_internal_config(configs, ['definition'])
        for internal_config in configs:
            all_element_names = internal_config.get_element_names()

	search = Search(config_search_type)
        search.add_filter("search_type", 'SideBarWdg')
        search.add_filter("view", 'definition')
        search.add_filter("login", None)

        config = search.get_sobject()
        element_names = []
        if config:
            element_names = config.get_element_names()
            for name in element_names:
                if 'separator' in name:
                    element_names.remove(name)

	all_element_names.extend(element_names)

	
        all_element_names = [str(name) for name in all_element_names] 
	all_element_names = Common.get_unique_list(all_element_names)
        widget = DivWdg(css='spt_load_test_top')
	
	span =SpanWdg('This loads all the pages defined in the Project views in popups. It will take a few minutes.')
	widget.add(span)
	widget.add('<br>')
        div = ActionButtonWdg(title='Run')
        web = WebContainer.get_web()
        base_url = web.get_base_url().to_string()
        base_url = '%s/tactic/%s' %(base_url, Project.get_project_code())
        div.add_behavior({'type': 'click_up',
           'cbjs_action': '''
            var element_names = eval(%s);
            var all_element_names = eval(%s);
            var top = spt.get_parent(bvr.src_el, '.spt_load_test_top');
            var cb = spt.get_element(top, '.spt_input')
            if (cb.checked)
                element_list = all_element_names;
            else
                element_list = element_names
            for (var k=0; k < element_list.length; k++) {
                var name = element_list[k];
		//if (k > 3) break;

                var url = '%s/#/link/' + name;
		var bvr2 = {
                    title: name,
                    target_id: 'TEST',
                    options: {'link': name,
                    'title': name,
		    'path': '/Link Test/' + name
			},
                    is_popup: true};

                spt.side_bar.display_link_cbk(null, bvr2);

            }
            ''' %(element_names, all_element_names, base_url)})
        widget.add('<br>')
        
        cb = CheckboxWdg('include_internal', label='include built-in pages')
        
        span = SpanWdg(cb, css='med')
        span.add_color('color','color')
        widget.add(span)
        widget.add(div)

        widget.add('<br>')
        widget.add('<br>')
	
        return widget




class PerformanceWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        top.add("<br/>")
        top.add_style("margin-left: 10px")
        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
        except (ImportError, NotImplementedError):
            cpu_count = 'n/a'
        title = DivWdg()
        title.add("Click to start performance test: ")
        title.add_style("float: left")
        top.add(title)
        title.add_style("margin-top: 5px")

        button = ActionButtonWdg(title='Test')
        top.add(button)
        

        button.add_behavior( {
        'type': 'click_up',
        'cpu_count': cpu_count,
        'cbjs_action': '''

var iterations = bvr.cpu_count;

if (iterations == 'n/a') 
    iterations = 1;
var server = TacticServerStub.get();
var class_name = 'tactic.ui.panel.ViewPanelWdg';
var kwargs = {
    'search_type': 'sthpw/login',
    'view': 'table'
};
var args = {
    'args': kwargs,
    'cbjs_action': function() {
        spt.app_busy.show("Asyncronous Test", "Running Test ["+(count+1)+" / "+iterations+"]");
        count += 1;
        var time = new Date().getTime() - start;
        if (time > async_avg) {
            async_avg = time;
        }
        if (count == iterations) {
            spt.app_busy.hide();
            async_avg = async_avg / iterations;
            alert("async: "+ async_avg + " ms");
        }
    }
};


var sync_avg = 0.0;
for (var i = 0; i < iterations; i++) {
    spt.app_busy.show("Syncronous Requests", "Running Test ["+(i+1)+" / "+iterations+"]");
    var start = new Date().getTime();
    server.get_widget(class_name, args);
    var time = new Date().getTime() - start;
    sync_avg += time;
}
sync_avg = sync_avg / iterations;
spt.app_busy.hide();
alert("sync: " + sync_avg + " ms");

var async_avg = 0.0;
var count = 0;
spt.app_busy.show("Asyncronous Requests", "Running Test ["+(count+1)+" / "+iterations+"]");
var start = new Date().getTime();  
for (var i = 0; i < iterations; i++) {
    server.async_get_widget(class_name, args); 
}


        '''
        } )

        return top
