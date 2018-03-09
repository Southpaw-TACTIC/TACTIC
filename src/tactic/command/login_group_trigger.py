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
__all__ = ['LoginGroupTrigger']

import tacticenv
import re

from pyasm.search import Search, SearchKey
from pyasm.command import Trigger
from pyasm.biz import Project
from tactic_client_lib import TacticServerStub


class LoginGroupTrigger(Trigger):

    def execute(self):

        input = self.get_input()
        mode = input.get("mode")

        if mode not in ['insert', 'update']:
            return

        update_data = input.get("update_data")

        if 'name' not in update_data and 'login_group' not in update_data:
            return

        search_key = input.get("search_key")
        sobj = SearchKey.get_by_search_key(search_key)


        # this logic makes the login name take precedence and determines the
        # code and login_group column

        # the problem is that groups are global and sometimes you want to have
        # the project_code prepended to the group in order to scope it
        # correctly.  However, you don't necessarily want the name of the
        # project to prepend the name


        if mode == "insert":
            login_group_name = sobj.get_value('login_group')

            if not login_group_name:
                raise Exception("A Group Name has not been entered. Please enter a Group Name.")

            sobj.set_value('name', login_group_name)

        elif mode == "update":
            if 'login_group' in update_data:
                raise Exception('Login group attribute is automatically updated. Please edit only the name attribute.')

            login_group_name = sobj.get_value('name')

            if not login_group_name:
                login_group_name = sobj.get_value('login_group')

        login_group = re.sub(r'[\$\s,#~`\%\*\^\&\(\)\+\=\[\]\[\}\{\;\:\'\"\<\>\?\|\\\!-]', "_", login_group_name)
        login_group = login_group.lower()
        login_group_name = sobj.get_value('login_group')



        # make sure the project code is prepended to the login_group
        if sobj.get_value("project_code"):
            project_code = Project.get_project_code()
            if not login_group.startswith("%s_" % project_code):
                login_group = "%s_%s" % (project_code, login_group)


        sobj.set_value('login_group', login_group)
        sobj.set_value('code', login_group)

        sobj.commit(triggers=False)

        self.update_related(login_group, login_group_name)



    def update_related(self, login_group, prev_login_group):
        '''Update related table login_in_group''' 

        search = Search('sthpw/login_in_group')
        search.add_filter('login_group', prev_login_group)
        login_in_groups = search.get_sobjects()

        if login_in_groups:

            server = TacticServerStub.get()
            login_in_group_dict = {}
            
            data = {
                "login_group": login_group
            }

            for login_in_group in login_in_groups:
                login_in_group_code = login_in_group.get("code")
                login_in_group_sk = server.build_search_key("sthpw/login_in_group", login_in_group_code)
                login_in_group_dict[login_in_group_sk] = data

            try:
                server.update_multiple(login_in_group_dict)
            except Exception, e:
                raise TacticException('Error updating login_in_group %s' % e.str())
