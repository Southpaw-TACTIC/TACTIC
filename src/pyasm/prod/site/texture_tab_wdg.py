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

__all__ = ["TextureTabWdg"]

from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.web import *
from pyasm.widget import FilterSelectWdg
from pyasm.prod.web import TextureFilterWdg



class TextureTabWdg(BaseTabWdg):

    def init(my):
        my.setup_tab("texture_pipeline_tab", css=TabWdg.SMALL)


    def handle_tab(my, tab):
        
        tab.add(my.get_texture_list_wdg, _("Texture List") )
        #tab.add(my.get_texture_list_wdg, _("Matte Painting") )
        tab.add(my.get_summary_wdg, _("Summary") )
        tab.add(my.get_task_manager_wdg, _("Tasks") )
        tab.add(my.get_texture_wdg, _("Artist (Textures)") )
        tab.add(my.get_source_wdg, _("Texture Sources") )


    def get_texture_list_wdg(my):

        widget = Widget()
        nav = DivWdg(css='filter_box')
        filter = TextureFilterWdg()
        nav.add(filter)
        widget.add(nav)
        
        search = Search("prod/texture")
        widget.set_search(search)
        table = TableWdg("prod/texture", "manage")
        widget.add(table)

        return widget



    def get_summary_wdg(my):

        widget = Widget()
        widget.add(HelpItemWdg('Summary tab', '/doc/site/prod/summary_tab.html'))
        
        nav = DivWdg(css='filter_box')
        filter = TextureFilterWdg()
        nav.add(filter)
        widget.add(nav)
        
        search = Search("prod/texture")
        widget.set_search(search)

        table = TableWdg("prod/texture", "summary")
        widget.add(table)

        return widget


    def get_task_manager_wdg(my):
        widget = Widget()
        widget.add(HelpItemWdg('Tasks tab', '/doc/site/prod/task_tab.html'))
        manager = TaskManagerWdg()
        widget.add(manager)
        manager.set_search_type("prod/texture")
        #manager.set_sobject_filter( AssetFilterWdg() )
        return widget



    def get_texture_wdg(my):

        widget = Widget()

        approval_wdg = ApprovalManagerWdg()
        widget.add(approval_wdg)
        approval_wdg.set_search_type("prod/texture")
        approval_wdg.set_view("artist")
        approval_wdg.set_sobject_filter( TextureFilterWdg() )
        return widget




    def get_source_wdg(my):

        search = Search(TextureSource.SEARCH_TYPE)

        widget = Widget()
        widget.set_search(search)

        filter = TextureFilterWdg()
        widget.add(filter)

        table = TableWdg(TextureSource.SEARCH_TYPE)

        widget.add(table)
        return widget






