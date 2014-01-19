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


__all__ = ['SnapshotFilesWdg','SObjectDirListWdg']

from pyasm.common import Environment, Common, jsonloads, jsondumps
from pyasm.search import SearchKey, Search
from pyasm.biz import Snapshot, Pipeline
from pyasm.web import WebContainer, SpanWdg, DivWdg, Table
from pyasm.widget import IconWdg, SelectWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.tools import RepoBrowserDirListWdg
from tactic.ui.widget import DirListWdg, SingleButtonWdg, ButtonNewWdg, IconButtonWdg
from tactic.ui.container import DialogWdg, Menu, MenuItem, SmartMenu

import os, re


class SnapshotFilesWdg(BaseRefreshWdg):
    '''This is used in the "Files" hidden row to display all the files of
    a snapshot'''

    def init(my):
        my.base_dir = None

    def get_files(my):

        paths = []

        # remember this here for now
        my.files = {}
        my.snapshots = {}


        search_key = my.kwargs.get("search_key")
        sobject = SearchKey.get_by_search_key(search_key)
        # if it is deleted, return
        if not sobject:
            return []
    
        if isinstance(sobject, Snapshot):
            snapshots = [sobject]
        else:
            snapshots = Snapshot.get_by_sobject(sobject, "publish")

        for snapshot in snapshots:
            snapshot_paths = snapshot.get_all_lib_paths()

            files = snapshot.get_all_file_objects()

            for path, file in zip(snapshot_paths, files):

                # if the path is a directory, get all of the files
                if os.path.isdir(path):
                    for root, dirnames, filenames in os.walk(path):

                        for filename in filenames:
                            item_path = "%s/%s" % (root, filename)
                            paths.append(item_path)
                            my.files[item_path] = file
                            my.snapshots[item_path] = snapshot

                        for dirname in dirnames:
                            item_path = "%s/%s/" % (root, dirname)
                            paths.append(item_path)
                            my.files[item_path] = file
                            my.snapshots[item_path] = snapshot


                    """
                    dirlist = os.listdir(path)
                    for item in dirlist:
                        item_path = "%s%s" % (path, item)
                        if os.path.isdir(path):
                            item_path = "%s/" % item_path
                        paths.append(item_path)
                        my.files[path] = file
                    """

                else:
                    paths.append(path)
                    my.files[path] = file
                    base_dir_alias =  file.get_value('base_dir_alias')
                    if not my.base_dir and base_dir_alias:
                        my.base_dir = Environment.get_asset_dir(alias=base_dir_alias)

        return paths




    def get_display(my):

        top = my.top
        top.add_style("padding: 10px")
        top.add_color("background", "background", -5)
        top.add_style("min-width: 350px")

        paths = my.get_files()

       
        # assume that all the paths are part of the same repo
        repo = 'tactic'
        for file in my.files.values():
            repo = file.get_value("repo_type", no_exception=True)
            break

        if repo == 'perforce':
            search_key = my.kwargs.get("search_key")
            sobject = SearchKey.get_by_search_key(search_key)
     
            project = sobject.get_project()
            depot = project.get_value("location", no_exception=True)
            if not depot:
                depot = project.get_code()
            location = '//%s' % depot

            dir_list = SnapshotDirListWdg(base_dir=location, location="scm", show_base_dir=True,paths=paths, all_open=True, files=my.files, snapshots=my.snapshots) 
        else:
            # If not discovered thru base_dir_alias, use the default
            if not my.base_dir:
                my.base_dir = Environment.get_asset_dir()
            
            dir_list = SnapshotDirListWdg(base_dir=my.base_dir, location="server", show_base_dir=True,paths=paths, all_open=True, files=my.files, snapshots=my.snapshots)

        top.add(dir_list)


        return top






