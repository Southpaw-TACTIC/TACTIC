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

__all__ = ["EditorialTabWdg", "SubmissionListWdg"]

from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.web import *
from pyasm.search import *
from pyasm.prod.biz import *
from pyasm.biz import Project
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import TableLayoutWdg


class EditorialTabWdg(BaseTabWdg):

    TAB_NAME = "Editorial"      # 1st level tab name
    TAB_KEY = "editorial_tab"
    DAILIES_TAB = "Dailies"
    
    def init(self):
        help = HelpItemWdg('Editorial', 'The Editorial area lets users manage bins for media submission, review dailies, organize plates and cut sequences.')
        self.add(help)

        self.setup_tab(self.TAB_KEY, css=TabWdg.SMALL)
        


    def handle_tab(self, tab):
        tab.add(self.get_bins, _("Bins") )
        tab.add(self.get_submissions_in_bins, self.DAILIES_TAB)
        tab.add(self.get_plate_wdg, _("Plates") )
        tab.add(self.get_cut_seq_wdg, _("Cut Sequences") )
        #tab.add(self.get_director_notes, "Director Notes")
        #tab.add(self.get_final_approval, "Final Approval")


    def get_bins(self):
        widget = Widget()
    
        nav = DivWdg(css='filter_box')

        type_filter = BinTypeFilterWdg()
        nav.add(type_filter)

        code_filter = CodeFilterWdg()
        nav.add(code_filter)
        
        label_select = BinLabelFilterSelectWdg()
        nav.add(label_select)

        #search_limit = SearchLimitWdg(limit=50)
        #nav.add(search_limit)
        
        label = label_select.get_value()
        search = Search(Bin)
        
        code_filter.alter_search(search)
        type_filter.alter_search(search)
        #search_limit.alter_search(search)
        search.add_order_by('code desc')

        if label:
            search.add_filter('label', label)
        table = TableWdg(Bin.SEARCH_TYPE)
        table.set_search(search)
        table.set_search_limit(50)
        
        widget.add(nav)
        widget.add(table)
    
        return widget
   
    def _get_aux_data(self, sobjs):
        info = SubmissionInfo(sobjs)
        aux_data = info.get_info()
        return aux_data 

    def get_submissions_in_bins(self):
        widget = Widget()
   
        help = HelpItemWdg('Dailies', 'Dailies tab show a list of submitted media for the bin selected. You can narrow down the submission of a particular asset by using the Item Filter.')
        self.add(help)

        nav = DivWdg(css='filter_box')
        #nav = FilterboxWdg()
        bin_filter = BinFilterWdg()
        bin_filter.add_empty_option('', '-- Select a bin --')
        nav.add(SpanWdg('Bin: '))
        nav.add(bin_filter)
        hint = HintWdg("To see any bins, you need to create them (Type 'dailies') in the Bins tab.")
        nav.add(hint)


        user_filter = UserFilterWdg(['user_filter','Artist: '])
        user_filter.set_search_column('artist')
        nav.add_advanced_filter(user_filter)

        config_base = 'table' 
        notes_context_select = FilterSelectWdg("%s_discussion_context" %config_base, \
            label="Notes Context: ", css='med')
        notes_context_select.add_empty_option("-- Any Context --")
        notes_context_select.set_option("setting", "notes_dailies_context")

        notes_context_select.get_values()
        nav.add(notes_context_select)

        search = Search(Submission)
        user_filter.alter_search(search)

        span = SpanWdg(css="med")
        span.add("Status: ")
        status_filter = FilterSelectWdg("dailies_status_select")
        status_filter.add_empty_option("-- Any Status --")
        status_filter.set_option("setting", "dailies_submission_status")
        span.add(status_filter)
        nav.add(span)

        

        bin_id = bin_filter.get_value()
        if not bin_id or bin_id == SelectWdg.NONE_MODE:
           #search.add_filter('id','-1')
           search.add_where("id in (select submission_id from "\
            " submission_in_bin"\
            " where bin_id in (select id from bin where type = 'dailies') )" )
        elif bin_id:
           search.add_where("id in (select submission_id from "\
            " submission_in_bin"\
            " where bin_id = %s)" %bin_id)
        search.add_order_by('timestamp desc')

        all_sobjs = search.get_sobjects()
        all_aux_data = self._get_aux_data(all_sobjs)

        status_filter_value = status_filter.get_value()
        if status_filter_value:
            search.add_filter("status", status_filter_value)

        
        table = TableWdg(Submission.SEARCH_TYPE)
        
        filter_span = SubmissionItemFilterWdg(all_aux_data, all_sobjs)
        filter_span.alter_search(search)

        

        sobjs = search.get_sobjects(redo=True)
        table.set_sobjects(sobjs)
      
        aux_data = self._get_aux_data(sobjs)
        
        table.set_aux_data(aux_data)
        widget.add(nav)
    
        
        
        nav.add(filter_span)
        #nav.add(retired)
        nav.add(search_limit)
        
        widget.add(table)
    
        return widget

    def get_director_notes(self):
        # FIXME: hard-coded director notes status
        task_status = "Waiting"
        
        widget = Widget()

        nav = DivWdg(css='filter_box')
        episode_filter = None
        if Project.get().get_type() == 'flash':
            episode_filter = EpisodeFilterWdg()
        else:
            episode_filter = SequenceFilterWdg()
        nav.add( episode_filter )

        widget.add(nav)



        shot_search = Search(Shot)
        episode_filter.alter_search(shot_search)
        shot_search.add_column('id')
        shot_ids = shot_search.get_sobjects()
        shot_ids = SObject.get_values(shot_ids, 'id')
        
        # only show shots that have a task at the director level
        search_type = SearchType.get("prod/shot").get_full_key()
        search = Search("sthpw/task")
        

        search.add_filter("search_type", search_type)
        search.add_filters("search_id", shot_ids)
        search.add_filter("status", task_status)
        tasks = search.get_sobjects()

        table = TableWdg("sthpw/task", "director")
        table.set_sobjects(tasks)
        widget.add(table)

        return widget




    def get_final_approval(self):
        widget = Widget()

        nav = DivWdg(css='filter_box')
        episode_filter = None
        if Project.get().get_type() == 'flash':
            episode_filter = EpisodeFilterWdg()
        else:
            episode_filter = SequenceFilterWdg()
        
        nav.add( episode_filter )
        widget.add(nav)


        search = Search("prod/shot")
        episode_filter.alter_search(search)
        table = TableWdg("prod/shot", "director")
        table.set_search(search)

        widget.add(table)

        return widget

    

    def get_plate_wdg(self):
        ''' get the plates tab'''
        search = Search("effects/plate")

        widget = Widget()

        div = DivWdg(css="filter_box")
        sequence_filter = SequenceFilterWdg()
        episode_code, sequence_code = sequence_filter.get_value()
        div.add(sequence_filter)

        columns = ['shot_code','type', 'description']
        search_filter = SearchFilterWdg("plate_search", columns=columns,\
            has_persistence=False)
     
        search_filter.alter_search(search)
        div.add(search_filter)

        if sequence_code:
            search.add_where("shot_code in (select code from shot where sequence_code = '%s')" % sequence_code)

      
        widget.add(div)

        table = TableWdg("effects/plate")
        table.set_search(search)
        widget.add(table)

        return widget

    def get_cut_seq_wdg(self):
        ''' get the cut sequences tab'''
        search = Search("prod/cut_sequence")

        widget = Widget()
        help = HelpItemWdg('Cut Sequences', 'Cut Sequences tab lets the user organize cuts for each sequence. You are only required to [Insert] once per sequence. Subsequent versions of the cut should be published via the [Publish] button.')
        self.add(help)

        div = DivWdg(css="filter_box")
        sequence_filter = SequenceFilterWdg()
        sequence_code = sequence_filter.get_value()
        div.add(sequence_filter)
        
        columns = ['shot_code','type', 'description']
        search_filter = SearchFilterWdg("plate_search", columns=columns,\
            has_persistence=False)
     
        search_filter.alter_search(search)
        div.add(search_filter)
       

        if sequence_code:
            search.add_where("shot_code in (select code from shot where sequence_code = '%s') or sequence_code ='%s'" % (sequence_code, sequence_code))

      
        widget.add(div)

        table = TableWdg("prod/cut_sequence")
        table.set_search(search)
        widget.add(table)

        return widget





