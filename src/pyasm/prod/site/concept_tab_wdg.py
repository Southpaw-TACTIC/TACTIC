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

__all__ = ["ConceptTabWdg"]

from pyasm.biz import Project
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.web import *
from pyasm.widget import FilterSelectWdg


class ConceptTabWdg(BaseTabWdg):

    def init(my):
        my.add(HelpItemWdg('Concept Pipeline', 'Concept Pipeline contains a collection of tabs that manage the creation process of concept artwork.', False))
        my.setup_tab("concept_pipeline_tab", css=TabWdg.SMALL)



    def handle_tab(my, tab):
        
        tab.add(my.get_concept_list_wdg, _("Concept List") )
        tab.add(my.get_summary_wdg, _("Summary") )
        tab.add(my.get_task_manager_wdg, _("Tasks") )
        tab.add(my.get_concept_artist_wdg, _("Artist (Concepts)") )
        tab.add(my.get_concept_supe_wdg, _("Supe (Concepts)") )
        tab.add(my.get_notes_wdg, _("Notes") )


    def get_concept_list_wdg(my):

        widget = Widget()

        nav = DivWdg(css='filter_box')
        widget.add(nav)
        
        search = Search("prod/concept")

        concept_filter.alter_search(search)
        table = TableWdg("prod/concept", "manage")
        table.set_search(search)
        widget.add(table)

        return widget



    def get_summary_wdg(my):

        widget = Widget()
        #widget.add(HelpItemWdg('Summary tab', '/doc/site/prod/summary_tab.html'))
        
        nav = DivWdg(css='filter_box')
        #concept_filter = ConceptFilterWdg()
        #nav.add(concept_filter)
        #widget.add(nav)
        
        search = Search("prod/concept")
        #concept_filter.alter_search(search)
        

        table = TableWdg("prod/concept", "summary")
        table.set_search(search)
        table.set_search_limit(50)

        widget.add(table)

        return widget


    def get_task_manager_wdg(my):
       
        widget = Widget()
        help = HelpItemWdg('Tasks tab', 'The Task Manager lets the coordinator set up tasks for each individual asset. Once created, the tasks can be assigned to different users. Settings such as bid date, duration, and milestone can be customized at any time.')
        widget.add(help)
        manager = TaskManagerWdg()
        widget.add(manager)
        manager.set_search_type("prod/concept")
        #manager.set_sobject_filter( ConceptFilterWdg() )
        return widget



    def get_concept_artist_wdg(my):
        widget = Widget()
        approval_wdg = ApprovalManagerWdg()
        widget.add(approval_wdg)
        approval_wdg.set_search_type("prod/concept")
        approval_wdg.set_sobject_filter( ConceptFilterWdg() )
        
        help = HelpItemWdg('Artist tab', 'The Artist tab lets the artist to set the status of his assigned tasks, leave notes, publish, and view all sorts of info related to various concepts')
        widget.add(help)
        return widget

    def get_concept_supe_wdg(my):
        widget = Widget()
        approval_wdg = ApprovalManagerWdg()
        widget.add(approval_wdg)
        approval_wdg.set_search_type("prod/concept")
        approval_wdg.set_sobject_filter( ConceptFilterWdg() )
        approval_wdg.set_view('supe')
    
        help = HelpItemWdg('Supe tab', 'In addition to what the Artist tab does, The Supe tab lets the supervisor assign existing tasks to differernt users, and modify the estimated date range for each task.')
        widget.add(help)
        return widget



    def get_notes_wdg(my):
        widget = Widget()

        help = HelpItemWdg('Notes tab', 'The Notes tab focuses on the display of notes. It includes both concept notes and submission notes for each concept.')
        widget.add(help)

        div = DivWdg(css='filter_box')
        concept_filter = ConceptFilterWdg()
        div.add(concept_filter)
 
        
        context_select = FilterSelectWdg("discussion_context")
        context_select.set_option("setting", "notes_prod_context")
        context_select.add_empty_option("-- Any Context --")
        span = SpanWdg(css="med")
        span.add("Notes Context: ")
        span.add(context_select)
        hint = HintWdg('Submission notes for each concepts are also included here')
        span.add(hint)
        div.add(span)

        #search_limit = SearchLimitWdg()
        #div.add(search_limit)

        widget.add(div)


        # create a search
        search = Search("prod/concept")
        concept_filter.alter_search(search)
        #search_limit.alter_search(search)
        #sobjects = search.get_sobjects()

        table = TableWdg("prod/concept", "prod_notes")
        table.set_search(search)
        widget.add(table)
        return widget


 



