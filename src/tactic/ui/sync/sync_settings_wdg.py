###########################################################
#
# Copyright (c) 2005-2011, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['SyncSettingsWdg','SyncRemoteProjectCmd','SyncCreateTemplateCmd', 'SyncServerAddWdg','SyncServerAddCbk']


from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment, Xml, Common, Environment, Config, TacticException
from pyasm.biz import Project
from pyasm.search import Search, SearchType
from pyasm.web import DivWdg, Table, WebContainer
from pyasm.widget import TextWdg, SelectWdg, TextAreaWdg, IconWdg, CheckboxWdg
from pyasm.command import Command

from tactic.ui.widget import ActionButtonWdg
from tactic.ui.input import TextInputWdg

from tactic_client_lib import TacticServerStub

import os, shutil


class SyncSettingsWdg(BaseRefreshWdg):

    def get_value(my, name):
        web = WebContainer.get_web()
        value = web.get_form_value(name)
        if not value:
            value = my.kwargs.get(value)
        return value

    def get_display(my):

        top = my.top
        my.set_as_panel(top)

        is_refresh = my.kwargs.get("is_refresh")

        inner = DivWdg()
        top.add(inner)

        title = DivWdg()
        inner.add(title)

        inner.add_class("spt_sync_settings_top")

        inner.add_style("padding: 20px")
        inner.add_color("background", "background")


        server_code = my.get_value("server")

        # get all of the defined servers
        search = Search("sthpw/sync_server")
        servers = search.get_sobjects()
        server_codes = [x.get_code() for x in servers]
        if not server_codes and not server_code:
            msg_div = DivWdg()
            msg_div.add("No servers defined.  Please add a server")
            inner.add(msg_div)
            return top


        if len(server_codes) == 1 or not server_code:
            server_code = server_codes[0]


        select = SelectWdg("server")
        inner.add("Server: ")
        inner.add(select)
        select.set_option("values", server_codes)
        if server_code:
            select.set_value(server_code)
        else:
            return top

        select.add_behavior( { 
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_sync_settings_top");
            spt.panel.refresh(top);
            '''
        } )



        project = Project.get()
        project_code = project.get_code()
        if project_code == "admin":
            project_code = ""


        inner.add( my.get_install_wdg(server_code, project_code) )
        inner.add( my.get_dump_wdg(server_code, project_code) )

        if is_refresh:
            return inner
        else:
            return top


    def get_dump_wdg(my, server_code, project_code):

        div = DivWdg()
        div.add_style("padding: 30px")
        div.add_style("margin: 10px")
        div.add_border()
        div.add_style("width: 300px")
        div.add_class("spt_sync_dump_top")
        div.add_color("background", "background3")



        # Dump Project

        search = Search("sthpw/project")
        search.add_filters("code", ["admin","unittest"], op='not in')
        projects = search.get_sobjects()
        project_codes = [x.get_code() for x in projects]


        div.add("This will dump out the current state of the project and can be reimported back in on a remote server<br/><br/>")

        div.add("Project: ")
        text_wdg = SelectWdg("project_to_dump")
        text_wdg.add_empty_option("-- Select --")
        text_wdg.set_option("values", project_codes)
        if project_code:
            text_wdg.set_value(project_code)
        text_wdg.add_class("spt_project")
        div.add(text_wdg)

        div.add("<br/>"*2)


        button = ActionButtonWdg(title="Dump")
        div.add(button)
        button.add_style("margin-left: auto")
        button.add_style("margin-right: auto")
        button.add_behavior( {
            'type': 'click_up',
            'server': server_code,
            'project_code': project_code,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_sync_dump_top");
            var text = top.getElement(".spt_project");
            var project_code = text.value;


            if (!project_code) {
                spt.alert("No project specified");
                return
            }

            spt.app_busy.show("Dumping "+project_code+" Project ...") ;

            var cmd = 'tactic.ui.sync.SyncCreateTemplateCmd';
            var server = TacticServerStub.get();

            var kwargs = {
                'server': bvr.server,
                'project_code': project_code
            }
            server.execute_cmd(cmd, kwargs);

            var top = bvr.src_el.getParent(".spt_sync_settings_top");
            spt.panel.refresh(top);

            spt.app_busy.hide();

            '''
        } )


        return div




    def get_install_wdg(my, server_code, project_code):

        div = DivWdg()
        div.add_style("padding: 30px")
        div.add_style("margin: 10px")
        div.add_border()
        div.add_style("width: 300px")
        div.add_class("spt_sync_install_top")
        div.add_color("background", "background3")


        server = Search.get_by_code("sthpw/sync_server", server_code)
        if not server:
            div.add("No server [%s] exists in this installation" % server_code)
            return div

        if server.get_value("sync_mode") == "file":
            base_dir = server.get_value("base_dir")
        else:
            div.add("No base directory defined")
            return div


        if not os.path.exists(base_dir):
            div.add("Base Directory [%s] does not exist" % base_dir)
            return div



        dirnames = os.listdir(base_dir)
        templates_set = set()
        for dirname in dirnames:
            if dirname.endswith(".zip"):
                if dirname.find("_template-") != -1:
                    parts = dirname.split("_template-")
                    templates_set.add(parts[0])
                

        project_codes = list(templates_set)
        project_codes.sort()

        if not project_codes:
            div.add("There are no templates available.<br/><br/>")


        else:

            div.add("This will import a project template that has been dumped out.  The project cannot currently exist in the database.<br/><br/>")


            div.add("Available Templates: ")
            text_wdg = SelectWdg("server")
            text_wdg.set_option("values", project_codes)
            if project_code:
                text_wdg.set_value(project_code)
            text_wdg.add_class("spt_project")
            div.add(text_wdg)

            div.add("<br/>"*2)

            # This will create a project template dynamically and provide it for
            # download?
            button = ActionButtonWdg(title="Install")
            div.add(button)
            button.add_style("margin-left: auto")
            button.add_style("margin-right: auto")
            button.add_behavior( {
                'type': 'click_up',
                'server': server_code,
                'project_code': project_code,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_sync_install_top");
                var text = top.getElement(".spt_project");
                var project_code = text.value ;

                spt.app_busy.show("Importing Project", "from remote server ["+bvr.server+"].");

                try {
                    var cmd = 'tactic.ui.sync.SyncRemoteProjectCmd';
                    var kwargs = {
                        'server': bvr.server,
                        'project_code': project_code
                    }
                    var server = TacticServerStub.get();
                    server.execute_cmd(cmd, kwargs);
                }
                catch(e) {
                    alert("Error importing project: " + e);
                }
                spt.app_busy.hide();
                '''
            } )

        return div




class SyncCreateTemplateCmd(Command):
    def execute(my):

        import datetime
        now = datetime.datetime.now()
        version = now.strftime("%Y%m%d_%H%M%S")


        project_code = my.kwargs.get("project_code")
        if project_code:
            project = Project.get_by_code(project_code)
        else:
            project = Project.get()
        project_code = project.get_code()

        server_code = my.kwargs.get("server")
        assert server_code

        if not isinstance(server_code, basestring):
            server_code = server_code.get_value("code")


        base_dir = my.kwargs.get('base_dir')
        ticket = Environment.get_ticket()
        tmp_dir = "%s/sync_%s" % (Environment.get_tmp_dir(), ticket)
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)


        server = Search.get_by_code("sthpw/sync_server", server_code)
        if server.get_value("sync_mode") == "file":
            if not base_dir:
                base_dir = server.get_value("base_dir")

        else:
            raise Exception("sync mode [%s] not support" % sync_mode)
            # FIXME: not sure if this is valid anymore
            asset_dir = Environment.get_asset_dir()
            base_dir = "%s/_temp" % asset_dir


        # create the project template
        from tactic.command import ProjectTemplateCreatorCmd
        cmd = ProjectTemplateCreatorCmd(project_code=project_code, version=version, base_dir=tmp_dir)
        cmd.execute()

        project_path = cmd.get_zip_path()


        # create zip of the project files
        from pyasm.common import ZipUtil
        zip_util = ZipUtil()
        asset_dir = Environment.get_asset_dir()
        project_dir = "%s/%s" % (asset_dir, project_code)

        zip_dir = "%s/%s" % (tmp_dir, project_code)
        file_path = "%s-files-%s.zip" % (zip_dir, version)

        if os.path.exists(file_path):
            os.unlink(file_path)
        zip_util.zip_dir2(project_dir, zip_path=file_path)




        # create a manifest for all the data in the project.
        xml = Xml()
        my.xml = xml

        xml.create_doc("manifest")
        manifest_node = xml.get_root_node()
        xml.set_attribute(manifest_node, "code", "%s-data" % project_code)

        search_types = project.get_search_types()

        # just dump the data
        for search_type in search_types:
            data_node = xml.create_element("sobject")
            xml.append_child(manifest_node, data_node)
            xml.set_attribute(data_node, "search_type", search_type.get_value("search_type"))


        # dump the note entries
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/note['project_code','%s'])" % project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/note")


        # dump the task entries
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/task['project_code','%s'])" % project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/task")


        # dump the snapshot entries
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/snapshot['project_code','%s'])" % project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/snapshot")


        # dump the file entries
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/file['project_code','%s'])" % project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/file")


        manifest = xml.to_string()


        # create a virtual plugin sobject
        from tactic.command import PluginCreator
        plugin = SearchType.create("config/plugin")
        plugin.set_value("version", version)
        plugin.set_value("code", "%s_project" % project_code)

        creator = PluginCreator( base_dir=tmp_dir, plugin=plugin, manifest=manifest, version=version )
        creator.execute()

        data_path = creator.get_zip_path()




        # move the files to the appropriate base_dir
        import shutil

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)


        if os.path.exists(project_path):
            basename = os.path.basename(project_path)
            if os.path.exists("%s/%s" % (base_dir, basename)):
                os.unlink("%s/%s" % (base_dir, basename))
            shutil.move(project_path, base_dir)

        if os.path.exists(data_path):
            basename = os.path.basename(data_path)
            if os.path.exists("%s/%s" % (base_dir, basename)):
                os.unlink("%s/%s" % (base_dir, basename))
            shutil.move(data_path, base_dir)

        if os.path.exists(file_path):
            basename = os.path.basename(file_path)
            if os.path.exists("%s/%s" % (base_dir, basename)):
                os.unlink("%s/%s" % (base_dir, basename))
            shutil.move(file_path, base_dir)


        shutil.rmtree(tmp_dir)


        my.handle_manifest(base_dir, project_code, version)



    def handle_manifest(my, base_dir, project_code, version):

        import datetime

        manifest_path = "%s/%s-manifest-%s.txt" % (base_dir, project_code, version)


        # find the last transaction for this project
        search = Search("sthpw/transaction_log")
        search.add_filter("namespace", project_code)
        search.add_order_by("timestamp desc")
        last_transaction = search.get_sobject()
        if last_transaction:
            transaction_code = last_transaction.get_code()
            # get rid of the unicode because pprint doesn't remove it
            transaction_code = str(transaction_code)
        else:
            transaction_code = ""


        f = open(manifest_path, 'wb')

        manifest = {
          "code": project_code,
          "description": "???",
          "version": version,
          "last_transaction": transaction_code,
          "is_encrypted": "true",
          "date_created": datetime.datetime.now(),
          "created_by": "???" 
        }

        from pyasm.common import jsondumps
        #f.write(Common.get_pretty_print(manifest))
        f.write(jsondumps(manifest))
        f.close()






class SyncRemoteProjectCmd(Command):

    def execute(my):
        # This will go to a registered remote server and get the project

        #server_code = my.kwargs.get("server")
        #assert server_code
        ## get the registered server
        #server = Search.get_by_code("sthpw/sync_server", server_code)
        #assert server


        project_code = my.kwargs.get("project_code")
        assert project_code

        version = my.kwargs.get("version")
        if not version:
            version = "1.0.0"


        # build the project names
        template_name = "%s-%s.zip" % (project_code, version)
        data_name = "%s-data-%s.zip" % (project_code, version)
        file_name = "%s-files-%s.zip" % (project_code, version)

        tmp_dir = Environment.get_tmp_dir()
        to_dir = tmp_dir
        to_template_path = "%s/%s-%s.zip" % (to_dir, project_code, version)
        to_data_path = "%s/%s-data-%s.zip" % (to_dir, project_code, version)
        to_file_path = "%s/%s-files-%s.zip" % (to_dir, project_code, version)




        #sync_mode = server.get_value("sync_mode")
        sync_mode = "file"

        if sync_mode == "file":
            base_dir = my.kwargs.get("base_dir")

            from_template_path = "%s/%s" % (base_dir, template_name)
            from_data_path = "%s/%s" % (base_dir, data_name)
            from_file_path = "%s/%s" % (base_dir, file_name)
            to_file_path = from_file_path

            # copy the files 
            # ???? why are we copying here?
            shutil.copy(from_template_path, to_template_path)
            shutil.copy(from_data_path, to_data_path)

        else:


            # TEST TEST TEST
            ticket = server.get_value("server")

            remote_server = TacticServerStub(
                protocol='xmlrpc',
                server=server,
                project=project_code,
                #user=user,
                #password=password,
                ticket=ticket,
            )


            class_name = 'tactic.ui.sync.SyncCreateTemplateCmd'
            kwargs = {
                'project_code': project_code
            }
            remote_server.execute_cmd(class_name, kwargs)

            base_url = "http://%s/assets/_temp/" % server


            # download and install the files


            from_template_path = "%s/%s_template-%s.zip" % (base_url, project_code, version)
            from_data_path = "%s/%s_data-%s.zip" % (base_url, project_code, version)

            remote_server.download(from_template_path, to_dir)
            remote_server.download(from_data_path, to_dir)



        # This makes the pretty big assumption that this is an official template
        if not os.path.exists(to_template_path):
            raise Exception("Path [%s] does not exist" % to_template_path)

        template_code = project_code

        try:
            new_project = False

            from tactic.command import ProjectTemplateInstallerCmd

            cmd = ProjectTemplateInstallerCmd(project_code=project_code, path=to_template_path,template_code=template_code, new_project=new_project, version=version)
            cmd.execute()

            Project.set_project(project_code)
            project = Project.get()

            # NOTE: this avoids breaking on search.py, line 203, where it checks
            # for tables.  The caching mechanism for what tables are in the
            # database need to be refreshed once a template is imported
            from pyasm.search import DatabaseImpl, DbContainer
            DatabaseImpl.clear_table_cache()


            # import from a plugin
            kwargs = {
                #'base_dir': base_dir,
                #'manifest': my.xml.to_string(),
                'code': "%s_data" % project_code,
                'zip_path': to_data_path,
            }
     

            from tactic.command import PluginInstaller
            cmd = PluginInstaller(**kwargs)
            cmd.execute()



            # create zip of the project files
            if os.path.exists(to_file_path):
                from pyasm.common import ZipUtil
                zip_util = ZipUtil()
                asset_dir = Environment.get_asset_dir()
                to_file_dir = os.path.dirname(to_file_path)
                zip_util.extract(to_file_path, base_dir=asset_dir)





        except Exception as e:
            print("Error: ", str(e))
            raise




class SyncServerAddWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_color("background", "background")
        top.add_border()
        top.add_style("padding: 10px")
        top.add_style("font-size: 12px")

        from tactic.ui.container import WizardWdg

        title = DivWdg()
        title.add("Share Project")


        wizard = WizardWdg(title=title, submit_title="Save", command="tactic.ui.sync.SyncServerAddCbk")

        top.add(wizard)


        #wizard.add(my.get_local_wdg(), "Local")
        wizard.add(my.get_info_wdg(), "Info")
        wizard.add(my.get_sync_mode_wdg(), "Mode")
        #wizard.add(my.get_export_wdg(), "Export")
        #wizard.add(my.get_security_wdg(), "Security")

        return top


    def get_local_wdg(my):

        div = DivWdg()

        server = Config.get_value("install", "server")
        if not server:

            msg_div = DivWdg()
            msg_div.add( IconWdg("No local prefix set", IconWdg.WARNING) )
            msg_div.add("WARNING: No local server prefix set.  This will allow transactions to be merged properly with remote servers.  Without a local prefix, it is highly likely that transactions will conflict")


            msg_div.add("<br/>"*2)


            text = TextWdg("local_prefix")
            change_div = DivWdg()
            msg_div.add(change_div)
            change_div.add("Set Local Prefix: ")
            change_div.add(text)




        else:
            msg_div = DivWdg()
            msg_div.add( IconWdg("No local prefix set", IconWdg.CREATE) )
            msg_div.add("Local server set to [%s]" % server)

        msg_div.add_style("padding: 30px")
        msg_div.add_style("width: 80%")
        msg_div.add_color("background", "background3")
        msg_div.add_border()
        msg_div.add_style("text-align: center")

        div.add(msg_div)

        return div


    def get_info_wdg(my):

        div = DivWdg()

        div.add("<b>Create a share</b>")
        div.add("<br/>"*2)

        table = Table()
        div.add(table)
        table.add_style("margin-left: 15px")


        table.add_row()
        td = table.add_cell("Share Code: ")
        td.add_style("vertical-align: top")
        text = TextWdg("code")
        table.add_cell(text)
        text.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var value = bvr.src_el.value;
            if (!value) {
                return;
            }
            var server = TacticServerStub.get();
            var expr = "@SOBJECT(sthpw/sync_server['code','"+value+"'])";
            var test = server.eval(expr);
            if (test.length > 0) {
                spt.alert("Share ["+value+"] already exists.");
                bvr.src_el.value = "";
                bvr.src_el.focus();
            }
            '''
        } )
        tr, td = table.add_row_cell()
        msg_div = DivWdg()
        td.add(msg_div)
        msg_div.add("The share code is used as a prefix for all transactions and allows TACTIC to separate transactions from each location.  By convention, these codes should be a short initial (ie: ABC).")
        msg_div.add_style("margin: 10px 20px 20px 20px")


        


        table.add_row()
        table.add_row_cell("&nbsp;")


        table.add_row()
        td = table.add_cell("Description: ")
        td.add_style("vertical-align: top")
        text = TextAreaWdg("description")
        td = table.add_cell(text)


        #table.add_row()
        #table.add_cell("Auth Ticket: ")
        #text = TextWdg("ticket")
        #table.add_cell(text)


        return div


    def get_security_wdg(my):

        div = DivWdg()
        div.add_class("spt_security")

        div.add("A server can sync either be scoped for a single project or all projects.  Transactions that occur in the admin project never get synced.")

        div.add("<br/>"*2)

        div.add("Project: ")

        search = Search("sthpw/project")
        search.add_filters("code", ['admin','unittest'], op='not in')
        search.add_order_by("title")
        projects = search.get_sobjects()

        select = SelectWdg("projects")
        div.add(select)
        labels = [x.get_value("title") for x in projects]
        values = [x.get_value("code") for x in projects]

        project_code = Project.get_project_code()
        if project_code != 'admin':
            select.set_value(project_code)
        select.set_option("labels", labels)
        select.set_option("values", values)
        select.add_empty_option("-- All --")


        div.add("<br/>"*2)

        return div



    def get_sync_mode_wdg(my):

        div = DivWdg()
        div.add_class("spt_sync_mode")

        div.add("Share Mode: ")
        select = SelectWdg("sync_mode")
        div.add(select)
        select.set_option("values", "file|xmlrpc")

        select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_sync_mode");
            var value = bvr.src_el.value;
            var xmlrpc_el = top.getElement(".spt_xmlrpc_mode");
            var file_el = top.getElement(".spt_file_mode");

            if (value == 'xmlrpc') {
                spt.show(xmlrpc_el);
                spt.hide(file_el);
            }
            else {
                spt.hide(xmlrpc_el);
                spt.show(file_el);
            }
            '''
        } )

        div.add( my.get_xmlrpc_mode_wdg() )
        div.add( my.get_file_mode_wdg() )

        return div


    def get_xmlrpc_mode_wdg(my):
        div = DivWdg()
        div.add_style("margin-top: 15px")
        div.add_style("margin-bottom: 15px")
        div.add_class("spt_xmlrpc_mode")
        div.add_style("display: none")

        div.add("Server: ")
        text = TextWdg("host")
        text.add_style("width: 300px")
        div.add(text)

        div.add("<br/>"*2)

        div.add("Each server requires an authentication that will be used to enable sending transactions to the remote server.  The remote server must have this ticket defined in order to recieve the transaction.")

        div.add("<br/>"*2)
        div.add("Authentication Ticket: ")
        text = TextWdg("auth_ticket")
        text.add_style("width: 300px")
        div.add(text)


        return div



    def get_file_mode_wdg(my):
        div = DivWdg()
        div.add_style("margin-top: 15px")
        div.add_style("margin-bottom: 15px")
        div.add_class("spt_file_mode")

        # drop folder
        div.add("A writable folder is required.  This is the folder that sync will drop the transacton file into.  This folder should be common to all shares that need to have recieve the transactions.")

        div.add("<br/>"*2)

        # only valid for standalone
        browser = WebContainer.get_web().get_browser()
        if browser == 'Qt':
            button = ActionButtonWdg(title="Browse")
            div.add(button)
            button.add_style("float: right")

            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var applet = spt.Applet.get();
                var files = applet.open_file_browser();
                if (files.length == 0) {
                    return;
                }

                var dir = files[0];
                if (!applet.is_dir(dir)) {
                    spt.alert("Please select a folder");
                    return;
                }
                var top = bvr.src_el.getParent(".spt_file_mode");
                var folder_el = top.getElement(".spt_sync_folder");
                folder_el.value = dir;

                '''
            } )

        div.add("Sync Folder: ")
        text = TextInputWdg(name="sync_folder")
        text.add_class("spt_sync_folder")
        text.add_style("width: 300px")
        div.add(text)

        #div.add("<br/>"*2)
        #div.add("Set whether this transaction is plaintext, zipped or encrypted.")

        div.add("<br/>"*3)
        div.add("The transactions can be encrypted with an encryption ticket.  All shares must set this to be the same value in order for the transaction to be appropriately encrypted and decrypted.")


        div.add("<br/>"*2)
        div.add("Encrypt Transactions? ")
        checkbox = CheckboxWdg("is_encrypted")
        div.add(checkbox)
        checkbox.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_file_mode");
            var el = top.getElement(".spt_encrypt");
            if (el.getStyle("display") == "none") {
                el.setStyle("display", "");
            }
            else {
                el.setStyle("display", "none");
            }
            '''
        } )



        #div.add("Set whether this transaction is plaintext, zipped or encrypted.")
        encrypt_div = DivWdg()
        encrypt_div.add_class("spt_encrypt")
        div.add(encrypt_div)
        encrypt_div.add_style("display: none")
        encrypt_div.add_style("padding: 30px 20px 30px 20px")
        encrypt_div.add("Encryption Key: ")
        text = TextWdg("encrypt_key")
        text.add_style("width: 300px")
        encrypt_div.add(text)

        #div.add(my.get_ticket_wdg())


        return div


    def get_export_wdg(my):

        div = DivWdg()

        """
        # get the sync folder and dynamically load in the project
        #base_dir = "C:/Users/Southpaw/Dropbox/sync_share_folder"
        base_dir = "/home/apache/rsync"
        project_codes = ['game']
        project_codes.sort()
        project_code = "game"
        server = "FL"
        server_code = "FL"
        """

        div.add("This will export out the current state of the project and can be reimported back in on a remote server<br/><br/>")

        div.add( my.get_security_wdg() )

        export_div = DivWdg()
        div.add(export_div)
        export_div.add_style("margin: 30px")

        checkbox = CheckboxWdg() 
        export_div.add(checkbox)
        export_div.add("&nbsp;"*2)
        export_div.add("Export template")
        export_div.add("<br/>"*2)
        checkbox = CheckboxWdg() 
        export_div.add(checkbox)
        export_div.add("&nbsp;"*2)
        export_div.add("Export data")
        export_div.add("<br/>"*2)
        checkbox = CheckboxWdg() 
        export_div.add(checkbox)
        export_div.add("&nbsp;"*2)
        export_div.add("Export files")
        export_div.add("<br/>"*2)


        return div



class SyncServerAddCbk(Command):

    def get_value(my, name):
        value = my.kwargs.get(name)
        if value:
            return value[0]
        else:
            return ""

    def execute(my):

        # save prefix
        local_prefix = my.get_value("local_prefix")
        my.server_prefix = Config.get_value("install", "server")

        if not local_prefix and not my.server_prefix:
            raise TacticException("Cannot have empty local server prefix")

        if local_prefix and local_prefix != my.server_prefix:
            Config.set_value("install", "server", local_prefix)

            Config.save_config()

        my.project_code = my.get_value("project")
        if not my.project_code:
            my.project_code = Project.get_project_code()


        # create a share
        share = SearchType.create("sthpw/sync_server")
        my.handle_info(share)
        my.handle_sync_mode(share)

        share.commit()

        #my.handle_share_project(share)
        #my.handle_manifest(share)


    def handle_share_project(my, share):

        create_template = SyncCreateTemplateCmd(server=share,project_code=my.project_code)
        create_template.execute()



    def handle_info(my, share):

        code = my.get_value("code")
        if not code:
            raise TacticException("Cannot have empty code")
        share.set_value("code", code)


        description = my.get_value("description")
        if description:
            share.set_value("description", description)
            

        share.set_value("state", "online")


        project_code = my.get_value("project")
        if not project_code or project_code == "__all__":
            project_code = "*"


        # default access rules are pretty open
        access_rules = """
<rules>
<rule group="project" code="%s" access="allow"/>
<rule group="search_type" code="*" access="allow"/>
</rules>
        """ % my.project_code
        share.set_value("access_rules", access_rules)



    def handle_sync_mode(my, share):

        sync_mode = my.get_value("sync_mode")
        share.set_value("sync_mode", sync_mode)

        if sync_mode == 'file':
            ticket = my.get_value("encrypt_key")
            if not ticket:
                ticket = "tactic"

            sync_folder = my.get_value("sync_folder")
            assert(sync_folder)
            share.set_value("base_dir", sync_folder)


            share.set_value("ticket", ticket)
        else:

            host = my.get_value("host")
            if not host:
                raise TacticException("Must defined a host")
            share.set_value("host", host)

            ticket = my.get_value("auth_ticket")
            if not ticket:
                raise TacticException("Must defined a ticket")

            share.set_value("ticket", ticket)


    def handle_manifest(my, share):

        import datetime

        sync_folder = my.get_value("sync_folder")
        if not os.path.exists(sync_folder):
            os.makedirs(sync_folder)

        manifest_path = "%s/tactic.txt" % sync_folder


        """
        # find the last transaction for this project
        project_code = my.get_value("projects")
        search = Search("sthpw/transaction_log")
        search.add_filter("namespace", project_code)
        search.add_order_by("timestamp desc")
        last_transaction = search.get_sobject()
        if last_transaction:
            transaction_code = last_transaction.get_code()
            # get rid of the unicode because pprint doesn't remove it
            transaction_code = str(transaction_code)
        else:
            transaction_code = ""
        """


        f = open(manifest_path, 'wb')

        manifest = {
          "code": str(share.get_code()),
          "description": share.get_value('description'),
          #"last_transaction": transaction_code,
          "is_encrypted": "true",
          "date_created": datetime.datetime.now(),
          "created_by": my.server_prefix,
          "project": my.project_code
        }

        from pyasm.common import jsondumps
        #f.write(Common.get_pretty_print(manifest))
        f.write(jsondumps(manifest))
        f.close()




