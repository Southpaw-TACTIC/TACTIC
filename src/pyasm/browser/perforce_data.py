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

__all__ = ['PerforceData']

import binascii, marshal

from pyasm.common import *
from pyasm.web import WebContainer


class PerforceData(Base):
    '''get data from cgi passed in from the PerforceApplet'''

    def __init__(my, sobject):
        my.sobject = sobject

        my.all_data = {}


    def _get_data(my, key):
        '''gets the data from cgi and unmarshals it into a python dictionary'''
        web = WebContainer.get_web()

        name = my.sobject.get_value("name")

        data = []

        # get the data
        value = web.get_form_value("%s_%s" % (key,name) )
        if not value:
            return data

        value = binascii.unhexlify(value)


        current = 1
        is_first = True
        while 1:
            index = value.find("{s", current)
            if index == -1:
                if is_first:
                    index = len(value)
                    is_first = False
                else:
                    break
            tmp = value[current-1:index]

            if not tmp:
                break


            tmp_data = marshal.loads(tmp)
            data.append(tmp_data)

            current = index+1

        return data
 


    def process_all_data(my):
        web = WebContainer.get_web()

        for type in ("workspaces", "have"):
            data = my._get_data(type)
            my.all_data[type] = data


    def get_data(my, type, index=0):
        return my.all_data[type][index]


    def get_value(my, type, key, index=0):
        return my.all_data[type][index][key]

    def get_values(my, type, key):
        values = []
        for data in my.all_data[type]:
            values.append(data[key])
        return values





