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
from prod_context import *

__all__ = ['ShotNavigatorWdg', 'SequenceNavigatorWdg', 'GeneralNavigatorWdg',
            'EpisodeNavigatorWdg', 'EpisodeShotNavigatorWdg',
            'SequenceShotNavigatorWdg']

class ShotNavigatorWdg(BaseRefreshWdg):
    
    def init(self):
        shot_select_name = 'shot_id' 
        if self.kwargs.get('name'):
            shot_select_name = self.kwargs.get('name')
        self.shot_select_name = shot_select_name
        self.seq_select_name = "seq_select"
        self.epi_select_name = "epi_select"
        self.shot_id = None

    
        
            
        
        epi_code = ''
        self.epi_select = FilterSelectWdg(self.epi_select_name, \
                label='Episode: ', css='small smaller')
        
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
            

        self.seq_select = FilterSelectWdg(self.seq_select_name, \
            label='Sequence: ', css='small smaller')
        self.seq_select.add_empty_option('-- Select --')
        self.seq_select.add_style("font-size: 0.9em")
        self.seq_select.add_behavior({'type' : 'change',
            'cbjs_action': "var shot_select=bvr.src_el.getParent('.spt_filter_top').getElement('input[name=%s]'); \
            if (shot_select) {shot_select.value='';}  %s; %s" \
            % (self.shot_select_name, self.seq_select.get_save_script(), self.seq_select.get_refresh_script())})
        seq_code = self.seq_select.get_value()
        
        search = Search( Sequence.SEARCH_TYPE )
        if epi_code:
            search.add_filter('episode_code', epi_code)        
            
        self.seq_select.set_search_for_options(search, "code")

        
        self.shot_id = 0

        self.shot_select = SelectWdg(self.shot_select_name)
        self.shot_select.add_empty_option('-- Select --')
        self.shot_select.set_id("shot_id")
        self.shot_select.add_behavior({'type' : 'change',
            'cbjs_action': "%s; %s" \
            % (self.shot_select.get_save_script(), self.shot_select.get_refresh_script())})

        # get all of the shots
        shot_search = Search("prod/shot")
        shot_search.add_column('id')
        shot_search.add_column('code')
        if seq_code:
            shot_search.add_filter("sequence_code", seq_code)
        shot_search.add_order_by("code")
        self.shots = shot_search.get_sobjects()

        # if shots are defined, then find the selected one
        if self.shots:
            self.shot_select.set_sobjects_for_options(self.shots,"id","code")

            # adjust the value if buttons have been pressed
            self.shot_id = self.shot_select.get_value( for_display=False )
            self.shot = self.get_shot_by_buttons(self.shot_id)
            if self.shot:
                self.shot_id = self.shot.get_id()
                self.shot_select.set_value(self.shot_id)

            else:
                if self.shot_id == "":
                    self.shot = self.shots[0]
                    # set the value as a default
                    self.shot_select.set_value(self.shot.get_id())
                else:
                    self.shot = Shot.get_by_id(self.shot_id)

            if not self.shot and self.shots:
                self.shot = self.shots[0]

            if not self.shot:
                return

            #TODO: remove these
            WebState.get().add_state("shot_key", self.shot.get_search_key())
            WebState.get().add_state("shot_id" , self.shot.get_id())
            WebState.get().add_state("shot_code", self.shot.get_code())
            WebState.get().add_state("edit|shot_code", self.shot.get_code())

        
    
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
        prev.add_behavior({'type' : 'click_up',
            'cbjs_action': "var top=bvr.src_el.getParent('.spt_main_panel'); \
                if (!top) top =bvr.src_el.getParent('.spt_panel'); spt.panel.refresh(top, {'Prev':'Prev'}, true);"
           })
        prev.set_text('')
        next = IconButtonWdg("Next", IconWdg.RIGHT, True, icon_pos="right")
        next.add_behavior({'type' : 'click_up',
            'cbjs_action': "var top=bvr.src_el.getParent('.spt_main_panel'); \
                if (!top) top =bvr.src_el.getParent('.spt_panel'); spt.panel.refresh(top, {'Next':'Next'}, true);"
           })
        next.set_text('')

        title.add( prev )
        title.add(self.shot_select)
        title.add( next )

        div.add(title)
        return div
        #self.add(div)

    def get_shot_by_buttons(self, shot_id):
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
       
        # find the current hsot
        for shot in self.shots:
            if shot_id and shot_id != "" \
                and shot.get_id() == int(shot_id):
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
        value = self.shot_id
        if value == '':
            return self.shots[0].get_id()
        else:
            return self.shot_id

    def get_shot(self):
        shot_id = self.get_value()
        if shot_id == "":
            return None
        else:
            return Shot.get_by_id(shot_id)
        

