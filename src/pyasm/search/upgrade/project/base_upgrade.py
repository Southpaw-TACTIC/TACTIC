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

__all__ = ['BaseUpgrade']


import inspect, re

from pyasm.biz import Project
from pyasm.command import Command
from pyasm.search import Search, DbContainer, SqlException, Transaction
from pyasm.common import Base, Common, Container



class BaseUpgrade(Command):


    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)


    def __init__(self):
        self.upgrade_method = None
        self.to_version = 0
        self.is_forced = False
        self.quiet = False
        self.is_confirmed = False
        self.commit_now = True
        self.upgrade_class = None
        super(BaseUpgrade, self).__init__()
    
    def set_project(self, project_code):
        self.project_code = project_code
        Project.set_project(project_code)

    def set_upgrade_method(self, method):
        ''' this is the name of the method for the current upgrade instance'''
        if not isinstance(method, basestring):
            raise TacticException('method should be a string')
        self.upgrade_method = method 

    def set_upgrade_class(self, class_name):
        self.upgrade_class = class_name

    def set_to_version(self, version):
        self.to_version = version

    def set_forced(self, forced):
        self.is_forced = forced

    def set_quiet(self, quiet):
        self.quiet = quiet

    def set_confirmed(self, is_confirmed):
        self.is_confirmed = is_confirmed

    def set_commit(self, commit):
        self.commit_now = commit

    def execute(self):
        assert self.project_code

        # get the project and find out the date of the last update of the
        # database
        project = Project.get()
        self.version_update = project.get_value("last_version_update", no_exception=True)

        if not self.version_update:
            self.version_update = "2.5.0.v01"
      
        members = inspect.getmembers(self.__class__, predicate=inspect.ismethod)
        methods = []
        critical_methods = []
        for name, member in members:
            if name.startswith('upgrade_v'):
                methods.append((name, member))
            if name.startswith('critical_v'):
                critical_methods.append((name, member))

        methods.sort()

        # add the critical methods at the beginning
        critical_methods.reverse()
        for critical_method in critical_methods:
            methods.insert(0, critical_method)


        # make sure critical methods are run first
        methods.sort()
        for name, method in methods:
            if name.startswith("critical"):
                method_version = re.sub(r'critical_v(\w*)_(\d{3}(\w)?)$', '\\1', name) 
            else:
                method_version = re.sub(r'upgrade_v(\w*)_(\d{3}(\w)?)$', '\\1', name) 

            method_version = method_version.replace('_', '.')
            if self.is_forced:
                if not (self.version_update <= method_version <= self.to_version):
                    continue
            elif not (self.version_update < method_version <= self.to_version):
                    continue
            if not self.quiet:
                print "Running upgrade for [%s]..." %name

            self.run_method(name, method)

    def get_database_type(self):
        project = Project.get_by_code(self.project_code)
        db_resource = project.get_project_db_resource()
        db = DbContainer.get(db_resource)
        return db.get_database_type()

    def run_method(self, name, method):
            try:
                #upgrade = eval( '%s()' %self.__class__.__name__)
                upgrade = BaseUpgrade()
            except NameError:
                print "Failed to import upgrade script for %s" %self.__class__.__name__ 
                return
            # substitute the function of 'execute' method with the
            # upgrade script
            Common.add_func_to_class(method, upgrade, upgrade.__class__, 'execute')
            upgrade.set_project(self.project_code)
            upgrade.set_upgrade_class(self.__class__.__name__)
            upgrade.set_upgrade_method(name)

            upgrade.set_quiet(self.quiet)
            upgrade.set_confirmed(self.is_confirmed)

            Command.execute_cmd(upgrade, call_trigger=False)

    def get_database_type(self):
        project = Project.get_by_code(self.project_code)
        db_resource = project.get_project_db_resource()
        db = DbContainer.get(db_resource)
        return db.get_database_type()




    def run_sql(self, sql):
        ''' run an sql statement. self is an instance of the dynamically created 
        <project_type>Upgrade class. If SqlException arise, it will record the
        error, and the user is advised to check if the error is a result of syntax 
        error or the upgrade function is doing redundant work'''
        project = Project.get_by_code(self.project_code)
        db_resource = project.get_project_db_resource()
        db = DbContainer.get(db_resource)
        #if not self.quiet:
        #    print sql
        try:
            db.do_update(sql, quiet=self.quiet)
        except SqlException, e:
            print "Error: ", e
            # TEST for Sqlite
            if str(e).startswith("duplicate column name:"):
                pass
            elif str(e).startswith("table") and str(e).endswith("already exists"):
                pass

            elif not self.quiet:
                print
                print "WARNING: Skipping due to SqlException..."
                print "Message: ", e
                print
            members = inspect.getmembers(self, predicate=inspect.ismethod)
            key = '%s|%s' %(self.project_code, self.upgrade_class)
            
            Container.append_seq(key, (self.upgrade_method, str(e)))
            """  
            for name, member in members:
                # there should only be 1 upgrade method
                if name.startswith('upgrade_v'):       
                    Container.append_seq(key, (self.upgrade_method, str(e)))
                    break
            """          
            # to prevent sql error affecting query that follows the Upgrade
            #DbContainer.abort_thread_sql()
            DbContainer.release_thread_sql()
        else:
            if self.commit_now:
                db.commit()






