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

__all__ = [ 'SObjectGroupUtil', 'ParentGroupTableElementWdg', 'ParentGroupAction' ]

import re, time, types

from pyasm.common import Environment
from pyasm.search import SObject, Search, SearchException, SearchKey, SearchType
from pyasm.web import WebContainer, Widget, DivWdg, SpanWdg, FloatDivWdg, Table
from pyasm.widget import ExpandableTextWdg, SwapDisplayWdg, IconWdg, ThumbWdg, ProdIconButtonWdg, HiddenWdg
from tactic.ui.common import BaseTableElementWdg


class SObjectGroupUtil(object):
    '''container widget groupings in tables'''

    def __init__(my):
        my.prev_sobj = None


    def is_new_group(my, prev_sobj, sobj):
        '''check if this task belong to a new parent ''' 
        if not prev_sobj:
            return True

        # let the widget determine if it is new
        is_new = my.widget.is_new_group(prev_sobj, sobj)
        if is_new != None:
            return is_new


        # if it is None, use the default
        prev_value = prev_sobj.get_value(my.column)
        sobj_value = sobj.get_value(my.column, no_exception=True)


        # Now check for timestamp values and if found group by each calendar day (as default behavior),
        # otherwise you get one grouping for each row if the time part of the timestamp is not the same ...
        #
        st = sobj.get_search_type()
        value_type = SearchType.get_tactic_type(st, my.column)
        
        if value_type == 'timestamp':
            from dateutil import parser

            prev_date = parser.parse(prev_value)  # returns a datetime object
            sobj_date = parser.parse(sobj_value)  # returns a datetime object

            prev_value = "%s-%s-%s" % (prev_date.year, str(prev_date.month).zfill(2), str(prev_date.day).zfill(2))
            sobj_value = "%s-%s-%s" % (sobj_date.year, str(sobj_date.month).zfill(2), str(sobj_date.day).zfill(2))


        # compare search key here 
        if prev_value == sobj_value:
            return False
        else:
            return True


    def set_widget(my, widget):
        my.widget = widget

    def set_sobject(my, sobject):
        my.sobject = sobject


    def get_group_wdg(my):
        assert my.widget

        if not my.sobject:
            my.sobject = my.widget.get_current_sobject()

        assert my.sobject


        my.column = my.widget.get_name()
        #if not my.column:
        #    my.column = web.get_form_value(my.parent_wdg.get_order_by_id() )

        div = None

        if my.is_new_group(my.prev_sobj, my.sobject):
            div = DivWdg()
            div.add_style("width: 100%")

            group_wdg = my.widget.get_group_wdg(my.prev_sobj)
            if group_wdg:
                if type(group_wdg) in types.StringTypes:
                    div.add( group_wdg )
                else:
                    div.add( group_wdg.get_buffer_display() )

            else:
                value = my.sobject.get_value(my.column, no_exception=True)
                if not value:
                    value = "-- empty --"

                value = my.widget.get_buffer_display()

                column_div = DivWdg()
                div.add(column_div)
                column_div.add_style("float: left")
                column_div.add( "<i style='color: #666'/>%s:</i> &nbsp;&nbsp;" % my.column )
                div.add( value )
                div.add_style("font-weight: bold")
                div.add_style("font-size: 1.1em")


        my.prev_sobj = my.sobject
        #print my.sobject.get_code(), my.sobject.get_search_key()
        return div

     
    
