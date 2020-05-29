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
from pyasm.biz import FileGroup

import os, re, six


class SnapshotFilesWdg(BaseRefreshWdg):
    '''This is used in the "Files" hidden row to display all the files of
    a snapshot'''

    def init(self):
        self.base_dir = None

    def get_files(self):

        paths = []

        # remember this here for now
        self.files = {}
        self.snapshots = {}


        search_key = self.kwargs.get("search_key")
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
                            self.files[item_path] = file
                            self.snapshots[item_path] = snapshot

                        for dirname in dirnames:
                            item_path = "%s/%s/" % (root, dirname)
                            paths.append(item_path)
                            self.files[item_path] = file
                            self.snapshots[item_path] = snapshot


                    """
                    dirlist = os.listdir(path)
                    for item in dirlist:
                        item_path = "%s%s" % (path, item)
                        if os.path.isdir(path):
                            item_path = "%s/" % item_path
                        paths.append(item_path)
                        self.files[path] = file
                    """

                else:
                    paths.append(path)
                    self.files[path] = file
                    base_dir_alias =  file.get_value('base_dir_alias')
                    if not self.base_dir and base_dir_alias:
                        self.base_dir = Environment.get_asset_dir(alias=base_dir_alias)

        return paths




    def get_display(self):

        top = self.top
        top.add_style("padding: 10px")
        top.add_color("background", "background", -5)
        top.add_style("min-width: 600px")

        paths = self.get_files()

       
        # assume that all the paths are part of the same repo
        repo = 'tactic'
        for file in self.files.values():
            repo = file.get_value("repo_type", no_exception=True)
            break

        if repo == 'perforce':
            search_key = self.kwargs.get("search_key")
            sobject = SearchKey.get_by_search_key(search_key)
     
            project = sobject.get_project()
            depot = project.get_value("location", no_exception=True)
            if not depot:
                depot = project.get_code()
            location = '//%s' % depot

            dir_list = SnapshotDirListWdg(base_dir=location, location="scm", show_base_dir=True,paths=paths, all_open=True, files=self.files, snapshots=self.snapshots) 
        else:
            # If not discovered thru base_dir_alias, use the default
            if not self.base_dir:
                self.base_dir = Environment.get_asset_dir()
            
            dir_list = SnapshotDirListWdg(base_dir=self.base_dir, location="server", show_base_dir=True,paths=paths, all_open=True, files=self.files, snapshots=self.snapshots)

        top.add(dir_list)


        return top






