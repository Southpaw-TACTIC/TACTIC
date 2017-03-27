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

__all__ = ['BaseRestHandler', 'TestCustomRestHandler', 'SObjectRestHandler','APIRestHandler']

from pyasm.common import jsonloads
from tactic.ui.common import BaseRefreshWdg

import re

class BaseRestHandler(BaseRefreshWdg):

    def get_display(my):

        method = my.kwargs.get("Method")
        if not method:
            raise Exception("No method specified")

        if method == "GET":
            ret_val = my.GET()
        elif method == "POST":
            ret_val = my.POST()
        elif method == "PUT":
            ret_val = my.PUT()
        elif method == "DELETE":
            ret_val = my.PUT()
        else:
            ret_val = my.GET()

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




class APIRestHandler(BaseRestHandler):
    def get_content_type(my):
        return "application/json"

    def GET(my):

        return "TACTIC REST Interface"



    def POST(my):

        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        method = web.get_form_value("method")
        print "method: ", method

        # make sure there are no special characters in there ie: ()
        p = re.compile('^\w+$')
        if not re.match(p, method):
            raise Exception("Mathod [%s] does not exist" % method)


        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get()

        if not eval("server.%s" % method):
            raise Exception("Mathod [%s] does not exist" % method)


        keys = web.get_form_keys()

        kwargs = {}
        for key in keys:
            if key in ["method", "login_ticket", "password"]:
                continue

            if key == 'kwargs':
                args = web.get_form_value(key)
                args = jsonloads(args)
                for name, value in args.items():
                    kwargs[name] = value
            else:
                kwargs[key] = web.get_form_value(key)

        call = "server.%s(**kwargs)" % method


        return eval(call)