class SnapshotDirListWdg(DirListWdg):

    def __init__(my, **kwargs):
        if kwargs.get("all_open") == None:
            kwargs["all_open"] = True

        super(SnapshotDirListWdg, my).__init__(**kwargs)
        my.snapshots = kwargs.get("snapshots")
        if not my.snapshots:
            my.snapshots = {}

    def add_top_behaviors(my, top):

        # convert this to a repo directory
        asset_dir = Environment.get_asset_dir()

        # FIXME: not sure how general this
        #webdirname = "/assets/%s" % dirname.replace(asset_dir, "")

        web = WebContainer.get_web()
        browser = web.get_browser()


        if browser == 'Qt':
            top.add_relay_behavior( {
            'type': 'dblclick',
            'bvr_match_class': 'spt_dir_list_item',
            'cbjs_action': '''
            var path = bvr.src_el.getAttribute("spt_path");
            var asset_dir = '%s';
            var url = "/assets/" + path.replace(asset_dir, "");
            //window.open(url);

            var class_name = 'tactic.ui.widget.EmbedWdg';
            var kwargs = {
                src: url
            }

            var parts = path.split("/");
            var filename = parts[parts.length-1];
            spt.tab.set_main_body_tab()
            spt.tab.add_new(filename, filename, class_name, kwargs);
            ''' % asset_dir
            } )
        else:
            top.add_relay_behavior( {
            'type': 'dblclick',
            'bvr_match_class': 'spt_dir_list_item',
            'cbjs_action': '''
            var path = bvr.src_el.getAttribute("spt_path");
            var asset_dir = '%s';
            var url = "/assets/" + path.replace(asset_dir, "");
            window.open(url);
            ''' % asset_dir
            } )

        # add a top menu
        menu = Menu(width=180)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Download to Folder')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var applet = spt.Applet.get();
            var select_dir = true;
            var dir = applet.open_file_browser('', select_dir);
            if (!dir) {
                dir = applet.get_current_dir();
            }
            if (!dir) {
                spt.alert("No folder selected to copy to");
                return;
            }
            
            var path = activator.getAttribute("spt_path");

            var asset_dir = '%s';
            var env = spt.Environment.get();
            var server_url = env.get_server_url();
            var url = server_url + "/assets/" + path.replace(asset_dir, "");
            var parts = path.split("/");
            var filename = parts[parts.length-1];
            spt.app_busy.show("Downloading file", filename);
            applet.download_file(url, dir + "/" + filename);
            spt.app_busy.hide();
            if (dir)
                spt.notify.show_message("Download to '" + dir + "' completed.")
            ''' % asset_dir
        } )
        #menu_item = MenuItem(type='action', label='Check-out To Sandbox')
        #menu.add(menu_item)
        #menu_item.add_behavior( {
        #'type': 'click_up',
        #'cbjs_action': '''spt.alert('Not implemented yet.')'''
        #} )
        menu_item = MenuItem(type='action', label='Copy to Clipboard')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var activator = spt.smenu.get_activator(bvr);
        var path = activator.getAttribute("spt_path");

        var search_key = activator.getAttribute("spt_file_search_key");

        var server = TacticServerStub.get();
        var class_name = 'tactic.command.clipboard_cmd.ClipboardCopyCmd';
        var search_keys = [search_key];
        var kwargs = {
            search_keys: search_keys
        }
        try {
            spt.app_busy.show("Copy to Clipboard ...");
            server.execute_cmd(class_name, kwargs);
            spt.app_busy.hide();
            }
        catch(e) {
            spt.alert(spt.exception.handler(e));
        }
        '''
        } )


        menu_item = MenuItem(type='action', label='View Metadata')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var activator = spt.smenu.get_activator(bvr);
        var path = activator.getAttribute("spt_path");

        var search_key = activator.getAttribute("spt_file_search_key");

        var server = TacticServerStub.get();
        var class_name = 'tactic.ui.checkin.SnapshotMetadataWdg';
        var kwargs = {
            search_key: search_key
        }
        spt.panel.load_popup("Metadata", class_name, kwargs);
        '''
        } )



        menus_in = {
            'FILE_MENU_CTX': menu,
        }
        SmartMenu.attach_smart_context_menu( top, menus_in, False )


        my.add_selection(top)
 
        super(SnapshotDirListWdg, my).add_top_behaviors(top)





    def add_file_behaviors(my, item_div, dirname, basename):


        path = "%s/%s" % (dirname, basename)

        file_objects = my.kwargs.get("files")
        file_object = file_objects.get(path)
        if not file_object:
            print "WARNING: No file object for [%s]" % path
            return
        file_search_key = file_object.get_search_key()


        item_div.add_class("spt_dir_list_item")
        item_div.add_attr("spt_path", path)
        item_div.add_attr("spt_file_search_key", file_search_key)
        SmartMenu.assign_as_local_activator( item_div, 'FILE_MENU_CTX' )




    def handle_item_div(my, item_div, dirname, basename):
        path = "%s/%s" % (dirname, basename)
        if my.info.get("file_type") == 'missing':
            icon_string = IconWdg.DELETE
            tip = 'Missing [%s]' %path
        else:
            icon_string = my.get_file_icon(dirname, basename)
            tip = path

        icon_div = DivWdg()
        item_div.add(icon_div)
        icon = IconWdg(tip, icon_string)
        icon_div.add(icon)
        icon_div.add_style("float: left")
        icon_div.add_style("margin-top: -1px")



        # add the file name
        filename_div = DivWdg()
        item_div.add(filename_div)
        filename_div.add_style("float: left")
        filename_div.add_style("overflow: hidden")

        snapshot = my.snapshots.get(path)
        file_type = my.info.get('file_type')
        if file_type == 'sequence':
            if snapshot:
                file_range = snapshot.get_file_range()
                start_frame = file_range.get_frame_start()
                end_frame = file_range.get_frame_end()
                basename = re.sub(re.compile("#+"), "(%s-%s)" % (start_frame, end_frame), basename)
                #file_names = snapshot.get_expanded_file_names()
                filename_div.add(basename)
            else:
                filename_div.add(basename)
        else:
            filename_div.add(basename)


        if snapshot:
            snapshot_div = DivWdg()
            item_div.add(snapshot_div)
            snapshot_div.add_style("float: left")
            snapshot_div.add_style("font-style: italic")
            snapshot_div.add_style("opacity: 0.5")
            process = snapshot.get_value("process")
            version = snapshot.get_value("version")
            if version == 0:
                version = 'current'
            elif version == -1:
                version = 'lastest'
            else:
                version = 'v%s' % version
            snapshot_div.add(" &nbsp; (%s %s)" % (version, process))

            #size = snapshot.get_value("st_size")

        # Right now, the size is taken from the file system, however,
        # should we be reporting the database size?
        size = my.info.get('size')
        if not size:
            size = 0

        from pyasm.common import FormatValue
        size = FormatValue().get_format_value(size, 'KB')

        filesize_div = DivWdg()
        item_div.add(filesize_div)
        filesize_div.add(size)
        #filesize_div.add_style("width: 200px")
        filesize_div.add_style("text-align: right")






    def get_file_icon(my, dir, item):
        if my.info.get("file_type") == 'link':
            return IconWdg.LINK
        return IconWdg.DETAILS

    def get_dir_icon(my, dir, item):
        return IconWdg.LOAD



    def add_selection(my, top):
        '''adding the behavior to select/unselect items'''
        top.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

spt.selection = {};
spt.selection.top = null;

spt.selection.set_top = function(top) {
    spt.selection.top = top;
}

spt.selection.item_class = 'spt_dir_list_item';

spt.selection.get_all_items = function() {
    var items = spt.selection.top.getElements("."+spt.selection.item_class);
    return items;
}


spt.selection.select = function(el) {
    el.addClass("spt_select");
    el.setStyle("background", "#888");
    el.setAttribute("spt_background", '#888');
}

spt.selection.unselect = function(el) {
    el.removeClass("spt_select");
    el.setStyle("background", "#FFF");
    el.setAttribute("spt_background", '#FFF');
}


spt.selection.select_all_items = function() {
    var items = spt.selection.get_all_items();
    for (var i = 0; i < items.length; i++) {
        spt.selection.select(items[i]);
    }
}


spt.selection.unselect_all_items = function() {
    var items = spt.selection.get_all_items();
    for (var i = 0; i < items.length; i++) {
        spt.selection.unselect(items[i]);
    }
}






spt.selection.get_selected = function() {
    var items = spt.selection.top.getElements("."+spt.selection.item_class);
    var selected = [];
    for (var i = 0; i < items.length; i++) {
        if (items[i].hasClass("spt_select")) {
            selected.push(items[i]);
        }
    }
    return selected;
}

            '''
        } )

        top_class = 'spt_dir_list_top'
        item_class = 'spt_dir_list_item'


        # selection
        bg_color = top.get_color("background")
        hilight_color = top.get_color("background", -5)
        top.add_behavior( {
        'type': 'smart_click_up',
        'bvr_match_class': item_class,
        'cbjs_action': '''
        var top_class = '%s';
        var top = bvr.src_el.getParent("."+top_class);

        spt.selection.set_top(top);
        spt.selection.unselect_all_items();
        spt.selection.select(bvr.src_el);
        ''' % top_class
        } )

        # CTRL: toggle selection
        top.add_behavior( {
        'type': 'smart_click_up',
        'bvr_match_class': item_class,
        'modkeys': 'CTRL',
        'cbjs_action': '''
        var top_class = '%s';
        var top = bvr.src_el.getParent("."+top_class);

        spt.selection.set_top(top);
        spt.selection.select(bvr.src_el);
        ''' % top_class
        } )



        # SHIFT: select all items in between
        top.add_behavior( {
        'type': 'smart_click_up',
        'bvr_match_class': item_class,
        'modkeys': 'SHIFT',
        'cbjs_action': '''
        var top_class = '%s';
        var top = bvr.src_el.getParent("."+top_class);

        spt.selection.set_top(top);
        spt.selection.select(bvr.src_el);
        ''' % top_class
        } )





