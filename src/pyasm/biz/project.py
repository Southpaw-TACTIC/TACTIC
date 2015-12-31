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

__all__ = ["Project", "ProjectType", "ProjectResource", "Repo", "RemoteRepo"]

import types

from pyasm.common import Common, TacticException, SecurityException, Container, Environment, Xml, Config, jsonloads, jsondumps
from pyasm.search import SObjectFactory, SObject, SearchType, DatabaseImpl, Search, SearchKey, Sql, DbContainer, DbResource


class Project(SObject):

    SEARCH_TYPE = "sthpw/project"

    def __init__(my, search_type=None, columns=None, results=None, fast_data=None):
        super(Project, my).__init__(search_type, columns, results, fast_data=fast_data)

        my.file_naming = None
        my.project_type = None

        my.search_types = None


    #def get_icon_context(my, context=None):
    #    return "publish"

    def is_admin(my):
        code = my.get_code()
        if code == "admin":
            return True
        else:
            return False


    def validate(my):
        '''The project code cannot just be an integer'''
        try:
            int(my.get_value("code"))
        except ValueError:
            pass
        else:
            raise TacticException('Project code cannot be a number')



    def get_resource(my):
        key = "Project:resource:%s" % my
        resource = Container.get(key)
        if resource == None:
            resource = ProjectResource(my)
            Container.put(key, resource)
        return resource


    def get_project_db_resource(my, database=None):
        # get the db resource for attached to this particular project.
        # Not the db_resource for "sthpw/project" for which
        # project.get_db_resource() does
        from pyasm.security import Site
        site = Site.get_site()
        if site:
            key = "Project:db_resource_cache:%s" % site
        else:
            key = "Project:db_resource_cache"

        resource_dict = Container.get(key)
        if resource_dict:
            resource = resource_dict.get( my.get_code() )
            if resource != None:
                return resource
        else:
            resource_dict = {}
            Container.put(key, resource_dict)


        # the project defines the resource
        if not database:
            database = my.get_database_name()
        assert database

        if database == 'sthpw':
            # get if from the config
            db_resource_code = None
        else:
            db_resource_code = my.get_value("db_resource", no_exception=True)

        if not db_resource_code:
            # this could be any project, not just sthpw
            # already looked at cache, so set use_cache to False
            db_resource = Site.get_db_resource(site, database)
            if not db_resource:
                db_resource = DbResource.get_default(database, use_cache=False)
            #db_resource = DbResource.get_default(database, use_cache=False)
            resource_dict[key] = db_resource
            return db_resource
        #elif isinstance(db_resource_code, DbResource):
        elif DbResource.is_instance(db_resource_code):   
            db_resource = db_resource_code
            resource_dict[key] = db_resource
            return db_resource


        db_resource_code = db_resource_code.strip()
        search = Search("sthpw/db_resource")
        search.add_filter("code", db_resource_code)
        db_resource_sobj = search.get_sobject()
        if not db_resource_sobj:
            raise TacticException("Database Resource [%s] does not exist" % db_resource_code)


        host = db_resource_sobj.get_value("host")
        vendor = db_resource_sobj.get_value("vendor")
        host = db_resource_sobj.get_value("host")
        port = db_resource_sobj.get_value("port")
        user = db_resource_sobj.get_value("login")
        password = db_resource_sobj.get_value("password")
       
        db_resource = DbResource(user=user, database=database, host=host, port=port, vendor=vendor, password=password)
        #Container.put(key, db_resource)
        resource_dict[key] = db_resource

        return db_resource


    def get_sql(my):
        db_resource = my.get_project_db_resource()
        from pyasm.search import DbContainer
        sql = DbContainer.get(db_resource)

        return sql



    def get_database_name(my):
        # This will cause an infinite loop.  Get the data directly to avoid
        #database_name = my.get_value("database", no_exception=True)
        database_name = my.get_data().get("database")

        if not database_name:
            database_name = my.get_code()
        if database_name == "admin":
            database_name = "sthpw"
        return database_name


    def get_database_type(my):
        db_resource = my.get_project_db_resource()
        impl = DatabaseImpl.get()
        return impl.get_database_type()


    def database_exists(my):
        '''returns whether a database exists for this project'''
        if not my.get_value("code"):
            return False

        db_resource = my.get_project_db_resource()
        impl = DatabaseImpl.get()
        return impl.database_exists(db_resource)

    # DEPRECATED. use get_base_type()
    # TODO: make it just return the value "type"
    def get_type(my):
        '''get the string value, type of project'''
        return my.get_base_type()

    def get_base_type(my):
        '''get the string value, type of project'''
        if my.get_code() == "admin":
            return "admin"

        if my.project_type:
            return my.project_type.get_type()
        else:
            project_type = my.get_project_type()
            if project_type:
                return project_type.get_type()
            else:
                # special project like sthpw and admin have an empty type
                return ''   

    def get_project_type(my):
        ''' get the sobject ProjectType'''
        if not my.project_type:
            type = my.get_value('type')
            my.project_type = ProjectType.get_by_code(type)
        return my.project_type 

    def get_initials(my):
        '''get the initials of project'''
        initials = my.get_value('initials')
        if not initials:
            initials = my.get_code().upper()
        return initials




    def get_by_code(cls, project_name):
        if project_name == "default":
            project = Container.get("default_project")
            return project
        return super(Project, cls).get_by_code(project_name)
    get_by_code = classmethod(get_by_code)



    #
    # static functions
    #
    def get(cls, no_exception=False):
        '''get current project'''
        project_name = cls.get_global_project_code()
        if project_name == "":
            project_name = "sthpw"

        project = Project.get_by_code(project_name)
         
        if not project:
            # check if its the sthpw database and create
            if project_name in ("sthpw", "admin"):
                project = SearchType.create(Project.SEARCH_TYPE)
                project.set_value("code", project_name)

                # admin does not have a project type
                if project_name == 'sthpw':
                    project.set_value("type", 'sthpw')

                project.set_value("title", "Tactic")
                project.set_value("database", "sthpw")
                project.commit(triggers=False)
                sk ='sthpw/project?code=%s'%project_name
                Project.clear_cache(search_key=sk)

            elif project_name in ['default']:
                project = Container.get("default_project")
                if not project:
                    project = SearchType.create("sthpw/project")
                    Container.put("default_project", project)
                    project.set_value("code", project_name)

            elif no_exception:
                return None
            else:
                # FIXME: why is a virtual project created?
                raise TacticException("No project [%s] exists" % project_name)
                #print "WARNING: No project entry exists for project '%s'" % project_name
                #print "Creating virtual project"
                #project = SearchType.create(Project.SEARCH_TYPE)
                #project.set_value("code", project_name)

        return project
    get = classmethod(get)


    def get_default_project(cls):
        from pyasm.security import Site
        project = Site.get().get_default_project()
        if project:
            return project
        project = Config.get_value("install", "default_project")
        return project
    get_default_project = classmethod(get_default_project) 



    def get_all_projects(cls):
        search = Search("sthpw/project")
        search.add_filters("code", ['admin','sthpw'], op='not in')
        projects = search.get_sobjects()
        return projects
    get_all_projects = classmethod(get_all_projects) 



    def get_user_projects(cls):
        search = Search("sthpw/project")
        projects = search.get_sobjects()

        security = Environment.get_security()
        key = { "code": "*" }
        if security.check_access("project", key, "allow", default="deny"):
            return projects

        # which projects is a user allowed to see
        allowed = []
        for project in projects:
            key = {"code": project.get_code() }
            if security.check_access("project", key, "allow", default="deny"):
                allowed.append(project)

        return allowed

    get_user_projects = classmethod(get_user_projects)


    def get_by_search_type(cls, search_type):
        # Make sure it is not a search type object because a search type
        # object does not contain any project info
        assert not isinstance(search_type, SearchType)

        project_code = cls.extract_project_code(search_type)
        assert project_code != "__NONE__"


        project = cls.get_by_code(project_code)
        return project
    get_by_search_type = classmethod(get_by_search_type)



    def get_project_filter(cls, project_code=None, show_unset=True):
        if not project_code:
            project_code = cls.get_project_code()
        
        if isinstance(project_code, list):
            project_filters = []
            for code in project_code:
                project_filter = "(\"project_code\" = '%s' or \"project_code\" like '%%||%s||%%')" % (code, code)
                project_filters.append(project_filter)
            project_filter = ' or '.join(project_filters)
        else:
            if show_unset:
                project_filter = "(\"project_code\" is NULL or \"project_code\" = '%s' or \"project_code\" like '%%||%s||%%')" % (project_code, project_code)
            else:   
                project_filter = "(\"project_code\" = '%s' or \"project_code\" like '%%||%s||%%')" % (project_code, project_code)
        return project_filter
    get_project_filter = classmethod(get_project_filter)



    def has_table(my, search_type):
        if isinstance(search_type, basestring):
            search_type = SearchType.get(search_type)


        # in search type database == project 
        project_code = search_type.get_project_code()

        # get the db_resource for this project
        db_resource = my.get_project_db_resource()

        # get the table
        table = search_type.get_table()
        if not table:
            return False

        try:
            # looking up a database's tables other than the current one
            sql = DbContainer.get(db_resource)
            tables = sql.get_tables()
            has_table = table in tables
        except Exception, e:
            print "WARNING: in Project.has_table(): table [%s] not found" % table
            print "Message: ", e
            has_table = False

        return has_table


    def get_search_types(my, include_sthpw=False, include_config=False, include_multi_project=False):
        '''get all the search types in this project'''
        if my.search_types != None:
            return my.search_types

        project_type = my.get_value("type")

        search = Search("sthpw/search_object")

        project_code = my.get_code()
        namespaces = [project_code]
        namespaces.append(project_type)

        if include_sthpw:
            namespaces.append("sthpw")
        if include_config:
            namespaces.append("config")
        if include_multi_project:
            if not include_config:
                search.add_filter('namespace','config',op='!=')
            if not include_sthpw:
                search.add_filter('namespace','sthpw',op='!=')
            search.add_op('begin')
            search.add_filter('database','{project}')
            

        search.add_filters("namespace", namespaces)

        if include_multi_project:
            search.add_op('or')

        search.add_order_by("search_type")
        search_type_objs = search.get_sobjects()

        """
        from pyasm.biz import Schema
        schema = Schema.get()
        xml = schema.get_xml_value("schema")
        search_types = xml.get_values("schema/search_type/@name")
        search = Search("sthpw/search_object")
        search.add_filters("code", search_types)
        search_type_objs = search.get_sobjects()
        """



        search_types = []
        for x in search_type_objs:
            # to avoid the old ill-defined prod/custom_property defined in sthpw namespace
            if (x.get_value('namespace') == 'sthpw' and x.get_value('search_type').find('custom_property') == -1)\
                or my.has_table(x):
                search_types.append(x)
        return search_types



    def get_project_name():
        return Project.get().get_code()
    get_project_name = staticmethod(get_project_name)

    def get_project_code(no_exception=False):
        project = Project.get(no_exception=no_exception)
        if project:
            return project.get_code()
        else:
            return ""
    get_project_code = staticmethod(get_project_code)

    # DEPRECATED
    def get_reg_hours():
        # FIXME: this shold be in pyasm.biz, not pyasm.prod.biz
        from pyasm.prod.biz import ProdSetting
        reg_hours = ProdSetting.get_value_by_key("reg_hours")
        if not reg_hours:
            # auto create if it does not exist
            ProdSetting.create('reg_hours', '10',  'sequence', \
                description='regular work hours', search_type='sthpw/project')

        return reg_hours
    get_reg_hours = staticmethod(get_reg_hours)
  
    def get_database_impl():
        project = Project.get()
        db_resource = project.get_db_resource()
        sql = DbContainer.get(db_resource)
        return sql.get_database_impl()

    get_database_impl = staticmethod(get_database_impl)

    
    
    #
    # Setting projects
    #
    def set_project(cls, project_code):
        '''This is kept here because everybody is used to using this'''

        security = Environment.get_security()
        # FIXME:
        # Because it is possible to call this before one is 
        # logged in.  This is required to see the login screen.
        from pyasm.security import get_security_version
        security_version = get_security_version()
        if security_version != 1 and not project_code == 'admin':
            key = { 'code': project_code }
            key2 = { 'code': "*" }
            keys = [key, key2]
            if not security.check_access("project", keys, access="allow", default="deny"):
                user = Environment.get_login()
                if user:
                    user = user.get_value("login")
                    raise SecurityException("User [%s] is not permitted to view project [%s]" % (user, project_code))
                else:
                    raise SecurityException("User is not permitted to view project [%s]" % (project_code))

        from pyasm.security import Site
        site = Site.get_site()
        PROJECT_KEY = "Project:global:%s:" % site
        Container.put(PROJECT_KEY, project_code)
    set_project = classmethod(set_project)
 
    def set_global_project_code(cls, project_code):
        cls.set_project(project_code)
        #PROJECT_KEY = "Project:global"
        #Container.put(PROJECT_KEY, project_code)
    set_global_project_code = classmethod(set_global_project_code)
        
    def get_global_project_code(cls):
        from pyasm.security import Site
        site = Site.get_site()
        PROJECT_KEY = "Project:global:%s:" % site
        project_code = Container.get(PROJECT_KEY)
        if not project_code:
            project_code = "admin"
            Project.set_global_project_code(project_code)
        return project_code
    get_global_project_code = classmethod(get_global_project_code)


    def get_full_search_type(cls, search_type, project_code=None, project=None):
        if type(search_type) in types.StringTypes:
            if search_type.find("?") == -1:
                base_key = search_type
            else:
                # if there is a project, just use it
                return search_type
        else:
            base_key = search_type.get_base_key()

        if base_key.startswith("sthpw/"):
            full_key = base_key
            return full_key



        if project_code:
            code = project_code
        elif project:
            code = project.get_code()
        else:
            # get the current project
            #code = Project.get_global_project_code()
            search_type_obj = SearchType.get(base_key)
            code = search_type_obj.get_database()



        # NOTE: if someone expliclity set the Project.set('sthpw') before this, 
        # it will affect the full key of this sobject
        # prevent sthpw projects from having a "project=" at the end
        if code in ["sthpw", "admin"]:
            full_key = base_key
        else:
            full_key = "%s?project=%s" % (base_key, code)
        return full_key

    get_full_search_type = classmethod(get_full_search_type)


    def extract_base_search_type(cls, search_type):
        base_search_type, data = SearchKey._get_data(search_type)
        return base_search_type
    extract_base_search_type = classmethod(extract_base_search_type)


    def extract_project_code(cls, search_type):
        base_search_type, data = SearchKey._get_data(search_type)
        project_code = data.get("project")
        if project_code == None:
            if search_type.startswith('sthpw/'):
                return 'sthpw'
            # this is specifically for project-specific sType
            
            search_type_obj = SearchType.get(search_type)
            database = search_type_obj.get_value("database")
            if database != "{project}":
                project_code = database
            else:
                # get the global project code
                project_code = Project.get_project_code()

            #project_code = cls.get_global_project_code()
        return project_code
    extract_project_code = classmethod(extract_project_code)
        
    def extract_host(cls, search_type):
        base_search_type, data = SearchKey._get_data(search_type)
        host = data.get("host")
        return host
    extract_host = classmethod(extract_host)


    def extract_database(cls, search_type):
        if search_type.startswith("sthpw/"):
            return 'sthpw'

        if search_type.find("?") != -1:
            project_code = cls.extract_project_code(search_type)

            # when viewing widget_config in Admin site
            if project_code == 'admin':
                project_code = 'sthpw'
            return project_code
        else:
            return 'sthpw'
            
    extract_database = classmethod(extract_database)



    def get_database_by_search_type(cls, search_type):
        base_search_type, data = SearchKey._get_data(search_type)
        if base_search_type.startswith("sthpw/"):
            return "sthpw"

        project_code = data.get("project")

        # if no project is defined, get the global default
        if project_code == None:
            search_type_obj = SearchType.get(search_type)
            # this is more accurate specifically for project-specific sType
            project_code = search_type_obj.get_database()
            #project_code = cls.get_global_project_code()
       
        if project_code == 'admin':
            project_code = 'sthpw'

        return project_code
    get_database_by_search_type = classmethod(get_database_by_search_type)



    def get_db_resource_by_search_type(cls, search_type):
        if search_type.startswith('sthpw/'):
            # get the local db_resource
            from pyasm.security import Site
            site = Site.get_site()
            db_resource = None
            if site:
                db_resource = Site.get_db_resource(site, "sthpw")
            if not db_resource:
                db_resource = DbResource.get_default("sthpw")
            return db_resource

        project_code = cls.get_database_by_search_type(search_type)
        project = Project.get_by_code(project_code)
        if not project:
            raise Exception("Error: Project [%s] does not exist" % project_code)
        db_resource = project.get_project_db_resource()
        return db_resource
    get_db_resource_by_search_type = classmethod(get_db_resource_by_search_type)







    # repo handling
    def get_project_repo_handler(project_code=None):
        if not project_code:
            project = Project.get()
        else:
            project = Project.get_by_code(project_code)

        repo_handler_cls = project.get_value("repo_handler_cls", no_exception=True)

        if not repo_handler_cls and project.get_project_type():
            repo_handler_cls = project.get_project_type().get_value("repo_handler_cls", no_exception=True)


        if not repo_handler_cls:
            repo_handler_cls = "pyasm.biz.BaseRepoHandler"

        repo_handler = Common.create_from_class_path(repo_handler_cls)

        return repo_handler
    get_project_repo_handler = staticmethod(get_project_repo_handler)


    # sobject code naming
    def get_code_naming(sobject,code):
        '''Gets the code naming object for the current project'''
        project = Project.get()
        code_naming_cls = project.get_value("code_naming_cls")
        if code_naming_cls == "":
            code_naming_cls = "pyasm.biz.CodeNaming"

        naming = Common.create_from_class_path(code_naming_cls, \
            [sobject,code] )
        return naming
    get_code_naming = staticmethod(get_code_naming)


    # file naming
    def get_file_naming(cls, sobject=None, project=None):
        '''Gets the file naming object for the current project'''
        return cls.get_naming("file", sobject, project)
    get_file_naming = classmethod(get_file_naming)

    def get_dir_naming(cls, sobject=None, project=None):
        '''Gets the directory naming object for the current project'''
        return cls.get_naming("dir", sobject)
    get_dir_naming = classmethod(get_dir_naming)


    
    def get_naming(cls, naming_type, sobject=None, project=None):
        '''get a certain type of naming determined by type of naming'''

        naming_cls = ""
        
        # this import statement is needed for running Batch
        from pyasm.biz import Project
        if not project:
            if sobject:
                project = sobject.get_project()
            else:
                project = Project.get()
       

        if project:
            naming_cls = project.get_value("%s_naming_cls" % naming_type, no_exception=True)
            if not naming_cls and project.get_project_type():
                naming_cls = project.get_project_type().get_value("%s_naming_cls" % naming_type, no_exception=True)



        # if none is defined, use defaults
        if not naming_cls:
            # TODO: this should probably be stored somewhere else
            if naming_type == "file":
                naming_cls = "pyasm.biz.FileNaming"
            elif naming_type == "dir":
                naming_cls = "pyasm.biz.DirNaming"
            elif naming_type == "node":
                naming_cls = "pyasm.prod.biz.ProdNodeNaming"
       
        naming = Common.create_from_class_path(naming_cls)
        return naming
    get_naming = classmethod(get_naming)







    # directory functions for the project
    def get_project_web_dir(sobject,snapshot,file_type=None,file_object=None):
        return Project._get_dir("http", sobject,snapshot,file_type,file_object=file_object)
    get_project_web_dir = staticmethod(get_project_web_dir)

    def get_project_lib_dir(sobject,snapshot,file_type=None, create=False, file_object=None, dir_naming=None):
        return Project._get_dir("file", sobject,snapshot,file_type, create, file_object, dir_naming=dir_naming)
    get_project_lib_dir = staticmethod(get_project_lib_dir)

    def get_project_env_dir(sobject,snapshot,file_type=None):
        return Project._get_dir("env", sobject,snapshot,file_type)
    get_project_env_dir = staticmethod(get_project_env_dir)

    def get_project_client_lib_dir(sobject,snapshot,file_type=None, create=False, file_object=None, dir_naming=None):
        return Project._get_dir("client_lib", sobject,snapshot,file_type, create, file_object, dir_naming=dir_naming)
    get_project_client_lib_dir = staticmethod(get_project_client_lib_dir)


    # DEPRECATED: use get_project_local_repo_dir
    def get_project_local_dir(sobject,snapshot,file_type=None):
        #return Project._get_dir("local", sobject,snapshot,file_type)
        return Project._get_dir("local_repo", sobject,snapshot,file_type)
    get_project_local_dir = staticmethod(get_project_local_dir)

    def get_project_local_repo_dir(sobject,snapshot,file_type=None,file_object=None):
        return Project._get_dir("local_repo", sobject,snapshot,file_type, file_object=file_object)
    get_project_local_repo_dir = staticmethod(get_project_local_repo_dir)




    def get_project_sandbox_dir(sobject,snapshot,file_type=None):
        return Project._get_dir("sandbox", sobject,snapshot,file_type)
    get_project_sandbox_dir = staticmethod(get_project_sandbox_dir)

    def get_sandbox_base_dir(sobject, decrement=0):
        return Project._get_base_dir("sandbox", sobject, decrement=decrement)
    get_sandbox_base_dir = staticmethod(get_sandbox_base_dir)

    def get_project_remote_web_dir(sobject,snapshot,file_type=None):
        return Project._get_dir("remote", sobject,snapshot,file_type)
    get_project_remote_web_dir = staticmethod(get_project_remote_web_dir)

    def get_project_relative_dir(sobject,snapshot,file_type=None, create=False, file_object=None, dir_naming=None):
        return Project._get_dir("relative", sobject,snapshot,file_type, create, file_object, dir_naming=dir_naming)
    get_project_relative_dir = staticmethod(get_project_relative_dir)



    def _get_dir(protocol,sobject,snapshot,file_type=None, create=False, file_object=None, dir_naming=None):

        dir_naming_expr = dir_naming

        from snapshot import Snapshot, SObjectNotFoundException
        if isinstance(sobject,Snapshot):
            snapshot = sobject
            try:
                sobject = snapshot.get_sobject()
            except SObjectNotFoundException, e:
                pass

        dir_naming = Project.get_dir_naming(sobject)
        dir_naming.set_sobject(sobject)
        dir_naming.set_snapshot(snapshot)
        dir_naming.set_file_type(file_type)
        dir_naming.set_file_object(file_object)
        dir_naming.set_naming(dir_naming_expr)
        dir_naming.set_create(create)
        dir_naming.set_protocol(protocol)
        dirname = dir_naming.get_dir()
        
        return dirname
    _get_dir = staticmethod(_get_dir)


    def _get_base_dir(protocol, sobject, decrement=0):
        '''decrement is the number of levels it tries to go up the directory'''
        snapshot = None
        from snapshot import Snapshot
        if isinstance(sobject,Snapshot):
            snapshot = sobject

            # try to get the parent, but protect against dangling snapshots
            from snapshot import SObjectNotFoundException
            try:
                sobject = snapshot.get_sobject()
            except SObjectNotFoundException, e:
                pass
        
        dir_naming = Project.get_dir_naming(sobject)
        dir_naming.set_sobject(sobject)
        dir_naming.set_snapshot(snapshot)
        dir_naming.set_protocol(protocol)

        """
        dirs = dir_naming.get_base_dir()
        dirs = dir_naming.get_default(dirs)
        dirs = '/'.join(dirs).split('/')
        """
        full_dirs = dir_naming.get_dir().split('/')
        full_dirs = full_dirs[0:len(full_dirs)-decrement]
        return '/'.join(full_dirs)

    _get_base_dir = staticmethod(_get_base_dir)

    def get_all(cls):
        '''returns all of the projects in the system.'''
        search = Search(cls.SEARCH_TYPE)
        sobjects = search.get_sobjects()
        return sobjects
    get_all = classmethod(get_all)



