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
    
    def init(my):
        shot_select_name = 'shot_id' 
        if my.kwargs.get('name'):
            shot_select_name = my.kwargs.get('name')
        my.shot_select_name = shot_select_name
        my.seq_select_name = "seq_select"
        my.epi_select_name = "epi_select"
        my.shot_id = None

    
        
            
        
        epi_code = ''
        my.epi_select = FilterSelectWdg(my.epi_select_name, \
                label='Episode: ', css='small smaller')
        
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
            

        my.seq_select = FilterSelectWdg(my.seq_select_name, \
            label='Sequence: ', css='small smaller')
        my.seq_select.add_empty_option('-- Select --')
        my.seq_select.add_style("font-size: 0.9em")
        my.seq_select.add_behavior({'type' : 'change',
            'cbjs_action': "var shot_select=bvr.src_el.getParent('.spt_filter_top').getElement('input[name=%s]'); \
            if (shot_select) {shot_select.value='';}  %s; %s" \
            % (my.shot_select_name, my.seq_select.get_save_script(), my.seq_select.get_refresh_script())})
        seq_code = my.seq_select.get_value()
        
        search = Search( Sequence.SEARCH_TYPE )
        if epi_code:
            search.add_filter('episode_code', epi_code)        
            
        my.seq_select.set_search_for_options(search, "code")

        
        my.shot_id = 0

        my.shot_select = SelectWdg(my.shot_select_name)
        my.shot_select.add_empty_option('-- Select --')
        my.shot_select.set_id("shot_id")
        my.shot_select.add_behavior({'type' : 'change',
            'cbjs_action': "%s; %s" \
            % (my.shot_select.get_save_script(), my.shot_select.get_refresh_script())})

        # get all of the shots
        shot_search = Search("prod/shot")
        shot_search.add_column('id')
        shot_search.add_column('code')
        if seq_code:
            shot_search.add_filter("sequence_code", seq_code)
        shot_search.add_order_by("code")
        my.shots = shot_search.get_sobjects()

        # if shots are defined, then find the selected one
        if my.shots:
            my.shot_select.set_sobjects_for_options(my.shots,"id","code")

            # adjust the value if buttons have been pressed
            my.shot_id = my.shot_select.get_value( for_display=False )
            my.shot = my.get_shot_by_buttons(my.shot_id)
            if my.shot:
                my.shot_id = my.shot.get_id()
                my.shot_select.set_value(my.shot_id)

            else:
                if my.shot_id == "":
                    my.shot = my.shots[0]
                    # set the value as a default
                    my.shot_select.set_value(my.shot.get_id())
                else:
                    my.shot = Shot.get_by_id(my.shot_id)

            if not my.shot and my.shots:
                my.shot = my.shots[0]

            if not my.shot:
                return

            #TODO: remove these
            WebState.get().add_state("shot_key", my.shot.get_search_key())
            WebState.get().add_state("shot_id" , my.shot.get_id())
            WebState.get().add_state("shot_code", my.shot.get_code())
            WebState.get().add_state("edit|shot_code", my.shot.get_code())

        
    
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
        title.add(my.shot_select)
        title.add( next )

        div.add(title)
        return div
        #my.add(div)

    def get_shot_by_buttons(my, shot_id):
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
       
        # find the current hsot
        for shot in my.shots:
            if shot_id and shot_id != "" \
                and shot.get_id() == int(shot_id):
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
        value = my.shot_id
        if value == '':
            return my.shots[0].get_id()
        else:
            return my.shot_id

    def get_shot(my):
        shot_id = my.get_value()
        if shot_id == "":
            return None
        else:
            return Shot.get_by_id(shot_id)
        

