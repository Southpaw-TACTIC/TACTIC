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


__all__ = ['ScmPublishWdg', 'ScmFileSelectorWdg', 'ScmDirListWdg', 'ScmCheckinHistoryWdg', 'ScmSignInWdg']

from pyasm.common import Environment, Common, FormatValue, Directory, Config
from pyasm.search import SearchKey, Search, SearchType
from pyasm.biz import Snapshot, Project
from pyasm.web import DivWdg, Table, WidgetSettings, HtmlElement, WebContainer
from pyasm.widget import IconWdg, TextWdg, TextAreaWdg, SelectWdg, HiddenWdg, CheckboxWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import DirListWdg, ActionButtonWdg
from tactic.ui.container import DialogWdg, Menu, MenuItem, SmartMenu

import os

from checkin_dir_list_wdg import CheckinDirListWdg
from tactic.ui.widget import FileSelectorWdg


class ScmPublishWdg(BaseRefreshWdg):

    def get_display(my):

        my.sobject = my.kwargs.get("sobject")
        search_key = my.sobject.get_search_key()

        top = DivWdg()
        top.add_class("spt_checkin_publish")
        top.add_style("padding: 10px")

        margin_top = '60px'
        top.add_style("margin-top", margin_top)
        top.add_style("position: relative")


        current_changelist = WidgetSettings.get_value_by_key("current_changelist")
        current_branch = WidgetSettings.get_value_by_key("current_branch")
        current_workspace = WidgetSettings.get_value_by_key("current_workspace")

        top.add("Branch: %s<br/>" % current_branch)
        top.add("Changelist: %s<br/>" % current_changelist)
        top.add("Workspace: %s<br/>" % current_workspace)
        top.add("<br/>")


        checked_out_div = DivWdg()
        checkbox = CheckboxWdg("editable")
        top.add(checked_out_div)
        checkbox.add_class("spt_checkin_editable")
        checked_out_div.add(checkbox)
        checked_out_div.add("Leave files editable")

        top.add("<br/>")

        top.add("Publish Description<br/>")
        text = TextAreaWdg("description")
        # this needs to be set or it will stick out to the right
        text.add_style("width: 220px")
        text.add_class("spt_checkin_description")
        top.add(text)


        # add as a note
        note_div = DivWdg()
        top.add(note_div)
        note_div.add_class("spt_add_note")
        checkbox = CheckboxWdg("add_note")

        web = WebContainer.get_web()
        browser = web.get_browser()
        if browser in ['Qt']:
            checkbox.add_style("margin-top: -4px")
            checkbox.add_style("margin-right: 3px")
            note_div.add_style("margin-top: 3px")



        checkbox.add_class("spt_checkin_add_note")
        note_div.add(checkbox)
        note_div.add("Also add as note")

        top.add("<br/><br/>")


        button = ActionButtonWdg(title="Check-in", icon=IconWdg.PUBLISH, size='medium')
        top.add(button)

        my.repo_type = 'perforce'
        if my.repo_type == 'perforce':

            # the depot is set per project (unless overridden)
            project = my.sobject.get_project()
            depot = project.get_value("location", no_exception=True)
            if not depot:
                depot = project.get_code()

            asset_dir = Environment.get_asset_dir()
            sandbox_dir = Environment.get_sandbox_dir()
           
            changelist = WidgetSettings.get_value_by_key("current_changelist")
            button.add_behavior( {
            'type': 'click_up',
            'depot': depot,
            'changelist': changelist,
            'sandbox_dir': sandbox_dir,
            'search_key': search_key,
            'cbjs_action': '''

            var paths = spt.checkin.get_selected_paths();
            spt.app_busy.show("Checking in "+paths.length+" file/s into Perforce");
            var top = bvr.src_el.getParent(".spt_checkin_top");
            var description = top.getElement(".spt_checkin_description").value;
            var add_note = top.getElement(".spt_checkin_add_note").value;
            var editable = top.getElement(".spt_checkin_editable").value;

            if (editable == 'on') {
                editable = true;
            }
            else {
                editable = false;
            }

            var process = top.getElement(".spt_checkin_process").value;

            // check into TACTIC
            var server = TacticServerStub.get();

            var revisions = [];
            server.start({description: "File Check-in"});

            try {

            var top = bvr.src_el.getParent(".spt_checkin_top");
            var el = top.getElement(".spt_mode");
            var mode = el.value;

            // check-in the changelist
            var changelist = 'default';
            if (mode == 'changelist') {
                var scm_info = spt.scm.run("commit_changelist", [changelist, description]);

                for ( var i = 1; i < scm_info.length-1; i++) {
                    // the first item is the changelist number
                    //console.log(scm_info[i]);

                    var action = scm_info[i];
                    revision = action.rev;
                    revisions.push(revision);

                    // Do an inplace check-in into TACTIC
                    var path = action.depotFile;

                    var parts = path.split("/");
                    var filename = parts[parts.length-1];
                    var context = process + "/" + filename;

                    var snapshot = server.simple_checkin(bvr.search_key, context, path, {description: description, mode: "perforce", version: revision} );
                }

            }
            else {

                // check in all of the files
                for ( var i = 0; i < paths.length; i++) {
                    var path = paths[i];
                    var scm_info = spt.scm.run("commit_file", [path, description, editable]);
                    // the first item is the changelist number
                    var action = scm_info[1];
                    revision = action.rev;
                    revisions.push(revision);

                    var parts = path.split("/");
                    var filename = parts[parts.length-1];
                    var context = process + "/" + filename;

                    //path = path.replace(bvr.sandbox_dir, "//"+bvr.depot);
                    // NOTE: this assumes project == depot
                    path = path.replace(bvr.sandbox_dir, "//");

                    // Do an inplace check-in into TACTIC
                    var snapshot = server.simple_checkin(bvr.search_key, context, path, {description: description, mode: "perforce", version: revision} );
                }
            }


            if (add_note == 'on') {
                var note = [];
                note.push('CHECK-IN');
                for (var i = 0; i < paths.length; i++) { 
                    var parts = paths[i].split("/");
                    var filename = parts[parts.length-1];
                    note.push(filename+' (v'+revisions[i]+')');
                }
                note.push(': ');
                note.push(description);

                note = note.join(" ");
                server.create_note(bvr.search_key, note, {process: process});
            }
            server.finish({description: "File Check-in ["+paths.length+" file/s]"});
            spt.panel.refresh(top);

            }
            catch(e) {
              spt.error("Error detected: " + e.msg)
              //console.log(e);
              server.abort();
            }

            spt.app_busy.hide();
            '''
            } )
        else:
            button.add_behavior(behavior)





        button.add_style("margin-right: auto")
        button.add_style("margin-left: auto")
        button.add_style("margin-top: 20px")
        button.add_style("margin-bottom: 20px")



        top.add("<br clear='all'/>")
        top.add("<hr/>")
 
        hidden = HiddenWdg("checkin_type")
        top.add(hidden)
        hidden.add_class("spt_checkin_type")


        grey_out_div = DivWdg()
        top.add(grey_out_div)
        grey_out_div.add_class("spt_publish_disable")
        grey_out_div.add_style("position: absolute")
        grey_out_div.add_style("left: 0px")
        grey_out_div.add_style("top: 10px")
        grey_out_div.add_style("opacity: 0.6")
        grey_out_div.add_color("background", "background")
        grey_out_div.add_style("height: 100%")
        grey_out_div.add_style("width: 100%")
        #grey_out_div.add_border()



        return top






