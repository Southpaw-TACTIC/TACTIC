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
#

__all__ = ['DirNaming']

'''Base class for all directory structures'''

import re, os, types

from pyasm.common import Common, Config, Container, Environment, TacticException
from pyasm.search import SearchType, Search
from project import Repo, RemoteRepo, Project
from snapshot import Snapshot
from naming import NamingUtil, Naming
from preference import PrefSetting


class DirNaming(object):

    def __init__(my, sobject=None, snapshot=None, file_type=None, file_object=None):
        my.sobject = sobject
        my.snapshot = snapshot
        my._file_object = file_object

        my.file_type = file_type
        my.create = False
        my.protocol = "http"
        my.global_context = None

        my.naming_expr = None

    def set_sobject(my, sobject):
        my.sobject = sobject

    def set_snapshot(my, snapshot):
        my.snapshot = snapshot

    def set_file_object(my, file_object):
        my._file_object = file_object

    def set_file_type(my, file_type):
        if not file_type and my.snapshot:
            # get from snapshot's first file node
            file_type = my.snapshot.get_file_type()
            #assert file_type
        my.file_type = file_type

    def get_file_type(my):
        return my.file_type

    def set_create(my, create):
        my.create = create

    def set_protocol(my, protocol):
        my.protocol = protocol

    def set_naming(my, naming_expr):
        my.naming_expr = naming_expr


    def get_web_dir(my):
        my.protocol = "http"
        return my.get_dir()
        
    def get_lib_dir(my):
        my.protocol = "file"
        return my.get_dir()


    def _get_recorded_dir(my):
        '''get the recorded dir info in the file table'''
        dir_dict = {}
        file_type = my.get_file_type()
        if file_type and my.snapshot:
            # This is for inplace checkin ... should use relative_dir
            # if possible.
            #
            # if there is a snapshot check the file to see if naming conventions
            # are even used
            if not my.snapshot.get_use_naming_by_type(file_type):
                relative_dir = my._file_object.get_value("relative_dir")
                if relative_dir:
                    dir_dict['relative_dir'] = relative_dir
                checkin_dir = my._file_object.get_value("checkin_dir")
                if checkin_dir:
                    dir_dict['inplace_dir'] = checkin_dir

                return dir_dict
 

    
        # if this is just querying and not sandbox, use relative dir
        if my._file_object and my.protocol != 'sandbox':
            relative_dir = my._file_object.get_value("relative_dir")
            if relative_dir:
                dir_dict['relative_dir'] = relative_dir
                return dir_dict
       
        return dir_dict

    def _init_file_object(my):
        '''initialize the file object. Some fields are still empty before checkin postprocess'''

        # if set externally already, skip and return
        if my._file_object:
            return
        file_type = my.get_file_type()
        if file_type and my.snapshot:
            # get the file_object
            file_code = my.snapshot.get_file_code_by_type(file_type)
            from pyasm.biz import File 
            my._file_object = File.get_by_code(file_code)

    def get_dir(my):
        assert my.protocol != None
        assert my.sobject != None
        
        # this is needed first
        my._init_file_object()

        dirs = []
        dirs.extend( my.get_base_dir() )
        if not my.create:
           dir_dict = my._get_recorded_dir()
           if dir_dict.get('relative_dir'):
                dirs.append(dir_dict.get('relative_dir'))
                return '/'.join(dirs)
           elif dir_dict.get('inplace_dir'):
                return dir_dict.get('inplace_dir')
        
        # Now either create is True or relative_dir has been cleared in the db
        # first check the db, so we build up the naming

        if type(my.naming_expr) == types.DictType:
            override_naming_expr = my.naming_expr.get("override")
            default_naming_expr = my.naming_expr.get("default")
        else:
            override_naming_expr = my.naming_expr
            default_naming_expr = None

        if override_naming_expr:
            dir_name = my.get_from_expression(override_naming_expr)
            if dir_name.startswith("/"):
                return dir_name
            else:
                dirs.append(dir_name)
                return '/'.join(dirs)

        # get from db
        db_dir_name = my.get_from_db_naming(my.protocol)
        if db_dir_name:
            dirs.append(db_dir_name)
            return '/'.join(dirs)
        elif db_dir_name == "":
            return '/'.join(dirs)


        # otherwise look for an overriding python method
        search_type = my.sobject.get_search_type_obj().get_base_key()
        func_name = search_type.replace("/", "_")


        # if there is no snapshot, then create a virtual one
        if not my.snapshot:
            # TODO: may have to fill this in later
            my.snapshot = SearchType.create("sthpw/snapshot")
            my.snapshot.set_value("context", "publish")
        if not my.file_type:
            my.file_type = "main"


        # check to see if the function name exists.
        try:
            dirs = eval( "my.%s(dirs)" % func_name)
            return "/".join(dirs)
        except Exception, e:
            msg = e.__str__()
            if msg.find("object has no attribute '%s'" % func_name) != -1:
                pass
            else:
                raise

        if default_naming_expr:
            dir_name = my.get_from_expression(default_naming_expr)
            if dir_name.startswith("/"):
                return dir_name
            else:
                dirs.append(dir_name)
                return '/'.join(dirs)



        # get the default
        dirs = my.get_default(dirs)
        return "/".join(dirs)



    def get_default(my, dirs):
        # add <project_code>/<table>/<context>
        dirs = my.get_sobject_base(dirs)

        if not Config.get_value("checkin", "default_naming_version") == "1":
            if my.sobject.has_value("code"):
                code = my.sobject.get_value("code")
                if code:
                    dirs.append( code )
            else: 
                sobj_id = my.sobject.get_id()
                if sobj_id:
                    dirs.append( str(sobj_id) )


            # add in the context
            process = my.snapshot.get_value("process")
            if process:
                dirs.append(process)

        return dirs


    def get_sobject_base(my, dirs):
        # add <project_code>/<table>
        search_type_obj = my.sobject.get_search_type_obj()


        project_code = my.sobject.get_project().get_code()
        dirs.append( project_code )
        #db_name = search_type_obj.get_database()
        #dirs.append( db_name )

        from pyasm.prod.biz import ProdSetting
        if project_code not in ["admin", 'sthpw']:
            icon_separation = ProdSetting.get_value_by_key("use_icon_separation")           
            if not icon_separation:
                # put in a default
                icon_separation = "false"
                ProdSetting.create('use_icon_separation', icon_separation, 'string',\
                    description='Determines whether icons are in complete separate directories')
               
            if icon_separation == 'true':
                if my.snapshot and my.snapshot.get_value("context") == "icon":
                    dirs.append("icon")
                elif my.get_file_type() == "icon":
                    dirs.append("icon")


        #process = my.snapshot.get_value("process")
        #search_type = my.snapshot.get_value("search_type")

        # add a concept of branching
        #    from pyasm.web import WidgetSettings
        #    branch = WidgetSettings.get_value_by_key("current_branch")
        #    #WidgetSettings.set_value_by_key("current_branch", branch)
        #    if branch:
        #        #dirs.append( "perforce" )
        #        dirs.append( branch )

        table = search_type_obj.get_table()
        dirs.append( table )

        return dirs



    def get_parent_dir(my, search_type=None, context=None, sobject=None):
        from project import Project

        if not sobject:
            sobject = my.sobject
        if search_type:
            parent = sobject.get_parent(search_type)
        else:
            search_type = sobject.get_value("search_type")
            search_id = sobject.get_value("search_id")
            parent = Search.get_by_id(search_type, search_id)

        if not parent:
            raise TacticException("No parent exists for '%s', possibly a result of Shot rename or removal." % sobject.get_code())

        # just use the latest of the context desired
        if context:
            search_id = parent.get_id()
            search_type = parent.get_search_type()
            snapshot = Snapshot.get_latest(search_type, search_id, context)
        else:
            # basically this means that without a parent context, there is
            # no way to know the directory this is in.
            snapshot = None
        dirs = Project._get_dir( my.protocol,parent,snapshot,None )
        dirs = dirs.split("/")
        return dirs




    def get_base_dir(my, protocol=None):
        '''get the default base directory for this sobject'''
        dirs = []
        base_dir = ''
        
        if not protocol:
            protocol = my.protocol

        if protocol == "http":

            repo_handler = my.sobject.get_repo_handler(my.snapshot)
            if repo_handler.is_tactic_repo():
                base_dir = Config.get_value("checkin", "web_base_dir")
            else:
                base_dir = Config.get_value("perforce", "web_base_dir")


        elif protocol == "remote":
            # TODO: currently needs web to do this
            base_dir = Environment.get_env_object().get_base_url().to_string()

            repo_handler = my.sobject.get_repo_handler(my.snapshot)
            if repo_handler.is_tactic_repo():
                sub_dir = Config.get_value("checkin", "web_base_dir")
            else:
                sub_dir = Config.get_value("perforce", "web_base_dir")

            base_dir = "%s%s" % (base_dir, sub_dir)

        elif protocol == "file":
            #base_dir = Config.get_value("checkin", "asset_base_dir")
            base_dir = Environment.get_asset_dir(my._file_object)

        elif protocol == "env":
            base_dir = "$TACTIC_ASSET_DIR"

        # This is the central repository as seen from the client
        elif protocol in ["client_lib", "client_repo"]:
            
            if Environment.get_env_object().get_client_os() =='nt':
                base_dir = my.get_custom_setting('win32_client_repo_dir')
                if not base_dir:
                    if my._file_object:
                        base_dir_alias = my._file_object.get_value('base_dir_alias')
                        if base_dir_alias:
                            alias_dict = Config.get_value("checkin", "base_dir_alias", sub_key=base_dir_alias)
                            base_dir = alias_dict.get("win32_client_repo_dir")
                    if not base_dir:
                        base_dir = Config.get_value("checkin", "win32_client_repo_dir", no_exception=True)
            else:
                base_dir = my.get_custom_setting('linux_client_repo_dir')
                if not base_dir:
                    if my._file_object:
                        base_dir_alias = my._file_object.get_value('base_dir_alias')
                        if base_dir_alias:
                            alias_dict = Config.get_value("checkin", "base_dir_alias", sub_key=base_dir_alias)
                            base_dir = alias_dict.get("linux_client_repo_dir")
                        if not base_dir:
                            base_dir = Config.get_value("checkin", "linux_client_repo_dir", no_exception=True)
            if not base_dir:
                #base_dir = Config.get_value("checkin", "asset_base_dir")
                base_dir = Environment.get_asset_dir()

        # DEPRECATED: The local repo.  This one has logic to add "repo" dir
        # at the end.  Use local_repo which does not have this logic.
        # keeping this around for backward compatibility
        elif protocol == "local":
            remote_repo = my.get_remote_repo()
            if remote_repo:
                #base_dir = remote_repo.get_value("repo_base_dir")
                base_dir = Environment.get_asset_dir()
            else:
                if Environment.get_env_object().get_client_os() =='nt':
                    base_dir = Config.get_value("checkin","win32_local_base_dir")
                else:
                    base_dir = Config.get_value("checkin","linux_local_base_dir")
                base_dir += "/repo"

        # The local repo
        elif protocol == "local_repo":
            remote_repo = my.get_remote_repo()
            if remote_repo:
                base_dir = remote_repo.get_value("repo_base_dir")
            else:
                if Environment.get_env_object().get_client_os() =='nt':
                    base_dir = Config.get_value("checkin","win32_local_repo_dir")
                else:
                    base_dir = Config.get_value("checkin","linux_local_repo_dir")
                if not base_dir:
                    base_dir = Environment.get_asset_dir()


        elif protocol == "sandbox":
            remote_repo = my.get_remote_repo()
            if remote_repo:
                base_dir = remote_repo.get_value("sandbox_base_dir")
            else:

                base_dir = PrefSetting.get_value_by_key("sandbox_base_dir")
                if not base_dir:

                    if Environment.get_env_object().get_client_os() =='nt':
                        base_dir = Config.get_value("checkin","win32_sandbox_dir")
                        if base_dir == "":
                            base_dir = Config.get_value("checkin","win32_local_base_dir")
                            base_dir += "/sandbox"
                    else:
                        base_dir = Config.get_value("checkin","linux_sandbox_dir")
                        if base_dir == "":
                            base_dir = Config.get_value("checkin","linux_local_base_dir")
                            base_dir += "/sandbox"

        elif protocol == "relative":
            return []

        return [base_dir]


    def get_custom_setting(my, key):
        from pyasm.biz import ProdSetting
        value = ProdSetting.get_value_by_key(key)
        return value


    def get_remote_repo(my):
        # remote repo does not make sense in batch mode
        if Environment.get_app_server() == 'batch':
            return

        remote_repos = Container.get("remote_repos")
        if remote_repos == None:
            search = Search("sthpw/remote_repo")
            remote_repos = search.get_sobjects()
            Container.put("remote_repos", remote_repos)

        # TODO: Get this function out of this class
        # THIS function requires the web
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        if not web:
            return None

        # if a login name is found, use that instead of doing the more 
        # stringent IP match
        current_user = Environment.get_user_name()
        simple_remote_repo = RemoteRepo.get_by_login(current_user)
        if simple_remote_repo:
            return simple_remote_repo

        src_ip = web.get_request_host()
        if not src_ip:
            return

        for remote_repo in remote_repos:
            tgt_ip  = remote_repo.get_value("ip_address")
            mask = remote_repo.get_value("ip_mask")

            if Common.match_ip(src_ip, tgt_ip, mask):
                return remote_repo

        return None




    def get_template_dir(my, template):
        # use regular expressions to match
        pattern = re.compile(r'\{(\w+)\}')
        list = pattern.findall(template)
        if list:
            for group in list:
                value = my.sobject.get_value(group)
                template = template.replace("{%s}" % group, value)

        return template.split("/")


    def get_from_expression(my, naming_expr):
        naming_util = NamingUtil()
        file_type = my.get_file_type()

        # build the dir name
        return naming_util.naming_to_dir(naming_expr, my.sobject, my.snapshot, file=my._file_object, file_type=file_type)



    def get_from_db_naming(my, protocol):
        project_code = Project.get_project_code()
        if project_code in ["admin", "sthpw"]:
            return None

        # get the naming object
        naming = Naming.get(my.sobject, my.snapshot)
        if not naming:
            return None

        if protocol == 'sandbox':
            mode = 'sandbox_dir'
        else:
            mode = 'dir'

        # Provide a mechanism for a custom class
        naming_class = naming.get_value("class_name", no_exception=True)
        #naming_class = "pyasm.biz.TestFileNaming"
        if naming_class:
            kwargs = {
                'sobject': my.sobject,
                'snapshot': my.snapshot,
                'file_object': my._file_object,
                #'ext': my.get_ext(),
                'file_type': my.file_type,
                'mode': mode
            }
            naming = Common.create_from_class_path(naming_class, [], kwargs)
            dirname = naming.get_dir()
            if dirname:
                return dirname


        # provide a mechanism for a custom client side script
        script_path = naming.get_value("script_path", no_exception=True)
        if script_path:
            project_code = my.sobject.get_project_code()
            input = {
                'sobject': my.sobject,
                'snapshot': my.snapshot,
                'file_object': my._file_object,
                #'ext': my.get_ext(),
                'file_type': my.file_type,
                'mode': mode,
                'project': project_code
            }
            from tactic.command import PythonCmd

            cmd = PythonCmd(script_path=script_path, input=input)
            results = cmd.execute()
            if results:
                return results


        naming_util = NamingUtil()

        naming_expr = ''
        if protocol == 'sandbox':
            naming_expr = naming.get_value("sandbox_dir_naming")

        if not naming_expr:
            naming_expr = naming.get_value("dir_naming")

        if not naming_expr:
            return ""

        file_type = my.get_file_type()

        # build the dir name
        dir_name = naming_util.naming_to_dir(naming_expr, my.sobject, my.snapshot, file=my._file_object, file_type=file_type)
        return dir_name






    #
    # Some implementations
    #
    def sthpw_note(my, dirs):
        dirs = my.get_default(dirs)
        context = my.sobject.get_value("context")
        parent = my.sobject.get_parent()
        if parent:
            parent_search_type = parent.get_base_search_type()
            parent_code = parent.get_code()

            dirs.append(parent_search_type)
            dirs.append(parent_code)
        dirs.append(context)
        return dirs



