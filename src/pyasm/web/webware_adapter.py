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

#
# DEPRECATED
#



__all__ = ['get_app_server', 'get_xmlrpc_server', 'WebWareException', 'WebWare', 'WebWareXmlrpcAdapter']

import types, os

from WebKit.Page import Page

from pyasm.common import Config
from pyasm.web import Url

from web_environment import *

class WebWareException(Exception):
    pass



def get_app_server():
    '''dynamically load in the appserver classes'''
    from app_server import BaseAppServer
    from WebKit.Page import Page
    class AppServer(Page, BaseAppServer):

        def get_adapter(self):
            adapter = WebWare(self)
            return adapter


        def writeHTML(self):
            self.writeln( self.get_display() )

    return AppServer




def get_xmlrpc_server():
    '''dynamically load in an xmlrpc server'''
    from WebKit.XMLRPCServlet import XMLRPCServlet

    class XmlrpcServer(XMLRPCServlet):
        def get_adapter(self):
            adapter = WebWareXmlrpcAdapter(self.transaction())
            return adapter

    return XmlrpcServer


           

class WebWare(WebEnvironment):
    """Encapsulates webware environment. Implements the web interface"""

    def __init__(self,page):
        super(WebWare,self).__init__()
        self.request = page.request()
        self.response = page.response()


    def get_context_name(self):
        '''this includes all of the subdirectories as well as the main
        context'''
        dir = self.request.urlPathDir()

        # strip of the / at the front and the back
        dir = dir.rstrip("/")
        dir = dir.lstrip("/")
        return dir




    # form submission methods
    #def reset_form(self):
    #    return self.request.fields() = {}

    def get_form_keys(self):
        return self.request.fields().keys()

    def has_form_key(self, key):
        return self.request.fields().has_key(key)

    def set_form_value(self, name, value):
        '''Set the form value to appear like it was submitted'''
        self.request.setField(name, value)


    def get_form_values(self, name, raw=False):
        """returns a string list of the values of a form element.
        If raw is True, then a nonexistant value returns None"""
        
        if self.request.hasValue(name):
            values = self.request.value(name)
            if isinstance(values, basestring):
                values = values.decode('utf-8')
                values = self._process_unicode(values)
                return [values]
            elif isinstance(values, list):
                new_values = []
                for value in values:
                    if isinstance(value, basestring):
                        value = self._process_unicode(value.decode('utf-8'))
                    new_values.append(value)
                return new_values
            else: # this can be a FieldStorage instance
                return values
        else:
            if raw == True:
                return None
            else:
                return []


    def get_form_value(self, name, raw=False):
        """returns the string value of the form element.
        If raw is True, then a nonexistant value returns None"""
        values = self.get_form_values(name,raw)
        if values == None:
            return None

        if values.__class__.__name__ == "FieldStorage":
            return values
        elif len(values) > 0:
            return values[0]
        else:
            return ""

    def _process_unicode(self, value):
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

    # cookie methods


    def set_cookie(self, name, value):
        """set a cookie"""
        self.response.setCookie(name, value, expires="NEVER")


    def get_cookie(self, name):
        """get a cookie"""
        if self.request.hasCookie(name):
            return self.request.cookie(name)
        else:
            return ""


    # environment methods

    def get_env_keys(self):
        env = self.request.environ()
        return env.keys()

    def get_env(self, env_var):
        env = self.request.environ()
        return env.get(env_var)





class WebWareXmlrpcAdapter(WebWare):

    def __init__(self, transaction):
        # NOTE: the call to WebWare's super is intentional
        super(WebWare,self).__init__()
        self.request = transaction.request()
        self.response = transaction.response()





