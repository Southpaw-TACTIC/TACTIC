###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['SyncImportWdg', 'SyncImportCmd']

from pyasm.common import jsondumps, jsonloads, TacticException, Common
from pyasm.search import SearchType
from pyasm.web import DivWdg, Table
from pyasm.widget import TextWdg, TextAreaWdg, IconWdg, RadioWdg, CheckboxWdg
from pyasm.command import Command
from pyasm.biz import Project

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg
from tactic.ui.input import TextInputWdg

import os

class SyncImportWdg(BaseRefreshWdg):

    def get_display(my):
        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_sync_import_top")
        top.add_style("width: 500px")
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("padding: 20px")

        inner = DivWdg()
        top.add(inner)

        inner.add(my.get_base_dir_wdg())

        is_refresh = my.kwargs.get("is_refresh") == 'true'


        base_dir = my.kwargs.get("base_dir")
        if base_dir:
            data = my.kwargs.get("data")
            if data:
                my.data = jsonloads(data)
            else:
                if not os.path.exists(base_dir):
                    msg_div = DivWdg()

                    inner.add("<br/>"*2)
                    inner.add(msg_div)

                    msg_div.add_style("padding: 20px 20px 30px 20px")
                    msg_div.add_color("background", "background3")
                    msg_div.add_color("color", "color")
                    msg_div.add_border()

                    icon = IconWdg("WARNING", IconWdg.WARNING)
                    msg_div.add(icon)
                    icon.add_style("float: left")

                    msg_div.add("<br/>")

                    msg_div.add("Base folder [%s] does not exist on server" % base_dir)
                    if is_refresh:
                        return inner
                    else:
                        return top


                manifest_path = "%s/tactic.txt" % base_dir
                f = open(manifest_path)
                data = f.read()
                my.data = jsonloads(data)

                inner.add( my.get_import_wdg() )

        else:
            my.data = {}

            msg_div = DivWdg()
            inner.add(msg_div)
            icon = IconWdg("", IconWdg.ARROW_UP)
            msg_div.add(icon)
            msg_div.add("Please browse or enter in a sync location")
            msg_div.add_style("padding: 20px")
            msg_div.add_style("margin: 30px")
            msg_div.add_style("text-align: center")
            msg_div.add_border()
            msg_div.add_color("background", "background3")
            msg_div.add_color("color", "color3")


        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top


    def get_base_dir_wdg(my):

        div = DivWdg()

        title = DivWdg()
        div.add(title)
        title.add("Sync Project Import: ")
        title.add_style("font-size: 14px")
        title.add_style("font-weight: bold")

        div.add("<br/>")


        base_dir = my.kwargs.get("base_dir")

        is_local = False

        if is_local:
            button = ActionButtonWdg(title="Browse")
            div.add(button)
            button.add_style("float: right")
            button.add_style("margin-top: -5px")
            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var applet = spt.Applet.get();
                var files = applet.open_file_browser();
                if (!files.length) {
                    return;
                }

                var file = files[0];

                var top = bvr.src_el.getParent(".spt_sync_import_top");
                var el = top.getElement(".spt_sync_base_dir");
                el.value = file;

                '''
            } )



        div.add("Share Location: ")


        text = TextInputWdg(name="base_dir")
        div.add(text)
        text.add_class("spt_sync_base_dir")
        text.add_style("width: 300px")
        if base_dir:
            text.set_value(base_dir)


        text.add_behavior( {
            'type': 'blur',
            'is_local': is_local,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_sync_import_top");
            var applet = spt.Applet.get();

            var value = bvr.src_el.value;
            var manifest_path = value + "/tactic.txt";


            if (!value) {
                return;
            }

            if (bvr.is_local) {

                if (!applet.exists(value)) {
                    alert('Share folder does not exist.');
                    return;
                }
                if (!applet.exists(manifest_path)) {
                    alert('Cannot find manifest file.');
                    return;
                }

                var data = applet.read_file(manifest_path);
                var json = JSON.parse(data);
                data = JSON.stringify(json);
                top.setAttribute("spt_data", data)
            }

            top.setAttribute("spt_base_dir", value)

            spt.panel.refresh(top);
            '''
        } )

        return div


    def get_import_wdg(my):
        div = DivWdg()

        if my.data:

            div.add("<br/>"*2)
            div.add("The following TACTIC share was found: ")
            div.add("<br/>"*2)

            data_input = TextAreaWdg("data")
            data_input.add_style("display: none")
            div.add(data_input)

            #print "xxxx: ", my.data
            data_str = jsondumps(my.data)
            #data_str = data_str.replace('"', "'")
            print "data: ", data_str
            data_input.set_value(data_str)




            table = Table()
            div.add(table)
            table.set_max_width()
            table.add_style("margin-left: 20px")
            table.add_style("margin-right: 20px")

            for name, value in my.data.items():
                name = Common.get_display_title(name)
                table.add_row()
                table.add_cell(name)
                table.add_cell(value)



            div.add("<br/>"*2)

            div.add( my.get_versions_wdg() )

            div.add("<br/>"*2)

            # check to see if the project exists
            project_code = my.data.get("project_code")
            project_code = my.data.get("projects")
            project = Project.get_by_code(project_code)
            #if project:
            if False:
                msg_div = DivWdg()
                div.add(msg_div)
                msg_div.add_style("padding: 20px")
                msg_div.add_color("background", "background3")
                msg_div.add_color("color", "color")
                msg_div.add_border()

                icon = IconWdg("WARNING", IconWdg.WARNING)
                msg_div.add(icon)
                icon.add_style("float: left")

                msg_div.add("The project with code [%s] already exists.  You must remove the installed project before trying to import this one." % project_code)
                return div





            if my.data.get("is_encrypted") == "true":
                div.add("The transactions in this share is encrypted.  Please provide an encryption key to decrypt the transactions<br/><br/>")
                div.add("Encryption Key: ")
                text = TextWdg("encryption_key")
                div.add(text)
                div.add("<br/>"*2)

            button = ActionButtonWdg(title="Import >>")
            button.add_style("float: right")
            div.add(button)
            div.add("<br/>"*2)
            button.add_behavior( {
                'type': 'click_up',
                'project_code': project_code,
                'cbjs_action': '''
                spt.app_busy.show("Importing Project "+bvr.project_code+"...");
                var top = bvr.src_el.getParent(".spt_sync_import_top");
                var values = spt.api.Utility.get_input_values(top, null, false);
                var cmd = "tactic.ui.sync.SyncImportCmd";
                var server = TacticServerStub.get();
                server.execute_cmd(cmd, values, {}, {use_transaction: false});
                spt.notify.show_message("Finished importing project");
                spt.app_busy.hide();
                document.location = '/tactic/'+bvr.project_code;
                '''
            } )



        return div


    def get_versions_wdg(my):

        div = DivWdg()
        div.add_class("spt_imports")

        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add("Imports found:")
        title_wdg.add_style("padding: 0px 0px 8px 0px")


        base_dir = my.kwargs.get("base_dir")
        imports_dir = "%s/imports" % base_dir
        if not os.path.exists(imports_dir):
            imports_dir = base_dir

        basenames = os.listdir(imports_dir)
        basenames.sort()
        basenames.reverse()


        div.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': "spt_import_item",
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_imports");
            var els = top.getElements(".spt_import_info");
            for ( var i = 0; i < els.length; i++) {
                spt.hide(els[i]);
            }

            var el = bvr.src_el.getElement(".spt_import_info");
            spt.show(el);
            '''
        } )



        # find all the zip files
        count = 0
        for basename in basenames:
            if not basename.endswith(".txt"):
                continue
            if basename.find("-files-") != -1:
                continue
            if basename.find("-data-") != -1:
                continue

            version_wdg = DivWdg()
            div.add(version_wdg)
            version_wdg.add_style("padding: 3px 3px 3px 12px")
            version_wdg.add_class("spt_import_item")

            radio = RadioWdg("basename")
            version_wdg.add(radio)
            radio.set_option("value", basename)
            if not count:
                radio.set_checked()


            version_wdg.add(basename)

            version_wdg.add("<br/>")



            # add info
            path = "%s/%s" % (imports_dir, basename)
            f = open(path)
            data = f.read()
            f.close()

            data = jsonloads(data)

            table = Table()
            version_wdg.add(table)
            table.add_class("spt_import_info")
            if count:
                table.add_style("display: none")
            table.set_max_width()
            table.add_style("margin-left: 40px")
            table.add_style("margin-right: 20px")



            version_wdg.add(table)
            for name, value in my.data.items():
                name = Common.get_display_title(name)
                table.add_row()
                table.add_cell(name)
                table.add_cell(value)



            count += 1


        if count == 0:
            msg_wdg = DivWdg()
            div.add(msg_wdg)
            msg_wdg.add("<i>No imports found</i>")
            msg_wdg.add_border()
            msg_wdg.add_style("padding: 20px")
            msg_wdg.add_style("padding: 10px")
            msg_wdg.add_style("text-align: center")
            msg_wdg.add_color("background", "background", -10)


        return div



class SyncImportCmd(Command):

    def execute(my):
        print "SyncImportCmd"

        # extract the version
        basename = my.kwargs.get("basename")
        root, ext = os.path.splitext(basename)
        parts = root.split("-")
        version = parts[-1]

        encryption_key = my.kwargs.get("encryption_key")
        base_dir = my.kwargs.get("base_dir")
        imports_dir = "%s/imports" % base_dir



        data = my.kwargs.get("data")
        if data:
            data = eval(data)
        else:
            data = {}

        if not data:
            return

        code = data.get("code")
        description = data.get("description")

        # NOTE: for now, we are only supporting a single project
        project_code = data.get("project")

        # look at current project ...
        current_project_code = Project.get_project_code()
        if project_code != current_project_code:
            raise Exception("Cannot load into current project.  This template must be loaded into a project called [%s]" % project_code)

        

        # NOTE: TEST to see what happens when project already exists
        # check to see if the project exists
        #project = Project.get_by_code(project_code)
        #if project:
        #    raise TacticException("Project [%s] already exists" % project_code)





        sync_mode = "file"

        is_encrypted = data.get("is_encrypted")
        if is_encrypted == "true":
            ticket = encryption_key



        # create the share
        server = SearchType.create("sthpw/sync_server")



        # default access rules are pretty open
        access_rules = """
<rules>
<rule group="project" code="%s" access="allow"/>
<rule group="search_type" code="*" access="allow"/>
</rules>
        """ % project_code
        server.set_value("access_rules", access_rules)


        server.set_value("code", code)
        server.set_value("description", description)
        server.set_value("state", "online")

        server.set_value("sync_mode", sync_mode)
        server.set_value("ticket", ticket)
        server.set_value("base_dir", base_dir)

        server.commit()




        # import the project
        import_files = True
        if import_files:
            # import files
            from tactic.ui.sync import SyncRemoteProjectCmd
            sync_import_cmd = SyncRemoteProjectCmd(
                base_dir=imports_dir,
                project_code=project_code,
                version=version

            )
            sync_import_cmd.execute()






