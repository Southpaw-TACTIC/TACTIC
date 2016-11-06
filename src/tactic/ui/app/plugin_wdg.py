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

__all__ = ['PluginWdg', 'PluginEditWdg', 'PluginInstallWdg', 'PluginDownloadCbk', 'PluginDirListActionCbk', 'PluginRemoveCbk', 'PluginDirListWdg']

from pyasm.common import Environment, TacticException, Config, Xml, Common, ZipUtil
from pyasm.command import Command
from pyasm.web import DivWdg, Table, HtmlElement
from pyasm.widget import ButtonWdg, ProdIconButtonWdg, TextWdg, TextAreaWdg, CheckboxWdg, IconWdg, SelectWdg
from pyasm.search import Search, SearchType
from pyasm.biz import File

import os, codecs
import zipfile, shutil

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg
from tactic.ui.widget import ActionButtonWdg, DirListWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu
from tactic.ui.widget import ButtonRowWdg, ButtonNewWdg

class PluginWdg(BaseRefreshWdg):


    def get_display(my):

        div = DivWdg()
        div.add_class("spt_plugin_top")
        my.set_as_panel(div)

        div.add_color("background", "background")

        inner = DivWdg()
        div.add(inner)


        # add the main layout
        #table = ResizableTableWdg()
        table = Table()
        table.add_color("color", "color")
        inner.add(table)
        table.add_style("margin: -1")

        table.add_row()
        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("min-width: 275px")
        left.add_style("height: 400px")
        left.add_style("padding: 0px")
        left.add_color("background", "background3")
        left.add_border()

        plugin_dir = Environment.get_plugin_dir()
        plugin_wdg = my.get_plugins_wdg("Plugin", plugin_dir)
        left.add(plugin_wdg)

        builtin_plugin_dir = Environment.get_builtin_plugin_dir()
        plugin_wdg = my.get_plugins_wdg("Built-in Plugin", builtin_plugin_dir, is_editable=False)
        if plugin_wdg:
            left.add(plugin_wdg)



        #left.add("<br/>")
        #template_dir = Environment.get_template_dir()
        #left.add(my.get_plugins_wdg("Template", template_dir) )

        right = table.add_cell()
        right.add_style("vertical-align: top")
        right.add_style("min-width: 400px")
        right.add_style("width: 100%")
        right.add_style("height: 400px")
        right.add_style("padding: 5px")
        right.add_border()

        plugin_dir = my.kwargs.get("plugin_dir")
        edit = PluginEditWdg(plugin_dir=plugin_dir)
        right.add(edit)

        if my.kwargs.get("is_refresh"):
            return inner
        else:
            return div



    def get_plugins_wdg(my, title, plugin_dir, is_editable=True):
        div = DivWdg()



        # use the file system
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)

        dirnames = os.listdir(plugin_dir)
        dirnames.sort()
        dirnames.reverse()
        plugin_dirnames = []
        for dirname in dirnames:
            if dirname.endswith(".zip"):
                continue
            if dirname.endswith(".enc"):
                continue
            if not os.path.isdir("%s/%s" % (plugin_dir, dirname)):
                continue
            #if not os.path.exists("%s/%s/manifest.xml" % (plugin_dir, dirname)):
            #    continue

            plugin_dirnames.append(dirname)


        # get all of the active plugins in this project
        search_type = 'config/plugin'
        search = Search(search_type)
        active_plugins = search.get_sobjects()
        active_codes = [x.get_code() for x in active_plugins]
        active_versions = [x.get_value("version") for x in active_plugins]
        active_map = {}
        for x in active_plugins:
            active_map[x.get_code()] = x.get_value("version") 

        title_div = DivWdg()
        div.add(title_div)
        title_div.add("%s List" % title)
        title_div.add_style("font-size: 14px")
        title_div.add_style("font-weight: bold")
        title_div.add_gradient("background", "background", 0, -10)
        title_div.add_style("padding: 10px 5px 10px 5px")
        title_div.add_style("margin-bottom: 15px")



 
        button_row = ButtonRowWdg()
        title_div.add(button_row)
        button_row.add_style("float: right")
        button_row.add_style("margin-top: -8px")


       

        if is_editable:
            new_button = ButtonNewWdg(title="Create a New Plugin", icon=IconWdg.NEW)

            button_row.add(new_button)
            new_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_plugin_top");
            var edit = top.getElement(".spt_plugin_edit");
            var class_name = "tactic.ui.app.PluginEditWdg";
            var kwargs = {
                mode: 'insert'
            };
            spt.panel.load(edit, class_name, kwargs);
            '''
            } )



            add_button = ButtonNewWdg(title="Install a Plugin", icon=IconWdg.ADD)
            button_row.add(add_button)

            add_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_plugin_top");
            var edit = top.getElement(".spt_plugin_edit");
            var class_name = "tactic.ui.app.PluginInstallWdg";
            var kwargs = {
              search_key: bvr.search_key
            };
            spt.panel.load(edit, class_name, kwargs);
            '''
            } )


           # add in a context menu
            menu = my.get_context_menu()
            menus = [menu.get_data()]
            menus_in = {
                'PLUGIN_CTX': menus,
            }
            SmartMenu.attach_smart_context_menu( div, menus_in, False )



     
            help_button = ButtonNewWdg(title="Show Plugin Manger Help", icon=IconWdg.HELP)
            
            button_row.add(help_button)
            help_button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.help.set_top();
                spt.help.load_alias("plugin-manager-interface|tactic-developer_developer_plugin-manager-interface");
                '''
            } )






        base_dir = plugin_dir

        plugin_div_dict = {}
        last_title = ""
        folder_wdgs = {}
        folder_wdgs['/'] = div
        folder_states = {}

        content_div = DivWdg()
        div.add_widget(content_div, "content")
        content_div.add_style("margin-left: 3px")
        content_div.add_style("margin-bottom: 10px")

        plugin_dirnames = my.get_plugin_list(base_dir)


        if not plugin_dirnames:
            content_div.add("No plugins installed")
            content_div.add_style("padding: 5px 5px 5px 10px")
            content_div.add_style("font-style: italic")

        show_active_only = my.kwargs.get("show_active_only") 
        if show_active_only in [True, 'true']: 
            show_active_only = True 
        else: 
            show_active_only = False 
      
        for dirname in plugin_dirnames:

            parts = dirname.split("/")
            folder = parts[:-1]
            folder = "/".join(folder)
            if not folder:
                folder = "/"

            folder_wdg = folder_wdgs.get(folder)
            if folder_wdg:
                folder_content = folder_wdg.get_widget("content")
            else:
                parts = folder.split("/")
                # need to find the leaf folder, creating on the way, if
                # necessary
                parent_wdg = folder_wdgs.get("/")
                for i in range(1, len(parts)+1):

                    # find the folder, if it exists
                    folder = "/".join(parts[0:i])
                    folder_wdg = folder_wdgs.get(folder)

                    if folder_wdg:
                        parent_wdg = folder_wdg
                        continue

                    title = parts[i-1]

                    # else create a new one
                    folder_wdg = DivWdg()
                    if i != 1:
                        folder_wdg.add_style("padding-left: 13px")

                    # add it to the parent and remember this as the last parent
                    parent_wdg.get_widget("content").add(folder_wdg)
                    parent_wdg = folder_wdg

                    # add it to the list
                    folder_wdgs[folder] = folder_wdg

                    # remember it as the parent
                    parent_wdg = folder_wdg

                    # fill it in
                    icon = IconWdg(folder, IconWdg.FOLDER, inline=False)
                    icon.add_style("margin-top: -2px")
                    icon.add_style("margin-left: -2px")

                    folder_header = DivWdg()
                    folder_content = DivWdg()
                    folder_content.add_style("margin-left: 13px")


                    from tactic.ui.widget import SwapDisplayWdg
                    swap = SwapDisplayWdg()
                    folder_wdg.add(swap)
                    swap.set_title_wdg(folder_header)
                    folder_wdg.add_widget(folder_content, "content")
                    swap.add_class("spt_folder")
                    swap.add_attr("spt_folder", folder)

                    if folder_states.get(folder) == "open":
                        is_on = True
                    else:
                        is_on = False

                    swap.set_on(is_on)
                    if not is_on:
                        folder_content.add_style("display: none")


                    unique_id = folder_content.set_unique_id("content")
                    swap.set_content_id(unique_id)

                    folder_header.add(icon)
                    folder_header.add(title)
                    folder_header.add_style("margin-top: 3px")
                    folder_header.add_style("margin-bottom: 3px")
                    if folder == "-- no folder --":
                        folder_header.add_style("opacity: 0.5")
                        folder_header.add_style("font-style: italic")
                    else:
                        SmartMenu.assign_as_local_activator( folder_header, 'DIR_LAYOUT_CTX' )
                        folder_header.add_attr("spt_folder", folder)




            # find the manifest file
            plugin_dir = "%s/%s" % (base_dir, dirname)
            manifest_path = "%s/manifest.xml" % (plugin_dir)
            if not os.path.exists(manifest_path):
                invalid = True
            else:
                invalid = False
                

            if invalid:
                data = {}
            else:
                manifest = Xml()
                try:
                    manifest.read_file(manifest_path)
                except Exception, e:
                    print "Error reading manifest: [%s]" % manifest_path, e
                    msg = "Error reading manifest [%s]: %s" % (manifest_path, str(e))

                    manifest_xml = """
                    <manifest>
                    <data>
                      <title>ERROR (%s)</title>
                      <description>%s</description>
                    </data>
                    </manifest>
                    """ % (dirname, msg)
                    manifest.read_string(manifest_xml)


                node = manifest.get_node("manifest/data")
                data = manifest.get_node_values_of_children(node)

                # create a plugin sobject (not committed)
                #plugin = SearchType.create("sthpw/plugin")
                #plugin.set_value("description", data.get("description") or "")
                #plugin.set_value("title", data.get("title") or "")
                #plugin.set_value("code", data.get("code") or "")
                #plugin.set_value("version", data.get("version") or "" )


            title = data.get("title") or ""
            description = data.get("description") or "N/A"
            code = data.get("code") or ""
            version = data.get("version") or ""


            plugin_div = DivWdg()
            #div.add(plugin_div)
            folder_content.add(plugin_div)

            plugin_div.add_style("padding: 5px")
            plugin_div.add_class("hand")

            SmartMenu.assign_as_local_activator( plugin_div, 'PLUGIN_CTX' )
            plugin_div.add_attr("spt_plugin_dirname", dirname)

           
            active_version = active_map.get(code)

            is_active = version == active_version
         

            icon = DivWdg()
            icon.add_style("width: 9px")
            icon.add("&nbsp;")
            icon.add_style("float: left")
            plugin_div.add(icon)

            if is_active:
                icon = IconWdg("Active in project", IconWdg.CHECK)

                if show_active_only: 
                    swap.set_on(True) 
                    folder_content.add_style("display", "") 
                    #folder_header.add_style("display: none") 
                    folder_header.add_style("opacity: 0.3") 
            else:
                icon = IconWdg("Not Active in project", IconWdg.DELETE)
                icon.add_style("opacity: 0.2")

                if show_active_only: 
                    plugin_div.add_style("display: none") 
                    folder_header.add_style("opacity: 0.3") 

            icon.add_style("margin-right: -3px")

            plugin_div.add_attr("title", description)

            if invalid:
                plugin_div.add("<i style='opacity: 0.5; color: red'>%s</i>" % dirname)

            elif not title:
                if code:
                    title = Common.get_display_title(code)
                    plugin_div.add(icon)
                    plugin_div.add("%s" % title)

                else:
                    title = dirname
                    plugin_div.add(icon)
                    plugin_div.add("N/A <i>(%s)</i>" % title)
            else:
                plugin_div.add(icon)
                if title == last_title:

                    plugin_div_dict[title] = plugin_div
                    plugin_div.add(title, "TITLE")
                else:
                    plugin_div.add(title)
                  
      
            if not invalid:
                if version:
                    version_str = '''<span style="opacity: 0.5; font-style: italic; font-size: 10px"> (v%s)</span>''' % version
                else:
                    version_str = '''<span style="opacity: 0.5; font-style: italic; font-size: 10px"> (DEV)</span>'''
                plugin_div.add(version_str)

            
            last_title = title
           
            plugin_div.add_behavior( {
            'type': 'click_up',
            'plugin_dir': plugin_dir,
            'dirname': dirname,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_plugin_top");
            var edit = top.getElement(".spt_plugin_edit");
            var class_name = "tactic.ui.app.PluginEditWdg";
            var kwargs = {
              plugin_dir: bvr.plugin_dir,
              dirname: bvr.dirname
            };
            spt.panel.load(edit, class_name, kwargs);
            '''
            } )

            hover = plugin_div.get_color("background", -5)
            plugin_div.add_behavior( {
            'type': 'hover',
            'hover': hover,
            'cbjs_action_over': '''
            bvr.src_el.setStyle("background", bvr.hover);
            ''',
            'cbjs_action_out': '''
            bvr.src_el.setStyle("background", '');
            '''
            } )


        # bold the last version of each duplicated title
        for dup_title, special_div in plugin_div_dict.items():
            title_wdg = HtmlElement.b(dup_title)
            special_div.add(title_wdg, "TITLE")


        return div



    def get_plugin_list(my, base_dir):

        plugin_dirnames = []

        for root, dirnames, filenames in os.walk(base_dir, followlinks=True):

            if '.svn' in dirnames:
                dirnames.remove('.svn')

            root = root.replace("\\", "/")

            # filter out the dirnames
            if root.endswith(".zip"):
                del dirnames[:]
                continue
            if root.endswith(".enc"):
                del dirnames[:]
                continue


            if os.path.exists("%s/manifest.xml" % root):
                del dirnames[:]
                reldir = root.replace(base_dir+"/", "")
              
                if reldir.startswith('TACTIC/internal/'):
                    continue
                plugin_dirnames.append( reldir )

        plugin_dirnames.sort()
        return plugin_dirnames 




    def get_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Delete Plugin')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var view = activator.getAttribute("spt_view");

            spt.api.app_busy_show("Removing plugin ["+bvr.code+"]");

            var dirname = activator.getAttribute("spt_plugin_dirname");

            if (!confirm("Uninstall plugin '"+dirname+"'?")) {
                spt.api.app_busy_hide();
                return;
            }

            var kwargs = {
                dirname: dirname
            }

            var class_name = 'tactic.ui.app.PluginRemoveCbk';

            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

            spt.notify.show_message("Plugin '" + dirname + "' uninstalled.");

            var top = activator.getParent(".spt_plugin_top");
            //top.setStyle("border", "solid 5px blue");
            spt.panel.refresh(top);

            spt.api.app_busy_hide();

        ''' } )

        return menu



class PluginEditWdg(BaseRefreshWdg):
    
    def get_display(my):

        my.is_active_flag = None

        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_plugin_edit")

        top.add_style("min-width: 600px")

        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add_style("font-size: 14px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("margin: -5 -5 10px -5")
        title_wdg.add_style("padding: 10px 15px 10px 15px")
        title_wdg.add_gradient("background", "background", 0, -10)

        my.mode = my.kwargs.get("mode")
        if my.mode != 'insert':

            my.plugin_dir = my.kwargs.get("plugin_dir")
            if my.plugin_dir:
                manifest_path ="%s/manifest.xml" % (my.plugin_dir)

            else:
                msg = DivWdg()
                msg.add("No Plugin Selected")
                msg.add_border()
                msg.add_color("background", "background3")
                msg.add_style("padding", "30px 50px 30px 50px")
                msg.add_style("margin", "100px auto")
                msg.add_style("text-align: center")
                msg.add_style("width: 300px")

                top.add(msg)
                return top



            #top.add("<br/>")

            manifest = Xml()
            manifest.read_file(manifest_path)
            node = manifest.get_node("manifest/data")
            data = manifest.get_node_values_of_children(node)

            plugin = None

            my.code = data.get("code") or ""
            description = data.get("description") or ""
            my.version = data.get("version") or ""
            title = data.get("title") or ""
            manifest = manifest.to_string()

            if not my.version:
                title_wdg.add('''Plugin "%s" <i style='opacity: 0.5'>(DEV)</i>''' % title)
            else:
                title_wdg.add('Plugin "%s" <i>%s</i>' % (title, my.version))

        else:
            my.plugin_dir = ""

            my.code = ''
            description = ''
            my.version = ''
            title = ''
            manifest = ''

            plugin = None

            title_wdg.add("Create New Plugin")

        from tactic.ui.container import TabWdg

        selected = my.kwargs.get("selected")
        if not selected:
            selected = "info"

        tab = TabWdg(selected=selected, show_add=False, show_remove=False, allow_drag=False, tab_offset="10px")
        top.add(tab)
        tab.add_style("margin: 0px -6px 0px -6px")

        info_div = DivWdg()
        tab.add(info_div)
        if my.mode != "insert":
            action_wdg = my.get_action_wdg()
            info_div.add(action_wdg)
        info_div.add_color("background", "background")
        info_div.set_name("info")
        info_div.add_style("height: 50px")
        info_div.add_style("margin: 0px 20px 10px 20px")

        if my.mode == "insert":
            info_div.add("<br/>"*2)
            info_div.add("Enter the following data and press 'Create' to create a new plugin")
            info_div.add("<br/>"*2)


        table = Table()
        info_div.add(table)
        table.add_color("color", "color")
        table.add_style("height: 320px")
        table.set_unique_id()

        table.add_smart_style("spt_table_header", "width", "200px")
        table.add_smart_style("spt_table_header", "text-align", "right")
        table.add_smart_style("spt_table_header", "padding-right", "20px")
        table.add_smart_style("spt_table_header", "margin-bottom", "10px")
        table.add_smart_style("spt_table_header", "vertical-align", "top")
        table.add_smart_style("spt_table_element", "vertical-align", "top")


        #if my.mode == 'insert':
        #    read_only = False
        #else:
        #    read_only = True
        read_only = False


        table.add_row()
        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Title: ")
        text = TextInputWdg(name="title", read_only=read_only)
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(title)
        text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var code_el = top.getElement(".spt_plugin_code");
            var value = bvr.src_el.value;

            var code = spt.convert_to_alpha_numeric(value);
            code_el.value = code;
            '''
        } )




        table.add_row()
        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Code: ")
        text = TextInputWdg(name="code", read_only=read_only)
        text.add_class("spt_plugin_code")
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(my.code)


        tr = table.add_row()
        if my.mode == 'insert':
            tr.add_style("display: none")
        td = table.add_cell()
        td.add_class('spt_table_header')
        td.add("Version: ")

        td.add_style("vertical-align: top")
        #text = TextInputWdg(name="version", read_only=read_only)
        text = TextInputWdg(name="version", read_only=False)
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        if not my.version:
            text.set_value("DEV")
        else:
            text.set_value(my.version)


        table.add_row()
        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Description: ")
        text = TextAreaWdg("description")
        text.set_option("read_only", read_only)
        text.add_style("height", "150px")
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(description)



        if my.mode == 'insert':
            table.add_row()
            td = table.add_cell()
            td.add_class("spt_table_header")
            td.add("<br/>")
            td.add("Plugin Type: ")
            select = SelectWdg("plugin_template")
            select.set_option("labels", "Project|Theme|Widget|Column")
            select.set_option("values", "project|theme|widget|column")
            select.add_empty_option("--  --")
            td = table.add_cell()
            td.add("<br/>")
            td.add_class("spt_table_element")
            td.add(select)
            td.add("<br/>"*2)





        if my.mode == 'insert':
            table.add_row()
            td = table.add_cell()
            insert_wdg = my.get_insert_wdg()
            td.add(insert_wdg)
        else:
            # add the Publish button at the bottom
            button = ActionButtonWdg(title='Publish', tip='Publish new version')
            button.add_style("float: right")
            button.add_behavior( {
            'type': 'click_up', 
            'from_version': my.version,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");
            var values = spt.api.get_input_values(top, null, false);

            var manifest = values.manifest;
            if (!manifest || manifest == "") {
                manifest = "<manifest/>";
            }

            var code = values.code;
            var version = values.version;
            if (version == 'DEV') {
                spt.alert("Cannot publish DEV version. Please change the version.");
                return;
            }
            if (version.match(/^v/i)) {
                spt.alert("We recommend Version not starting with a V.")
                return;
            }


            // PluginCreator handles version as well
            var exec = function() {
                var class_name = 'tactic.command.PluginCreator';
                var kwargs = {
                    code: code,
                    version: version,
                    from_version: bvr.from_version
                }

                var server = TacticServerStub.get();
                try {
                    server.execute_cmd(class_name, kwargs);
                } catch(e) {
                    spt.alert(spt.exception.handler(e));
                    spt.api.app_busy_hide();
                    return;
                }


                var top = bvr.src_el.getParent(".spt_plugin_top");
                spt.panel.refresh(top);
            }
            exec();
            spt.notify.show_message('Plugin [' + code + '] v' + version+ ' created.');
            
            '''
            } )
            table.add_row()
            td = table.add_cell(button)
    
        dirname = my.kwargs.get('dirname')
        if not dirname:
            plugin_base_dir = Environment.get_plugin_dir()
            builtin_plugin_base_dir = Environment.get_builtin_plugin_dir()
            if my.plugin_dir.startswith(plugin_base_dir):
                dirname = my.plugin_dir.replace(plugin_base_dir + "/", "")
            else:
                dirname = my.plugin_dir.replace(builtin_plugin_base_dir + "/", "")
            

        my.dirname = dirname

        
           
        #
        # Doc
        #
        if my.plugin_dir:
            tab.add( my.get_doc_wdg() )


        if my.mode != 'insert':
            tab.add( my.get_manifest_wdg(manifest) )

        #
        # Files
        #
        dir_div = DivWdg()
        tab.add(dir_div)
        dir_div.set_name("files")
        dir_div.add_style("padding: 5px 15px 15px 15px")


        if my.mode != 'insert':

            title_wdg = DivWdg()
            dir_div.add(title_wdg)
            title_wdg.add_color("background", "background3")
            title_wdg.add_style("margin: -5 -16 15 -16")
            title_wdg.add_style("padding: 5px")
            title_wdg.add_style("height: 40px")
            title_wdg.add_border()

            button_row = ButtonRowWdg()
            title_wdg.add(button_row)
            button_row.add_style("float: left")


            button = ButtonNewWdg(title="Refresh", icon=IconWdg.REFRESH)
            button_row.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_plugin_edit");
                top.setAttribute("spt_selected", "files");
                spt.panel.refresh(top);

                '''
            } )




            button = ButtonNewWdg(title="New File", icon=IconWdg.ADD)
            button_row.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'dirname': dirname, 
                'cbjs_action': '''
                // create a new file
                var class_name = 'tactic.ui.app.PluginDirListActionCbk';
                var kwargs = {
                    'action': 'new_file',
                    'dirname': bvr.dirname
                }
                var server = TacticServerStub.get();
                try {
                    server.execute_cmd(class_name, kwargs);
                } catch(e) {
                    spt.alert(spt.exception.handler(e));
                }
                var top = bvr.src_el.getParent(".spt_plugin_edit");
                top.setAttribute("spt_selected", "files");
                spt.panel.refresh(top)

                '''
            } )


            button = ButtonNewWdg(title="New Folder", icon=IconWdg.FOLDER)
            button_row.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'dirname': dirname, 
                'cbjs_action': '''
                // create a new folder
                var class_name = 'tactic.ui.app.PluginDirListActionCbk';
                var kwargs = {
                    'action': 'new_folder',
                    'dirname': bvr.dirname
                }
                var server = TacticServerStub.get();
                try {
                    server.execute_cmd(class_name, kwargs);
                } catch(e) {
                    spt.alert(spt.exception.handler(e));
                }

                var top = bvr.src_el.getParent(".spt_plugin_edit");
                top.setAttribute("spt_selected", "files");
                spt.panel.refresh(top)

                '''
            } )

            from tactic.ui.input import UploadButtonWdg
            upload_button = UploadButtonWdg(name="Upload")
            upload_button.add_style('float: left')
            title_wdg.add(upload_button)
            title_wdg.add(HtmlElement.br(2))

            upload_button.set_on_complete('''
                var file = spt.html5upload.get_file();
                if (!file) {
                   alert('Error: file cannot be found.')
                   spt.app_busy.hide();
                   return;
                }

                var file_name = file.name;

                var server = TacticServerStub.get();

                var kwargs = spt.html5upload.kwargs;


                var class_name = 'tactic.ui.app.PluginDirListActionCbk';
                var kwargs = {
                    'action': 'upload',
                    'upload_file_name': file_name,
                    'dirname': kwargs.dirname

                }
                try {
                    server.execute_cmd(class_name, kwargs);
                    spt.notify.show_message(file_name + "added to plugin.");
                } catch(e) {
                    spt.alert(spt.exception.handler(e));
                }

                var top = bvr.src_el.getParent(".spt_plugin_edit");
                top.setAttribute("spt_selected", "files");
                spt.panel.refresh(top);

                spt.app_busy.hide();

                ''',
                dirname=dirname
            )




            dir_div.add_color("background", "background")
            dir_list = PluginDirListWdg(base_dir=my.plugin_dir, location="server", plugin_dirname=dirname, ignore=['.svn'])
            dir_div.add(dir_list)

        else:
            msg = DivWdg()
            msg.add("No Files in Plugin")
            msg.add_border()
            msg.add_color("background", "background3")
            msg.add_style("padding", "30px 50px 30px 50px")
            msg.add_style("margin", "100px auto")
            msg.add_style("text-align: center")
            msg.add_style("width: 300px")
            dir_div.add(msg)


        return top


    def get_manifest_wdg(my, manifest):

        #
        # Manifest
        #

        dirname = my.dirname


        manifest_div = DivWdg()

        shelf_wdg = DivWdg()
        manifest_div.add(shelf_wdg)
        shelf_wdg.add_style("height: 40px")
        shelf_wdg.add_style("padding: 5px 10px")
        shelf_wdg.add_color("background", "background3")


        if my.is_active():

            """
            clear_button = ActionButtonWdg(title="Clear .spt")
            shelf_wdg.add(clear_button)
            clear_button.add_style("float: left")
            clear_button.add_behavior( {
                'type': 'click_up',
                'dirname': dirname,
                'cbjs_action': '''
                var class_name = 'tactic.ui.app.PluginDirListActionCbk';
                var kwargs = {
                    'action': 'clear_spt',
                    'dirname': bvr.dirname
                };
                var server = TacticServerStub.get();
                server.execute_cmd(class_name, kwargs);
                '''
            } )
            """




            button = ActionButtonWdg(title='Export', tip='Export .spt Files')
            shelf_wdg.add(button)
            button.add_style("float: left")
            button.add_behavior( {
            'type': 'click_up', 
            'dirname': dirname,
            'cbjs_action': '''

            spt.api.app_busy_show("Clearing all .spt files");

            var class_name = 'tactic.ui.app.PluginDirListActionCbk';
            var kwargs = {
                'action': 'clear_spt',
                'dirname': bvr.dirname
            };
            var server = TacticServerStub.get();

            try {
                server.execute_cmd(class_name, kwargs);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
                return;
            }

            spt.api.app_busy_show("Exporting Plugin");


            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");

            var values = spt.api.get_input_values(top, null, false);

            var manifest = values.manifest;
            if (!manifest || manifest == "") {
                manifest = "<manifest/>";
            }

            var code = values.code;
            var version = values.version;
            if (version == 'DEV') {
                version = '';
            }
            var description = values.description;
            var title = values.title;

            var plugin_template = values.plugin_template;

            var server = TacticServerStub.get();

            var class_name;
            if (plugin_template == "Project") {
                class_name = 'tactic.command.ProjectTemplateCreatorCmd';
            }
            else {
                class_name = 'tactic.command.PluginCreator';
            }

            
            var kwargs = {
                clean: false,
                code: code,
                version: version,
                title: title,
                description: description,
                manifest: manifest,
                plugin_template: plugin_template
            };
             
            try {
                server.execute_cmd(class_name, kwargs);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
                spt.api.app_busy_hide();
                return;
            }

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            top.setAttribute("spt_selected", "manifest");
            spt.panel.refresh(top);

            spt.api.app_busy_hide();

            '''
            })



            button = ActionButtonWdg(title='Publish', tip='Publish new version')
            shelf_wdg.add(button)
            button.add_style("float: left")
            button.add_behavior( {
            'type': 'click_up', 
            'from_version': my.version,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");
            var values = spt.api.get_input_values(top, null, false);

            var manifest = values.manifest;
            if (!manifest || manifest == "") {
                manifest = "<manifest/>";
            }

            var code = values.code;
            var version = values.version;
            if (version == 'DEV') {
                spt.alert("Cannot publish DEV version. Please change the version.");
                return;
            }


            // PluginCreator handles version as well
            var exec = function() {
                var class_name = 'tactic.command.PluginCreator';

                var kwargs = {
                    code: code,
                    version: version,
                    from_version: bvr.from_version
                }

                var server = TacticServerStub.get();
                try {
                    server.execute_cmd(class_name, kwargs);
                } catch(e) {
                    spt.alert(spt.exception.handler(e));
                    spt.api.app_busy_hide();
                    return;
                }


                var top = bvr.src_el.getParent(".spt_plugin_top");
                spt.panel.refresh(top);
            }
            exec();
            spt.notify.show_message('Plugin [' + code + '] v' + version+ ' created.');

            
            '''
            } )


        else:
            button = ActionButtonWdg(title='Clean', tip='Clean up project for this plugin')
            shelf_wdg.add(button)
            button.add_style("margin: 10px auto")
            button.add_behavior( {
            'type': 'click_up', 
            'plugin_code': my.code,
            'cbjs_action': '''
            spt.api.app_busy_show("Removing Plugin");

            if (!confirm("WARNING: This will clean up entries associated with this plugin manifest: ["+bvr.plugin_code+"]?")) {
                spt.api.app_busy_hide();
                return;
            }

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");
            var values = spt.api.get_input_values(top, null, false);

            var manifest = values.manifest;


            var class_name = 'tactic.command.PluginUninstaller';
            var kwargs = {
                manifest: manifest
            };

            var server = TacticServerStub.get();

            try {
                server.execute_cmd(class_name, kwargs);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }

            var top = bvr.src_el.getParent(".spt_plugin_top");
            spt.panel.refresh(top);

            spt.api.app_busy_hide();

            '''
            })




        manifest_div.set_name("manifest")

        text = TextAreaWdg("manifest")
        text.add_style("width: 100%")
        text.add_style("min-height: 400px")
        text.add_style("font-size: 12px")
        manifest_div.add(text)
        text.set_value(manifest)


        return manifest_div


    def get_doc_wdg(my):

        # documentation for the plugin
        doc_path = "%s/doc.html" % my.plugin_dir
        #dirname = os.path.basename(my.plugin_dir)

        if my.dirname.startswith("TACTIC"):
            rel_path = "/builtin_plugins/%s/doc.html" % my.dirname
        else:
            rel_path = "/plugins/%s/doc.html" % my.dirname
        
        if os.path.exists(doc_path):
            doc_div = DivWdg()

            dirname = os.path.dirname(doc_path)
            basename = os.path.basename(doc_path)
            
            shelf_wdg = DivWdg()
            shelf_wdg.add_style("height: 35px")
            shelf_wdg.add_style("padding: 5px 10px")
            shelf_wdg.add_color("background", "background3")
            doc_div.add(shelf_wdg)

            button = ActionButtonWdg(title="Edit")
            shelf_wdg.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'dirname': dirname,
                'basename': basename,
                'cbjs_action': '''
                //var path = bvr.rel_path;

                var class_name = 'tactic.ui.app.PluginDirListEditFileWdg';
                var kwargs = {
                    dirname: bvr.dirname,
                    basename: bvr.basename
                }
                spt.panel.load_popup(bvr.basename, class_name, kwargs);
                '''
                } )
            # prevent drawing bug when file size is 0 byte
            if os.path.getsize(doc_path) > 0:
                from tactic.ui.app import HelpContentWdg
                doc_wdg = HelpContentWdg(rel_path=rel_path)
                doc_div.add(doc_wdg)
        else:
            doc_div = DivWdg()
            doc_div.add("No Documentation File in Plugin")
            doc_div.add_border()
            doc_div.add_color("background", "background3")
            doc_div.add_style("padding", "30px 50px 30px 50px")
            doc_div.add_style("margin", "100px auto")
            doc_div.add_style("text-align: center")
            doc_div.add_style("width: 300px")

            doc_div.add("<br/><br/>")

            button = ActionButtonWdg(title="Create")
            doc_div.add(button)
            button.add_style("margin-left: auto")
            button.add_style("margin-right: auto")

            button.add_behavior( {
                'type': 'click_up',
                'dirname': my.dirname,
                'cbjs_action': '''
                var class_name = 'tactic.ui.app.PluginDirListActionCbk';
                var kwargs = {
                    'action': 'new_file',
                    'basename': 'doc.html',
                    'dirname': bvr.dirname, 
                }
                var server = TacticServerStub.get();
                try {
                    server.execute_cmd(class_name, kwargs);
                } catch(e) {
                    spt.alert(spt.exception.handler(e));
                    return;
                }

                var top = bvr.src_el.getParent(".spt_plugin_edit");
                top.setAttribute("spt_selected", "documentation")
                spt.panel.refresh(top)

                '''
            } )


        doc_div.set_name("documentation")


        return doc_div



    def get_insert_wdg(my):

        shelf_div = DivWdg()

        button = ActionButtonWdg(title='Create >>', tip='Create Plugin')
        shelf_div.add(button)
        button.add_style("float: right")
        button.add_behavior( {
        'type': 'click_up', 
        'cbjs_action': '''
        spt.api.app_busy_show("Exporting Plugin");

        var top = bvr.src_el.getParent(".spt_plugin_edit");
        var search_key = top.getAttribute("spt_search_key");

        var values = spt.api.get_input_values(top, null, false);

        var manifest = values.manifest;
        if (!manifest || manifest == "") {
            manifest = "<manifest/>";
        }

        var code = values.code;
        var version = values.version;
        if (version == 'DEV') {
            version = '';
            register = true;
        }
        else {
            register = false;
        }
        var description = values.description;
        var title = values.title;

        var plugin_template = values.plugin_template;

        var server = TacticServerStub.get();

        var class_name;
        if (plugin_template == "Project") {
            class_name = 'tactic.command.ProjectTemplateCreatorCmd';
        }
        else {
           //class_name = 'tactic.command.PluginCreator';
           class_name = 'tactic.ui.app.PluginCreatorCmd';
        }

        var kwargs = {
            clean: false,
            code: code,
            version: version,
            title: title,
            description: description,
            manifest: manifest,
            plugin_template: plugin_template,
            register: register,
        };
        try {
            server.execute_cmd(class_name, kwargs);
            var top = bvr.src_el.getParent(".spt_plugin_top");
            spt.notify.show_message('Plugin "' + title + '" installed.')
        }
        catch(err) {
            spt.alert(spt.exception.handler(err));
        }
        spt.panel.refresh(top);

        spt.api.app_busy_hide();

        '''
        })

        return shelf_div



    def is_active(my):

        if my.is_active_flag != None:
            return my.is_active_flag

        shelf_div = DivWdg()

        search = Search("config/plugin")
        search.add_filter("code", my.code)

        if my.version:
            search.add_filter("version", my.version)

        active = search.get_sobject()
        if active:
            active = True
        else:
            active = False

        my.is_active_flag = active

        return active



    def get_action_wdg(my):

        shelf_div = DivWdg()

        active = my.is_active()


        shelf_div.add_color("background", "background", -10)
        shelf_div.add_color("color", "color")
        shelf_div.add_border()
        shelf_div.add_style("padding: 15px 5px 0px 15px")
        shelf_div.add_style("margin: 0px -21px 20px -21px")


        if not active:

            plugin_base_dir = os.path.dirname(my.plugin_dir)
            code = os.path.basename(my.plugin_dir)

            shelf_div.add(HtmlElement.b("This plugin is not active in this project. Click on the button to activate."))

            button = ActionButtonWdg(title='Activate', tip='Activate Plugin in Current Project')
            shelf_div.add(button)
            
            button.add_style("margin: 20px 250px")
            button.add_behavior( {
            'type': 'click_up', 
            'plugin_dir': my.plugin_dir,
            'cbjs_action': '''
            spt.api.app_busy_show("Activating Plugin");

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");

            var class_name = 'tactic.command.PluginInstaller';
            var kwargs = {
                mode: 'install',
                plugin_dir: bvr.plugin_dir,
                register: true
            };

            var server = TacticServerStub.get();
            try {
                server.execute_cmd( class_name, kwargs );
            }
            catch(e) {
                spt.alert(spt.exception.handler(e));
                spt.api.app_busy_hide();
                return;
            } 

            var top = bvr.src_el.getParent(".spt_plugin_top");
            top.setAttribute("spt_plugin_dir", bvr.plugin_dir);
            top.setAttribute("spt_selected", "info")
            spt.panel.refresh(top);

            spt.api.app_busy_hide();
            spt.notify.show_message('plugin "'+ bvr.plugin_dir +'" activated');

            '''
            })

        else:
            shelf_div.add(HtmlElement.b("This plugin is active in this project. Click to Remove or Reload."))
            buttons_div = DivWdg()
            buttons_div.add_style("margin-left: 200px")
            remove_button = ActionButtonWdg(title='Remove', tip='Remove Plugin from current preject')
            reload_button = ActionButtonWdg(title='Reload', tip='Reload Plugin from current preject')
            buttons_div.add(remove_button)
            buttons_div.add(reload_button)
            shelf_div.add(buttons_div)
            remove_button.add_style("margin: 20px 10px")
            remove_button.add_style("display: inline-block")
            reload_button.add_style("margin: 20px 10px")
            reload_button.add_style("display: inline-block")
            
            remove_button.add_behavior( {
            'type': 'click_up', 
            'plugin_code': my.code,
            'cbjs_action': '''
            spt.api.app_busy_show("Removing Plugin");

            if (!confirm("WARNING: Remove plugin ["+bvr.plugin_code+"]?")) {
                spt.api.app_busy_hide();
                return;
            }

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");

            var class_name = 'tactic.command.PluginUninstaller';
            var kwargs = {
                code: bvr.plugin_code
            };

            var server = TacticServerStub.get();
            try {
                server.execute_cmd( class_name, kwargs );
            }
            catch(e) {
                spt.alert(spt.exception.handler(e));
                spt.api.app_busy_hide();
                return;
            } 

            var top = bvr.src_el.getParent(".spt_plugin_top");
            spt.notify.show_message('Plugin "'+bvr.plugin_code+'" successfully removed')
            spt.panel.refresh(top);

            spt.api.app_busy_hide();

            '''
            })
            
            reload_button.add_behavior( {
            'type': 'click_up', 
            'plugin_code': my.code,
            'cbjs_action': '''
            spt.api.app_busy_show("Reloading Plugin");

            if (!confirm("WARNING: Reload plugin ["+bvr.plugin_code+"]?")) {
                spt.api.app_busy_hide();
                return;
            }

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");

            var class_name = 'tactic.command.PluginReloader';
            var kwargs = {
                code: bvr.plugin_code
            };

            var server = TacticServerStub.get();
            try {
                server.execute_cmd( class_name, kwargs );
            }
            catch(e) {
                spt.alert(spt.exception.handler(e));
                spt.api.app_busy_hide();
                return;
            } 

            var top = bvr.src_el.getParent(".spt_plugin_top");
            spt.notify.show_message('Plugin "'+bvr.plugin_code+'" successfully reloaded')
            spt.panel.refresh(top);

            spt.api.app_busy_hide();

            '''
            })


            """
            button = ActionButtonWdg(title='Publish', tip='Publish new version')
            shelf_div.add(button)
            button.add_style("float: left")
            button.add_behavior( {
            'type': 'click_up', 
            'from_version': my.version,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");

            var values = spt.api.get_input_values(top, null, false);

            var manifest = values.manifest;
            if (!manifest || manifest == "") {
                manifest = "<manifest/>";
            }

            var code = values.code;
            var version = values.version;
            if (version == 'DEV') {
                spt.alert("Cannot create DEV version");
                return;
            }
            if (version.match(/^v/i)) {
                spt.alert("We recommend Version not starting with a V.")
                return;
            }

            var class_name = 'tactic.ui.app.PluginVersionCreator';
            var kwargs = {
                code: code,
                version: version,
                from_version: bvr.from_version
            }

            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);


            var top = bvr.src_el.getParent(".spt_plugin_top");
            spt.panel.refresh(top);

            spt.notify.show_message('Plugin [' + code + '] ' + version+ ' created.');
            
            '''
            } )
            """


        shelf_div.add("<br clear='all'/>")
        return shelf_div



__all__.append("PluginCreatorCmd")
class PluginCreatorCmd(Command):
    def execute(my):

        plugin_type = my.kwargs.get("plugin_type")

        if plugin_type == "column":
            my.create_column_type()
    
        elif plugin_type == "theme":
            my.create_theme_type()


        from tactic.command import PluginCreator
        cmd = PluginCreator(**my.kwargs)
        cmd.execute()


    def create_widget_type(my):

        code = my.kwargs.get("code")
        view = code.replace("/", ".")

        config = SearchType.create("config/widget_config")
        config.set_value("view", view)
        config.set_value("widget_type", "widget")
        config.set_value("category", "CustomLayoutWdg")
        config.set_value("config", '''
<config>
  <%s>
    <html>
      <div>Created from plugin [%s]</div>
    </html>
  </%s>
</config>
        ''' % (view, code, view))


        config.commit()

        my.kwargs['manifest'] = '''
        <manifest>
          <sobject search_type="config/widget_config" view="%s"/>
        </manifest>
        ''' % view




    def create_column_type(my):

        code = my.kwargs.get("code")
        view = code.replace("/", ".")

        config = SearchType.create("config/widget_config")
        config.set_value("view", view)
        config.set_value("widget_type", "column")
        config.set_value("category", "CustomLayoutWdg")
        config.set_value("config", '''
<config>
  <%s>
    <html>
      <div>Created from plugin [%s]</div>
    </html>
  </%s>
</config>
        ''' % (view, code, view))


        config.commit()

        my.kwargs['manifest'] = '''
        <manifest>
          <sobject search_type="config/widget_config" view="%s"/>
        </manifest>
        ''' % view


    def create_theme_type(my):

        code = my.kwargs.get("code")
        view = code.replace("/", ".")

        config = SearchType.create("config/widget_config")
        config.set_value("view", view)
        config.set_value("widget_type", "theme")
        config.set_value("category", "CustomLayoutWdg")
        config.set_value("config", '''
<config>
  <%s>
    <html>
      <div>Theme from plugin [%s]</div>
    </html>
  </%s>
</config>
        ''' % (view, code, view))


        config.commit()

        my.kwargs['manifest'] = '''
        <manifest>
          <sobject search_type="config/widget_config" view="sample_theme.index" path="config/config_widget_config.spt"/>
          <sobject search_type="config/url" url="/index" path="config/config_url.spt"/>
        </manifest>
        '''






class PluginDirListWdg(DirListWdg):


    def handle_dir_div(my, item_div, dirname, basename):
        value_div = DivWdg()
        item_div.add(value_div)
        value_div.add_class("spt_value")
        value_div.add(basename)
        SmartMenu.assign_as_local_activator( item_div, 'PLUGIN_ITEM_CTX' )

        my.add_rename_wdg(item_div, dirname, basename)

    def handle_item_div(my, item_div, dirname, basename):
        path = "%s/%s" % (dirname, basename)
        if my.info.get("file_type") == 'missing':
            icon_string = IconWdg.DELETE
            tip = 'Missing [%s]' %path
        else:
            icon_string = my.get_file_icon(dirname, basename)
            tip = path


        SmartMenu.assign_as_local_activator( item_div, 'PLUGIN_ITEM_CTX' )

        icon_div = DivWdg()
        item_div.add(icon_div)
        icon = IconWdg(tip, icon_string)
        icon_div.add(icon)
        icon_div.add_style("float: left")
        icon_div.add_style("margin-top: -1px")

        # add the file name
        filename_div = DivWdg()
        item_div.add(filename_div)
        filename_div.add_class("spt_value")
        filename_div.add(basename)
        filename_div.add_style("float: left")
        filename_div.add_style("overflow: hidden")
        filename_div.add_class("SPT_DTS")

        my.add_rename_wdg(item_div, dirname, basename)


        item_div.add("<br clear='all'/>")



    def add_rename_wdg(my, item_div, dirname, basename):
        text = TextWdg("value")
        item_div.add(text)
        text.add_class("spt_rename")
        text.add_style("display: none")
        text.add_attr("spt_basename", basename)
        text.add_style("font-size: 12px")

        text.add_behavior( {
            'type': 'blur',
            'dirname': dirname,
            'cbjs_action': '''
            // rename the file
            basename = bvr.src_el.getAttribute("spt_basename");
            new_basename = bvr.src_el.value;

            if (basename != new_basename) {

                var class_name = 'tactic.ui.app.PluginDirListActionCbk';
                var kwargs = {
                    'new_basename': new_basename,
                    'basename': basename,
                    'action': 'rename',
                    'dirname': bvr.dirname
                }
                var server = TacticServerStub.get();
                server.execute_cmd(class_name, kwargs)

                bvr.src_el.setAttribute("spt_basename", new_basename);
            }

            var top = bvr.src_el.getParent(".spt_dir_list_item");
            //var top = bvr.src_el.getParent(".spt_dir");
            var rename_el = top.getElement(".spt_rename");
            var value_el = top.getElement(".spt_value");
            spt.hide(rename_el);
            spt.show(value_el);
            value_el.innerHTML = rename_el.value;
            

            '''
        } )

        text.add_behavior( {
            'type': 'keyup',
            'cbjs_action': '''
            var key = evt.key;
            if (key == 'enter') {
                var top = bvr.src_el.getParent(".spt_dir_list_item");
                //var top = bvr.src_el.getParent(".spt_dir");
                var rename_el = top.getElement(".spt_rename");
                var value_el = top.getElement(".spt_value");
                spt.hide(rename_el);
                spt.show(value_el);
                value_el.innerHTML = rename_el.value;
         
            }
            '''
        } )



    def add_top_behaviors(my, top):


        top.add_behavior( {
            'type': 'load',
            'plugin_dirname': my.kwargs.get("plugin_dirname"),
            'cbjs_action': '''
            spt.plugin = {}
            spt.plugin.dirname = bvr.plugin_dirname;

            spt.plugin.start_y = null;


            spt.plugin.drag_file_setup = function(evt, bvr, mouse_411) {
                spt.plugin.start_y = mouse_411.curr_y
                spt.plugin.start_pos = bvr.src_el.getPosition();
            }
            spt.plugin.drag_file_motion = function(evt, bvr, mouse_411) {
                var diff_y = mouse_411.curr_y - spt.plugin.start_y;
                if (diff_y < 1 && diff_y > -1) {
                    return;
                }

                bvr.src_el.setStyle("position", "absolute");
                bvr.src_el.position({x:mouse_411.curr_x+5, y:mouse_411.curr_y+5});
            }
            spt.plugin.drag_file_action = function(evt, bvr, mouse_411) {
 
                //bvr.src_el.position(spt.plugin.start_pos);

                var pos = spt.plugin.start_pos;
                new Fx.Tween(bvr.src_el,{duration:"short"}).start('top', pos.y);
                new Fx.Tween(bvr.src_el,{duration:"short"}).start('left', pos.x);
                bvr.src_el.setStyle("position", "");

                var drop_on_el = spt.get_event_target(evt);

                if (!drop_on_el.hasClass("spt_dir_item")) {
                    drop_on_el = drop_on_el.getParent(".spt_dir_item");
                }

                if (! drop_on_el) {
                    return;
                }

                var content = drop_on_el.getNext();
                if (!content.hasClass("spt_dir_content")) {
                    spt.alert("Must drop on a folder");
                    return;
                }

                bvr.src_el.inject(content, "top");

                var new_basename = drop_on_el.getAttribute("spt_basename");
                var new_dirname = drop_on_el.getAttribute("spt_dirname");

                var dirname = bvr.src_el.getAttribute("spt_dirname");
                var basename = bvr.src_el.getAttribute("spt_basename");


                new_basename = new_basename + "/" + basename;


                var server = TacticServerStub.get();
                var class_name = 'tactic.ui.app.PluginDirListActionCbk';
                var kwargs = {
                    'new_basename': new_dirname + "/" + new_basename,
                    'basename': dirname + "/" + basename,
                    'action': 'rename',
                    'dirname': spt.plugin.dirname,
                }
                var server = TacticServerStub.get();
                server.execute_cmd(class_name, kwargs)


            }

            '''
        } )

        top.add_behavior( {
            'type': 'smart_drag',
            'bvr_match_class': 'spt_file_item',
            'cbjs_setup': 'spt.plugin.drag_file_setup(evt, bvr, mouse_411)',
            'cbjs_motion': 'spt.plugin.drag_file_motion(evt, bvr, mouse_411)',
            'cbjs_action': 'spt.plugin.drag_file_action(evt, bvr, mouse_411)',
        } )


        # add in a context menu
        menu = my.get_context_menu()
        menus = [menu.get_data()]
        menus_in = {
            'PLUGIN_ITEM_CTX': menus,
        }
        SmartMenu.attach_smart_context_menu( top, menus_in, False )


    def get_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Delete')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var dirname = activator.getAttribute("spt_dirname");
            var basename = activator.getAttribute("spt_basename");
            var kwargs = {
                'action': 'delete',
                'dirname': dirname,
                'basename': basename
            }
            if (!confirm('Delete "' + basename + '"?') ) {
                return;
            }
            var class_name = 'tactic.ui.app.PluginDirListActionCbk';
            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

            var top = activator.getParent(".spt_plugin_edit");
            top.setAttribute("spt_selected", "files");

            spt.panel.refresh(top);

            '''
        } )

        return menu






    def add_dir_behaviors(my, item_div, dir, item):

        item_div.add_behavior( {
            'type': 'click_up',
            'modkeys': 'CTRL',
            'cbjs_action': '''
            var rename_el = bvr.src_el.getElement(".spt_rename");
            var value_el = bvr.src_el.getElement(".spt_value");
            spt.hide(value_el);
            spt.show(rename_el);
            rename_el.value = value_el.innerHTML;
            rename_el.focus();
            '''
        } )






    def add_file_behaviors(my, item_div, dirname, basename):

        plugin_base_dir = Environment.get_plugin_dir()
        builtin_plugin_base_dir = Environment.get_builtin_plugin_dir()

        if dirname.startswith(plugin_base_dir):
            is_builtin = False
            dirname = dirname.replace(plugin_base_dir, "")
        elif dirname.startswith(builtin_plugin_base_dir):
            is_builtin = True
            dirname = dirname.replace(builtin_plugin_base_dir, "")
        else:
            item_div.add_style("color", "#F00")
            return item_div


        if not is_builtin:

            item_div.add_behavior( {
                'type': 'drag',
                "mouse_btn": 'LMB',
                "drag_el": '@',
                "cb_set_prefix": 'spt.plugin.drag_file'

            } )



            item_div.add_behavior( {
                'type': 'click_up',
                'modkeys': 'CTRL',
                'cbjs_action': '''
                var rename_el = bvr.src_el.getElement(".spt_rename");
                var value_el = bvr.src_el.getElement(".spt_value");
                spt.hide(value_el);
                spt.show(rename_el);
                rename_el.value = value_el.innerHTML;
                rename_el.focus();
                '''
            } )


        item_div.add_behavior( {
        'type': 'double_click',
        'dirname': dirname,
        'basename': basename,
        'cbjs_action': '''
        var path = bvr.dirname + "/" + bvr.basename;

        var class_name = 'tactic.ui.app.PluginDirListEditFileWdg';
        var kwargs = {
            dirname: bvr.dirname,
            basename: bvr.basename
        }
        spt.panel.load_popup(bvr.basename, class_name, kwargs);
        '''
        } )


__all__.append("PluginDirListEditFileWdg")
class PluginDirListEditFileWdg(BaseRefreshWdg):
    '''This widget shows the contents of a selected file in an editor
    and allows you to save'''

    def get_plugin_base_dir(my):
        dirname = my.kwargs.get("dirname")
        if dirname.startswith("/TACTIC"):
            plugin_base_dir = Environment.get_builtin_plugin_dir()
        else:
            plugin_base_dir = Environment.get_plugin_dir()


        return plugin_base_dir


    def get_display(my):

        top = my.top


        dirname = my.kwargs.get("dirname")
        basename = my.kwargs.get("basename")

        base, ext = os.path.splitext(basename)
        if ext in ['.txt', '.spt', '.xml', '.html', '.py']:
            button_row = ButtonRowWdg()
            top.add(button_row)
            button_row.add_style("float: left")
            button = ButtonNewWdg(title="Save", icon=IconWdg.SAVE)
            button_row.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'dirname': dirname,
                'basename': basename,
                'cbjs_action': '''

                var content = spt.ace_editor.get_value();

                spt.app_busy.show("Saving " +bvr.basename);

                // save the file
                var class_name = 'tactic.ui.app.PluginDirListActionCbk';
                var kwargs = {
                    'content': content,
                    'basename': bvr.basename,
                    'dirname': bvr.dirname,
                    'action': 'save'
                }
                var server = TacticServerStub.get();
                server.execute_cmd(class_name, kwargs)

                spt.app_busy.hide();

                '''
            } )


            from tactic.ui.app import AceEditorWdg

            # This is protection against accessing any file in the file
            # system
            plugin_base_dir = my.get_plugin_base_dir()
            if (plugin_base_dir in dirname):
                plugin_dir = dirname
            else:
                plugin_dir = "%s/%s" % (plugin_base_dir, dirname)

            doc_path = "%s/%s" % (plugin_dir, basename)
            f = open(doc_path, 'r')
            html = f.read()
            f.close()

            ace = AceEditorWdg(code=html, language="html", show_options=False)
            top.add(ace)
        else:
            if dirname.startswith("/TACTIC"):
                path = "/builtin_plugins%s/%s" % (dirname, basename)
            else:
                path = "/plugins%s/%s" % (dirname, basename)
            div = DivWdg()
            top.add(div)
            div.add("<img style='max-width: 600px' src='%s'/>" % path)


        return top






class PluginInstallWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_style("padding: 30px")
        top.add_class("spt_plugin_install_top")


        url_wdg = DivWdg()
        top.add(url_wdg)
        url_wdg.add_style("padding: 20px")
        url_wdg.add_border()
        url_wdg.add_color("background", "background3")
        url_wdg.add_color("color", "color3")
        url_wdg.add_style("width: 600px")

        url_wdg.add("Copy and paste the URL of a plugin: ")

        table = Table()
        table.add_style("width: 600px")
        url_wdg.add(table)
        table.add_row()
        td = table.add_cell("URL: ")
        table.add_style("margin: 10px")
        td.add_style("width: 150px")
        td.add_style("padding-right: 10px")
        td.add_style("text-align: right")
        td.add_style("vertical-align: top")

        td = table.add_cell()
        url_text = TextInputWdg(name="url")
        url_text.add_style("width: 400px")
        td.add(url_text)

        
        tr = table.add_row()
        tr.add_style("display: none")
        td = table.add_cell("MD5 Checksum: ")
        td.add("<br/><i style=font-size: 10px>(optional)</i>")
        td.add_style("text-align: right")
        td.add_style("padding-right: 10px")
        td.add_style("vertical-align: top")

        td = table.add_cell()
        md5_text = TextInputWdg(name="md5")
        md5_text.add_style("width: 400px")
        td.add(md5_text)

        tr, td = table.add_row_cell()
        install_button = ActionButtonWdg(title="Install")
        td.add(install_button)  
        install_button.add_style("margin: 10px")
        install_button.add_style("float: right")
        install_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_plugin_install_top");
            var values = spt.api.get_input_values(top);
            var url = values.url[0];
            if (! url) { 
                spt.alert("No URL for plugin specified");
                return;
            }
            var md5 = values.md5[0];

            var class_name = 'tactic.ui.app.PluginDownloadCbk';
            var kwargs = {
                url: url,
                md5: md5
            }

            spt.app_busy.show("Downloading and installing plugin ...");

            var server = TacticServerStub.get();

            try {
                server.execute_cmd( class_name, kwargs );
            }
            catch(e) {
                alert(e);
                spt.api.app_busy_hide();
                return;
            }


            var top = bvr.src_el.getParent(".spt_plugin_top");
            spt.panel.refresh(top);

            spt.api.app_busy_hide();




            '''
        } )

        top.add("<br/>"*2)


        or_div = DivWdg()
        top.add(or_div)
        or_div.add("OR")
        or_div.add_style("width: 600px")
        or_div.add_style("text-align: center")
        or_div.add_style("font-size: 2.0em")

        top.add("<br/>"*3)

        browse_div = DivWdg()
        top.add(browse_div)
        browse_div.add_style("width: 600px")
        browse_div.add_style("padding: 20px")
        browse_div.add_border()
        browse_div.add_color("background", "background3")
        browse_div.add_color("color", "color3")


        browse_div.add("Press Browse and select the .zip plugin file")
        from tactic.ui.input import UploadButtonWdg
        upload_button = UploadButtonWdg(name="Browse")
        upload_button.add_style("float: right")
        browse_div.add(upload_button)

        upload_button.set_on_complete('''
            var file = spt.html5upload.get_file();
            if (!file) {
               alert('Error: file cannot be found.')
               spt.app_busy.hide();
               return;
            }

            var file_name = file.name;

            try {

                var server = TacticServerStub.get();
                //var class_name = 'tactic.command.PluginInstaller';
                var class_name = 'tactic.command.PluginUploader';
                var kwargs = {
                    'upload_file_name': file_name,
                    'path': file_name
                }
                server.execute_cmd(class_name, kwargs);

                spt.notify.show_message("Plugin successfully added.");

            } catch(e) {
                alert("Cannot install plugin: " + file_name);
            }

            var top = bvr.src_el.getParent(".spt_plugin_top");
            spt.panel.refresh(top);

            spt.app_busy.hide();

        ''')


        return top



__all__.append("PluginVersionCreator")
class PluginVersionCreator(Command):
    '''This is called when clicking on Publish'''
    def execute(my):

        dist_dir = my.kwargs.get("dist_dir")
        if not dist_dir:
            dist_dir = Environment.get_dist_dir()

        version = my.kwargs.get("version")
        from_version = my.kwargs.get("from_version")
        if from_version in ['None', None]:
            from_version = ''

        assert version
       
        # code is the same as dirname usually
        code = my.kwargs.get('code')

        search = Search("config/plugin")
        search.add_filter("code", code)
        plugin = search.get_sobject()
        # In case there is extra plugins folder which is the case when the user 
        # is developing. 
        relative_dir = plugin.get_value("rel_dir")
        relative_parts = relative_dir.split('/') 
        relative_dir_no_leaf = '/'.join(relative_parts[0:-1])
        relative_dir_head = relative_parts[0]
       
        plugin_base_dir = Environment.get_plugin_dir()
        plugin_dir = "%s/%s" % (plugin_base_dir, relative_dir)



        existing_dirname = code
        if from_version:
            existing_dirname = '%s-%s'%(existing_dirname, from_version)
       
        new_dirname = code
        if version:
            new_dirname = '%s-%s'%(new_dirname, version)

        basecode = os.path.basename(code)

        zip_path = "%s/%s-%s.zip" % (dist_dir, basecode, version)

        """
        
        if not existing_dirname.startswith(plugin_base_dir):
            plugin_dir = "%s/%s" % (plugin_base_dir, existing_dirname)
        else:
            plugin_dir = existing_dirname
        """
        
        if relative_dir_no_leaf:
            new_plugin_dir = "%s/%s/%s" % (plugin_base_dir, relative_dir_no_leaf, new_dirname)
            root_dir = "%s/%s" % (plugin_base_dir, relative_dir_head)
            new_relative_dir =  "%s/%s" %(relative_dir_no_leaf, new_dirname)
            new_relative_parts = new_relative_dir.split('/')
            include_dirs = ['/'.join(new_relative_parts[1:])]
        else:
            new_plugin_dir = "%s/%s" % (plugin_base_dir, new_dirname)
            root_dir = new_plugin_dir
            include_dirs = None

        if os.path.exists(new_plugin_dir):
            os.makedirs(new_plugin_dir)

        try:
            from shutil import ignore_patterns
            ignore_pat = ignore_patterns('*.pyc', '*.swp', '*.swo', '*.py~','*.bak')
            shutil.copytree(plugin_dir, new_plugin_dir, ignore=ignore_pat)
        except ImportError:    
            shutil.copytree(plugin_dir, new_plugin_dir)
        
        # find manifest
        manifest_path = "%s/manifest.xml" % new_plugin_dir
        f = open(manifest_path)
        manifest = f.read()
        f.close()

        xml = Xml()
        xml.read_string(manifest)

        node = xml.get_node("manifest/data/version")
        if node is not None:
            xml.set_node_value(node, version)
        else:
            node = xml.create_element("version")
            xml.set_node_value(node, version)
            data_node = xml.get_node("manifest/data")
            xml.append_child(data_node, node)
    

        f = open(manifest_path, 'wb')
        f.write( xml.to_string())
        f.close()

        # zip up the folder from the plugin root
        # FIXME: this doesn't quite work yet
        """
        from pyasm.common import ZipUtil
        plugin_base_dir = Environment.get_plugin_dir()
        zip_path = "%s.zip" % new_plugin_dir

        include_dirs = ['southpaw']
        zip_util = ZipUtil()
        zip_util.zip_dir(plugin_base_dir, zip_path=zip_path, include_dirs=include_dirs)
        """

        # OLD logic to be deleted
        """
        #parts = new_plugin_dir.split("/")
        #include_dirs = [parts[-1]]
        #root_dir = '/'.join(parts[0:-1])
        
        # e.g. vfx or spt/vfx
        parts = code.split("/")
        root_dir = "%s/%s" % (plugin_base_dir, parts[0])
        if len(parts) >= 2:
            include_dirs = ["/".join(parts[1:])]
        else:
            include_dirs = None
        """

        ignore_dirs = ['.svn']
        ZipUtil.zip_dir(root_dir, zip_path, ignore_dirs=ignore_dirs, include_dirs=include_dirs)
        



class PluginDirListActionCbk(Command):

    def execute(my):
        action = my.kwargs.get("action")

        dirname = my.kwargs.get("dirname")
        assert(dirname)


        builtin_plugin_base_dir = Environment.get_builtin_plugin_dir()
        if dirname.startswith(builtin_plugin_base_dir):
            plugin_base_dir = builtin_plugin_base_dir
        elif dirname.startswith("TACTIC"):
            plugin_base_dir = builtin_plugin_base_dir
        else:
            plugin_base_dir = Environment.get_plugin_dir()

        if not dirname.startswith(plugin_base_dir):
            plugin_dir = "%s/%s" % (plugin_base_dir, dirname)
        else:
            plugin_dir = dirname


        if action == 'new_file':
            basename = my.kwargs.get("basename")
            default_name = False
            if not basename:
                basename = "new_file"
                default_name = True

            file_path = "%s/%s" % (plugin_dir, basename)

            if not file_path.startswith(plugin_base_dir):
                raise Exception("Cannot alter file outside of plugin")

            
            if not os.path.exists(file_path):
                if default_name:
                    file_path = "%s.html" %file_path
                f = open(file_path, 'w')
                 
                f.close()
            else:
                i = 2
                while os.path.exists("%s%s.html"%(file_path, str(i))):
                    i += 1

                f = open("%s%s.html"%(file_path, str(i)), 'w')
                f.close()

        elif action == 'new_folder':
            basename = "new_folder"
            file_path = "%s/%s" % (plugin_dir, basename)

            if not file_path.startswith(plugin_base_dir):
                raise Exception("Cannot alter file outside of plugin")

            if not os.path.exists(file_path):
                os.makedirs(file_path)
            else:            
                i = 2
                while os.path.exists(file_path + str(i)):
                    i += 1

                os.makedirs(file_path + str(i))
                
        elif action == 'rename':
            basename = my.kwargs.get("basename")
            new_basename = my.kwargs.get("new_basename")

            if not basename.startswith(plugin_dir):
                file_path = "%s/%s" % (plugin_dir, basename)
            else:
                file_path = basename 

            if not new_basename.startswith(plugin_dir):
                new_file_path = "%s/%s" % (plugin_dir, new_basename)
            else:
                new_file_path = new_basename 


            if not file_path.startswith(plugin_base_dir):
                raise Exception("Cannot alter file outside of plugin")
            if not new_file_path.startswith(plugin_base_dir):
                raise Exception("Cannot alter file outside of plugin")


            if os.path.exists(file_path):
                os.rename(file_path, new_file_path)
                


        elif action == 'upload':
            upload_dir = Environment.get_upload_dir()
            basename = my.kwargs.get("upload_file_name")
            # use the same call as in the FileUpload class
            basename = File.get_filesystem_name(basename)
            
            upload_path = "%s/%s" % (upload_dir, basename)


            to_path = "%s/%s" % (plugin_dir, basename)
            if os.path.exists(to_path):
                os.unlink(to_path)

            shutil.move(upload_path, to_path)
            if to_path.endswith(".zip"): 
                from pyasm.common import ZipUtil
                zip_util = ZipUtil()
                zip_util.extract(cls, to_path)



        elif action == 'save':
            basename = my.kwargs.get("basename")
            file_path = "%s/%s" % (plugin_dir, basename)

            content = my.kwargs.get("content")

            if not file_path.startswith(plugin_base_dir):
                raise Exception("Cannot alter file outside of plugin")

            f = open(file_path, 'wb')
            f.write(content)
            f.close()

        elif action == 'delete':

            basename = my.kwargs.get("basename")
            file_path = "%s/%s" % (plugin_dir, basename)

            if not file_path.startswith(plugin_base_dir):
                raise Exception("Cannot alter file outside of plugin")

            if not os.path.exists(file_path):
                raise Exception("File [%s] does not exist" % basename)

            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.unlink(file_path)

            # remove all the plugin entry???


        elif action == 'clear_spt':
            for root, dirnames, basenames in os.walk(plugin_dir, followlinks=True):
                for basename in basenames:
                    path = "%s/%s" % (root, basename)
                    if path.endswith(".spt"):
                        os.unlink(path)

        else:
            raise Exception("Action [%s] not support" % action)







class PluginRemoveCbk(Command):

    def execute(my):

        dirname = my.kwargs.get("dirname")
        if not dirname:
            return

        plugin_base_dir = Environment.get_plugin_dir()

        plugin_dir = "%s/%s" % (plugin_base_dir, dirname)
        if os.path.exists(plugin_dir):
            print "Removing from installation: ", plugin_dir
            shutil.rmtree(plugin_dir)

        zip_path = "%s.zip" % plugin_dir
        if os.path.exists(zip_path):
            os.unlink(zip_path)

        # remove dist dir
        dist_dir = Environment.get_dist_dir()
        plugin_dir = "%s/%s" % (dist_dir, dirname)
        zip_path = "%s.zip" % plugin_dir
        if os.path.exists(zip_path):
            os.unlink(zip_path)

class PluginDownloadCbk(Command):

    def execute(my):

        url = my.kwargs.get("url")

        if not url or not url.endswith(".zip"):
            raise TacticException("URL [%s] is not a link to a plugin file")


        md5 = my.kwargs.get("md5")

        my.plugin_dir = Environment.get_plugin_dir()

        basename = os.path.basename(url)
        plugin_path = "%s/%s" % (my.plugin_dir, basename)
        if os.path.exists(plugin_path):
            raise TacticException("This plugin [%s] is already installed. Please remove first" % basename)


        path = Common.download(url, to_dir=my.plugin_dir, md5_checksum=md5)

        from tactic.command import PluginUploader
        installer = PluginUploader(
            zip_path=path,
        )
        installer.execute()





