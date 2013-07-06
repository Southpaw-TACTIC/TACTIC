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

    def __init__(my,req):
        # store the request handler
        my.request = req;

        # contains all the information in a form
        my.form = req.form


    def get_site_url(my):
        url = Url("/py")
        return url


    def get_context_name(my):
        return "pig"




    def get_form_keys(my):
        return my.get_field_storage().keys()


    def get_form_values(my, name):
        """ returns a string list of the values of a form element"""
        list = my.form.getlist(name)
        values = [ field.value for field in list ]
        return values


    def get_form_value(my, name):
        """returns the string value of the form element"""
        field = my.form.getfirst(name)
        if field != None:
            return field.value
        else:
            return ""



    def get_field_storage(my):
        return util.FieldStorage(my.request)

   
    def get_env_keys(my):
        env = my.request.subprocess_env
        return env.keys()

    def get_env(my, env_var):
        env = my.request.subprocess_env
        if env.has_key(env_var):
            return env[env_var]
        else:
            return ""


    def get_cookie(my, name):
        cookies = Cookie.get_cookies(my.request)
        cookie = cookies[name]
        if cookie == None:
            return ""
        else:
            my.error("cookie: "+cookie.value)
            return cookie.value

    def set_cookie(my, name, value):
        Cookie.add_cookie(my.request, name, value)





