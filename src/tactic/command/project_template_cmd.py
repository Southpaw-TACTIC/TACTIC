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


__all__ = ['ProjectTemplateInstallerCmd', 'ProjectTemplateCreatorCmd', 'ProjectTemplateCheckCmd']

import tacticenv

from pyasm.common import Xml, Environment, TacticException, Common
from pyasm.search import Search, SearchType
from pyasm.biz import Project

from pyasm.command import Command

import os, shutil
import re


class ProjectDeleteCmd(Command):
    def execute(self):
        # drop database pg

        # DATA
        # delete from file where project_code = 'pg'
        # delete from snapshot where project_code = 'pg'
        # delete from task where project_code = 'pg'
        # delete from work_hour where project_code = 'pg'
        # delete from note where project_code = 'pg'
        # delete from wdg_settings where project_code = 'pg'

        # configuration
        # delete from schema where code = 'pg'
        # delete from pipeline where project_code = 'pg'
        # delete from search_object where namespace = 'pg'
        pass


class ProjectTemplateCreatorCmd(Command):

    def execute(self):

        self.base_dir = self.kwargs.get("base_dir")
        if not self.base_dir:
            self.base_dir = Environment.get_template_dir()


        self.project_code = self.kwargs.get("project_code")
        if not self.project_code:
            self.project_code = Project.get_project_code()

        assert self.project_code

        # project code can be called anything, and we want to have a _template suffix for the template code
        #self.plugin_code = "%s_template" % self.project_code

        #self.template_project_code = re.sub( '_template$', '', self.plugin_code)
        self.template_project_code = self.project_code
        self.project = Project.get_by_code(self.project_code)
        if not self.project:
            raise TacticException('This project [%s] does not exist'%self.project_code)

        self.project_type = self.project.get_value("type")
        if not self.project_type:
            self.project_type = self.project_code
        Project.set_project(self.project_code)

        self.export_template()


    def export_template(self):

        xml = Xml()
        self.xml = xml

        xml.create_doc("manifest")
        manifest_node = xml.get_root_node()

        # Old implementation.  Code is now on the data node
        xml.set_attribute(manifest_node, "code", self.template_project_code)

        # dump the notification entries
        data_node = xml.create_element("data")
        xml.append_child(manifest_node, data_node)

        code_node = xml.create_element("code")
        xml.append_child(data_node, code_node)
        xml.set_node_value(code_node, self.template_project_code)

        version = self.kwargs.get("version") or ""
        version_node = xml.create_element("version")
        xml.append_child(data_node, version_node)
        xml.set_node_value(version_node, version)



        # dump the project entry
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/project['code','%s'])" % self.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/project")
        xml.set_attribute(data_node, "unique", "true")

        # dump the project_type entry
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/project['code','%s'].sthpw/project_type)" % self.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/project_type")
        xml.set_attribute(data_node, "unique", "true")


        # dump the schema entry
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/schema['code','%s'])" % self.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/schema")
        xml.set_attribute(data_node, "unique", "true")

        # find the project template search types
        namespace = self.project_type
        if not namespace or namespace == "default":
            namespace = self.project_code
        project_search_types = Search.eval("@GET(sthpw/search_object['namespace','%s'].search_type)" % namespace)

        #project_types = Search.eval("@GET(sthpw/search_object['namespace','%s'].search_type)" % self.project_code)

        # just dump the definition for data
        for search_type in project_search_types:
            data_node = xml.create_element("search_type")
            xml.append_child(manifest_node, data_node)
            xml.set_attribute(data_node, "code", search_type)


        search_types = [
            "config/custom_script",
            "config/widget_config",
            "config/naming",
            "config/client_trigger",
            "config/process",
            "config/trigger",
            "config/url",

            #"config/ingest_rule",
            #"config/ingest_session",
        ]

        for search_type in search_types:
            data_node = xml.create_element("sobject")
            xml.append_child(manifest_node, data_node)
            xml.set_attribute(data_node, "search_type", search_type)

            # find the currval 
            st_obj = SearchType.get(search_type)
            # have to call nextval() to initiate this sequence in the session in psql since Postgres 8.1
            seq_id = SearchType.sequence_nextval(search_type)
            
            seq_id = SearchType.sequence_currval(search_type)

            seq_id -= 1
            if seq_id > 0:
                SearchType.sequence_setval(search_type, seq_id)
            xml.set_attribute(data_node, "seq_max", seq_id)
            
            #xml.set_attribute(data_node, "path", "data.spt")


       



        # dump the login_groups entries
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/login_group['project_code','%s'])" % self.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/login_group")
        xml.set_attribute(data_node, "unique", "true")

        # dump the pipelines entries
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/pipeline['project_code','%s'])" % self.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/pipeline")
        xml.set_attribute(data_node, "unique", "true")

        # dump the notification entries
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/notification['project_code','%s'])" % self.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/notification")




        from plugin import PluginCreator
        creator = PluginCreator( base_dir=self.base_dir, manifest=xml.to_string(), force=True, version=version )
        creator.execute()

        self.zip_path = creator.get_zip_path()


    def get_zip_path(self):
        return self.zip_path