class ScmFileSelectorWdg(FileSelectorWdg):

    def get_display(my):

        my.search_key = my.kwargs.get("search_key")
        my.process = my.kwargs.get("process")
        my.sobject = Search.get_by_search_key(my.search_key)
        my.pipeline_code = my.kwargs.get("pipeline_code")

        top = DivWdg()
        top.add_class("spt_file_selector")
        top.add_style("position: relative")


        hidden = HiddenWdg("mode")
        #hidden = TextWdg("mode")
        hidden.add_class("spt_mode")
        top.add(hidden)



        top.add_style("padding: 5px")
        top.add_style("min-width: 500px")
        top.add_style("min-height: 400px")
        top.add_color("background", "background")
        top.add_color("color", "color")
        #top.add_border()


        logo_wdg = DivWdg()
        logo = HtmlElement.img(src="/context/icons/logo/perforce_logo.gif")
        logo_wdg.add(logo)
        top.add(logo_wdg)
        logo_wdg.add_style("opacity: 0.2")
        logo_wdg.add_style("position: absolute")
        logo_wdg.add_style("bottom: 0px")
        logo_wdg.add_style("right: 5px")



        # get some info from the config file
        """
        client_env_var = Config.get_value("perforce", "client_env_var")
        if not client_env_var:
            client_env_var = "P4Client"
        port_env_var = Config.get_value("perforce", "port_env_var")
        if not port_env_var:
            port_env_var = "P4Port"
        user_env_var = Config.get_value("perforce", "user_env_var")
        if not user_env_var:
            user_env_var = "P4User"
        password_env_var = Config.get_value("perforce", "password_env_var")
        if not password_env_var:
            password_env_var = "P4Passwd"
        """

        # {GET(sthpw/login)}_user
        host = ""
        client = ""
        user = ""
        password = ""
        port = ""

        project = my.sobject.get_project()
        depot = project.get_value("location", no_exception=True)
        if not depot:
            depot = ""


        top.add_behavior( {
            'type': 'load',
            #'client_env_var': client_env_var,
            #'port_env_var': port_env_var,
            #'user_env_var': user_env_var,
            #'password_env_var': password_env_var,
            'client': client,
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'depot': depot,
            'cbjs_action': get_onload_js()
        } )


        list_wdg = DivWdg()
        top.add(list_wdg)
        list_wdg.add_style("height: 32px")

        from tactic.ui.widget import SingleButtonWdg, ButtonNewWdg, ButtonRowWdg

        button_row = ButtonRowWdg()
        list_wdg.add(button_row)
        button_row.add_style("float: left")

        button = ButtonNewWdg(title="Refresh", icon=IconWdg.REFRESH, long=False)
        button_row.add(button)
        button.add_style("float: left")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.app_busy.show("Reading file system ...")
        var top = bvr.src_el.getParent(".spt_checkin_top");
        spt.panel.refresh(top);
        spt.app_busy.hide();
        '''
        } )



        button = ButtonNewWdg(title="Check-out", icon=IconWdg.CHECK_OUT, long=False)
        button_row.add(button)

        my.sandbox_dir = my.kwargs.get("sandbox_dir")



        # what are we trying to do here???
        #my.root_sandbox_dir = Environment.get_sandbox_dir()
        #project = my.sobject.get_project()
        #my.root_sandbox_dir = "%s/%s" % (my.root_sandbox_dir, project.get_code())
        #repo_dir = my.sandbox_dir.replace("%s/" % my.root_sandbox_dir, "")
        #repo_dir = "%s/%s" % (project.get_code(), repo_dir)




        # checkout command requires either starting with //<depot>/ or just
        # the relative path to the root.  The following removes
        # the root of the sandbox folder assuming that this is mapped
        # to the base of the depot
        my.root_sandbox_dir = Environment.get_sandbox_dir()
        repo_dir = my.sandbox_dir
        repo_dir = my.sandbox_dir.replace("%s/" % my.root_sandbox_dir, "")



        #button.add_style("padding-right: 14px")
        button.add_style("float: left")
        button.add_behavior( {
        'type': 'click_up',
        'repo_dir': repo_dir,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_checkin_top");
        spt.app_busy.show("Reading file system ...")

        var data = spt.scm.checkout(bvr.repo_dir)
        spt.panel.refresh(top);

        spt.app_busy.hide();
        '''
        } )





        button = ButtonNewWdg(title="Perforce Actions", icon=IconWdg.PERFORCE, show_arrow=True)
        #button.set_show_arrow_menu(True)
        button_row.add(button)

        menu = Menu(width=220)
        menu_item = MenuItem(type='title', label='Perforce')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Show Workspaces')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);

            var class_name = 'tactic.ui.checkin.WorkspaceWdg';
            var top = activator.getParent(".spt_checkin_top");
            var content = top.getElement(".spt_checkin_content");

            var el = top.getElement(".spt_mode");
            el.value = "workspace";

            var kwargs = {};
            spt.panel.load(content, class_name, kwargs);
            '''
        } )





        menu_item = MenuItem(type='action', label='Show Changelists')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);

            var class_name = 'tactic.ui.checkin.ChangelistWdg';
            var top = activator.getParent(".spt_checkin_top");
            var content = top.getElement(".spt_checkin_content");

            var el = top.getElement(".spt_mode");
            el.value = "changelist";

            var kwargs = {};
            spt.panel.load(content, class_name, kwargs);
            '''
        } )



        menu_item = MenuItem(type='action', label='Show Branches')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);

            var class_name = 'tactic.ui.checkin.branch_wdg.BranchWdg';
            var top = activator.getParent(".spt_checkin_top");
            var content = top.getElement(".spt_checkin_content");

            var el = top.getElement(".spt_mode");
            el.value = "branch";

            var kwargs = {};
            spt.panel.load(content, class_name, kwargs);
            '''
        } )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label='Add New Changelist')
        menu.add(menu_item)

        menu_item.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            spt.scm.run("add_changelist", ["New Changelist"]);

            var class_name = 'tactic.ui.checkin.ChangelistWdg';
            var top = activator.getParent(".spt_checkin_top");
            var content = top.getElement(".spt_checkin_content");
            spt.panel.load(content, class_name);

            '''
        } )


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Sign Out of Perforce')
        menu.add(menu_item)

        menu_item.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            if (!confirm("Are you sure you wish to sign out of Perforce?")) {
                return;
            }
            spt.scm.host = null;
            spt.scm.user = null;
            spt.scm.password = null;

            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_checkin_top");
            spt.panel.refresh(top);


            '''
        } )



 
        #SmartMenu.add_smart_menu_set( button.get_arrow_wdg(), { 'BUTTON_MENU': menu } )
        #SmartMenu.assign_as_local_activator( button.get_arrow_wdg(), "BUTTON_MENU", True )

        SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': menu } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )




        # Perforce script editor. (nice because it should run as the user
        # in the appopriate environment
        """
        button = ButtonNewWdg(title="P4 Script Editor", icon=IconWdg.CREATE, show_arrow=True)
        #button_row.add(button)
        button.add_style("padding-right: 14px")
        button.add_style("float: left")
        """



        button = ButtonNewWdg(title="Changelists Counter", icon=IconWdg.CHECK_OUT_SM, show_arrow=True)
        #button_row.add(button)
        #button.add_style("padding-right: 14px")
        button.add_style("float: left")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
                // find any changelists that were missed
                var changelists = spt.scm.run("get_changelists", []);
                for (var i = 0; i < changelists.length; i++) {
                    var changelist = changelists[i];
                    var info = spt.scm.run("get_changelist_info",[changelist.change]);
                    console.log(info);
                }
                '''
            } )



        # Hiding this for now

        button = ButtonNewWdg(title="Create", icon=IconWdg.NEW, show_arrow=True)
        #button_row.add(button)
        button.add_style("padding-right: 14px")
        button.add_style("float: left")

        menu = Menu(width=220)
        menu_item = MenuItem(type='title', label='New ...')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Text File')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'sandbox_dir': my.sandbox_dir,
        'cbjs_action': '''
        var path = bvr.sandbox_dir + "/" + "new_text_file.txt";
        var env = spt.Environment.get();
        var url = env.get_server_url() + "/context/VERSION_API";
        var applet = spt.Applet.get();
        applet.download_file(url, path);

        var activator = spt.smenu.get_activator(bvr);
        var top = activator.getParent(".spt_checkin_top");
        spt.panel.refresh(top);

        '''
        } )


        #create_sobj = SObject.create("sthpw/virtual")
        #create_sobj.set_value("title", "Maya Project")
        #create_sobj.set_value("script_path", "create/maya_project")


        script_path = 'create/maya_project'
        menu_item = MenuItem(type='action', label='Maya Project')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'sandbox_dir': my.sandbox_dir,
        'process': my.process,
        'script_path': script_path,
        'cbjs_action': '''
        var script = spt.CustomProject.get_script_by_path(bvr.script_path);
        var options = {};
        options.script = script;

        // add some data to options
        options.sandbox_dir = bvr.sandbox_dir;
        options.process = bvr.process;
        spt.CustomProject.exec_custom_script({}, options);

        var activator = spt.smenu.get_activator(bvr);
        var top = activator.getParent(".spt_checkin_top");
        spt.panel.refresh(top);
        '''
        } )


        template_path = '/context/template/maya_project.zip'
        menu_item = MenuItem(type='action', label='Zipped Template')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'sandbox_dir': my.sandbox_dir,
        'template_path': template_path,
        'cbjs_action': '''
        var path = bvr.sandbox_dir + "/" + "_template.zip";
        var env = spt.Environment.get();
        var url = env.get_server_url() + bvr.template_path;
        var applet = spt.Applet.get();
        applet.download_file(url, path);
        applet.unzip_file(path, bvr.sandbox_dir);
        applet.rmtree(path);

        var activator = spt.smenu.get_activator(bvr);
        var top = activator.getParent(".spt_checkin_top");
        spt.panel.refresh(top);

        '''
        } )



        SmartMenu.add_smart_menu_set( button, { 'BUTTON_MENU': menu } )
        SmartMenu.assign_as_local_activator( button, "BUTTON_MENU", True )



        # Browse button for browsing files and dirs directly
        """
        browse_div = DivWdg()
        list_wdg.add(browse_div)
        browse_div.add_style("float: left")

        button = ActionButtonWdg(title="Browse", tip="Select Files or Folder to Check-In")
        browse_div.add(button)

        behavior = {
        'type': 'click_up',
        'base_dir': my.sandbox_dir,
        'cbjs_action': '''
            var current_dir = bvr.base_dir;
            var is_sandbox = false;
            spt.checkin.browse_folder(current_dir, is_sandbox);
        '''
        }
        button.add_behavior( behavior )
        """

        from tactic.ui.widget import SandboxButtonWdg, CheckoutButtonWdg, ExploreButtonWdg, GearMenuButtonWdg

        button_row = ButtonRowWdg()
        list_wdg.add(button_row)
        button_row.add_style("float: right")

        #button = SandboxButtonWdg(base_dir=my.sandbox_dir, process=my.process)
        #button_row.add(button)

        #button = CheckoutButtonWdg(base_dir=my.sandbox_dir, sobject=my.sobject, proces=my.process)
        #button_row.add(button)

        button = ExploreButtonWdg(base_dir=my.sandbox_dir)
        button_row.add(button)

        button = GearMenuButtonWdg(base_dir=my.sandbox_dir, process=my.process, pipeline_code=my.pipeline_code)
        button_row.add(button)



        list_wdg.add("<br clear='all'/>")

        top.add("<hr/>")

        content_div = DivWdg()
        top.add(content_div)
        content_div.add_class("spt_checkin_content")

        content = my.get_content_wdg()
        content_div.add(content)

        return top



    def get_content_wdg(my):
        content = DivWdg()

        project = my.sobject.get_project()
        depot = project.get_value("location", no_exception=True)
        if not depot:
            depot = Config.get_value("perforce", "depot")
        if not depot:
            depot = ""

        branch = "r1.1"
        root_sandbox_dir = Environment.get_sandbox_dir()

        web = WebContainer.get_web()
        folder_state = web.get_form_value("folder_state")

        content.add_behavior( {
            'type': 'load',
            'folder_state': folder_state,
            'search_key': my.search_key,
            'sandbox_dir': my.sandbox_dir,
            'root_sandbox_dir': root_sandbox_dir,
            'depot': depot,
            'process': my.process,
            'branch': branch,
            'cbjs_action': '''

// set the sync root directory
spt.scm.sync_dir = bvr.root_sandbox_dir;
spt.scm.depot = bvr.depot;

// check to see if we are logged in
var is_logged_in = spt.scm.is_logged_in();
if (!is_logged_in) {
    spt.scm.show_login();
    return;
}


// check to see if we are logged in
/*
var is_logged_in = spt.scm.is_logged_in();
if (!is_logged_in) {
    spt.scm.show_login();
    return;
}
*/



var applet = spt.Applet.get();

if (! applet.exists(bvr.sandbox_dir)) {
    var class_name = 'tactic.ui.widget.CheckinSandboxNotExistsWdg';
    var kwargs = {
        'process': bvr.process,
        'sandbox_dir': bvr.sandbox_dir,
        // FIXME: missing create_sandbox_script_path
        'create_sandbox_script_path': ''
    }
    spt.panel.load(bvr.src_el, class_name, kwargs);
    return;
}


spt.app_busy.show("Reading Sync Folder ...");
var ret_val;
try {
    ret_val = spt.scm.status(bvr.sandbox_dir);
} catch(e) {
    ret_val = {};
}

var paths = [];
var sizes = [];
for (var path in ret_val) {
    paths.push(path);
}
paths = paths.sort();
// TODO: is this slow?
for (var i = 0; i < paths.length; i++) {
    if (applet.is_dir(paths[i])) {
        paths[i] = paths[i] + "/";
    }
    else {
        if (applet.exists(paths[i])) {
            var path_info = applet.get_path_info(paths[i]);
            var size = path_info.size;
            sizes.push(size);
        }
        else {
            sizes.push(-1);
        }
    }
}


spt.app_busy.show("Loading display ...");
var class_name = 'tactic.ui.checkin.ScmDirListWdg';
var kwargs = {
    path_info: ret_val,
    paths: paths,
    base_dir: bvr.sandbox_dir,
    search_key: bvr.search_key,
    sizes: sizes,
    folder_state: bvr.folder_state,

}
spt.panel.load(bvr.src_el, class_name, kwargs);

spt.app_busy.hide();

            '''
        } )

        return content