class ProjectType(SObject):
    SEARCH_TYPE = 'sthpw/project_type'

    def get_type(my):
        return my.get_value('type')
    
    def get_label(my):
        return '%s (%s)' %(my.get_code(), my.get_type())





class ProjectResource(object):
    '''class that stores and retrieves the data connection information
    for a particular project'''

    def __init__(my, project):
        my.project = project

        my.resource = my.get_info_by_project(project)

        my.protocol = my.resource.get("protocol")
        my.host = my.resource.get("host")
        my.project_code = my.resource.get("project")
        if not my.project_code:
            my.project_code = project.get_code()

        #my.port = None
        #my.ticket = ticket
        my.ticket = my.resource.get("ticket")
        if not my.ticket:
            ticket_obj = Environment.get_security().get_ticket()
            if ticket_obj:
                my.ticket = ticket_obj.get_key()
        # What does it mean when my.ticket is None? it happens on first
        # login_with_ticket() before my._ticket is generated


    def get_host(my):
        return my.host

    def get_protocol(my):
        return my.protocol

    def get_ticket(my):
        return my.ticket

    def get_project(my):
        return my.project_code


    def get_server(my):
        # do a query for the search
        from tactic_client_lib import TacticServerStub
        if my.protocol == 'xmlrpc':
            stub = TacticServerStub(setup=False, protocol=my.protocol)
            stub.set_server(my.host)
            stub.set_project(my.project_code)
            stub.set_ticket(my.ticket)
        else:
            stub = TacticServerStub.get()

        return stub



    def get_info_by_project(my, project):

        if not project.has_value("resource"):
            return {}
        xml = project.get_xml_value("resource")
        """
        if project.get_code() == 'sample3d':
            resource_xml = '''
            <resource>
              <protocol>xmlrpc</protocol>
              <host>192.168.109.132:8082</host>
              <user>admin</user>
              <password>tactic</password>
              <ticket>c19eeef8f38d9d57b23a3d3c3fc73c86</ticket>
            </resource>
            '''
        else:
            resource_xml = '''
            <resource>
              <protocol>local</protocol>
            </resource>
            '''


        xml = Xml()
        xml.read_string(resource_xml)
        """


        node = xml.get_node("resource")
        values = xml.get_node_values_of_children(node)
        return values





# DEPRECATED
class Repo(SObject):
    SEARCH_TYPE = "sthpw/repo"

    def get_handler(my):
        handler_class = my.get_value("handler")
        repo_handler = Common.create_from_class_path(handler_class)
        return handler
        
class RemoteRepo(SObject):
    SEARCH_TYPE = "sthpw/remote_repo"

    def get_by_login(login):
        search = Search(RemoteRepo.SEARCH_TYPE)
        search.add_filter('login', login)
        repo = RemoteRepo.get_by_search(search, login)
        return repo

    get_by_login = staticmethod(get_by_login)


