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
#

__all__ = ['DirListWdg', 'DirInfoWdg', 'FileInfoWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Common, Config, jsonloads, jsondumps, Environment
from pyasm.command import Command, DatabaseAction
from pyasm.web import DivWdg, Table, SpanWdg, FloatDivWdg, WebContainer, HtmlElement, SpanWdg
from pyasm.search import Search, SearchType, WidgetDbConfig
from pyasm.widget import ProdIconButtonWdg, TextWdg, IconWdg, SelectWdg, SwapDisplayWdg, HiddenWdg, CheckboxWdg

from tactic.ui.container import Menu, MenuItem, SmartMenu

from .button_new_wdg import ActionButtonWdg, IconButtonWdg, SingleButtonWdg

import os

import six
basestring = six.string_types



class DirListWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'base_dir': {
        'description': 'Base Directory of the file list',
        'type': 'TextWdg',
        'order': 1,
        'category': 'Options'
    },
 

    'location': {
        'description': 'Determines whether files are relative to the client or the server',
        'type': 'SelectWdg',
        'values': 'server|client',
        'order': 2,
        'category': 'Options'
    },
    }



 

    def add_style(self, name, value=None):
        self.top.add_style(name, value)


    def get_depth(self):
        depth = self.kwargs.get("depth")
        if depth == None:
            depth = -1
        elif isinstance(depth, basestring):
            depth = int(depth)
        return depth



    def get_relative_paths(self, base_dir):

        # put a maximum for now
        depth = self.kwargs.get("depth")
        if depth == None:
            depth = -1
        elif isinstance(depth, basestring):
            depth = int(depth)


        location = self.kwargs.get("location")
        self.paths = self.kwargs.get("paths")

        # a little hacky
        if isinstance(self.paths, basestring):
            self.paths = self.paths.replace("'", '"');
            self.paths = jsonloads(self.paths)
            return self.paths

        self.directory = None
        from pyasm.common.directory import Directory
        if self.paths == []:
            pass
        elif self.paths is None and location == 'server':
            self.directory = Directory(base_dir=base_dir, depth=depth)
            self.paths = self.directory.get_all_paths()
            #self.paths = []
        elif location == 'scm':
            self.directory = Directory(paths=self.paths, base_dir=base_dir)
        else:
            self.directory = Directory(paths=self.paths, base_dir=base_dir)

        if self.directory:
            self.paths = self.directory.get_all_paths()

        if not self.paths:
            self.paths = []

        # switching "\" to "/"
        self.paths = [path.replace("\\","/") for path in self.paths]
        self.paths.sort()

        return self.paths



    def init(self):

        self.data = {}

        self.level = self.kwargs.get("level")
        if not self.level:
            self.level = 0


        self.base_dir = self.kwargs.get("base_dir")

        # root directory is starts at the first base_dir
        self.root_dir = self.kwargs.get("root_dir")
        if not self.root_dir:
            self.root_dir = self.base_dir



        self.paths = self.kwargs.get("paths")
        if not self.paths:
            self.paths = []


        self.handler_kwargs = self.kwargs.get('handler_kwargs')
        self.preselected = {}
        self.use_applet = True
        self.preprocess()




    def preprocess(self):
        # provide the opportunity to preprocess information
        pass


    def get_paths(self):
        #raise Exception("What runs this??")
        return self.paths


    def get_num_paths(self):
        return len(self.paths)


    def get_selection_wdg(self, bg_color, hilight_color):
        '''get the Select All checkbox menu widget'''
        select_all_wdg = DivWdg()
        select_all_wdg.add("Select All ")
        checkbox = CheckboxWdg("select_all")
        select_all_wdg.add(checkbox)

        select_all_wdg.add_color("background", "background3")
        select_all_wdg.add_style("padding: 3px")
        select_all_wdg.add_style("margin-top: -8px")
        select_all_wdg.add_border()

        checkbox.add_behavior( {
        'type': 'click_up',
        #'propagate_evt': True,
        'bg_color': bg_color,
        'hilight_color': hilight_color,
        'cbjs_action': '''

        var value = bvr.src_el.checked;
        var top = bvr.src_el.getParent(".spt_checkin_sandbox_top");
        var els = top.getElements(".spt_dir_list_item");

        var real_top = bvr.src_el.getParent(".spt_checkin_top");


        var paths = [];
#
        for (var i = 0; i < els.length; i++) {
            var el = els[i];
            if (el.hasClass("spt_dir")) {
                continue;
            }
            //matching the inverse of cb value
            el.is_selected = !value;
            spt.checkin_list.select(el);
         
        }
      
        '''
        } )





        from tactic.ui.widget import IconButtonWdg
        icon = IconButtonWdg(title="More Select Options", icon=IconWdg.ARROWHEAD_DARK_DOWN)
        icon.add_style("float: right")
        select_all_wdg.add(icon)


        menu = Menu(width=180)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Select Changed Files')
        menu.add(menu_item)


        menu_item.add_behavior( {
        'type': 'click_up',
        #'propagate_evt': True,
        'bg_color': bg_color,
        'hilight_color': hilight_color,
        'cbjs_action': '''
        var button = spt.smenu.get_activator(bvr);

        var top = button.getParent(".spt_checkin_sandbox_top");
        //var real_top = button.getParent(".spt_checkin_top");
        //var el = real_top.getElement(".spt_file_selector");
        var els = top.getElements(".spt_dir_list_item");

        for (var i = 0; i < els.length; i++) {
            var value = els[i].hasClass("spt_changed");

            if (els[i].hasClass("spt_dir")) {
                continue;
            }
            // trick it to think it's already selected to turn it off
            // since spt.checkin_list.select() is like a toggle
            if (value == false) {
                els[i].is_selected = true;
            }
            else {
                els[i].is_selected = false;
            }
            spt.checkin_list.select(els[i]);
            
        }
      
        
        '''
        } )

        menu_item = MenuItem(type='action', label='Toggle Selection')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'bg_color': bg_color,
        'hilight_color': hilight_color,
        'cbjs_action': '''
        var button = spt.smenu.get_activator(bvr);

        var top = button.getParent(".spt_checkin_sandbox_top");
        var els = top.getElements(".spt_dir_list_item");

        for (var i = 0; i < els.length; i++) {

            if (els[i].hasClass("spt_dir")) {
                continue;
            }
            // this does toggling
            spt.checkin_list.select(els[i]);
            
        }
        '''
        } )



        menu_item = MenuItem(type='action', label='Unselect All')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'bg_color': bg_color,
        'hilight_color': hilight_color,
        'cbjs_action': '''
        var button = spt.smenu.get_activator(bvr);
        var top = button.getParent(".spt_checkin_top");
        spt.checkin_list.set_top(top);
        spt.checkin_list.unselect_all_rows();
        '''
        } )





        SmartMenu.add_smart_menu_set( icon, { 'BUTTON_MENU': menu } )
        SmartMenu.assign_as_local_activator( icon, "BUTTON_MENU", True )
        return select_all_wdg



    def get_no_paths_wdg(self):
        no_files_wdg = DivWdg()
        no_files_wdg.add("&nbsp;"*5)
        no_files_wdg.add("<i>-- No files found --</i>")
        #no_files_wdg.add_style("opacity: 0.5")
        no_files_wdg.add_style("margin: 30px auto")
        no_files_wdg.add_color("color", "color3")
        no_files_wdg.add_color("background", "background3")
        no_files_wdg.add_style("text-align", "center")
        no_files_wdg.add_style("padding-top: 20px")
        no_files_wdg.add_style("padding-bottom: 20px")
        no_files_wdg.add_style("width: 250px")
        no_files_wdg.add_border()
        return no_files_wdg









    def get_display(self):

        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_dir_list_top")
        top.add_class("SPT_DTS")


        self.add_load_behavior()
        self.add_top_behaviors(top)


        # FIXME: these break selection in Check-in widget
        """
        hover = top.get_color("background", -8)
        top.add_relay_behavior( {
            'type': 'mouseover',
            'bgcolor': hover,
            'bvr_match_class': "spt_dir_item",
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.bgcolor);
            '''
        } )
        top.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': "spt_dir_item",
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )
        top.add_relay_behavior( {
            'type': 'mouseover',
            'bgcolor': hover,
            'bvr_match_class': "spt_file_item",
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.bgcolor);
            '''
        } )
        top.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': "spt_file_item",
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )
        """



        base_dir = self.kwargs.get("base_dir")

        location = self.kwargs.get("location")
        if not location:
            location = 'server'

        show_selection = self.kwargs.get("show_selection")
        if show_selection == None:
            show_selection = False

        show_base_dir = self.kwargs.get("show_base_dir")
        if not base_dir and show_base_dir:
            top.add("No folder specified")
            return top

        if show_base_dir in ['false', False]:
            pass
        else:
            dir_title = DivWdg()

            icon_div = DivWdg()
            dir_title.add(icon_div)

            icon = IconWdg("%s" % base_dir, "FA_FOLDER_OPEN")
            icon_div.add(icon)
            icon_div.add_style("float: left")

            display_dir = base_dir
            display_dir = os.path.basename(display_dir)

            title_div = FloatDivWdg("%s" % display_dir)
            title_div.add_style("margin-left: 5px")
            dir_title.add(title_div)
            title_div.add_style("padding-top: 2px")
            
            dir_title.add_style("margin-bottom: 8px")
            dir_title.add_attr("spt_path", base_dir)

            self.add_base_dir_behaviors(title_div, base_dir)

            top.add(dir_title)

            background = self.kwargs.get("background")
            if not background:
                background = "background"
            bg_color = dir_title.get_color(background)
            hilight_color =  dir_title.get_color(background, -10)

            if show_selection:
                select_wdg = self.get_selection_wdg(bg_color, hilight_color)
                select_div = DivWdg(select_wdg)
                select_div.add_style('float: right')

                
                dir_title.add(select_div)
                top.add(HtmlElement.br(2))
            else:
                dir_title.add(HtmlElement.br())



        depth = self.kwargs.get("depth")
        if depth == None:
            depth = -1
        open_depth = self.kwargs.get("open_depth")
        if open_depth == None:
            open_depth = 0

        dynamic = self.kwargs.get("dynamic")
        if dynamic in ["true", True]:
            dynamic = True
        else:
            dynamic = False



        handler_class = Common.get_full_class_name(self)


        search_keys = self.kwargs.get("search_keys")
        if not search_keys:
            search_keys = []
        top.add_attr("spt_search_keys", "|".join(search_keys) )

        search_types = self.kwargs.get("search_types")
        if not search_types:
            search_types = []
        top.add_attr("spt_search_types", "|".join(search_types) )


        # This is the package that gets passed around
        core_handler_kwargs = {
            'base_dir': self.base_dir,
            'root_dir': self.root_dir,
            'search_types': self.kwargs.get("search_types"),
            'search_keys': self.kwargs.get("search_keys"),
        }
        if self.handler_kwargs:
            core_handler_kwargs.update(self.handler_kwargs)

        if dynamic:
            dir_list = DirListPathHandler(
                location=location,
                level=0,
                base_dir=self.base_dir,
                root_dir=self.root_dir,
                handler_class=handler_class,
                handler_kwargs=core_handler_kwargs,
                depth=depth,
                all_open=False,
                # Open depth is not really supported on dynamic mode yet
                #open_depth=open_depth,
                dynamic=dynamic,
            )
            top.add(dir_list)
        else:
            all_open = self.kwargs.get("all_open")
            if all_open in [True, 'true']:
                all_open = True
            else:
                all_open = False

            dir_list = DirListPathHandler(
                location=location,
                level=0,
                base_dir=self.base_dir,
                root_dir=self.root_dir,
                handler_kwargs=core_handler_kwargs,
                handler=self,
                handler_class=handler_class,
                depth=depth,
                all_open=all_open,
                open_depth=open_depth,
                paths=self.paths,
                dynamic=False,
            )
            top.add(dir_list)



        return top




    def add_load_behavior(self):
        pass




    def _get_dir_item(self, dir, item, is_open=False):

        div = DivWdg()
        div.add_class("hand")
        div.add_class("SPT_DTS")
        div.add_style("display: flex")
        div.add_style("margin-top: 2px")
        div.add_style("margin-bottom: 2px")
        div.add_style("height: 18px")
        div.add_style("padding-top: 2px")

        div.add_class("spt_item")
        div.add_class("spt_dir_item")
        div.add_attr("spt_dirname", dir)
        div.add_attr("spt_basename", item)

        path = "%s/%s" % (dir, item)
 
        # Dynamic loading of swap content
        dynamic = self.kwargs.get("dynamic")
        if dynamic in ["true", "True", True]:
            dynamic = True
        else:
            dynamic = False
 
        if dynamic:
            div.add_class("spt_dynamic")
        
        if is_open:
            div.add_class("spt_open")

        # Swap display will be set off when opened
        if dynamic:
            swap_open = False
        else:
            swap_open = is_open

        from pyasm.widget import SwapDisplayWdg
        swap = SwapDisplayWdg.get_triangle_wdg(is_open=swap_open)
        div.add(swap)

        swap.add_style("margin-right: -7px")
        swap.add_class("spt_dir_swap")
        swap.add_style("float: left")
 
        # FIXME: self.base_dir = dir
        reldir = dir.replace(self.base_dir, "")
        reldir = reldir.lstrip("/")
        if reldir:
            reldir = reldir + "/" + item
        else:
            reldir = item
        div.add_attr("spt_reldir", reldir)

        div.add_attr("spt_dir", path)
        div.add_attr("spt_root_dir", self.root_dir)

        


        class_path = Common.get_full_class_name(self)
        div.add_attr("spt_handler_class", class_path)
        div.add_attr("spt_level", self.level+1)

        swap_action = self.get_swap_action()
        swap.add_action_script(swap_action)


        # Open if is_open or it is the first folder
        if dynamic and (is_open or self.get_depth() == 0):
            swap.get_widget("div1").add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                bvr.src_el.click();
                '''
            } )



        background = self.kwargs.get("background")
        if not background:
            background = "background"
        hover = div.get_color(background, -5)
        div.add_color("background", background)
        div.add_event("onmouseover", "spt.mouse.table_layout_hover_over({}, {src_el: document.id(this), add_color_modifier: -5})" )
        div.add_event("onmouseout", "spt.mouse.table_layout_hover_out({}, {src_el: document.id(this)})")
     
 


        div.add_attr("spt_path", "%s/%s" % (dir, item) )
        self.add_dir_behaviors(div, dir, item)

        location = self.kwargs.get("location")
        if location == 'server':
            # to improve speed, skip collecting dir info for each sub dir
            info = Common.get_dir_info(path, skip_dir_details=True)
        elif location == 'scm':
            info = {}
        else:
            info = {}

        
        icon_div = self.get_dir_icon_wdg(dir, item)
        if not icon_div:
            if info.get("file_type") == 'missing':
                icon_string = IconWdg.DELETE
            else:
                icon_string = self.get_dir_icon(dir, item)

            icon_div = DivWdg()
            icon = IconWdg(path, icon_string)
            icon_div.add(icon)

        div.add(icon_div)
        icon_div.add_style("float: left")
        icon_div.add_style("margin-left: 3px")
        icon_div.add_style("margin-top: -1px")

        location = self.kwargs.get("location")
        if location in ['server', 'scm']:
            item_div = DivWdg()
            div.add(item_div)

            item_div.add_attr("spt_dirname", dir)
            item_div.add_attr("spt_basename", item)

            item_div.add_style("float: left")
            item_div.add_class("spt_dir")
            self.handle_dir_div(item_div, dir, item)
        else:
            div.add_class("spt_dir")
            self.handle_dir_div(div, dir, item)
       

        view_indicator = self.get_view_indicator(dir, item)
        if view_indicator:
            div.add(view_indicator)


        div.add("<br clear='all'/>")

        return div

    def get_view_indicator(self, dir, basename):
        '''Indicator used in tactic.ui.tools.RepoBrowserWdg'''
        return None

    def get_swap_action(self):
        return r'''
        var item_top = bvr.src_el.getParent(".spt_dir_item");
        var sibling = item_top.getNext(".spt_dir_content");

        if (item_top.hasClass("spt_dynamic")) {

            if (item_top.hasClass("spt_open")) {
                //spt.hide(sibling);
                var children = sibling.getChildren()
                for (var i = 0; i < children.length; i++) {
                    spt.behavior.destroy_element(children[i]);
                }
                item_top.removeClass("spt_open");
                sibling.setStyle("display", "none");
            }
            else {
                item_top.addClass("spt_open");
                sibling.setStyle("display", "");

                var base_dir = item_top.getAttribute("spt_dir");
                var root_dir = item_top.getAttribute("spt_root_dir");

                // get the search_keys, if any
                var top = bvr.src_el.getParent(".spt_dir_list_top");

                var search_keys = top.getAttribute("spt_search_keys");
                if (search_keys) {
                    search_keys = search_keys.split("|");
                }
                else {
                    search_keys = [];
                }

                var search_types = top.getAttribute("spt_search_types");
                if (search_types) {
                    search_types = search_types.split("|");
                }
                else {
                    search_types = [];
                }


                //FIXME: are these root_dir and base_dir are really needed in this handler_kwargs?
                var handler_kwargs = {
                        root_dir: root_dir,
                        base_dir: base_dir,
                        search_keys: search_keys,
                        search_types: search_types
                       
                    } 
                var extra_handler_kwargs = eval(%s);
                
                for (handler_kw in extra_handler_kwargs) {
                    if (extra_handler_kwargs.hasOwnProperty(handler_kw))
                        handler_kwargs[handler_kw] = extra_handler_kwargs[handler_kw];
                }
                var class_name = 'tactic.ui.widget.DirListPathHandler';
                var kwargs = {
                    level: item_top.getAttribute("spt_level"),
                    base_dir: base_dir,
                    depth: 1,
                    all_open: false,
                    dynamic: true,
                    handler_class: item_top.getAttribute("spt_handler_class"),
                    handler_kwargs: handler_kwargs

                };
               
                spt.panel.load(sibling, class_name, kwargs, {}, {show_loading: false});
            }
        }
        else {
            spt.toggle_show_hide(sibling);
        }


        var top = item_top.getParent(".spt_dir_list_top");
        var folder_state_el = top.getElement(".spt_folder_state");
        if (! folder_state_el) {
            return;
        }

        var reldir = item_top.getAttribute("spt_reldir");

        var folder_state = folder_state_el.value;

        var items;
        if (folder_state == '') {
            items = [];
        }
        else {
            items = folder_state.split("|");
        }

        //var index = items.indexOf(reldir);
        var exists = false;
        for (var i = 0; i < items.length; i++) {
            if (items[i] == reldir) {
                exists = true;
                break;
            }
        }
        if (exists) {
            items.splice(i, 1);
        }
        else {
            items.push(reldir);
        }

        folder_state = items.join("|");
        folder_state_el.value = folder_state;

        ''' % (jsondumps(self.handler_kwargs))

    def get_info(self, dirname, basename):
        location = self.kwargs.get("location")
        # get some info about the file
        path = "%s/%s" % (dirname, basename)
        if location == 'server':
            self.info = Common.get_dir_info(path)
        else:
            self.info = {}
        return self.info


    def _get_file_item(self, dirname, basename):

        item_div = DivWdg()
        item_div.add_class("spt_item")
        item_div.add_class("spt_file_item")
        item_div.add_attr("spt_path", "%s/%s" % (dirname, basename) )
        item_div.add_attr("spt_dirname", dirname)
        item_div.add_attr("spt_basename", basename)

        item_div.add_styles("margin-top: 2px; margin-bottom: 2px; padding-top: 2px; padding-bottom: 2px")

        left_padding = self.level*11+15
        item_div.add_style("padding-left: %spx" % left_padding)
        item_div.add_attr("spt_padding_left", left_padding)
        item_div.add_class("hand")

        item_div.add_style("display: flex")


        self.add_file_behaviors(item_div, dirname, basename)


        background = self.kwargs.get("background")
        if not background:
            background = "background"
        hover = item_div.get_color(background, -5)
        item_div.add_color("background", background)


        item_div.add_event("onmouseover", "spt.mouse.table_layout_hover_over({}, {src_el: document.id(this), add_color_modifier: -5})" )
        item_div.add_event("onmouseout", "spt.mouse.table_layout_hover_out({}, {src_el: document.id(this)})")
     
 

     
        # self.info is used in SnapshotDirLIstWdg also
        self.info = self.get_info(dirname, basename)
        location = self.kwargs.get("location")

        if location == 'xxxserver':
            # DEPRECATED
            icon_div = DivWdg()
            item_div.add(icon_div)
            icon = IconWdg("%s/%s" % (dirname, basename), icon_string)
            icon_div.add(icon)
            icon_div.add_style("float: left")
            icon_div.add_style("margin-top: -1px")

            # add the file name
            filename_div = DivWdg()
            item_div.add(filename_div)
            filename_div.add(basename)
            filename_div.add_style("float: left")
            filename_div.add_style("overflow: hidden")
            filename_div.add_style("margin-left: 5px")


            size = self.info.get('size')
            from pyasm.common import FormatValue
            size = FormatValue().get_format_value(size, 'KB')

            filesize_div = DivWdg()
            item_div.add(filesize_div)
            filesize_div.add(size)
            #filesize_div.add_style("width: 200px")
            filesize_div.add_style("text-align: right")
        else:
            item_div.add_class("spt_dir_list_item")
            self.handle_item_div(item_div, dirname, basename)
            #item_div.add("<br/>")

        return item_div


    def handle_dir_div(self, dir_div, dirname, basename):
        span = SpanWdg()
        span.add(self.get_dirname(dirname, basename))
        span.add_class("spt_value")
        span.add_class("spt_dir_value")
        span.add_style("margin-left: 5px")
        dir_div.add(span)


    def handle_item_div(self, item_div, dirname, basename):
 
        path = "%s/%s" % (dirname, basename)
        if self.info.get("file_type") == 'missing':
            icon_string = IconWdg.DELETE
            tip = 'Missing [%s]' %path
        elif self.info.get("file_type") == 'sequence':
            icon_string = "BS_FILM"
            tip = 'Sequence [%s]' %path
        else:
            icon_string = self.get_file_icon(dirname, basename)
            tip = path


        icon_div = DivWdg()
        item_div.add(icon_div)
        icon = IconWdg(tip, icon_string)
        icon_div.add(icon)
        icon_div.add_style("float: left")
        icon_div.add_style("margin-top: -1px")
        icon_div.add_style("margin-right: 5px")

        # add the file name
        filename_div = DivWdg()
        item_div.add(filename_div)
        filename_div.add(self.get_basename(dirname, basename) )
        filename_div.add_style("float: left")
        filename_div.add_style("overflow: hidden")
        filename_div.add_style("margin-left: 5px")
        filename_div.add_class("spt_item_value")


        #from pyasm.widget import CheckboxWdg, TextWdg
        #checkbox = CheckboxWdg("check")
        #checkbox.add_class("spt_select")
        #checkbox.add_style("float: right")
        #item_div.add(checkbox)


        view_indicator = self.get_view_indicator(dirname, basename)
        if view_indicator:
            item_div.add(view_indicator)


        item_div.add("<br clear='all'/>")


    def get_basename(self, dirname, basename):
        return basename


    def get_dirname(self, dirname, basename):
        return basename



    def add_top_behaviors(self, top):

        top.add_behavior( {
            'type': 'smart_click_up',
            'modkeys': 'SHIFT',
            'bvr_match_class': 'spt_dir_list_item',
            'cbjs_action': '''
            var el = bvr.src_el.getElement(".spt_select");
            if (!el) return;

            if (el.checked) {
                el.checked = false;
            }
            else {
                el.checked = true;
            }
            '''
        } )

        web = WebContainer.get_web()
        folder_state = web.get_form_value("folder_state")
        if not folder_state:
            folder_state = self.kwargs.get("folder_state")
        #text_wdg = TextWdg("folder_state")
        #text_wdg.add_style("width: 400px")
        text_wdg = HiddenWdg("folder_state")
        text_wdg.add_class("spt_folder_state")
        top.add(text_wdg)
        if folder_state:
            text_wdg.set_value(folder_state)




    def add_base_dir_behaviors(self, div, base_dir):

        pass
        """
        location = self.kwargs.get("location")
        if location == 'server':
            base_dir = Environment.get_client_repo_dir()

        div.add_class("hand")
        div.add_attr('title','Double click to open explorer')
        div.add_behavior( {
        'type': 'double_click',
        'base_dir': base_dir,
        'cbjs_action': '''
        var applet = spt.Applet.get();
        var path = bvr.base_dir;
        applet.open_explorer(path); 
        '''
        } )
        """



    def add_dir_behaviors(self, item_div, dir, item):

        location = self.kwargs.get("location")
        if location == 'server':
            base_dir = self.kwargs.get("base_dir")
            repo_dir = Environment.get_client_repo_dir()
            dir = dir.replace(base_dir,'')
            dir = repo_dir + dir

        """
        item_div.add_attr('title','Double click to open explorer')
        item_div.add_behavior( {
        'type': 'double_click',
        'dirname': dir,
        'basename': item,
        'cbjs_action': '''
        var applet = spt.Applet.get();
        var path = bvr.dirname + "/" + bvr.basename;
        applet.open_explorer(path); 
        '''
        } )
        """




    def add_file_behaviors(self, item_div, dir, item):
        location = self.kwargs.get("location")

        item_div.add_class("SPT_DTS")

        web = WebContainer.get_web()
        browser = web.get_browser()


        if location == 'server':
            # convert this to a repo directory
            asset_dir = Environment.get_asset_dir()

            # FIXME: not sure how general this
            webdirname = "/assets/%s" % dir.replace(asset_dir, "")

            if browser == 'Qtxx':       # DISABLING FOR NOW
                item_div.add_behavior( {
                'type': 'click_up',
                'webdirname': webdirname,
                'basename': item,
                'cbjs_action': '''
                spt.tab.set_main_body_tab()
                var class_name = 'tactic.ui.widget.EmbedWdg';
                var kwargs = {
                    src: bvr.webdirname + "/" + bvr.basename;
                }
                spt.tab.add_new("Embed", "Embed", class_name, kwargs);
                //window.open(bvr.webdirname + "/" + bvr.basename, '_blank');
                '''
                } )


            else:

                item_div.add_behavior( {
                'type': 'click_up',
                'webdirname': webdirname,
                'basename': item,
                'cbjs_action': '''
                window.open(bvr.webdirname + "/" + bvr.basename, '_blank');
                '''
                } )

        else:
            item_div.add_behavior( {
            'type': 'double_click',
            'dirname': dir,
            'basename': item,
            'cbjs_action': '''
            var applet = spt.Applet.get();
            var path = bvr.dirname + "/" + bvr.basename;
            if (applet) {
                spt.app_busy.show("Opening file", path);
                applet.open_file(path);
                spt.app_busy.hide();
            }
            '''
            } )

        return




    def get_file_icon_wdg(self, dirname, basename):
        return


    def get_dir_icon_wdg(self, dirname, basename):
        return 


    def get_file_icon(self, dir, item):
        return "FA_FILE"



    def get_dir_icon(self, dir, item):
        return "FA_FOLDER_OPEN"



__all__.append("DirListPathHandler")
class DirListPathHandler(BaseRefreshWdg):

    def get_display(self):
        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_dir_list_handler_top")

        inner = DivWdg(css="spt_dir_list_handler_content")
        top.add(inner)


        all_open = self.kwargs.get("all_open")
        if all_open in ["True", 'true']:
            all_open = True
        elif all_open in ["False", 'false']:
            all_open = False
        elif all_open == None:
            all_open = False


        self.level = self.kwargs.get("level")
        if not self.level:
            self.level = 0
        else:
            self.level = int(self.level)

        padding = self.level * 11
        top.add_style("padding-left: %spx" % padding)

        self.handler = self.kwargs.get("handler")
        if not self.handler or isinstance(self.handler, basestring):
            handler_class = self.kwargs.get("handler_class")
            handler_kwargs = self.kwargs.get("handler_kwargs")
            if not handler_kwargs:
                handler_kwargs = {}
            if isinstance(handler_kwargs, basestring):
                handler_kwargs = eval(handler_kwargs)

            handler_kwargs['location'] = self.kwargs.get("location")
            handler_kwargs['all_open'] = all_open
            handler_kwargs['depth'] = self.kwargs.get("depth")
            handler_kwargs['open_depth'] = self.kwargs.get("open_depth")
            #handler_kwargs['search_type'] = self.kwargs.get("search_type")
            handler_kwargs['dynamic'] = self.kwargs.get("dynamic")
            handler_kwargs['folder_state'] = self.kwargs.get("folder_state")
            
            self.handler = Common.create_from_class_path(handler_class, [], handler_kwargs)



        base_dir = self.kwargs.get("base_dir")
        assert(base_dir)

        self.paths = self.kwargs.get("paths")
        if isinstance(self.paths, basestring):
            self.paths = []
        if not self.paths: 
            self.paths = self.handler.get_relative_paths(base_dir)
        self.paths.sort()

        """
        paths = []
        for root, dirnames, basenames in os.walk(base_dir):
            for dirname in dirnames:
                path = "%s/%s/" % (root, dirname)
                paths.append(path)
            for basename in basenames:
                path = "%s/%s" % (root, basename)
                paths.append(path)

        paths.sort()
        """


        depth = self.kwargs.get("depth")
        if depth == None:
            depth = -1

        open_depth = self.kwargs.get("open_depth")
        if open_depth == None:
            open_depth = -1


        self.handle_paths(self.paths, base_dir, inner, depth=depth, all_open=all_open, open_depth=open_depth)

        if self.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top



    def handle_paths(self, paths, base_dir, div, depth=-1, all_open=False, open_depth=-1 ):
        '''assume path ending with / is a directory'''
        new_paths = []
        last_parts = []
        for path in paths:
            if not path.startswith("%s/" % base_dir):
                continue

            extra = path.replace("%s/" % base_dir, "")

            dirname = os.path.dirname(extra)
            # strip both ends
            dirname = dirname.strip("/")
            basename = os.path.basename(extra)

            if not dirname:
                parts = []
            else:
                parts = dirname.split("/")

                for i, part in enumerate(parts):

                    # skip any parts that are already accounted for
                    new_dir = base_dir + "/" + "/".join(parts[:i+1]) + "/"

                    # slow but it works
                    if new_dir in new_paths:
                        continue
                    
                    new_paths.append(new_dir)

            if basename:
                new_paths.append(path)

            last_parts = parts


        base_length = len( base_dir.split("/") )

        current_dir = base_dir
        level = 0


        # remember the levels
        level_divs = []
        level_divs.append(div)
        level_dirs = []


        count = 0
        self.file_count = 0

        self.max_level = depth
        for path in new_paths:

            level = len(path.rstrip("/").split("/")) - base_length - 1

            if self.max_level != -1 and level > self.max_level:
                continue

            # put an artificial maximum
            if self.max_level == -1:
                count += 1
                if count > 1000:
                    print("Hitting maximum of 1000 entries")
                    break



            # set the current level
            self.level = level
            self.handler.level = level


            # check if this is a directory, which ends in a /
            if path.endswith("/"):
                dirname = os.path.dirname(path.rstrip("/"))
                basename = os.path.basename(path.rstrip("/"))

                #print(" "*level, level, path, basename)

                # FIXME: hard coded
                if basename == '.versions':
                    xis_open = False
                else:

                    web = WebContainer.get_web()
                    folder_state = web.get_form_value("folder_state")
                    if not folder_state:
                        folder_state = self.kwargs.get("folder_state")
                    if folder_state:
                        folder_state = folder_state.split("|")
                    else:
                        folder_state = []
                    
                    rel_dir = path.replace(base_dir + "/", "").rstrip("/")
                    
                    # The repo_browser stores dir in folder_state relative to
                    # asset_base_dir.
                    asset_base_dir = Environment.get_asset_dir()
                    rel_dir2 = path.replace("%s/" % asset_base_dir, "").rstrip("/")

                    if not folder_state:
                        if open_depth != -1 and level < open_depth:
                            xis_open = True
                        else:
                            xis_open = all_open
                    elif rel_dir in folder_state:
                        xis_open = True
                    elif rel_dir2 in folder_state:
                        xis_open = True
                    else:
                        xis_open = False
                    
                # get the level_div and add the directory to it
                level_divs = level_divs[:level+1]
                # put some protection here so that there is minimum level
                if not level_divs:
                    level_divs = [div]
                level_div = level_divs[-1]

                dir_item_div = self.handler._get_dir_item(dirname, basename, is_open=xis_open)
                if dir_item_div:
                    dir_item_div.add_style("padding-left: %spx" % ((level)*11))
                    level_div.add( dir_item_div )

                    # create a new items div
                    items_div = DivWdg()
                    items_div.add_class("spt_dir_content")
                    level_div.add( items_div )
                    level_divs.append(items_div)

                    if not xis_open:
                        items_div.add_style("display: none")

                current_dir = path

            else:

                dirname = os.path.dirname(path)
                # windows server needs this since os.path.dirname() is different in windows
                dirname = dirname.rstrip("/")
                dirname = dirname.rstrip("\\")
                basename = os.path.basename(path)

                xpath = path.replace(current_dir, "")

                # get the level_div and add the directory to it
                level_divs = level_divs[:level+1]

                if not level_divs:
                    level_div = div
                else:
                    level_div = level_divs[-1]

                level_div.add( self.handler._get_file_item(dirname, basename))

                self.file_count += 1






class DirInfoWdg(BaseRefreshWdg):
    def get_display(self):
        dirname = self.kwargs.get("dirname")

        top = DivWdg()

        is_local = self.kwargs.get("is_local")
        if is_local in [True, 'true']:
            is_local = True
        else:
            is_local = False



        top.add("Folder: %s<br/>" % dirname)
        if not is_local and not os.path.exists(dirname):
            top.add("<br/>Does not exist - Please refresh")
            return top

        size = self.kwargs.get("size")
        count = self.kwargs.get("count")


        if not size:
            info = Common.get_dir_info(dirname)
            size = info.get('size')
            size = float(size)
            count = info.get('count')

        size = float(size)

        # adjust for size
        if size > 1024*1024*1024:
            top.add("Size: %0.1f GB<br/>" % (size/(1024*1024*1024)) )
        elif size > 1024*1024:
            top.add("Size: %0.1f MB<br/>" % (size/(1024*1024)) )
        elif size > 1024:
            top.add("Size: %0.1f KB<br/>" % (size/1024) )
        else:
            top.add("Size: %d B<br/>" % size )


        top.add("Count: %d files<br/>" % count )

        # map server dirs to client dirs
        dirmaps = Config.get_value("checkin", "client_dir_map")
        if dirmaps:
            dirmaps = jsonloads(dirmaps)
        else:
            dirmaps = {}

        # get some directories
        top.add("<br/>" )

        client_dir = None
        for a, b in dirmaps.items():
            if dirname.startswith(b):
                client_dir = dirname.replace(b, a)
                break

        if not client_dir:
            top.add("Cannot map server directory to client")
            return top


        top.add("Folder from Client: %s" % client_dir)
        explore = ProdIconButtonWdg("Explore")
        explore.add_behavior( {
        'type': 'click_up',
        'client_dir': client_dir,
        'cbjs_action': '''
            var applet = spt.Applet.get();
            if (applet)
                applet.open_explorer(bvr.client_dir);
        '''
        } )
        top.add(explore)

        return top


class FileInfoWdg(BaseRefreshWdg):
    def get_display(self):

        dirname = self.kwargs.get("dirname")
        basename = self.kwargs.get("basename")

        path = "%s/%s" % (dirname, basename)


        search = Search('sthpw/file')
        search.add_filter("file_name", basename)
        search.add_filter("checkin_dir", dirname)

        search2 = Search('sthpw/snapshot')
        search2.add_relationship_search_filter(search)
        snapshots = search2.get_sobjects()

        top = DivWdg()

        top.add("File: %s<br/>" % path)
        info = Common.get_dir_info(path)
        size = info.get('size')

        top.add("Size: %s bytes<br/>" % size )

        #if not snapshots:
        #    top.add("<br/><br/>No Corresponding Snapshot Found")
        #else:
        #    from tactic.ui.panel import TableLayoutWdg
        #    table = TableLayoutWdg(search_type="sthpw/snapshot", view='table', mode='simple')
        #    table.set_sobjects(snapshots)
        #    top.add(table)

        return top


class SObjectSearchWdg(BaseRefreshWdg):
    def get_display(self):
        search_types = self.kwargs.get("search_types")
        if isinstance(search_types, basestring):
            search_types = eval(search_types)
        if not search_types:
            project_type = Project.get().get_value("type")
            search_types = Search.eval("@GET(sthpw/search_object['namespace','%s'].search_type)" % project_type)

        top = DivWdg()
        top.add_class("spt_search_top")
        self.set_as_panel(top)

        web = WebContainer.get_web()

        search_div = DivWdg()
        search_div.add_class("spt_search_filter");

        select = SelectWdg("search_type")
        select.set_persistence()
        select.set_option("values", search_types)
        select.add_empty_option("-- Select --")
        select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_search_top");
        spt.panel.refresh(top);
        '''
        } )

        #search_type = web.get_form_value("search_type")
        search_type = select.get_value()

        top.add("<br/>")
        top.add(SpanWdg("Ingest to Search Type: "))
        top.add(select)
        top.add(search_div)

        table = Table()
        table.add_style("margin-left: 15px")
        table.add_style("padding: 5px")
        table.add_border()
        table.add_color("color", "color")
        table.add_color("background", "background", -5)
        table.add_style("margin: 10px")
        swap = SwapDisplayWdg()
        title = SpanWdg('Checkin Options:')

        SwapDisplayWdg.create_swap_title(SpanWdg('Options:'), swap, table, is_open=False)
        search_div.add("<br/>")
        search_div.add(swap)
        search_div.add(title)
        search_div.add(HtmlElement.br())
        search_div.add(table)
        
        tr = table.add_row()
        td = table.add_cell("Transfer Mode: ")

        td.add_style("padding-bottom: 5px")
        select = SelectWdg("transfer_mode")
        select.set_persistence()
        select.set_option("values", "free_copy|free_move|inplace")
        select.set_option("labels", "Copy|Move|In Place")
        td = table.add_cell(select)
        td.add_style("padding-bottom: 5px")
        td.add_style("width: 300px")
        
        tr = table.add_row()
        td = table.add_cell("Checkin as: ")
        td.add_style("padding-bottom: 5px")
        select = SelectWdg("checkin_mode")
        select.set_persistence()
        select.set_option("values", "default|file|file_group")
        select.set_option("labels", "Best Guess|Files in Directory|Files Group")
        td = table.add_cell(select)
        td.add_style("padding-bottom: 5px")
        td.add_style("width: 300px")

        tr = table.add_row()
        td = table.add_cell("Context: ")
        td.add_style("padding-bottom: 5px")
        text = TextWdg("context")
        text.set_value("publish")
        td = table.add_cell(text)
        td.add_style("padding-bottom: 5px")

        tr = table.add_row()
        td = table.add_cell("Subcontext: ")
        td.add_style("padding-bottom: 5px")

        select = SelectWdg("subcontext_mode")
        select.add_style("float: left")
        #TODO: make {leaf} unavailable when Files Group or Files in Folder is chosen
        select.set_option("values", "{none}|{leaf}|{folder}|{custom}")
        select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
            var value = bvr.src_el.value;
            var td = bvr.src_el.getParent(".spt_subcontext_td");
            var text = td.getElement(".spt_subcontext");
            if (value == '{custom}') {
                text.setStyle("display", "");
            }
            else {
                text.setStyle("display", "none");
            }
        '''
        } )
        td = table.add_cell(select)
        td.add_class("spt_subcontext_td")
        td.add_style("padding-bottom: 5px")

        subcontext_div = DivWdg()
        subcontext_div.add_class("spt_subcontext")
        subcontext_div.add_style("display: none")
        td.add(subcontext_div)
        text = TextWdg("subcontext")
        subcontext_div.add("&nbsp; => value: ")
        subcontext_div.add(text)

        tr = table.add_row()
        td = table.add_row_cell("(use subcontext to differentiate between multiple drop items for each sobject)")


        if not search_type:
            return top

        view = 'ingest'
        element_names = ['preview', 'code', 'folder_drop', 'history']

        from tactic.ui.panel import ViewPanelWdg
        #from tactic.ui.panel import TableLayoutWdg

        # try this mechanism
        save_inputs = "spt_search_top/spt_search_filter"

        # or try it inline to gather data manually
        #cbjs_get_inputs_cbk = '''
        #    var input_parent = bvr.src_el.getParent(".spt_search_top");
        #    var input_wdg = input_parent.getElement(".spt_search_filter");
        #    var input_data = spt.api.get_input_values(input_wdg);
        #    return input_data;
        #'''

        table_div = DivWdg()
        top.add(table_div)

        # check if the view exists first, do not hardcode element_names if it does
        config = WidgetDbConfig.get_by_search_type(search_type, view)
        if config:
            element_names=[]
        table = ViewPanelWdg(search_type=search_type, view=view, element_names=element_names, show_gear='false', save_inputs=save_inputs)
        table_div.add(table)

        return top



