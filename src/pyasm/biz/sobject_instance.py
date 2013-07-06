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

__all__ = ["SObjectInstance"]


from pyasm.common import Xml
from pyasm.search import SearchType, Search, SObject

from schema import Schema
from project import Project


class SObjectInstance(SObject):

    def get_by_sobject(cls, sobject, related_search_type):
        '''Get all by sobject respecting hierarchy'''
        project_code = sobject.get_project_code()
        schema = Schema.get_by_code(project_code)
        if not schema:
            return []

        sobject_code = sobject.get_code()
        foreign_key = sobject.get_foreign_key()
        search_type = sobject.get_base_search_type()

        related_search_type_obj = SearchType.get(related_search_type)
        related_key = related_search_type_obj.get_foreign_key()

        # get the instance search type
        parent_search_type = schema.get_parent_type(search_type)
        instance_type = schema.get_instance_type(search_type, related_search_type)

        # get all of the instances
        search = Search(instance_type)
        search.add_filter(foreign_key, sobject_code)
        instances = search.get_sobjects()

        # if there is no parent, then return the regular search result
        if not parent_search_type:
            return instances


        # find the parent of the sobject
        parent = sobject.get_parent( parent_search_type )
        if not parent:
            return []



        # get the instances from the parent
        parent_code = parent.get_code()
        parent_foreign_key = parent.get_foreign_key()

        # get all of the parent instances
        parent_instance_type = schema.get_instance_type(parent_search_type, related_search_type)
        search = Search(parent_instance_type)
        search.add_filter(parent_foreign_key, parent_code)
        parent_instances = search.get_sobjects()

        # convert the parent instances into child instances
        final_instances = []
        for parent_instance in parent_instances:

            related_code = parent_instance.get_value(related_key)

            for instance in instances:
                if instance.get_value(foreign_key) == sobject_code \
                        and instance.get_value(related_key) == related_code:
                    break
            else:
                # dynamically create new instances that do not exist
                instance = SearchType.create(instance_type)
                for name, value in parent_instance.data.items():
                    if name == "id":
                        continue
                    if name == parent_foreign_key:
                        continue
                    if value == None:
                        continue
                    instance.set_value(name, value)
                instance.set_value(foreign_key, sobject_code)
                instance.commit()

            final_instances.append(instance)

        return final_instances

    get_by_sobject = classmethod(get_by_sobject)