class SObjectDirListWdg(DirListWdg):
    '''Widget to display all the files in an sobject'''

    def get_files(my):

        paths = []

        # remember this here for now
        my.files = {}

        my.snapshots = {}


        search_key = my.kwargs.get("search_key")
        search_keys = my.kwargs.get("search_keys")
        if search_key:
            sobject = SearchKey.get_by_search_key(search_key)
            my.sobjects = [sobject]

        if search_keys:
            if isinstance(search_keys, basestring):
                search_keys = search_keys.replace("'", '"')
                search_keys = jsonloads(search_keys)
            my.sobjects = Search.get_by_search_keys(search_keys)

        if not my.sobjects:
            return []

        my.sobject = my.sobjects[0]


        for sobject in my.sobjects:
            
            if sobject.get_base_search_type() in ['sthpw/task', 'sthpw/note']:
                parent = sobject.get_parent()
                sobject_paths = my.get_sobject_files(parent)
                paths.extend(sobject_paths)

            else:
                sobject_paths = my.get_sobject_files(sobject)
                paths.extend(sobject_paths)


        return paths


    def get_sobject_files(my, sobject):
        paths = []

        show_versionless = my.kwargs.get("show_versionless")
        if show_versionless in [True, 'true']:
            show_versionless = True
        else:
            show_versionless = False


        if isinstance(sobject, Snapshot):
            snapshots = [sobject]
        else:
            # get the snapshots
            versions = my.get_value("versions")
            search = Search("sthpw/snapshot")

            search.add_parent_filter(sobject)


            if not versions or versions == 'latest':
                search.add_filter("is_latest", True)
            elif versions == 'current':
                search.add_filter("is_current", True)

            if show_versionless:
                search.add_filter("version", -1)
                search.add_op('or')

            processes = my.kwargs.get("processes")
            process = my.get_value("process")
            if process and process != 'all':
                search.add_filter("process", process)
            if processes:
                search.add_filters("process", processes)

            snapshots = search.get_sobjects()

            #snapshots = Snapshot.get_by_sobject(sobject)

        for snapshot in snapshots:

            exclude = ['web','icon']
            snapshot_paths = snapshot.get_all_lib_paths(exclude_file_types=exclude)
            files = snapshot.get_all_file_objects(exclude_file_types=exclude)
            for path, file in zip(snapshot_paths, files):

                # if the path is a directory, get all of the files
                if os.path.isdir(path):
                    for root, dirnames, filenames in os.walk(path):

                        for filename in filenames:
                            item_path = "%s/%s" % (root, filename)
                            paths.append(item_path)
                            my.files[item_path] = file

                        for dirname in dirnames:
                            item_path = "%s/%s/" % (root, dirname)
                            paths.append(item_path)
                            my.files[item_path] = file

                else:
                    paths.append(path)
                    my.snapshots[path] = snapshot
                    my.files[path] = file

        return paths



    def get_value(my, name):
        web = WebContainer.get_web()
        value = web.get_form_value(name)
        if not value:
            value = my.kwargs.get(name)
        return value





    def get_display(my):

        paths = my.get_files()

        top = my.top
        top.add_style("padding: 10px")
        top.add_color("background", "background", -5)
        top.add_style("min-width: 500px")
        top.add_style("font-size: 12px")
        top.add_class("spt_sobject_dir_list_top")
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)


        show_title = my.kwargs.get("show_title")
        if show_title not in [False, 'false']:
            title_wdg = DivWdg()
            inner.add(title_wdg)
            title_wdg.add("File Browser [%s]" % my.sobject.get_code())
            title_wdg.add_gradient("background", "background3")
            title_wdg.add_style("padding: 5px")
            title_wdg.add_style("margin: -10px -10px 10px -10px")
            title_wdg.add_style("font-weight: bold")

        show_shelf = my.kwargs.get("show_shelf")
        if show_shelf not in [False, 'false']:
            shelf_wdg = DivWdg()
            inner.add(shelf_wdg)
            shelf_wdg.add(my.get_shelf_wdg())
            shelf_wdg.add_style("padding: 5px")
            shelf_wdg.add_style("margin: -5px -5px 15px -5px")
            shelf_wdg.add_style("font-weight: bold")



        base_dir = Environment.get_asset_dir()

        dir_list = SnapshotDirListWdg(base_dir=base_dir, location="server", show_base_dir=True,paths=paths, all_open=True, files=my.files, snapshots=my.snapshots)

        inner.add(dir_list)


        if my.kwargs.get("is_refresh"):
            return inner
        else:
            return top



    def get_shelf_wdg(my):

        process = my.get_value("process")
        versions = my.get_value("versions")

        div = DivWdg()

        button = SingleButtonWdg(title="Refresh", icon=IconWdg.REFRESH)
        div.add(button)
        button.add_style("float: left")
        div.add("&nbsp;"*5)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.panel.refresh(bvr.src_el);
            '''
        } )

        # get all of the pipelnes for this search type
        pipeline_code = my.sobject.get_value("pipeline_code", no_exception=True)
        processes = []
        if pipeline_code:
            pipeline = Pipeline.get_by_code(pipeline_code)
            if pipeline:
                process_names = pipeline.get_process_names()
                processes.extend(process_names)

        processes.insert(0, "all")



        div.add("Process: ")
        select = SelectWdg("process")
        if process != 'all':
            select.set_value(process)

        select.set_option("values", processes)

        div.add(select)



        div.add("&nbsp;"*10)

        div.add("Versions: ")
        select = SelectWdg("versions")
        select.set_option("values", "latest|current|today|last 10|all")
        if versions:
            select.set_value(versions)
        div.add(select)


        asset_dir = Environment.get_asset_dir()

        select = IconButtonWdg( tip="Toggle Selection", icon=IconWdg.SELECT, show_arrow=False )
        div.add(select)
        select.add_style("float: right")
        select.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top_class = 'spt_sobject_dir_list_top'
            var toggle_state = bvr.src_el.getAttribute('toggle');
            if (toggle_state && toggle_state=='true')
                bvr.src_el.setAttribute('toggle','false');
            else
                bvr.src_el.setAttribute('toggle','true');

            var top = bvr.src_el.getParent("."+top_class);
            spt.selection.set_top(top);
            
            toggle_state = bvr.src_el.getAttribute('toggle');
            if (toggle_state == 'true')
                spt.selection.select_all_items();
            else
                spt.selection.unselect_all_items();

            '''
            } )



        show = IconButtonWdg( tip="Switch View", icon=IconWdg.VIEW, show_arrow=False )
        div.add(show)
        show.add_style("float: right")
        show.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top_class = 'spt_sobject_dir_list_top'
            var top = bvr.src_el.getParent("."+top_class);
            spt.selection.set_top(top);
            var els = top.getElements(".spt_file_dir_item");
            for (var i = 0; i < els.length; i++) {
                var el = els[i];
                if (el.getStyle("display") == "none") {
                    els[i].setStyle("display", "");
                }
                else {
                    els[i].setStyle("display", "none");
                }
            }
            var els = top.getElements(".spt_file_item");
            for (var i = 0; i < els.length; i++) {
                var el = els[i];
                if (el.getStyle("padding-left") == "6px") {
                    var padding = el.getAttribute("spt_padding_left");
                    el.setStyle("padding-left", padding);
                }
                else {
                    el.setStyle("padding-left", "6px");
                }

            }


            '''
        } )






        gear = IconButtonWdg( tip="Download", icon=IconWdg.DOWNLOAD, show_arrow=False )
        div.add(gear)
        gear.add_style("float: right")
        gear.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show('Select a folder to download to...','');
            var top_class = 'spt_sobject_dir_list_top';
            var top = bvr.src_el.getParent("."+top_class);
            spt.selection.set_top(top);
            var items = spt.selection.get_selected();
            
       
            setTimeout( function() {
                var applet = spt.Applet.get();
                var select_dir =true;
                var dir = applet.open_file_browser('', select_dir);
                if (dir.length == 0)
                    dir = applet.get_current_dir();
                else 
                    dir = dir[0];

                if (!dir) {
                    spt.alert("No folder selected to copy to.");
                    spt.app_busy.hide();
                    return;
                }
                if (items.length == 0){
                    spt.alert("Please select at least one file to download.");
                    spt.app_busy.hide();
                    return;
                }
                

                var asset_dir = '%s';
                for (var i = 0; i < items.length; i++) {
                    var path = items[i].getAttribute("spt_path");
                    var env = spt.Environment.get();
                    var server_url = env.get_server_url();
                    var url = server_url + "/assets/" + path.replace(asset_dir, "");
                    var parts = path.split("/");
                    var filename = parts[parts.length-1];
                    spt.app_busy.show("Downloading file", filename);
                    applet.download_file(url, dir + "/" + filename);
                }
                spt.app_busy.hide();
                if (dir)
                    spt.notify.show_message("Download to '" + dir + "' completed.")
            }, 100);

            ''' % asset_dir
 
        } )

        return div



