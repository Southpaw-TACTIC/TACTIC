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

__all__ = ['SObjectNavigatorWdg', 'SObjectNavigatorLayoutWdg', 'SObjectCodeLinkTableElementWdg', 'PipelinePropertyWdg', 'PipelineContextWdg']

from pyasm.common import Environment
from pyasm.search import SearchType, Search, SearchException
from pyasm.web import Widget, DivWdg, SpanWdg, HtmlElement, WebState, WebContainer, Table
from pyasm.biz import Schema, Project, Pipeline

from pyasm.widget import HiddenWdg, SObjectLevelWdg, FilterSelectWdg, TextWdg, SwfEmbedWdg, TableWdg, ThumbWdg, BaseTableElementWdg, IconWdg, IconButtonWdg, CustomEditViewPopupWdg, ProgressWdg, HierarchicalFilterWdg, GeneralFilterWdg, SelectWdg
from pyasm.common import Environment


class SObjectNavigatorWdg(Widget):
    '''Main widget to navigate between sobjects'''
    def get_display(my):

        div = DivWdg()

        schema = Schema.get()
        if schema:
            div.add( my.get_schema_wdg(schema) )
            div.add( HtmlElement.br() )

        schema = Schema.get_admin_schema()
        div.add( my.get_schema_wdg(schema) )

        return div


    def get_schema_wdg(my, schema):
        web = WebContainer.get_web()

        div = DivWdg()
        search_type = web.get_form_value("filter|search_type")
        search_id = web.get_form_value("filter|search_id")
        div.add( HiddenWdg("filter|search_type", search_type ) )
        div.add( HiddenWdg("filter|search_id", search_id ) )

        div.add_style("font-size: 1.2em")
        div.add_style("padding: 5px")

        if not schema:
            Environment.add_warning("No schema", "No schema found")
            return div
        schema_xml = schema.get_xml_value("schema")
        code = schema.get_code()


        project_code = Project.get_project_code()
        #link = HtmlElement.href("Schema [%s]" % code, "/tactic/%s/?filter|search_type=" % project_code )
        link = SpanWdg()
        link.add("Schema [%s]" % code)
        div.add("<b>%s</b><br/>" % link.get_buffer_display())
        div.add("<hr/>")
        schema_search_types = schema_xml.get_values("schema/search_type/@name")
        for schema_search_type in schema_search_types:
            try:
                search_type_obj = SearchType.get(schema_search_type)
            except SearchException:
                title = "<span style='color: #F44'>? %s</span>" % schema_search_type
            else:
                title = search_type_obj.get_title()


            span = DivWdg()
            link = HtmlElement.href(title, "/tactic/%s/?filter|search_type=%s" % (project_code, schema_search_type) )
            if schema_search_type == search_type:
                span.add_class("active_label")


            # walk up the tree
            current_type = schema_search_type
            has_parent = False
            while 1:
                parent_type = schema.get_parent_type(current_type)
                if parent_type:
                    span.add("&nbsp;&nbsp;&nbsp;")
                    has_parent = True
                else:
                    if has_parent:
                        span.add("+&nbsp;")
                    break
                current_type = parent_type

            span.add(link)
            div.add(span)

        return div




