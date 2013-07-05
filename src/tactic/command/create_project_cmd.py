###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
# Description: Actions executed when an element of an EditWdg is called to
# update an sobject.  

__all__ = ['CreateProjectCmd', 'CopyProjectCmd']


import subprocess
import os, shutil, string, types, re, zipfile

from pyasm.common import Environment, System, TacticException, Config, Common
from pyasm.search import Search, SearchType, DatabaseImpl
from pyasm.command import Command
from pyasm.biz import Project, IconCreator


__all__.append("CopyFileToAssetTempCmd")
class CopyFileToAssetTempCmd(Command):
    def execute(my):
        filename = my.kwargs.get("filename")
        ticket = my.kwargs.get("ticket")
        upload_dir = Environment.get_upload_dir(ticket=ticket)
        # can't rely on that
        #ticket = Environment.get_ticket()
        asset_temp_dir = "%s/temp/%s" % (Environment.get_asset_dir(), ticket)

        if not os.path.exists(asset_temp_dir):
            os.makedirs(asset_temp_dir)

        from_path = "%s/%s" % (upload_dir, filename)

        icon_creator = IconCreator(from_path)
        icon_creator.execute()
        icon_path = icon_creator.get_icon_path()

        to_path = "%s/%s" % (asset_temp_dir, filename)
        shutil.copy(icon_path, to_path)

        my.info = {
            "path": "/assets/temp/%s/%s" % (ticket, filename)
        }

        
