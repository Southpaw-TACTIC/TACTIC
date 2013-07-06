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
    def execute(my):
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

    def execute(my):

        my.base_dir = my.kwargs.get("base_dir")
        if not my.base_dir:
            my.base_dir = Environment.get_template_dir()


        my.project_code = my.kwargs.get("project_code")
        if not my.project_code:
            my.project_code = Project.get_project_code()

        assert my.project_code

        # project code can be called anything, and we want to have a _template suffix for the template code
        #my.plugin_code = "%s_template" % my.project_code

        #my.template_project_code = re.sub( '_template$', '', my.plugin_code)
        my.template_project_code = my.project_code
        my.project = Project.get_by_code(my.project_code)
        if not my.project:
            raise TacticException('This project [%s] does not exist'%my.project_code)

        my.project_type = my.project.get_value("type")
        if not my.project_type:
            my.project_type = my.project_code
        Project.set_project(my.project_code)

        my.export_template()


    def export_template(my):

        xml = Xml()
        my.xml = xml

        xml.create_doc("manifest")
        manifest_node = xml.get_root_node()

        # Old implementation.  Code is now on the data node
        xml.set_attribute(manifest_node, "code", my.template_project_code)

        # dump the notification entries
        data_node = xml.create_element("data")
        xml.append_child(manifest_node, data_node)

        code_node = xml.create_element("code")
        xml.append_child(data_node, code_node)
        xml.set_node_value(code_node, my.template_project_code)

        version = my.kwargs.get("version") or ""
        version_node = xml.create_element("version")
        xml.append_child(data_node, version_node)
        xml.set_node_value(version_node, version)



        # dump the project entry
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/project['code','%s'])" % my.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/project")
        xml.set_attribute(data_node, "unique", "true")

        # dump the project_type entry
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/project['code','%s'].sthpw/project_type)" % my.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/project_type")
        xml.set_attribute(data_node, "unique", "true")


        # dump the schema entry
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/schema['code','%s'])" % my.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/schema")
        xml.set_attribute(data_node, "unique", "true")

        # find the project template search types
        namespace = my.project_type
        if not namespace or namespace == "default":
            namespace = my.project_code
        project_search_types = Search.eval("@GET(sthpw/search_object['namespace','%s'].search_type)" % namespace)

        #project_types = Search.eval("@GET(sthpw/search_object['namespace','%s'].search_type)" % my.project_code)

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
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/login_group['project_code','%s'])" % my.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/login_group")
        xml.set_attribute(data_node, "unique", "true")

        # dump the pipelines entries
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/pipeline['project_code','%s'])" % my.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/pipeline")
        xml.set_attribute(data_node, "unique", "true")

        # dump the notification entries
        data_node = xml.create_element("sobject")
        xml.append_child(manifest_node, data_node)
        xml.set_attribute(data_node, "expression", "@SOBJECT(sthpw/notification['project_code','%s'])" % my.project_code)
        xml.set_attribute(data_node, "search_type", "sthpw/notification")




        from plugin import PluginCreator
        creator = PluginCreator( base_dir=my.base_dir, manifest=xml.to_string(), force=True, version=version )
        creator.execute()

        my.zip_path = creator.get_zip_path()


    def get_zip_path(my):
        return my.zip_path



