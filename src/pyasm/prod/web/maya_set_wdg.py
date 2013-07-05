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

from pyasm.common import *
from pyasm.search import Search
from pyasm.biz import Snapshot
from pyasm.command import *
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.biz import *
from shot_navigator_wdg import ItemsNavigatorWdg
from prod_wdg import *
from prod_checkin_wdg import *

import re

class MayaSetWdg(MayaCheckinWdg):
    '''widget desigend to rapidly and easily build sets'''

    CATEGORY = "set_category"
    NEW_SECTION = "new_section_name"
    PUBLISH_BUTTON = "Publish_Section"
    CREATE_BUTTON = "Create"
    CURRENT_SECTION = "current_set_section"
    MAX_ITEMS_PER_PAGE = 10
    ITEMS_NAV_LABEL = "Section Items"
    SEARCH_TYPE = "prod/asset"
    PUBLISH_TYPE = "set"

    def __init__(my,name=""):
        my.asset_type = "section"
        super(MayaSetWdg,my).__init__(name)


    def set_asset_type(my, asset_type):
        my.asset_type = asset_type

    def get_display(my):

        my.add("Category: ")

        search = Search("prod/asset_library")
        category_select = SelectWdg(my.CATEGORY)
        category_select.add_empty_option(label='-- Select Category --')
        category_select.set_search_for_options(search, "code", "title" )
        category_select.add_style("font-size: 0.9em")
        category_select.add_style("margin: 0px 3px")
        category_select.add_event("onchange", "document.form.submit()")
        category_select.set_persistence()
        my.add(category_select)

        current_category = category_select.get_value()
        if current_category == "":
            return super(MayaSetWdg,my).get_display()

        section_span = SpanWdg("Section: ", css='small')
        my.add(section_span)
        search = Search("prod/asset")
        search.add_filter("asset_library", current_category)
        search.add_filter("asset_type", my.asset_type)
        section_select = SelectWdg(my.CURRENT_SECTION)
        section_select.set_persistence()
        section_select.add_empty_option()
        section_select.add_event('onchange', "var item=document.form.elements['%s']; \
            if (item) {item.value='';} document.form.submit()" % my.ITEMS_NAV_LABEL)
        section_select.set_search_for_options(search, "get_full_name()", "name" )
        section_select.add_style("font-size: 0.9em")
        section_select.add_style("margin: 0px 3px")
        section_span.add(section_select)

        my.handle_create_set_asset()
         
        # get the current set and display the contents
        current_section_name = section_select.get_value()
        if current_section_name != "":
            section_code = current_section_name.split("|")[1]
            section = Asset.get_by_code(section_code)
            table = TableWdg("prod/asset", "load")
            table.set_sobject(section)
            my.add(table)
            
            # handle set contents
            if section:
                my.handle_contents(section)
                my.handle_add_instance(section)

        else:
            my.add(HtmlElement.h3("No section selected"))

        return super(MayaSetWdg,my).get_display()


    def handle_create_set_asset(my):

        div = DivWdg()

        context = my.get_context_filter_wdg()
        div.add(context)
        div.add_style("line-height: 4em")

        div.add("Create New %s: " % my.asset_type)
        
        div.add_style("border-bottom: 1px dashed #666")
        input = TextWdg(my.NEW_SECTION)
        div.add(input)

        button = ProdIconSubmitWdg(my.CREATE_BUTTON)
        button.add_event("onclick", "create_set( document.form.elements['%s'].value, \
            document.form.elements['%s'].value, document.form.elements['%s_context'].value)" \
            %(my.NEW_SECTION, my.CATEGORY, my.PUBLISH_TYPE))

        div.add(button)


        hint = HintWdg("First select the items to be included in the set, then click [Create]")
                
        div.add(hint)
        my.add(div)
        my.add(HtmlElement.br())

    def handle_contents(my, set):

        my.add(HtmlElement.br())
        
        # get all of the reference nodes
        snapshot = Snapshot.get_latest_by_sobject(set, "publish")
        if snapshot == None:
            my.add(HtmlElement.h3("No Contents"))
            return

        snapshot_xml = snapshot.get_xml_value("snapshot")
        ref_nodes = snapshot_xml.get_nodes("snapshot/ref")

        nav = ItemsNavigatorWdg(my.ITEMS_NAV_LABEL, \
            len(ref_nodes), my.MAX_ITEMS_PER_PAGE)
        items_range = nav.get_value()
        my.add(nav)
        
        introspect = IntrospectWdg()
        introspect.add_style('padding-bottom: 3px')
        my.add(introspect)
       
        
        # get the contents in the introspection
        session = SessionContents.get()
     
        
        start, end = 1 , my.MAX_ITEMS_PER_PAGE
        try:
            start, end = items_range.split("-")
        except Exception:
            pass    
        
        ref_nodes = ref_nodes[int(start)-1 : int(end)]
        sobjects = []
        info = []
        for node in ref_nodes:
            search_type = Xml.get_attribute(node,"search_type")
            search_id = Xml.get_attribute(node,"search_id")
            instance = Xml.get_attribute(node,"instance")
            version = Xml.get_attribute(node,"version")
            latest_context = Xml.get_attribute(node,"context")
            
            # get the latest snapshot
            #TODO: this query can be optimized
            
            latest = Snapshot.get_latest(search_type, search_id, \
                latest_context)
            if latest == None:
                latest_version = 0
            else:
                latest_version = latest.get_value("version")

            # add an icon
            if latest != None:
                sobject = latest.get_sobject()
            else:
                sobject = None
            session_version = session.get_version(instance)
            session_context = session.get_context(instance)

            sobjects.append(sobject)
            info.append({'session_version': session_version, \
                'session_context': session_context,  \
                'latest_context': latest_context, \
                'latest_version': latest_version, 'instance': instance})
        
        table = TableWdg('prod/asset','set_items')
        table.set_sobjects(sobjects)
        table.set_aux_data(info)
   
        my.add(table)





    def handle_add_instance(my, set):

        WebContainer.register_cmd("pyasm.prod.web.SetCheckinCbk")

        my.add(DivWdg("Comments:"))
        textarea = TextAreaWdg("description")
        textarea.set_attr("cols", "30")
        textarea.set_attr("rows", "2")
        my.add(textarea)

        set_name = set.get_value("name")
        
        button = ProdIconSubmitWdg(my.PUBLISH_BUTTON, long=True)
        button.add_event("onclick", "if (checkin_set('%s','%s')!=true) return" \
            % (set_name, set.get_code() ))
        my.add(button)


        

        # get all of the assets belonging to this set
        search = Search("prod/asset")
        search.add_regex_filter('code', set_name, op='EQ' )
        set_assets = search.do_search()

        #for set_asset in set_assets:
        #    print set_asset.get_value("name")