class ProjectTemplateInstallerCmd(Command):
    '''Install a template project thru a zip file or the unzipped folder'''
    def execute(self):

        self.new_project = self.kwargs.get("new_project")
        if self.new_project in [False, 'false']:
            self.new_project = False
        else:
            self.new_project = True


        self.mode = self.kwargs.get("mode")
        if not self.mode:
            self.mode = 'copy'

        # if a path is specified, then handle this
        self.path = self.kwargs.get("path")
        self.project_code = self.kwargs.get("project_code")
        self.is_template = self.kwargs.get("is_template")

        # check to see if the project already exists
        # FIXME: how to determine which project code? pass it in even with path kwarg for now
        project = Project.get_by_code(self.project_code)
        if self.new_project and project:
            raise TacticException("Project [%s] already exists in this installation. Exiting..." % self.project_code)

        if self.path:
            self.handle_path(self.path)



        assert self.project_code

        # determines which template to use
        self.template_code = self.kwargs.get("template_code")
        if not self.template_code:
            self.template_code = self.project_code

       

        # template code can end with _template or not depending if it's coming from a zip file
        #if self.template_code.endswith("_template"):
        
        #    self.plugin_code = self.template_code
        #else:
        #    self.plugin_code = "%s_template" % self.template_code

        #self.template_project_code = re.sub( '_template$', '', self.template_code)
        self.template_project_code = self.template_code
        self.force_database = self.kwargs.get("force_database")
    
        self.import_template()


    def get_template_dir(self, template_dir):
        '''check if it exists and return the one that does'''

        if not os.path.exists(template_dir):
            # for backward compatibility
            template_dir2 = '%s_template' %template_dir
            if not os.path.exists(template_dir2):
                return template_dir
            else:
                return template_dir2

        return template_dir




    def import_template(self):

        if self.path:
            base_dir = os.path.dirname(self.path)
        else:
            base_dir = Environment.get_template_dir()


        version = self.kwargs.get("version")
        if version:
            template_dir = "%s/%s-%s" % (base_dir, self.template_code, version)
        else:
            template_dir = "%s/%s" % (base_dir, self.template_code)

        template_dir = self.get_template_dir(template_dir)
        
        # if the directory does not exist then look for a zip file
        use_zip = False
        if not os.path.exists(template_dir):
            template_zip = "%s.zip" % (template_dir)
            if os.path.exists(template_zip):
                use_zip = True
            else:
                hint = "Please check if you have created the Template already using the Update button in the Template Project view."
                if version:
                    raise TacticException("No template found for [%s] version [%s]. %s" % (self.template_code, version, hint))
                else:
                    raise TacticException("No template found for [%s]. %s" % (self.template_code, hint))
                    



        # check to see if the database exists in the default
        # database implementation
        from pyasm.search import DbContainer, DatabaseImpl
        impl = DatabaseImpl.get()
        exists = impl.database_exists(self.project_code)

        # if the database already exists, then raise an exception
        if exists and self.new_project:
            msg = "WARNING: Database [%s] already exists" % self.project_code
            print msg
            raise TacticException(msg)


        # this is the overriding factor:
        if self.is_template == True:
            title = Common.get_display_title(self.project_code)
        elif self.is_template == False:
            title = Common.get_display_title(self.project_code)
        elif self.is_template == None:
            # these 2 is for old usage using the command line script create_template.py
            if self.template_project_code != self.project_code:
                self.is_template = False
                title = Common.get_display_title(self.project_code)
            else:
                self.is_template = True
                title = Common.get_display_title(self.template_project_code)


        # create a new project if this was desired
        if self.new_project == True:
            from create_project_cmd import CreateProjectCmd
            project_image_path = self.kwargs.get("project_image_path")

            # the project_type will get updated properly by the PluginInstaller
            # but that break the ties to the project_type entry created though,
            # which is ok
            creator = CreateProjectCmd(
                project_code=self.project_code,
                project_title=title,
                project_type=self.template_project_code,
                is_template=self.is_template,
                use_default_side_bar=False,
                project_image_path=project_image_path
            )
            creator.execute()


        # set the project
        Project.set_project(self.project_code)

        # import from a plugin
        if use_zip:
            kwargs = {
                'zip_path': template_zip,
                'code': self.project_code
            }

        else:
            kwargs = {
                'plugin_dir': template_dir
            }


        kwargs['filter_line_handler'] = self.filter_line_handler
        kwargs['filter_sobject_handler'] = self.filter_sobject_handler

        from plugin import PluginCreator, PluginInstaller
        installer = PluginInstaller( **kwargs )
        installer.execute()



    def handle_path(self, src_path):

        src_path = src_path.replace("\\", "/")

        # upload folder
        basename = os.path.basename(src_path)

        if self.mode =='copy':
            target_path = src_path
            target_dir = os.path.dirname(target_path)
        else:
            target_dir = Environment.get_upload_dir()
            target_path = "%s/%s" % (target_dir, basename)
    

        base_dir = Environment.get_template_dir()
        template_dir = "%s/%s" % (base_dir, self.project_code)
        

        if os.path.exists(template_dir):
            shutil.rmtree(template_dir)
            #raise TacticException("Template is already installed at [%s]" %template_dir)

        # unzip the file
        from pyasm.common import ZipUtil
        # this is fixed for windows if zipping doesn't use compression
        paths = ZipUtil.extract(target_path)

        # veryify that the paths extracted are the expected ones
        rootname, ext = os.path.splitext(basename)

        # check if it unzips at the templates folder directly
        unzip_at_template_dir = False
        # move the plugin zip file to the appropriate folder
        if self.mode == 'copy':
            # if they manually drop the zip file already here, skip
            if target_dir != base_dir:
                shutil.copy(target_path, base_dir)
            else:
                unzip_at_template_dir = True
        else:
            shutil.move(target_path, base_dir)


        # move unzipped files into the plugin area
        # remove any version info, only allow 1 particular version installed for now
        import re
        rootname = re.sub('(.*)(-)(\d.*)', r'\1', rootname)
        unzip_path = "%s/%s" % (target_dir, rootname)
       
        
        dest_dir = '%s/%s'%(base_dir, rootname)
        
        if not unzip_at_template_dir and os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)

            shutil.move(unzip_path, dest_dir)
        

        


    def filter_sobject_handler(self, sobject):

        search_type = sobject.get_base_search_type()

        if search_type == 'sthpw/project':
            project = Project.get_by_code(self.project_code)
            if project:
                sobject.set_value("id", project.get_id() )

            # change the code of the project
            sobject.set_value("code", self.project_code)

            title = Common.get_display_title(self.project_code)
            sobject.set_value("title", title)

            if self.is_template:
                sobject.set_value("is_template", True)
            else:
                sobject.set_value("is_template", False)

        elif search_type == 'sthpw/schema':
            sobject.set_value("code", self.project_code)

        elif search_type == 'sthpw/notification':
            sobject.set_value("project_code", self.project_code)
            sobject.set_value("code", "")

        elif search_type in ['sthpw/pipeline']:
            sobject.set_value("project_code", self.project_code)
            if self.template_project_code != self.project_code:
                # get the old code
                old_code = sobject.get_code()
                if old_code.startswith("%s/" % self.template_project_code):
                    new_code = old_code.replace("%s/" % self.template_project_code, "%s/" % self.project_code)
                else:
                    new_code = "%s/%s" % (self.project_code, old_code)
                sobject.set_value("code", new_code)

        elif search_type in ['sthpw/login_group']:
            sobject.set_value("project_code", self.project_code)
            if self.template_project_code != self.project_code:

                # get the old login_group
                for column in ['login_group', 'code']:
                    old_code = sobject.get_value(column)
                    if old_code.startswith("%s/" % self.template_project_code):
                        new_code = old_code.replace("%s/" % self.template_project_code, "%s/" % self.project_code)
                    else:
                        new_code = "%s/%s" % (self.project_code, old_code)
                    sobject.set_value(column, new_code)

                # go through the access rules and replace project
                access_rules = sobject.get_xml_value("access_rules")
                nodes = access_rules.get_nodes("rules/rule")
                for node in nodes:
                    project_code = Xml.get_attribute(node, "project")
                    if project_code and project_code != "*" and project_code == self.template_project_code:
                        Xml.set_attribute(node, "project", self.project_code)
                sobject.set_value("access_rules", access_rules.to_string())


        return sobject




    def filter_line_handler(self, path, line):
        '''NOT used now'''
        return line

        # this is only called if the project code is different from the
        # template code

        file_name = os.path.basename(path)

        if file_name in ['sthpw_project.spt']:
            # change codes to project code
            if line.startswith('''insert.set_value('code','''):
                line = '''insert.set_value('code', """%s""")\n''' % self.project_code
            elif line.startswith('''insert.set_value('title','''):
                title = Common.get_display_title(self.project_code)
                line = '''insert.set_value('title', """%s""")\n''' % title

            elif line.startswith('''insert.set_value('is_template','''):
                if self.is_template:
                    line = '''insert.set_value('is_template', """true""")\n'''
                else:
                    line = '''insert.set_value('is_template', """false""")\n'''



        elif file_name in ['sthpw_schema.spt']:
            if line.startswith('''insert.set_value('code','''):
                line = '''insert.set_value('code', """%s""")\n''' % self.project_code

        elif file_name in ['sthpw_pipeline.spt']:
            if line.startswith('''insert.set_value('project_code','''):
                line = '''insert.set_value('project_code', """%s""")\n''' % self.project_code

        return line




