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
    def __init__(self):
        super(ClipboardWdg,self).__init__()

    def get_display(self):
        # set up the self refresh event for other widgets or callbacks to call
        event_container = WebContainer.get_event_container()
        script = ClipboardWdg.get_self_refresh_script(show_progress=False)
        event_container.add_listener(self.EVENT_ID, script, replace=True )

        if self.is_from_ajax():
            div = Widget()
        else:
            div = DivWdg()
            div.set_id(self.ID)
            div.add_style("display: block")
            div.add_class("background_box")
            div.add_style("padding-left: 3px")
            div.add_style("padding-right: 3px")
            div.add_style("height: 1.5em")
            div.add_style("width: 150px")

        # handle the ajax
        self.set_ajax_top_id(self.ID)
        self.register_cmd(ClipboardClearCbk)
        refresh_script = self.get_refresh_script()

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
    def __init__(self, view="table"):
        super(ClipboardListWdg,self).__init__()
        self.view = view

    def get_display(self):
    
        clipboards = Clipboard.get_all("select")

        from layout_wdg import TableWdg
        widget = Widget()
        widget.add( "<h3>Clipboard</h3>")
        table = TableWdg("sthpw/clipboard", self.view)
        table.set_sobjects(clipboards)
        widget.add(table)
        return widget



class ClipboardHistoryElement(BaseTableElementWdg):

    def get_display(self):

        sobject = self.get_current_sobject()
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
    def __init__(self, sobject, icon_size=0):
        assert sobject
        super(ClipboardAddWdg,self).__init__()
        self.sobject = sobject
        self.icon_size = icon_size
        self.thumbnail_mode = True
    
    def set_thumbnail_mode(self, mode):
        ''' If set to true, adding it will refresh the thumbnail '''
        self.thumbnail_mode = mode

    def get_id(self):
        return "clipboard_%s" % self.sobject.get_search_key()

    def get_display(self):
        ajax = AjaxCmd()
        ajax.register_cmd("pyasm.widget.ClipboardAddCbk")
        progress = ajax.generate_div()
        progress.add_style('display', 'inline')

        search_type = self.sobject.get_search_type()
        search_id = self.sobject.get_id()
        ajax.set_option("search_type", search_type)
        ajax.set_option("search_id", search_id)

        search_key = self.sobject.get_search_key()

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

        if self.thumbnail_mode: 
            post_script.append( ThumbWdg.get_refresh_script(\
                self.sobject, self.icon_size, show_progress=False) )
        progress.set_post_ajax_script(';'.join(post_script))
        
        if Clipboard.is_selected(self.sobject):
            checkbox.set_option("checked", "1")
        """
        span.add(checkbox)
        span.add(progress)

        return span



class ClipboardAddCbk(Command):

    def get_title(self):
        return "Add to clipboard"


    def is_undoable():
        return False
    is_undoable = staticmethod(is_undoable)

    def check(self):
        return True

    def execute(self):

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


            self.description = "Removed %s '%s' from clipboard" % (search_type_obj.get_title(), sobject.get_code() )

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

            self.description = "Added %s '%s' to clipboard" % (search_type_obj.get_title(), sobject.get_code() )



class ClipboardClearCbk(Command):
    def get_title(self):
        return "Clear clipboard"

    def is_undoable():
        return False
    is_undoable = staticmethod(is_undoable)

    def execute(self):
        category = "select"
        search = Search("sthpw/clipboard")
        search.add_filter("category", category)
        search.add_user_filter()
        clipboards = search.get_sobjects()
        for item in clipboards:
            item.delete()

        self.description = "Cleared %s items from clipboard" % len(clipboards)



class ClipboardCopyInputWdg(BaseInputWdg):
    '''Input that edit widget can use to add as a connection'''

    def get_display(self):

        widget = Widget()
        checkbox = CheckboxWdg(self.get_input_name())
        widget.add(checkbox)

        where = self.get_option("where")
        count = Clipboard.get_count(where=where)

        widget.add("Copy from clipboard: ( %s items )" % count)

        return widget



            



class ClipboardCopyConnectionCmd(DatabaseAction):
    '''Action that edit widget can use to add as a connection'''

    def execute(self):

        name = self.get_input_name()
        web = WebContainer.get_web()
        if not web.get_form_value( self.get_input_name() ):
            return

        clipboard_items = Clipboard.get_all(category='select')
        sobject = self.sobject

        context = self.get_option("context")
        if not context:
            context = 'reference'

        for item in clipboard_items:
            parent = item.get_parent()
            SObjectConnection.create(parent, sobject, context)
            



class ClipboardMoveToCategoryCbk(Command):
    '''Moves the selected clipboard items to a new category'''
    COPY_BUTTON = "Copy from Clipboard"

    def get_title(self):
        return "ClipboardMoveToCategoryCbk"

    def check(self):
        web = WebContainer.get_web()
        if not web.get_form_value(self.COPY_BUTTON):
            return False

        self.category = web.get_form_value("clipboard_category")
        if not self.category:
            raise UserException("You need to select a watch list")
            return False

        return True

    def execute(self):

        clipboard_items = Clipboard.get_all(category="select")
        for item in clipboard_items:
            item.set_value("category", self.category)
            item.commit()

            










