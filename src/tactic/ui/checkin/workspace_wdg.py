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


__all__ = ['WorkspaceWdg']

from pyasm.common import Environment, jsonloads, jsondumps
from pyasm.biz import Project
from pyasm.web import DivWdg, Table, WidgetSettings
from tactic.ui.common import BaseRefreshWdg
from pyasm.widget import IconWdg, RadioWdg
from tactic.ui.widget import IconButtonWdg

from scm_dir_list_wdg import get_onload_js as scm_get_onload_js

class WorkspaceWdg(BaseRefreshWdg):


    def get_display(my):

        top = my.top
        top.add_class("spt_workspace_content")
        my.set_as_panel(top)
        top.add_color("color", "color")
        top.add_color("background", "background")
        top.add_style("min-width: 600px")
        top.add_style("min-height: 400px")


        # NOTE: is there ever a time when this is not loaded already?
        top.add_behavior( {
            'type': 'load',
            'cbjs_action': scm_get_onload_js()
        } )



        sync_dir = Environment.get_sandbox_dir()
        project = Project.get()
        depot = project.get_value("location", no_exception=True)
        if not depot:
            depot = project.get_code()
        location = '//%s' % depot


        workspace = my.kwargs.get("workspace")
        if not workspace:
            workspace = WidgetSettings.get_value_by_key("current_workspace")
        else:
            WidgetSettings.set_value_by_key("current_workspace", workspace)

        if not workspace:
            workspace = 'main'


        workspaces = my.kwargs.get("workspaces")
        if not workspaces:
            workspaces = []
        elif isinstance(workspaces, basestring):
            workspaces = workspaces.replace("'", '"')
            workspaces = jsonloads(workspaces)

        top.add_behavior( {
            'type': 'load',
            'depot': depot,
            'sync_dir': sync_dir,
            'cbjs_action': '''
            spt.scm.sync_dir = bvr.sync_dir;
            spt.scm.depot = bvr.depot;
            '''
        } )



        inner = DivWdg()
        top.add(inner)

        table = Table()
        inner.add(table)
        table.add_style("width: 100%")

        table.add_row()
        th = table.add_header("")



        th = table.add_header("Workspaces")
        th.add_style("text-align: left")
        th = table.add_header("Description")
        th.add_style("text-align: left")
        th = table.add_header("Owner")
        th.add_style("text-align: left")
        th = table.add_header("Root")
        th.add_style("text-align: left")


        bgcolor = table.get_color("background", -8)
        table.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_workspace_item',
            'bgcolor': bgcolor,
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", bvr.bgcolor);
            '''
        } )


        table.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_workspace_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", '');
            '''
        } )


        table.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': "spt_workspace_radio",
            'cbjs_action': '''
            var value = bvr.src_el.value;

            spt.app_busy.show("Setting current workspace to " + value);
            var server = TacticServerStub.get();
            server.set_widget_setting("current_workspace", value);

            var top = bvr.src_el.getParent(".spt_checkin_top");
            top.removeAttribute("spt_sandbox_dir");
            spt.panel.refresh(top);
            spt.app_busy.hide();

            '''
        } )


        for c in workspaces:
            name = c.get("client")

            tr = table.add_row()
            tr.add_class("spt_workspace_item")

            radio = RadioWdg("workspace")
            radio.add_class("spt_workspace_radio")
            table.add_cell(radio)
            radio.set_option("value", name)
            if name == workspace:
                radio.set_checked()


            table.add_cell(name)
            table.add_cell(c.get("Description"))
            table.add_cell(c.get("Owner"))
            table.add_cell(c.get("Root"))

        if not workspaces:
            ws_div = DivWdg()
            table.add_row()
            table.add_cell(ws_div)
            ws_div.add_style("height: 60px")
            ws_div.add_style("width: 300px")
            ws_div.add("<b>No workspaces defined</b>")
            ws_div.add_color("color", "color3")
            ws_div.add_color("background", "background3")
            ws_div.add_border()
            ws_div.add_style("margin-top: 30px")
            ws_div.add_style("margin-bottom: 30px")
            ws_div.add_style("margin-left: auto")
            ws_div.add_style("margin-right: auto")
            ws_div.add_style("padding-top: 30px")
            ws_div.add_style("text-align: center")




        inner.add("<hr/>")

        if my.kwargs.get("workspaces") == None:
            inner.add_behavior( {
            'type': 'load',
            'location': location,
            'sync_dir': sync_dir,
            'cbjs_action': '''

spt.workspace = {}
spt.workspace.load = function(el) {
    var workspaces = spt.scm.run("get_workspaces",[]);

    console.log(workspaces);

    var class_name = 'tactic.ui.checkin.workspace_wdg.WorkspaceWdg';
    var kwargs = {
        workspaces: workspaces,
    }
    var top = el.getParent(".spt_workspace_content");
    spt.panel.load(top, class_name, kwargs);
}

spt.workspace.load(bvr.src_el);

        ''' } )


        return top




