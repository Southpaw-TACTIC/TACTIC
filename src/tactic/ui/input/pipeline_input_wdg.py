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


__all__ = ['PipelineInputWdg']

from pyasm.search import Search
from pyasm.web import WebContainer, Widget, DivWdg
from pyasm.widget import BaseInputWdg, SelectWdg, TextWdg, IconButtonWdg, IconWdg, BaseInputWdg

class PipelineInputWdg(BaseInputWdg):
    
    def get_display(my):


        state = my.get_state()
        search_type = state.get("search_type")
        sobj = my.get_current_sobject()

        if search_type:
            st = search_type
        else:
            
            st = sobj.get_base_search_type()
        # for inline insert, this should proceed
        #if not sobj:
        #    return ''
        
        st_suffix = st.split('/', 1)
    
        if len(st_suffix) == 2:
            st_suffix = st_suffix[1]
        
        search = Search('sthpw/pipeline')
        search.add_op_filters([('search_type','EQ', '/%s' %st_suffix)])

        # takes into account site-wide pipeline
        search.add_project_filter(show_unset=True)
        sobjects = search.get_sobjects()

        codes = [x.get_code() for x in sobjects]

        if my.get_option("use_code") in [True, 'true']:
            names = codes
        else:

            names = []
            for x in sobjects:
                name = x.get_value("name")
                if not name:
                    name = x.get_value("code")
                names.append(name)

        select = SelectWdg(my.get_input_name())
        
        # Only on insert, a default pipeline will
        # be assigned.
        if sobj and sobj.is_insert():
            select.add_empty_option("-- Default --")
        else:
            select.add_empty_option()
        select.set_option("values", codes)
        select.set_option("labels", names)
        
        if sobj:
            value = sobj.get_value(my.get_name())
            if value:
                select.set_value(value)

        else: 
            # only for inline
            #behavior =  { 'type': 'click',
            #       'cbjs_action': 'spt.dg_table.select_wdg_clicked( evt, bvr.src_el );'}
            #select.add_behavior(behavior)
            pass
        

        return select



   