__all__.append("SnapshotMetadataWdg")
class SnapshotMetadataWdg(BaseRefreshWdg):

    def get_display(my):

        search_key = my.kwargs.get("search_key")
        snapshot = my.kwargs.get("snapshot")

        if snapshot:
            my.snapshot = snapshot
        else:
            my.snapshot = SearchKey.get_by_search_key(search_key)


        assert my.snapshot

        metadata = my.snapshot.get_metadata()

        top = my.top
        top.add_color("background", "background")


        table = Table()
        table.set_max_width()
        top.add(table)
        table.set_unique_id()
        table.add_border()

        table.add_smart_styles("spt_cell", {
            'padding': '3px'
        } )



        tr = table.add_row()
        tr.add_gradient("background", "background3")
        th = table.add_header("Property")
        th.add_style("min-width: 200px")
        th.add_style("padding: 5px")
        th = table.add_header("Value")
        th.add_style("min-width: 400px")
        th.add_style("padding: 5px")

        keys = metadata.get("__keys__")
        if not keys:
            keys = metadata.keys()

        empty = False
        if not keys:
            empty = True
            keys = ['','','','','','','']
            table.add_smart_styles("spt_cell", {
                'height': '20px'
            } )


        for i, key in enumerate(keys):
            value = metadata.get(key)

            title = Common.get_display_title(key)

            tr = table.add_row()

            if i % 2:
                tr.add_color("background", "background")
                tr.add_color("color", "color")
            else:
                tr.add_color("background", "background", -8)
                tr.add_color("color", "color")

            td = table.add_cell()
            td.add_class("spt_cell")
            td.add(title)

            td = table.add_cell()
            td.add_class("spt_cell")
            td.add(value)


        if empty:
            div = DivWdg()
            top.add(div)
            div.add_style("height: 30px")
            div.add_style("width: 150px")
            div.add_style("margin-top: -110px")
            div.center()
            div.add("<b>No Metadata</b>")
            div.add_border()
            div.add_color("background", "background3")
            div.add_color("color", "color3")
            div.add_style("padding: 20px")
            div.add_style("text-align: center")

            top.add_style("min-height: 200px")

        return top



