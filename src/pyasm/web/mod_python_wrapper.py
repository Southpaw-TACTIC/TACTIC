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


# NOTE: this has never been used
# DEPRECATED

from mod_python import util
from mod_python import Cookie

from web_environment import *


class ModPythonException(Exception):
    pass


class ModPython(WebEnvironment):
    """set of functions related to the web environment"""

    def __init__(self,req):
        # store the request handler
        self.request = req;

        # contains all the information in a form
        self.form = req.form


    def get_site_url(self):
        url = Url("/py")
        return url


    def get_context_name(self):
        return "pig"




    def get_form_keys(self):
        return self.get_field_storage().keys()


    def get_form_values(self, name):
        """ returns a string list of the values of a form element"""
        list = self.form.getlist(name)
        values = [ field.value for field in list ]
        return values


    def get_form_value(self, name):
        """returns the string value of the form element"""
        field = self.form.getfirst(name)
        if field != None:
            return field.value
        else:
            return ""



    def get_field_storage(self):
        return util.FieldStorage(self.request)

   
    def get_env_keys(self):
        env = self.request.subprocess_env
        return env.keys()

    def get_env(self, env_var):
        env = self.request.subprocess_env
        if env.has_key(env_var):
            return env[env_var]
        else:
            return ""


    def get_cookie(self, name):
        cookies = Cookie.get_cookies(self.request)
        cookie = cookies[name]
        if cookie == None:
            return ""
        else:
            self.error("cookie: "+cookie.value)
            return cookie.value

    def set_cookie(self, name, value):
        Cookie.add_cookie(self.request, name, value)





