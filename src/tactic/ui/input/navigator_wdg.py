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
    
    def init(self):
        shot_select_name = 'shot_code' 
        if self.kwargs.get('name'):
            shot_select_name = self.kwargs.get('name')
        self.shot_select_name = shot_select_name
        self.seq_select_name = "seq_select"
        self.epi_select_name = "epi_select"
        self.shot_code = None
        self.refresh_mode = self.kwargs.get('refresh_mode')=='true'
        self.shot_search_type = self.kwargs.get('shot_search_type')
        if not self.shot_search_type:
            self.shot_search_type = 'prod/shot'
        self.sequence_search_type = self.kwargs.get('sequence_search_type')
        if not self.sequence_search_type:
            self.sequence_search_type = 'prod/sequence'
        

        epi_code = ''
        self.epi_select = SelectWdg(self.epi_select_name, \
                label='Episode: ', css='small smaller')
        self.epi_select.set_persistence() 
        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            self.epi_select.add_empty_option('-- Select --')
            self.epi_select.add_style("font-size: 0.9em")
            search = Search( Episode.SEARCH_TYPE )
            search.add_order_by("code")
            self.epi_select.set_search_for_options(search, "code")
            self.epi_select.add_behavior({'type' : 'change',
                'cbjs_action': "var seq_select= bvr.src_el.getParent('.spt_filter_top').getElement('input[name=%s]'); \
            if (seq_select) {seq_select.value='';} var shot_select=bvr.src_el.getParent('.spt_filter_top').getElement('input[name=%s]'); \
            if (shot_select) {shot_select.value='';} %s; %s " %( self.seq_select_name, self.shot_select_name, self.epi_select.get_save_script(), self.epi_select.get_refresh_script())})
            epi_code = self.epi_select.get_value()
            

        self.seq_select = SelectWdg(self.seq_select_name, \
            label='Sequence: ', css='small')
        self.seq_select.set_persistence() 
        self.seq_select.add_empty_option('-- Select --')
        self.seq_select.add_style("font-size: 0.9em")
        self.seq_select.add_behavior({'type' : 'change',
            'cbjs_action': "var shot_select=bvr.src_el.getParent('.spt_filter_top').getElement('input[name=%s]'); \
            if (shot_select) {shot_select.value='';}  %s; %s" \
            % (self.shot_select_name, self.seq_select.get_save_script(), self.seq_select.get_refresh_script())})
        seq_code = self.seq_select.get_value()
        
        search = Search( self.sequence_search_type)
        if epi_code:
            search.add_filter('episode_code', epi_code)        
            
        self.seq_select.set_search_for_options(search, "code")

        
        self.shot_id = 0

        self.shot_select = SelectWdg(self.shot_select_name)
        self.shot_select.set_persistence() 
        self.shot_select.add_empty_option('-- Select --')
        self.shot_select.set_id("shot_id")
        self.shot_select.add_behavior({'type' : 'change',
            'cbjs_action': "%s;" \
            % (self.shot_select.get_save_script())})

        # get all of the shots
        shot_search = Search(self.shot_search_type)
        shot_search.add_column('id')
        shot_search.add_column('code')
        if seq_code:
            shot_search.add_filter("sequence_code", seq_code)
        shot_search.add_order_by("code")
        self.shots = shot_search.get_sobjects()

        # if shots are defined, then find the selected one
        if self.shots:
            self.shot_select.set_sobjects_for_options(self.shots,"code","code")

            # adjust the value if buttons have been pressed
            self.shot_code = self.shot_select.get_value( for_display=False )
            self.shot = self.get_shot_by_buttons(self.shot_code)
            if self.shot:
                self.shot_code = self.shot.get_code()
                self.shot_select.set_value(self.shot_code)

            else:
                if self.shot_code:
                    #self.shot = self.shots[0]
                    # set the value as a default
                    #self.shot_select.set_value(self.shot.get_code())
                    shot_search  = Search(self.shot_search_type)
                    shot_search.add_filter('code', self.shot_code)
                    self.shot = shot_search.get_sobject()

            """
            # It is no longer desirable to pick a default shot
            if not self.shot and self.shots:
                self.shot = self.shots[0]
            """

                    
    
    def get_display(self):
        # use a span instead so I can add more stuff easily on its right
        div = SpanWdg(css='spt_filter_top')

        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            div.add(self.epi_select)

        div.add(self.seq_select)

        # actually draw the widgets
        title = SpanWdg("Shot: ")
        
        title.add_style("font-size: 1.0em")
        title.add_style("font-weight: bold")
        title.add_style("height: 1.2em")
        prev = IconButtonWdg("Prev", IconWdg.LEFT, True)
                  
        prev.set_text('')
        next = IconButtonWdg("Next", IconWdg.RIGHT, True, icon_pos="right")
        if self.refresh_mode:
           prev.add_behavior({'type' : 'click_up',
            'cbjs_action': "var top=spt.get_parent_panel(bvr.src_el);  \
                 spt.panel.refresh(top, {'Prev':'Prev'}, true);"
           })

           next.add_behavior({'type' : 'click_up',
            'cbjs_action': "var top=spt.get_parent_panel(bvr.src_el);\
                    spt.panel.refresh(top, {'Next':'Next'}, true);"
           })
           self.shot_select.add_behavior({'type': 'change',
              'cbjs_action':"var top=spt.get_parent_panel(bvr.src_el);\
                    spt.panel.refresh(top, {});"
            })
        next.set_text('')

        if self.refresh_mode:
            title.add( prev )
        title.add(self.shot_select)
        if self.refresh_mode:
            title.add( next )

        div.add(title)
        return div
        #self.add(div)

    def get_shot_by_buttons(self, shot_code):
        ''' find out the position in shots array for the current shot_value
            and sets it if the user press "Prev" or "Next" '''    

        # check to see if the any of the buttons have been pressed
        web = WebContainer.get_web()
        if web.get_form_value("Prev") == "" and \
            web.get_form_value("Next") == "":
            return None
       
        # if there are not shots, don't bother
        if not self.shots:
            return None

        index = 0
       
        # find the current shot
        for shot in self.shots:
            if shot_code and shot.get_code() == shot_code:
                break
            index += 1

        if web.get_form_value("Prev") != "":
            if index == 0:
                index = len(self.shots) - 1
            else:
                index = index-1

        elif web.get_form_value("Next") != "":
            if index == len(self.shots):
                index = 0
            else:
                index += 1
               
        if index < 0 or index >= len(self.shots):
            shot = self.shots[0]
        else:
            shot = self.shots[index]

        return shot



    def get_value(self):
        value = self.shot_code
        return value

    def get_shot(self):
        shot_code = self.get_value()
        if shot_code == "":
            return None
        else:
            shot_search  = Search(self.shot_search_type)
            shot_search.add_filter('code', shot_code)
            shot = shot_search.get_sobject()
            return shot 
        

