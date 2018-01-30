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

__all__ = ['ProjectTemplateWdg', 'ProjectTemplateEditWdg', 'ProjectTemplateDeleteCmd', 'ProjectTemplateInstallCmd', 'ProjectTemplateDownloadCmd']

from pyasm.common import Environment, TacticException, Config
from pyasm.biz import Project
from pyasm.command import Command
from pyasm.web import DivWdg, Table
from pyasm.widget import ButtonWdg, ProdIconButtonWdg, TextWdg, TextAreaWdg, CheckboxWdg, IconWdg
from pyasm.search import Search

import os, codecs
import zipfile, shutil

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg
from tactic.ui.widget import ActionButtonWdg


class ProjectTemplateWdg(BaseRefreshWdg):

    def get_display(self):

        div = DivWdg()
        div.add_class("spt_project_template_top")
        self.set_as_panel(div)

        div.add_color("background", "background")

        upload_div = DivWdg()
        upload_div.add_style("padding: 10px")
        upload_div.add_style("width: 600px")



        # add the main layout
        table = ResizableTableWdg()
        table.add_color("color", "color")
        div.add(table)

        table.add_row()
        left = table.add_cell()
        left.add_border()
        left.add_style("min-width: 250px")
        left.add_style("height: 400px")

        left.add(self.get_templates_wdg() )

        right = table.add_cell()
        right.add_border()
        right.add_style("width: 400px")
        right.add_style("height: 400px")
        right.add_style("padding: 5px")
        right.add_class("spt_project_template_content")

        template = self.kwargs.get("template")
        if template: 
            template_dir = Environment.get_template_dir()
            template_dir = "%s/%s" % (template_dir, template)
            class_name = 'tactic.ui.app.ProjectTemplateEditWdg';
            content_div = ProjectTemplateEditWdg(template_dir=template_dir)
        else:
            content_div = DivWdg()
            content_div.add_style("margin: 40px")
            content_div.add_style("width: 300px")
            content_div.add_style("height: 150px")
            content_div.add_style("opacity: 0.7")
            content_div.add_border()
            content_div.add_color("background", "background3")
            content_div.add("<br/>"*4)
            content_div.add("No templates selected")
            content_div.add_style("text-align: center")

        right.add(content_div)

        return div



    def get_templates_wdg(self):

        div = DivWdg()
        div.add_style("padding: 5px")
        div.add_color("background", "background3")
        div.add_style("height: 100%")

        title_div = DivWdg()

        button = ActionButtonWdg(title="+", tip="Choose a Project Template file to install", size="small")
        title_div.add(button)
        button.add_style("float: right")
        button.add_style("margin-top: -6px")
        button.add_style("margin-right: -4px")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': r'''
            var applet = spt.Applet.get();
            spt.app_busy.show('Choose a Project Template file');

            var paths = applet.open_file_browser();
            var server = TacticServerStub.get();
            var cmd = "tactic.ui.app.ProjectTemplateInstallCmd";

            if (!paths.length) {
                return;
            }

            try {
                
                for (var i = 0; i < paths.length; i++) {    
                    if (!paths[i].test(/\.zip/)) {
                        spt.alert('A template file should be a zip file');
                        return;
                    }

                    server.upload_file(paths[i]);
                }

                var kwargs = {
                    paths: paths
                };
                server.execute_cmd(cmd, kwargs);

                var path = paths[0]
                path = path.replace(/\\/g, "/");
                var parts = path.split("/");
                var name = parts[parts.length-1];
                var parts2 = name.split("-");
                var name = parts2[0];


                var top = bvr.src_el.getParent(".spt_project_template_top");
                top.setAttribute("spt_template", name);
                spt.panel.refresh(top);
                spt.app_busy.hide();
                spt.notify.show_message("Project Template ["+name+"] has been installed.");
            }catch (e) {
                spt.app_busy.hide();
                spt.alert(spt.exception.handler(e));
            }

            '''
        } )




        div.add(title_div)
        title_div.add("<b>Installed Templates</b>")
        title_div.add_gradient("background", "background", 0, -10)
        title_div.add_color("color", "color3")
        title_div.add_style("margin: -5px -5px 5px -5px")
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 8px")

        templates_div = DivWdg()
        div.add(templates_div)

        templates_div.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_template',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_project_template_top");
            var content = top.getElement(".spt_project_template_content")
            var class_name = 'tactic.ui.app.ProjectTemplateEditWdg';
            var template_dir = bvr.src_el.getAttribute("spt_template_dir");
            var kwargs = {
                template_dir: template_dir
            };
            spt.panel.load(content, class_name, kwargs);
            '''
        } )
        templates_div.add_class("hand")


        bgcolor = title_div.get_color("background3")
        bgcolor2 = title_div.get_color("background3", -10)
        templates_div.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_template',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "%s")
            ''' % bgcolor2
        } )
        templates_div.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_template',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "%s")
            ''' % bgcolor
        } )





        template_dir = Environment.get_template_dir()
        if not template_dir:
            raise Exception("No template dir defined")
        #template_dir = "/home/apache/project_templates"
        dirnames = os.listdir(template_dir)

        #templates = ['scrum', 'tickets', 'vfx', 'game']
        for template in dirnames:

            path = "%s/%s" % (template_dir, template)

            if not os.path.isdir(path):
                continue


            template_div = DivWdg()
            templates_div.add(template_div)
            icon = IconWdg("View Template [%s]" % template, IconWdg.DETAILS)
            template_div.add(icon)
            template_div.add(template)
            template_div.add_style("padding: 5px 3px 5px 3px")
            template_div.add_class("spt_template")
            template_div.add_attr("spt_template_dir", path)

        return div



