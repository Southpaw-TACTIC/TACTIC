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

    def __init__(self):
        self.env = AppEnvironment.get()
        self.app = self.env.get_app()
        self.server = None
        self.input = {}
        self.output = {}

    def set_package(self, package):
        self.package = package

    def set_server(self, server):
        '''holds a reference to the Tactic server stub'''
        self.server = server

    def get_server(self):
        return self.server




    def get_value(self, path):
        parts = path.split("/")
        current = self.package
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

    def get_output(self):
        return self.output

    def set_input(self, input):
        self.input = input


    #
    # Data dump methods
    #




    #
    # Data accessor methods
    #

    def get_input_value(self, name):
        return self.input.get(name)

    def set_output_value(self, name, value):
        self.output[name] = value

    def get_output_value(self, name):
        return self.output.get(name)

    def get_package_value(self, path):
        return self.get_value(path)


    #
    # Implmentation method
    #

    def execute(self):
        '''method that does all of the work'''
        pass

    def undo(self):
        '''method that undos what execute just did'''
        pass