class ScmDirListWdg(CheckinDirListWdg):

    def preprocess(my):
        my.search_key = my.kwargs.get("search_key")
        if my.search_key:
            my.sobject = Search.get_by_search_key(my.search_key)
        else:
            my.sobject = None

        my.path_info = my.kwargs.get("path_info")
        my.paths = my.kwargs.get("paths")

        sizes = my.kwargs.get("sizes")

        my.sizes = {}

        #for path, size in zip(my.paths, sizes):
        i = 0
        for path in my.paths:
            if path.endswith("/"):
                continue

            size = sizes[i]
            my.sizes[path] = size
            i += 1






    def add_top_behaviors(my, top):

        super(ScmDirListWdg, my).add_top_behaviors(top)

        changelist = WidgetSettings.get_value_by_key("current_changelist")

        menu_item = MenuItem(type='title', label="Perforce Actions")
        my.menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Add To Changelist [%s]' % changelist)
        my.menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'changelist': changelist,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);

            var paths = spt.checkin.get_selected_paths();
            if (paths.length == 0) {
                var path = activator.getAttribute("spt_path");
                paths = [path]
            }

            var changelist = bvr.changelist;

            // TODO: optimize this to call on once by passing in the array
            // of paths
            for (var i = 0; i < paths.length; i++) {
                var path = paths[i];
                spt.scm.run("add", [path, changelist]);
            }
            var top = activator.getParent(".spt_checkin_top");
            spt.panel.refresh(top);
            '''
        } )


        menu_item = MenuItem(type='action', label='Make Editable')
        my.menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'changelist': changelist,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);

            var paths = spt.checkin.get_selected_paths();
            if (paths.length == 0) {
                var path = activator.getAttribute("spt_path");
                paths = [path]
            }

            // TODO: optimize this to call on once by passing in the array
            // of paths
            for (var i = 0; i < paths.length; i++) {
                var path = paths[i];
                spt.scm.run("edit", [path, bvr.changelist]);
            }

            var top = activator.getParent(".spt_checkin_top");
            spt.panel.refresh(top);

            '''
        } )


        menu_item = MenuItem(type='action', label='Revert File')
        my.menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var path = activator.getAttribute("spt_path");
            try {
                spt.scm.revert(path);
                var top = activator.getParent(".spt_checkin_top");
                spt.panel.refresh(top);
            }
            catch (e) {
                spt.scm.handle_error(e);
            }

            '''
        } )



        menu_item = MenuItem(type='action', label='File Log')
        my.menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var path = activator.getAttribute("spt_path");
            try {
                var file_logs = spt.scm.file_log(path);

                var class_name = 'tactic.ui.checkin.ScmCheckinHistoryWdg';
                var kwargs = {
                    'file_logs': file_logs
                }
                spt.panel.load_popup("Check-in History", class_name, kwargs);
            }
            catch (e) {
                spt.scm.handle_error(e);
            }

            '''
        } )




    def handle_dir_div(my, dir_div, dirname, basename):
        dir_div.add("%s" % basename )


    def handle_item_div(my, item_div, dirname, basename):


        table = Table()
        item_div.add(table)
        table.add_row()
        table.add_style("width: 100%")



        icon_string = my.get_file_icon(dirname, basename)

        icon_div = DivWdg()
        td = table.add_cell(icon_div)
        td.add_style("width: 15px")

        icon = IconWdg("%s/%s" % (dirname, basename), icon_string)
        icon_div.add(icon)
        icon_div.add_style("float: left")
        icon_div.add_style("margin-top: -1px")



        path = "%s/%s" % (dirname, basename)
        status = my.path_info.get(path)
        margin_left = -16
        if status == 'same':
            check = IconWdg( "No Changes", IconWdg.CHECK, width=12 )
        elif status == 'added':
            check = IconWdg( "Added", IconWdg.NEW, width=16 )
            margin_left = -18
        elif status == 'unversioned':
            check = IconWdg( "Unversioned", IconWdg.HELP, width=12 )
        elif status == 'missing':
            check = IconWdg( "Missing", IconWdg.WARNING, width=12 )
        elif status == 'editable':
            check = IconWdg( "Editable", IconWdg.EDIT, width=12 )
        elif status == 'modified':
            check = IconWdg( "Modified", IconWdg.WARNING, width=12 )
        else:
            check = IconWdg( "Error (unknown status)", IconWdg.ERROR, width=12 )

        if check:
            td = table.add_cell(check)
            td.add_style("width: 3px")
            check.add_style("float: left")
            check.add_style("margin-left: %spx" % margin_left)
            check.add_style("margin-top: 4px")
            item_div.add_color("color", "color", [0, 0, 50])

            if status == 'missing':
                item_div.add_style("opacity: 0.3")

        else:
            item_div.add_style("opacity: 0.8")


        name_div = DivWdg()
        td = table.add_cell(name_div)
        name_div.add(basename)
        name_div.add_style("float: left")

        if status != "same":
            name_div.add(" <i style='opacity: 0.5; font-size: 10px'>(%s)</i>" % status)

        spath = path.replace(" ", "_")


        # add the size of the file
        size_div = DivWdg()
        td = table.add_cell(size_div)
        td.add_style("width: 60px")

        size = my.sizes.get(spath)
        if size is None or size == -1:
            size_div.add("-")
        else:
            size_div.add(FormatValue().get_format_value(size, 'KB'))

        size_div.add_style("margin-right: 5px")
        size_div.add_style('text-align: right')



        # FIXME: this still is needed right now, although really used.
        my.subcontext_options = []
        if not my.subcontext_options:
            subcontext = TextWdg("subcontext")
            subcontext = HiddenWdg("subcontext")
            subcontext.add_class("spt_subcontext")
            subcontext.add_style("float: right")

        else:
            subcontext = SelectWdg("subcontext")
            subcontext = HiddenWdg("subcontext")
            subcontext.set_option("show_missing", False)
            subcontext.set_option("values", my.subcontext_options)
            subcontext.add_empty_option("----")


        subcontext.add_behavior( {
            'type': 'click_up',
            'propagate_evt': False,
            'cbjs_action': '''
            bvr.src_el.focus();
            '''
        } )

        subcontext.add_style("display: none")
        item_div.add(subcontext)





    #def get_file_icon(my, dirname, basename):
    #    if my.path_info.get("%s/%s" % (dirname, basename)) == 'none':
    #        return IconWdg.DETAILS
    #    else:
    #        return IconWdg.ERROR





class ScmSignInWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_class("spt_sign_in_top")


        top.add_color("background", "background")
        top.add_style("padding: 30px")
        top.add_style("width: 300px")


        icon = IconWdg("Not signed in", IconWdg.WARNING)
        top.add(icon)

        top.add("You are not signed into Perforce.")
        top.add("<br/>"*2)


        table = Table()
        top.add(table)


        from tactic.ui.input import TextInputWdg, PasswordInputWdg

        table.add_row()
        td = table.add_cell("Port: ")
        td.add_style("width: 75px")

        text = TextInputWdg(name="port")
        table.add_cell(text)
        text.set_value("1666")

        tr = table.add_row()
        table.add_row_cell("&nbsp;")

        table.add_row()
        td = table.add_cell("Login: ")
        td.add_style("width: 75px")

        text = TextInputWdg(name="user")
        table.add_cell(text)
        user = Environment.get_user_name()
        text.set_value(user)

        table.add_row()

        table.add_cell("Password: ")

        text = PasswordInputWdg(name="password")
        table.add_cell(text)

        tr = table.add_row()
        table.add_row_cell("&nbsp;")

        tr = table.add_row()
        table.add_cell("Workspace: ")
        text = TextInputWdg(name="workspace")
        table.add_cell(text)
        text.add_class("spt_workspace")



        top.add("<br/>"*2)


        button = ActionButtonWdg(title="Sign In", icon=IconWdg.PUBLISH, size='medium')
        top.add(button)
        button.add_style("float: right")


        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_sign_in_top");
            var values = spt.api.get_input_values(top);

            var port = values.port[0];
            var user = values.user[0];
            var password = values.password[0];
            var client = values.workspace[0];

            // login in user
            spt.scm.port = port;
            spt.scm.user = user;
            spt.scm.password = password;
            spt.scm.client = client;


            // test the connection
            var ping = spt.scm.ping();
            if (ping != "OK") {
                spt.scm.show_login();
                return;
            }

            // TODO: get the workspaces and use this as a list
            // For now, just fill it in with the first one
            if (!client) {
                var workspaces = spt.scm.get_workspaces();
                if (workspaces.length > 0) {
                    var workspace = workspaces[0];
                    var Root = workspace.root;
                    // TODO: make sure Root == snapshot_dir

                    console.log("workspace");
                    console.log(workspace);

                    var client = workspace.client;
                    var workspace_el = top.getElement(".spt_workspace");
                    workspace_el.value = client;
                }
                return;
            }


            // check the workspaces
            if (!spt.scm.check_workspace()) {
                alert("Problem with current workspace");
                spt.scm.show_login();
                return;
            }

            // close the popup
            var popup = bvr.src_el.getParent(".spt_popup");
            if (popup) {
                spt.popup.destroy(popup);
            }



            // NOTE: this is global: find a check-in widget and refresh
            var checkin_el = $(document.body).getElement(".spt_checkin_top");
            spt.panel.refresh(checkin_el);

            '''
        } )

        top.add("<br/>"*2)



        return top



__all__.append("get_onload_js")
def get_onload_js():

        return r'''
