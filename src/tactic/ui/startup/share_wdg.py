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

__all__ = ['ShareWdg', 'LocalItemWdg', 'ShareItemWdg', 'ShareItemCbk']

from pyasm.common import Environment, Common, Config
from pyasm.search import Search
from pyasm.biz import Project
from pyasm.command import Command
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg, TextWdg, TextAreaWdg

import os, shutil

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg, SingleButtonWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.app import SearchWdg
from tactic.ui.panel import ViewPanelWdg
from tactic.ui.container import SmartMenu, Menu, MenuItem


class ShareWdg(BaseRefreshWdg):
    '''This is the welcome widget widget will appear on creation of a new
    project
    '''

    def get_args_keys(my):
        return {
        }



    def get_display(my):

        top = my.top
        top.add_class("spt_share_top")
        my.set_as_panel(top)

        top.add_color("background", "background")

        title = DivWdg()
        top.add(title)
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        #title.add_style("margin: -10px -10px 10px -10px")

        title.add_gradient("background", "background3", 5, -10)

        title.add("Share Project")



        # add the main layout
        #table = ResizableTableWdg()
        table = Table()
        table.add_color("color", "color")
        top.add(table)

        table.add_row()
        left = table.add_cell()
        left.add_border()
        left.add_style("vertical-align: top")
        left.add_style("min-width: 250px")
        left.add_style("height: 400px")
        left.add_color("background", "background3")

        left.add(my.get_share_wdg() )

        right = table.add_cell()
        right.add_border()
        right.add_style("vertical-align: top")
        right.add_style("min-width: 400px")
        right.add_style("width: 100%")
        right.add_style("height: 400px")
        right.add_style("padding: 5px")

        right.add_class("spt_share_content")


        share_item_wdg = ShareItemWdg()
        right.add(share_item_wdg)


        return top



    def get_share_wdg(my):

        div = DivWdg()
        div.add_style("padding: 20px")


        msg = '''<p>Before starting to work on a project that you are sharing, you should import the starting point.</p>'''
        div.add(msg)


        button = ActionButtonWdg(title="Import")
        div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.sync.SyncImportWdg';

            var top = bvr.src_el.getParent(".spt_share_top");
            var content = top.getElement(".spt_share_content");
            spt.panel.load(content, class_name);
            //spt.panel.load_popup("Sync Import", class_name);
            '''
        } )




        msg = '''<p>This allows you to create a share for this project.  This will allow you to share this project with others.</p>'''
        div.add(msg)


        button = ActionButtonWdg(title="Share")
        div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.sync.SyncServerAddWdg';
            spt.panel.load_popup("Sync Share", class_name);
            '''
        } )




        title_wdg = DivWdg()
        div.add( title_wdg )
        title_wdg.add( "Local" )
        title_wdg.add_style("padding: 5px")
        title_wdg.add_color("background", "background", -10)
        title_wdg.add_border()
        title_wdg.add_style("margin: 5px -22px 10px -22px")


        local_code = Config.get_value("install", "server") or ""
        local_div = DivWdg()
        div.add(local_div)
        local_div.add_class("spt_share_item")
        local_div.add_attr("spt_server_code", local_code)
        local_div.add_class("hand")
        local_div.add(local_code)

        local_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.startup.LocalItemWdg';

            var top = bvr.src_el.getParent(".spt_share_top");
            var content = top.getElement(".spt_share_content");
            spt.panel.load(content, class_name);
            //spt.panel.load_popup("Sync Import", class_name);
            '''
        } )






        div.add("<br/>")




        search = Search("sthpw/sync_server")
        shares = search.get_sobjects()

        title_wdg = DivWdg()
        div.add( title_wdg )
        title_wdg.add( "Share List" )
        title_wdg.add_style("padding: 5px")
        title_wdg.add_color("background", "background", -10)
        title_wdg.add_border()
        title_wdg.add_style("margin: 5px -22px 10px -22px")





        shares_div = DivWdg()
        div.add(shares_div)

        shares_div.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_share_item',
            'cbjs_action': '''
            var server_code = bvr.src_el.getAttribute("spt_server_code");
            var class_name = 'tactic.ui.startup.ShareItemWdg';
            var kwargs = {
                server_code: server_code
            }
            var top = bvr.src_el.getParent(".spt_share_top");
            var content = top.getElement(".spt_share_content");
            spt.panel.load(content, class_name, kwargs);
            '''
        } )


        bgcolor = shares_div.get_color("background", -5)
        shares_div.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_share_item',
            'bgcolor': bgcolor,
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.bgcolor);
            '''
        } )
        shares_div.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_share_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )


        from pyasm.security import AccessManager
        access_manager = AccessManager()
        project = Project.get()
        project_code = project.get_code()



        # add in a context menu
        menu = my.get_context_menu()
        menus = [menu.get_data()]
        menus_in = {
            'SHARE_ITEM_CTX': menus,
        }
        SmartMenu.attach_smart_context_menu( shares_div, menus_in, False )



        count = 0
        for share in shares:

            # hide the shares that are not in this project
            rules = share.get_value("access_rules");
            access_manager.add_xml_rules(rules)

            key1 = { 'code': project_code }
            key2 = { 'code': '*' }
            keys = [key1, key2]
            if not access_manager.check_access("project", keys, "allow", default="deny"):
                continue
  

            share_div = DivWdg()
            shares_div.add(share_div)
            share_div.add_class("spt_share_item")
            share_div.add_attr("spt_server_code", share.get_code())
            share_div.add_class("hand")

            share_div.add(share.get_code())
            share_div.add_attr("title", share.get_value("description") )
            share_div.add_style("padding: 5px")

            base_dir = share.get_value("base_dir")
            if base_dir:
                base_div = SpanWdg()
                share_div.add(base_div)
                base_div.add_style("font-size: 0.9em")
                base_div.add_style("font-style: italic")
                base_div.add_style("opacity: 0.5")
                base_div.add(" (%s)" % base_dir)


            share_div.add_attr("spt_share_code", share.get_code() )
            SmartMenu.assign_as_local_activator( share_div, 'SHARE_ITEM_CTX' )

            count += 1


        if not count:
            share_div = DivWdg()
            shares_div.add(share_div)

            share_div.add("<i>No shares</i>")
            share_div.add_style("padding: 5px")


        return div



    def get_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Remove Share')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
            if (!confirm("Delete share?") ) {
                return;
            }

            var activator = spt.smenu.get_activator(bvr);
            var code = activator.getAttribute("spt_share_code");

            var class_name = 'tactic.ui.startup.ShareItemCbk';
            var kwargs = {
                'action': 'delete',
                'code': code
            };
            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);
            
            var top = activator.getParent(".spt_share_top");
            spt.panel.refresh(top);

            '''
        })
        return menu
 

class LocalItemWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        my.set_as_panel(top)



        title_wdg = DivWdg()
        top.add( title_wdg )
        title_wdg.add( "Local" )
        title_wdg.add_style("padding: 10px")
        title_wdg.add_color("background", "background", -10)
        title_wdg.add_border()
        title_wdg.add_style("margin: -6px -6px 10px -6px")
        title_wdg.add_style("font-weight: bold")



        from tactic.ui.container import TabWdg
        tab = TabWdg(selected="Info", show_add=False)
        top.add(tab)
        tab.add(my.get_info_wdg())

        return top


    def get_info_wdg(my):

        div = DivWdg()
        div.set_name("Info")
        div.add_style("padding: 20px")

        
        table = Table()
        div.add(table)
        table.add_color("color", "color")
        #table.add_style("height: 280px")
        table.set_unique_id()

        table.add_smart_style("spt_table_header", "width", "200px")
        table.add_smart_style("spt_table_header", "text-align", "right")
        table.add_smart_style("spt_table_header", "padding-right", "20px")
        table.add_smart_style("spt_table_header", "margin-bottom", "10px")
        table.add_smart_style("spt_table_element", "vertical-align", "top")

        table.add_row()

        #if my.mode == 'insert':
        #    read_only = False
        #else:
        #    read_only = True
        read_only = False

        code = Config.get_value("install", "server") or ""

        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Code: ")
        td.add_style("vertical-align: top")
        text = TextInputWdg(name="code", read_only=read_only)
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(code)

        return div



class ShareItemWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_share_item")

        my.server_code = my.kwargs.get("server_code")
        if not my.server_code:
            top.add("No server selected")
            return top



        my.server = Search.get_by_code("sthpw/sync_server", my.server_code)
        my.base_dir = my.server.get_value("base_dir")


        title_wdg = DivWdg()
        top.add( title_wdg )
        title_wdg.add( my.server_code )
        title_wdg.add_style("padding: 10px")
        title_wdg.add_color("background", "background", -10)
        title_wdg.add_border()
        title_wdg.add_style("margin: -6px -6px 10px -6px")
        title_wdg.add_style("font-weight: bold")

        description = my.server.get_value("description")
        title_wdg.add(" &nbsp; <i style='font-size: 9px; opacity: 0.5'>( %s )</i>" % description )




        from tactic.ui.container import TabWdg
        tab = TabWdg(selected="Info", show_add=False)
        top.add(tab)
        tab.add(my.get_info_wdg())
        tab.add(my.get_files_wdg())

        tab.add( my.get_tools_wdg() )

        return top



    def get_info_wdg(my):

        div = DivWdg()
        div.set_name("Info")
        div.add_style("padding: 20px")

        
        table = Table()
        div.add(table)
        table.add_color("color", "color")
        #table.add_style("height: 280px")
        table.set_unique_id()

        table.add_smart_style("spt_table_header", "width", "200px")
        table.add_smart_style("spt_table_header", "text-align", "right")
        table.add_smart_style("spt_table_header", "padding-right", "20px")
        table.add_smart_style("spt_table_header", "margin-bottom", "10px")
        table.add_smart_style("spt_table_element", "vertical-align", "top")


        #if my.mode == 'insert':
        #    read_only = False
        #else:
        #    read_only = True
        read_only = False

        code = my.server.get_code() or ""
        description = my.server.get_value("description") or ""

        table.add_row()

        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Code: ")
        td.add_style("vertical-align: top")
        text = TextInputWdg(name="code", read_only=read_only)
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(code)

        table.add_row()
        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Description: ")
        td.add_style("vertical-align: top")
        text = TextAreaWdg(name="description", read_only=read_only)
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(description)

        table.add_row()
        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Base Directory: ")
        td.add_style("vertical-align: top")
        text = TextInputWdg(name="base_dir", read_only=read_only)
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(my.base_dir)



        return div



    def get_files_wdg(my):

        div = DivWdg()
        div.set_name("Files")
        div.add_style("padding: 10px")


        shelf_wdg = DivWdg()
        div.add(shelf_wdg)
        shelf_wdg.add_style("height: 25px")
        shelf_wdg.add_style("padding: 5px")
        shelf_wdg.add_border()
        shelf_wdg.add_color("background", "background3")
        shelf_wdg.add_style("margin: 0px -11px 10px -11px")

        project_code = Project.get_project_code()
        share_code = my.server.get_code()

        # NOT supported yet
        base_dir = my.server.get_value("base_dir")
        imports_dir = "%s/imports" % base_dir
        #import datetime
        #now = datetime.datetime.now()
        #version = now.strftime("%Y%m%d_%H%M%S")

        
        button = ActionButtonWdg(title="Export")
        shelf_wdg.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'project_code': project_code,
            'share_code': share_code,
            'imports_dir': imports_dir,
            'cbjs_action': '''

            var class_name = 'tactic.ui.sync.SyncCreateTemplateCmd'
            var kwargs = {
                server: bvr.share_code,
                project_code: bvr.project_code,
                base_dir: bvr.imports_dir,
            }

            spt.app_busy.show("Exporting project ...");
            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

            var top = bvr.src_el.getParent(".spt_share_item");
            spt.panel.refresh(top);
            spt.app_busy.hide();

            '''
        })


        from tactic.ui.app import PluginDirListWdg
        dir_list = PluginDirListWdg(base_dir=my.base_dir, location="server")
        #from tactic.ui.widget import DirListWdg
        #dir_list = DirListWdg(base_dir=my.base_dir, location="server")
        div.add(dir_list)



        return div



    def get_tools_wdg(my):

        div = DivWdg()
        div.set_name("Tools")
        div.add_style("padding: 10px")

        div.add("This tool will export out a version of the project")

        button = ActionButtonWdg(title="Export")
        div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'server': my.server_code,
            'cbjs_action': '''
            var class_name = 'tactic.ui.sync.SyncCreateTemplateCmd';
            var kwargs = {
                server: bvr.server
            }
            spt.app_busy.show("Exporting project ...");
            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);
            spt.app_busy.hide();

            spt.panel.refresh(bvr.src_el);

            '''
        } )



        return div




class ShareItemCbk(Command):

    def execute(my):

        action = my.kwargs.get("action")
        if action == "delete":
            my.delete()


    def delete(my):

        code = my.kwargs.get("code")
        assert code

        server = Search.get_by_code("sthpw/sync_server", code)
        print server.get_data()

        base_dir = server.get_value("base_dir")

        server.delete()

        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)