class CreateProjectCmd(Command):

    def get_title(my):
        return "Create Project"

    def get_args_keys(my):
        return {
        'project_code': 'code of the new project',
        'project_title': 'title of the new project',
        'project_type': 'determines the type of project which specifies the initial schema and the naming conventions',
        #'copy_pipelines': 'flag to copy template site pipelines to project'
        }

    def check(my):
        project_code = my.kwargs.get('project_code')
        regexs = '^\d|\W'
        m = re.search(r'%s' % regexs, project_code) 
        if m:
            if isinstance(project_code, unicode):
                project_code = project_code.encode('utf-8')
            else:
                project_code = unicode(project_code).encode('utf-8')
            raise TacticException('<project_code> [%s] cannot contain special characters or start with a number.' %project_code)

        # check to see if this project already exists
        test_project = Project.get_by_code(project_code)
        if test_project:
            if test_project.get_value('s_status') == 'retired':
                raise TacticException('Project with code [%s] already exists but is retired.' %project_code)
            else:
                raise TacticException('Project with code [%s] already exists.' %project_code)

        return True

    def execute(my):

        project_code = my.kwargs.get('project_code')
        project_title = my.kwargs.get('project_title')
        project_type = my.kwargs.get('project_type')
        is_template = my.kwargs.get('is_template')

        use_default_side_bar = my.kwargs.get('use_default_side_bar')
        if use_default_side_bar in [False, 'false']:
            use_default_side_bar = False
        else:
            use_default_side_bar = True


        assert project_code
        assert project_type
        if project_type:
            # check to see if it exists
            search = Search("sthpw/project_type")
            search.add_filter("code", project_type)
            project_type_sobj = search.get_sobject()
            if not project_type_sobj:

                # just create a default one in this case if it is named
                # after the project code
                if not is_template and project_type == project_code:
                    project_type = 'default'
                    
                # create a new project type
                search = Search("sthpw/project_type")
                search.add_filter("code", project_type)
                project_type_sobj = search.get_sobject()
                if not project_type_sobj:
                    project_type_sobj = SearchType.create("sthpw/project_type")
                    project_type_sobj.set_value("code", project_type)
                    project_type_sobj.set_value("type", "simple")
                    project_type_sobj.commit()

        # set the current project to Admin
        Project.set_project("admin")


        # create a new project sobject
        project = SearchType.create("sthpw/project")
        project.set_value("code", project_code)
        project.set_value("title", project_title)
        project.set_value("type", project_type)
        # set the update of the database to current (this is obsolete)
        #project.set_value("last_db_update", "now()")
        project.set_value("last_version_update", "2.5.0.v01")

        if is_template in ['true', True, 'True']:
            project.set_value("is_template", True)
        else:
            project.set_value("is_template", False)


        if project_type != "default":
            category = Common.get_display_title(project_type)
            project.set_value("category", category)


        project.commit()
       
 

        # if there is an image, check it in
        image_path = my.kwargs.get("project_image_path")
        if image_path:
            image_path = image_path.replace("\\", "/")
            basename = os.path.basename(image_path)
            upload_dir = Environment.get_upload_dir()
            upload_path = "%s/%s" % (upload_dir, basename)
            if not os.path.exists(upload_path):
                raise TacticException("Cannot find upload image for project [%s]" % upload_path)
            file_type = 'main'

            file_paths = [upload_path]
            file_types = [file_type]

            source_paths = [upload_path]
            from pyasm.biz import IconCreator
            if os.path.isfile(upload_path):
                icon_creator = IconCreator(upload_path)
                icon_creator.execute()

                web_path = icon_creator.get_web_path()
                icon_path = icon_creator.get_icon_path()
                if web_path:
                    file_paths = [upload_path, web_path, icon_path]
                    file_types = [file_type, 'web', 'icon']

            from pyasm.checkin import FileCheckin
            checkin = FileCheckin(project, context='icon', file_paths=file_paths, file_types=file_types)
            checkin.execute()

        # find project's base_type
        base_type = project.get_base_type()

        if not base_type and project_type =='unittest':
            base_type = 'unittest'
        elif not base_type:
            base_type = 'simple'


        database = DatabaseImpl.get()
        database_type = database.get_database_type()
        if database_type == 'Oracle':
            raise TacticException("Creation of project is not supported. Please create manually")


        # check if database exists
        print "Creating database '%s' ..." % project_code
        try:
            # create the datbase
            database.create_database(project_code)
        except Exception, e:
            print str(e)
            print "WARNING: Error creating database [%s]" % project_code
            raise



        # import the appropriate schema with config first
        

        db_resource = project.get_project_db_resource()
        database.import_schema(db_resource, base_type)

        my.upgrade()

        # import the appropriate data
        database.import_default_data(db_resource, base_type)



        # import default links
        if use_default_side_bar:
            my.import_default_side_bar()


        # create specified stypes
        my.create_search_types()


        # initiate the DbContainer
        from pyasm.search import DbContainer
        DbContainer.get('sthpw')


        my.info['result'] = "Finished creating project [%s]."%project_code

        print "Done."





    def import_default_side_bar(my):
        project_code = my.kwargs.get('project_code')
        # It looks like project=XXX on SearchType.create does not work
        Project.set_project(project_code)
        config = SearchType.create("config/widget_config?project=%s" % project_code)
        config.set_value("category", "SideBarWdg")
        config.set_value("search_type", "SideBarWdg")
        config.set_value("view", "project_view")
        
        xml = '''<?xml version='1.0' encoding='UTF-8'?>
<config>
  <project_view>
    <element name='_home' title='Project Home'/>
    <element name='_client_home' title='Client Home'/>
<!--
    <element name='_my_tactic'/>
    <element name='_manage'/>
-->
  </project_view>
</config>
'''
        config.set_value("config", xml)

        config.commit()



    def upgrade(my):
        project_code = my.kwargs.get('project_code')
        # run the upgrade script (this has to be done in a separate
        # process due to possible sql errors in a transaction
        install_dir = Environment.get_install_dir()
        python = Config.get_value("services", "python")
        if not python:
            python = "python"

        impl = Project.get_database_impl()

        from pyasm.search.upgrade import Upgrade
        version = Environment.get_release_version()
        version.replace('.', '_')
        upgrade = Upgrade(version, is_forced=True, project_code=project_code, quiet=True)
        upgrade.execute()



    def create_search_types(my):
        from tactic.ui.app import SearchTypeCreatorCmd

        project_code = my.kwargs.get('project_code')

        search_types = my.kwargs.get('project_stype')
        if not search_types:
            return

        for search_type in search_types:
            if search_type == "":
                continue

            search_type = Common.get_filesystem_name(search_type)
            search_type = search_type.lower()

            if search_type.find("/") != -1:
                parts = search_type.split("/")
                namespace = parts[0]
                table = parts[1]
            else:
                namespace = project_code
                table = search_type

            search_type = "%s/%s" % (namespace, search_type)

            description = Common.get_display_title(table)
            title = description
            has_pipeline = True


            kwargs = {
                'database': project_code,
                'namespace': project_code,
                'schema': 'public',

                'search_type_name': search_type,
                'asset_description': description,
                'asset_title': title,
                'sobject_pipeline': has_pipeline,
            }

            creator = SearchTypeCreatorCmd(**kwargs)
            creator.execute()

            # add a link the side bar
            class_name = "tactic.ui.panel.ViewPanelWdg"
            display_options = {
                "class_name": class_name,
                "search_type": search_type,
                "view": "table",
                "layout": "fast_table"
            }
            element_attrs = {
                #'title': '%s List' % title
                'title': title
            }
            action_options = {}
            action_class_name = {}

            view = "definition"
            element_name = "%s_list" % table

            from pyasm.search import WidgetDbConfig
            config = WidgetDbConfig.append( "SideBarWdg", view, element_name, class_name="LinkWdg", display_options=display_options, element_attrs=element_attrs)

            view = "project_view"
            element_name = "%s_list" % table
            config = WidgetDbConfig.append( "SideBarWdg", view, element_name)




