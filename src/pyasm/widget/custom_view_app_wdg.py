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

__all__ = ["CustomViewAppWdg", 'CreateTabCmd', 'CustomCreateViewPopupWdg']

from pyasm.search import SearchException, SqlException, Search, SearchType, SObjectFactory
from pyasm.biz import Project
from pyasm.command import Command, CommandException
from pyasm.web import Widget, DivWdg, SpanWdg, HtmlElement, WebContainer, AjaxCmd
from pyasm.widget import SelectWdg, TextWdg, TableWdg, FilterCheckboxWdg, SwapDisplayWdg, HintWdg, IconSubmitWdg, IconButtonWdg, IconWdg, GeneralFilterWdg, EditWdg, PopupWdg, FilterSelectWdg, CheckboxWdg

from custom_view_wdg import *


class CustomViewAppWdg(Widget):

    def get_display(my):

        widget = Widget()

        div = DivWdg(css="filter_box")

        show_span = SpanWdg(css='med')
        show_span.add('Show All Types: ')
        checkbox = FilterCheckboxWdg('show_all_types')
        checkbox.set_persistence()
        show_span.add(checkbox)
        show_all_types = checkbox.get_value()
        div.add(show_span)


        span = SpanWdg(css="med")
        span.add("Search Type: ")

        select = SelectWdg("filter|search_type")
        select.add_empty_option("-- Select --")
        project = Project.get()
        project_type = project.get_base_type()
        search = Search("sthpw/search_object")
        if show_all_types:
            search.add_where('''
            namespace = '%s' or namespace = '%s' or search_type in ('sthpw/task')
            ''' % (project_type, project.get_code()) )
        else:
            # show only the custom ones
            search.add_filter('namespace', project.get_code() )

        search.add_order_by("title")
        sobjects = search.get_sobjects()

        select.set_sobjects_for_options(sobjects,"search_type", "title")
        #select.set_option("query", "sthpw/search_object|search_type|title")
        select.set_persistence()
        select.add_event("onchange", "document.form.submit()")
        search_type = select.get_value()
        span.add(select)
        div.add(span)


        # make sure the current selection exists
        try:
            SearchType.get(search_type)
        except SearchException, e:
            return div
        except SqlException, e:
            return div


        # add the view selector
        view_select = SelectWdg("view")
        view_select.add_empty_option("-- View --")
        view_select.add_event("onchange", "document.form.submit()")
        view_select.set_persist_on_submit()
        #view_select.set_persistence()
        span = SpanWdg(css="med")
        span.add("Defined Views: ")
        span.add(view_select)
        div.add(span)

        div.add( my.get_create_view_wdg(search_type))

        div.add( HtmlElement.br(2) )


        div.add( my.get_new_tab_wdg() )


        widget.add(div)

        search = Search("sthpw/widget_config")
        #search.add_user_filter()
        search.add_filter("search_type", search_type)
        search.add_where("view != 'definition' and view != 'custom'")
        #search.add_column("view")
        widget_configs = search.get_sobjects()
        if widget_configs:
            view_select.set_sobjects_for_options(widget_configs,"view","view")
        view = view_select.get_value()
        if not view:
            view = "custom"
            #return widget

        # get the selected widget config
        for widget_config in widget_configs:
            if widget_config.get_value("view") == view:
                break
        else:
            return widget

        # get the handler: a little HACKY.
        config_xml = widget_config.get_xml_value("config")
        handler = config_xml.get_value("config/%s/@handler" % view)

        if not search_type:
            return widget

        widget.add(HtmlElement.br())
        span = SpanWdg()
        custom_view = CustomViewWdg(search_type)
        span.add(custom_view)
        span.add_style("float: right")
        widget.add(span)


        widget.add( HtmlElement.br() )
        widget.add("<h3>Example View [%s]</h3>" % view)

        # add a general filter
        filter_div = DivWdg()
        for i in range(0,1):
            filter = GeneralFilterWdg()
            filter.set_columns_from_search_type(search_type)
            filter_div.add("Filter: ")
            filter_div.add(filter)
            #filter_div.add(IconWdg("Remove Filter", IconWdg.RETIRE))
            filter_div.add( HtmlElement.br(2) )

        widget.add(filter_div)

        search = Search(search_type)
        search.set_limit(5)
        filter.alter_search(search)

        
        if not handler:
            if view in ["edit","insert"]:
                table = EditWdg(search_type, view)
            else:
                table = TableWdg(search_type, view)
        else:
            table = eval("%s(search_type,view)" % handler)

        #table.alter_search(search)
        sobjects = search.get_sobjects()

        if not sobjects and view in ["edit","insert"]:
            sobjects = [SObjectFactory.create(search_type)]
        table.set_sobjects(sobjects)
        widget.add(table)

        # show the custom properties
        widget.add("<h3>Custom Properties [%s]</h3>" % search_type)
        search = Search("prod/custom_property")
        search.add_filter("search_type", search_type)
        # This is actually reading the sthpw/custom_property conf file, weird
        table = TableWdg("prod/custom_property")
        table.set_search_limit(5)
        table.set_sobjects(search.get_sobjects() )
        widget.add(table)

        return widget


    def get_create_view_wdg(my, search_type):

        # create popup
        create_popup = PopupWdg("create_action")
        create_popup.set_auto_hide(False)
        create_popup.add( "Enter name of view: " )
        create_popup.add( TextWdg("create_view_name") )
        #create_popup.add( HtmlElement.br(2) )
        #create_popup.add( "Copy from template: " )
        #template_select = SelectWdg("copy_from_template")
        #template_select.add_empty_option("-- None --")
        #template_select.set_option("values", "list|summary|task")
        #create_popup.add( template_select )
        create_popup.add(HtmlElement.br(2))
        create_popup.add(CheckboxWdg('auto_create_edit', label='Auto Create Edit View'))
        create_popup.add( HtmlElement.br(2, clear="all") )

        from pyasm.prod.web import ProdIconButtonWdg, ProdIconSubmitWdg
        create_icon = ProdIconButtonWdg('Create')

        ajax = AjaxCmd()
        ajax.register_cmd("pyasm.widget.CustomCreateViewCbk")
        ajax.add_element_name("create_view_name")
        ajax.add_element_name("auto_create_edit")
        ajax.set_option("search_type", search_type)
        ajax.set_option("project", Project.get_project_code() )
        div = ajax.generate_div()
        div.set_post_ajax_script('document.form.submit()')
        create_icon.add_event("onclick", "%s;%s" % (ajax.get_on_script(),"toggle_display('create_action')") )

        cancel_icon = ProdIconButtonWdg('Cancel')
        cancel_icon.add_event("onclick", "toggle_display('create_action')")

        span = SpanWdg()
        span.add( create_icon )
        span.add( cancel_icon )
        create_popup.add( span )
        create_popup.add( HtmlElement.br() )

        # add the create button
        create = IconButtonWdg("Create View", IconWdg.SAVE, True)
        create.add_event("onclick", "%s" % create_popup.get_on_script() )
        
        # lay it all out
        widget = Widget()
        widget.add(create_popup)
        widget.add(create)
        widget.add(div)
        return widget



    def get_new_tab_wdg(my):
        widget = Widget()

        span = SpanWdg()
        swap = SwapDisplayWdg.get_triangle_wdg()
        title = SpanWdg("Tab Creation")
        span.add(swap)
        span.add(title)
        span.add_style("float: left")
        widget.add(span)
        widget.add(HtmlElement.br() )

        # add the tab selector
        div = DivWdg()
        SwapDisplayWdg.create_swap_title( title, swap, div)

        tab_text = TextWdg("tab")
        tab_text.set_persistence()
        span = SpanWdg(css="med")
        span.add("Tab: ")
        span.add(tab_text)
        div.add(span)

        # parent
        index_text = TextWdg("parent_tab")
        index_text.set_persistence()
        span = SpanWdg(css="med")
        span.add("Parent Tab: ")
        span.add(index_text)
        span.add(HintWdg("Enter the name of the tab that this will fall under. Leave empty to put on the main tab") )
        div.add(span)


        # index
        index_text = TextWdg("index")
        index_text.set_attr("size", "4")
        index_text.set_persistence()
        span = SpanWdg(css="med")
        span.add("Index: ")
        span.add(index_text)
        span.add(HintWdg("Enter the numeric location for this tab to be placed") )
        div.add(span)

        WebContainer.register_cmd("CreateTabCmd")
        button = IconSubmitWdg("Create Tab", IconWdg.CREATE, True)
        div.add(button)

        widget.add(div)

        return widget


