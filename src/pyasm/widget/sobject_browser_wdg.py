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

__all__ = ['SObjectBrowserWdg', 'SObjectBrowserListWdg', 'SObjectBrowserAction', 'SObjectConnectionElement', 'SObjectConnectionDetailElement', 'SObjectConnectionRemoveCbk']

from pyasm.common import Date
from pyasm.search import Search, SearchType, SObject
from pyasm.web import DivWdg, WebContainer, Widget, AjaxLoader, Table, AjaxWdg, Callback
from pyasm.widget import *
from pyasm.biz import Project, SObjectConnection
from pyasm.command import DatabaseAction
from pyasm.common import Date, Common

class SObjectBrowserWdg(BaseInputWdg):
    '''A widget that allows you to search for an sobject and select it'''

    def get_display(self):
        div = DivWdg()

        select = SelectWdg("browser_search_type")
        select.add_empty_option("<- Select ->")
        search = Search("sthpw/search_object")
        search.add_order_by("search_type")

        search_types = self.get_option("search_types")
        if search_types:
            search_types = search_types.split("|")
            search.add_filters("search_type", search_types)

        select.set_persist_on_submit()
        select.set_search_for_options(search,"search_type","title")
        div.add(select)

        text = TextWdg("browser_search_text")
        text.set_persist_on_submit()
        div.add(text)

        # draw the sobjects
        sobject_element_id = "sobject_browser"
        button = ButtonWdg("Search")
        div.add(button)


        ajax = AjaxLoader()
        ajax.set_display_id(sobject_element_id)
        ajax.set_load_class("pyasm.widget.SObjectBrowserListWdg")
        ajax.add_element_name("browser_search_type")
        ajax.add_element_name("browser_search_text")
        script = ajax.get_on_script()
        button.add_event("onclick", script)


        div2 = DivWdg()
        div2.add_style("display: block")
        div2.set_id(sobject_element_id)
        div.add(div2)

        return div



class SObjectBrowserListWdg(Widget):

    def get_display(self):

        web = WebContainer.get_web()
        search_type = web.get_form_value("browser_search_type")
        search_text = web.get_form_value("browser_search_text")

        div = DivWdg()

        if search_type.startswith("prod/shot"):
            filter = self.get_filter(search_text, ['code','description'])
        elif search_type.startswith("prod/art_reference"):
            filter = self.get_filter(search_text, ['category','description'])
        else:
            filter = self.get_filter(search_text, ['name','code','description'])
        if not filter:
            return div

        search = Search(search_type)

        search.add_where(filter)

        div.add_style("width: 300")
        div.add_style("height: 200")
        div.add_style("overflow: auto")
        table = TableWdg(search_type, "list", css="minimal")
        table.set_show_property(False)
        table.set_sobjects(search.get_sobjects())
        div.add(table)

        return div


    def get_filter(self, text_value, columns):
        '''a more sophisticated search'''
        if text_value == "":
            return None

        filter_string = Search.get_compound_filter(text_value, columns)
        return filter_string 


class SObjectBrowserAction(DatabaseAction):

    def execute(self):
        # do nothing
        pass

    def postprocess(self):
        web = WebContainer.get_web()
        values = web.get_form_values("select_key")
        if not values or values == ['']:
            return

        dst_sobject = self.sobject

        project_code = Project.get_project_code()

        for value in values:
            src_sobject = Search.get_by_search_key(value)
            if not src_sobject:
                continue
            connection = SearchType.create("sthpw/connection")
            connection.set_value("src_search_type", src_sobject.get_search_type() )
            connection.set_value("dst_search_type", dst_sobject.get_search_type() )
            connection.set_value("src_search_id", src_sobject.get_id() )
            connection.set_value("dst_search_id", dst_sobject.get_id() )
            connection.set_value("context", "reference")
            connection.set_value("project_code", project_code)

            connection.commit()



