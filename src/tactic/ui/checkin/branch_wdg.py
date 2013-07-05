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


__all__ = ['BranchWdg']

from pyasm.common import Environment, jsonloads, jsondumps
from pyasm.biz import Project
from pyasm.web import DivWdg, Table, WidgetSettings
from tactic.ui.common import BaseRefreshWdg
from pyasm.widget import IconWdg, RadioWdg
from tactic.ui.widget import IconButtonWdg

from scm_dir_list_wdg import get_onload_js as scm_get_onload_js

class BranchWdg(BaseRefreshWdg):


    def get_display(my):

        top = my.top
        top.add_class("spt_branch_content")
        my.set_as_panel(top)
        top.add_color("color", "color")
        top.add_color("background", "background")
        #top.add_border()
        #top.add_style("padding", "10px")
        top.add_style("min-width: 600px")
        top.add_style("min-height: 400px")

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


        branch = my.kwargs.get("branch")
        if not branch:
            branch = WidgetSettings.get_value_by_key("current_branch")
        else:
            WidgetSettings.set_value_by_key("current_branch", branch)

        if not branch:
            branch = 'main'


        branches = my.kwargs.get("branches")
        if not branches:
            branches = []
        elif isinstance(branches, basestring):
            branches = branches.replace("'", '"')
            branches = jsonloads(branches)

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

        th = table.add_header("Branches")
        th.add_style("text-align: left")
        th = table.add_header("Options")
        th.add_style("text-align: left")
        th = table.add_header("Owner")
        th.add_style("text-align: left")
        th = table.add_header("Check-out")
        th.add_style("text-align: left")

        bgcolor = table.get_color("background", -8)
        table.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_branch_item',
            'bgcolor': bgcolor,
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", bvr.bgcolor);
            '''
        } )
        table.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_branch_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", '');
            '''
        } )


        table.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': "spt_branch_radio",
            'cbjs_action': '''
            var value = bvr.src_el.value;


            spt.app_busy.show("Setting current branch to " + value);
            var server = TacticServerStub.get();

            server.set_widget_setting("current_branch", value);

            var top = bvr.src_el.getParent(".spt_checkin_top");
            top.removeAttribute("spt_sandbox_dir");
            spt.panel.refresh(top);
            spt.app_busy.hide();

            '''
        } )


        for c in branches:
            name = c.get("branch")

            tr = table.add_row()
            tr.add_class("spt_branch_item")

            radio = RadioWdg("branch")
            radio.add_class("spt_branch_radio")
            table.add_cell(radio)
            radio.set_option("value", name)
            if name == branch:
                radio.set_checked()


            table.add_cell(name)
            table.add_cell(c.get("Options"))
            table.add_cell(c.get("Owner"))

            icon = IconButtonWdg(title="Check-out", icon=IconWdg.CHECK_OUT_SM)
            table.add_cell(icon)

            icon.add_behavior( {
                'type': 'click_up',
                'branch': c.get("branch"),
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_branch_content");
                top.setAttribute("spt_brange", bvr.branch);

                spt.app_busy.show("Checking out branch ["+bvr.branch+"]");
                spt.scm.checkout("new_project/"+bvr.branch);
                spt.app_busy.hide();

                '''
            } )



        inner.add("<hr/>")

        if my.kwargs.get("branches") == None:
            inner.add_behavior( {
            'type': 'load',
            'location': location,
            'sync_dir': sync_dir,
            'cbjs_action': '''

spt.branch = {}
spt.branch.load = function(el) {
    var branches = spt.scm.run("get_branches",[]);

    var class_name = 'tactic.ui.checkin.branch_wdg.BranchWdg';
    var kwargs = {
        branches: branches,
    }
    var top = el.getParent(".spt_branch_content");
    spt.panel.load(top, class_name, kwargs);
}

spt.branch.load(bvr.src_el);

        ''' } )


        return top