class SObjectNavigatorLayoutWdg(Widget):

    def get_display(my):
        web = WebContainer.get_web()
        search_type = web.get_form_value("filter|search_type")
        search_id = web.get_form_value("filter|search_id")
        view = web.get_form_value("filter|view")

        widget = Widget()

        left = DivWdg()
        left.set_id('layout/left')
        left.add_style("float: left")
        left.add_style("margin: 20px 0 0 -10px")
        left.add_style("width: 200px")
        widget.add(left)

        #title = DivWdg()
        #title.add(IconButtonWdg("Create", IconWdg.INFO_OPEN_SMALL))
        #title.add_event("onclick", "toggle_display('layout_sidebar')")
        #left.add(title)

        sidebar = DivWdg()
        sidebar.add_style("display: block")
        sidebar.set_id("layout_sidebar")
        sidebar.add(SObjectNavigatorWdg())
        sidebar.add_class("background_box")
        sidebar.add_class("background")
        left.add(sidebar)


        div = DivWdg()
        widget.add(div)
        layout = Table()
        div.add(layout)


        if not WebContainer.get_web().is_IE():
            layout.set_style("width: 80%")
        tr = layout.add_row()
        layout.add_header("<span>&nbsp;</span>")
        level_wdg = SObjectLevelWdg()
        layout.add_header(level_wdg)
        layout.set_id("layout")
        layout.add_row()


        if not search_type:
            #div = DivWdg()
            #div.add_style("z-index: -100")

            #progress = ProgressWdg()
            #div.add(progress)
            #swf = SwfEmbedWdg()
            #swf.set_code( Project.get_project_code() )
            #swf.set_search_type("sthpw/schema")
            #swf.set_connector_type("hierarchy")
            #div.add(swf)
            #content_td.add(div)

            widget.add("<br clear='all'/>")
            widget.add("<br clear='all'/>")
            return widget



        content_td = layout.add_cell()
        content_td.add_style("vertical-align: top")

        div = DivWdg()

        nav = DivWdg(css='filter_box')

        view_options = "custom|list|manage|table"
        label_options = "custom|list|manage|table"
        if search_type:
            from pyasm.widget import WidgetConfigView
            config = WidgetConfigView.get_by_search_type(search_type, "table")
            view_options = "|".join( config.get_views() )
            label_options = "|".join( config.get_views() )

        view_filter = FilterSelectWdg(name="filter|view")
        view_filter.set_option("values", view_options)
        view_filter.set_option("labels", label_options)
        view_filter.add_empty_option("-- Custom --")
        span = SpanWdg(css="med")
        span.add_style("float: left")
        span.add("View: ")
        span.add(view_filter)
        nav.add(span)

        if view.startswith("custom_"):
            from pyasm.widget import CustomCreateViewPopupWdg
            custom_view_wdg = CustomCreateViewPopupWdg(search_type)
            nav.add(custom_view_wdg)


        nav.add(HtmlElement.br(clear="all"))
        nav.add(HtmlElement.br(clear="all"))


        hierarchical_filter = HierarchicalFilterWdg()
        hierarchical_filter.set_name("filter|parent_%s" % search_type)
        nav.add(hierarchical_filter)

        search_filter = TextWdg(name="filter|search")
        span = SpanWdg(css="med")
        span.add("Search: ")
        #span.add(search_filter)

        if search_type:
            general_filter = GeneralFilterWdg()
            general_filter.set_columns_from_search_type(search_type)
            span.add(general_filter)
            nav.add(span)


        # get the view
        view = view_filter.get_value()
        if not view:
            user = Environment.get_user_name() 
            view = "custom_%s" % user


        if view.startswith("custom_"):
            from pyasm.widget import CustomViewWdg
            custom_view_wdg = CustomViewWdg(search_type)
            custom_view_wdg.set_mode("user")
            nav.add(custom_view_wdg)


        nav.add("<br/>")

        div.add(nav)

      

        if not search_id:
            search = Search(search_type)
            table = TableWdg(search_type, view, is_dynamic=True)
            hierarchical_filter.alter_search(search)
            general_filter.alter_search(search)
            #search_value = search_filter.get_value()
            table.set_search(search)
            table.do_search()
            #table.set_sobjects( search.get_sobjects() )



            div.add(table)

            content_td.add( div )
        else:
            content_td.add( SObjectInfoLayoutWdg() )

        widget.add("<br clear='all'/>")
        widget.add("<br clear='all'/>")

        return widget