class CopyProjectFromTemplateCmd(Command):

    def execute(my):
        project_code = my.kwargs.get("project_code")
        template_code = my.kwargs.get("template_code")
        project_title = my.kwargs.get("project_title")

        # check to see if the template actually exists


        from tactic.command import ProjectTemplateInstallerCmd
        cmd = ProjectTemplateInstallerCmd(**my.kwargs)
        cmd.execute()



#
# DEPRECATED
#
class CopyProjectCmd(Command):
    '''Command to copy configuration entries to project specific databases'''

    def get_args_keys(my):
        return {
        'project_code': 'code of the new project',
        'project_title': 'title of the new project',
        'project_type': 'determines the type of project which specifies the initial schema and the naming conventions',
        'copy_project': 'project to copy from'
        }

    def check(my):
        project_code = my.kwargs.get('project_code')
        regexs = '^\d|\W'
        m = re.search(r'%s' % regexs, project_code) 
        if m:
            raise TacticException('<project_code> [%s] cannot contain special characters or start with a number.' %project_code)

        # check to see if this project already exists
        test_project = Project.get_by_code(project_code)
        if test_project:
            if test_project.get_value('s_status') == 'retired':
                raise TacticException('Project with code [%s] already exists but is retired.' %project_code)
            else:
                raise TacticException('Project with code [%s] already exists.' %project_code)

        return True


    def execute(my):

        project_code = my.kwargs.get("project_code")
        project_title = my.kwargs.get("project_title")
        src_project_code = my.kwargs.get("src_project")
        assert(project_code)
        assert(src_project_code)

        src_project = Project.get_by_code(src_project_code)
        assert(src_project)

        project_type = my.kwargs.get("project_type")
        if not project_type:
            project_type = src_project.get_value("type")

        project = Project.get()
        # look to see if there are any project specific search types
        has_project_stypes = False
        if project_code != project_type:
            search = Search("sthpw/search_object")
            search.add_filter("namespace", project_code)
            if search.get_count():
                has_project_stypes = True





        # copy from another project
        install_dir = Environment.get_install_dir()
        copy_script = "%s/src/bin/util/create_project_from_template.py" % install_dir
        if not os.path.exists(copy_script):
            raise TacticException("Copy script does not exist in [%s]" % copy_script)
        python_exec = Config.get_value("services", "python") 

        # do not do a search and replace if there are no project specific
        # stypes
        if has_project_stypes:
            cmd = '''%s %s -c -w -s %s -n %s -t''' % (python_exec, copy_script, src_project_code, project_code)
        else:
            cmd = '''%s %s -s %s -n %s -t''' % (python_exec, copy_script, src_project_code, project_code)

        #os.system(cmd)
        cmd_list = cmd.split(' ')
        cmd_list.append(project_title)

        print ' '.join(cmd_list)
        program = subprocess.Popen(cmd_list, shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        program.wait()
        value = program.communicate()
        err = None
        if value:
            err = value[1]
       
        if err:
            raise TacticException("Error found in project creation: %s" %err)

        return



