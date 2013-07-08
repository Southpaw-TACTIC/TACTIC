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
__all__ = ["SearchTypePanelWdg"]

import os, types

from pyasm.biz import Schema
from pyasm.search import Search, SearchKey, SearchType
from pyasm.web import DivWdg, SpanWdg, HtmlElement, Table

from tactic.ui.common import BaseRefreshWdg

from panel_wdg import SideBarBookmarkMenuWdg, TableLayoutWdg


class SearchTypePanelWdg(BaseRefreshWdg):
    '''Panel to manage search types'''

    def get_args_keys(my):
        return {
        'search_type': 'search type of the sobject to be display'
        }

    def get_display(my):
        div = DivWdg()

        search_type = "prod/asset"

        search_type_obj = SearchType.get(search_type)
        title = search_type_obj.get_title()
        title_wdg = DivWdg()
        title_wdg.add_style("font-size: 1.8em")
        title_wdg.add("%s" % (title) )

        div.add(title_wdg)
        div.add(HtmlElement.hr())


        table = Table()
        div.add(table)
        table.set_max_width()

        table.add_row()

        from pyasm.widget import ThumbWdg, DiscussionWdg, SObjectTaskTableElement

        td = table.add_cell()
        td.add_style("width: 250px")
        td.add_style("vertical-align: top")
        td.add_style("border-right: solid 1px")
        title = DivWdg()
        title.add_class("maq_search_bar")
        x = DivWdg("[?] [x]")
        x.add_style("float: right")
        title.add(x)
        title.add("Info")
        td.add(title)
        thumb = ThumbWdg()
        thumb.set_sobject(sobject)
        td.add(thumb)
        from pyasm.prod.web import AssetInfoWdg
        info = AssetInfoWdg()
        info.thumb = thumb
        info.set_sobject(sobject)
        td.add(info)

        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding-left: 5px")
        td.add_style("border-right: solid 1px")
       
        # notes
        title = DivWdg()
        title.add_class("maq_search_bar")
        x = DivWdg("[x]")
        x.add_style("float: right")
        title.add(x)
        title.add("Notes")
        td.add(title)
        discussion_wdg = DiscussionWdg()
        discussion_wdg.preprocess()
        discussion_wdg.set_sobject(sobject)
        td.add(discussion_wdg)

        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding-left: 5px")
        td.add_style("border-right: solid 1px")
 

        # tasks
        title = DivWdg()
        title.add_class("maq_search_bar")
        x = DivWdg("[x]")
        x.add_style("float: right")
        title.add(x)
        title.add("Custom Properties")
        td.add(title)
        search = Search("prod/custom_property")
        search.add_filter("search_type", "sample3d/book")
        sobjects = search.get_sobjects()
        table = TableLayoutWdg(search_type="prod/custom_property", view='table')
        table.set_sobjects(sobjects)
        td.add(table)

        div.add(HtmlElement.hr())
        div.add(HtmlElement.br(clear="all"))





        title_wdg = DivWdg()
        title_wdg.add_class("maq_search_bar")
        x = DivWdg("[x]")
        x.add_style("float: right")
        title_wdg.add(x)
        #title_wdg.add_style("font-size: 1.5em")
        title_wdg.add("Detail" )
        div.add(title_wdg)
        div.add(HtmlElement.br())



        # TEST getting schema
        search_type = sobject.get_base_search_type()
        schema = Schema.get_by_sobject(sobject)

        



        # add a second table
        table = Table()
        table.set_max_width()


        # show the snapshots for this sobject
        search_type = "sthpw/snapshot"
        search = Search(search_type)
        search.add_sobject_filter(sobject)
        search.set_limit(50)
        sobjects = search.get_sobjects()


        table.add_row()
        nav_td = table.add_cell()
        nav_td.add_style("width: 100px")
        nav_td.add_style("vertical-align: top")
        #section_wdg = my.get_section_wdg(sobject)
        #nav_td.add( section_wdg )

        #from tactic.ui.panel import ManageViewPanelWdg
        #defined = ManageViewPanelWdg()
        from tactic.ui.panel import ManageViewWdg
        defined = ManageViewWdg()
        nav_td.add(defined)

        #content_wdg = TableLayoutWdg(search_type=search_type, view='table')
        #content_wdg.set_sobjects(sobjects)
        #content_td = table.add_cell()
        #content_td.set_id("sobject_relation")
        #content_td.add_style("display: table-cell")
        #content_td.add_style("vertical-align: top")
        #content_td.add(content_wdg)

        div.add(table)

        return div



    def get_section_wdg(my, sobject):

        parent_key = SearchKey.get_by_sobject(sobject)

        section_id = "wow"
        title = ""
        view = "children"
        target_id = "sobject_relation"

        kwargs = {
            'section_id': section_id,
            'title': title,
            'view': view,
            'target_id': target_id,
            'width': '125',
            'parent_key': parent_key
        }
        section_div = DivWdg()
        section_div.add_style("display: block")
        section_div.set_id(section_id)
        section_div.set_attr('spt_class_name', "tactic.ui.panel.ChildrenBookmarkMenuWdg")
        for name, value in kwargs.items():
            if name == "config":
                continue
            section_div.set_attr("spt_%s" % name, value)

        section_wdg = SObjectChildrenMenuWdg(**kwargs)
        section_div.add(section_wdg)
        return section_div






