###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['ProcessElementWdg', 'SubContextElementWdg']

from pyasm.web import Widget, DivWdg, HtmlElement
from pyasm.widget import SelectWdg, TextWdg
from pyasm.search import Search, SearchType, SObject, SearchKey, SearchException
from pyasm.biz import Project, Pipeline
from pyasm.common import Environment, SObjectSecurityException

from tactic.ui.common import BaseTableElementWdg, SimpleTableElementWdg

class ProcessElementWdg(SimpleTableElementWdg):
    ARGS_KEYS = {}

    """
    def alter_order_by(my, search, direction=''):
        '''handle order by'''
        search.add_order_by("status", direction)
    """
    
    def handle_td(my, td):
        sobj = my.get_current_sobject()
        parent = None
        
        value = sobj.get_value('process')
        td.add_attr('spt_input_value', value)

        if sobj.is_insert():
            state = my.get_state()
            parent_key = state.get('parent_key')
            if parent_key:
                parent = SearchKey.get_by_search_key(parent_key)
        else:
            # get the parent pipeline code
            try:
                parent = sobj.get_parent()
            except SObjectSecurityException, e:
                print "SObjectSecurityException raised for getting parent of [%s]" %sobj.get_code()
                pass
            except SearchException, e:
                if e.__str__().find('not registered') != -1:
                    pass
                elif e.__str__().find('does not exist for database') != -1:
                    pass    
                else:
                    raise
            except Exception, e:
                print "WARNING: ", e


        if parent:
            pipeline_code = parent.get_value("pipeline_code", no_exception=True)
            if pipeline_code:
                td.add_attr('spt_pipeline_code', pipeline_code)
            


    def process_sobjects(sobjects, search=None):
        '''process sobjects order according to pipeline process order'''
        if not sobjects:
            return
        if search:
            order_list = search.get_order_bys()
            
            # it could be search_type asc or search_tpe desc
            # that means the user has applied an order by in some specific column
            if order_list and not order_list[0].startswith('search_type'):
                return
        parent = None
        last_parent = None
        last_parent_key = None

        parents = []
        groups = []
        group = None

        # group tasks according to parent
        for i, sobject in enumerate(sobjects):
            # get the parent key
            search_type = sobject.get_value("search_type")
            search_id = sobject.get_value("search_id")
            parent_key = "%s|%s" % (search_type, search_id)
            process = sobject.get_value('process')
            
            
            if parent_key != last_parent_key:
                parent = SearchKey.get_by_search_key(parent_key)
                parents.append(parent)
                group = []
                groups.append(group)

            group.append(sobject)
            
            last_parent_key = parent_key

        new_sobjects = []

        # reorder each group
        for i, group in enumerate(groups):
            parent = parents[i]
            processes = []
            if parent:
                pipeline_code = parent.get_value("pipeline_code")
                pipeline = Pipeline.get_by_code( pipeline_code )
                if pipeline:
                    processes = pipeline.get_process_names(recurse=True)
            
            if processes:
                # build a sorting key dict
                sort_dict = {}
                for sobject in group:
                    process = sobject.get_value('process')
                    try:
                        sort_dict[sobject] = processes.index(process)
                    except ValueError:
                        # put at the bottom for outdated processes
                        # this is important to still display tasks with outdated processe names
                        sort_dict[sobject] = len(processes)

                sorted_group = sorted(group, key=sort_dict.__getitem__)

                new_sobjects.extend(sorted_group)
            else:
                new_sobjects.extend(group)

       
        return new_sobjects
    process_sobjects = staticmethod(process_sobjects)


class SubContextElementWdg(BaseTableElementWdg):

    def is_editable(cls):
        '''Determines whether this element is editable'''
        return True
    is_editable = classmethod(is_editable)

    def _get_subcontext(my):
        sobject = my.get_current_sobject()
        context = sobject.get_value("context")
        if not context:
            return ""

        if context.find("/") == -1:
            return ""

        base, subcontext = context.split("/", 1)

        return subcontext
    
    def handle_td(my, td):
        subcontext =  my._get_subcontext()

        if subcontext:
            td.add_attr('spt_input_value', subcontext)

    def get_display(my):
        return my._get_subcontext()
            


