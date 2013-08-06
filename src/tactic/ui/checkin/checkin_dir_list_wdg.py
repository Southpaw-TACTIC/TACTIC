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


__all__ = ['CheckinDirListWdg']

from pyasm.common import Environment, Common, FormatValue
from pyasm.search import SearchKey, Search
from pyasm.biz import Snapshot
from pyasm.web import DivWdg, SpanWdg
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import DirListWdg
from tactic.ui.container import DialogWdg, Menu, MenuItem, SmartMenu

import os


class CheckinDirListWdg(DirListWdg):


    def preprocess(my):
        # find out if there is a snapshot associated with this path
        #print "sobject: ", my.sobject

        #context = "design/%s" % basename
        #search = Search("sthpw/snapshot")
        #search.add_filter("context", context)
        #my.sobject = search.get_sobject()

        search_key = my.kwargs.get("search_key")
        my.sobject = Search.get_by_search_key(search_key)

        md5s = my.kwargs.get("md5s")
        sizes = my.kwargs.get("sizes")

        # bit of a hack get the file system paths
        spaths = []
        my.md5s = {}
        my.sizes = {}
        for i, path in enumerate(my.paths):
            #path = Common.get_filesystem_name(path)
            #new_path = path.replace(" ", "_")
            new_path = path
            spaths.append(new_path)

            my.md5s[new_path] = md5s[path]
            my.sizes[new_path] = sizes[path]


        process = my.kwargs.get("process")

        # need to match up files 
        search = Search("sthpw/file")
        search.add_sobject_filter(my.sobject)
        snapshots = []
        if process:
            search2 = Search("sthpw/snapshot")
            search2.add_filter("process", process)
            search2.add_filter("is_latest", True)
            search2.add_sobject_filter(my.sobject)
            snapshots = search2.get_sobjects()
            search.add_relationship_search_filter(search2)
        #search.add_filters("source_path", spaths)
        sobjects = search.get_sobjects()

        my.snapshots_dict = {}
        for snapshot in snapshots:
            my.snapshots_dict[snapshot.get_code()] = snapshot


        my.base_dir = my.kwargs.get("base_dir")
        my.checked_in_paths = {}
        for sobject in sobjects:
            source_path = sobject.get_value("source_path")
            if not source_path:
                print "WARNING: source_path for file [%s] is empty" % sobject.get_code()
                continue
            my.checked_in_paths[source_path] = sobject

            #print "source_path: ", source_path
            #if not source_path.startswith(my.base_dir):
            #    basename = os.path.basename(source_path)
            #    my.checked_in_paths[basename] = sobject
            #else:
            #    basename = source_path.replace(my.base_dir, "")
            #    my.checked_in_paths[basename] = sobject
            # get the snapshot
            snapshot = my.snapshots_dict.get(sobject.get_value("snapshot_code"))
            context = snapshot.get_value("context")
            parts = context.split("/")
            if len(parts) > 1:
                rel = "/".join( parts[1:] )
                if source_path.endswith(rel):
                    my.checked_in_paths[rel] = sobject





        # this is advanced option
        my.context_options = my.kwargs.get("context_options")

        my.subcontext_options = my.kwargs.get("subcontext_options")
        # do not set default here, let FileCheckin determine it
        #if not my.subcontext_options:
        #    my.subcontext_options = ["(auto)"]


        my.preselected = my.kwargs.get("preselected")



    def add_base_dir_behaviors(my, div, base_dir):

        # add tooltip
        div.add_attr('title','This is the sandbox folder. Double-click to open and right-click for more options.')
        # add a top menu
        menu = Menu(width=180)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label='Explore sandbox folder')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'base_dir': base_dir,
            'cbjs_action': '''
            var applet = spt.Applet.get();
            var activator = spt.smenu.get_activator(bvr);
            var path = bvr.base_dir;
            applet.open_file(path);
            '''
        } )


        menu_item = MenuItem(type='action', label='Browse for sandbox folder')
        menu.add(menu_item)
        # FIXME: this code is identical to the one in checkin_wdg.py
        menu_item.add_behavior( {
        'type': 'click_up',
        'base_dir': base_dir,
        'cbjs_action': '''
            var current_dir = bvr.base_dir;
            var applet = spt.Applet.get();
            var file_paths = applet.open_file_browser(current_dir);

            // take the first one make sure it is a directory
            var dir = file_paths[0];
            if (!applet.is_dir(dir)) {
                spt.alert("Please Select a Folder");
                return;
            }
            dir = dir.replace(/\\\\/g, "/");

            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_checkin_top");
            top.setAttribute("spt_sandbox_dir", dir);
            spt.panel.refresh(top);

        '''
        } )


        menu_item = MenuItem(type='action', label='Download from clipboard')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'base_dir': base_dir,
        'cbjs_action': '''
        var current_dir = bvr.base_dir;
        var server = TacticServerStub.get();
        var base = spt.Environment.get().get_server_url();
        var user = spt.Environment.get().get_user();

        var expr = "@SOBJECT(sthpw/clipboard['login','"+user+"'].sthpw/file)";
        var items = server.eval(expr);

        var applet = spt.Applet.get();

        var urls = [];
        for (var i = 0; i < items.length; i++) {
            var url = base + "/assets/" + items[i].relative_dir + "/" + items[i].file_name;
            var file_name = items[i].file_name;
            applet.download_file(url, current_dir + "/" + file_name);
        }

        var activator = spt.smenu.get_activator(bvr);
        var top = activator.getParent(".spt_checkin_top");
        spt.panel.refresh(top);

        '''
        } )

        menus_in = {
            'SANDBOX_MENU_CTX': menu,
        }
        SmartMenu.attach_smart_context_menu( div, menus_in, False )
        SmartMenu.assign_as_local_activator( div, 'SANDBOX_MENU_CTX' )


        super(CheckinDirListWdg, my).add_base_dir_behaviors(div,base_dir)



    def handle_dir_div(my, dir_div, dirname, basename):
        my.handle_dir_or_item(dir_div, dirname, basename)


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

        my.handle_dir_or_item(item_div, dirname, basename)

        size_div = DivWdg()
        size_div.add(FormatValue().get_format_value(my.sizes.get(path), 'KB'))
        size_div.add_style("float: left")
        item_div.add(size_div)
        size_div.add_style("margin-right: 30px")
        size_div.add_style("width: 60px")
        size_div.add_style('text-align: right')

        #icon_div = DivWdg()
        #item_div.add(icon_div)
        #icon = IconWdg("Delvered to next process", IconWdg.JUMP)
        #icon_div.add(icon)
        #icon_div.add_style("float: right")
        #icon_div.add_style("margin-top: -1px")

        item_div.add("<br clear='all'/>")




    def handle_dir_or_item(my, item_div, dirname, basename):
        spath = "%s/%s" % (dirname, basename)
        md5 = my.md5s.get(spath)
        changed = False
        context = None
        error_msg = None
        snapshot = None
        file_obj = my.checked_in_paths.get(spath)
        if not file_obj:
            if spath.startswith(my.base_dir):
                rel = spath.replace("%s/" % my.base_dir, "")
                file_obj = my.checked_in_paths.get(rel)


        if file_obj != None:

            snapshot_code = file_obj.get_value("snapshot_code")
            snapshot = my.snapshots_dict.get(snapshot_code)
            if not snapshot:
                # last resort
                snapshot = file_obj.get_parent()

            if snapshot:
                context = snapshot.get_value("context")
                item_div.add_attr("spt_snapshot_code", snapshot.get_code())

                snapshot_md5 = file_obj.get_value("md5")
                item_div.add_attr("spt_md5", snapshot_md5)
                item_div.add_attr("title", "Checked-in as: %s" % file_obj.get_value("file_name"))

                if md5 and md5 != snapshot_md5:
                    item_div.add_class("spt_changed")
                    changed = True
            else:
                error_msg = 'snapshot not found'

            


        status = None
        if file_obj != None:
            if changed:
                check = IconWdg( "Checked-In", IconWdg.ERROR, width=12 )
                status = "changed"
            else:
                check = IconWdg( "Checked-In", IconWdg.CHECK, width=12 )
                status = "same"
            item_div.add_color("color", "color", [0, 0, 50])

        else:
            check = None
            item_div.add_style("opacity: 0.8")
            status = "unversioned"



        if check:
            item_div.add(check)
            check.add_style("float: left")
            check.add_style("margin-left: -16px")
            check.add_style("margin-top: 4px")


        # add the file name
        filename_div = DivWdg()
        item_div.add(filename_div)
        filename_div.add(basename)
        file_info_div = None
        if snapshot and status != 'unversioned':
            file_info_div = SpanWdg()
            filename_div.add(file_info_div)

        if error_msg:
            filename_div.add(' (%s)'%error_msg)
        filename_div.add_style("float: left")
        filename_div.add_style("overflow: hidden")
        filename_div.add_style("width: 65%")


        # DEPRECATED
        from pyasm.widget import CheckboxWdg, TextWdg, SelectWdg, HiddenWdg
        checkbox = CheckboxWdg("check")
      

        checkbox.add_style("display: none")
        checkbox.add_class("spt_select")
        checkbox.add_style("float: right")
        checkbox.add_style("margin-top: 1px")
        item_div.add(checkbox)

        subcontext_val = ''
        cat_input = None
        is_select = True
        if my.context_options:
            context_sel = SelectWdg("context")
            context_sel.add_attr('title', 'context')
            context_sel.set_option("show_missing", False)
            context_sel.set_option("values", my.context_options)
            item_div.add_attr("spt_context", my.context_options[0]) 
            cat_input = context_sel
            input_cls = 'spt_context'

    
        else:
            if my.subcontext_options in [['(main)'], ['(auto)'] , []]:
                is_select = False
                #subcontext = TextWdg("subcontext")
                subcontext = HiddenWdg("subcontext")
                subcontext.add_class("spt_subcontext")

            elif my.subcontext_options == ['(text)']:
                is_select = False
                subcontext = TextWdg("subcontext")
                subcontext.add_class("spt_subcontext")

            else:
                is_select = True


                subcontext = SelectWdg("subcontext")
                subcontext.set_option("show_missing", False)
                subcontext.set_option("values", my.subcontext_options)
                #subcontext.add_empty_option("----")


            cat_input = subcontext
            input_cls = 'spt_subcontext'
            
          


            if my.subcontext_options == ['(main)'] or my.subcontext_options == ['(auto)']:
                subcontext_val = my.subcontext_options[0]
                subcontext.set_value(subcontext_val)
                item_div.add_attr("spt_subcontext", subcontext_val)
            elif context:
                parts = context.split("/")
                if len(parts) > 1:

                    # get the actual subcontext value
                    subcontext_val = "/".join(parts[1:])

                    # identify a previous "auto" check-in and preselect the item in the select
                    if is_select and subcontext_val not in my.subcontext_options:
                        subcontext_val = '(auto)'

                    elif isinstance(cat_input,  HiddenWdg):
                        subcontext_val =  ''
					# the Text field will adopt the subcontext value of the last check-in
                    subcontext.set_value(subcontext_val)
                    item_div.add_attr("spt_subcontext", subcontext_val)

            else:
                if is_select:
                    subcontext_val = '(auto)'
                    cat_input.set_value(subcontext_val)
                else:
                    subcontext_val = ''
                item_div.add_attr("spt_subcontext", subcontext_val)
        item_div.add(cat_input)


        cat_input.add_behavior( {
                'type': 'click_up',
                'propagate_evt': False,
                'cbjs_action': '''
                bvr.src_el.focus();
                '''
            } )

        cat_input.add_style("display: none") 
        cat_input.add_class("spt_subcontext")
        cat_input.add_style("float: right")
        cat_input.add_style("width: 50px")
        cat_input.add_style("margin-top: -1px")
        cat_input.add_style("font-size: 10px")
        cat_input.add_style("height: 16px")


        # we depend on the attribute cuz sometimes we go by the initialized value 
        # since they are not drawn
        cat_input.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var el = bvr.src_el.getParent('.spt_dir_list_item');
            el.setAttribute("%s", bvr.src_el.value);
            ''' %input_cls
        } )


       


        if file_info_div:
            if subcontext_val in ['(auto)','(main)', '']:
                file_info_div.add(" <i style='font-size: 9px; opacity: 0.6'>(v%s)</i>" % snapshot.get_value("version") )
            else:
                file_info_div.add(" <i style='font-size: 9px; opacity: 0.6'>(v%s - %s)</i>" % (snapshot.get_value("version"), subcontext_val) )







    def add_top_behaviors(my, top):
        if my.sobject:
            search_key = my.sobject.get_search_key()
        else:
            search_key = None

        bg_color = top.get_color("background")
        hilight_color =  top.get_color("background", -20)

        top.add_behavior( {
        'type': 'smart_click_up',
        'bvr_match_class': 'spt_dir_list_item',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_checkin_top");
        spt.checkin_list.set_top(top);

        spt.checkin_list.unselect_all_rows();
        spt.checkin_list.select(bvr.src_el);

        var applet = spt.Applet.get();

        var path = bvr.src_el.getAttribute("spt_path");
        var checkin_type = top.getElement(".spt_checkin_type");
        if (applet.is_dir(path)) {
            checkin_type.value = "dir_checkin";
        }
        else {
            checkin_type.value = "file_checkin";
        }

        ''' %{'bg_color': bg_color, 'hilight_color': hilight_color}
        } )


        top.add_behavior( {
        'type': 'smart_click_up',
        'bvr_match_class': 'spt_dir_list_item',
        'modkeys': 'CTRL',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_checkin_top");
        spt.checkin_list.set_top(top);

        //spt.checkin_list.unselect_all_rows();
        spt.checkin_list.select(bvr.src_el);

        var applet = spt.Applet.get();

        var path = bvr.src_el.getAttribute("spt_path");
        var checkin_type = top.getElement(".spt_checkin_type");
        if (applet.is_dir(path)) {
            checkin_type.value = "dir_checkin";
        }
        else {
            checkin_type.value = "file_checkin";
        }

        ''' %{'bg_color': bg_color, 'hilight_color': hilight_color}
        } )



        top.add_behavior( {
        'type': 'load',
        'cbjs_action': '''

//for shift click feature
spt.checkin_list = {};
spt.checkin_list.top = null;
spt.checkin_list.last_selected = null;
spt.checkin_list.single_select = false;

spt.checkin_list.set_top = function(top) {
    spt.checkin_list.top = top;
}



spt.checkin_list.get_selected_paths = function() {
    // find the subcontext widget
    var rows = spt.checkin_list.get_all_rows();

    var paths = [];
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        if (row.is_selected == true) {
            var path = row.getAttribute("spt_path");
            paths.push(path);
        }
    }
    return paths;
} 


spt.checkin_list.get_all_rows = function() {
    var rows = spt.checkin_list.top.getElements(".spt_dir_list_item");
    return rows;
}

spt.checkin_list.unselect_all_rows = function() {

    var rows = spt.checkin_list.get_all_rows();
    for (var i = 0; i < rows.length; i++) {
        spt.checkin_list.unselect(rows[i]);
    }

}


spt.checkin_list.unselect = function(row) {
    var subcontext_el = row.getElement(".spt_subcontext");
    var context_el = row.getElement(".spt_context")
    row.is_selected = false;
    row.setStyle("background", '%(bg_color)s');
    row.setAttribute("spt_background", '%(bg_color)s');
    if (subcontext_el)
        subcontext_el.setStyle("display", "none");
    else if (context_el)
        context_el.setStyle("display", "none");

    spt.checkin_list.last_selected = null;

    spt.checkin_list.disable_checkin();
}



spt.checkin_list.select = function(row) {
    // find the subcontext widget
    var subcontext_el = row.getElement(".spt_subcontext")
    var context_el = row.getElement(".spt_context")

    if (row.is_selected == true) {
        row.is_selected = false;
        row.setStyle("background", '%(bg_color)s');
        row.setAttribute("spt_background", '%(bg_color)s');
        if (subcontext_el)
            subcontext_el.setStyle("display", "none");
        else if (context_el)
            context_el.setStyle("display", "none");

        spt.checkin_list.last_selected = null;

    }
    else {
        row.is_selected = true;
        row.setStyle("background", '%(hilight_color)s');
        row.setAttribute("spt_background", '%(hilight_color)s');
        if (subcontext_el)
            subcontext_el.setStyle("display", "");
		else if (context_el)
            context_el.setStyle("display", "");
        
        spt.checkin_list.last_selected = row;
    }
    var top = spt.checkin_list.top; 
    var paths = [];
    var els = top.getElements(".spt_dir_list_item");
    for (var i = 0; i < els.length; i++) {
        if (els[i].is_selected) {
            paths.push( els[i].getAttribute("spt_path") );
        }
    }

    var grey_el = top.getElement(".spt_publish_disable");
    if (paths.length == 0) {
        grey_el.setStyle("display", "");
        return;
    }

    grey_el.setStyle("display", "none");
}


spt.checkin_list.enable_checkin = function() {
    var top = spt.checkin_list.top; 
    var grey_el = top.getElement(".spt_publish_disable");
    grey_el.setStyle("display", "none");
} 


spt.checkin_list.disable_checkin = function() {
    var top = spt.checkin_list.top; 
    var grey_el = top.getElement(".spt_publish_disable");
    grey_el.setStyle("display", "");
} 





spt.checkin_list.select_preselected = function(){
    var top = spt.checkin_list.top; 
    var el = top.getElement(".spt_file_selector");
    if (el == null) {
        return;
    }

    var rows = spt.checkin_list.get_all_rows()
    //var cbs = top.getElements(".spt_dir_list_item");
    var paths = [];
    for (var k=0; k<rows.length; k++){
        var row = rows[k];
        if (spt.has_class(row, 'spt_preselected')) {
            var path = row.getAttribute("spt_path");
            paths.push(path); 
            spt.checkin_list.select(row);
        }
    }
    // reassign the new paths selection
    el.file_paths = paths;
}


var top = bvr.src_el.getParent(".spt_checkin_top");
spt.checkin_list.set_top(top);
spt.checkin_list.select_preselected();


        ''' %{'bg_color': bg_color, 'hilight_color': hilight_color}
        } )
 

        top.add_behavior( {
        'type': 'smart_click_up',
        'modkeys': 'SHIFT',
        'bvr_match_class': 'spt_dir_list_item',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_checkin_top");

        spt.checkin_list.set_top(top);

        var rows = spt.checkin_list.get_all_rows();

        var last_selected = spt.checkin_list.last_selected;
        var last_index;
        var cur_index;
        for (var i = 0; i < rows.length; i++) {
            if (rows[i] == last_selected) {
                last_index = i;
            }
            if (rows[i] == bvr.src_el) {
                cur_index = i;
            }
        }
        var start_index;
        var end_index;
        if (last_index < cur_index) {
            start_index = last_index + 1;
            end_index = cur_index ;
        }
        else {
            start_index = cur_index;
            end_index = last_index -1 ;
        }

        for (var i = start_index; i < end_index+1; i++) {
            spt.checkin_list.select(rows[i]);
        }

        spt.checkin_list.last_selected = bvr.src_el;
        '''
        } )




        # add a top menu
        menu = Menu(width=180)
        my.menu = menu
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        #menu_item = MenuItem(type='action', label='Revert to Latest')
        #menu.add(menu_item)




        menu_item = MenuItem(type='action', label='Open File')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var applet = spt.Applet.get();

            var activator = spt.smenu.get_activator(bvr);
            var path = activator.getAttribute("spt_path");
            applet.open_file(path);
            '''
        } )



        menu_item = MenuItem(type='action', label='Open Containing Folder')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var applet = spt.Applet.get();

            var activator = spt.smenu.get_activator(bvr);
            var path = activator.getAttribute("spt_path");
            var parts = path.split("/");
            parts.pop()
            path = parts.join("/");
            applet.open_explorer(path);
            '''
        } )



        menu_item = MenuItem(type='action', label='Copy File to Sandbox')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var applet = spt.Applet.get();

            var activator = spt.smenu.get_activator(bvr);
            var path = activator.getAttribute("spt_path");

            var selected_paths = spt.checkin_list.get_selected_paths();
            if (!selected_paths.length) {
                selected_paths = [path];
            }

            var top = activator.getParent(".spt_checkin_top");
            var default_sandbox_dir = top.getAttribute("spt_default_sandbox_dir");

            spt.app_busy.show("Copying files to Sandbox");
            for (var i = 0; i < selected_paths.length; i++) {
                var path = selected_paths[i];
                var parts = path.split("/");
                var filename = parts[parts.length-1];
                applet.copy_file(path, default_sandbox_dir + "/" + filename);
            }
            spt.app_busy.hide();

            spt.notify.show_message("Copied " + selected_paths.length + " files to sandbox");
            '''
        } )


 


        #menu_item = MenuItem(type='action', label='Rename File')
        #menu.add(menu_item)

        # DISABLING until we actually have something that works better
        menu_item = MenuItem(type='action', label='Copy File')
        #menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var path = activator.getAttribute("spt_path");
            var applet = spt.Applet.get();

            var parts = path.split("/");
            var basename = parts[parts.length-1];

            // FIXME: new to create new path
            var new_path = path + "_copy";
            var index = 1;
            while(1) {
                if (applet.exists(new_path)) {
                    new_path = path + "_copy" + index;
                    index += 1;
                }
                else {
                    break;
                }

                if (index > 100) {
                    spt.alert("More than 100 copies.  Exiting");
                    break;
                }
            }

            applet.copy_file(path, new_path);

            var top = activator.getParent(".spt_checkin_top");
            spt.panel.refresh(top);
            '''
        } )



        menu_item = MenuItem(type='separator')
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label='Delete File')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''

            var activator = spt.smenu.get_activator(bvr);
            var path = activator.getAttribute("spt_path");
            var parts = path.split("/");
            var filename = parts[parts.length-1];

            var applet = spt.Applet.get();
            var label = applet.is_dir(path) ? 'directory': 'file';
            if (!confirm("Are you sure you wish to delete the local " + label + " ["+filename+"]?")) {
                return;
            }

            applet.rmtree(path);

            var top = activator.getParent(".spt_checkin_top");
            spt.panel.refresh(top);
            '''
        } )


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label='Properties')
        menu.add(menu_item)

        menu_item.add_behavior( {
            'type': 'click_up',
            'search_key': search_key,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);

            var snapshot_code = activator.getAttribute("spt_snapshot_code");
            var path = activator.getAttribute("spt_path");
            var md5 = activator.getAttribute("spt_md5");

            var applet = spt.Applet.get();
            var cur_md5 = applet.get_md5(path);

            //if (md5 != cur_md5) {
            //    activator.setStyle("background", "#A77");
            //}


            var class_name = 'tactic.ui.checkin.FilePropertiesWdg';
            var kwargs = {
                path: path,
                md5: cur_md5,
                snapshot_code: snapshot_code,
                search_key: bvr.search_key
            };
            spt.panel.load_popup("File Properties", class_name, kwargs);
            '''
        } )


        menu_item = MenuItem(type='action', label='Use as Preview Image')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'search_key': search_key,
            'cbjs_action': '''
            var server = TacticServerStub.get();

            var activator = spt.smenu.get_activator(bvr);
            var path = activator.getAttribute("spt_path");

            var context = "icon";
            server.simple_checkin( bvr.search_key, context, path);

            var top = activator.getParent(".spt_checkin_top");
            spt.panel.refresh(top);
            '''
        } )

        menus_in = {
            'FILE_MENU_CTX': menu,
        }
        SmartMenu.attach_smart_context_menu( top, menus_in, False )
 
        super(CheckinDirListWdg, my).add_top_behaviors(top)




    def add_dir_behaviors(my, dir_div, dirname, basename):

        path = "%s/%s" % (dirname, basename)
        dir_div.add_attr("spt_path", path)

        dir_div.add_class("spt_dir_list_item")
        SmartMenu.assign_as_local_activator( dir_div, 'FILE_MENU_CTX' )
        dir_div.add_class("spt_dir")
        # for explicit Browse
        if my.preselected:
            dir_div.add_class("spt_preselected")
            # for dir, only preselect the first one
            my.preselected = False
        super(CheckinDirListWdg, my).add_dir_behaviors(dir_div, dirname, basename)




    def add_file_behaviors(my, item_div, dirname, basename):

        path = "%s/%s" % (dirname, basename)
        item_div.add_attr("spt_path", path)

        item_div.add_class("spt_dir_list_item")
        SmartMenu.assign_as_local_activator( item_div, 'FILE_MENU_CTX' )
        # for explicit Browse
        if my.preselected:
            item_div.add_class("spt_preselected") 
        super(CheckinDirListWdg, my).add_file_behaviors(item_div, dirname, basename)