class SnapshotDirListWdg(DirListWdg):

    def __init__(self, **kwargs):
        if kwargs.get("all_open") == None:
            kwargs["all_open"] = True
        
        super(SnapshotDirListWdg, self).__init__(**kwargs)
        self.snapshots = kwargs.get("snapshots")
        if not self.snapshots:
            self.snapshots = {}

    def add_top_behaviors(self, top):

        # convert this to a repo directory
        asset_dir = Environment.get_asset_dir()
        web_dir = Environment.get_web_dir()

        web = WebContainer.get_web()
        browser = web.get_browser()
        use_applet = web.use_applet()

        if browser == 'Qt':
            top.add_relay_behavior( {
            'type': 'dblclick',
            'bvr_match_class': 'spt_dir_list_item',
            'cbjs_action': '''
            var path = bvr.src_el.getAttribute("spt_path");
            var asset_dir = '%s';
            var web_dir = '%s';
            var relative_dir = path.replace(asset_dir, "");
            var url = web_dir + "/" + relative_dir;

            var url_parts = url.split("/");
            var file = url_parts.pop();
            file = encodeURIComponent(file);
            url_parts.push(file);
            url = url_parts.join("/");

            var class_name = 'tactic.ui.widget.EmbedWdg';
            var kwargs = {
                src: url
            }

            var parts = path.split("/");
            var filename = parts[parts.length-1];
            spt.tab.set_main_body_tab()
            spt.tab.add_new(filename, filename, class_name, kwargs);
            ''' % (asset_dir, web_dir)
            } )
        else:
            top.add_relay_behavior( {
            'type': 'dblclick',
            'bvr_match_class': 'spt_dir_list_item',
            'cbjs_action': '''
            var path = bvr.src_el.getAttribute("spt_path");
            if (path.indexOf('####') != -1) {
                spt.info('Cannot open the file sequence');
            } else {
                var asset_dir = '%s';
                var web_dir = '%s';
                var relative_dir = path.replace(asset_dir, "");
                var url = web_dir + "/" + relative_dir;

                // Encode the filename
                var url_parts = url.split("/");
                var filename = url_parts.pop();
                filename = encodeURIComponent(filename);
                url_parts.push(filename);
                url = url_parts.join("/");

                window.open(url);
            }
            ''' % (asset_dir, web_dir)
            } )

        if use_applet:
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


        self.add_selection(top)
 
        super(SnapshotDirListWdg, self).add_top_behaviors(top)





    def add_file_behaviors(self, item_div, dirname, basename):


        path = "%s/%s" % (dirname, basename)

        file_objects = self.kwargs.get("files")
        file_object = file_objects.get(path)
        if not file_object:
            print("WARNING: No file object for [%s]" % path)
            return
        file_search_key = file_object.get_search_key()


        item_div.add_class("spt_dir_list_item")
        item_div.add_attr("spt_path", path)
        item_div.add_attr("spt_file_search_key", file_search_key)
        SmartMenu.assign_as_local_activator( item_div, 'FILE_MENU_CTX' )



    def get_info(self, dirname, basename):
        location = self.kwargs.get("location")
        # get some info about the file
        path = "%s/%s" % (dirname, basename)

        snapshot = self.snapshots.get(path)
        file_range = None

        if FileGroup.is_sequence(path) and snapshot:
            file_range = snapshot.get_file_range()
            #start_frame = file_range.get_frame_start()
            #end_frame = file_range.get_frame_end()

        if location == 'server':
            self.info = Common.get_dir_info(path, file_range=file_range)
        else:
            self.info = {}
        return self.info


    def handle_item_div(self, item_div, dirname, basename):
        path = "%s/%s" % (dirname, basename)
        if self.info.get("file_type") == 'missing':
            icon_string = IconWdg.DELETE
            tip = 'Missing [%s]' %path
        else:
            icon_string = self.get_file_icon(dirname, basename)
            tip = path

        icon_div = DivWdg()
        icon_div.add_style("display: flex")

        item_div.add(icon_div)
        icon = IconWdg(tip, icon_string)
        icon_div.add(icon)
        icon_div.add_style("margin-right: 3px")



        # add the file name
        filename_div = DivWdg()
        item_div.add(filename_div)
        filename_div.add_style("float: left")
        filename_div.add_style("overflow: hidden")

        snapshot = self.snapshots.get(path)
        file_type = self.info.get('file_type')
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
        size = self.info.get('size')
        if not size:
            size = 0

        from pyasm.common import FormatValue
        size = FormatValue().get_format_value(size, 'KB')

        filesize_div = DivWdg()
        item_div.add(filesize_div)
        filesize_div.add(size)
        #filesize_div.add_style("width: 200px")
        filesize_div.add_style("text-align: right")
        filesize_div.add_style("margin-left: 15px")






    def get_file_icon(self, dir, item):
        if self.info.get("file_type") == 'link':
            return IconWdg.LINK
        return IconWdg.DETAILS

    def get_dir_icon(self, dir, item):
        return IconWdg.LOAD



    def add_selection(self, top):
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
    el.setStyle("background", "");
    el.setAttribute("spt_background", '');
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

    def get_files(self):

        paths = []

        # remember this here for now
        self.files = {}

        self.snapshots = {}


        search_key = self.kwargs.get("search_key")
        search_keys = self.kwargs.get("search_keys")
        if search_key:
            sobject = SearchKey.get_by_search_key(search_key)
            self.sobjects = [sobject]

        if search_keys:
            if isinstance(search_keys, six.string_types):
                search_keys = search_keys.replace("'", '"')
                search_keys = jsonloads(search_keys)
            self.sobjects = Search.get_by_search_keys(search_keys)

        if not self.sobjects:
            return []

        self.sobject = self.sobjects[0]


        for sobject in self.sobjects:
            
            if sobject.get_base_search_type() in ['sthpw/task', 'sthpw/note']:
                parent = sobject.get_parent()
                sobject_paths = self.get_sobject_files(parent)
                paths.extend(sobject_paths)

            else:
                sobject_paths = self.get_sobject_files(sobject)
                paths.extend(sobject_paths)


        return paths


    def get_sobject_files(self, sobject):
        paths = []

        show_versionless = self.kwargs.get("show_versionless")
        if show_versionless in [True, 'true']:
            show_versionless = True
        else:
            show_versionless = False


        if isinstance(sobject, Snapshot):
            snapshots = [sobject]
        else:
            # get the snapshots
            versions = self.get_value("versions")
            search = Search("sthpw/snapshot")

            search.add_parent_filter(sobject)


            if not versions or versions == 'latest':
                search.add_filter("is_latest", True)
            elif versions == 'current':
                search.add_filter("is_current", True)

            if show_versionless:
                search.add_filter("version", -1)
                search.add_op('or')

            processes = self.kwargs.get("processes")
            process = self.get_value("process")
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
                            self.files[item_path] = file

                        for dirname in dirnames:
                            item_path = "%s/%s/" % (root, dirname)
                            paths.append(item_path)
                            self.files[item_path] = file

                else:
                    paths.append(path)
                    self.snapshots[path] = snapshot
                    self.files[path] = file

        return paths



    def get_value(self, name):
        web = WebContainer.get_web()
        value = web.get_form_value(name)
        if not value:
            value = self.kwargs.get(name)
        return value





    def get_display(self):

        paths = self.get_files()

        top = self.top
        top.add_style("padding: 10px")
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("min-width: 500px")
        top.add_style("font-size: 12px")
        top.add_class("spt_sobject_dir_list_top")
        self.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)


        show_title = self.kwargs.get("show_title")
        if show_title not in [False, 'false']:
            title_wdg = DivWdg()
            inner.add(title_wdg)
            title_wdg.add("File Browser [%s]" % self.sobject.get_code())
            title_wdg.add_color("background", "background3")
            title_wdg.add_color("color", "color3")
            title_wdg.add_style("padding: 16px 10px")
            title_wdg.add_style("margin: -10px -10px 10px -10px")
            title_wdg.add_style("font-weight: bold")

        show_shelf = self.kwargs.get("show_shelf")
        if show_shelf not in [False, 'false']:
            shelf_wdg = DivWdg()
            inner.add(shelf_wdg)
            shelf_wdg.add(self.get_shelf_wdg())
            shelf_wdg.add_style("padding: 5px")
            shelf_wdg.add_style("margin: -5px -5px 15px -5px")
            shelf_wdg.add_style("font-weight: bold")



        base_dir = Environment.get_asset_dir()

        dir_list = SnapshotDirListWdg(base_dir=base_dir, location="server", show_base_dir=True,paths=paths, all_open=True, files=self.files, snapshots=self.snapshots)

        inner.add(dir_list)


        if self.kwargs.get("is_refresh"):
            return inner
        else:
            return top



    def get_shelf_wdg(self):

        process = self.get_value("process")
        versions = self.get_value("versions")

        div = DivWdg()

        filter_table = Table()
        div.add(filter_table)
        filter_table.add_row()


        button = SingleButtonWdg(title="Refresh", icon=IconWdg.REFRESH)
        filter_table.add_cell(button)
        filter_table.add_cell("&nbsp;"*5)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.panel.refresh(bvr.src_el);
            '''
        } )

        # get all of the pipelnes for this search type
        pipeline_code = self.sobject.get_value("pipeline_code", no_exception=True)
        processes = []
        if pipeline_code:
            pipeline = Pipeline.get_by_code(pipeline_code)
            if pipeline:
                process_names = pipeline.get_process_names()
                processes.extend(process_names)

        processes.insert(0, "all")



        filter_table.add_cell("Process: ")
        select = SelectWdg("process")
        select.add_style("width: 200px")
        if process != 'all':
            select.set_value(process)

        select.set_option("values", processes)

        filter_table.add_cell(select)



        filter_table.add_cell("&nbsp;"*10)

        filter_table.add_cell("Versions: ")
        select = SelectWdg("versions")
        select.add_style("width: 200px")
        select.set_option("values", "latest|current|today|last 10|all")
        if versions:
            select.set_value(versions)
        filter_table.add_cell(select)


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

    def get_display(self):

        search_key = self.kwargs.get("search_key")
        snapshot = self.kwargs.get("snapshot")

        if snapshot:
            self.snapshot = snapshot
        else:
            self.snapshot = SearchKey.get_by_search_key(search_key)


        assert self.snapshot

        metadata = self.snapshot.get_metadata()

        top = self.top
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
        tr.add_color("background", "background", -5)
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

    ARGS_KEYS = {
        "search_key": {
            'description': "Search key used to extract metadata from",
            'type': 'TextWdg',
            'order': 0,
        },
        "path": {
            'description': "Path of image to be used to extract metadata",
            'type': 'TextWdg',
            'order': 1,
        },
    }
 
    def get_display(self):

        search_key = self.kwargs.get("search_key")
        path = self.kwargs.get("path")
        parser_str = self.kwargs.get("parser")
        use_tactic_tags = self.kwargs.get("use_tactic_tags")


        from pyasm.checkin import BaseMetadataParser, ParserImportError

        #parser_str = "EXIF"
        if parser_str:
            parser = BaseMetadataParser.get_parser(parser_str, path)
        else:
            parser = BaseMetadataParser.get_parser_by_path(path)

        if parser:
            try:
                if use_tactic_tags in ['true', True]:
                    metadata = parser.get_tactic_metadata()
                else:
                    metadata = parser.get_metadata()
            except ParserImportError as e:
                div = DivWdg()
                div.add_class("fa")
                div.add_class("fa-times-circle")
                div.add_style("font-size: 800%")
                div.add_style("color: slategrey")
                div.add_style("line-height: 100px")
                
                msg_div = DivWdg()
                msg_div.add(e)
                msg_div.add_style("font-size: 200%")
                msg_div.add_style("color: grey")

                top = DivWdg()
                top.add(div)
                top.add(msg_div)
                top.add_style("display: flex")
                top.add_style("flex-direction: column")
                top.add_style("justify-content: center")
                top.add_style("align-items: center")
                return top
        else:
            metadata = {}


        parser_title = parser.get_title()


        top = self.top
        top.add_color("background", "background")
        top.add_class("spt_metadata_top")


        shelf = DivWdg()
        top.add(shelf)
        from tactic.ui.widget import ActionButtonWdg
        button = ActionButtonWdg(title="Add Selected to Keywords", width="200")
        shelf.add(button)
        shelf.add_style("margin: 10px 0px")
        button.add_behavior( {
            'search_key': search_key,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_metadata_top");
            var values = spt.api.get_input_values(top, null, true);
            var searchables = values.searchable;
            var items = [];
            for (var i = 0; i < searchables.length; i++) {
                if (searchables[i] == "") {
                    continue;
                }
                items.push(searchables[i]);
            }

            var server = TacticServerStub.get();

            var class_name = 'spt.modules.workflow.AssetAddMetadataToKeywordsCmd';
            var kwargs = {
                search_key: bvr.search_key,
                items: items,
            };
            server.p_execute_cmd(class_name, kwargs)
            .then( function() {
                spt.api.clear_inputs(top);
                spt.notify.show_message("Added Keywords");
            } )


            '''
        } )


        table = Table()
        table.add_style("width: 100%")
        #table.add_style("table-layout: fixed")
        top.add(table)
        table.set_unique_id()

        table.add_smart_styles("spt_cell", {
            'padding': '3px'
        } )


        tr, td = table.add_row_cell()
        td.add(parser_title)
        td.add_style("height: 20px")
        td.add_style("font-weight: bold")
        td.add_style("padding: 5px 3px")
        td.add_color("background", "background", -5)
        border_color = td.get_color("border")
        td.add_color("border-bottom", "solid 1px %s" % border_color)

        tr.add_class("tactic_hover")


        """
        tr = table.add_row()
        tr.add_color("background", "background", -5)
        th = table.add_header("Property")
        th.add_style("min-width: 200px")
        th.add_style("padding: 5px")
        th = table.add_header("Value")
        #th.add_style("min-width: 400px")
        th.add_style("padding: 5px")
        """

        keys = metadata.get("__keys__")
        if not keys:
            keys = list(metadata.keys())

        empty = False
        if not keys:
            empty = True
            keys = ['','','','','','','']
            table.add_smart_styles("spt_cell", {
                'height': '20px'
            } )

        keys.sort()


        for i, key in enumerate(keys):
            value = metadata.get(key)

            value = Common.process_unicode_string(value)


            if not isinstance(key, six.string_types):
                key = str(key)
            #title = Common.get_display_title(key)
            title = key

            tr = table.add_row()
            tr.add_class("tactic_hover")

            if i % 2:
                tr.add_color("background", "background", -2)
                tr.add_color("color", "color")
            else:
                tr.add_color("background", "background")
                tr.add_color("color", "color")

            td = table.add_cell()
            td.add_class("spt_cell")
            td.add(title)
            td.add_style("width: 300px")
            td.add_style("min-width: 200px")

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
            td.add_style("max-width: 600px")

            td.add_style("overflow: hidden")
            td.add_style("text-overflow: ellipsis")
            td.add_style("white-space: nowrap")





            td = table.add_cell()
            td.add_class("spt_cell")

            try:
                is_ascii = True
                for c in str(value):
                    if ord(c) > 128:
                        is_ascii = False
                        break
                if not is_ascii:
                    continue
            except Exception as e:
                print("WARNING: ", e)
                continue



            from pyasm.widget import CheckboxWdg
            checkbox = CheckboxWdg("searchable")
            checkbox.add_attr("spt_is_multiple", "true")
            td.add(checkbox)
            td.add_style("width: 40px")
            td.add_style("max-width: 30px")
            checkbox.set_option("value", "%s|%s|%s" % (parser_title,key,value))



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










