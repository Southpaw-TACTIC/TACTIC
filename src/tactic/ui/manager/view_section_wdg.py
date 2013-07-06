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
__all__ = ["SectionManagerWdg", 'ViewSectionWdg']

import os, types
import math

from pyasm.common import Common
from pyasm.command import Command

from pyasm.web import DivWdg
from pyasm.widget import WidgetConfigView

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import SideBarBookmarkMenuWdg


class SectionManagerWdg(BaseRefreshWdg):

    def get_display(my):
        my.search_type = my.kwargs.get('search_type')
        my.view = my.kwargs.get('view')

        return my.get_section_wdg(my.view)


    def get_section_wdg(my, view, editable=True, default=False):

        title = ""
        target_id = "sobject_relation"
        if editable:
            edit_mode = 'edit'
        else:
            edit_mode = 'read'
        kwargs = {
            'title': title,
            'config_search_type': my.search_type,
            'view': view,
            'target_id': target_id,
            'width': '300',
            'prefix': 'manage_side_bar',
            'mode': edit_mode,
            'default': str(default)
        }
        if view in ["definition", "custom_definition"]:
            kwargs['recurse'] = "false"

        section_wdg = ViewSectionWdg(**kwargs)
        class_path = Common.get_full_class_name(section_wdg)

        section_div = DivWdg()
        section_div.add_style("display: block")
        section_div.set_attr('spt_class_name', class_path)
        for name, value in kwargs.items():
            if name == "config":
                continue
            section_div.set_attr("spt_%s" % name, value)

        section_div.add(section_wdg)
        return section_div


from base_section_wdg import BaseSectionWdg
class ViewSectionWdg(BaseSectionWdg):

    def get_config(cls, config_search_type, view,  default=False):
        config = WidgetConfigView.get_by_search_type(config_search_type, view)
        return config


    def get_detail_class_name(my):
        return "tactic.ui.manager.ElementDefinitionWdg"

    #
    # behavior functions
    #
    def add_separator_behavior(my, separator_wdg, element_name, config, options):
        if my.mode == 'edit':
            # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp',
            }
            separator_wdg.add_behavior(behavior)
            separator_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")



    def add_folder_behavior(my, folder_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a folder'''

        # determines whether the folder opens on click
        recurse = my.kwargs.get("recurse")!= "false"

        # edit behavior
        edit_allowed = True
        if my.mode == 'edit' and edit_allowed:
            # IS EDITABLE ...

            # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp'
            }
            if recurse:
                behavior['cbjs_action_onnomotion'] = 'spt.side_bar.toggle_section_display_cbk(evt,bvr); ' \
                                                     'spt.side_bar.display_element_info_cbk(evt,bvr);'
            else:
                behavior['cbjs_action_onnomotion'] = 'spt.side_bar.display_element_info_cbk(evt,bvr);'
            behavior['class_name'] = my.get_detail_class_name()
           
            folder_wdg.add_behavior(behavior)
            folder_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        else:
            # IS NOT EDITABLE ...
            if recurse:
                behavior = {
                    'type':         'click_up',
                    'cbfn_action':  'spt.side_bar.toggle_section_display_cbk',
                }
                folder_wdg.add_behavior( behavior )



    def add_link_behavior(my, link_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a link'''

        edit_allowed = True
        if my.mode == 'edit' and edit_allowed:
                # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp',
                'cbjs_action_onnomotion':  'spt.side_bar.display_element_info_cbk(evt,bvr);',
                'class_name':   my.get_detail_class_name()
            }

            link_wdg.add_behavior(behavior)
            link_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")