class ProjectTemplateEditWdg(BaseRefreshWdg):
    def get_display(self):

        top = self.top
        self.set_as_panel(top)
        top.add_style("width: 500px")

        template_dir = self.kwargs.get("template_dir")

        manifest_path = "%s/manifest.xml" % template_dir

        f = open(manifest_path)
        manifest_xml = f.read()
        f.close()

        template = os.path.basename(template_dir)


        button = ActionButtonWdg(title="Delete", tip="Delete template from installation")
        button.add_style("float: right")
        top.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'template': template,
            'cbjs_action': '''

            var template = bvr.template;
            if (!confirm("Are you sure you wish to delete the ["+template+"] template?") ) {
                return;
            }


            var cmd = "tactic.ui.app.ProjectTemplateDeleteCmd";
            var server = TacticServerStub.get();
            spt.app_busy.show("Removing Template", template)

            var kwargs = {
                'template': template
            }
            try {
                server.execute_cmd(cmd, kwargs);

                var top = bvr.src_el.getParent(".spt_project_template_top");
                spt.panel.refresh(top);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }



            spt.app_busy.hide();
            '''
        } )



        button = ActionButtonWdg(title="Save As", tip="Save template as file")
        button.add_style("float: right")
        top.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'template_dir': template_dir,
            'cbjs_action': '''
            var applet = spt.Applet.get();
            var dirname = applet.open_file_browser();
            if (!dirname) {
                return;
            }

            var class_name = 'tactic.ui.app.ProjectTemplateDownloadCmd';
            var kwargs = {
                'template_dir': bvr.template_dir
            }
            var server = TacticServerStub.get();
            var ret_val = server.execute_cmd(class_name, kwargs);
            var info = ret_val['info'];
            var filename = info['filename'];

            var env = spt.Environment.get();
            var ticket = env.get_ticket();

            var server = env.get_server_url();
            var url = server + "/assets/_cache/" + ticket + "/" + filename;
            applet.download_file(url, dirname + "/" + filename);

            applet.open_explorer(dirname);

            '''
        } )




        #button = ActionButtonWdg(title="Dump", tip="Create a template from a project")
        #button.add_style("float: right")
        #top.add(button)
        #button.add_behavior( {
        #    'type': 'click_up',
        #    'cbjs_action': '''
        #    '''
        #} )



        info_div = DivWdg()
        top.add(info_div)
        info_div.add_style("padding: 20px")

        info_div.set_unique_id()
        info_div.add_smart_style("spt_none", "font-style", "italic")
        info_div.add_smart_style("spt_none", "opacity", "0.5")

        #project = Project.get()

        # import the transaction data
        from tactic.command import PluginInstaller
        installer = PluginInstaller(manifest=manifest_xml)
        project_path = "%s/%s" % (template_dir, "sthpw_project.spt")
        jobs = installer.import_data(project_path, commit=False)
        project = jobs[0]

        project_code = project.get_code()

        info_div.add("<br/>")
        info_div.add("Template Code: <b>%s</b><br/>" % project_code)
        info_div.add("<br/>")

        info_div.add("Title: <b>%s</b><br/>" % project.get_value("title"))
        info_div.add("<br/>")


        description = project.get_value("description", no_exception=True)
        if not description:
            description = "<span class='spt_none'>None</span>"
        info_div.add("Description: %s<br/>" % description)
        info_div.add("<br/>")


        version = project.get_value("version", no_exception=True)
        if not version:
            version = "<span class='spt_none'>None</span>"
        info_div.add("Version: %s<br/>" % version)
        info_div.add("<br/>")

        status = project.get_value("status", no_exception=True)
        if not status:
            status = "<span class='spt_none'>None</span>"
        info_div.add("Status: %s<br/>" % status )
        info_div.add("<br/>")



        top.add("<span style='opacity: 0.5'>Manifest Path: %s</span>" % manifest_path)


        return top