if ( typeof(spt.scm) != 'undefined' ) {
    return;
}

spt.scm = {};

spt.scm.sync_dir = null;
spt.scm.depot = null;

// this can be either a password or a ticket
spt.scm.port = bvr.port;
spt.scm.user = bvr.user;
spt.scm.password = bvr.password;
spt.scm.client = ""

spt.scm.kwargs = null;

spt.scm.get_kwargs = function() {

    if (spt.scm.kwargs != null) {
        // set the current password
        var port = spt.scm.port;
        var user = spt.scm.user;
        var password = spt.scm.password;
        var client = spt.scm.client;
        spt.scm.kwargs.port = port;
        spt.scm.kwargs.user = user;
        spt.scm.kwargs.password = password;
        spt.scm.kwargs.client = client;
        return spt.scm.kwargs;
    }

    if (spt.scm.sync_dir == null) {
        throw("Sync dir is not set");
    }



    var port = spt.scm.port;
    var user = spt.scm.user;
    var password = spt.scm.password;
    var client = spt.scm.client;

    var depot = bvr.depot;

    spt.scm.depot = depot;


    var kwargs = {
        port: port,
        user: user,
        password: password,
        client: client,

        depot: depot,

        root: '',
        branch: '',
        sync_dir: spt.scm.sync_dir,
    }

    // remember this setting
    spt.scm.kwargs = kwargs;

    return kwargs;
}


