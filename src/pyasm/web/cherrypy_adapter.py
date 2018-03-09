########################################################### #
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
        def index(self, **args):
            '''main method that returns the display'''
            return self.get_display()

    return CherryPyAppServer



def get_xmlrpc_server():
    '''dynamically load in an xmlrpc server'''

    class XmlrpcServer(object):
         def get_adapter(self):
            adapter = CherryPyAdapter()
            return adapter

    return XmlrpcServer




class CherryPyAdapter(WebEnvironment):
    """Encapsulates webware environment. Implements the web interface"""

    def __init__(self):
        self.request = cherrypy.request
        self.response = cherrypy.response

        if self.get_web_server() == "IIS":
            self.init_IIS()
        else:
            self.init_apache()


    def get_web_server(self):
        '''Yet another "check if this is Microsoft" method.
        NOTE: With ASAPI_rewrite forwarding, there really isn't anything to
        solid to key on, so we will use X-FORWAREDED-HOST'''
        check = self.get_env("HTTP_X_FORWARDED_HOST")
        if check:
            return "IIS"
        else:
            return "Apache"


    def init_IIS(self):

        # have to use the forwarded host
        host = self.get_env("HTTP_X_FORWARDED_HOST")

        # have to rebuild the request
        path = self.request.path
        query_string = self.request.query_string
        protocol = self.request.protocol
        if protocol.startswith("HTTPS"):
            protocol = "https"
        else:
            protocol = "http"

        if query_string:
            url = "%s://%s%s?%s" % (protocol, host, path, query_string)
        else:
            url = "%s://%s%s" % (protocol, host, path)

        self.set_env('HTTP_HOST', host)
        self.set_env('REQUEST_URI', url)


    def init_apache(self):
        # map envrionment varibles
        self.set_env('REQUEST_URI', self.request.browser_url)



    def get_context_name(self):
        '''this includes all of the subdirectories as well as the main
        context'''
        dir = self.request.path
        p = re.compile( r"/(tactic|projects)/?(\w+)/")
        m = p.search(dir)
        if not m:
            return "default"

        context = m.groups()[1]
        return context


    def restart(self):
        cherrypy.server.restart()



    def get_request_method(self):
        return self.request.method



    def set_content_type(self, content_type):
        self.response.headers['Content-Type'] = content_type


    def get_content_type(self, content_type):
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
        assert name
        if type(value) == types.UnicodeType:
            value = self._process_unicode(value)
        self.request.params[name] = value


    def get_form_data(self):
        return self.request.params


    def get_form_values(self, name, raw=False):
        '''returns a string list of the values of a form element.
        If raw is True, then a nonexistant value returns None'''
        try:
            values = self.request.params[name]
            if type(values) == types.UnicodeType:
                values = self._process_unicode(values)
                return [values]
            elif isinstance(values,basestring):
                return [values]
            elif type(values) in (types.IntType, types.FloatType, types.TypeType, types.BooleanType):
                return [values]
            elif values.__class__.__name__ in ["FieldStorage", "datetime"]:
                return [values]
            elif not values:
                return []
            elif type(values) == types.ListType:
                new_values = []
                for value in values:
                    if type(value) == types.UnicodeType:
                        value = self._process_unicode(value)
                    new_values.append(value)
                return new_values
            else:
                return [values]
        except KeyError:
            if raw == True:
                return None
            else:
                return []

    # DEPRECATED: this is no longer needed
    def _process_unicode(self, value):
        return value

        '''
        if not value:
            return value
        try:
            value = value.encode("ascii")
        except:
            chars = []
            for char in value:
                ord_value = ord(char)
                if ord_value > 128:
                    chars.append("&#%s;" % ord(char) )
                else:
                    chars.append(char)
            value = "".join(chars)

        return value
        '''




    def get_form_value(self, name, raw=False):
        '''returns the string value of the form element.
        If raw is True, then a nonexistant value returns None'''
        values = self.get_form_values(name,raw)
        if values == None:
            return None

        if values.__class__.__name__ == "FieldStorage":
            return values
        elif len(values) > 0:
            return values[0]
        else:
            return ""




    # cookie functions

    def set_cookie(self, name, value):
        """set a cookie"""
        cherrypy.response.simpleCookie[name] = value
        cherrypy.response.simpleCookie[name]['path'] = '/'
        cherrypy.response.simpleCookie[name]['max-age'] = 120*3600


    def get_cookie(self, name):
        """get a cookie"""
        try:
            return cherrypy.request.simpleCookie[name].value
            
        except KeyError, e:
            return ""


    def get_cookies(self):
        '''get a cookies'''
        try:
            return cherrypy.request.simpleCookie
            
        except KeyError, e:
            return ""




    # environment functions

    def get_env_keys(self):
        env = self.request.wsgi_environ
        return env.keys()



    def get_env(self, env_var):
        env = self.request.wsgi_environ
        return env.get(env_var)


    def set_env(self, env_var, value):
        self.request.wsgi_environ[env_var] = value






