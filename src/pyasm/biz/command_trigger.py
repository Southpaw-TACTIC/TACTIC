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

__all__ = ["CommandSObj", "Trigger", "TriggerSObj", "TriggerInCommand"]


from pyasm.search import SObject, Search

class CommandSObj(SObject):

    SEARCH_TYPE = "sthpw/command"

    def get_primary_key(self):
        return "class_name"

    def get_description(self):
        return self.get_primary_key_value() 

    # static methods 
    def get_by_class_name(name):
        search = Search( CommandSObj.SEARCH_TYPE )
        search.add_filter("class_name", name)
        sobj = search.get_sobject()
        return sobj
    get_by_class_name = staticmethod(get_by_class_name)
    


class TriggerSObj(SObject):

    SEARCH_TYPE = "sthpw/trigger"

    def get_search_columns():
        return ['event','class_name']
    get_search_columns = staticmethod(get_search_columns)

    def get_required_columns():
        '''for csv import'''
        return ['event','class_name']
    get_required_columns = staticmethod(get_required_columns)

    def get_primary_key(self):
        return "class_name"

    def get_description(self):
        return self.get_primary_key_value()   

     
class Trigger(TriggerSObj):
    #DEPRECATED   
    pass 

class TriggerInCommand(SObject):

    SEARCH_TYPE = "sthpw/trigger_in_command"

    def get_by_command_code(command_code):
        search = Search(TriggerInCommand.SEARCH_TYPE)
        search.add_filter("command_code", command_code)
        return search.get_sobjects()
    get_by_command_code = staticmethod(get_by_command_code)
   
  



