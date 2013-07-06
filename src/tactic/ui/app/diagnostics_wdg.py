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

__all__ = ['DiagnosticsWdg', 'DiagnosticsHandoffDirTestCmd']

import os, random

from pyasm.common import Environment, Config, TacticException
from pyasm.command import Command
from pyasm.web import DivWdg, WebContainer
from pyasm.widget import IconButtonWdg, IconWdg, CheckboxWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import RoundedCornerDivWdg


class DiagnosticsWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    }


    def get_display(my):
        top = DivWdg()
        my.set_as_panel(top)

        title_div = DivWdg()
        title_div.add_class("maq_search_bar")
        title_div.add("Diagnostics")
        top.add(title_div)


        tool_div = DivWdg()
        top.add(tool_div)
        refresh = IconButtonWdg("Refresh", IconWdg.REFRESH)
        refresh.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_panel");
            spt.panel.refresh(top);
            '''
        } )
        tool_div.add(refresh)




        content = RoundedCornerDivWdg(hex_color_code="2F2F2F",corner_size="10")
        content.set_dimensions( width_str='300px', content_height_str=None )
        top.add(content)

        server_title_div = DivWdg()
        server_title_div.add_class("maq_search_bar")
        content.add(server_title_div)
        server_title_div.add("Server")
        server_content_div = DivWdg()
        server_content_div.add_style("padding: 10px")
        server_content_div.add(my.get_ping_wdg())
        server_content_div.add(my.get_load_balance_wdg())
        content.add(server_content_div)


        database_title_div = DivWdg()
        database_title_div.add_class("maq_search_bar")
        content.add(database_title_div)
        database_title_div.add("Database")
        database_content_div = DivWdg()
        database_content_div.add_style("padding: 10px")
        database_content_div.add(my.get_database_wdg())
        content.add(database_content_div)


        checkin_title_div = DivWdg()
        checkin_title_div.add_class("maq_search_bar")
        content.add(checkin_title_div)
        checkin_title_div.add("Database")
        checkin_content_div = DivWdg()
        checkin_content_div.add_style("padding: 10px")
        checkin_content_div.add(my.get_asset_dir_wdg() )
        checkin_content_div.add(my.get_asset_management_wdg())
        content.add(checkin_content_div)

 

        return top


    def get_ping_wdg(my):
        div = DivWdg()
        div.add_class("spt_diagnostics_ping")

        ping_div = DivWdg()
        div.add(ping_div)

        ping_div.add( CheckboxWdg() )

        ping_div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var server = TacticServerStub.get();
            var result = server.ping();

            var msg = 'wow';

            var status_el = spt.get_cousin(bvr.src_el, ".spt_diagnostics_ping",".spt_diagnostics_ping_status");
            status_el.innerHTML = result;
            '''
        } )




        # Test database connection
        ping_div.add("Test Server Ping")

        status_div = DivWdg()
        status_div.add_class("spt_diagnostics_ping_status")
        status_div.add("Checking ...")
        div.add(status_div)

        return div



    def get_asset_dir_wdg(my):
        div = DivWdg()

        asset_dir_div = DivWdg()
        div.add(asset_dir_div)

        asset_dir_div.add( CheckboxWdg() )

        asset_dir_div.add("Test Asset Directory")


        status = my.test_asset_dir()

        status_div = DivWdg()
        status_div.add_class("spt_diagnostics_asset_dir")
        status_div.add(status)
        div.add(status_div)

        return div




    def test_asset_dir(my):
        asset_dir = "/home/apache/assets"

        status = 'OK'

        exists = os.path.exists(asset_dir)
        if not exists:
            status = "Error: asset_dir [%s] does not exist" % asset_dir


        # test writing a file
        file_name = ".test.txt"
        path = "%s/%s" % (asset_dir, file_name)

        try:
            f = open(path)
            f.write("test.txt", 'w')
            f.close()
        except Exception, e:
            status = "Error: can't write to asset folder"

        return status



    def get_database_wdg(my):
        div = DivWdg()

        database_div = DivWdg()
        div.add(database_div)


        database_div.add( CheckboxWdg() )

        # Test database connection
        database_div.add("Test Database Connection")

        status_div = DivWdg()
        status_div.add_class("spt_diagnostics_database")
        status_div.add("Checking ...")
        div.add(status_div)

        return div


    def get_load_balance_wdg(my):
        div = DivWdg()
        div.add_class("spt_diagnostics_load_balance")

        load_div = DivWdg()
        div.add(load_div)
        load_div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var server = TacticServerStub.get();

            var ports = {};
            var num_ports = 0;
            for (var i=0; i<10; i++) {
                var info = server.get_connection_info();
                var port = info.port;
                if (typeof(ports[port]) == 'undefined') {
                    ports[port] = 0;
                    num_ports += 1;
                }
                ports[port] += 1
            }

            var msg = "Number of ports: "+num_ports;

            var status_el = spt.get_cousin(bvr.src_el, ".spt_diagnostics_load_balance",".spt_diagnostics_load_status");
            status_el.innerHTML = "OK - "+msg;
            '''
        } )

        # Test load balancing
        load_div.add( CheckboxWdg() )
        load_div.add("Test Load Balancing")

        load_status_div = DivWdg()
        load_status_div.add_class("spt_diagnostics_load_status")
        load_status_div.add("Checking ...")
        div.add(load_status_div)



        return div



    def get_asset_management_wdg(my):
        div = DivWdg()
        div.add_class("spt_diagnostics_dam")

        handoff_div = DivWdg()
        handoff_div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var server = TacticServerStub.get();
            var handoff_dir = server.get_handoff_dir();

            var applet = spt.Applet.get();
            applet.makedirs(handoff_dir);

            var random_number=Math.floor(Math.random()*100)
            var filename = 'test'+random_number+'.txt';
            applet.create_file(handoff_dir+'/'+filename, 'test');

            var cmd = 'tactic.ui.app.DiagnosticsHandoffDirTestCmd';
            var args = {
                handoff_dir: handoff_dir,
                filename: filename
            };
            server.execute_cmd(cmd, args);

            var status_el = spt.get_cousin(bvr.src_el, ".spt_diagnostics_dam",".spt_diagnostics_handoff_status");
            status_el.innerHTML = "OK";


            '''
        } )

        # Test handoff directory
        div.add(handoff_div)
        handoff_div.add( CheckboxWdg() )
        handoff_div.add("Test Handoff Directory")

        handoff_status_div = DivWdg()
        handoff_status_div.add_class("spt_diagnostics_handoff_status")
        handoff_status_div.add("Checking ...")
        div.add(handoff_status_div)

        return div



class DiagnosticsHandoffDirTestCmd(Command):

    def execute(my):
        handoff_dir = my.kwargs.get("handoff_dir")
        filename = my.kwargs.get("filename")
        client_path = "%s/%s" % (handoff_dir, filename)

        web = WebContainer.get_web()
        server_handoff_dir = web.get_server_handoff_dir()

        # look for a "test.txt" file
        if not os.path.exists(server_handoff_dir):
            raise TacticException("Server cannot find handoff dir [%s]" % server_handoff_dir)

        path = "%s/%s" % (server_handoff_dir, filename)
        if not os.path.exists(path):
            raise TacticException("Server cannot find test.txt [%s]" % path)

        f = open(path)
        line = f.readline()
        f.close()

        if line != 'test':
            raise TacticException("File [%s] is not correct" % client_path)




