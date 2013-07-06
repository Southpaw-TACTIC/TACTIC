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

__all__ = ['UnittestTrigger']

from tactic_client_lib import TacticServerStub
from tactic_client_lib.interpreter import Handler
from pyasm.common import TacticException
from pyasm.prod.service import ApiException

class UnittestTrigger(Handler):

    def execute(my):
        server = TacticServerStub.get()
        server.start("Starting city insert trigger", "On inserting seoul, insert incheon")

        try:
            
            city_key = my.get_input_value("search_key")
            mode = my.get_input_value("mode")
            if mode == 'delete':
                return
            city  = server.get_by_search_key(city_key)
            if city.get('code') == 'seoul':
                # make sure triggers=False to avoid infinite loop
                server.insert('unittest/city', {'code': 'incheon', 'country_code': 'korea'}, triggers=False)

            if city.get('code') == 'incheon':
                raise TacticException('Should not have reached this point and fired this trigger.')

        except:
            server.abort()
            raise
        else:
            server.finish()

