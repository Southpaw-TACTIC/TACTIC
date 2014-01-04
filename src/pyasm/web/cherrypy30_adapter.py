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

__all__ = ['CherryPyException', 'CherryPyAdapter']


import types, os, re

from pyasm.common import TacticException
from web_environment import *

import cherrypy


class CherryPyException(Exception):
    pass


def get_app_server():

    server_cls = os.environ.get("TACTIC_SERVER_CLS")
    if not server_cls:
        from app_server import BaseAppServer
        base_cls = BaseAppServer
    elif server_cls == "pyasm.web.WidgetAppServer":
        from widget_app_server import WidgetAppServer
        base_cls = WidgetAppServer
    else:
        from simple_app_server import SimpleAppServer
        base_cls = SimpleAppServer

    class CherryPyAppServer(base_cls):

        def get_adapter(my):
            adapter = CherryPyAdapter()
            return adapter
            

        @cherrypy.expose()
        def index(my, **kwargs):
            my.hash = ()
            return my.get_display()


        # set the hash object as a list
        @cherrypy.expose()
        def default(my, *vpath, **kwargs):
            my.hash = vpath
            return my.get_display()




    return CherryPyAppServer



def get_xmlrpc_server():
    '''dynamically load in an xmlrpc server'''

    from cherrypy import _cptools
    class XmlrpcServer(_cptools.XMLRPCController):
         def get_adapter(my):
            adapter = CherryPyAdapter()
            return adapter

    return XmlrpcServer



from cherrypy_adapter import CherryPyAdapter as CherryPyAdapter20
class CherryPyAdapter(CherryPyAdapter20):
    """Encapsulates cherrypy environment. Implements the web interface"""

    def __init__(my):
        my.request = cherrypy.request
        my.response = cherrypy.response

        #my.request.wsgi_environ['REQUEST_URI'] = my.request.browser_url
        my.request.wsgi_environ['REQUEST_URI'] = cherrypy.url()


    def get_context_name(my):
        '''this includes all of the subdirectories as well as the main
        context'''
        dir = my.request.path_info
        p = re.compile( r"/(tactic|projects)/?(\w+)/")
        m = p.search(dir)
        if not m:
            return "default"

        context = m.groups()[1]
        return context


    def get_request_method(my):
        return my.request.method

    def get_request(my):
        return my.request

    def get_request_headers(my):
        return my.request.headers


    def get_response(my):
        return my.response

    def set_header(my, name, value):
        my.response.headers[name] = value

    def get_response(my):
        return my.response

    def set_content_type(my, content_type):
        my.response.headers['Content-Type'] = content_type

    def get_content_type(my, content_type):
        return my.response.headers['Content-Type']



    def set_force_download(my, filename):
        my.response.headers['Content-Type'] = "application/force-download"
        my.response.headers['Content-Disposition'] = "attachment; filename=%s" % filename


    def set_csv_download(my, filename):
        filename = os.path.basename(filename)
        my.response.headers['Content-Type'] = "text/x-csv"
        my.response.headers['Content-Disposition'] = "attachment; filename=%s" % filename



    # form submission functions
    def reset_form(my):
        my.request.params = {}
   
    def get_form_keys(my):
        return my.request.params.keys()

    def has_form_key(my, key):
        return my.request.params.has_key(key)

    def set_form_value(my, name, value):
        '''Set the form value to appear like it was submitted'''
        # protect from accidental null names.  This can occur when an
        # input widget has not name specified.
        if not name:
            return
        my.request.params[name] = value


    def get_form_data(my):
        return my.request.params



    # cookie functions

    def set_cookie(my, name, value):
        '''set a cookie'''
        cherrypy.response.cookie[name] = value
        cherrypy.response.cookie[name]['path'] = '/'
        cherrypy.response.cookie[name]['max-age'] = 120*3600


    def get_cookie(my, name):
        '''get a cookie'''
        try:
            return cherrypy.request.cookie[name].value
            
        except KeyError, e:
            return ""



    def get_cookies(my):
        '''get a cookies'''
        return cherrypy.request.cookie
            


    # environment functions
    """
    def get_env_keys(my):
        env = my.request.wsgi_environ
        return env.keys()



    def get_env(my, env_var):
        env = my.request.wsgi_environ
        return env.get(env_var)
    """



