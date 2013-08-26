###########################################################
#
# Copyright (c) 2005-2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['BaseRestHandler', 'TestCustomRestHandler', 'SObjectRestHandler']


from tactic.ui.common import BaseRefreshWdg

class BaseRestHandler(BaseRefreshWdg):

    def get_display(my):

        method = my.kwargs.get("Method")

        if method == "GET":
            ret_val = my.GET()
        elif method == "POST":
            ret_val = my.POST()
        elif method == "PUT":
            ret_val = my.PUT()
        elif method == "DELETE":
            ret_val = my.PUT()

        return ret_val



    def GET(my):
        pass

    def POST(my):
        return my.GET()

    def PUT(my):
        pass

    def DELETE(my):
        pass





class TestCustomRestHandler(BaseRestHandler):

    def GET(my):
        return "Test Custom GET"

    def POST(my):
        return "Test Custom POST"



from tactic_client_lib import TacticServerStub

class SObjectRestHandler(BaseRestHandler):

    def GET(my):
        method = my.kwargs.get("method")
        print my.kwargs
        print "method: ", method
        print "expression: ", my.kwargs.get("expression")


        # /rest/get_by_code/cars/CAR00009

        # /rest/query?search_type=sthpw/cars
        if method == "query":
            code = my.kwargs.get("data")
            from pyasm.search import Search
            sobject = Search.get_by_code(search_type, code)
            sobject_dict = sobject.get_sobject_dict()
            return sobject_dict

        # /rest/expression/@SOBJECT(sthpw/task)
        elif method == "expression":
            expression = my.kwargs.get("expression")
            server = TacticServerStub.get()
            return server.eval(expression)

        # /rest/simple_checkin?search_key=dfadfdsas&data={}
        elif method == "expression":
            expression = my.kwargs.get("expression")
            server = TacticServerStub.get()
            return server.eval(expression)


        return {}




