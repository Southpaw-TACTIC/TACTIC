###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['NoteInputWdg', 'NoteHistoryWdg']

from pyasm.biz import Project
from pyasm.web import DivWdg
from pyasm.widget import BaseInputWdg, SelectWdg, TextWdg, IconButtonWdg, IconWdg, HiddenWdg, TextAreaWdg

from pyasm.common import TacticException

from pyasm.search import Search

from tactic.ui.common import BaseRefreshWdg


class NoteInputWdg(BaseInputWdg):
    '''This will display the latest note with a text area below it'''

    def get_display(my):

        top = DivWdg()

        context = my.get_option("context")

        sobject = my.get_option("sobject")
        if not sobject:
            search_key = my.get_option("search_key")
            sobject = Search.get_by_search_key(search_key)
        else:
            search_key = sobject.get_search_key()

        if search_key or not sobject.is_insert():

            search = Search("sthpw/note") 
            #search.add_relationship_filters(my.filtered_parents, type='hierarchy')
            search.add_parent_filter(sobject)
            search.add_order_by("process")
            search.add_order_by("context")
            search.add_order_by("timestamp desc")
            last_note = search.get_sobject()
        else:
            last_note = None


        if last_note:
            last_div = DivWdg()
            top.add(last_div)

            note_str = last_note.get_value("note")
            login = last_note.get_value("login")
            if not login:
                login = "<i style='opacity: 0.3'>unknown</i>"
            date = last_note.get_datetime_value("timestamp")
            date_str = date.strftime("%Y-%m-%d")

            last_div.add("%s - %s<br/>" % (login, date_str))

            note_str_div = DivWdg()
            last_div.add(note_str_div)
            note_str_div.add(note_str)
            note_str_div.add_style("padding: 15px")

            last_div.add_style("padding: 5px")


            last_div.add_behavior( {
                'type': 'click_up',
                'search_key': search_key,
                'cbjs_action': '''

                var class_name = 'tactic.ui.input.note_input_wdg.NoteHistoryWdg';
                var kwargs = {
                    search_key: bvr.search_key
                }
                spt.panel.load_popup("Notes Log", class_name, kwargs);
                
                '''
            } )


        name = my.get_input_name()
        text = TextAreaWdg(name)
        top.add(text)

        if search_key and not sobject.is_insert():
            from tactic.ui.widget import DiscussionWdg
            discussion_wdg = DiscussionWdg(search_key=search_key, context_hidden=False, show_note_expand=False, show_add=False)
            top.add(discussion_wdg)

        return top



class NoteHistoryWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        my.set_as_panel(top)
        top.set_unique_id()
        top.add_style("min-width: 600px")
        top.add_style("max-height: 600px")
        top.add_style("overflow-y: auto")

        top.add_color("background", "background")
        top.add_color("color", "color")

        sobject = my.get_option("sobject")
        if not sobject:
            search_key = my.get_option("search_key")
            sobject = Search.get_by_search_key(search_key)
        else:
            search_key = sobject.get_search_key()


        search = Search("sthpw/note") 
        #search.add_relationship_filters(my.filtered_parents, type='hierarchy')
        search.add_parent_filter(sobject)
        search.add_order_by("process")
        search.add_order_by("context")
        search.add_order_by("timestamp desc")
        notes = search.get_sobjects()

        notes.extend(notes)
        notes.extend(notes)
        notes.extend(notes)
        notes.extend(notes)


        top.add_smart_style("spt_note", "padding", "15px")

        for i, note in enumerate(notes):

            note_div = DivWdg()
            top.add( note_div )
            note_div.add( my.get_note_wdg(note) )

            if i % 2 == 0:
                note_div.add_color("background", "background", -3)

        return top


    def get_note_wdg(my, note):

        div = DivWdg()
        div.add_class("spt_note")

        note_str = note.get_value("note")
        login = note.get_value("login")
        if not login:
            login = "<i style='opacity: 0.3'>unknown</i>"
        date = note.get_datetime_value("timestamp")
        date_str = date.strftime("%Y-%m-%d")

        div.add("%s - %s<br/>" % (login, date_str))
        div.add(note_str)


        return div




