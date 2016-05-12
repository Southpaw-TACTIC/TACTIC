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

from pyasm.search import SearchKey
from pyasm.command import Trigger


class LoginGroupTrigger(Trigger):

    def execute(my):

        input = my.get_input()
        mode = input.get("mode")

        if mode not in ['insert', 'update']:
            return

        search_key = input.get("search_key")
        sobj = SearchKey.get_by_search_key(search_key)

        if mode == "insert":
            login_group_name = sobj.get_value('login_group')

            if not login_group_name:
                raise Exception("A Group Name has not been entered. Please enter a Group Name.")

            sobj.set_value('name', login_group_name)

        elif mode == "update":
            login_group_name = sobj.get_value('name')

            if not login_group_name:
                login_group_name = sobj.get_value('login_group')

        login_group = login_group_name.lower()
        login_group = login_group.replace(" ", "_")

        sobj.set_value('login_group', login_group)
        sobj.set_value('code', login_group)

        sobj.commit(triggers=False)