class ProjectTemplateUpdaterCmd(Command):

    def execute(self):

        # force every search type and sobject to be unique

        manifest_xml = ""





class ProjectTemplateCheckCmd(Command):
    '''This will check the integrity of a project to see if is suitable
    for export as a distributable project template'''

    def execute(self):

        self.project_code = self.kwargs.get("project_code")
        self.prefix = self.kwargs.get("prefix")


        self.project = Project.get_by_code(self.project_code)
        self.project_type = self.project.get_value("type")

        self.check_project()
        self.check_search_type()



    def check_project(self):


        # check that the project code starts with the prefix
        if not self.project.get_code().startswith("%s_" % self.prefix):
            raise TacticException("Project code [%s] does not start with prefix [%s]" % (self.project_code, self.prefix) )


        # check that the project type is the same as the project code
        if not self.project_code != self.project_type:
            raise TacticException("Project code [%s] does not match the project_type [%s]" % (self.project_code, self.project_type) )



    def check_search_type(self):

        # all search objects in the namespace of <project_code> should
        # start with the prefix


        search = Seach("sthpw/search_type")
        search.add_filter("namespace", self.project_type)
        search_types = search.get_sobjects()


        for search_type in search_types:
            if search_type.get_value("search_type").startswith("%s_" % self.prefix):
                raise TacticException( "sType [%s] does not start with prefix [%s]" % (search_type.get_value("search_type"), self.prefix) )





if __name__ == '__main__':

    from pyasm.security import Batch
    Batch(project_code='admin')

    #cmd = ProjectTemplateCreatorCmd(project_code='pg')
    #Command.execute_cmd(cmd)

    cmd = ProjectTemplateInstallerCmd(project_code='scrum')
    Command.execute_cmd(cmd)

    #cmd = ProjectTemplateCheckCmd(project_code='di', prefix='di')
    #Command.execute_cmd(cmd)




