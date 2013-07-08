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

__all__ = ["TransactionState"]

import types

from pyasm.common import Xml
from search import SObject, Search, SObjectFactory
from transaction_log import TransactionLog
from transaction import Transaction

class TransactionState(SObject):

    SEARCH_TYPE = "sthpw/transaction_state"

    @staticmethod
    def get_by_ticket(ticket):
        search = Search(TransactionState)
        search.add_filter("ticket", ticket)
        state = search.get_sobject()

        # create the state data for this ticket
        if not state:
            state = SObjectFactory.create(TransactionState.SEARCH_TYPE)
            state.set_value("ticket", ticket)
            data = Xml()
            data.create_doc("state")
            state.set_value("data", data.to_string() )
            state.commit()

        return state


    def reset_state(my):
        data = Xml()
        data.create_doc("state")
        my.set_value("data", data.to_string() )


    def set_state(my, name, value):
        '''set a state outside of the whole transaction'''
        data = my.get_xml_value("data")
        node = data.get_node("state/%s" % name)

        root = data.get_root_node()
        element = data.create_text_element(name, str(value), node)
        data.append_child(root,element)

        my.set_value( "data", data.to_string() )

        return True


    def get_state(my, name):
        '''get a state value'''
        data = my.get_xml_value("data")
        value = data.get_value("state/%s" % name)
        return value





    def restore_state(my):
        '''
        <state>
        <project>bar</project>
        </state>
        '''
        data = my.get_xml_value("data")

        # restore project
        project_code = data.get_value("state/project")

        # if it doesn't exist, maybe it was set through some other means
        if not project_code:
            from pyasm.biz import Project
            project_code = Project.get_project_code()

        if not project_code:
            raise Exception("No project state defined")

        from pyasm.biz import Project
        Project.set_project(project_code)
        
        return True