class ProjectTemplateDeleteCmd(Command):
    def execute(self):
        template = self.kwargs.get("template")

        template_dir = Environment.get_template_dir()

        template = self.kwargs.get("template")


        from pyasm.search import FileUndo
        path = "%s/%s-1.0.0.zip" % (template_dir, template)
        if not os.path.exists(path):
            raise Exception("Path [%s] does not exists" % path)

        FileUndo.remove(path)

        path = "%s/%s" % (template_dir, template)
        FileUndo.remove(path)


class ProjectTemplateInstallCmd(Command):

    def execute(self):

        from pyasm.common import ZipUtil
        ziputil = ZipUtil()

        paths = self.kwargs.get("paths")

        upload_dir = Environment.get_upload_dir()
        template_dir = Environment.get_template_dir()

        for path in paths:
            path = path.replace("\\", "/")
            basename = os.path.basename(path)
            upload_path = "%s/%s" % (upload_dir, basename)

            if not upload_path.endswith(".zip"):
                continue

            print "upload: ", upload_path
            if not os.path.exists(upload_path):
                continue


            print "template_dir: ", template_dir
            shutil.move(upload_path, template_dir)
            to_path = "%s/%s" % (template_dir, basename)

            # unzip the file
            ziputil.extract(to_path)


class ProjectTemplateDownloadCmd(Command):
    '''prepare a template for download'''

    def execute(self):

        template_dir = Environment.get_template_dir()

        # find the 
        template_dir = self.kwargs.get("template_dir")
        if not template_dir:
            return


        path = None

        template_name = os.path.basename(template_dir)
        template_dir = os.path.dirname(template_dir)

        filenames = os.listdir(template_dir)
        for filename in filenames:
            if not filename.endswith(".zip"):
                continue

            if filename.startswith(template_name):
                path = "%s/%s" % (template_dir, filename)
                break

        if not path:
            return


        asset_dir = Environment.get_asset_dir()

        ticket = Environment.get_ticket()
        cache_dir = "%s/_cache/%s" % (asset_dir, ticket)

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        shutil.copy(path, cache_dir)

        self.info["filename"] = filename