class SObjectInfoLayoutWdg(Widget):

    def get_display(my):

        web = WebContainer.get_web()
        search_type = web.get_form_value("filter|search_type")
        search_id = web.get_form_value("filter|search_id")

        sobject = Search.get_by_id(search_type, search_id)

        layout = Table()

        table = TableWdg(search_type)
        table.set_show_property(False)
        table.set_sobject(sobject)
        layout.add_row_cell(table)


        tr = layout.add_row()
        td = layout.add_cell()
        td.add_style("vertical-align: top")

        from pyasm.widget import SObjectTaskTableElement
        task_wdg = SObjectTaskTableElement()
        task_wdg.set_sobject(sobject)
        td.add(task_wdg)

        
        from pyasm.prod.web import SObjectDetailWdg
        detail = SObjectDetailWdg()
        detail.set_sobject(sobject)
        td = layout.add_cell(detail)
        td.add_style("vertical-align: top")
        td.add_style("width: 100%")

        return layout


class SObjectCodeLinkTableElementWdg(BaseTableElementWdg):
    def get_display(my):
        sobject = my.get_current_sobject()
        value = sobject.get_code()

        project_code = Project.get_project_code()
        search_type = sobject.get_base_search_type()
        search_id = sobject.get_id()
        link = HtmlElement.href(value, "/tactic/%s/?filter|search_type=%s&filter|search_id=%s" % (project_code, search_type, search_id) )


        return link




class PipelinePropertyWdg(Widget):

    def get_display(my):

        web = WebContainer.get_web()

        div = DivWdg()
        div.set_id("properties_editor")
        #div.add_style("display", "none")

        # get a list of known properties
        #properties = ["completion", "task_pipeline", "color"]
        properties = ['group', "completion", "task_pipeline", 'assigned_login_group', 'supervisor_login_group', 'duration']


        # show other properties
        table = Table()
        table.add_color('background-color', 'background')
        table.add_row()
        #table.add_header("Property")
        #table.add_header("Value")
        
		# Removing loop here because each property is now being displayed
		# with more than just a text box.
		
        # group
        table.add_row()
        td = table.add_cell('group')


        text_name = "property_group"
        text = TextWdg(text_name)
        text.set_id(text_name)
        text.add_event("onBlur", "set_properties()")

        th = table.add_header(text)
        
        # completion
        table.add_row()
        td = table.add_cell('completion (0 to 100)')

        text_name = "property_completion"
        text = TextWdg(text_name)
        text.set_id(text_name)
        text.add_event("onBlur", "set_properties()")

        th = table.add_header(text)
        
        # These searchs are needed for the task_pipeline select widget
        task_pipeline_search = Search('sthpw/pipeline')
        task_pipeline_search.add_filter('search_type', 'sthpw/task')
        task_pipelines = task_pipeline_search.get_sobjects()
        
        normal_pipeline_search = Search('sthpw/pipeline')
        normal_pipeline_search.add_filter('search_type', 'sthpw/task', '!=')
        normal_pipelines = normal_pipeline_search.get_sobjects()
        
        # task_pipeline
        table.add_row()
        td = table.add_cell('task_pipeline')

        text_name = "property_task_pipeline"
        select = SelectWdg(text_name)
        select.append_option('<< sthpw/task pipelines >>', '')
        
        for pipeline in task_pipelines:
            select.append_option(pipeline.get_value('code'), pipeline.get_value('code'))
        select.append_option('', '')
        select.append_option('<< all other pipelines >>', '')
        
        for pipeline in normal_pipelines:
            select.append_option('%s (%s)'%(pipeline.get_value('code'), pipeline.get_value('search_type')), pipeline.get_value('code'))
        
        select.add_empty_option('-- Select --')
        select.set_id(text_name)
        select.add_event("onBlur", "set_properties()")

        th = table.add_header(select)
        
        # The search needed for the login_group select widgets
        login_group_search = Search('sthpw/login_group')
        
        # assigned_login_group
        table.add_row()
        td = table.add_cell('assigned_login_group')

        text_name = "property_assigned_login_group"
        select = SelectWdg(text_name)
        select.set_search_for_options(login_group_search, 'login_group', 'login_group')
        select.add_empty_option('-- Select --')
        select.set_id(text_name)
        select.add_event("onBlur", "set_properties()")

        th = table.add_header(select)
        
        # supervisor_login_group
        table.add_row()
        td = table.add_cell('supervisor_login_group')
        text_name = "property_supervisor_login_group"
        select = SelectWdg(text_name)
        select.set_search_for_options(login_group_search, 'login_group', 'login_group')
        select.add_empty_option('-- Select --')
        select.set_id(text_name)
        select.add_event("onBlur", "set_properties()")

        th = table.add_header(select)
        
        # duration
        table.add_row()
        td = table.add_cell('duration')

        text_name = "property_duration"
        text = TextWdg(text_name)
        text.add_style("width: 30px")
        text.set_id(text_name)
        text.add_event("onBlur", "set_properties()")

        th = table.add_header(text)
        th.add(" days")
        
        # color
        table.add_row()
        td = table.add_cell('color')

        text_name = "property_color"
        text = TextWdg(text_name)
        text.set_id(text_name)
        text.add_event("onBlur", "set_properties()")

        table.add_header(text)

        # label
        table.add_row()
        td = table.add_cell('label')

        text_name = "property_label"
        text = TextWdg(text_name)
        text.set_id(text_name)
        text.add_event("onBlur", "set_properties()")

        table.add_header(text)

        '''
        for property in properties:
            table.add_row()
            table.add_header(property)

            text_name = "property_%s" % property
            text = TextWdg(text_name)
            text.set_id(text_name)
            text.add_event("onBlur", "set_properties()")

            th = table.add_header(text)
        '''
        """
        property = "group"
        table.add_row()
        table.add_header(property)
        text_name = "property_%s" % property
        text = TextWdg(text_name)
        text.set_id(text_name)
        text.add_event("onBlur", "set_properties()")
        th = table.add_header(text)


        property = "task_pipeline"
        table.add_row()
        table.add_header(property)
        select_name = "property_%s" % property
        select = SelectWdg(select_name)
        select.add_empty_option("-- Default --")
        select.set_option("query", "sthpw/pipeline|code|code")
        select.set_option("query_filter", "search_type = 'sthpw/task'")
        select.add_event("onChange", "set_properties()")
        table.add_header(select)

        property = "completion"
        table.add_row()
        table.add_header(property)
        select_name = "property_%s" % property
        select = SelectWdg(select_name)
        select.set_option("values", "0|10|20|30|40|50|60|70|80|100")
        select.add_event("onChange", "set_properties()")
        table.add_header(select)
        """


        div.add(table)

        return div