class CreateTabCmd(Command):

    def execute(my):
        web = WebContainer.get_web()
        if web.get_form_value("Create Tab"):
            title = web.get_form_value("tab")
            index = web.get_form_value("index")
            key = web.get_form_value("parent_tab")
            search_type = web.get_form_value("search_type")
            view = web.get_form_value("view")



        elif web.get_form_value("do_edit"):
            title = web.get_form_value("edit|title")
            index = web.get_form_value("edit|index")
            key = web.get_form_value("edit|parent_tab")
            search_type = web.get_form_value("edit|search_type")
            view = web.get_form_value("edit|view")

        else:
            return

        type = "TabWdg"

        if not view:
            view = "table"
        if not title:
            raise CommandException("Missing Tab Title")
        if not key:
            raise CommandException("Missing Parent Tab")
        if not index:
            index = "-1"
            

        sobject = SearchType.create("sthpw/widget_extend")
        sobject.set_value("type", type)
        sobject.set_value("key", key)

        data = '''<widget name="%s" index="%s">
  <display class="CustomTableWdg">
    <search_type>%s</search_type>
    <view>%s</view>
  </display>
</widget>
        ''' % ( title, index, search_type, view)

        sobject.set_value("data", data)
        sobject.commit()




class CustomCreateViewPopupWdg(Widget):
    def __init__(my, search_type, view=None):
        my.search_type = search_type
        my.view = view
        super(CustomCreateViewPopupWdg,my).__init__()


    def get_display(my):
        web = WebContainer.get_web()
        if not my.view:
            view = web.get_form_value("filter|view")

        # create popup
        create_popup = PopupWdg("create_action")
        create_popup.set_auto_hide(False)
        create_popup.add( "Enter name of view: " )
        create_popup.add( TextWdg("create_view_name") )
        #create_popup.add( HtmlElement.br(2) )
        #create_popup.add( "Copy from template: " )
        #template_select = SelectWdg("copy_from_template")
        #template_select.add_empty_option("-- None --")
        #template_select.set_option("values", "list|summary|task")
        #create_popup.add( template_select )

        create_popup.add( HtmlElement.br(2, clear="all") )

        from pyasm.prod.web import ProdIconButtonWdg, ProdIconSubmitWdg
        create_icon = ProdIconButtonWdg('Create')

        ajax = AjaxCmd()
        ajax.register_cmd("pyasm.widget.CustomCreateViewCbk")
        ajax.add_element_name("create_view_name")
        ajax.add_element_name("auto_create_edit")
        ajax.set_option("search_type", my.search_type)
        ajax.set_option("project", Project.get_project_code() )
        if my.view:
            ajax.set_option("template_view", my.view )
        create_icon.add_event("onclick", "%s;%s" % (ajax.get_on_script(),"toggle_display('create_action');setTimeout('document.form.submit()',1000)") )

        cancel_icon = ProdIconButtonWdg('Cancel')
        cancel_icon.add_event("onclick", "toggle_display('create_action')")

        span = SpanWdg()
        span.add( create_icon )
        span.add( cancel_icon )
        create_popup.add( span )
        create_popup.add( HtmlElement.br() )

        # add the create button
        create = IconButtonWdg("Create View", IconWdg.SAVE, True)
        create.add_event("onclick", "%s" % create_popup.get_on_script() )

        # lay it all out
        widget = Widget()
        widget.add(create_popup)
        # Browser does not have create
        #widget.add(create)
        return widget