__all__.append("PathMetadataWdg")
class PathMetadataWdg(BaseRefreshWdg):

    def get_display(my):

        search_key = my.kwargs.get("search_key")
        path = my.kwargs.get("path")
        parser_str = my.kwargs.get("parser")

        from pyasm.checkin import PILMetadataParser, ImageMagickMetadataParser, ExifMetadataParser

        if parser_str == "EXIF":
            parser = ExifMetadataParser(path=path)
        elif parser_str == "ImageMagick":
            parser = ImageMagickMetadataParser(path=path)
        elif parser_str == "PIL":
            parser = PILMetadataParser(path=path)
        else:
            parser = None

        if parser:
            metadata = parser.get_metadata()
        else:
            metadata = {}


        top = my.top
        top.add_color("background", "background")


        table = Table()
        table.set_max_width()
        top.add(table)
        table.set_unique_id()
        table.add_border()

        table.add_smart_styles("spt_cell", {
            'padding': '3px'
        } )



        tr = table.add_row()
        tr.add_gradient("background", "background3")
        th = table.add_header("Property")
        th.add_style("min-width: 200px")
        th.add_style("padding: 5px")
        th = table.add_header("Value")
        th.add_style("min-width: 400px")
        th.add_style("padding: 5px")

        keys = metadata.get("__keys__")
        if not keys:
            keys = metadata.keys()

        empty = False
        if not keys:
            empty = True
            keys = ['','','','','','','']
            table.add_smart_styles("spt_cell", {
                'height': '20px'
            } )


        for i, key in enumerate(keys):
            value = metadata.get(key)

            title = Common.get_display_title(key)

            tr = table.add_row()

            if i % 2:
                tr.add_color("background", "background")
                tr.add_color("color", "color")
            else:
                tr.add_color("background", "background", -8)
                tr.add_color("color", "color")

            td = table.add_cell()
            td.add_class("spt_cell")
            td.add(title)

            td = table.add_cell()
            td.add_class("spt_cell")

            if len(str(value)) > 500:
                inside = DivWdg()
                td.add(inside)
                value = value[:500]
                inside.add(value)
                inside.add_style("max-width: 600px")
            else:
                td.add(value)


        if empty:
            div = DivWdg()
            top.add(div)
            div.add_style("height: 30px")
            div.add_style("width: 150px")
            div.add_style("margin-top: -110px")
            div.center()
            div.add("<b>No Metadata</b>")
            div.add_border()
            div.add_color("background", "background3")
            div.add_color("color", "color3")
            div.add_style("padding: 20px")
            div.add_style("text-align: center")

            top.add_style("min-height: 200px")

        return top