__all__.append("FileIngestCmd")
class FileIngestCmd(DatabaseAction):

    def execute(self):

        dirs_str = self.get_value()
        if dirs_str:
            dirs = jsonloads(dirs_str)
        else:
            dirs = []

        if not dirs:
            return


        # autoname code
        if not self.sobject.get_value("code"):
            basename = os.path.basename(dirs[0])
            self.sobject.set_value("code", basename)
            self.sobject.commit()


    def postprocess(self):

        web = WebContainer.get_web()
        self.kwargs = jsonloads( web.get_form_value("input_data") )
        transfer_mode = self.kwargs.get("transfer_mode")
        if transfer_mode:
            transfer_mode = transfer_mode[0]
        else:
            trasfer_mode = 'free_copy'
        
        checkin_mode = self.kwargs.get("checkin_mode")
        if checkin_mode:
            checkin_mode = checkin_mode[0]
        else:
            checkin_mode = "default"

        context = self.kwargs.get("context")
        if context:
            context = context[0]
        if not context:
            context = "publish"


        subcontext_mode = self.kwargs.get("subcontext_mode")
        if subcontext_mode:
            subcontext_mode = subcontext_mode[0]
        if not subcontext_mode:
            subcontext_mode = "{none}"


        subcontext = self.kwargs.get("subcontext")
        if subcontext:
            subcontext = subcontext[0]
        else:
            subcontext = ""


        dirs_str = self.get_value()
        if dirs_str:
            dirs = jsonloads(dirs_str)
        else:
            dirs = []

        if not dirs:
            return




        #print("tran_mode: ", transfer_mode)
        #print("checkin_mode: ", checkin_mode)
        #print("dir: ", dirs)
        #print("context: ", context)
        #print("subcontext_mode: ", subcontext_mode)
        #print("subcontext: ", subcontext)

        # checkin all the files in the folder
        if checkin_mode == 'file':
            for dir in dirs:
                paths = []
                #file_types = []
                for (path, subdirs, files) in os.walk(unicode(dir)):

                    # analyze the files
                    files.sort()
                    pattern = None
                    for file in files:
                        if not pattern:
                            pattern = file
                            #print(pattern, file)
                    
                    for file in files:
                        paths.append( "%s/%s" % (path, file))
                        #file_types.append('main')

                paths.sort()

        else:
            paths = dirs

        if checkin_mode in ['file_group','file']:
           self.file_group_checkin(paths, context, subcontext_mode, subcontext, transfer_mode)
        else:
           self.default_checkin(paths, context, subcontext_mode, subcontext, transfer_mode)

    def file_group_checkin(self, paths, context, subcontext_mode, subcontext, transfer_mode):
        '''having multiple files in one single check-in'''
        from pyasm.checkin import FileCheckin
        if subcontext_mode == '{leaf}':
            print("WARNING: {leaf} mode is not supported in file group checkin!")
        if subcontext_mode == '{folder}':
            tmp = path.replace("/", "_")
            checkin_context = "%s/%s" % (context, tmp)

        elif subcontext:
            checkin_context = "%s/%s" % (context, subcontext)
        elif context:
            checkin_context = context
        else:
            checkin_context = path.replace("/", "_")
        file_types = []
        for idx, path in enumerate(paths):
            file_types.append('ingest%s'%idx)
        
        checkin = FileCheckin(self.sobject, paths, context=checkin_context, mode=transfer_mode,\
              file_types=file_types, description='Ingest Files as group  check-in [%s]'% self.sobject.get_code())
        checkin.execute()
       
        for path in paths:   
            basedir = path
            if not os.path.isdir(basedir):
                basedir = os.path.dirname(path)

            # attempt to remove the directory if it is empty
            try:
                os.removedirs(basedir)
            except:
                pass



	
            
    def default_checkin(self, paths, context, subcontext_mode, subcontext, transfer_mode):

        from pyasm.checkin import FileCheckin

        # if no subcontext was specified, then for now, check in everything to
        # the same checkin

        if subcontext_mode == '{none}':
            snapshot_type = "file"
            checkin_context = context

            # use extension as a file type
            file_types = []
            for path in paths:
                base, ext = os.path.splitext(path)
                ext = ext.replace(".", "")
                file_types.append(ext)

            checkin = FileCheckin(self.sobject, paths, context=checkin_context, mode=transfer_mode, file_types=file_types, snapshot_type=snapshot_type, description='Ingest check-in [%s]'% self.sobject.get_code())
            checkin.execute()

            return


        # otherwise checkin according to the subcontext rules
        for path in paths:
            if subcontext_mode == '{leaf}':
                leaf = os.path.basename(path)
                checkin_context = "%s/%s" % (context, leaf)
            elif subcontext_mode == '{folder}':
                tmp = path.replace("/", "_")
                checkin_context = "%s/%s" % (context, tmp)
            elif subcontext:
                checkin_context = "%s/%s" % (context, subcontext)
            elif context:
                checkin_context = context
            else:
                checkin_context = path.replace("/", "_")

            snapshot_type = "file"
            if os.path.isdir(path):
                snapshot_type = "dir"
            checkin = FileCheckin(self.sobject, path, context=checkin_context, mode=transfer_mode, file_types=['main'], snapshot_type=snapshot_type, description='Ingest check-in [%s]'% self.sobject.get_code())
            checkin.execute()

            basedir = path
            if not os.path.isdir(basedir):
                basedir = os.path.dirname(path)

            # attempt to remove the directory if it is empty
            try:
                os.removedirs(basedir)
            except:
                pass


        return

        """
        snapshot_codes = []

        search = Search("sthpw/snapshot")
        search.add_filters("code", snapshot_codes)
        snapshots = search.get_sobjects()

        sobject = None

        # associate the snapshot
        for snapshot in snapshots:
            snapshot.set_parent(sobject)
            snapshot.commit()
        """