spt.scm.run = function(method, args) {
    var applet = spt.Applet.get();
    var class_name = 'scm.delegate.DelegateCmd';
    var kwargs = spt.scm.get_kwargs();
    kwargs['method'] = method;
    kwargs['args'] = args;
    try {
        var ret_val = applet.exec_local_cmd(class_name, kwargs);
        var value = ret_val.value;
        return value;
    }
    catch(e) {
        if (e.status == "error") {

            if (method != "is_logged_in") { // to prevent infinite loops
                var is_logged_in = spt.scm.is_logged_in();
                if (!is_logged_in) {
                    spt.scm.show_login();
                    throw(e);
                }
            }

            alert(e.msg);
            spt.app_busy.hide();
            throw(e.msg);
        }
    }

}


spt.scm.handle_error = function(info) {
    if (info.status != 'error') {
        return;
    }

    //spt.log.error(info.stack_trace);
    console.log("---");
    console.log(info.msg);
    console.log("\n");
    console.log(info.stack_trace);
    var msg = info.msg.replace("\\n", "<br/>\\n");
    spt.notify.show_message(msg);
}



spt.scm.ping = function() {
    return spt.scm.run("ping", [])
}

spt.scm.login_user = function(user, password) {
    //return spt.scm.run("login_user", [password])
    spt.scm.user = user
    spt.scm.password = password
}


