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

__all__ = ['PluginWdg', 'PluginEditWdg', 'PluginUploadRegisterWdg', 'PluginUploadRegisterCbk', 'PluginInstallIntoProjectCbk', 'PluginRemoveCbk']

from pyasm.common import Environment, TacticException, Config, Xml, Common
from pyasm.command import Command
from pyasm.web import DivWdg, Table
from pyasm.widget import ButtonWdg, ProdIconButtonWdg, TextWdg, TextAreaWdg, CheckboxWdg, IconWdg
from pyasm.search import Search, SearchType

import os, codecs
import zipfile, shutil

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg
from tactic.ui.widget import ActionButtonWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu


class PluginWdg(BaseRefreshWdg):

    def get_display(my):

        div = DivWdg()
        div.add_class("spt_plugin_top")
        my.set_as_panel(div)

        div.add_color("background", "background")


        # add the main layout
        #table = ResizableTableWdg()
        table = Table()
        table.add_color("color", "color")
        div.add(table)

        table.add_row()
        left = table.add_cell()
        left.add_border()
        left.add_style("vertical-align: top")
        left.add_style("min-width: 250px")
        left.add_style("height: 400px")
        left.add_color("background", "background3")

        left.add(my.get_plugins_wdg() )

        right = table.add_cell()
        right.add_border()
        right.add_style("vertical-align: top")
        right.add_style("min-width: 400px")
        right.add_style("width: 100%")
        right.add_style("height: 400px")
        right.add_style("padding: 5px")


        edit = PluginEditWdg()
        right.add(edit)

        return div



    def get_plugins_wdg(my):
        div = DivWdg()

        # use the file system
        data_dir = Environment.get_data_dir()
        plugin_dir = Environment.get_plugin_dir()
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)

        dirnames = os.listdir(plugin_dir)
        dirnames.sort()
        dirnames.reverse()
        plugin_dirnames = []
        for dirname in dirnames:
            if dirname.endswith(".zip"):
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


        title_div = DivWdg()
        div.add(title_div)
        title_div.add("Plugin List")
        title_div.add_style("font-size: 14px")
        title_div.add_style("font-weight: bold")
        title_div.add_gradient("background", "background", 0, -10)
        title_div.add_style("padding: 5px")
        title_div.add_style("margin-bottom: 15px")

        new_button = ActionButtonWdg(title='New', size='medium', tip='Create a new plugin')
        title_div.add(new_button)
        new_button.add_style("margin-top: -22px")
        new_button.add_style("margin-right: -5px")
        new_button.add_style("float: right")
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




        add_button = ActionButtonWdg(title='+', size='small', tip='Install a plugin')
        title_div.add(add_button)
        add_button.add_style("margin-top: -22px")
        add_button.add_style("margin-right: -5px")
        add_button.add_style("float: right")

        add_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_plugin_top");
        var edit = top.getElement(".spt_plugin_edit");
        var class_name = "tactic.ui.app.PluginUploadRegisterWdg";
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



        base_dir = Environment.get_plugin_dir()

        last_title = ""

        for dirname in plugin_dirnames:

            # find the manifest file
            plugin_dir = "%s/%s" % (base_dir, dirname)
            manifest_path ="%s/manifest.xml" % (plugin_dir)
            if not os.path.exists(manifest_path):
                invalid = True
            else:
                invalid = False
                

            if invalid:
                data = {}
            else:
                manifest = Xml()
                manifest.read_file(manifest_path)

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
            div.add(plugin_div)
            plugin_div.add_style("padding: 5px")
            plugin_div.add_class("hand")

            SmartMenu.assign_as_local_activator( plugin_div, 'PLUGIN_CTX' )
            plugin_div.add_attr("spt_plugin_dirname", dirname)

            # FIXME: this logic is NOT correct
            is_active = code in active_codes and version in active_versions

            if is_active:
                icon = IconWdg("Active in project", IconWdg.CHECK)
            else:
                icon = DivWdg()
                icon.add_style("width: 22px")
                icon.add("&nbsp;")
                icon.add_style("float: left")
            plugin_div.add(icon)

            plugin_div.add_attr("title", description)

            if invalid:
                plugin_div.add("<i style='opacity: 0.5; color: red'>%s</i>" % dirname)

            elif not title:
                if code:
                    title = Common.get_display_title(code)
                    plugin_div.add("%s" % title)
                else:
                    title = dirname
                    plugin_div.add("N/A <i>(%s)</i>" % title)
            else:
                if title == last_title:
                    plugin_div.add("<i style='opacity: 0.5'>%s</i>" % title)
                else:
                    plugin_div.add(title)

                if version:
                    version_str = '''<span style="opacity: 0.5; font-style: italic; font-size: 10px"> (v%s)</span>''' % version
                else:
                    version_str = '''<span style="opacity: 0.5; font-style: italic; font-size: 10px"> (DEV)</span>'''
                plugin_div.add(version_str)


            last_title = title


            plugin_div.add_behavior( {
            'type': 'click_up',
            'plugin_dir': plugin_dir,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_plugin_top");
            var edit = top.getElement(".spt_plugin_edit");
            var class_name = "tactic.ui.app.PluginEditWdg";
            var kwargs = {
              plugin_dir: bvr.plugin_dir
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

        return div


    def get_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Remove Plugin')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_custom_layout_top");
            var view = activator.getAttribute("spt_view");

            spt.api.app_busy_show("Removing plugin ["+bvr.code+"]");

            var dirname = activator.getAttribute("spt_plugin_dirname");

            if (!confirm("Remove plugin ["+dirname+"] from installation")) {
                return
            }

            var kwargs = {
                dirname: dirname
            }

            var class_name = 'tactic.ui.app.PluginRemoveCbk';

            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

            var top = activator.getParent(".spt_plugin_top");
            spt.panel.refresh(top);

            spt.api.app_busy_hide();

        ''' } )

        return menu



class PluginEditWdg(BaseRefreshWdg):
    def get_display(my):

        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_plugin_edit")


        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add_style("font-size: 14px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("margin-bottom: 10px")

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



            top.add(manifest_path)
            top.add("<br/>"*2)

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

            title_wdg.add("Edit Plugin Info")

        else:
            my.plugin_dir = ""

            my.code = ''
            description = ''
            my.version = ''
            title = ''
            manifest = ''

            plugin = None

            title_wdg.add("Create New Plugin")

        action_wdg = my.get_action_wdg()
        top.add(action_wdg)

        from tactic.ui.container import TabWdg
        selected = "info"
        tab = TabWdg(selected=selected, show_add=False, tab_offset="10px")
        top.add(tab)
        tab.add_style("margin: 0px -6px 0px -6px")

        info_div = DivWdg()
        tab.add(info_div)
        info_div.add_color("background", "background")
        info_div.set_name("info")
        info_div.add_style("height: 100%")
        info_div.add_style("padding: 20px 30px 20px 30px")

        table = Table()
        info_div.add(table)
        table.add_color("color", "color")
        table.add_style("height: 280px")
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


        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Title: ")
        td.add_style("vertical-align: top")
        text = TextInputWdg(name="title", read_only=read_only)
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(title)




        table.add_row()
        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Code: ")
        td.add_style("vertical-align: top")
        text = TextInputWdg(name="code", read_only=read_only)
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(my.code)


        table.add_row()
        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Version: ")
        td.add_style("vertical-align: top")
        #text = TextInputWdg(name="version", read_only=read_only)
        text = TextInputWdg(name="version", read_only=False)
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(my.version)


        table.add_row()
        td = table.add_cell()
        td.add_class("spt_table_header")
        td.add("Description: ")
        td.add_style("vertical-align: top")
        text = TextAreaWdg("description")
        text.set_option("read_only", read_only)
        text.add_style("height", "150px")
        td = table.add_cell()
        td.add_class("spt_table_element")
        td.add(text)
        text.set_value(description)


        manifest_div = DivWdg()
        tab.add(manifest_div)
        manifest_div.set_name("manifest")
        text = TextAreaWdg("manifest")
        text.add_style("width: 100%")
        text.add_style("min-height: 400px")
        text.add_style("font-size: 12px")
        manifest_div.add(text)
        text.set_value(manifest)



        dir_div = DivWdg()
        tab.add(dir_div)
        dir_div.set_name("files")



        dir_div.add_style("padding: 15px")

        if my.mode != 'insert':
            from tactic.ui.widget import DirListWdg
            dir_div.add_color("background", "background")
            dir_list = DirListWdg(base_dir=my.plugin_dir, location="server")
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



        # documentation for the plugin
        if my.plugin_dir:
            doc_path = "%s/doc.html" % my.plugin_dir
            dirname = os.path.basename(my.plugin_dir)
            rel_path = "/plugins/%s/doc.html" % dirname
            if os.path.exists(doc_path):
                from tactic.ui.app import HelpContentWdg
                doc_div = HelpContentWdg(rel_path=rel_path)
                tab.add(doc_div)
                doc_div.set_name("Documentation")


        return top


    def get_action_wdg(my):

        div = DivWdg()

        insert = my.get_insert_wdg()
        div.add( insert )
        if my.mode == 'insert':
            return div


        search = Search("config/plugin")
        search.add_filter("code", my.code)
        search.add_filter("version", my.version)

        installed = search.get_sobject()
        if installed:
            installed = True
        else:
            installed = False

        if not installed:

            plugin_base_dir = os.path.dirname(my.plugin_dir)
            code = os.path.basename(my.plugin_dir)


            button = ActionButtonWdg(title='Activate', tip='Install Plugin into Current Project')
            div.add(button)
            button.add_behavior( {
            'type': 'click_up', 
            'plugin_dir': my.plugin_dir,
            'cbjs_action': '''
            spt.api.app_busy_show("Installing Plugin");

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");

            var class_name = 'tactic.command.PluginInstaller';
            var kwargs = {
                mode: 'install',
                plugin_dir: bvr.plugin_dir,
                register: true
            };

            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

            var top = bvr.src_el.getParent(".spt_plugin_top");
            spt.panel.refresh(top);

            spt.api.app_busy_hide();

            '''
            })

        else:

            button = ActionButtonWdg(title='Remove', tip='Remove Plugin from current preject')
            div.add(button)
            button.add_behavior( {
            'type': 'click_up', 
            'plugin_code': my.code,
            'cbjs_action': '''
            spt.api.app_busy_show("Removing Plugin");

            var top = bvr.src_el.getParent(".spt_plugin_edit");
            var search_key = top.getAttribute("spt_search_key");

            var class_name = 'tactic.command.PluginUninstaller';
            var kwargs = {
                code: bvr.plugin_code
            };

            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

            var top = bvr.src_el.getParent(".spt_plugin_top");
            spt.panel.refresh(top);

            spt.api.app_busy_hide();

            '''
            })




        return div


    def get_insert_wdg(my):

        div = DivWdg()

        button = ActionButtonWdg(title='Save', tip='Save Plugin Info')
        div.add(button)
        button.add_behavior( {
        'type': 'click_up', 
        'cbjs_action': '''
        spt.api.app_busy_show("Saving Plugin");

        var top = bvr.src_el.getParent(".spt_plugin_edit");
        var search_key = top.getAttribute("spt_search_key");

        var values = spt.api.get_input_values(top, null, false);

        var manifest = values.manifest;
        if (manifest == "") {
            manifest = "<manifest/>";
        }

        var code = values.code;
        var version = values.version;
        var description = values.description;
        var title = values.title;

        var class_name = 'tactic.command.PluginCreator';

        var kwargs = {
            force: true,
            code: code,
            version: version,
            title: title,
            description: description,
            manifest: manifest
        };

        var server = TacticServerStub.get();
        server.execute_cmd(class_name, kwargs);

        var top = bvr.src_el.getParent(".spt_plugin_top");
        spt.panel.refresh(top);

        spt.api.app_busy_hide();

        '''
        })

        return div





class PluginUploadRegisterWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        top.add("Plugin File: ")

        file_div = DivWdg()
        file_div.add_class("spt_plugin_file")
        top.add(file_div)
        file_div.add_style("padding: 10px")
        file_div.add("-- None Selected --")

        from tactic.ui.input import UploadButtonWdg
        upload_button = UploadButtonWdg(name="Browse")
        top.add(upload_button)

        upload_button.set_on_complete('''
            var file = spt.html5upload.get_file();
            if (!file) {
               alert('Error: file cannot be found.')
               spt.app_busy.hide();
               return;
            }

            file_name = file.name;

            try {

                var server = TacticServerStub.get();
                var class_name = 'tactic.command.PluginInstaller';
                var kwargs = {
                    'upload_file_name': file_name,
                    'path': file_name
                }
                server.execute_cmd(class_name, kwargs);

            } catch(e) {
                alert("Cannot install plugin: " + file_name);
            }

            spt.notify.show_message(file_name);
            spt.app_busy.hide();

        ''')


        return top


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



class PluginUploadRegisterCbk(Command):

    def execute(my):

        my.base_dir = Environment.get_plugin_dir()
        upload_dir = Environment.get_upload_dir()

        orig_path = my.kwargs.get("path")
        orig_path = orig_path.replace("\\", "/")

        basename = os.path.basename(orig_path)
        plugin_name, ext = os.path.splitext(basename)
        my.plugin_dir = "%s/%s" % (my.base_dir, plugin_name)

        upload_path = "%s/%s" % (upload_dir, basename)


        if not os.path.exists(upload_path):
            raise TacticException("File [%s] does not exist" % upload_path)

        if not basename.endswith(".zip"):
            raise TacticException("Plugin file requires zip extension")


        plugin_dir = "%s/%s" % (my.base_dir, plugin_name)

        # remove the plugin dir
        if os.path.exists(plugin_dir):
            shutil.rmtree(plugin_dir)
            os.makedirs(plugin_dir)


        # extract the zip file
        zip = zipfile.ZipFile(upload_path)
        info_list = zip.infolist()
        info_list.sort()

        for info in info_list:
            out_path = "%s/%s" % (my.base_dir, info.filename)

            # check if this is a directory
            if out_path.endswith("/"):
                # eliminate if it already exists
                if os.path.exists(out_path):
                    shutil.rmtree(out_path)
                os.makedirs(out_path)


        for info in info_list:
            out_path = "%s/%s" % (my.base_dir, info.filename)

            # check if this is a directory
            if out_path.endswith("/"):
                continue

            # finally make sure that the output directory exists
            out_dir = os.path.dirname(out_path)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            

            print "Extracting: ", out_path

            #out_dirname = os.path.dirname(out_path)
            #if not os.path.exists(out_dirname):
            #    os.makedirs(out_dirname)

            fout = codecs.open(out_path, 'w')
            buffer = zip.read(info.filename)
            fout.write(buffer)
            fout.close()

        # load the plugin info into the plugin table
        from tactic.command import PluginInstaller
        installer = PluginInstaller(mode='register', code=plugin_name)
        installer.execute()

 




class PluginInstallIntoProjectCbk(Command):
    '''This actually installs the plugin in to the project'''
    def execute(my):

        # get the plugin directory
        my.plugin_dir = "%s/%s" % (my.base_dir, plugin_name)

        # get the manifest path for the plugin
        manifest_path = "%s/manifest.xml" % plugin_dir
        if not os.path.exists(upload_path):
            raise TacticException("Plugin has no manifest file [%s]" % manifest_path)

        # read the manifest file
        f = codecs.open(manifest_path, 'r')
        manifest = f.read()
        f.close()


        # install the plugin into the project
        from tactic.command import PluginInstaller
        installer = PluginInstaller(manifest=manifest)
        installer.execute()

        



