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

__all__ = ['PreprodTabWdg']


from pyasm.web import Widget, DivWdg, SpanWdg
from pyasm.search import Search
from pyasm.widget import TabWdg, TableWdg, TextWdg, SearchLimitWdg, FilterSelectWdg, HintWdg, HelpItemWdg, BaseTabWdg
from pyasm.prod.web import SequenceFilterWdg, SearchFilterWdg



class PreprodTabWdg(BaseTabWdg):


    def init(self):
        help = HelpItemWdg('Preproduction', 'The Preproduction area lets you organize art references, storyboard, scripts, and camera data.')
        self.add(help)
        self.setup_tab("preprod_pipeline_tab", css=TabWdg.SMALL)


    def handle_tab(self, tab):
        
        tab.add(self.get_art_reference, _("Reference") )
        tab.add(self.get_script_wdg, _("Scripts") )
        tab.add(self.get_storyboard_wdg, _("Storyboards") )
        tab.add(self.get_camera_wdg, _("Camera Data") )
        
        tab.add(self.get_notes_wdg, _("Notes") )
        



  


    def get_art_reference(self):

        widget = Widget()
        help = HelpItemWdg('References', 'References tab lets the user organize art references. Each reference can be [related] to one or more assets defined in TACTIC. It can be set up when you [Edit] the reference.')
        self.add(help)
        div = DivWdg(css="filter_box")
        
        widget.add(div)
        columns = ['description','keywords']
        search_filter = SearchFilterWdg("art_ref_search", columns=columns,\
            has_persistence=False)
       
        div.add(search_filter)
           
        select = FilterSelectWdg("art_ref_category", label='Category: ', css='snall')
        select.set_option("setting", "art_reference_category")
        select.add_empty_option('-- Any --')
        
        div.add( select )

        table = TableWdg("prod/art_reference")
        search = Search("prod/art_reference")
       
        search_filter.alter_search(search)
       
        value = select.get_value()
        if value != "":
            search.add_filter("category", value)
        table.set_search(search)
        widget.add(table)
        return widget
    

    def get_storyboard_wdg(self):
        widget = Widget()
        help = HelpItemWdg('Storyboards', 'Storyboards tab lets the user organize storyboards. You are only required to [Insert] once per shot. Subsequent versions of the storyboard should be published via the [Publish] button.')
        self.add(help)
        div = DivWdg(css="filter_box")

        sequence_filter = SequenceFilterWdg()
        epi_code, sequence_code = sequence_filter.get_value()
        div.add(sequence_filter)


        columns = ['code','shot_code']
        search_filter = SearchFilterWdg("storyboard_search", columns=columns,\
            has_persistence=False)
     
       
        div.add(search_filter)

        

        widget.add(div)


        # create a search
        search = Search("prod/storyboard")
        
        if sequence_code:
            search.add_where("shot_code in (select code from shot where sequence_code = '%s')" % sequence_code)



        table = TableWdg("prod/storyboard")
        table.set_class("table")
        table.set_search_limit(25)
        table.set_search(search)
        widget.add(table)
        return widget


    def get_script_wdg(self):
        table = TableWdg("prod/script")
        table.set_class("table")
        search = Search("prod/script")
        table.set_search(search)
        return table



    def get_camera_wdg(self):
        widget = Widget()

        div = DivWdg(css="filter_box")
        sequence_filter = SequenceFilterWdg()
        epi_code, sequence_code = sequence_filter.get_value()
        div.add(sequence_filter)

        search = Search("prod/camera")

        columns = ['shot_code', 'description']
        search_filter = SearchFilterWdg("camera_search", columns=columns,\
            has_persistence=False)
     
        search_filter.alter_search(search)
        div.add(search_filter)
        widget.add(div)

        if sequence_code:
            search.add_where("shot_code in (select code from shot where sequence_code = '%s')" % sequence_code)

        table = TableWdg("prod/camera")
        table.set_search(search)
        widget.add(table)
        return widget




    

    def get_notes_wdg(self):
        widget = Widget()

        div = DivWdg(css="filter_box")
        columns = ['code', 'description']
        search_filter = SearchFilterWdg("note_search", columns=columns,\
            has_persistence=False)
     
        
        div.add(search_filter)
        sequence_filter = SequenceFilterWdg()
        
        div.add(sequence_filter)

        context_select = FilterSelectWdg("discussion_context")
        context_select.set_option("setting", "notes_preprod_context")
        context_select.add_empty_option("-- Any Context --")
        span = SpanWdg(css="med")
        span.add("Notes Context: ")
        span.add(context_select)
        hint = HintWdg('Submission notes for each shot are also included here')
        span.add(hint)
        div.add(span)

       

        widget.add(div)

        # create a search
        search = Search("prod/shot")
        sequence_filter.alter_search(search)

        search_filter.alter_search(search)

        table = TableWdg("prod/shot", "preprod_notes")
        table.set_search(search)
        widget.add(table)
        return widget