class SObjectConnectionElement(AjaxWdg, BaseTableElementWdg):

    def set_name(self, name):
        self.name = name

    def init_cgi(self):
        web = WebContainer.get_web()
        search_key = web.get_form_value("search_key")
        if not search_key:
            search_type = web.get_form_value("search_type")

            if not search_type:
                return

            search_id = web.get_form_value("search_id")
            search_key = "%s|%s" % (search_type,search_id)
        sobject = Search.get_by_search_key(search_key)
        self.set_sobject(sobject)

    def get_display(self):

        # get all of the options
        direction = self.get_option("direction")
        if not direction:
            direction = "dst"

        icon_size = self.get_option("icon_size")
        if not icon_size:
            icon_size = 60

        src_sobject = self.get_current_sobject()
        dst_sobjects = []

        if isinstance(src_sobject, SObjectConnection):
            connection = src_sobject

            dst_sobject = connection.get_sobject(direction)
            src_sobject = connection.get_sobject(direction="src")

            connections = [connection]
            dst_sobjects = [dst_sobject]
        else:
            connections, dst_sobjects = SObjectConnection.get_connected_sobjects(src_sobject, direction)


        div = DivWdg()
        div.set_id("connection_%s" % src_sobject.get_id() )

        # set the ajax options
        self.set_ajax_top(div)
        self.set_ajax_option("search_key", src_sobject.get_search_key() )
        self.register_cmd("pyasm.widget.SObjectConnectionRemoveCbk")

        table = Table()
        table.set_max_width()
        table.set_class("minimal")
        count = 0
        for dst_sobject in dst_sobjects:
            tr = table.add_row()
            if not dst_sobject:
                table.add_cell("referenced to retired or deleted asset....")
                continue
            if dst_sobject.is_retired():
                tr.add_class("retired_row")

            thumb = ThumbWdg()
            thumb.set_show_filename(True)

            thumb.set_icon_size(icon_size)
            thumb.set_sobject(dst_sobject)
            td = table.add_cell(thumb)
            td.add_style("padding: 1px")
            td.add_style("width: 20%")

            id = dst_sobject.get_id()
            name = dst_sobject.get_name()
            code = dst_sobject.get_code()
            if code == str(id):
                pass 
            elif name == code:
                td = table.add_cell(name)
                td.add_style("width: 20%")
            else:
                td = table.add_cell("%s<br/>%s" % (name,code) )
                td.add_style("width: 20%")
            if dst_sobject.has_value("title"):
                td = table.add_cell(dst_sobject.get_value("title") )
            elif dst_sobject.has_value("description"):
                td = table.add_cell(dst_sobject.get_value("description") )
                if dst_sobject.has_value("keywords"):
                     table.add_cell(dst_sobject.get_value("keywords") )
            
            # remove connection
            connection = connections[count]
            connection_id = connection.get_id()
            self.set_ajax_option("connection_id", connection_id )
            refresh_script = self.get_refresh_script(False)

            remove = IconButtonWdg("Remove Connection", IconWdg.DELETE)
            remove.add_event("onclick", refresh_script)

            table.add_cell(remove)

            count += 1

        div.add(table)
        return div


