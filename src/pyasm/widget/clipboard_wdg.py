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


__all__ = ["ClipboardWdg", "ClipboardListWdg", "ClipboardAddWdg", "ClipboardAddCbk", "ClipboardCopyInputWdg", "ClipboardCopyConnectionCmd", "ClipboardMoveToCategoryCbk", 'ClipboardHistoryElement']


from pyasm.biz import Clipboard, SObjectConnection
from pyasm.search import SearchType, Search, SObject
from pyasm.command import Command, DatabaseAction
from pyasm.web import AjaxCmd, AjaxWdg, AjaxLoader, Widget, DivWdg, WebContainer, SpanWdg, Widget, HtmlElement
from input_wdg import CheckboxWdg, BaseInputWdg
from icon_wdg import *
from table_element_wdg import BaseTableElementWdg
from pyasm.common import UserException
import math, random, types, cgi



class ClipboardWdg(AjaxWdg):

    ID = 'ClipboardWdg'
    EVENT_ID = 'ClipboardWdg_refresh'
    def __init__(my):
        super(ClipboardWdg,my).__init__()

    def get_display(my):
        # set up the self refresh event for other widgets or callbacks to call
        event_container = WebContainer.get_event_container()
        script = ClipboardWdg.get_self_refresh_script(show_progress=False)
        event_container.add_listener(my.EVENT_ID, script, replace=True )

        if my.is_from_ajax():
            div = Widget()
        else:
            div = DivWdg()
            div.set_id(my.ID)
            div.add_style("display: block")
            div.add_class("background_box")
            div.add_style("padding-left: 3px")
            div.add_style("padding-right: 3px")
            div.add_style("height: 1.5em")
            div.add_style("width: 150px")

        # handle the ajax
        my.set_ajax_top_id(my.ID)
        my.register_cmd(ClipboardClearCbk)
        refresh_script = my.get_refresh_script()

        search = Search("sthpw/clipboard")
        search.add_user_filter()
        search.add_filter("category", "select")
        count = search.get_count()

        div.add("Clipboard: %s items: " % count)


        web = WebContainer.get_web()
        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "pyasm.widget.ClipboardListWdg")
        ref = url.to_string()

        iframe = WebContainer.get_iframe()
        iframe.set_width(64)
        action = iframe.get_on_script(ref)
       
        button = IconButtonWdg("View Clipboard", IconWdg.LOAD)
        button.add_event("onclick", action)
        div.add(button)



        # add the clear clipboard icon
        clear_icon = IconButtonWdg("Clear Clipboard", IconWdg.CLEAR)
        clear_icon.add_event("onclick", refresh_script)

        div.add(clear_icon)

        return div



class ClipboardListWdg(AjaxWdg):
    def __init__(my, view="table"):
        super(ClipboardListWdg,my).__init__()
        my.view = view

    def get_display(my):
    
        clipboards = Clipboard.get_all("select")

        from layout_wdg import TableWdg
        widget = Widget()
        widget.add( "<h3>Clipboard</h3>")
        table = TableWdg("sthpw/clipboard", my.view)
        table.set_sobjects(clipboards)
        widget.add(table)
        return widget



class ClipboardHistoryElement(BaseTableElementWdg):

    def get_display(my):

        sobject = my.get_current_sobject()
        sobject = sobject.get_parent()
        if not sobject:
            return Widget()

        # get all of the sobject_logs
        search = Search("sthpw/sobject_log")
        search.add_sobject_filter(sobject)
        logs = search.get_sobjects()

        search = Search("sthpw/transaction_log")
        search.add_filters("id", [x.get_value("transaction_log_id") for x in logs] )
        search.set_limit(200)
        logs = search.get_sobjects()
        
        from layout_wdg import TableWdg
        widget = Widget()
        table = TableWdg("sthpw/transaction_log")
        table.add_class("minimal")
        table.set_header_flag(False)
        table.set_show_property(False)
        table.set_no_results_wdg( "&nbsp;" )
        table.set_sobjects(logs)
        widget.add(table)
        return widget