class SequenceNavigatorWdg(HtmlElement):
    
    def __init__(self, name="sequence_code_nav"):
        self.select_name = name 
        self.select = None 
        self.epi_select = None
        super(SequenceNavigatorWdg,self).__init__('span')
       
    def init(self):
        epi_code = ''
        self.epi_select = FilterSelectWdg("epi_select_%s" %self.select_name, \
                label='Episode: ', css='small smaller')
        self.epi_select.add_empty_option('-- Any --')

        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            self.epi_select.add_style("font-size: 0.9em")
            search = Search( Episode.SEARCH_TYPE )
            search.add_order_by("code")
            self.epi_select.set_search_for_options(search, "code")

            self.epi_select.set_event('onchange', "var seq_select=get_elements('%s'); \
            if (seq_select) {seq_select.value='';} " %(self.select_name))
            epi_code = self.epi_select.get_value()
            self.add(self.epi_select)

        sequence_select = FilterSelectWdg(self.select_name, label="Sequence: ", css='smaller')
        #sequence_select.set_submit_onchange(False)
        # set up the select to be manipulated on
        self.select = sequence_select
        
        sequence_select.add_style("font-size: 0.95em")
        
        sequence_select.add_empty_option("-- Any Seqs. --")
        search = Search( Sequence.SEARCH_TYPE )
        if epi_code:
            search.add_filter('episode_code', epi_code)
        sequence_select.set_search_for_options(search,"code")
        
        self.add( sequence_select )

        sequence_code = sequence_select.get_value()
        if sequence_code == '':
            return
        
        
        state = WebState.get()
        state.add_state("sequence_code", sequence_code)

        # TODO: don't like the need for this.  This requires too much knowledge
        # of what the state is used for
        state.add_state("edit|sequence_code", sequence_code)

    def add_none_option(self):
        self.select.add_none_option()
 
    def remove_empty_option(self):
        self.select.remove_empty_option()
        
    def get_value(self):
        seq_code = self.select.get_value()
        epi_code = self.epi_select.get_value()
        return epi_code, seq_code

    def set_option(self, name, value):
        self.select.set_option(name, value)

    def get_select(self):
        return self.select

    
   

class GeneralNavigatorWdg(HtmlElement):
    '''a general navigation widget that is built up from a hierarchy of
    sobjects'''
    def __init__(self, search_types):
        if isinstance(search_types, list):
            self.search_types = search_types
        else:
            self.search_types = [search_types]

        self.selects = []
        super(GeneralNavigatorWdg,self).__init__("span")


    def init(self):

        for search_type in self.search_types:

            search_type_obj = SearchType.get(search_type)

            self.add("<b>%s</b>: " % search_type_obj.get_title())

            select = self._create_select_wdg(search_type,"code")
            self.add( select )


    def _create_select_wdg(self, search_type, column ):

        select = SelectWdg(column)
        select.add_style("font-size: 0.9em")
        search = Search( search_type )
        select.set_search_for_options(search,column)
        select.set_persistence(self)
        return select



    def get_value(self):
        if self.selects:
            return self.selects[0].get_value()


class EpisodeNavigatorWdg(SequenceNavigatorWdg):

    def __init__(self, name="episode_code_nav", title="Episode"):
        # quick fix.  If name is used, it will get reset in the super functions
        self.select_name = name 
        self.display_title = title
        super(EpisodeNavigatorWdg,self).__init__(name)
        self.name = name 


    def init(self):
        # set up the select to be manipulated on
        self.select = FilterSelectWdg(self.select_name)
        episode_select = self.select
        
        episode_select.add_empty_option("-- Any Episodes --")
        episode_select.add_style("font-size: 0.9em")
        search = Search( Episode.SEARCH_TYPE )
        search.add_order_by("code")
        episode_select.set_search_for_options(search,"code")
        

        self.add(SpanWdg("%s:" % self.display_title, css='small'))
        self.add( episode_select )

        episode_code = episode_select.get_value()
               
        state = WebState.get()
        state.add_state("episode_code", episode_code)
        if episode_code == '':
            return
        
        # TODO: don't like the need for this.  This requires too much knowledge
        # of what the state is used for
        state.add_state("edit|episode_code", episode_code)

        search.add_regex_filter("code", episode_code, op='EQ') 

    def get_value(self):
        epi_code = self.select.get_value()
        return epi_code
   
        