# DEPRECATED
__all__.append("IngestWdg")
class IngestWdg(BaseRefreshWdg):
    def get_display(self):
        top = DivWdg()
        top.add_class("spt_ingest_top")
        self.set_as_panel(top)


        text = TextWdg("dir")
        top.add(text)


        browse = ProdIconButtonWdg("Load")
        browse.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_ingest_top");
        spt.panel.refresh(top);
        '''
        } )
        

        top.add(browse)

        icon = ProdIconButtonWdg("Ingest")
        top.add(icon)

        icon.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.app_busy.show("Ingesting ...", "This may take a while ....");
        var top = bvr.src_el.getParent(".spt_ingest_top");
        var values = spt.api.Utility.get_input_values(top, null, false);
        var server = TacticServerStub.get();
        var class_name = 'tactic.ui.widget.file_browser_wdg.IngestCmd';
        server.execute_cmd(class_name, values);
        spt.app_busy.hide();
        '''
        } )


        info_div = DivWdg()
        info_div.add_border()
        info_div.add_style("padding: 20px")

        import os
        dir = "/home/apache/assets"

        if os.path.exists(dir):

            dir_size = 0
            for (path, dirs, files) in os.walk(unicode(dir)):
                for file in files:
                    filename = os.path.join(path, file)
                    dir_size += os.path.getsize(filename)
            
            info_div.add( "Importing: %s<br/><br/>" % dir) 
            info_div.add( "Folder = %0.1f MB" % (dir_size/(1000*1000.0)) )
            top.add(info_div)
                
        else:
            div = DivWdg("Folder does not exist")
            top.add(div)
            div.add("margin: 15px 5px")

        return top