class SequenceNavigatorWdg(HtmlElement):
    
    def __init__(my, name="sequence_code_nav"):
        my.select_name = name 
        my.select = None 
        my.epi_select = None
        super(SequenceNavigatorWdg,my).__init__('span')
       
    def init(my):
        epi_code = ''
        my.epi_select = FilterSelectWdg("epi_select_%s" %my.select_name, \
                label='Episode: ', css='small smaller')
        my.epi_select.add_empty_option('-- Any --')

        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            my.epi_select.add_style("font-size: 0.9em")
            search = Search( Episode.SEARCH_TYPE )
            search.add_order_by("code")
            my.epi_select.set_search_for_options(search, "code")

            my.epi_select.set_event('onchange', "var seq_select=get_elements('%s'); \
            if (seq_select) {seq_select.value='';} " %(my.select_name))
            epi_code = my.epi_select.get_value()
            my.add(my.epi_select)

        sequence_select = FilterSelectWdg(my.select_name, label="Sequence: ", css='smaller')
        #sequence_select.set_submit_onchange(False)
        # set up the select to be manipulated on
        my.select = sequence_select
        
        sequence_select.add_style("font-size: 0.95em")
        
        sequence_select.add_empty_option("-- Any Seqs. --")
        search = Search( Sequence.SEARCH_TYPE )
        if epi_code:
            search.add_filter('episode_code', epi_code)
        sequence_select.set_search_for_options(search,"code")
        
        my.add( sequence_select )

        sequence_code = sequence_select.get_value()
        if sequence_code == '':
            return
        
        
        state = WebState.get()
        state.add_state("sequence_code", sequence_code)

        # TODO: don't like the need for this.  This requires too much knowledge
        # of what the state is used for
        state.add_state("edit|sequence_code", sequence_code)

    def add_none_option(my):
        my.select.add_none_option()
 
    def remove_empty_option(my):
        my.select.remove_empty_option()
        
    def get_value(my):
        seq_code = my.select.get_value()
        epi_code = my.epi_select.get_value()
        return epi_code, seq_code

    def set_option(my, name, value):
        my.select.set_option(name, value)

    def get_select(my):
        return my.select

    
   

class GeneralNavigatorWdg(HtmlElement):
    '''a general navigation widget that is built up from a hierarchy of
    sobjects'''
    def __init__(my, search_types):
        if isinstance(search_types, list):
            my.search_types = search_types
        else:
            my.search_types = [search_types]

        my.selects = []
        super(GeneralNavigatorWdg,my).__init__("span")


    def init(my):

        for search_type in my.search_types:

            search_type_obj = SearchType.get(search_type)

            my.add("<b>%s</b>: " % search_type_obj.get_title())

            select = my._create_select_wdg(search_type,"code")
            my.add( select )


    def _create_select_wdg(my, search_type, column ):

        select = SelectWdg(column)
        select.add_style("font-size: 0.9em")
        search = Search( search_type )
        select.set_search_for_options(search,column)
        select.set_persistence(my)
        return select



    def get_value(my):
        if my.selects:
            return my.selects[0].get_value()


class EpisodeNavigatorWdg(SequenceNavigatorWdg):

    def __init__(my, name="episode_code_nav", title="Episode"):
        # quick fix.  If name is used, it will get reset in the super functions
        my.select_name = name 
        my.display_title = title
        super(EpisodeNavigatorWdg,my).__init__(name)
        my.name = name 


    def init(my):
        # set up the select to be manipulated on
        my.select = FilterSelectWdg(my.select_name)
        episode_select = my.select
        
        episode_select.add_empty_option("-- Any Episodes --")
        episode_select.add_style("font-size: 0.9em")
        search = Search( Episode.SEARCH_TYPE )
        search.add_order_by("code")
        episode_select.set_search_for_options(search,"code")
        

        my.add(SpanWdg("%s:" % my.display_title, css='small'))
        my.add( episode_select )

        episode_code = episode_select.get_value()
               
        state = WebState.get()
        state.add_state("episode_code", episode_code)
        if episode_code == '':
            return
        
        # TODO: don't like the need for this.  This requires too much knowledge
        # of what the state is used for
        state.add_state("edit|episode_code", episode_code)

        search.add_regex_filter("code", episode_code, op='EQ') 

    def get_value(my):
        epi_code = my.select.get_value()
        return epi_code
   
        
