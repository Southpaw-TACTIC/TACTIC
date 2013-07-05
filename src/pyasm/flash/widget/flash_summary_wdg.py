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

__all__ = ['FlashSummaryWdg', 'FlashAssetDetailWdg', 'FlashShotDetailWdg']

from pyasm.prod.biz import Shot
from pyasm.search import Search
from pyasm.web import Widget, Table, WebContainer, DivWdg, HtmlElement
from pyasm.widget import ThumbWdg, TableWdg, FilterSelectWdg, SimpleStatusWdg
from pyasm.prod.web import AssetDetailWdg, ShotDetailWdg


class FlashSummaryWdg(Widget):

    def init(my):

        # get the args in the URL
        args = WebContainer.get_web().get_form_args()
        search_type = args['search_type']
        search_id = args['search_id']

        sobject = Search.get_by_id(search_type, search_id)

        main_div = DivWdg()
        main_div.add_style("width: 95%")
        main_div.add_style("float: right")
        my.add(main_div)

        
        if isinstance(sobject, Shot):

            content_id ='summary_story_%s' %sobject.get_id()
            title_id = 'story_head_%s' %sobject.get_id()
            story_div = DivWdg(id=content_id)
            story_div.add_style('display','block')
            
            story_head = HtmlElement.h3("Storyboard")
            my.add_title_style(story_head, title_id, content_id)
            
            main_div.add(story_head)
            main_div.add(story_div)

            storyboard_table = TableWdg("prod/storyboard", "summary", css='minimal')
            search = Search("prod/storyboard")
            search.add_filter( sobject.get_foreign_key(), sobject.get_code() )
            sobjects = search.get_sobjects()
            storyboard_table.set_sobjects(sobjects)
            story_div.add(storyboard_table)


        # add reference material
        search = Search("sthpw/connection")
        search.add_filter("src_search_type", search_type)
        search.add_filter("src_search_id", search_id)
        connections = search.get_sobjects()

        if connections:
            content_id ='summary_ref_%s' %sobject.get_id()
            title_id = 'ref_head_%s' %sobject.get_id()

            ref_head = HtmlElement.h3("Reference")
            my.add_title_style(ref_head, title_id, content_id)
            
            ref_div = DivWdg(id = content_id)
            ref_div.add_style('display','block')
            
            for connection in connections:
                thumb = ThumbWdg()
                thumb.set_name("snapshot")
                dst_search_type = connection.get_value("dst_search_type")
                dst_search_id = connection.get_value("dst_search_id")
                dst = Search.get_by_id(dst_search_type, dst_search_id)
                thumb.set_sobject(dst)
                ref_div.add(thumb)

            
            main_div.add(ref_head)
            main_div.add(ref_div)


       
        task_head = HtmlElement.h3("Tasks")
        content_id ='summary_task_%s' %sobject.get_id()
        title_id = 'task_head_%s' %sobject.get_id()
        my.add_title_style(task_head, title_id, content_id)
        
        main_div.add(task_head)

        task_div = DivWdg(id=content_id)
        task_div.add_style('display','block')
        
        main_div.add(task_div)
        
        search = Search("sthpw/task")
        #if process != "":
        #    search.add_filter("process", process)

        search.add_filter("search_type", search_type)
        search.add_filter("search_id", search_id)

        #search.set_limit(4)
        task_table = TableWdg("sthpw/task", "summary", css='minimal')
        task_table.set_id('sthpw/task%s' % search_id)
        task_table.set_search(search)
        task_div.add(task_table)

        content_id ='summary_hist_%s' %sobject.get_id()
        title_id = 'hist_head_%s' %sobject.get_id()
        hist_head = HtmlElement.h3("Checkin History")
        my.add_title_style(hist_head, title_id, content_id)
        
        hist_div = DivWdg(id=content_id)
        hist_div.add_style('display','block')
        
        
        main_div.add(hist_head)
        main_div.add(hist_div)
        from flash_asset_history_wdg import FlashAssetHistoryWdg
        history = FlashAssetHistoryWdg()
        hist_div.add(history)
        main_div.add(HtmlElement.br())

    def add_title_style(my, title, title_id, content_id):
        '''add style and toggle effect to different sections of the summary'''
        title.add_class('hand')
        title.set_id(title_id)
        title.add_event('onclick',"toggle_display('%s')" %content_id)
               
        title.add_event('onmouseover', "Effects.bg_color('%s',"\
              "'#FFF', '#E3E6C8')" %title_id ) 
        title.add_event('onmouseout', "Effects.bg_color('%s',"\
              "'#E3E6C8', '#FFF')" %title_id ) 
        



class FlashAssetDetailWdg(AssetDetailWdg):
    pass

class FlashShotDetailWdg(ShotDetailWdg):

    def get_display(my):

        # get the args in the URL
        args = WebContainer.get_web().get_form_args()
        search_type = args['search_type']
        search_id = args['search_id']

        sobject = Search.get_by_id(search_type, search_id)

        main_div = DivWdg()
        main_div.add_style("width: 98%")
        main_div.add_style("float: right")
        my.add(main_div)

        # get planned assets
        planned_head, planned_div = my.get_planned_wdg(sobject)
        main_div.add(planned_head)
        main_div.add(planned_div)


        # add notes
        notes_head, notes_div = my.get_sobject_wdg(sobject, "sthpw/note", "summary")
        main_div.add(notes_head)
        main_div.add(notes_div)

        # add storyboards
        story_head, story_div = my.get_sobject_wdg(sobject, "prod/storyboard", "summary")
        main_div.add(story_head)
        main_div.add(story_div)

        # add references
        ref_head, ref_div = my.get_sobject_wdg(sobject, "sthpw/connection","detail",title="Reference Material")
        main_div.add(ref_head)
        main_div.add(ref_div)
        
        task_head, task_div = my.get_sobject_wdg(sobject, "sthpw/task", "summary")
        main_div.add(task_head)
        main_div.add(task_div)



        # add dailies: need a special function for this
        dailies_head, dailies_div = my.get_dailies_wdg(sobject)
        main_div.add(dailies_head)
        main_div.add(dailies_div)


        # add history div
        hist_head, hist_div = my.get_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)

        return main_div
       
