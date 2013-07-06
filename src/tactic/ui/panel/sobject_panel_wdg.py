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
__all__ = ["SObjectPanelWdg", "SObjectChildrenMenuWdg"]

import os, types

from pyasm.biz import Schema
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, SpanWdg, HtmlElement, Table

from tactic.ui.common import BaseRefreshWdg

from panel_wdg import SideBarBookmarkMenuWdg, ViewPanelWdg


class SObjectPanelWdg(BaseRefreshWdg):
    '''Panel to view an individual sobject and all the information related
    to it'''

    def get_args_keys(my):
        return {
        'search_key': 'search key of the sobject to be displayed',
        # or
        'search_type': 'search type of the sobject to be displayed',
        'code': 'code of the sobject to be displayed',
        'id': 'id of the sobject to be displayed'
        }

    def get_display(my):
        div = DivWdg()

        sobject = my.get_sobject_from_kwargs()
        if not sobject:
            div.add("SObject not found")
            return div

        search_type_obj = sobject.get_search_type_obj()
        title = search_type_obj.get_title()
        title_wdg = DivWdg()
        title_wdg.add_style("font-size: 1.8em")
        title_wdg.add("%s: %s" % (title, sobject.get_code() ) )

        div.add(title_wdg)
        div.add(HtmlElement.hr())


        table = Table()
        table.set_max_width()

        col1 = table.add_col()
        col1.add_style('width: 200px')
        col2 = table.add_col()
        col2.add_style('width: 320px')
        col3 = table.add_col()
        col3.add_style('width: 400px')
        table.add_row()

        from pyasm.widget import ThumbWdg, DiscussionWdg, SObjectTaskTableElement

        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("border-right: solid 1px")
        title = DivWdg()
        title.add_class("maq_search_bar")
        #x = DivWdg("[?] [x]")
        #x.add_style("float: right")
        #title.add(x)
        title.add("Info")
        td.add(title)
        thumb = ThumbWdg()
        thumb.set_sobject(sobject)
        thumb.set_option("detail", "false")
        td.add(thumb)
        from pyasm.prod.web import AssetInfoWdg
        info = AssetInfoWdg()
        info.thumb = thumb
        info.set_sobject(sobject)
        td.add(info)

        # tasks
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding-left: 5px")
        td.add_style("border-right: solid 1px")
        title = DivWdg()
        title.add_class("maq_search_bar")
        #x = DivWdg("[x]")
        #x.add_style("float: right")
        #title.add(x)
        title.add("Tasks")
        td.add(title)
        task_wdg = SObjectTaskTableElement()
        task_wdg.set_sobject(sobject)
        td.add(task_wdg)
        td.add_style('cell-padding','10')


        # discussion
        td = table.add_cell()
        #td.add_style("min-width: 300px")
        #td.add_style("width: 600px")
        td.add_style("vertical-align: top")
        td.add_style("padding-left: 5px")
        td.add_style("border-right: solid 1px")
       
        title = DivWdg()
        title.add_class("maq_search_bar")
        #x = DivWdg("[x]")
        #x.add_style("float: right")
        #title.add(x)
        title.add("Notes")
        td.add(title)
        discussion_wdg = DiscussionWdg()
        discussion_wdg.preprocess()
        discussion_wdg.set_sobject(sobject)
        td.add(discussion_wdg)
        note_panel = discussion_wdg.get_note_menu()
        td.add(note_panel)

        div.add(table)
       

        div.add(HtmlElement.hr())
        div.add(HtmlElement.br(clear="all"))

        title_wdg = DivWdg()
        title_wdg.add_class("maq_search_bar")
        #x = DivWdg("[x]")
        #x.add_style("float: right")
        #title_wdg.add(x)
        #title_wdg.add_style("font-size: 1.5em")
        title_wdg.add("Detail" )
        div.add(title_wdg)
        div.add(HtmlElement.br())



        # TEST getting schema
        search_type = sobject.get_base_search_type()
        schema = Schema.get_by_sobject(sobject)
        child_types = schema.get_child_types(search_type)




        # add a second table
        table = Table()
        table.set_max_width()


        # show the snapshots for this sobject
        search_type = "sthpw/snapshot"
        search = Search(search_type)
        search.add_sobject_filter(sobject)
        search.set_limit(25)
        sobjects = search.get_sobjects()


        table.add_row()
        nav_td = table.add_cell()
        nav_td.add_style("width: 100px")
        nav_td.add_style("vertical-align: top")
        section_wdg = my.get_section_wdg(sobject)
        nav_td.add( section_wdg )

        parent_key = SearchKey.get_by_sobject(sobject)
        content_wdg = ViewPanelWdg(search_type=search_type, element_name='Snapshots', \
            title='Snapshots', view='table', parent_key=parent_key, do_search=True)
        #content_wdg.set_sobjects(sobjects)
        content_td = table.add_cell()
        content_td.set_id("sobject_relation")
        content_td.add_style("display: table-cell")
        content_td.add_style("vertical-align: top")
        content_td.add_style("padding-left: 10px")
        content_td.add(content_wdg)

        div.add(table)

        return div



    def get_section_wdg(my, sobject):

        parent_key = SearchKey.get_by_sobject(sobject)

        section_id = "wow"
        title = ""
        view = "children"
        target_id = "sobject_relation"

        kwargs = {
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




class SObjectChildrenMenuWdg(SideBarBookmarkMenuWdg):

    #def get_config(my):
    #    pass

    def get_target_id(my):
        return "sobject_relation"

