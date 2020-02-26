###########################################################
#
# Copyright (c) 2020, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['ExternalService']

import tacticenv

import os

from pyasm.common import jsonloads, jsondumps
from pyasm.search import Search, SObject

class ExternalService(SObject):

    SEARCH_TYPE = "config/authenticate"

    def get_client_id(self):
        pass


    def get_client_secret(self):
        pass


    def get_base_dir(self):
        code = self.get_code()
        base_dir = "%s/authenticate/%s" % (tacticenv.get_data_dir(), code)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        return base_dir


    def get_url(self):
        path = "%s/url.txt" % self.get_base_dir()
        if os.path.exists(path):
            f = open(path, "r")
            url = f.read()
            f.close()
            return url

        raise Exception("No url specified")            



    def get_data_value(self, name):

        path = "%s/data.json" % self.get_base_dir()

        try:
            file_data = self.file_data
        except:
            file_data = None
            self.file_data = file_data

        if file_data is None and os.path.exists(path):
            f = open(path, "r")
            file_data = f.read()
            f.close()
            try:
                file_data = jsonloads(file_data)
            except:
                file_data = {}
        else:
            file_data = {}


        value = file_data.get(name)
        return value





