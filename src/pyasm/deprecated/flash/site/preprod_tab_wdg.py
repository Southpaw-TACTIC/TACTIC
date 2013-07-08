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


from pyasm.web import Widget, DivWdg
from pyasm.search import Search
from pyasm.widget import TabWdg, TableWdg, HelpItemWdg

from pyasm.flash import *
from pyasm.prod.web import EpisodeNavigatorWdg, SearchLimitWdg


class PreprodTabWdg(Widget):

    def init(my):

        tab = TabWdg(css=TabWdg.SMALL)
        tab.set_tab_key("preprod_pipeline_tab")
        my.handle_tab(tab)
        my.add(tab, 'tab')


    def handle_tab(my, tab):
        
        tab.add(my.get_script_wdg, "Scripts")
        tab.add(my.get_storyboard_wdg, "Storyboards")
        tab.add(AudioTabWdg, "Audio")
        tab.add(my.get_leica_wdg, "Leica")
        #tab.add(my.get_funpack_wdg, "Fun Packs")
        #tab.add(None, "Design Packs")


    def _get_sobject_wdg(my, search_type):
        widget = Widget()
        if search_type =="flash/nat_pause":
            widget.add(HelpItemWdg('Nat Pause tab', '/doc/flash/nat_pause_tab.html', is_link=True))
        div = DivWdg(css="filter_box")
        episode_filter = EpisodeNavigatorWdg()
        div.add(episode_filter)
        div.add(SearchLimitWdg())
        widget.add(div)
        table = TableWdg(search_type)
        table.set_class("table")
        widget.add(table)
        search = Search(search_type)

        episode_code = episode_filter.get_value()
        if episode_code:
            search.add_filter("episode_code", episode_filter.get_value())
        widget.set_search(search)
        return widget


    def get_leica_wdg(my):
        return my._get_sobject_wdg("flash/leica")


    def get_storyboard_wdg(my):
        return my._get_sobject_wdg("flash/storyboard")


    def get_script_wdg(my):
        return my._get_sobject_wdg("flash/script")


    def get_funpack_wdg(my):
        return my._get_sobject_wdg("flash/funpack")



class AudioTabWdg(PreprodTabWdg):

    def init(my):

        tab = TabWdg(css=TabWdg.SMALL)
        tab.set_tab_key("audio_tab")
        my.handle_tab(tab)
        my.add(tab, 'tab')


    def handle_tab(my, tab):
        
        tab.add(my.get_nat_pause_wdg, "Nat Pause")
        tab.add(my.get_pickup_request_wdg, "Pickup Request")
        tab.add(my.get_final_wave_wdg, "Final Wave")

    def get_nat_pause_wdg(my):
       
        return my._get_sobject_wdg("flash/nat_pause")

    def get_pickup_request_wdg(my):
        return my._get_sobject_wdg("flash/pickup_request")

    def get_final_wave_wdg(my):
        return my._get_sobject_wdg("flash/final_wave")