class PipelineContextWdg(Widget):
    def get_display(my):

        web = WebContainer.get_web()

        div = DivWdg()
        div.set_id("context_editor")
        div.add_style("display", "none")

        property = "context"
        text_name = "property_%s" % property
        text = TextWdg(text_name)
        text.set_id(text_name)
        text.add_event("onBlur", "set_properties()")


        table = Table(css="table")
        table.add_row()
        th = table.add_header("Context:")
        th = table.add_header(text)
        div.add(table)

        return div





class PipelineEventWdg(Widget):
    def get_display():
        return "<h3>PipelineEventWdg</h3>"
        """
        process_name = "validation"
        pipeline_code = "checkin"

        # get the pipeline (probably better to use a virtual one)
        pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline:
            return ''

        process = pipeline.get_process(process_name)
        attributes = process.get_attributes()
        actions = process.get_action_nodes(scope=None)
        

        # add events
        button = IconButtonWdg("Add Event", IconWdg.CREATE, True)
        div.add(button)

        table = Table(css="table")
        #table.set_max_width()
        table.add_row()
        table.add_header("Event")
        table.add_header("Scope")
        table.add_header("Handler")

        for action in actions:

            attrs = action.attributes.values()
            dict = {}
            for attr in attrs:
                print "attr: ", attr.name, attr.value
                dict[attr.name] = attr.value
            print "dict: ", dict

            event_text = TextWdg("event_text")
            event_text.set_value(dict.get("event"))

            scope_text = TextWdg("scope_text")
            scope_text.set_value(dict.get("scope"))

            handler_text = TextWdg("handler_text")
            handler_text.set_value(dict.get("class"))

            table.add_row()
            table.add_cell(event_text)
            table.add_cell(scope_text)
            table.add_cell(handler_text)

        div.add(table)
        """

        return div





