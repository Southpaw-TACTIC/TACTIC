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

__all__ = ['SchemaSectionWdg']

from pyasm.common import Common, Environment, SetupException
from pyasm.search import Search, SearchException, SearchType, DbContainer
from pyasm.biz import Schema, Project
from pyasm.web import Widget, DivWdg, WebContainer, SpanWdg, HtmlElement, Palette

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import LabeledHidableWdg, RoundedCornerDivWdg


class SchemaSectionWdg(BaseRefreshWdg):
    '''Widget that displays the schema'''

    def get_display(my):
        from pyasm.biz import Project

        security = Environment.get_security()
        if not security.check_access("builtin", "side_bar_schema", "allow", default="deny"):
            return DivWdg()


        section_div = LabeledHidableWdg(label="Schema Views")
        section_div.set_attr('spt_class_name', Common.get_full_class_name(my) )

        palette = Palette.get()
        color = palette.color("background3")

        project_div = RoundedCornerDivWdg(hex_color_code=color,corner_size="10")
        project_div.set_dimensions( width_str='175px', content_height_str='100px' )

        project = Project.get()
        project_code = project.get_code()
        project_type = project.get_type()

        div = DivWdg()
        section_div.add(project_div)
        project_div.add(div)

        # get project type schema
        schema = Schema.get_by_code(project_code)
        if schema:
            div.add( my.get_schema_wdg(schema) )
        #if not project_type:
        #    raise SetupException("Project type not found for this [%s]" %project_code)
        if project_type:
            schema = Schema.get_predefined_schema(project_type)
            if schema:
                div.add( my.get_schema_wdg(schema) )

        schema = Schema.get_predefined_schema('config')
        div.add( my.get_schema_wdg(schema) )

        schema = Schema.get_admin_schema()
        div.add( my.get_schema_wdg(schema) )

        return section_div


        # create a fake schema
        project = Project.get()
        db_name = project.get_database()
        sql = DbContainer.get(db_name)
        tables = sql.get_tables()
        tables.sort()
        tables_str = "\n".join( ['<search_type name="%s"/>'%x for x in tables] )

        # look at all of the search objects for mapped tables
        search = Search("sthpw/search_object")
        #search.add_where('''"namespace" = 'MMS' or namespace = '{project}' ''')
        search.add_filter("namespace", 'MMS')
        search.add_filter("namespace", '{project}')
        search.add_where("or")
        search_types = search.get_sobjects()
        #for search_type in search_types:
        #    print "hhhh: ", search_type

        schema_xml = '''
        <schema>
        %s
        </schema>
        ''' % tables_str
        schema = SearchType.create("sthpw/schema")
        schema.set_value("code", "table")
        schema.set_value("schema", schema_xml)
        #div.add( my.get_schema_wdg(schema) )



        return section_div


    def get_schema_wdg(my, schema):
        web = WebContainer.get_web()

        div = DivWdg()
        div.add_style("margin: 10 0 10 0")

        if not schema:
            Environment.add_warning("No schema", "No schema found")
            return div
        schema_xml = schema.get_xml_value("schema")
        code = schema.get_code()


        schema_search_types = schema_xml.get_values("schema/search_type/@name")
        if not schema_search_types:
            return


        title = DivWdg()
        view_margin_top = '4px'
        title.add_styles( "margin-top: %s; margin-bottom: 3px; vertical-align: middle" % view_margin_top )
        if not web.is_IE():
            title.add_styles( "margin-left: -10px; margin-right: -10px;" )
        title.add_looks( "navmenu_header" )

        title_label = SpanWdg()
        title_label.add_styles( "margin-left: 6px; padding-bottom: 2px;" )
        title_label.add_looks( "fnt_title_5 fnt_bold" )
        title_label.add("%s Schema" % code.capitalize())
        title.add(title_label)
        #title.add_style("margin-top: 7px")
        #title.add_style("font-weight: bold")
        #title.add_style("font-size: 1.1em")
        #title.add_style("color: black")
        #underline = HtmlElement.hr()
        #underline.add_style("color: black")
        #underline.add_style("size: 1px")
        #underline.add_style("margin-top: -3px")
        #title.add(underline)
        div.add( title )



        for schema_search_type in schema_search_types:
            try:
                search_type_obj = SearchType.get(schema_search_type)
            except SearchException:
                title = "<span style='color: #F44'>? %s</span>" % schema_search_type
            else:
                title = search_type_obj.get_title()


            span = DivWdg()
            span.add_style("padding: 1px")

            options = {
                'search_type': schema_search_type,
                'view': 'table',
                'schema_default_view': 'true',
            }
            link = my.get_link_wdg("schema", "main_body", title, options)


            # walk up the tree
            current_type = schema_search_type
            has_parent = False
            while 1:
                parent_type = schema.get_parent_type(current_type)
                if parent_type and parent_type != '*':
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


    def get_link_wdg(my, section_id, target_id, title, options):
        view_link_wdg = SpanWdg(css="hand")
        view_link_wdg.add_class("SPT_DTS")
        view_link_wdg.add_style("color: #292929")
        view_link_wdg.add_event("onmouseover", "this.style.background='#696969'")
        view_link_wdg.add_event("onmouseout", "this.style.background='#949494'")

        view_link_wdg.add(title)

        path = title
        options['path'] = "/%s" % title


        if not options.get('class_name'):
            options['class_name'] = "tactic.ui.panel.ViewPanelWdg"

        behavior = {
            'type':         'click_up',
            'cbfn_action':  'spt.side_bar.display_link_cbk',
            'target_id':    target_id,
            'title':        title,
            'options':      options,
        }
        view_link_wdg.add_behavior( behavior )

        options2 = options.copy()
        options2['inline_search'] = "true"

        behavior = {
            'type':         'click_up',
            'modkeys':      'SHIFT',
            'cbfn_action':  'spt.side_bar.display_link_cbk',
            'is_popup':     'true',
            'target_id':    path,
            'title':        title,
            'options':      options2,
        }
        view_link_wdg.add_behavior( behavior )

        return view_link_wdg


