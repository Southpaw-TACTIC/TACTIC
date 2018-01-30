###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['SyncSecurityWdg', 'SyncProjectSecurityWdg', 'SyncSearchTypeSecurityWdg']

from pyasm.search import Search, SearchType

from pyasm.common import Xml, Common, Environment
from pyasm.command import Command
from pyasm.search import Search
from pyasm.web import DivWdg, Table
from pyasm.biz import Project
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import TabWdg

from tactic.ui.startup import ProjectSecurityWdg, SearchTypeSecurityWdg


class SyncSecurityWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top

        return top



class SyncProjectSecurityWdg(ProjectSecurityWdg):

    def get_groups(self):

        search = Search("sthpw/sync_server")
        servers = search.get_sobjects()
        self.servers = {}

        # HACK
        for server in servers:
            server.set_value("login_group", server.get_code() )
            self.servers[server.get_code()] = server

        return servers


    def get_sobjects(self, group_names):
        # get the project sobjects
        search = Search("sthpw/project")
        search.add_filters("code", ['sthpw','admin','unittest'], op='not in')
        search.add_order_by("title")
        projects = search.get_sobjects()


        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("title", "ALL PROJECTS")
        sobject.set_value("_extra_data", {"is_all": True})
        sobject.set_value("id", 1)
        sobject.set_value("code", "*")
        projects.insert(0, sobject)


        # process all of the groups and find out which projects
        security = Environment.get_security()

        rules_dict = {}

        for project in projects:
            for group_name in group_names:

                access_rules = rules_dict.get(group_name)
                if access_rules == None:

                    #!!!!!!
                    #group = LoginGroup.get_by_group_name(group_name)
                    group = self.servers.get(group_name)


                    access_rules = group.get_xml_value("access_rules")
                    rules_dict[group_name] = access_rules

                node = access_rules.get_node("rules/rule[@group='project' and @code='%s']" % project.get_code())

                if node is not None:
                    project.set_value("_%s" % group_name, True)
                else:
                    project.set_value("_%s" % group_name, False)


        return projects




class SyncSearchTypeSecurityWdg(SearchTypeSecurityWdg):

    def get_save_cbk(self):
        return 'tactic.ui.startup.SearchTypeSecurityCbk'

    def get_groups(self):

        search = Search("sthpw/sync_server")
        servers = search.get_sobjects()
        self.servers = {}

        # HACK
        for server in servers:
            server.set_value("login_group", server.get_code() )
            self.servers[server.get_code()] = server

        return servers




    def get_sobjects(self, group_names):
        # get the project sobjects
        sobjects = Project.get().get_search_types()

        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("title", "ALL PROJECTS")
        sobject.set_value("_extra_data", {"is_all": True})
        sobject.set_value("id", 1)
        sobject.set_value("code", "*")
        sobjects.insert(0, sobject)



        # process all of the groups and find out which sobjects
        security = Environment.get_security()

        rules_dict = {}

        for sobject in sobjects:
            for group_name in group_names:

                access_rules = rules_dict.get(group_name)
                if access_rules == None:

                    #!!!!!!
                    #group = LoginGroup.get_by_group_name(group_name)
                    group = self.servers.get(group_name)

                    access_rules = group.get_xml_value("access_rules")
                    rules_dict[group_name] = access_rules

                node = access_rules.get_node("rules/rule[@group='search_type' and @code='%s']" % sobject.get_code())

                if node is not None:
                    sobject.set_value("_%s" % group_name, True)
                else:
                    sobject.set_value("_%s" % group_name, False)

        return sobjects