class SubmissionListWdg(BaseRefreshWdg):

    def get_search_wdg(self):
        search_type = "prod/submission"
        type = self.kwargs.get('type') 
        if not type:
            type = 'dailies'
        from tactic.ui.app import SearchWdg
        filter_xml = '''
        <config>
        <filter>
              <element name='Main Filter'>
                <display class='tactic.ui.filter.SubmissionFilterWdg'>
                  <prefix>%(type)s</prefix>
                  <type>%(type)s</type>
                  <search_type>%(search_type)s</search_type>
                </display>
              </element>

              <element name='Quick Search'>
                <display class='tactic.ui.filter.SObjectSearchFilterWdg'>
                  <search_type>%(search_type)s</search_type>
                  <prefix>simple</prefix>
                </display>
              </element>

              <element name='General'>
                <display class='tactic.ui.filter.GeneralFilterWdg'>
                  <prefix>main_body</prefix>
                  <search_type>%(search_type)s</search_type>
                  <mode>sobject</mode>
                </display>
              </element>
        </filter>
        </config>''' %{'search_type': search_type, 'type': type}
        
        # provide a view, so it will not automatically get the last saved search instead
        # we need to differentiate between client and dailies search
        search_wdg = SearchWdg(search_type=search_type, view=type, filter=filter_xml)
    
        
        return search_wdg

    def get_display(self):
        widget = DivWdg(css="spt_view_panel")
   
        search_wdg = self.get_search_wdg()
        widget.add(search_wdg)
        widget.add(HtmlElement.br())
        search = search_wdg.get_search()
       
        type = self.kwargs.get('type')
        view = self.kwargs.get('view')
        if not view:
            view = 'table'
        
        table_id = "main_body_table" 
        table = TableLayoutWdg(table_id=table_id, search_type=Submission.SEARCH_TYPE, \
                view=view, inline_search=True)
        table.alter_search(search)
       
        sobjs = search.get_sobjects(redo=True)
        table.set_sobjects(sobjs, search)
    
        widget.add(table)
    
        return widget

   