class ClipboardAddWdg(Widget):
    '''A widget that allows adding of sobjects into the clipboard''' 
    def __init__(my, sobject, icon_size=0):
        assert sobject
        super(ClipboardAddWdg,my).__init__()
        my.sobject = sobject
        my.icon_size = icon_size
        my.thumbnail_mode = True
    
    def set_thumbnail_mode(my, mode):
        ''' If set to true, adding it will refresh the thumbnail '''
        my.thumbnail_mode = mode

    def get_id(my):
        return "clipboard_%s" % my.sobject.get_search_key()

    def get_display(my):
        ajax = AjaxCmd()
        ajax.register_cmd("pyasm.widget.ClipboardAddCbk")
        progress = ajax.generate_div()
        progress.add_style('display', 'inline')

        search_type = my.sobject.get_search_type()
        search_id = my.sobject.get_id()
        ajax.set_option("search_type", search_type)
        ajax.set_option("search_id", search_id)

        search_key = my.sobject.get_search_key()

        span = SpanWdg()
        span.set_id("clipboard_%s" % search_key)
        span.add_style("display: none")

        checkbox = CheckboxWdg()
        checkbox.add_style("vertical-align: top")
        checkbox.add_style("width: 7px")

        checkbox.add_event("onclick", "%s" % ajax.get_on_script(show_progress=False) )
        #checkbox.add_event("onmouseover", "this.style.width=15")
        #checkbox.add_event("onmouseout", "this.style.width=7")
        
        # FIXME :DEPRECATED
        """
        event = WebContainer.get_event_container()
        caller = event.get_event_caller(ClipboardWdg.EVENT_ID)

        from file_wdg import ThumbWdg
        post_script = [caller]

        if my.thumbnail_mode: 
            post_script.append( ThumbWdg.get_refresh_script(\
                my.sobject, my.icon_size, show_progress=False) )
        progress.set_post_ajax_script(';'.join(post_script))
        
        if Clipboard.is_selected(my.sobject):
            checkbox.set_option("checked", "1")
        """
        span.add(checkbox)
        span.add(progress)

        return span



class ClipboardAddCbk(Command):

    def get_title(my):
        return "Add to clipboard"


    def is_undoable():
        return False
    is_undoable = staticmethod(is_undoable)

    def check(my):
        return True

    def execute(my):

        web = WebContainer.get_web() 

        search_type = web.get_form_value("search_type")
        search_id = web.get_form_value("search_id")

        # check if item is already in the clipboard
        search = Search("sthpw/clipboard")
        search.add_filter("search_type", search_type)
        search.add_filter("search_id", search_id)
        search.add_filter("category", "select")
        if search.get_count():
            # if is already selected then remove.
            item = search.get_sobject()
            item.delete()

            search = Search(search_type)
            search.add_id_filter(search_id)
            sobject = search.get_sobject()
            search_type_obj = sobject.get_search_type_obj()


            my.description = "Removed %s '%s' from clipboard" % (search_type_obj.get_title(), sobject.get_code() )

        else:
            search = Search(search_type)
            search.add_id_filter(search_id)
            sobject = search.get_sobject()
            search_type_obj = sobject.get_search_type_obj()


            clipboard = SearchType.create("sthpw/clipboard")
            clipboard.set_value("search_type", search_type)
            clipboard.set_value("search_id", search_id)
            #TODO: set project_code as well
            clipboard.set_value("category", "select")
            clipboard.set_user()
            clipboard.commit()

            my.description = "Added %s '%s' to clipboard" % (search_type_obj.get_title(), sobject.get_code() )



class ClipboardClearCbk(Command):
    def get_title(my):
        return "Clear clipboard"

    def is_undoable():
        return False
    is_undoable = staticmethod(is_undoable)

    def execute(my):
        category = "select"
        search = Search("sthpw/clipboard")
        search.add_filter("category", category)
        search.add_user_filter()
        clipboards = search.get_sobjects()
        for item in clipboards:
            item.delete()

        my.description = "Cleared %s items from clipboard" % len(clipboards)



class ClipboardCopyInputWdg(BaseInputWdg):
    '''Input that edit widget can use to add as a connection'''

    def get_display(my):

        widget = Widget()
        checkbox = CheckboxWdg(my.get_input_name())
        widget.add(checkbox)

        where = my.get_option("where")
        count = Clipboard.get_count(where=where)

        widget.add("Copy from clipboard: ( %s items )" % count)

        return widget



            



class ClipboardCopyConnectionCmd(DatabaseAction):
    '''Action that edit widget can use to add as a connection'''

    def execute(my):

        name = my.get_input_name()
        web = WebContainer.get_web()
        if not web.get_form_value( my.get_input_name() ):
            return

        clipboard_items = Clipboard.get_all(category='select')
        sobject = my.sobject

        context = my.get_option("context")
        if not context:
            context = 'reference'

        for item in clipboard_items:
            parent = item.get_parent()
            SObjectConnection.create(parent, sobject, context)
            



class ClipboardMoveToCategoryCbk(Command):
    '''Moves the selected clipboard items to a new category'''
    COPY_BUTTON = "Copy from Clipboard"

    def get_title(my):
        return "ClipboardMoveToCategoryCbk"

    def check(my):
        web = WebContainer.get_web()
        if not web.get_form_value(my.COPY_BUTTON):
            return False

        my.category = web.get_form_value("clipboard_category")
        if not my.category:
            raise UserException("You need to select a watch list")
            return False

        return True

    def execute(my):

        clipboard_items = Clipboard.get_all(category="select")
        for item in clipboard_items:
            item.set_value("category", my.category)
            item.commit()

            










