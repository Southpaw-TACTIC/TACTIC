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

        def get_adapter(my):
            adapter = WebWare(my)
            return adapter


        def writeHTML(my):
            my.writeln( my.get_display() )

    return AppServer




def get_xmlrpc_server():
    '''dynamically load in an xmlrpc server'''
    from WebKit.XMLRPCServlet import XMLRPCServlet

    class XmlrpcServer(XMLRPCServlet):
        def get_adapter(my):
            adapter = WebWareXmlrpcAdapter(my.transaction())
            return adapter

    return XmlrpcServer


           

class WebWare(WebEnvironment):
    """Encapsulates webware environment. Implements the web interface"""

    def __init__(my,page):
        super(WebWare,my).__init__()
        my.request = page.request()
        my.response = page.response()


    def get_context_name(my):
        '''this includes all of the subdirectories as well as the main
        context'''
        dir = my.request.urlPathDir()

        # strip of the / at the front and the back
        dir = dir.rstrip("/")
        dir = dir.lstrip("/")
        return dir




    # form submission methods
    #def reset_form(my):
    #    return my.request.fields() = {}

    def get_form_keys(my):
        return my.request.fields().keys()

    def has_form_key(my, key):
        return my.request.fields().has_key(key)

    def set_form_value(my, name, value):
        '''Set the form value to appear like it was submitted'''
        my.request.setField(name, value)


    def get_form_values(my, name, raw=False):
        """returns a string list of the values of a form element.
        If raw is True, then a nonexistant value returns None"""
        
        if my.request.hasValue(name):
            values = my.request.value(name)
            if isinstance(values, basestring):
                values = values.decode('utf-8')
                values = my._process_unicode(values)
                return [values]
            elif isinstance(values, list):
                new_values = []
                for value in values:
                    if isinstance(value, basestring):
                        value = my._process_unicode(value.decode('utf-8'))
                    new_values.append(value)
                return new_values
            else: # this can be a FieldStorage instance
                return values
        else:
            if raw == True:
                return None
            else:
                return []


    def get_form_value(my, name, raw=False):
        """returns the string value of the form element.
        If raw is True, then a nonexistant value returns None"""
        values = my.get_form_values(name,raw)
        if values == None:
            return None

        if values.__class__.__name__ == "FieldStorage":
            return values
        elif len(values) > 0:
            return values[0]
        else:
            return ""

    def _process_unicode(my, value):
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


    def set_cookie(my, name, value):
        """set a cookie"""
        my.response.setCookie(name, value, expires="NEVER")


    def get_cookie(my, name):
        """get a cookie"""
        if my.request.hasCookie(name):
            return my.request.cookie(name)
        else:
            return ""


    # environment methods

    def get_env_keys(my):
        env = my.request.environ()
        return env.keys()

    def get_env(my, env_var):
        env = my.request.environ()
        return env.get(env_var)





class WebWareXmlrpcAdapter(WebWare):

    def __init__(my, transaction):
        # NOTE: the call to WebWare's super is intentional
        super(WebWare,my).__init__()
        my.request = transaction.request()
        my.response = transaction.response()





