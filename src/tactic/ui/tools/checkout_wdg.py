###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

from pyasm.common import Environment
from pyasm.biz import Project
from pyasm.search import Search
from pyasm.web import DivWdg
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg, SingleButtonWdg, ButtonRowWdg, ButtonNewWdg
from tactic.ui.panel import TableLayoutWdg, ViewPanelWdg


class CheckoutWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_checkout_top")
        top.add_color("background", "background")
        top.add_style("width: 800px")

        inner = DivWdg()
        top.add(inner)

        snapshot_codes = my.kwargs.get("snapshot_codes")

        search = Search("sthpw/snapshot")
        search.add_filters("code", snapshot_codes)
        snapshots = search.get_sobjects()

        sandbox_dir = Environment.get_sandbox_dir("default")
        project_code = Project.get_project_code()
        sandbox_dir = "%s/%s" % (sandbox_dir, project_code)

        base_dir = my.kwargs.get("base_dir")

        if base_dir:
            title_div = DivWdg()
            inner.add(title_div)
            title_div.add_color("background", "background3")
            title_div.add_color("color", "color3")
            title_div.add_style("padding", "15px")
            title_div.add_style("font-weight: bold")
            title_div.add("Path: %s" % base_dir)


        inner.add("Check-out to: %s" % sandbox_dir)


        button_div = ButtonRowWdg()
        inner.add(button_div)

        button = ButtonNewWdg(title="Refresh", icon=IconWdg.REFRESH)
        button_div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_checkout_top");
            spt.panel.refresh(top)
            '''
        } )


        use_applet = True
        if use_applet:

            button = ButtonNewWdg(title="Check-out", icon=IconWdg.CHECK_OUT)
            button_div.add(button)

            button.add_behavior( {
                'type': 'click_up',
                'snapshot_codes': snapshot_codes,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_checkout_top");
                var progress = top.getElement(".spt_checkout_progress");
                var message = top.getElement(".spt_checkout_message");
                var snapshot_codes = bvr.snapshot_codes;
                var num_snapshots = snapshot_codes.length;

                var server = TacticServerStub.get();

                for (var i = 0; i < snapshot_codes.length; i++) {
                    var snapshot_code = snapshot_codes[i];

                    var percent = parseInt( i / (num_snapshots-1) * 100);
                    progress.setStyle("width", percent + "%");

                    var desc = "Checking out: "+(i+1)+" of "+num_snapshots+": "+snapshot_code;
                    message.innerHTML = desc;

                    server.checkout_snapshot(snapshot_code, null, {file_types: ['main'], filename_mode: 'source'});


                }
                progress.setStyle("width", "100%");
                progress.setStyle("background", "#0F0");
                message.innerHTML = ""
                '''
            } )


            button = ButtonNewWdg(title="Sandbox", icon=IconWdg.FOLDER_GO)
            button_div.add(button)

            button.add_behavior( {
                'type': 'click_up',
                'sandbox_dir': sandbox_dir,
                'cbjs_action': '''
                var applet = spt.Applet.get();
                applet.open_explorer(bvr.sandbox_dir);
                '''
            } )




        msg_div = DivWdg()
        inner.add(msg_div)
        msg_div.add_class("spt_checkout_message")
        msg_div.add(" ")


        progress_div = DivWdg()
        inner.add(progress_div)
        progress_div.add_style("width: auto")
        progress_div.add_style("height: 15px")
        progress_div.add_style("margin: 0px 10px 10px 10px")
        progress_div.add_border()

        progress = DivWdg()
        progress.add_class("spt_checkout_progress")
        progress_div.add(progress)
        progress.add_style("background", "#F00")
        progress.add_style("width", "0%")
        progress.add("&nbsp;")


        snapshot_div = DivWdg()
        inner.add(snapshot_div)

        layout = ViewPanelWdg(
                search_type="sthpw/snapshot",
                show_shelf=False,
                edit=False,
                width="100%",
                element_names=['preview','file','context','version','timestamp','description'],
        )
        snapshot_div.add(layout)
        layout.set_sobjects(snapshots[:50])


        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top