from pyasm.common import Environment
from pyasm.biz import Project
from pyasm.search import Search


__all__.append("IngestCmd")
class IngestCmd(Command):

    def execute(self):
        dir = self.kwargs.get("dir")
        assert dir

        #dir = "/home/apache/tactic_plugin"
        #dir = "/home/apache/python"
        print("dir: ", dir)

        items = os.listdir(dir)
        for item in items:
            path = "%s/%s" % (dir, item)
            self.handle_path(path)


    def handle_path(self, path):
        path = str(path)
        if os.path.isdir(path):
            items = os.listdir(path)
            for item in items:
                sub_path = "%s/%s" % (path, item)
                self.handle_path(sub_path)
        else:
            print("path: ", path)
            self.checkin_file(path)



    def checkin_file(self, path):

        context = 'ingest'
        version = 1
        file_type = 'main'

        from pyasm.search import SearchType
        from pyasm.checkin import SnapshotBuilder
        import os

        basename = os.path.basename(path)
        dirname = os.path.dirname(path)

        file = SearchType.create("sthpw/file")
        file.set_value("checkin_dir", dirname)
        file.set_value("file_name", basename)
        file.set_value("relative_dir", dirname)
        file.set_value("type", file_type)

        file.set_value("search_type", "sthpw/virtual")
        file.set_value("search_id", "0")
        file.commit()

        # create the snapshot
        snapshot = SearchType.create("sthpw/snapshot")
        snapshot.set_value("context", context)
        snapshot.set_value("version", version)
        snapshot.set_value("login", Environment.get_user_name() )

        # dummy values 
        snapshot.set_value("search_type", "sthpw/virtual")
        snapshot.set_value("search_id", "0")
        snapshot.set_value("column_name", "snapshot")

        builder = SnapshotBuilder()
        builder.add_file(file, info={'file_type':file_type})
        xml_string = builder.to_string()
        #print(xml_string)
        snapshot.set_value("snapshot", xml_string)
        snapshot.commit()

        # set the snapshot code
        snapshot_code = snapshot.get_value("code")
        file.set_value("snapshot_code", snapshot_code)
        file.commit() 