spt.scm.is_logged_in = function() {
    if (!spt.scm.user) return false;
    if (!spt.scm.password) return false;
    return true;
}


/*
spt.scm.is_client_logged_in = function() {
    return spt.scm.run("is_logged_in");
}
*/

spt.scm.get_workspaces = function(user) {
    return spt.scm.run("get_workspaces",[user]);
}


spt.scm.check_workspace = function() {
    return spt.scm.run("check_workspace");
}



spt.scm.show_login = function(el) {
    spt.app_busy.hide();
    var class_name = 'tactic.ui.checkin.ScmSignInWdg';
    var kwargs = {};
    if (el) {
        spt.panel.load(el, class_name, kwargs);
    }
    else {
        spt.panel.load_popup("Perforce Sign In", class_name, kwargs);
    }
}


spt.scm.status = function(sync_path) {
    return spt.scm.run("status", [sync_path]);
}



spt.scm.checkout = function(repo_dir) {
    return spt.scm.run("checkout", [repo_dir]);
}



spt.scm.commit = function(paths, description) {
    return spt.scm.run("commit", [paths, description]);
}


spt.scm.add = function(path) {
    return spt.scm.run("add", [path]);
}


spt.scm.edit = function(path, changeset) {
    return spt.scm.run("edit", [path, changeset]);
}