class EpisodeShotNavigatorWdg(SequenceNavigatorWdg):

    def __init__(self, episode_select_name='combo_episode_code_nav', shot_select_name='combo_shot_code_nav'):
        self.episode_select_name = episode_select_name
        self.shot_select_name = shot_select_name
        super(EpisodeShotNavigatorWdg,self).__init__()


    def init(self):
        
        self.episode_select = FilterSelectWdg(self.episode_select_name, \
            label='Episode: ', css='med')
        self.episode_select.add_style("font-size: 0.9em")
        search = Search( Episode.SEARCH_TYPE )
        search.add_order_by("code")
        self.episode_select.set_search_for_options(search,"code")

        self.episode_select.set_event('onchange', "var sec_select=get_elements('%s'); \
            if (sec_select) {sec_select.value='NONE';}" % self.shot_select_name)

        episode_code = self.episode_select.get_value()

        self.shot_select = FilterSelectWdg(self.shot_select_name, label='Shot: ')
        self.shot_select.add_style("font-size: 0.9em")

        # set up the select to be manipulated on
        self.select = self.shot_select

        search = Search( "flash/shot" )
        search.add_column('code')
        search.add_filter("episode_code", episode_code)
        self.shot_select.add_empty_option('-- Any --')
        self.shot_select.set_search_for_options(search,"code","code")
        
        self.add(self.episode_select)
        
        self.add(self.shot_select)


        state = WebState.get()
        state.add_state("episode_code", episode_code)
        state.add_state("shot_code", self.get_value())
        state.add_state("edit|shot_code", self.get_value())

  

    def get_value(self):
        return self.shot_select.get_value()

class SequenceShotNavigatorWdg(SequenceNavigatorWdg):

    def __init__(self, seq_select_name='combo_sequence_code_nav', shot_select_name='combo_shot_code_nav'):
        self.seq_select_name = seq_select_name
        self.shot_select_name = shot_select_name
        self.epi_select_name = 'combo_epi_code_nav'
        super(SequenceShotNavigatorWdg, self).__init__()


    def init(self):

        epi_code = ''
        self.epi_select = FilterSelectWdg(self.epi_select_name, \
                label='Episode: ', css='small smaller')
        self.epi_select.add_empty_option('-- Any --')
        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            
            self.epi_select.add_style("font-size: 0.9em")
            search = Search( Episode.SEARCH_TYPE )
            search.add_order_by("code")
            self.epi_select.set_search_for_options(search, "code")

            self.epi_select.set_event('onchange', "var seq_select=get_elements('%s'); \
            if (seq_select) {seq_select.value='';} var shot_select=get_elements('%s'); \
            if (shot_select) {shot_select.value='';} " %(self.seq_select_name, self.shot_select_name))
            epi_code = self.epi_select.get_value()
            self.add(self.epi_select)

        self.seq_select = FilterSelectWdg(self.seq_select_name, \
            label='Sequence: ', css='small smaller')
        self.seq_select.add_empty_option('-- Any --')
        self.seq_select.add_style("font-size: 0.9em")
        search = Search( Sequence.SEARCH_TYPE )
        if epi_code:
            search.add_filter('episode_code', epi_code)

        search.add_order_by("code")
        seq_sobjs = search.get_sobjects()
        self.seq_select.set_sobjects_for_options(seq_sobjs, "code")

        self.seq_select.set_event('onchange', "var sec_select=document.form.elements['%s']; \
            if (sec_select) {sec_select.value='';} document.form.submit()" % self.shot_select_name)

        seq_code = self.seq_select.get_value()
        
        # if there is no sequence sobjects, do not show any shots
        if not seq_sobjs:
            seq_code = "NONE"

        self.shot_select = FilterSelectWdg(self.shot_select_name, label='Shot: ', css='small smaller')
        self.shot_select.add_style("font-size: 0.9em")

        # set up the select to be manipulated on
        self.select = self.shot_select

        search = Search( "prod/shot" )
        search.add_column('code')
        if seq_code:
            search.add_filter("sequence_code", seq_code)
        shot_sobjs = search.get_sobjects()
        if shot_sobjs:
            self.shot_select.add_empty_option('-- Any --')
            self.shot_select.set_sobjects_for_options(shot_sobjs,"code","code")
        
        self.add(self.seq_select)
        
        self.add(self.shot_select)


        state = WebState.get()
        state.add_state("seq_code", seq_code)
        state.add_state("shot_code", self.shot_select.get_value())
        state.add_state("edit|shot_code", self.shot_select.get_value())

  

    def get_value(self):
        ''' it returns both seq code and shot_code'''
        epi_value = self.epi_select.get_value()
        seq_value = self.seq_select.get_value()
        shot_value = self.shot_select.get_value()
        if self.shot_select.get_select_values() == ([],[]):
            shot_value = "NONE"

        return epi_value, seq_value, shot_value