class ParentGroupTableElementWdg(BaseTableElementWdg):
    '''shows which sobject this sobject is attached to'''

    def init(my):
        my.last_search_key = None
        my.swaps = []
        my.row_ids = []
        my.empty = True
        my.is_preprocessed = False
        my.preprocess()

    #def is_in_column(my):
    #    return False

    def is_groupable(my):
        return True

    def is_editable(my):
        return False

    def get_text_value(my):
        sobject = my.get_current_sobject()
        parent = sobject.get_parent()
        if parent:
            return parent.get_code()
        else:
            return ''


    def alter_search(my, search):
        # remove the limit to get all the parents' id
        # add reapply the limit later.. This is needed for an accurate
        # result when limit and offset is applied later

        # IS THIS EVEN CALLED??
        sdfsadfasfd

        limit = search.get_select().limit 
        search.set_limit(None)
        
        # do a quick and dirty presearch search
        sobjects = search.get_sobjects()
        search.set_search_done(False)
        # HACK: reset order bys
        search.get_select().order_bys = []
        if not sobjects:
            return
        search.set_limit(limit)
        
        
        # get the parent type
        sobject = sobjects[0]
        parent_type = sobject.get_value("search_type")
        search_type_obj = SearchType.get(parent_type)
        # DO NOT USE base key or it won't search properly for multi project
        #parent_type = search_type_obj.get_base_key()

        parent_ids = [x.get_value("search_id") for x in sobjects]

        #parent_type = 'prod/asset'
        parent_search = Search(parent_type)
        parent_search.add_filters("id", parent_ids)
        parent_search.add_order_by("code")

        parents = parent_search.get_sobjects()

        ids = [x.get_id() for x in parents]

        search.add_enum_order_by("search_id", ids)
        search.get_sobjects()
        search.add_order_by("description")



    '''
    def post_alter_search(my, sobjects):
        #sobjects = search.get_sobjects()
        if not sobjects:
            return

        column = 'code'
        def compare(sobject1, sobject2):
            code1 = sobject1.get_value(column)
            code2 = sobject2.get_value(column)
            return cmp(code1, code2)

        sobjects.sort(compare)
        for sobject in sobjects:
            print sobject.get_code()

    '''        


       

    def preprocess(my):
        
        # protect against the case where there is a single sobject that
        # is an insert (often seen in "insert")
        if my.is_preprocessed == True:
            return

        skip = False
        if len(my.sobjects) == 1:
            if not my.sobjects[0].has_value("search_type"):
                skip = True

        if not skip:
            search_types = SObject.get_values(my.sobjects, 'search_type', unique=True)

            try:
                search_codes = SObject.get_values(my.sobjects, 'search_code', unique=True)
                search_ids = None
            except Exception, e:
                print "WARNING: ", e
                search_ids = SObject.get_values(my.sobjects, 'search_id', unique=True)
                search_codes = None
        else:
            search_types = []
            search_codes = []


        # if there is more than one search_type, then go get each parent
        # individually
        # NOTE: this is very slow!!!!
        ref_sobjs = []
        if len(search_types) > 1:
            ref_sobjs = []
            for tmp_sobj in my.sobjects:
                try:
                    ref_sobj = tmp_sobj.get_parent()
                    if ref_sobj:
                        ref_sobjs.append(ref_sobj)
                    else:
                        warning = "Dangling reference: %s" % tmp_sobj.get_search_key()
                        Environment.add_warning(warning, warning)
                except SearchException, e:
                    # skips unknown search_type/project
                    print e.__str__()
                    continue

        elif len(search_types) == 1:
            search_type =  my.sobjects[0].get_value("search_type")
            try:
                if search_codes != None:
                    ref_sobjs = Search.get_by_code(search_type, search_codes)
                else:
                    ref_sobjs = Search.get_by_id(search_type, search_ids)
            except SearchException, e:
                # skips unknown search_type/project
                print e.__str__()
                pass

        # TODO: None defaults to search_key, should be empty
        my.ref_sobj_dict = SObject.get_dict(ref_sobjs, None)

        # when drawn as part of a TbodyWdg, we want to disable the calculation
        # of most things so that it will not try to display a prev row
        if my.get_option('disable') == 'true':
            my.ref_sobj_dict = None
            my.empty = True
  
        my.is_preprocessed = True

    #def handle_td(my, td):
    #    td.add_class("task_spacer_column")
    #    td.add_style("font-weight: bold")
    #    if my.empty:
    #        td.add_style("border-top: 0px")

    def is_new_group(my, prev_sobj, sobj):
        '''check if this task belong to a new parent ''' 
        if not prev_sobj:
            return True
        prev_ref_sobj = my.get_ref_obj(prev_sobj)
        ref_sobj = my.get_ref_obj(sobj)
             
        if not prev_ref_sobj or not ref_sobj:
            return False
        # compare search key here 
        if prev_ref_sobj.get_search_key() == ref_sobj.get_search_key():
            return False
        else:
            return True


           
    def get_group_wdg(my, prev_sobj):
        if not my.is_preprocessed:
            my.preprocess()

        sobject = my.get_current_sobject()
        ref_sobj = my.get_ref_obj(sobject)
        my.current_ref_sobj = ref_sobj
        
        if not ref_sobj:
            return "Undetermined parent: [%s]" % SearchKey.get_by_sobject(sobject)

        widget = DivWdg()

        # add add button
        #from tactic.ui.widget import TextBtnWdg, TextBtnSetWdg
        #buttons_list = []
        #buttons_list.append( {
        #    'label': '+', 'tip': 'Add Another Item',
        #    'bvr': { 'cbjs_action': "spt.dg_table.add_item_cbk(evt, bvr)" }
        #} )
        #add_btn = TextBtnSetWdg( float="right", buttons=buttons_list,
        #                     spacing=6, size='small', side_padding=0 )
        #widget.add(add_btn)

        from tactic.ui.widget import ActionButtonWdg
        button = ActionButtonWdg(title='+', tip='Add Another Item', size='small')
        widget.add(button)
        button.add_style("float: right")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': "spt.dg_table.add_item_cbk(evt, bvr)"
        } )

 
        label = "Attach"
        label_option = my.get_option("label")
        if label_option:
            label = label_option 
       
        table = Table()
        table.add_color("color", "color")
        table.add_row()

        search_key = sobject.get_search_key()
        # add a thumbe widget
        thumb = ThumbWdg()
        thumb.set_icon_size(40)
        thumb.set_sobject(ref_sobj)
        thumb.set_option('latest_icon', 'true') 
        table.add_cell(thumb)


        # add the text description
        name_span = DivWdg(ref_sobj.get_code())
        name_span.add_style('margin-left: 20px')
        table.add_cell(name_span)


        if ref_sobj.has_value("name"):
            name_span.add( " - " )
            name_span.add( ref_sobj.get_value("name") )

        #status = ref_sobj.get_value("status", no_exception=True)
        #if status:
        #    span = SpanWdg("(status:%s)" % ref_sobj.get_value("status"))
        #    table.add_cell(span)

        
        if ref_sobj.has_value("description"):
            description_wdg = ExpandableTextWdg("description")
            description_wdg.set_max_length(200)
            description_wdg.set_sobject(ref_sobj)
            td = table.add_cell( description_wdg )
            td.add_style("padding-left: 15px")



        # FIXME: not sure about the layout here
        #if ref_sobj.has_value("pipeline_code"):
        #    pipeline_code = ref_sobj.get_value("pipeline_code")
        #    span = SpanWdg("(pipeline:%s)" % pipeline_code )
        #    td = table.add_cell(span)
        #    td.add_style("padding-left: 15px")
        
        widget.add(table)
            

        return widget



    def handle_group_table(my, table, tbody, tr, td):
        # add some data about the sobject 
        if not my.current_ref_sobj:
            return
        tbody.set_attr("spt_search_key", SearchKey.get_by_sobject(my.current_ref_sobj))



    def get_ref_obj(my, sobject):
        search_type = sobject.get_value("search_type")
        search_code = sobject.get_value("search_code", no_exception=True)
        if not search_code:
            search_id = sobject.get_value("search_code")
        else:
            search_id = None

        key = SearchKey.build_search_key(search_type, search_code)

        ref_sobject = my.ref_sobj_dict.get(str(key))
        if not ref_sobject:
            try:
                if search_code:
                    ref_sobject = Search.get_by_code(search_type, search_code)
                else:
                    ref_sobject = Search.get_by_id(search_type, search_id)

                if not ref_sobject:
                    return None
            except SearchException, e:
                print e.__str__()
                return None

        return ref_sobject


    def handle_td(my, td):
        td.add_attr('spt_input_type', 'gantt')
        td.add_class("spt_input_inline")


    def get_display(my):
        #return None
        div = DivWdg()
        div.add_class("spt_gantt_top")

        value_wdg = HiddenWdg(my.get_name())
        value_wdg.add_class("spt_gantt_value")
        div.add( value_wdg )


        content_div = DivWdg()
        content_div.add_style("width: 100%")
        content_div.add_style("height: 100%")

        content_div.add_behavior( {
            'type': 'accept_drop',
            'drop_code': 'DROP_ROW',
            'cbjs_action': '''
            var src_el = bvr._drop_source_bvr.src_el;
            var src_table_top = src_el.getParent(".spt_table_top");
            var src_table = src_table_top.getElement(".spt_table");
            var src_search_keys = spt.dg_table.get_selected_search_keys(src_table);
            if (src_search_keys.length == 0) {
                var tbody = src_el.getParent(".spt_table_tbody");
                var src_search_key = tbody.getAttribute("spt_search_key");
                src_search_keys = [ src_search_key ];
            }

            var src_search_key = src_search_keys[0];

            var drop_el = bvr.src_el;
            var top_wdg = drop_el.getParent('.spt_gantt_top');
            var value_wdg = top_wdg.getElement('.spt_gantt_value');
            value_wdg.value = src_search_key;
            var content_wdg = top_wdg.getElement('.spt_content');

            var server = TacticServerStub.get();
            var sobject = server.get_by_search_key(src_search_key);
            var code = sobject['code'];
            content_wdg.innerHTML = code;

            spt.dg_table.edit.widget = top_wdg;
            var key_code = spt.kbd.special_keys_map.ENTER;
            spt.dg_table.edit_cell_cbk( value_wdg, key_code );

            '''
        } )

        sobject = my.get_current_sobject()
        try:
            parent = sobject.get_parent()
            if parent:
                value = parent.get_code()
            else:
                value = "&nbsp;"
        except SearchException, e:
            # skips unknown search_type/project
            print e.__str__()
            search_type =   sobject.get_search_type()
            if search_type in ['sthpw/task','sthpw/note','sthpw/snapshot']:
                value =  "Parent cannot be found for this parent key [%s&id=%s]" %(sobject.get_value('search_type'), sobject.get_value('search_id'))
            else:
                search_key = sobject.get_search_key()
                value = "Invalid parent for [%s]" % search_key


        content_div.add_class('spt_content')
        content_div.add(value)
        div.add(content_div)
        return div

 

from pyasm.command import DatabaseAction
class ParentGroupAction(DatabaseAction):

    def execute(my):

        sobject = my.sobject
        value = my.get_value(my.get_input_name())
        if not value:
            return

        sobject.add_relationship(value)
        #print "-"*20
        #print value
        #print "-"*20