spt.scm.revert = function(path) {
    return spt.scm.run("revert", [path]);
}

spt.scm.restore = function(path) {
    return spt.scm.run("restore", [path]);
}

spt.scm.file_log = function(path) {
    return spt.scm.run("file_log", [path]);
}


        '''





class ScmCheckinHistoryWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        file_logs = my.kwargs.get("file_logs")
        print "file_logs: ", file_logs

        attrs = ['depot', 'action','change','client','desc','digest','fileSize','rev','time','type','user']


        # FIXME: depotfile is Perforce specific

        # handle only one file for now
        file_log = file_logs[0]
        file_path = file_log.get("depotFile")

        # find the number of revisions
        my.sobjects = []
        num_sobjects = len(file_log.get("action"))
        for i in range(0, num_sobjects):
            sobject = SearchType.create("sthpw/virtual")
            my.sobjects.append(sobject)
            sobject.set_value("depotFile", file_path)
            sobject.set_value("id", i)

        # go through each attr
        for attr in attrs:
            if attr == 'depot':
                value = file_path.lstrip("//")
                parts = value.split("/")
                value = "//%s" % parts[0]
                for sobject in my.sobjects:
                    sobject.set_value(attr, value)
            else:
                values = file_log.get(attr)
                for i, value in enumerate(values):
                    my.sobjects[i].set_value(attr, value)

        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add("File Log for [%s]" % file_path)
        title_wdg.add_color("color", "color3")
        title_wdg.add_color("background", "background3")
        title_wdg.add_style("padding: 10px")
        title_wdg.add_style("font-size: 14px")
        title_wdg.add_style("font-weight: bold")



        from tactic.ui.panel import FastTableLayoutWdg
        table = FastTableLayoutWdg(search_type="sthpw/virtual", view="table", element_names=attrs, show_shelf=False)
        table.set_sobjects(my.sobjects)
        top.add(table)


        return top






class ScmScriptEdtior(BaseRefreshWdg):

    def get_display(my):
        top = my.top



        return top



__all__.append("ScmSnapshotDirListWdg")
class ScmSnapshotDirListWdg(DirListWdg):
    pass




