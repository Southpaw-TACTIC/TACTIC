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

__all__ = ['FilterData']

from pyasm.common import Container
from pyasm.web import WebContainer

from tactic.ui.common import BaseRefreshWdg
from pyasm.common import SetupException, Container, jsonloads, jsondumps

import types


class FilterData(object):
    '''Utility class to manipulate data used by filters.  The data is a global
    container one or more filters and filters make use of it to extract data.
    The reason for this class is that this data structured is marshalled to
    and from many locations, so it requires a centralized class to manage it.
    Also because the data structure is relatively flat, it can be annoying
    to extract data manually'''

    def __init__(self, data=[]):

        if not data:
            self.data = []
        elif type(data) in types.StringTypes:
            try:
                # optimize the loading of json data
                json_data = Container.get("json_data")
                if json_data == None:
                    json_data = {}
                    Container.put("json_data", json_data)

                self.data = json_data.get(data)
                if self.data == None:
                    self.data = jsonloads(data)
                    json_data[data] = self.data

            except ValueError, e:
                if e.__str__().find('No JSON object') != -1:
                    raise SetupException('Data is not decodable as JSON.')
                # try a straight eval
                self.data = eval(data)

            except Exception as e:
                 if e.__str__().find('cannot parse JSON description') != -1:
                    raise SetupException('Data is not valid JSON.')

        else:
            self.data = data

        # it takes care of different conditions that re-eval data as self.data
        if isinstance(self.data, dict):
            self.data = [self.data]

    def set_data(self, data):
        '''add data dictionary or a JSON string'''
        self.data = []
        # protect against empty spaces/lines from xml
        if isinstance(data, basestring):
            data = data.strip()
        if not data:
            return

        if isinstance(data, basestring):
            try:
                data = data.replace("'", '"')
                data = jsonloads(data)
            except ValueError, e:
                if e.__str__().find('No JSON object') != -1:
                    raise SetupException('Data is not decodable as JSON. [%s]'%data)
                # try a straight eval
                data = eval(data)

        if type(data) == types.ListType:
            for part in data:
                self.set_data(part)
        else:
            self.data.append(data)


    def add_data(self, data):
        '''add data dictionary.'''
        if type(data) in types.StringTypes:
            try:
                data = jsonloads(data)
            except ValueError, e:
                if e.__str__().find('No JSON object') != -1:
                    raise SetupException('Data is not decodable as JSON.')

                # try a straight eval
                data = eval(data)

        self.data.append(data)


    def set_to_cgi(self):
        web = WebContainer.get_web()
        data = jsondumps(self.data)
        web.set_form_value('json', data)
        Container.put("FilterData", self)


    def is_empty(self):
        '''serialize the data into a string'''
        if not self.data:
            return True
        return False



    def serialize(self):
        '''serialize the data into a string'''
        value = jsondumps(self.data)
        return value

    def get_data(self):
        return self.data
        

    def get_values_by_prefix(self, prefix):
        '''get data values for a specific prefix'''
        data = [] 
        for values in self.data:
            if values.get('prefix') == prefix:
                data.append(values)

        return data
            
    def get_values_by_index(self, prefix, filter_index=0):
        '''get data values for a specific prefix and index.
           The index refers to the index of the list that shares the
           same prefix'''
        count = 0
        for values in self.data:
            if not values.get('prefix') == prefix:
                continue

            if not count == filter_index:
                count += 1
                continue

            return values 

        return {}


    def get_values(self, prefix, name):
        '''Method to get the value from a certain prefix, regardless of
        index'''
        ret_values = []
        for values in self.data:
            if not values.get('prefix') == prefix:
                continue

            value = values.get(name)
            ret_values.append(value)


        return ret_values




    #
    # Static functions
    #
    def get_from_cgi(cls):
        # explicitly get from cgi.  Do not store
        web = WebContainer.get_web()
        data = web.get_form_value('json')
        filter_data = FilterData(data)
        return filter_data
    get_from_cgi = classmethod(get_from_cgi)

    def get(cls):
        filter_data = Container.get("FilterData")
        if filter_data == None:
            web = WebContainer.get_web()
            data = web.get_form_value('json')
            filter_data = FilterData(data)
            Container.put("FilterData", filter_data)
        return filter_data

    get = classmethod(get)