class ProjectTemplateInstallerCmd(Command):
    '''Install a template project thru a zip file or the unzipped folder'''
    def execute(my):

        my.new_project = my.kwargs.get("new_project")
        if my.new_project in [False, 'false']:
            my.new_project = False
        else:
            my.new_project = True


        my.mode = my.kwargs.get("mode")
        if not my.mode:
            my.mode = 'copy'

        # if a path is specified, then handle this
        my.path = my.kwargs.get("path")
        my.project_code = my.kwargs.get("project_code")
        my.is_template = my.kwargs.get("is_template")

        # check to see if the project already exists
        # FIXME: how to determine which project code? pass it in even with path kwarg for now
        project = Project.get_by_code(my.project_code)
        if my.new_project and project:
            raise TacticException("Project [%s] already exists in this installation. Exiting..." % my.project_code)

        if my.path:
            my.handle_path(my.path)



        assert my.project_code

        # determines which template to use
        my.template_code = my.kwargs.get("template_code")
        if not my.template_code:
            my.template_code = my.project_code

       

        # template code can end with _template or not depending if it's coming from a zip file
        #if my.template_code.endswith("_template"):
        
        #    my.plugin_code = my.template_code
        #else:
        #    my.plugin_code = "%s_template" % my.template_code

        #my.template_project_code = re.sub( '_template$', '', my.template_code)
        my.template_project_code = my.template_code
        my.force_database = my.kwargs.get("force_database")
    
        my.import_template()


    def get_template_dir(my, template_dir):
        '''check if it exists and return the one that does'''

        if not os.path.exists(template_dir):
            # for backward compatibility
            template_dir2 = '%s_template' %template_dir
            if not os.path.exists(template_dir2):
                return template_dir
            else:
                return template_dir2

        return template_dir




    def import_template(my):

        if my.path:
            base_dir = os.path.dirname(my.path)
        else:
            base_dir = Environment.get_template_dir()


        version = my.kwargs.get("version")
        if version:
            template_dir = "%s/%s-%s" % (base_dir, my.template_code, version)
        else:
            template_dir = "%s/%s" % (base_dir, my.template_code)

        template_dir = my.get_template_dir(template_dir)

        # if the directory does not exist then look for a zip file
        use_zip = False
        if not os.path.exists(template_dir):
            template_zip = "%s.zip" % (template_dir)
            if os.path.exists(template_zip):
                use_zip = True
            else:
                raise TacticException("No template found for [%s] version [%s]" % my.template_code, version)




        # check to see if the database exists in the default
        # database implementation
        from pyasm.search import DbContainer, DatabaseImpl
        impl = DatabaseImpl.get()
        exists = impl.database_exists(my.project_code)

        # if the database already exists, then raise an exception
        if exists and my.new_project:
            msg = "WARNING: Database [%s] already exists" % my.project_code
            print msg
            raise TacticException(msg)


        # this is the overriding factor:
        if my.is_template == True:
            title = Common.get_display_title(my.project_code)
        elif my.is_template == False:
            title = Common.get_display_title(my.project_code)
        elif my.is_template == None:
            # these 2 is for old usage using the command line script create_template.py
            if my.template_project_code != my.project_code:
                my.is_template = False
                title = Common.get_display_title(my.project_code)
            else:
                my.is_template = True
                title = Common.get_display_title(my.template_project_code)


        # create a new project if this was desired
        if my.new_project == True:
            from create_project_cmd import CreateProjectCmd
            project_image_path = my.kwargs.get("project_image_path")

            # the project_type will get updated properly by the PluginInstaller
            # but that break the ties to the project_type entry created though,
            # which is ok
            creator = CreateProjectCmd(
                project_code=my.project_code,
                project_title=title,
                project_type=my.template_project_code,
                is_template=my.is_template,
                use_default_side_bar=False,
                project_image_path=project_image_path
            )
            creator.execute()


        # set the project
        Project.set_project(my.project_code)

        # import from a plugin
        if use_zip:
            kwargs = {
                'zip_path': template_zip,
                'code': my.project_code
            }

        else:
            kwargs = {
                'plugin_dir': template_dir
            }


        kwargs['filter_line_handler'] = my.filter_line_handler
        kwargs['filter_sobject_handler'] = my.filter_sobject_handler

        from plugin import PluginCreator, PluginInstaller
        installer = PluginInstaller( **kwargs )
        installer.execute()



    def handle_path(my, src_path):

        src_path = src_path.replace("\\", "/")

        # upload folder
        basename = os.path.basename(src_path)

        if my.mode =='copy':
            target_path = src_path
            target_dir = os.path.dirname(target_path)
        else:
            target_dir = Environment.get_upload_dir()
            target_path = "%s/%s" % (target_dir, basename)
    

        base_dir = Environment.get_template_dir()
        template_dir = "%s/%s" % (base_dir, my.project_code)
        

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
        if my.mode == 'copy':
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
        

        


    def filter_sobject_handler(my, sobject):

        search_type = sobject.get_base_search_type()

        if search_type == 'sthpw/project':
            project = Project.get_by_code(my.project_code)
            if project:
                sobject.set_value("id", project.get_id() )

            # change the code of the project
            sobject.set_value("code", my.project_code)

            title = Common.get_display_title(my.project_code)
            sobject.set_value("title", title)

            if my.is_template:
                sobject.set_value("is_template", True)
            else:
                sobject.set_value("is_template", False)

        elif search_type == 'sthpw/schema':
            sobject.set_value("code", my.project_code)

        elif search_type == 'sthpw/notification':
            sobject.set_value("project_code", my.project_code)
            sobject.set_value("code", "")

        elif search_type in ['sthpw/pipeline']:
            sobject.set_value("project_code", my.project_code)
            if my.template_project_code != my.project_code:
                # get the old code
                old_code = sobject.get_code()
                if old_code.startswith("%s/" % my.template_project_code):
                    new_code = old_code.replace("%s/" % my.template_project_code, "%s/" % my.project_code)
                else:
                    new_code = "%s/%s" % (my.project_code, old_code)
                sobject.set_value("code", new_code)

        elif search_type in ['sthpw/login_group']:
            sobject.set_value("project_code", my.project_code)
            if my.template_project_code != my.project_code:

                # get the old login_group
                for column in ['login_group', 'code']:
                    old_code = sobject.get_value(column)
                    if old_code.startswith("%s/" % my.template_project_code):
                        new_code = old_code.replace("%s/" % my.template_project_code, "%s/" % my.project_code)
                    else:
                        new_code = "%s/%s" % (my.project_code, old_code)
                    sobject.set_value(column, new_code)

                # go through the access rules and replace project
                access_rules = sobject.get_xml_value("access_rules")
                nodes = access_rules.get_nodes("rules/rule")
                for node in nodes:
                    project_code = Xml.get_attribute(node, "project")
                    if project_code and project_code != "*" and project_code == my.template_project_code:
                        Xml.set_attribute(node, "project", my.project_code)
                sobject.set_value("access_rules", access_rules.to_string())


        return sobject




    def filter_line_handler(my, path, line):
        '''NOT used now'''
        return line

        # this is only called if the project code is different from the
        # template code

        file_name = os.path.basename(path)

        if file_name in ['sthpw_project.spt']:
            # change codes to project code
            if line.startswith('''insert.set_value('code','''):
                line = '''insert.set_value('code', """%s""")\n''' % my.project_code
            elif line.startswith('''insert.set_value('title','''):
                title = Common.get_display_title(my.project_code)
                line = '''insert.set_value('title', """%s""")\n''' % title

            elif line.startswith('''insert.set_value('is_template','''):
                if my.is_template:
                    line = '''insert.set_value('is_template', """true""")\n'''
                else:
                    line = '''insert.set_value('is_template', """false""")\n'''



        elif file_name in ['sthpw_schema.spt']:
            if line.startswith('''insert.set_value('code','''):
                line = '''insert.set_value('code', """%s""")\n''' % my.project_code

        elif file_name in ['sthpw_pipeline.spt']:
            if line.startswith('''insert.set_value('project_code','''):
                line = '''insert.set_value('project_code', """%s""")\n''' % my.project_code

        return line




