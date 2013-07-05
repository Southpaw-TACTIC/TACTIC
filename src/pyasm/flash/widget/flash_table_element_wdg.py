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

__all__ = ['PickupPublishTableElement', 'FlashShotInfoWdg']

import re, time, types

from pyasm.command import Command
from pyasm.search import SearchType, Search, SObject, SearchException
from pyasm.web import *
from pyasm.widget import BaseTableElementWdg, PublishLinkWdg, IconWdg
from pyasm.flash import NatPause
from pyasm.prod.web import ShotInfoWdg
 


class PickupPublishTableElement(BaseTableElementWdg):
    ''' Publish link used in Pickup Request tab '''

    def preprocess(my):
        episode_codes = SObject.get_values(my.sobjects, 'episode_code')
        search = Search(NatPause)
        search.add_filters('episode_code', episode_codes)
        net_pauses = search.get_sobjects()
        my.sobject_dict = SObject.get_dict(net_pauses, key_cols=['episode_code'])

    def get_title(my):
        option = my.get_option('multi_publish')
        if option and my.parent_wdg:
            search_type = my.parent_wdg.search_type
            if my.get_option('search_type'):
                search_type = my.get_option('search_type')
            publish_link = PublishLinkWdg(search_type, -1,\
                icon=IconWdg.PUBLISH_MULTI,  config_base='multi_publish_pickup', text='Multi Publish')
            publish_link.set_iframe_width(70)
            return publish_link
        else:
            return super(PublishTableElement, my).get_title()
        
    def get_display(my):
        
        sobject = my.get_current_sobject()
        if sobject:
            episode_code = sobject.get_value('episode_code')
            sobject = my.sobject_dict.get(episode_code)
            if not sobject:
                return ''
            publish_link = PublishLinkWdg(sobject.get_search_type(), \
                sobject.get_id(), config_base='publish_pickup')
            publish_link.set_iframe_width(70)
            return publish_link
        else:
            return ''

class FlashShotInfoWdg(ShotInfoWdg):
    '''Shot Info Wdg for Flash'''
    def _add_publish_link(my, main_div):
        pass

