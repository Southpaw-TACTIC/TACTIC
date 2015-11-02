###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['Handler']

import types

from pyasm.application.common import AppEnvironment


class Handler(object):

    def __init__(my):
        my.env = AppEnvironment.get()
        my.app = my.env.get_app()
        my.server = None
        my.input = {}
        my.output = {}

    def set_package(my, package):
        my.package = package

    def set_server(my, server):
        '''holds a reference to the Tactic server stub'''
        my.server = server

    def get_server(my):
        return my.server




    def get_value(my, path):
        parts = path.split("/")
        current = my.package
        for part in parts:
            current = current.get(part)
            # explict None comparison: empty string should go through
            if current == None:
                raise Exception("Part [%s] does not exist in package" % part)

        # if this is still a dictionary and it has __VALUE__ in it, the
        # get that value
        if type(current) == types.DictionaryType and current.has_key("__VALUE__"):
            current = current.get("__VALUE__")

        if type(current) == types.ListType:
            return current[0]
        else:
            return current

    def get_output(my):
        return my.output

    def set_input(my, input):
        my.input = input


    #
    # Data dump methods
    #




    #
    # Data accessor methods
    #

    def get_input_value(my, name):
        return my.input.get(name)

    def set_output_value(my, name, value):
        my.output[name] = value

    def get_output_value(my, name):
        return my.output.get(name)

    def get_package_value(my, path):
        return my.get_value(path)


    #
    # Implmentation method
    #

    def execute(my):
        '''method that does all of the work'''
        pass

    def undo(my):
        '''method that undos what execute just did'''
        pass


