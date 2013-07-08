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


__all__ = ['ChangelistWdg']

from pyasm.common import Environment, jsonloads, jsondumps
from pyasm.biz import Project
from pyasm.web import DivWdg, Table, WidgetSettings
from tactic.ui.common import BaseRefreshWdg
from pyasm.widget import IconWdg, RadioWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg

from scm_dir_list_wdg import get_onload_js as scm_get_onload_js

class ChangelistWdg(BaseRefreshWdg):


    def get_display(my):

        top = my.top
        top.add_class("spt_changelist_content")
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
        # HARD CODED
        project = Project.get()
        depot = project.get_value("location", no_exception=True)
        if not depot:
            depot = project.get_code()
        location = '//%s' % depot


        changelist = my.kwargs.get("changelist")
        if not changelist:
            changelist = WidgetSettings.get_value_by_key("current_changelist")
        else:
            WidgetSettings.set_value_by_key("current_changelist", changelist)

        if not changelist:
            changelist = 'default'


        changelists = my.kwargs.get("changelists")
        if not changelists:
            changelists = []
        elif isinstance(changelists, basestring):
            changelists = changelists.replace("'", '"')
            changelists = jsonloads(changelists)

        top.add_behavior( {
            'type': 'load',
            'sync_dir': sync_dir,
            'depot': depot,
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
        table.add_color("background", "background", -3)

        table.add_row()
        th = table.add_header("")

        th = table.add_header("Changelist")
        th.add_style("text-align: left")
        th = table.add_header("Description")
        th.add_style("text-align: left")
        th = table.add_header("# Items")
        th.add_style("text-align: left")
        th = table.add_header("Status")
        th.add_style("text-align: left")
        th = table.add_header("View")
        th.add_style("text-align: left")
        th = table.add_header("Delete")
        th.add_style("text-align: left")
        #table.set_unique_id()
        #table.add_smart_styles("spt_changelist_item", {
        #    'text-align: right'
        #    } ))

        bgcolor = table.get_color("background", -8)
        table.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_changelist_item',
            'bgcolor': bgcolor,
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", bvr.bgcolor);
            '''
        } )
        table.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_changelist_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", '');
            '''
        } )


        table.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': "spt_changelist_radio",
            'cbjs_action': '''

            var changelist = bvr.src_el.value;
            var top = bvr.src_el.getParent(".spt_changelist_content");
            top.setAttribute("spt_changelist", changelist);
            spt.app_busy.show("Loading Changelists Information");
            spt.changelist.load(bvr.src_el, changelist);
            spt.app_busy.hide();

            '''
        } )




        for c in changelists:
            num_items = len(c.get("info"))
            name = c.get("change")

            tr = table.add_row()
            tr.add_class("spt_changelist_item")

            radio = RadioWdg("changelist")
            radio.add_class("spt_changelist_radio")
            table.add_cell(radio)
            radio.set_option("value", name)
            if name == changelist:
                radio.set_checked()


            table.add_cell(name)
            table.add_cell(c.get("desc"))
            table.add_cell(num_items)
            table.add_cell(c.get("status"))

            if num_items:
                icon = IconButtonWdg(title="View", icon=IconWdg.ZOOM)

                icon.add_behavior( {
                    'type': 'click_up',
                    'changelist': c.get("change"),
                    'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_changelist_content");
                    top.setAttribute("spt_changelist", bvr.changelist);

                    spt.app_busy.show("Loading Changelist");
                    spt.changelist.load(bvr.src_el, bvr.changelist);
                    spt.app_busy.hide();

                    '''
                } )
            else:
                icon = ''
            table.add_cell(icon)

            if not num_items and name != 'default':
                icon = IconButtonWdg(title="Delete Changelist", icon=IconWdg.DELETE)
            else:
                icon = ""

            table.add_cell(icon)




        inner.add("<hr/>")


        files = my.kwargs.get("files")
        if isinstance(files, basestring):
            files = files.replace("'", '"')
            files = jsonloads(files)



        if files == None:
            inner.add_behavior( {
                'type': 'load',
                'location': location,
                'changelist': changelist,
                'sync_dir': sync_dir,
                'cbjs_action': '''

spt.changelist = {}
spt.changelist.load = function(el, changelist) {
    var applet = spt.Applet.get();
    var changelists = spt.scm.run("get_changelists_by_user",[]);
    var dflt = {
        'change': 'default',
        'status': 'pending'
    }
    changelists.push(dflt);
    changelists = changelists.reverse();
    for (var i = 0; i < changelists.length; i++) {
        var info = spt.scm.run("get_changelist_files",[changelists[i].change]);
        changelists[i]['info'] = info;
    }

    // get the current chnage list
    var files = spt.scm.run("get_changelist_files",[changelist]);
    var path_info = {};
    var sizes = [];
    for ( var i = 0; i < files.length; i++) {

        // FIXME: perforce specific
        var path = files[i].depotFile;
        path = path.replace(bvr.location, bvr.sync_dir);
        files[i].path = path;

        var size;
        if (applet.exists(path)) {
            var info = applet.get_path_info(path);
            size = info.size;
        }
        else {
            size = 0;
        }
        sizes.push(size);
        path_info[path] = 'editable';
    }
    //var ret_val = spt.scm.status(bvr.sync_dir);
    //console.log(ret_val);

    var class_name = 'tactic.ui.checkin.changelist_wdg.ChangelistWdg';
    var kwargs = {
        files: files,
        sizes: sizes,
        changelist: changelist,
        changelists: changelists,
        path_info: path_info,
    }
    var top = el.getParent(".spt_changelist_content");
    spt.panel.load(top, class_name, kwargs);

}
spt.changelist.load(bvr.src_el, bvr.changelist);
            '''
        } )

        content = DivWdg()
        inner.add(content)
        content.add_class("spt_changelist_content")


        if files == None:

            loading_wdg = DivWdg()
            content.add(loading_wdg)
            loading_wdg.add("<b>Loading ...</b>")
            loading_wdg.add_style("padding: 30px")



        elif files:
            title_wdg = DivWdg()
            title_wdg.add_style("height: 15px")
            title_wdg.add("Changelist: [%s]" % changelist)
            content.add(title_wdg)
            title_wdg.add_gradient("background", "background", -5)
            title_wdg.add_style("padding: 5px")
            title_wdg.add_border()

            #button = SingleButtonWdg(tip='Add New Changelist', icon=IconWdg.ADD)
            #content.add(button)

            content.add("<br/>")

            paths = [x.get("path") for x in files]
            sizes = my.kwargs.get("sizes")
            path_info = my.kwargs.get("path_info")
            from scm_dir_list_wdg import ScmDirListWdg
            # dummy search_key
            search_key = "sthpw/virtual?code=xx001"
            dir_list_wdg = ScmDirListWdg(
                    base_dir=sync_dir,
                    paths=paths,
                    sizes=sizes,
                    path_info=path_info,
                    all_open=True,
                    #search_key=search_key
            )
            content.add(dir_list_wdg)

        else:

            content.add("Changelist: [%s]" % changelist)
            content.add("<br/>"*2)

            no_files_wdg = DivWdg()
            content.add(no_files_wdg)
            no_files_wdg.add_style("padding: 20px")
            no_files_wdg.add_border()
            no_files_wdg.add("No files in changelist")

            no_files_wdg.add_color("color", "color3")
            no_files_wdg.add_color("background", "background3")
            no_files_wdg.add_style("font-weight: bold")
            no_files_wdg.add_style("text-align: center")



        return top




