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

__all__ = ['TableViewManagerWdg', 'ElementDefinitionWdg']

import os

import tacticenv

from pyasm.common import Date, Environment
from pyasm.search import Search
from pyasm.web import DivWdg, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, TextWdg, HiddenWdg, WidgetConfigView, TextAreaWdg, TextWdg, ProdIconButtonWdg, CheckboxWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.filter import FilterData
from tactic.ui.container import RoundedCornerDivWdg
from tactic.ui.widget import CalendarInputWdg, TextBtnSetWdg, SearchTypeSelectWdg

from dateutil import parser


from view_manager_wdg import ViewManagerWdg


# DEPRECATED: moved to tactic/ui/manager/...


class TableViewManagerWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'search type of the view',
        'view': 'view to be edited'
        }


    def get_display(my):

        top = DivWdg()
        my.set_as_panel(top)
        top.add_class("spt_table_view_manager_top")

        my.search_type = my.kwargs.get("search_type")
        my.view = my.kwargs.get("view")

        web = WebContainer.get_web()
        if not my.search_type:
            my.search_type = web.get_form_value("search_type")
        if not my.view:
            my.view = web.get_form_value("view")
        if not my.view:
            my.view = 'table'


        filter_wdg = my.get_filter_wdg()
        top.add(filter_wdg)


        #web = WebContainer.get_web()
        #search_type = web.get_form_value("search_type")
        #view = web.get_form_value("view")

        view_manager_wdg = ViewManagerWdg(search_type=my.search_type,view=my.view)
        top.add(view_manager_wdg)


        return top

        
    def get_filter_wdg(my):

        div = DivWdg()
        div.add_style("margin: 10px")
        div.add_class("spt_view_manager_filter")
        div.add('Search Type: ')

        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            select_mode =  SearchTypeSelectWdg.ALL
        else:
            select_mode =  SearchTypeSelectWdg.ALL_BUT_STHPW
        select = SearchTypeSelectWdg(name='search_type', \
            mode=select_mode)

        behavior = {'type': 'change', 'cbjs_action': '''
            var filter_top = bvr.src_el.getParent(".spt_view_manager_filter");
            var table_top = bvr.src_el.getParent(".spt_table_view_manager_top");
            var manager_top = table_top.getElement(".spt_view_manager_top");

            var input = spt.api.Utility.get_input(filter_top, 'search_type');
            var view_input = spt.api.Utility.get_input(filter_top, 'view');
            var view_input_value = '';
            if (view_input != null) {
                view_input_value = view_input.value;
            }
            var values = {'search_type': input.value, 'view': view_input_value, 'is_refresh': 'true'}; 
            spt.panel.refresh(table_top, values);'''
            #//spt.panel.refresh(manager_top, values);'''
        }
        select.add_behavior(behavior)
        select.set_value(my.search_type)
        div.add(select)

        if not my.search_type:
            return div

        div.add('View: ')
        view_wdg = SelectWdg("view")
        view_wdg.set_value(my.view)
        view_wdg.add_empty_option("-- Select --")
        view_wdg.add_behavior(behavior)
        div.add(view_wdg)


        search = Search("config/widget_config")
        search.add_filter("search_type", my.search_type)
        db_configs = search.get_sobjects()


        views = set()
        for db_config in db_configs:
            view = db_config.get_value("view")
            views.update([view])

        if my.search_type and my.view:
            config_view = WidgetConfigView.get_by_search_type(my.search_type, my.view)

            configs = config_view.get_configs()
            for x in configs:
                view = x.get_view()
                file_path = x.get_file_path()
                if view != my.view:
                    continue
                if file_path and file_path.endswith("DEFAULT-conf.xml"):
                    continue
                config_views = x.get_all_views()
                views.update(config_views)

        views_list = list(views)
        views_list.sort()
        view_wdg.set_option("values", views_list)


        return div



    def get_action_menu_details(my):
        # FIXME: not needed
        is_personal = 'false'
        return {
            'menu_id': 'ManageViewPanelWdg_DropdownMenu', 'width': 250, 'allow_icons': False,
            'opt_spec_list': [
                { "type": "action", "label": "New Link", "bvr_cb":
                    {'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'new_link'},'%s',%s);" % (my.view,is_personal)} },
                { "type": "separator" },
                { "type": "action", "label": "Save", "bvr_cb":
                    {'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'save'},'%s',%s);" % (my.view,is_personal)} }
            ]
        }






class ElementDefinitionWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'search type for this search widget',
        'view': 'the top level view we are looking at',
        'element_name': 'the element name to look at',
        }

    def get_display(my):
        top = DivWdg()


        search_type = my.kwargs.get("search_type")
        view = my.kwargs.get("view")
        element_name = my.kwargs.get("element_name")

        config_view = WidgetConfigView.get_by_search_type(search_type, view)


        #inner_div = RoundedCornerDivWdg(hex_color_code="949494",corner_size="10")
        inner_div = RoundedCornerDivWdg(hex_color_code="272727",corner_size="10")
        inner_div.set_dimensions( width_str='400px', content_height_str='600px' )
        top.add(inner_div)


        # add the save button
        buttons_list = []
        buttons_list.append( {'label': 'Save as View', 'tip': 'Save as View',
                'bvr': { 'cbjs_action': "alert('Not Implemented')" }
        })
        buttons_list.append( {'label': 'Save as Def', 'tip': 'Save as Definition',
                'bvr': { 'cbjs_action': "alert('Not Implemented')" }
        })

        buttons = TextBtnSetWdg( float="right", buttons=buttons_list,
                                 spacing=6, size='small', side_padding=4 )


        inner_div.add(buttons)


        title_div = DivWdg()
        title_div.add_style("margin-bottom: 10px")
        title_div.add_class("maq_search_bar")
        title_div.add("Element Definition")
        inner_div.add(title_div)



        test = SimpleElementDefinitionWdg(config_view=config_view, element_name=element_name)
        inner_div.add(test)



        config_title_wdg = DivWdg()
        inner_div.add(config_title_wdg)
        config_title_wdg.add("<b>Definitions in config</b>")
        config_title_wdg.add_style("margin: 15px 0px 5px 0px")

        for config in config_view.get_configs():
            view = config.get_view()
            xml = config.get_element_xml(element_name)

            config_div = DivWdg()
            inner_div.add(config_div)



            # add the title
            from pyasm.widget import SwapDisplayWdg, IconWdg

            view_div = DivWdg()
            view_div.add_class("spt_view")
            config_div.add(view_div)

            if not xml:
                icon_wdg = IconWdg( "Nothing defined", IconWdg.DOT_RED )
                icon_wdg.add_style("float: right")
                view_div.add(icon_wdg)
            else:
                icon_wdg = IconWdg( "Is defined", IconWdg.DOT_GREEN )
                icon_wdg.add_style("float: right")
                view_div.add(icon_wdg)

            swap = SwapDisplayWdg()
            view_div.add(swap)
            swap.add_action_script('''
                var info_wdg = bvr.src_el.getParent('.spt_view').getElement('.spt_info');
                spt.toggle_show_hide(info_wdg);
            ''')


            mode = "predefined"
            file_path = config.get_file_path()
            if not file_path:
                mode = "database"
            elif file_path == 'generated':
                mode = 'generated'
                

            # display the title
            view_div.add("%s" % view)
            view_div.add(" - [%s]" % mode)

            info_div = DivWdg()
            info_div.add_class("spt_info")
            info_div.add_style("margin-left: 20px")
            info_div.add_style("display: none")
            #if not xml:
            #    info_div.add_style("display: none")
            #else:
            #    swap.set_off()
            view_div.add(info_div)

            path_div = DivWdg()
            if not file_path:
                file_path = mode
            path_div.add("Defined in: %s" % file_path)
            info_div.add(path_div)

            text_wdg = TextAreaWdg()
            text_wdg.set_option("rows", 15)
            text_wdg.set_option("cols", 80)
            text_wdg.set_value(xml)
            info_div.add(text_wdg)

            #view_div.add("<hr/>")

        return top



    def get_definitions(my, element_name):
        '''get all the definitions for this element'''
        search_type = my.kwargs.get("search_type")
        view = my.kwargs.get("view")
        config_view = WidgetConfigView.get_by_search_type(search_type, view)

        display_class = config_view.get_display_handler(element_name)
        element_attr = config_view.get_element_attributes(element_name)

        for config in config_view.get_configs():
            #print config
            view = config.get_view()
            file_path = config.get_file_path()
            if not file_path:
                file_path = "from Database"
            #print view, file_path

            xml = config.get_element_xml(element_name)
            #print xml
            #print "-"*20





class SimpleElementDefinitionWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'search type for this search widget',
        'view': 'the top level view we are looking at',
        'element_name': 'the element name to look at',
        'config_view': 'config_view'
        }



    def get_display(my):
        top = DivWdg()

        element_name = my.kwargs.get('element_name')

        config_view = my.kwargs.get("config_view")
        display_class = config_view.get_display_handler(element_name)
        display_options = config_view.get_display_options(element_name)
        element_attr = config_view.get_element_attributes(element_name)

        name = element_attr.get('name')
        edit = element_attr.get('edit')
        title = element_attr.get('title')
        width = element_attr.get('width')


        # add the name
        from pyasm.web import Table
        table = Table()
        top.add(table)

        table.add_row()
        td = table.add_cell("Name: ")
        td.add_style("padding: 5px")
        name_text = SpanWdg(name)
        name_text.add_style('font-weight: bold')
        name_text.add_attr("size", "50")
        table.add_cell(name_text)


        table.add_row_cell("<br/>Element Attributes:<br/>")

        # add the title
        table.add_row()
        td = table.add_cell("Title: ")
        td.add_style("padding: 5px")
        title_text = TextWdg("title")
        title_text.add_attr("size", "50")
        if title:
            title_text.set_value(title)
        table.add_cell(title_text)



        # add the width
        table.add_row()
        td = table.add_cell("Width: ")
        td.add_style("padding: 5px")
        width_text = TextWdg("width")
        if width:
            width_text.set_value(width)
        width_text.add_attr("size", "50")
        table.add_cell(width_text)

        # add the editable
        table.add_row()
        td = table.add_cell("Editable: ")
        td.add_style("padding: 5px")
        editable_text = CheckboxWdg("editable")
        editable_text.add_attr("size", "50")
        table.add_cell(editable_text)




        table.add_row_cell("<br/>Display:<br/>")

        # add the widget
        table.add_row()
        td = table.add_cell("Widget: ")
        td.add_style("padding: 5px")
        widget_select = SelectWdg("widget")
        options = ['Expression']
        widget_select.set_option("values", options)
        widget_select.add_empty_option("-- Select --")
        #widget_select.set_value(display_class)
        table.add_cell(widget_select)

        table.add_row_cell("&nbsp;&nbsp;&nbsp;&nbsp;- or -")

        # add the class
        table.add_row()
        td = table.add_cell("Class Name: ")
        td.add_style("padding: 5px")
        class_text = TextWdg("class_name")
        class_text.set_value(display_class)
        class_text.add_attr("size", "50")
        table.add_cell(class_text)


        # introspect the widget
        if not display_class:
            display_class = "pyasm.widget.SimpleTableElementWdg"
        #display_class = "tactic.ui.panel.ViewPanelWdg"

        from pyasm.common import Common
        import_stmt = Common.get_import_from_class_path(display_class)
        if import_stmt:
            exec(import_stmt)
        else:
            exec("from pyasm.widget import %s" % display_class)
        try:
            options = eval("%s.get_args_options()" % display_class)
        except AttributeError:
            try:
                info = eval("%s.get_args_keys()" % display_class)
            except AttributeError:
                return top
                
            options = []
            for key, description in info.items():
                option = {
                    'name': key,
                    'type': 'TextWdg',
                    'description': description
                }
                options.append(option)


        '''
        options = [
        {
            'name': 'expression',
            'type': 'TextWdg',
            'size': '50'
        },
        ]
        '''

        if options:
            top.add("<br/>Widget Options:<br/>")

        table = Table()
        top.add(table)

        for option in options:
            table.add_row()

            name = option.get('name') 
            title = name
            type = option.get('type')

            td = table.add_cell( "%s: " % title )
            td.add_style("padding: 5px")

            value = display_options.get(name)

            if type == 'SelectWdg':
                edit_wdg = SelectWdg("%s|value" % name)
                edit_wdg.add_style("width: 250px")
                edit_wdg.add_empty_option('-- Select --')
                values = option.get('values')
                edit_wdg.set_option('values', values)
                if value:
                    edit_wdg.set_value(value)
            elif type == 'TextAreaWdg':
                edit_wdg = TextAreaWdg("%s|value" % name)
                if value:
                    edit_wdg.set_value(value)
                edit_wdg.add_attr("cols", "60")
                edit_wdg.add_attr("rows", "3")
            else:
                edit_wdg = TextWdg("%s|value" % name)
                if value:
                    edit_wdg.set_value(value)
                edit_wdg.add_style("width: 250px")

            table.add_cell(edit_wdg)

        return top







if __name__ == '__main__':
    from pyasm.security import Batch
    Batch(project_code='MMS')
    xx = ElementDefinitionWdg(search_type='MMS/job',view='job_dashboard')
    xx.get_definitions("supervisor")