class EpisodeShotNavigatorWdg(SequenceNavigatorWdg):

    def __init__(my, episode_select_name='combo_episode_code_nav', shot_select_name='combo_shot_code_nav'):
        my.episode_select_name = episode_select_name
        my.shot_select_name = shot_select_name
        super(EpisodeShotNavigatorWdg,my).__init__()


    def init(my):
        
        my.episode_select = FilterSelectWdg(my.episode_select_name, \
            label='Episode: ', css='med')
        my.episode_select.add_style("font-size: 0.9em")
        search = Search( Episode.SEARCH_TYPE )
        search.add_order_by("code")
        my.episode_select.set_search_for_options(search,"code")

        my.episode_select.set_event('onchange', "var sec_select=get_elements('%s'); \
            if (sec_select) {sec_select.value='NONE';}" % my.shot_select_name)

        episode_code = my.episode_select.get_value()

        my.shot_select = FilterSelectWdg(my.shot_select_name, label='Shot: ')
        my.shot_select.add_style("font-size: 0.9em")

        # set up the select to be manipulated on
        my.select = my.shot_select

        search = Search( "flash/shot" )
        search.add_column('code')
        search.add_filter("episode_code", episode_code)
        my.shot_select.add_empty_option('-- Any --')
        my.shot_select.set_search_for_options(search,"code","code")
        
        my.add(my.episode_select)
        
        my.add(my.shot_select)


        state = WebState.get()
        state.add_state("episode_code", episode_code)
        state.add_state("shot_code", my.get_value())
        state.add_state("edit|shot_code", my.get_value())

  

    def get_value(my):
        return my.shot_select.get_value()

class SequenceShotNavigatorWdg(SequenceNavigatorWdg):

    def __init__(my, seq_select_name='combo_sequence_code_nav', shot_select_name='combo_shot_code_nav'):
        my.seq_select_name = seq_select_name
        my.shot_select_name = shot_select_name
        my.epi_select_name = 'combo_epi_code_nav'
        super(SequenceShotNavigatorWdg, my).__init__()


    def init(my):

        epi_code = ''
        my.epi_select = FilterSelectWdg(my.epi_select_name, \
                label='Episode: ', css='small smaller')
        my.epi_select.add_empty_option('-- Any --')
        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            
            my.epi_select.add_style("font-size: 0.9em")
            search = Search( Episode.SEARCH_TYPE )
            search.add_order_by("code")
            my.epi_select.set_search_for_options(search, "code")

            my.epi_select.set_event('onchange', "var seq_select=get_elements('%s'); \
            if (seq_select) {seq_select.value='';} var shot_select=get_elements('%s'); \
            if (shot_select) {shot_select.value='';} " %(my.seq_select_name, my.shot_select_name))
            epi_code = my.epi_select.get_value()
            my.add(my.epi_select)

        my.seq_select = FilterSelectWdg(my.seq_select_name, \
            label='Sequence: ', css='small smaller')
        my.seq_select.add_empty_option('-- Any --')
        my.seq_select.add_style("font-size: 0.9em")
        search = Search( Sequence.SEARCH_TYPE )
        if epi_code:
            search.add_filter('episode_code', epi_code)

        search.add_order_by("code")
        seq_sobjs = search.get_sobjects()
        my.seq_select.set_sobjects_for_options(seq_sobjs, "code")

        my.seq_select.set_event('onchange', "var sec_select=document.form.elements['%s']; \
            if (sec_select) {sec_select.value='';} document.form.submit()" % my.shot_select_name)

        seq_code = my.seq_select.get_value()
        
        # if there is no sequence sobjects, do not show any shots
        if not seq_sobjs:
            seq_code = "NONE"

        my.shot_select = FilterSelectWdg(my.shot_select_name, label='Shot: ', css='small smaller')
        my.shot_select.add_style("font-size: 0.9em")

        # set up the select to be manipulated on
        my.select = my.shot_select

        search = Search( "prod/shot" )
        search.add_column('code')
        if seq_code:
            search.add_filter("sequence_code", seq_code)
        shot_sobjs = search.get_sobjects()
        if shot_sobjs:
            my.shot_select.add_empty_option('-- Any --')
            my.shot_select.set_sobjects_for_options(shot_sobjs,"code","code")
        
        my.add(my.seq_select)
        
        my.add(my.shot_select)


        state = WebState.get()
        state.add_state("seq_code", seq_code)
        state.add_state("shot_code", my.shot_select.get_value())
        state.add_state("edit|shot_code", my.shot_select.get_value())

  

    def get_value(my):
        ''' it returns both seq code and shot_code'''
        epi_value = my.epi_select.get_value()
        seq_value = my.seq_select.get_value()
        shot_value = my.shot_select.get_value()
        if my.shot_select.get_select_values() == ([],[]):
            shot_value = "NONE"

        return epi_value, seq_value, shot_value