class SObjectConnectionDetailElement(SObjectConnectionElement):

    def preprocess(self):
        direction = self.get_option("direction")
        self.info = {}
        if not direction:
            direction = "dst"
        for sobject in self.sobjects:
            src_sobject = sobject
            dst_sobjects = []
            if isinstance(src_sobject, SObjectConnection):
                connection = src_sobject

                dst_sobject = connection.get_sobject(direction)
                src_sobject = connection.get_sobject(direction="src")

                connections = [connection]
                dst_sobjects = [dst_sobject]
            else:
                connections, dst_sobjects = SObjectConnection.get_connected_sobjects(src_sobject, direction)

            self.info[sobject.get_search_key()] = (connections, dst_sobjects, sobject)

        # reorder sobjects
        sobj_dict = {}
        idx = 0
        for connections, dst_sobjects, sobject in self.info.values():
            obj = dst_sobjects[0]
            # obj has been deleted
            if obj:
                key = '%s_%s' %(obj.get_value('timestamp'), obj.get_id())
            else:
                key = '000_deleted_%s' %idx
            sobj_dict[key] = sobject
            idx += 1

        sobj_list = Common.sort_dict(sobj_dict, reverse=True)

        self.sobjects = sobj_list


    def get_display(self):

        # get all of the options
        direction = self.get_option("direction")
        if not direction:
            direction = "dst"
        

        icon_size = self.get_option("icon_size")
        if not icon_size:
            icon_size = 60
        try:
            sobject = self.get_current_sobject()
        except IndexError:
            return ''
        if not hasattr(self, 'info'):
            return ''
        
        connections, dst_sobjects, sobj = self.info.get(sobject.get_search_key())
      
        src_sobject = sobject

        # may not need this due to preprocess
        if isinstance(src_sobject, SObjectConnection):
            connection = src_sobject
            src_sobject = connection.get_sobject(direction="src")


        div = DivWdg()
        div.set_id("connection_%s" % src_sobject.get_id() )

        # set the ajax options
        self.set_ajax_top(div)
        self.set_ajax_option("search_key", src_sobject.get_search_key() )
        self.register_cmd("pyasm.widget.SObjectConnectionRemoveCbk")

        table = Table()
        table.set_max_width()
        table.set_class("minimal")
        count = 0
        
        for dst_sobject in dst_sobjects:
            tr = table.add_row()
            if not dst_sobject:
                table.add_cell("referenced to retired or deleted asset....")
                continue
            if dst_sobject.is_retired():
                tr.add_class("retired_row")

            thumb = ThumbWdg()
            thumb.set_show_filename(True)
            thumb.set_show_orig_icon(True) 
            thumb.set_icon_size(icon_size)
            thumb.set_sobject(dst_sobject)
            td = table.add_cell(thumb)
            td.add_style("padding: 1px")
            td.add_style("width: 20%")

            id = dst_sobject.get_id()
            name = dst_sobject.get_name()
            code = dst_sobject.get_code()
            if code == str(id):
                pass 
            elif name == code:
                td = table.add_cell(name)
                td.add_style("width: 20%")
            else:
                td = table.add_cell("%s<br/>%s" % (name,code) )
                td.add_style("width: 20%")

            if dst_sobject.has_value("title"):
                td = table.add_cell("%s" % dst_sobject.get_value("title") )
            elif dst_sobject.has_value("description"):
                td = table.add_cell("%s" % dst_sobject.get_value("description") )
                td.add_style("width: 30%")
            if dst_sobject.has_value("keywords"):

                td = table.add_cell("%s" % dst_sobject.get_value("keywords") )
                td.add_style("width: 20%")

            if dst_sobject.has_value("timestamp"):
                td = table.add_cell("%s" % Date(dst_sobject.get_value("timestamp")).get_display_time() )
                td.add_style("width: 20%")

            update = UpdateWdg()
            update.set_sobject(dst_sobject)
            update.set_option('delete', 'false')
            table.add_cell(update)
             
            # remove connection
            connection = connections[count]
            connection_id = connection.get_id()
            self.set_ajax_option("connection_id", connection_id )
            refresh_script = self.get_refresh_script(False)

            remove = IconButtonWdg("Remove Connection", IconWdg.DELETE)
            remove.add_event("onclick", refresh_script)

            table.add_cell(remove)

            count += 1

        div.add(table)
        return div



class SObjectConnectionRemoveCbk(Callback):

    def get_title(self):
        return "Remove Connection"

    def execute(self):
        web = WebContainer.get_web()
        connection_id = web.get_form_value("connection_id")

        connection = SObjectConnection.get_by_id(connection_id)
        if connection:
            connection.delete()

        self.description = "Deleted connection"