class ProjectTemplateUpdaterCmd(Command):

    def execute(my):

        # force every search type and sobject to be unique

        manifest_xml = ""





class ProjectTemplateCheckCmd(Command):
    '''This will check the integrity of a project to see if is suitable
    for export as a distributable project template'''

    def execute(my):

        my.project_code = my.kwargs.get("project_code")
        my.prefix = my.kwargs.get("prefix")


        my.project = Project.get_by_code(my.project_code)
        my.project_type = my.project.get_value("type")

        my.check_project()
        my.check_search_type()



    def check_project(my):


        # check that the project code starts with the prefix
        if not my.project.get_code().startswith("%s_" % my.prefix):
            raise TacticException("Project code [%s] does not start with prefix [%s]" % (my.project_code, my.prefix) )


        # check that the project type is the same as the project code
        if not my.project_code != my.project_type:
            raise TacticException("Project code [%s] does not match the project_type [%s]" % (my.project_code, my.project_type) )



    def check_search_type(my):

        # all search objects in the namespace of <project_code> should
        # start with the prefix


        search = Seach("sthpw/search_type")
        search.add_filter("namespace", my.project_type)
        search_types = search.get_sobjects()


        for search_type in search_types:
            if search_type.get_value("search_type").startswith("%s_" % my.prefix):
                raise TacticException( "sType [%s] does not start with prefix [%s]" % (search_type.get_value("search_type"), my.prefix) )





if __name__ == '__main__':

    from pyasm.security import Batch
    Batch(project_code='admin')

    #cmd = ProjectTemplateCreatorCmd(project_code='pg')
    #Command.execute_cmd(cmd)

    cmd = ProjectTemplateInstallerCmd(project_code='scrum')
    Command.execute_cmd(cmd)

    #cmd = ProjectTemplateCheckCmd(project_code='di', prefix='di')
    #Command.execute_cmd(cmd)




