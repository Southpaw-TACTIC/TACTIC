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
        search_key = input.get("search_key")

        sobj = SearchKey.get_by_search_key(search_key)
        login_group = sobj.get_value('login_group')
        sobj.set_value('code', login_group)

        sobj.commit(triggers=False)





