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
__all__ = ['IntrospectWdg','IntrospectSelectWdg', 'ProdIconButtonWdg', 
    'ProdIconSubmitWdg', 'SnapshotInfoWdg', 'SnapshotLabelWdg',
    'AssetLibrarySelectionWdg', 'SObjectSelectionWdg']


from pyasm.web import *
from pyasm.widget import *
from pyasm.search import Search, SObject
from pyasm.prod.biz import *
from pyasm.common import Container
from pyasm.prod.load import ProdLoaderContext

class ProdIconButtonWdg(IconButtonWdg):
    
    def __init__(my, name=None, icon=None, long=True, icon_pos="left"):
        super(ProdIconButtonWdg,my).__init__(name, icon, long, icon_pos)
        my.add_style("line-height: 14px")
        my.add_style("font-size: 0.8em")
        my.add_style("padding: 3px 10px 3px 10px")

class ProdIconSubmitWdg(IconSubmitWdg):
    
    def __init__(my, name=None, icon=None, long=True, icon_pos="left"):
        super(ProdIconSubmitWdg,my).__init__(name, icon, long, icon_pos)
        my.add_style("line-height: 14px")
        my.add_style("font-size: 0.8em")
        my.add_style("padding: 3px 10px 3px 10px")

class IntrospectWdg(ProdIconSubmitWdg):
    '''a widget that does introspection to analyze/update what 
        assets(versions) are loaded in the session of the app'''

    def __init__(my):
        super(IntrospectWdg, my).__init__("Introspect", long=True)
        my.add_style("height: 14px")
        my.add_style("font-size: 0.8em")
        #my.add_style("padding: 3px 10px 2px 10px")
        my.add_behavior({'type': "click", 'cbjs_action': "introspect(bvr)"})

class IntrospectSelectWdg(ProdIconSubmitWdg):
    '''a widget that does selected introspection to analyze/update 
        what assets(versions) are loaded in the session of the app'''

    def __init__(my):
        super(IntrospectSelectWdg, my).__init__("Introspect Select", long=True)
        my.add_style("height: 14px")
        my.add_style("font-size: 0.8em")
        my.add_event("onclick", "introspect_select()")

        
class SnapshotInfoWdg(BaseTableElementWdg):
    '''a widget that extracts the info of the xml snippet of a snapshot'''

    def preprocess(my):
        search_type_list  = SObject.get_values(my.sobjects, 'search_type', unique=True)
        search_id_dict = {}
        my.ref_sobject_cache = {}

        # initialize the search_id_dict
        for type in search_type_list:
            search_id_dict[type] = []
        # cache it first
        for sobject in my.sobjects:
            search_type = sobject.get_value('search_type')
            search_id_list = search_id_dict.get(search_type)
            search_id_list.append(sobject.get_value('search_id'))

        from pyasm.search import SearchException
        for key, value in search_id_dict.items():
            try:
                ref_sobjects = Search.get_by_id(key, value)
                sobj_dict = SObject.get_dict(ref_sobjects)
            except SearchException, e:
                print "WARNING: search_type [%s] with id [%s] does not exist" % (key, value)
                print str(e)
                sobj_dict = {}

            # store a dict of dict with the search_type as key
            my.ref_sobject_cache[key] = sobj_dict
            
            

    def get_display(my):
        search_type = my.get_current_sobject().get_value('search_type')
        search_id = my.get_current_sobject().get_value('search_id')

        sobject = None
        if my.ref_sobject_cache:
            sobj_dict = my.ref_sobject_cache.get(search_type)
            if sobj_dict:
                sobject = sobj_dict.get(str(search_id))
        else:
            sobject = Search.get_by_id(search_type, search_id)
        if sobject:
            if isinstance(sobject, ShotInstance):
                code = "%s-%s" %(sobject.get_value('shot_code'), sobject.get_code())
            elif sobject.has_value('name'):
                code = "%s-%s" %(sobject.get_value('name'), sobject.get_code())
            else:
                code = sobject.get_code()
        else:
            code = "n/a"

        return code
  

class SnapshotLabelWdg(BaseTableElementWdg):

    def get_snapshot(my, mode):
        ''' get the snapshot depending on the mode i.e. input, output'''
        dict = my.get_current_aux_data()
        output_snapshots = input_snapshots = None
        # the check for key is needed since snapshot can be None
        if dict and dict.has_key('%s_snapshots' %mode):
            if mode == 'output':
                output_snapshots = dict.get('%s_snapshots' %mode)
            else:
                input_snapshots = dict.get('%s_snapshots' %mode)
        else:
            sobject = my.get_current_sobject()
            context = my.get_context()
            loader = ProdLoaderContext()

            output_snapshots = loader.get_output_snapshots(sobject, context)
            input_snapshots = loader.get_input_snapshots(sobject, context)

            # this is for sharing with AssetLoaderWdg
            # should only be called once per sobject
            my.append_aux_data({'output_snapshots': output_snapshots, \
                'input_snapshots': input_snapshots})

        if mode == 'output':
            return output_snapshots
        else:
            return input_snapshots




    def get_context(my):
        context_select = Container.get('context_filter')
        context = 'publish'
        if context_select:
            context = context_select.get_value()
        if context == "":
            values = context_select.get_option('values')
            context = values[len(values)-1]
        return context
    
    def get_display(my):
        snapshot = my.get_snapshot('output')
        label = None
        if snapshot:
            label = snapshot.get_label()
        widget = Widget()
        if label:
            widget.add(IconWdg(label, eval('IconWdg.%s' %label.upper())))
        else:
            widget.add('')

        return widget
    
class AssetLibrarySelectionWdg(SelectWdg):
    
    def get_display(my):
        search = Search('prod/asset_library')
        my.set_search_for_options(search, 'code', 'title')
        my.set_option('web_state', 'true')
        my.add_empty_option()
        select = super(AssetLibrarySelectionWdg, my).get_display()
        
        span = SpanWdg(select)
        
        insert_wdg = IframeInsertLinkWdg(search.get_search_type())
        insert_wdg.set_refresh_mode("page")

        span.add(insert_wdg)
        return span


class SObjectSelectionWdg(SelectWdg):
    
    def get_display(my):
        search_type = my.get_option('search_type')
        if not search_type:
            return 
        search = Search(search_type)
        my.set_search_for_options(search, 'code', 'code')
        my.set_option('web_state', 'true')
        my.add_empty_option()
        select = super(SObjectSelectionWdg, my).get_display()
        span = SpanWdg(select)
        
        insert_wdg = IframeInsertLinkWdg(search.get_search_type())
        insert_wdg.set_refresh_mode("page")
        span.add(insert_wdg)
        return span
