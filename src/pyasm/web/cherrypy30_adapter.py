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

        def get_adapter(self):
            adapter = CherryPyAdapter()
            return adapter
            

        @cherrypy.expose()
        def index(self, **kwargs):
            self.hash = ()
            return self.get_display()


        # set the hash object as a list
        @cherrypy.expose()
        def default(self, *vpath, **kwargs):
            self.hash = vpath
            return self.get_display()




    return CherryPyAppServer



def get_xmlrpc_server():
    '''dynamically load in an xmlrpc server'''

    from cherrypy import _cptools
    class XmlrpcServer(_cptools.XMLRPCController):
         def get_adapter(self):
            adapter = CherryPyAdapter()
            return adapter

    return XmlrpcServer



from cherrypy_adapter import CherryPyAdapter as CherryPyAdapter20
class CherryPyAdapter(CherryPyAdapter20):
    """Encapsulates cherrypy environment. Implements the web interface"""

    def __init__(self):
        self.request = cherrypy.request
        self.response = cherrypy.response

        #self.request.wsgi_environ['REQUEST_URI'] = self.request.browser_url
        self.request.wsgi_environ['REQUEST_URI'] = cherrypy.url()


    def get_context_name(self):
        '''this includes all of the subdirectories as well as the main
        context. Preferabbly it gets the project_code. if not, site_code '''
        path = self.get_request_path()
        
        p = re.compile( r"/(tactic|projects)/?(\w+)/")
        m = p.search(path)
        if not m:
            return "default"

        from pyasm.security import Site
        site_obj = Site.get()
        path_info = site_obj.break_up_request_path(path)
        
        if path_info:
            context = path_info.get("project_code")
            
            if not context:
                context = path_info.get("site")
            
        else:
            context = m.groups()[1]

        return context


    def get_request_path(self):
        return self.request.path_info


    def get_request_method(self):
        return self.request.method

    def get_request(self):
        return self.request

    def get_request_headers(self):
        return self.request.headers


    def get_response(self):
        return self.response

    def set_header(self, name, value):
        self.response.headers[name] = value

    def get_response(self):
        return self.response

    def set_content_type(self, content_type):
        self.response.headers['Content-Type'] = content_type

    def get_content_type(self):
        return self.response.headers['Content-Type']



    def set_force_download(self, filename):
        self.response.headers['Content-Type'] = "application/force-download"
        self.response.headers['Content-Disposition'] = "attachment; filename=%s" % filename


    def set_csv_download(self, filename):
        filename = os.path.basename(filename)
        self.response.headers['Content-Type'] = "text/x-csv"
        self.response.headers['Content-Disposition'] = "attachment; filename=%s" % filename



    # form submission functions
    def reset_form(self):
        self.request.params = {}
   
    def get_form_keys(self):
        return self.request.params.keys()

    def has_form_key(self, key):
        return self.request.params.has_key(key)

    def set_form_value(self, name, value):
        '''Set the form value to appear like it was submitted'''
        # protect from accidental null names.  This can occur when an
        # input widget has not name specified.
        if not name:
            return
        self.request.params[name] = value


    def get_form_data(self):
        return self.request.params



    # cookie functions

    def set_cookie(self, name, value):
        '''set a cookie'''
        cherrypy.response.cookie[name] = value
        cherrypy.response.cookie[name]['path'] = '/'
        cherrypy.response.cookie[name]['max-age'] = 120*3600


    def get_cookie(self, name):
        '''get a cookie'''
        try:
            return cherrypy.request.cookie[name].value
            
        except KeyError, e:
            return ""



    def get_cookies(self):
        '''get a cookies'''
        return cherrypy.request.cookie
            


    # environment functions
    """
    def get_env_keys(self):
        env = self.request.wsgi_environ
        return env.keys()



    def get_env(self, env_var):
        env = self.request.wsgi_environ
        return env.get(env_var)
    """



