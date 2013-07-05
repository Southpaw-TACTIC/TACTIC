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


from pyasm.search import *
from pyasm.web import *
from pyasm.widget import *

from pyasm.prod.biz import *
from tactic.ui.common import BaseRefreshWdg
#from prod_context import *

__all__ = ['ShotNavigatorWdg']

class ShotNavigatorWdg(BaseRefreshWdg):
    
    def init(my):
        shot_select_name = 'shot_code' 
        if my.kwargs.get('name'):
            shot_select_name = my.kwargs.get('name')
        my.shot_select_name = shot_select_name
        my.seq_select_name = "seq_select"
        my.epi_select_name = "epi_select"
        my.shot_code = None
        my.refresh_mode = my.kwargs.get('refresh_mode')=='true'
        my.shot_search_type = my.kwargs.get('shot_search_type')
        if not my.shot_search_type:
            my.shot_search_type = 'prod/shot'
        my.sequence_search_type = my.kwargs.get('sequence_search_type')
        if not my.sequence_search_type:
            my.sequence_search_type = 'prod/sequence'
        

        epi_code = ''
        my.epi_select = SelectWdg(my.epi_select_name, \
                label='Episode: ', css='small smaller')
        my.epi_select.set_persistence() 
        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            my.epi_select.add_empty_option('-- Select --')
            my.epi_select.add_style("font-size: 0.9em")
            search = Search( Episode.SEARCH_TYPE )
            search.add_order_by("code")
            my.epi_select.set_search_for_options(search, "code")
            my.epi_select.add_behavior({'type' : 'change',
                'cbjs_action': "var seq_select= bvr.src_el.getParent('.spt_filter_top').getElement('input[name=%s]'); \
            if (seq_select) {seq_select.value='';} var shot_select=bvr.src_el.getParent('.spt_filter_top').getElement('input[name=%s]'); \
            if (shot_select) {shot_select.value='';} %s; %s " %( my.seq_select_name, my.shot_select_name, my.epi_select.get_save_script(), my.epi_select.get_refresh_script())})
            epi_code = my.epi_select.get_value()
            

        my.seq_select = SelectWdg(my.seq_select_name, \
            label='Sequence: ', css='small')
        my.seq_select.set_persistence() 
        my.seq_select.add_empty_option('-- Select --')
        my.seq_select.add_style("font-size: 0.9em")
        my.seq_select.add_behavior({'type' : 'change',
            'cbjs_action': "var shot_select=bvr.src_el.getParent('.spt_filter_top').getElement('input[name=%s]'); \
            if (shot_select) {shot_select.value='';}  %s; %s" \
            % (my.shot_select_name, my.seq_select.get_save_script(), my.seq_select.get_refresh_script())})
        seq_code = my.seq_select.get_value()
        
        search = Search( my.sequence_search_type)
        if epi_code:
            search.add_filter('episode_code', epi_code)        
            
        my.seq_select.set_search_for_options(search, "code")

        
        my.shot_id = 0

        my.shot_select = SelectWdg(my.shot_select_name)
        my.shot_select.set_persistence() 
        my.shot_select.add_empty_option('-- Select --')
        my.shot_select.set_id("shot_id")
        my.shot_select.add_behavior({'type' : 'change',
            'cbjs_action': "%s;" \
            % (my.shot_select.get_save_script())})

        # get all of the shots
        shot_search = Search(my.shot_search_type)
        shot_search.add_column('id')
        shot_search.add_column('code')
        if seq_code:
            shot_search.add_filter("sequence_code", seq_code)
        shot_search.add_order_by("code")
        my.shots = shot_search.get_sobjects()

        # if shots are defined, then find the selected one
        if my.shots:
            my.shot_select.set_sobjects_for_options(my.shots,"code","code")

            # adjust the value if buttons have been pressed
            my.shot_code = my.shot_select.get_value( for_display=False )
            my.shot = my.get_shot_by_buttons(my.shot_code)
            if my.shot:
                my.shot_code = my.shot.get_code()
                my.shot_select.set_value(my.shot_code)

            else:
                if my.shot_code:
                    #my.shot = my.shots[0]
                    # set the value as a default
                    #my.shot_select.set_value(my.shot.get_code())
                    shot_search  = Search(my.shot_search_type)
                    shot_search.add_filter('code', my.shot_code)
                    my.shot = shot_search.get_sobject()

            """
            # It is no longer desirable to pick a default shot
            if not my.shot and my.shots:
                my.shot = my.shots[0]
            """

                    
    
    def get_display(my):
        # use a span instead so I can add more stuff easily on its right
        div = SpanWdg(css='spt_filter_top')

        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            div.add(my.epi_select)

        div.add(my.seq_select)

        # actually draw the widgets
        title = SpanWdg("Shot: ")
        
        title.add_style("font-size: 1.0em")
        title.add_style("font-weight: bold")
        title.add_style("height: 1.2em")
        prev = IconButtonWdg("Prev", IconWdg.LEFT, True)
                  
        prev.set_text('')
        next = IconButtonWdg("Next", IconWdg.RIGHT, True, icon_pos="right")
        if my.refresh_mode:
           prev.add_behavior({'type' : 'click_up',
            'cbjs_action': "var top=spt.get_parent_panel(bvr.src_el);  \
                 spt.panel.refresh(top, {'Prev':'Prev'}, true);"
           })

           next.add_behavior({'type' : 'click_up',
            'cbjs_action': "var top=spt.get_parent_panel(bvr.src_el);\
                    spt.panel.refresh(top, {'Next':'Next'}, true);"
           })
           my.shot_select.add_behavior({'type': 'change',
              'cbjs_action':"var top=spt.get_parent_panel(bvr.src_el);\
                    spt.panel.refresh(top, {});"
            })
        next.set_text('')

        if my.refresh_mode:
            title.add( prev )
        title.add(my.shot_select)
        if my.refresh_mode:
            title.add( next )

        div.add(title)
        return div
        #my.add(div)

    def get_shot_by_buttons(my, shot_code):
        ''' find out the position in shots array for the current shot_value
            and sets it if the user press "Prev" or "Next" '''    

        # check to see if the any of the buttons have been pressed
        web = WebContainer.get_web()
        if web.get_form_value("Prev") == "" and \
            web.get_form_value("Next") == "":
            return None
       
        # if there are not shots, don't bother
        if not my.shots:
            return None

        index = 0
       
        # find the current shot
        for shot in my.shots:
            if shot_code and shot.get_code() == shot_code:
                break
            index += 1

        if web.get_form_value("Prev") != "":
            if index == 0:
                index = len(my.shots) - 1
            else:
                index = index-1

        elif web.get_form_value("Next") != "":
            if index == len(my.shots):
                index = 0
            else:
                index += 1
               
        if index < 0 or index >= len(my.shots):
            shot = my.shots[0]
        else:
            shot = my.shots[index]

        return shot



    def get_value(my):
        value = my.shot_code
        return value

    def get_shot(my):
        shot_code = my.get_value()
        if shot_code == "":
            return None
        else:
            shot_search  = Search(my.shot_search_type)
            shot_search.add_filter('code', shot_code)
            shot = shot_search.get_sobject()
            return shot 
        

