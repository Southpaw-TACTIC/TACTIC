###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['ForeignKeyElementWdg']

import re

from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, WikiUtil
from pyasm.biz import Schema, Project, NamingUtil
from tactic.ui.common import SimpleTableElementWdg

class ForeignKeyElementWdg(SimpleTableElementWdg):


    def init(my):
        my.parents_dict = {}
        my.td = None


    def get_args_keys(cls):
        return {
        }
    get_args_keys = classmethod(get_args_keys)



    def is_editable(my):
        return True



    def get_column(my):
        column = my.get_option('column')
        if not column:
            column = my.get_name()

        return column


    def get_relations(my, sobjects):

        if not sobjects:
            return {}

        column = my.get_column()
        
        if not column.endswith('_id'):
            return {}


        search_ids = [x.get_value(column) for x in sobjects]
        table = column.replace("_id", "")

        project_code = Project.get_project_code()

        # look at the first ones search type for the namespace
        sobject = sobjects[0]
        search_type_obj = sobject.get_search_type_obj()
        namespace = search_type_obj.get_value("namespace")

        parent_type = my.get_option('search_type')
        if not parent_type:
            parent_type = "%s/%s" % (namespace, table)
            # parent_type = "%s/%s" % (project_code, table)

        # NOTE: this is just to fix a bug in MMS.  When updating the
        # personal_time_log, the crossover to sthpw causes a stack trace
        #if parent_type == 'MMS/login':
        #    parent_type = 'sthpw/login'


        search = Search(parent_type)
        search.add_filters("id", search_ids)
        parents = search.get_sobjects()

        parents_dict = {}
        for parent in parents:
            id = parent.get_id()
            parents_dict[id] = parent

        return parents_dict



    def preprocess(my):

        sobject = my.get_current_sobject()

        my.parents_dict = my.get_relations(my.sobjects)


    def set_td(my, td):
        my.td = td


    def get_text_value(my):
        '''for csv export'''
        my.preprocess()
        sobject = my.get_current_sobject()
        result = my._get_result(sobject)
        return result


    def _get_result(my, sobject):

        # get the parent or relation
        column = my.get_column()
        parent_id = sobject.get_value(column)
        parent = my.parents_dict.get(parent_id)
        if not parent:
            return super(ForeignKeyElementWdg,my).get_display()


        template = my.get_option('template')
        # if not set, then look at the schema
        if not template:
            schema = Schema.get_by_project_code( Project.get_project_code() )
            search_type = parent.get_base_search_type()
            template = schema.get_attr_by_search_type(search_type,'display_template')

        if template:
            value = NamingUtil.eval_template(template, sobject, parent=parent)
        else:
            # NOTE: put something ... anything as a default
            columns = parent.get_search_type_obj().get_columns()
            if not len(columns):
                value = parent.get_value(columns[0])
            else:
                value = parent.get_value(columns[1])

        return value


    def handle_td(my, td):
        td.set_attr("spt_input_value",my.value)


    def get_display(my):
        sobject = my.get_current_sobject()
        my.value = my._get_result(sobject)
        my.set_value(my.value)


        #print "setting: ", my.get_value()
        div = DivWdg()
        display_value = WikiUtil().convert(my.value)
        div.add(my.value)
        return div