# DEPRECATED:
# This is really the IngestionTool
__all__.append("FileBrowserWdg")
class FileBrowserWdg(BaseRefreshWdg):

    def get_display(self):

        self.level = 0 
        self.max_level = 4


        top = DivWdg()
        top.add_class("spt_file_top")
        self.set_as_panel(top)




        # get the directory
        web = WebContainer.get_web()
        base_dir = web.get_form_value("base_dir")
        if not base_dir:
            base_dir = self.kwargs.get("base_dir")
        location = web.get_form_value("location")
        if not location:
            location = self.kwargs.get("location")

       
        table = Table()
        #from tactic.ui.container import ResizableTableWdg
        #table = ResizableTableWdg()
        table.add_color("background", "background")
        table.add_color("color", "color")
        table.add_row()
        td = table.add_cell()
        td.add_style("padding: 10px")
        td.add_border()
        td.add_attr("colspan", "2")


        refresh = SingleButtonWdg(title="Refresh", icon=IconWdg.REFRESH)
        refresh.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_file_top");
            spt.panel.refresh(top);
            '''
        } )
        refresh.add_style("float: right")
        td.add(refresh)


        nav_wdg = DivWdg()
        td.add(nav_wdg)
        nav_wdg.add_style("margin-bottom: 10px")
        nav_wdg.add_class("spt_file_nav")
        nav_wdg.add_style("width: 575px")

        button = ActionButtonWdg(title="Search", tip="Search for files in specified folder")
        #button = ProdIconButtonWdg("Search")
        button.add_style("float: right")
        button.add_style("margin-top: -5px")
        nav_wdg.add(button)

        title_wdg = "Base folder on server to search: "
        nav_wdg.add(title_wdg)

        from tactic.ui.input import TextInputWdg
        text = TextInputWdg(name="base_dir")
        text.add_class("spt_base_dir")
        text.add_style("width: 300px")
        if base_dir:
            text.set_value(base_dir)
        nav_wdg.add(text)

        # add a hidden paths variable
        text = HiddenWdg("paths")
        text.add_class("spt_paths")
        nav_wdg.add(text)

        nav_wdg.add("<br/>")

        # add a hidden paths variable
        select = SelectWdg("location")
        if location:
            select.set_value(location)
        nav_wdg.add("Folder is ")
        nav_wdg.add(select)
        select.set_option("values", "local|server")

        
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''

        var top = bvr.src_el.getParent(".spt_file_top");
        var nav = top.getElement(".spt_file_nav");

        var nav_values = spt.api.Utility.get_input_values(nav,null,false);

        var base_dir = nav_values.base_dir;
        var location = nav_values.location;

        spt.app_busy.show("Scanning", base_dir);

        if (location == 'local') {
            var applet = spt.Applet.get();
            if (applet) {
                var paths = applet.list_dir(base_dir, 2);
                var paths_el = nav.getElement(".spt_paths");
                var js_paths = [];
                for (var i = 0; i < paths.length; i++) {
                    var js_path = paths[i].replace(/\\\\/g,"/");
                    if (applet.is_dir(js_path) ) {
                        js_path = js_path + '/';
                        js_paths.push(js_path);
                    }
                    //if (i > 100) break;
                }

                paths_el.value = js_paths.join("|");
            }
        }

        var nav_values = spt.api.Utility.get_input_values(nav,null,false);
        spt.panel.refresh(top, nav_values);
        spt.app_busy.hide();
        '''
        } )

        table.add_style("min-height: 400px")
        
        table.add_row()
        td = table.add_cell()

        #td.add_class("spt_file_content")
        td.add_class("spt_dir_info")
        td.add_style("min-width: 400px")
        td.add_style("vertical-align: top")
        td.add_style("height: 100px")
        td.add_border()
        td.add_style("padding: 10px")
        td.add_color("background", "background", -5)
        title = DivWdg()

        title.add("<b>Info:</b><br/><br/>&nbsp;&nbsp;&nbsp;<i>Select a file or folder. Drag it into Folder drop column on the right.</i>")
        td.add(title)

        td = table.add_cell()
        td.set_attr("rowspan","2")
        td.add_class("spt_file_content")
        td.add_style("min-width: 500px")
        td.add_style("min-height: 400px")
        td.add_border()
        td.add_style("padding: 10px")
        
        search_type_objs = Project.get().get_search_types()
        search_types = [str(x.get_value("search_type")) for x in search_type_objs]
        from tactic.ui.tools.ingestion_wdg import IngestionToolWdg

        # FIXME: hard coding!!!
        content = IngestionToolWdg(session_code='session101')
        td.add(content)
        #content = SObjectSearchWdg(search_types=search_types)
        #td.add(content)
        td.add_style("vertical-align: top")


        top.add(table)
        table.add_row()
        td = table.add_cell()
        td.add_border()
        td.add_style("padding: 10px")
        td.add_style("width: 200px")
        td.add_style("min-height: 400px")
        td.add_style("vertical-align: top")

        web = WebContainer.get_web()
        paths = web.get_form_value("paths")
        if not paths:
            paths = self.kwargs.get("paths")
        if paths:
            paths = paths.split("|");
        if not paths:
            paths = []

        dir_wdg = DirListWdg(base_dir=base_dir, location=location, paths=paths)
        td.add(dir_wdg)
        td.add("<hr/")


        #td = table.add_blank_cell()
        td = table.add_cell("&nbsp;")
        # this ensures the UI doesn't jump up and down when the table
        # has like 1-20 objects returned
        td.add_style('height: 800px')

        return top



