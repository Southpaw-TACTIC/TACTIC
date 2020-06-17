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

__all__ = ['ElementDefinitionWdg', 'ViewElementDefinitionWdg', 'EditElementDefinitionWdg', 'SimpleElementDefinitionCbk']

import os

import tacticenv

from pyasm.common import Date, Environment, Xml, TacticException, SetupException, Common, jsonloads, jsondumps
from pyasm.command import Command
from pyasm.biz import Project
from pyasm.search import Search, SearchType, WidgetDbConfig
from pyasm.web import DivWdg, SpanWdg, Table, WebContainer, HtmlElement, Widget
from pyasm.widget import SelectWdg, HiddenWdg, WidgetConfigView, WidgetConfig, TextAreaWdg, TextWdg, ProdIconButtonWdg, CheckboxWdg, IconWdg, SwapDisplayWdg
from tactic.ui.common import BaseRefreshWdg, WidgetClassHandler, TableElementClassHandler
from tactic.ui.filter import FilterData
from tactic.ui.container import TabWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.widget import CalendarInputWdg, TextBtnSetWdg, SearchTypeSelectWdg, ActionButtonWdg

from dateutil import parser

import types
import functools
import operator

import six
basestring = six.string_types


if Common.IS_Pv3:
    def cmp(a, b):
        return (a > b) - (a < b)




class ElementDefinitionWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
        'search_type': 'search type for this search widget',
        'view': 'the top level view we are looking at',
        'element_name': 'the element name to look at',
        'is_insert':    'true|false',

        'display_handler': 'The display handler class'
        }

   

    def get_display(self):
        top = DivWdg()
        top.add_class("spt_element_top")
        top.add_color("color", "color")
        top.add_color("background", "background")

       

        is_insert = self.kwargs.get("is_insert")
        if is_insert in ['true', True]:
            self.is_insert = 'true'
        else:
            self.is_insert = 'false'

        simple_view_only = self.kwargs.get("simple_view_only")
        if simple_view_only in ['true', True]:
            self.simple_view_only = 'true'
        else:
            self.simple_view_only = 'false'


        search_type = self.kwargs.get("search_type")
        self.search_type = search_type
        view = self.kwargs.get("view")
        element_name = self.kwargs.get("element_name")


        # add hidden elements for the search_type and view

        hidden = HiddenWdg("search_type", search_type)
        top.add(hidden)
        hidden = HiddenWdg("view", view)
        top.add(hidden)




        config_view = WidgetConfigView.get_by_search_type(search_type, view)
        edit_config_view = WidgetConfigView.get_by_search_type(search_type, "edit")

        # This variable may be obsolete now
        # find out this so we don't draw Display if it is a edit layout
        view_attributes = config_view.get_view_attributes()
        self.is_edit_layout = 'false'
        if view in ['edit','edit_definition', 'insert'] or view_attributes.get('layout') == 'EditWdg':
            self.is_edit_layout = 'true'

       

        inner_div = DivWdg()
        inner_div.add_style("padding: 5px")
        inner_div.add_style("width: 580px")
        inner_div.add_style("min-height: 600px")
        top.add(inner_div)

        #view = config_view.get_view()
        if self.is_edit_layout == 'true':
            config_xml = '''
             <config>
              <tab>
              <element name='Edit Mode' load='true'>
                 <display class='tactic.ui.manager.EditElementDefinitionWdg'>
                <search_type>%(search_type)s</search_type>
                <view>%(view)s</view>
                <element_name>%(element_name)s</element_name>
                <is_insert>%(is_insert)s</is_insert>
                <is_edit_layout>true</is_edit_layout>
            </display>
          </element>
        </tab>
        </config>'''%{'search_type': search_type, 'view': view, 'element_name': element_name, 'is_insert': self.is_insert}
        else:
            show_title_details = self.kwargs.get("show_title_details")
            if show_title_details in [False, 'false']:
                show_title_details = 'false'
            else:
                show_title_details = 'true'


            config_xml = '''
            <config>
            <tab>
              <element name='View Mode' load='true'>
                <display class='tactic.ui.manager.ViewElementDefinitionWdg'>
                    <search_type>%(search_type)s</search_type>
                    <view>%(view)s</view>
                    <element_name>%(element_name)s</element_name>
                    <is_insert>%(is_insert)s</is_insert>
                    <simple_view_only>%(simple_view_only)s</simple_view_only>
                    <is_edit_layout>false</is_edit_layout>
                    <show_title_details>%(show_title_details)s</show_title_details>
                </display>
              </element>
              <element name='Edit Mode' load='true'>
                <display class='tactic.ui.manager.EditElementDefinitionWdg'>
                    <search_type>%(search_type)s</search_type>
                    <view>%(view)s</view>
                    <element_name>%(element_name)s</element_name>
                    <is_insert>%(is_insert)s</is_insert>
                    <is_edit_layout>true</is_edit_layout>
                </display>
              </element>
            </tab>
            </config>
            ''' % {'search_type': search_type, 'view': view, 'element_name': element_name, 'is_insert': self.is_insert, 'simple_view_only': self.simple_view_only, 'show_title_details': show_title_details}
       
        config = WidgetConfig.get(view='tab', xml=config_xml)

        if self.simple_view_only == 'true':
            column_config_view = self.kwargs.get("column_config_view")

            table_display = config.get_display_widget('View Mode', extra_options={"column_config_view": column_config_view })

            inner_div.add(table_display)
            submit_input = self.get_submit_input()
            inner_div.add(submit_input)

        elif self.is_insert =='true':
            from tactic.ui.container import WizardWdg
            wizard = WizardWdg(title="none")
            table_display = config.get_display_widget('View Mode')
            wizard.add(table_display, "View Mode")

            edit_display = config.get_display_widget('Edit Mode')
            wizard.add(edit_display, "Edit Mode")

            submit_input = self.get_submit_input()
            wizard.add_submit_button(submit_input)

            inner_div.add(wizard)

        else:
            tab = TabWdg(config_xml=config_xml, show_add=False, tab_offset=5, show_remove=False , allow_drag=False)
            inner_div.add(tab) 
            tab.add_style("margin: 0 -6 0 -6")


        return top

    def get_submit_input(self):

        if self.simple_view_only == 'true':
            view = self.kwargs.get("view")
        else:
            view = "definition"

        if self.is_insert == 'true':
            title = "Create >>"
            tip = "Create New Column"
        else:
            title = "Save >>"
            tip = "Save Column"

        submit_input = ActionButtonWdg(title=title, tip=tip)

        behavior = {
            'type': 'click_up',
            'is_insert': self.is_insert,
            'search_type': self.search_type,
            'view': view,
            'cbjs_action': self._get_save_cbjs_action()
        }
        submit_input.add_behavior(behavior)
        submit_input.add_style("float: right")

        return submit_input


    def get_definitions(self, element_name):
        '''get all the definitions for this element'''
        search_type = self.kwargs.get("search_type")
        view = self.kwargs.get("view")
        config_view = WidgetConfigView.get_by_search_type(search_type, view)

        display_class = config_view.get_display_handler(element_name)
        element_attr = config_view.get_element_attributes(element_name)

        for config in config_view.get_configs():
            view = config.get_view()
            file_path = config.get_file_path()
            if not file_path:
                file_path = "from Database"

            xml = config.get_element_xml(element_name)

    def _get_save_cbjs_action(self):
        ''' this takes input from both table and edit display and save a new column'''
        return  '''
            var server = TacticServerStub.get();
            var top = bvr.src_el.getParent(".spt_element_top");
            //var mode = top.getElement(".spt_element_def_mode");
            var inputs = spt.api.Utility.get_input_values(top, null, false);

            if (inputs.name == '') {
                alert('Please provide a name for this element');
                return;
            }
           
            spt.app_busy.show("Creating New Column", "");
            
            var widget_key = inputs['xxx_option|widget_key'];
            var is_continue = true;
            var is_insert = bvr.is_insert;
            var is_edit_layout = '%s';

            var search_type = bvr.search_type;
            var view = bvr.view;
            if (!view) {
                view = 'definition';
            }

            if (widget_key && !widget_key[0]  && is_insert==true) {
                if (!confirm('You are about to create a Widget Column without a database column. Continue?')){
                    is_continue = false;
                    spt.app_busy.hide();
                    return;
                }
            }
            if (is_continue){
                var class_name = 'tactic.ui.manager.SimpleElementDefinitionCbk';
                var args = {
                    search_type: search_type,
                    view: view,
                    is_insert: is_insert,
                    is_edit_layout: is_edit_layout
                };
                try {
                     server.execute_cmd(class_name, args, inputs);
                }
                catch(e) {
                     spt.alert(spt.exception.handler(e));
                     spt.app_busy.hide();
                     return;
                }
            }
            spt.app_busy.hide();
            var pop = bvr.src_el.getParent('.spt_popup');
            // pop could be null in Manage Views page
            var activator = (pop && pop.activator) ? pop.activator: bvr.src_el;
            try {
                var table_top = spt.get_parent(activator, '.spt_table_top')
                // may not have table_top in Manage Views
                if (table_top) {
                    // FIXME: the fast table has the layout inside the spt_table_top
                    var layout = table_top.getElement(".spt_layout");
                    if (!layout)
                        layout = table_top.getParent(".spt_layout");
                    var elem_name = inputs.name[0];
                    if (is_insert) {

                        if (layout.getAttribute("spt_version") == "2") {
                            spt.table.set_layout(layout);
                            spt.table.add_column(elem_name);
                        }
                        else {
                            var table = table_top.getElement(".spt_table");
                            spt.dg_table.toggle_column_cbk(table, elem_name,'-1');
                        }

                    }
                    else {
                        spt.dg_table.search_cbk( {}, {'src_el': table_top} );
                    }
                }
                if (pop)
                    var popup_id = pop.id;
                    var options = {
                        new_element : inputs.name
                    };
                    spt.named_events.fire_event('preclose_' + popup_id, {options: options});
                    spt.popup.close(pop);

            }
            catch (e) {
                // it happens when the user refreshes the table while changing
                // definition
                throw(e)
                spt.alert('Definition modified. Please refresh this table manually');
            }
            '''%(self.is_edit_layout)

    





class ViewElementDefinitionWdg(BaseRefreshWdg):

    def init(self):
        self.main_xml_text = None
        self.main_xml = None


    def get_args_keys(self):
        return {
        'search_type': 'search type for this search widget',
        'view': 'the top level view we are looking at',
        'element_name': 'the element name to look at',
        'config_view': 'config_view',
        'edit_config_view': 'edit_config_view',
        'is_edit_layout': 'True if it is edit layout',
        'is_insert': 'True if it is insert'
        }


    def _get_save_cbjs_action(self):
        return  '''
            var server = TacticServerStub.get();
            var top = bvr.src_el.getParent(".spt_element_definition");
            var mode = top.getElement(".spt_element_def_mode");
            var inputs = spt.api.Utility.get_input_values(top, null, false);

            var tab_top = bvr.src_el.getParent(".spt_element_top");
            spt.tab.set_tab_top(tab_top);
            var header = spt.tab.get_selected_header();
            var tab_name = header.getAttribute('spt_element_name');

            if (inputs.name == '') {
                alert('Please provide a name for this element');
                return;
            }

            spt.app_busy.show("Saving " + tab_name + " Element Definition", "");
            
            var widget_key = inputs['xxx_option|widget_key'];
            var is_continue = true;
            var is_insert = %s;
            var is_edit_layout = '%s';
            if (widget_key && !widget_key[0] && mode.value=='form' && is_insert==true) {
                if (!confirm('You are about to create a Widget Column without a database column. Continue?')){
                    is_continue = false;
                    spt.app_busy.hide();
                    return;
                }
            }
            if (is_continue){
                var class_name = 'tactic.ui.manager.SimpleElementDefinitionCbk';
                var args = {
                    search_type: '%s',
                    view: 'definition',
                    is_insert: is_insert,
                    is_edit_layout: is_edit_layout
                };
                try {
                     server.execute_cmd(class_name, args, inputs);
                }
                catch(e) {
                     spt.alert(spt.exception.handler(e));
                     spt.app_busy.hide();
                     return;
                }
            }
            spt.app_busy.hide();
            var pop = bvr.src_el.getParent('.spt_popup');
            var activator = (pop && pop.activator) ? pop.activator: bvr.src_el;
            try {
                // may not have table_top in Manage Views
                var table_top = spt.get_parent(activator, '.spt_table_top')
                // the fast table has the layout inside the spt_table_top
                if (table_top) {
                    var layout = table_top.getElement(".spt_layout");
                    if (!layout)
                        table_top.getParent(".spt_layout");
                    if (is_insert) {
                        var elem_name = inputs.name[0];
                        if (layout.getAttribute("spt_version") == "2") {
                            spt.table.set_layout(table_top);
                            spt.table.add_column(elem_name);
                        }
                        else {
                            var table = table_top.getElement(".spt_table");
                            spt.dg_table.toggle_column_cbk(table, elem_name,'-1');
                        }
                    }
                    else {
                        spt.dg_table.search_cbk( {}, {'src_el': table_top} );
                    }
                }
                if (pop)
                    spt.popup.close(pop);
                
            }
            catch (e) {
                alert(e);
                // it happens when the user refreshes the table while changing
                // definition
                spt.alert('Definition modified. Please refresh this table manually');
            }
            '''%(str(self.is_insert).lower(), self.is_edit_layout, self.search_type)

    def get_display(self):
        top = DivWdg()
        top.add_class("spt_element_definition")
        #top.add_style("width: 530px")

        self.is_edit_layout = self.kwargs.get("is_edit_layout")
        self.is_insert = self.kwargs.get("is_insert")
        
        if self.is_insert in ['true', True]:
            self.is_insert = True
        else:
            self.is_insert = False

        self.simple_view_only = self.kwargs.get("simple_view_only") in ['true', True]
        element_name = self.kwargs.get('element_name')
        search_type = self.kwargs.get('search_type')
        self.search_type = search_type
        view = self.kwargs.get('view')

        config_view = WidgetConfigView.get_by_search_type(search_type, view)
        configs = WidgetConfigView.get_by_type("column")
        config_view.get_configs().extend(configs)


        edit_config_view = WidgetConfigView.get_by_search_type(search_type, "edit")

        if self.is_insert in ['false', False]:

            display_class = config_view.get_display_handler(element_name)
            widget_key = config_view.get_widget_key(element_name,'display')
            display_options = config_view.get_display_options(element_name)
            element_attr = config_view.get_element_attributes(element_name)

            # test build the class
            try:
                widget = config_view.get_display_widget(element_name)
            except Exception as e:
                print("ERROR: ", e)
                widget = None
            is_editable = False
            if hasattr(widget, 'is_editable'):
                is_editable = widget.is_editable()

            
            if is_editable:
                #edit_config_view = self.kwargs.get("edit_config_view")
                edit_class = edit_config_view.get_edit_handler(element_name)
                edit_widget_key = edit_config_view.get_widget_key(element_name)
                edit_options = edit_config_view.get_options(element_name, "edit")
                action_class = edit_config_view.get_action_handler(element_name)
                
            else:
                edit_class = ''
                edit_widget_key = ''
                edit_options = {}
                action_class = ''
            
            # build the xml string
            configs = config_view.get_configs()
            for x in configs:
                xml_str = x.get_element_xml(element_name)
                xml_str = xml_str.strip()
                if xml_str and xml_str != "<element name='%s'/>" % element_name:
                    break
            if not xml_str:
                xml_str = "<element name='%s'/>" % element_name


            edit = element_attr.get('edit')
            show_color  = element_attr.get('color')
            title = element_attr.get('title')
            width = element_attr.get('width')
            access = element_attr.get('access')
            if is_editable:
                if is_editable=='optional':
                    # it needs to be explicit in this case to turn on the editability for Edit Panel mainly
                    editable = element_attr.get('edit') == 'true'
                else:
                    editable = element_attr.get('edit') != 'false'
            else:
               

                editable = False


        else:
            widget_key = ''
            edit_widget_key = ''
            display_class = ''
            display_options = {}

            edit_class = ''
            edit_options = {}
            action_class = ''

            element_name = ''
            edit = ''
            title = ''
            width = ''
            xml_str = ''
            editable = True




        # add in the mode selected
        mode_wdg = DivWdg()
        mode_wdg.add("<div style='float: left; display: inline-block; margin-right: 10px'>Mode: </div>")
        mode_select = SelectWdg("mode")
        mode_select.add_style("width: 120px")
        mode_select.add_class('spt_element_def_mode')
        mode_select.set_option("labels", "Form|XML")
        mode_select.set_option("values", "form|xml")
        # we want to start in Form all the time
        #mode_select.set_persistence()
        mode_select.add_behavior({
            'type': 'change',
            'cbjs_action': '''
            var value = bvr.src_el.value;
            var top = bvr.src_el.getParent(".spt_element_definition");
            var form_el = top.getElement(".spt_form_top");
            var xml_el = top.getElement(".spt_xml_top");

            if (value == 'form') {
               spt.show(form_el);
               spt.hide(xml_el);
            }
            else {
               spt.show(xml_el);
               spt.hide(form_el);
            }

            '''
        })
        mode_wdg.add(mode_select)
        mode_wdg.add_style("margin: 0px -2px 0px 0px")
        mode_wdg.add_style("width: 160px")
        mode_wdg.add_style("white-space: nowrap")
        mode_wdg.add_style("display: flex")
        mode_wdg.add_style("align-items: center")
        mode = mode_select.get_value()


        # add the save button
        from tactic.ui.widget import ActionButtonWdg
        save_button = ActionButtonWdg( title='Save', tip='Save To Definition' )
        save_button.add_style("margin: 3px 3px 5px 3px")
        save_button.add_style("float: right")
        save_button.add_behavior( {
        'type': 'click_up',
        'is_insert': self.is_insert,
        'search_type': self.search_type,
        'cbjs_action': self._get_save_cbjs_action()
        } )


        title_div = DivWdg()
        top.add(title_div)
        title_div.add_style("display: flex")
        title_div.add_style("justify-content: space-between")
        title_div.add_color("background", "background", -3 )
        title_div.add_style("margin: 0 -1 10 -1")
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 4px")
        #title_div.add_style("width: 520px")
        title_div.add_style("height: 30px")
        title_div.add_border()
        if self.is_insert:
            title_div.add("Add New Column")
        else:
            title_div.add("Edit Column Definition")

        if (not self.is_insert) and (not self.simple_view_only):

            title_div.add(mode_wdg)

            shelf_wdg = DivWdg()
            top.add(shelf_wdg)
            shelf_wdg.add_style("display: flex")
            shelf_wdg.add_style("align-items: center")
            shelf_wdg.add_style("justify-content: flex-end")
            gear = self.get_gear_menu(view)
                
            # add gear menu 
            shelf_wdg.add(save_button)
            shelf_wdg.add(gear)




        #top.add("<br clear='all'/>")



        # add in the pure xml wdg
        xml_wdg = self.get_xml_wdg(xml_str)
        if mode != 'xml':
            xml_wdg.add_style("display: none")

        config_wdg = self.get_definition_configs(config_view, element_name)
        xml_wdg.add('<br/>')
        xml_wdg.add(config_wdg)

        xml_wdg.add_class("spt_xml_top")
        top.add(xml_wdg)

        # add the name
        from pyasm.web import Table
        table = Table()
        table.add_color("color", "color")
        table.add_class("spt_form_top")
        #table.add_style("width: 530px")
        table.add_style("width: 100%")
        if mode == 'xml':
            table.add_style("display: none")
        top.add(table)
    
        tr, td = table.add_row_cell()

        attr_wdg = DivWdg()
        attr_wdg.add_color("background", "background", -3)
        attr_wdg.add_style("margin: 10px -2px 10px -2px")
        attr_wdg.add_style("padding: 10px")
        attr_wdg.add_border()
        #title_wdg = DivWdg()
        #title_wdg.add("Element Attributes")
        #title_wdg.add_style("margin-top: -25px")
        #attr_wdg.add(title_wdg)
        td.add(attr_wdg)


        attr_table = Table()
        attr_table.add_color("color", "color")


        # add the title
        attr_table.add_row()
        td = attr_table.add_cell("Title: ")
        td.add_style("padding: 5px")
        title_text = TextWdg("attr|title")
        title_text.add_class("form-control")
        title_text.add_class("spt_element_definition_title")
        title_text.add_style("margin-bottom: 8px")
        title_text.add_attr("size", "50")
        title_text.add_style("height: 25px")
        if title:
            title_text.set_value(title)
        attr_table.add_cell(title_text)
        attr_wdg.add(attr_table)

        title_text.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_element_definition");
        var el = top.getElement(".spt_element_definition_name");
        if (el && el.getStyle("display") != "none") {
            var value = bvr.src_el.value;
            var name = spt.convert_to_alpha_numeric(value);
            el.value = name;
        }
        '''
        } )


        show_title_details = self.kwargs.get("show_title_details") or True
        if show_title_details in ['false', False]:
            show_title_details = False
        else:
            show_title_details = True



        # add in the name widget
        tr = attr_table.add_row()
        if not show_title_details:
            tr.add_style("display: none")

        td = attr_table.add_cell("Name: ")
        td.add_style("padding: 5px")
        td = attr_table.add_cell()
        name = self.kwargs.get("element_name")
        if self.is_insert:
            name_text = TextWdg("name")
            name_text.add_style("margin-bottom: 8px")
            name_text.add_class("form-control")
            name_text.add_class("spt_element_definition_name")
            name_text.add_style("height: 25px")
            name_text.add_attr("size", "50")

            td.add(name_text)

        else:
            #hidden = HiddenWdg("name", element_name)
            hidden = TextWdg("name")
            td.add(hidden)
            hidden.set_value(element_name)
            hidden.add_style("display", "none")
            hidden.add_class("spt_element_definition_name")
            if name:
                hidden.set_value(name)

            td.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var el = bvr.src_el.getElement(".spt_element_definition_name");
                spt.toggle_show_hide(el);
                var el2 = bvr.src_el.getElement(".spt_element_definition_span");
                spt.toggle_show_hide(el2);
                '''
            } )


            name_text = SpanWdg(element_name)
            name_text.add_class("spt_element_definition_span")
            td.add(name_text)
            name_text.add_style('font-weight: bold')


 
        # add the default security
        """
        attr_table.add_row()
        td = attr_table.add_cell("Default Access: ")
        td.add_style("padding: 5px")
        access_select = SelectWdg("attr|default_access")
        access_select.set_option("values", "allow|deny")
        if access:
            access_select.set_value(access)
        attr_table.add_cell(access_select)
        """


 
        # add the width
        tr = attr_table.add_row()

        if not show_title_details:
            tr.add_style("display: none")

        td = attr_table.add_cell("Width: ")
        td.add_style("padding: 5px")
        width_text = TextWdg("attr|width")
        width_text.add_class("form-control")
        width_text.add_style("height: 25px")
        width_text.add_style("width: 75px")
        width_text.add_style("margin-bottom: 8px")
        if width:
            width_text.set_value(width)
        width_text.add_attr("size", "3")
        attr_table.add_cell(width_text)

 
        if not self.is_insert and not self.simple_view_only:

            tr, td = attr_table.add_row_cell()
            span = DivWdg("Enable Colors: ")
            span.add_style('margin-left: 5px')
            span.add_style('margin-top: 4px')
            td.add(span)
            color_wdg = CheckboxWdg("attr|color")
            span.add(color_wdg)
            color_wdg.add_attr("size", "50")
            show_color = show_color != 'false'
            if show_color:
                color_wdg.set_checked()


            # this is required if one is changing the View mode definition post creation
            # while making its editability info intact
            # add a hidden View Mode Enable edit here when not in insert mode
            editable_wdg = CheckboxWdg("attr|editable")
            editable_wdg.add_style('display: none')
            if editable:
                editable_wdg.set_checked()
                # set a original state to remember it is checked initially
                editable_wdg.set_attr('orig', 'true')

            td.add(editable_wdg)


        tr, td = table.add_row_cell()
        td.add_style("padding-top: 20px")

       
        is_edit_layout = self.kwargs.get('is_edit_layout') == 'true'

        if not is_edit_layout:
            tr, td = table.add_row_cell()
            td.add(HtmlElement.br())
            attr_wdg = DivWdg()
            attr_wdg.add_color("background", "background", -3)
            attr_wdg.add_style("margin-top: 5px")
            attr_wdg.add_style("padding: 10px")
            attr_wdg.add_border()
            attr_wdg.add_style("margin: 10px -2px 10px -2px")
            title_wdg = DivWdg()
            title_wdg.add("Display Options")
            title_wdg.add_style("margin-top: -25px")
            title_wdg.add_style("font-size: 1.2em")
            attr_wdg.add(title_wdg)
            td.add(attr_wdg)


            if not display_class:
                display_class = self.kwargs.get('display_handler')


            column_config_view = self.kwargs.get("column_config_view")

            if column_config_view:
                class_labels = None
                class_values = None

                default_class=''

            else:

                # add the widget information
                class_labels = ['Empty', 'Raw Data', 'Default', 'Formatted Value', 'Expression', 'Expression Value', 'Button', 'Link', 'Gantt', 'Hidden Row', 'Drop Item', 'Completion', 'Custom Layout', 'Python', '-- Class Path --']
                class_values = ['', 'raw_data', 'default', 'format', 'expression', 'expression_value', 'button', 'link', 'gantt', 'hidden_row', 'drop_item', 'completion', 'custom_layout', 'python', '__class__']


                default_class='format'

            widget_class_wdg = WidgetClassSelectorWdg(widget_key=widget_key, display_class=display_class, display_options=display_options,class_labels=class_labels,class_values=class_values, prefix='option', default_class=default_class, show_action=False, element_name=element_name, column_config_view=column_config_view)
            attr_wdg.add(widget_class_wdg)




        tr, td = table.add_row_cell()
        td.add(HtmlElement.br())

   
        if not self.is_insert and not self.simple_view_only:
            tr, td = table.add_row_cell()

            title_wdg = DivWdg()
            swap = SwapDisplayWdg.get_triangle_wdg()
            title_wdg.add(swap)
            title_wdg.add("Colors")
            td.add(title_wdg)

            color_wdg = DivWdg()
            SwapDisplayWdg.create_swap_title(title_wdg, swap, color_wdg, is_open=False)
            color_wdg.add_class("spt_element_colors")
            color_wdg.add_style("display: none")
            color_wdg.add_color("background", "background", -3)
            color_wdg.add_style("margin-left: 5px")
            color_wdg.add_style("margin-bottom: 10px")
            color_wdg.add_style("padding: 10px")
            color_wdg.add_border()
            td.add(color_wdg)

            # add the color widget information
            color_wdg.add( self.get_color_wdg() )

            # add definition configs
            tr, td = table.add_row_cell()

            config_wdg = self.get_definition_configs(config_view, element_name)
            td.add(config_wdg)
        
        top.add_style("margin-bottom: 10px")

        # set the main xml value if one with display handler is found
        if self.main_xml:
            self.main_xml_text.set_value(self.main_xml)
        return top



    def get_gear_menu(self, view):

        # FIXME: the gear menu widget should be here
        from tactic.ui.container import GearMenuWdg, Menu, MenuItem
        menu = Menu(width=200)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)



        menu_item = MenuItem(type='action', label='Save to Definition')
        behavior = {'cbjs_action': '''
            spt.app_busy.show("Saving Element Definition");
            var server = TacticServerStub.get();
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_element_definition");
            var inputs = spt.api.Utility.get_input_values(top, null, false);
            var class_name = 'tactic.ui.manager.SimpleElementDefinitionCbk';
            var is_insert = %s;
            var is_edit_layout = '%s';
            var args = {
                search_type: '%s',
                view: 'definition',
                is_insert : is_insert,
                is_edit_layout: is_edit_layout
            };
            try {
                server.execute_cmd(class_name, args, inputs);
            }
            catch(e) {
                alert(spt.exception.handler(e));
            }

            spt.app_busy.hide();
        ''' %(str(self.is_insert).lower(), self.is_edit_layout, self.search_type)}

        menu_item.add_behavior(behavior)
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Save to Current View')
        behavior = {'cbjs_action': '''
            if (confirm("Are you sure you wish to save to current view? This will override the default definition") ) {
            spt.app_busy.show("Saving to current view [%s]");
            var server = TacticServerStub.get();
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_element_definition");
            var inputs = spt.api.Utility.get_input_values(top, null, false);
            var class_name = 'tactic.ui.manager.SimpleElementDefinitionCbk';
            var is_insert = %s;
            var is_edit_layout = '%s';
            var args = {
                search_type: '%s',
                view: '%s',
                is_insert : is_insert,
                is_edit_layout: is_edit_layout
            };
            try {
                server.execute_cmd(class_name, args, inputs);
            }
            catch(e) {
                alert(spt.exception.handler(e));
            }
            spt.app_busy.hide();
            }
        '''%( view, str(self.is_insert).lower(), self.is_edit_layout, self.search_type, view)}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)




        menu_item = MenuItem(type='separator')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Show Server Transaction Log')
        behavior = {
            'cbjs_action': "spt.popup.get_widget(evt, bvr)",
            'options': {
                'class_name': 'tactic.ui.popups.TransactionPopupWdg',
                'title': 'Transaction Log',
                'popup_id': 'TransactionLog_popup'
            }
        }
        menu_item.add_behavior(behavior)
        menu.add(menu_item)

        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Undo Last Server Transaction')
        behavior = {'cbjs_action': "spt.undo_cbk(evt, bvr);"}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Redo Last Server Transaction')
        behavior = {'cbjs_action': "spt.redo_cbk(evt, bvr);"}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)


        gear_menu = GearMenuWdg()
        gear_menu.add(menu)

        return gear_menu

    def get_xml_wdg(self, xml_str):

        xml_wdg = DivWdg()
        #xml_wdg.add_style('width: 550px')
        xml_wdg.add_style("margin-top: 10px")
        xml_wdg.add_style("padding: 10px")
        xml_wdg.add_style("margin: 10px")
        xml_wdg.add_border()
        title_wdg = DivWdg()
        title_wdg.add("XML Definition")
        title_wdg.add_style("margin-top: -23px")
        xml_wdg.add(title_wdg)


        self.main_xml_text = TextAreaWdg("xml_def")
        self.main_xml_text.add_style('overflow: auto')
        self.main_xml_text.add_style("margin: 10px")
        self.main_xml_text.set_option("rows", "20")
        self.main_xml_text.set_option("cols", "75")

        if xml_str:
            self.main_xml_text.set_value(xml_str)

        xml_wdg.add(self.main_xml_text)
        return xml_wdg



    def get_color_wdg(self):
        search_type = self.kwargs.get('search_type')
        element_name = self.kwargs.get('element_name')

        # get the color maps
        color_config = WidgetConfigView.get_by_search_type(search_type, "color")
        color_xml = color_config.configs[0].xml

        color_maps = {}

        name = element_name
        xpath = "config/color/element[@name='%s']/colors" % name
        text_xpath = "config/color/element[@name='%s']/text_colors" % name
        bg_color_node = color_xml.get_node(xpath)
        bg_color_map = color_xml.get_node_values_of_children(bg_color_node)

        text_color_node = color_xml.get_node(text_xpath)
        text_color_map = color_xml.get_node_values_of_children(text_color_node)
 


        top = DivWdg()
        top.add_class("spt_color_top")


        existing_values = []
        # get existing values
        from pyasm.search import SqlException, SObjectValueException
        try:
            search = Search(search_type)
            if search.column_exists(element_name):

                column_info = search.get_column_info().get(element_name)
                data_type = column_info.get("data_type")

                if data_type in ["text", "varchar"]:
                    search.add_column(element_name, distinct=True)
                    #search.add_group_aggregate_filter([element_name])
                    if search.column_exists("project_code"):
                        search.add_project_filter()
                    search.set_limit(100)
                    sobjects = search.get_sobjects()

                    for x in sobjects:
                        value = x.get_value(element_name)
                        if isinstance(value, basestring):
                            value = value[:50]
                        existing_values.append(value)

                existing_values.sort()
        except (SObjectValueException, SqlException) as e:
            top.add("This widget cannot set colors")
            return top

        values = list(bg_color_map.keys())
        values.sort()

        from tactic.ui.input import ColorInputWdg
        from tactic.ui.container import DynamicListWdg


        if not values:
            create = DivWdg()
            top.add(create)
            create.add("No colors have been defined. Click to add first color.")
            create.add_style("padding: 10px")
            create.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_color_top");
            var list = top.getElement(".spt_color_list");
            spt.hide(bvr.src_el);
            spt.show(list);
            '''
            } )


        list_top = DivWdg()
        top.add(list_top)
        if not values:
            list_top.add_style("display: none")
        list_top.add_class("spt_color_list")

        list_wdg = DynamicListWdg()
        list_wdg.add(list)

        # create a template
        template = DivWdg()
        list_wdg.add_template(template)

        color_input = ColorInputWdg(name="bg_color")
        template.add(color_input)

        template.add_style("width: 350px")
        text = TextWdg("bg_color")

        text.add_style("width: 55px")
        text.add_style("float: left")
        text.add_style("padding-right: 10px")
        color_input.set_input(text)

        select_div = DivWdg()
        select_div.add_styles("float: left; width: 100px")
        select = SelectWdg("color|column")
        select.add_style("width: 150px")
        select.set_option("values", existing_values)
        select_div.add(select)
        
        template.add("&nbsp;"*2)
        template.add(select_div)
        template.add_style("padding: 3px")

        # NOTE:
        # add a first row.  Unfortunately we can't just add the template
        # row.  This is because select row breaks if it is drawn twice.
        if not values:
            first_row = DivWdg()
            list_wdg.add_item(first_row)

            color_input = ColorInputWdg("bg_color")
            first_row.add(color_input)

            first_row.add_style("width: 300px")
            text = TextWdg("bg_color")
            #text.set_value("-click-")

            text.add_style("width: 55px")
            text.add_style("float: left")
            color_input.set_input(text)

            select_div = DivWdg()
            select_div.add_styles("float: left; width: 100px")

            select = SelectWdg("color|column")
            select.add_style("width: 150px")
            select.set_option("values", existing_values)
            select_div.add(select)
            
            first_row.add("&nbsp;"*2)
            first_row.add(select_div)
            first_row.add_style("padding: 3px")


        for value in values:
            value_div = DivWdg()
            #top.add(value_div)
            list_wdg.add_item(value_div)
            value_div.add_style("width: 300px")

            # add a color chooser
            bg_color = bg_color_map.get(value)
            name = "bg_color"
            if bg_color:
                bg_color = bg_color.strip()
                color_input = ColorInputWdg(name, start_color=bg_color)
            else:
                color_input = ColorInputWdg(name)
            value_div.add(color_input)

            text = TextWdg(name)
            text.add_style("width: 55px")
            text.add_style("float: left")
            color_input.set_input(text)


            # set the current color
            if bg_color:
                text.add_style("background: %s" % bg_color)
                text.set_value(bg_color)

            value_div.add_style("padding: 3px")

            value_div.add("&nbsp;"*2)
            value_div.add(value)

            hidden = HiddenWdg("color|column")
            value_div.add(hidden)
            hidden.set_value(value)

        return top


    def get_definition_configs(self, config_view, element_name):
        config_wdg = DivWdg()
        

        title_wdg = DivWdg()
        config_wdg.add(title_wdg)
        from pyasm.widget import SwapDisplayWdg
        swap = SwapDisplayWdg.get_triangle_wdg()
        title_wdg.add(swap)
        title_wdg.add("Definitions in Config (Advanced)")

        content_div = DivWdg()
        SwapDisplayWdg.create_swap_title(title_wdg, swap, content_div, is_open=False)
        config_wdg.add(content_div)
        content_div.add_class("spt_element_definitions")
        content_div.add_style("display: none")
        content_div.add_color("background", "background", -3)
        content_div.add_style("margin-left: 5px")
        content_div.add_style("margin-bottom: 10px")
        content_div.add_style("padding: 10px")
        content_div.add_border()
    
        self.main_xml = None

        for config in config_view.get_configs():
            view = config.get_view()
            xml = config.get_element_xml(element_name)

            # find out which one to display up in the top text area
            if not self.main_xml:
                display_handler = config.get_display_handler(element_name)
                action_handler = config.get_action_handler(element_name)
                if display_handler or action_handler:
                    self.main_xml = xml

            config_div = DivWdg()
            content_div.add(config_div)


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

            text_wdg = TextAreaWdg("xml")
            text_wdg.add_style("font-size: 11px")
            text_wdg.add_style('overflow: auto')
            text_wdg.set_option("rows", 20)
            text_wdg.set_option("cols", 70)
            text_wdg.set_value(xml)
            info_div.add(text_wdg)

        return config_wdg

class EditElementDefinitionWdg(ViewElementDefinitionWdg):

    def init(self):
        self.main_xml_text = None
        self.main_xml = None
    
    def get_args_keys(self):
        return {
        'search_type': 'search type for this search widget',
        'view': 'the top level view we are looking at',
        'element_name': 'the element name to look at',
        'config_view': 'config_view',
        'edit_config_view': 'edit_config_view',
        'is_edit_layout': 'True if it is edit layout',
        'is_insert': 'True if it is insert'
        }


    def get_insert_view(self):
        '''the insert view is less complicated with less options'''
        widget_key = ''
        edit_widget_key = ''
        display_class = ''
        display_options = {}

        edit_class = ''
        edit_options = {}
        action_class = ''
        action_options = {}

        element_name = ''
        edit = ''
        title = ''
        width = ''
        xml_str = ''
        editable = True

        # see if this widget_class is editable
       
        is_editable = True

        widget = Widget()

       
        title_div = DivWdg()
        #widget.add(title_div)
        title_div.add_color("background", "background", -3 )
        title_div.add_style("margin-bottom: 10px")
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 4px")
        #title_div.add_style("width: 520px")
        title_div.add_style("height: 18px")
        title_div.add_border()
        title_div.add(IconWdg("New Element", IconWdg.NEW))
        title_div.add("New Column")

       

        from pyasm.web import Table
        attr_table = Table()
        attr_table.add_color("color", "color")


        # add the editable
        #attr_table.add_row()
        tr, td = attr_table.add_row_cell()
        td.add_style("padding: 5px")

        widget.add(attr_table)
        
        # for insert view
        td.add("Enable Edit: ")
        editable_wdg = CheckboxWdg("attr|editable")
        editable_wdg.add_attr("size", "50")
        # hide the table if chcecked off by user
        editable_wdg.add_behavior({'type': 'click_up',
            'propagate_evt': True,
            'cbjs_action': '''
            var table = spt.get_cousin(bvr.src_el,'.spt_element_definition', '.spt_edit_definition');
            if (bvr.src_el.checked)
                spt.show(table);
            else
                spt.hide(table);
            '''
            })

        if editable:
            editable_wdg.set_checked()
        elif is_editable == False:
            editable_wdg.set_option('disabled','disabled')
        td.add(editable_wdg)

        td.add("&nbsp;"*3)



        table = Table()
        table.add_color("color", "color")
        table.add_class("spt_edit_definition")
        table.add_style("width: 530px")
        if editable == False: 
            table.add_style("display: none")

        widget.add(table)

        tr, td = table.add_row_cell()
        td.add("<hr/>")
        td.add_style("padding-top: 20px")


        tr, td = table.add_row_cell()
        td.add(HtmlElement.br())

        title_wdg = DivWdg()
        swap = SwapDisplayWdg.get_triangle_wdg()
        title_wdg.add(swap)
        title_wdg.add("Edit Options")
        td.add(title_wdg)
     

        attr_wdg = DivWdg()
        
        SwapDisplayWdg.create_swap_title(title_wdg, swap, attr_wdg, is_open=self.is_edit_layout)
        attr_wdg.add_class("spt_element_edit")
        
        #attr_wdg.add_style("display: none")
        attr_wdg.add_color("background", "background", -3)
        #attr_wdg.add_style("margin-top: 5px")
        attr_wdg.add_style("margin-left: 5px")
        attr_wdg.add_style("padding: 10px")
        attr_wdg.add_border()
        td.add(attr_wdg)


        # add the widget information
        #class_labels = ['Default', 'Text', 'List', 'Color', '-- Class Path --']
        #class_values = ['', 'text', 'select', 'color', '__class__']
        class_labels = ['Default', 'Text', 'Select', 'Calendar' ,'Calendar Time', '-- Class Path --']
        class_values = ['', 'text', 'select', 'calendar','calendar_time', '__class__']
        prefix = 'edit'
        default_class=''
        
        widget_class_wdg = WidgetClassSelectorWdg(widget_key=edit_widget_key, display_class=edit_class, display_options=edit_options,class_labels=class_labels,class_values=class_values, prefix=prefix, default_class=default_class, action_class=action_class, action_options = action_options)
        attr_wdg.add(widget_class_wdg)

        widget.add(attr_wdg)

        return widget


    def get_display(self):
        top = DivWdg()
        top.add_class("spt_element_definition")
        #top.add_style("width: 530px")
        top.add_style("margin-bottom: 10px")

        self.is_insert = self.kwargs.get("is_insert")
        if self.is_insert in ['true', True]:
            self.is_insert = True
        else:
            self.is_insert = False


        self.is_edit_layout = self.kwargs.get('is_edit_layout')
        element_name = self.kwargs.get('element_name')
        search_type = self.kwargs.get('search_type')
        self.search_type = search_type

        view = self.kwargs.get('view')

        config_view = WidgetConfigView.get_by_search_type(search_type, view)
        edit_config_view = WidgetConfigView.get_by_search_type(search_type, "edit")

       

        if not self.is_insert:
            display_class = config_view.get_display_handler(element_name)
            widget_key = config_view.get_widget_key(element_name,'display')
            display_options = config_view.get_display_options(element_name)
            element_attr = config_view.get_element_attributes(element_name)
            # test build the class
            try:
                widget = config_view.get_display_widget(element_name)
            except Exception as e:
                print("ERROR: ", e)
                widget = None
            is_editable = False
            if hasattr(widget, 'is_editable'):
                is_editable = widget.is_editable()
            
            if is_editable:
                
                edit_class = edit_config_view.get_edit_handler(element_name)
                edit_widget_key = edit_config_view.get_widget_key(element_name)
                edit_options = edit_config_view.get_options(element_name, "edit")
                action_class = edit_config_view.get_action_handler(element_name)
                action_options = edit_config_view.get_options(element_name, "action")
                
            else:
                edit_class = ''
                edit_widget_key = ''
                edit_options = {}
                action_class = ''
                action_options = {}
            
            # build the xml string
            configs = config_view.get_configs()
            for x in configs:
                xml_str = x.get_element_xml(element_name)
                xml_str = xml_str.strip()
                if xml_str and xml_str != "<element name='%s'/>" % element_name:
                    break
            if not xml_str:
                xml_str = "<element name='%s'/>" % element_name


            edit = element_attr.get('edit')
            title = element_attr.get('title')
            width = element_attr.get('width')
            if is_editable:
                if is_editable=='optional':
                    # it needs to be explicit in this case to turn on the editability for Edit Panel mainly
                    editable = edit == 'true'
                else:
                    editable = edit != 'false'
            else:
               

                editable = False

        else:
         
            top.add( self.get_insert_view())
            return top




        # add in the mode selected
        mode_wdg = DivWdg()
        mode_wdg.add("Mode: ")
        mode_select = SelectWdg("mode")
        mode_wdg.add(mode_select)
        mode_select.add_style("width: 100px")
        mode_select.add_style("float: right")
        mode_select.add_style("margin-top: -5px")
        mode_select.add_style("margin-left: 5px")
        mode_wdg.add_style("float: right")
        
        mode_select.add_class('spt_element_def_mode')
        mode_select.set_option("labels", "Form|XML")
        mode_select.set_option("values", "form|xml")
        # we want to start in Form all the time
        #mode_select.set_persistence()
        mode_select.add_behavior({
            'type': 'change',
            'cbjs_action': '''
            var value = bvr.src_el.value;
            var top = bvr.src_el.getParent(".spt_element_definition");
            var form_el = top.getElement(".spt_form_top");
            var xml_el = top.getElement(".spt_xml_top");

            if (value == 'form') {
               spt.show(form_el);
               spt.hide(xml_el);
            }
            else {
               spt.show(xml_el);
               spt.hide(form_el);
            }

            '''
        })
        mode = mode_select.get_value()



        #top.add("<br clear='all'/>")


        # add the save button
        from tactic.ui.widget import ActionButtonWdg
        save_button = ActionButtonWdg( title='Save', tip='Save To Definition' )
        save_button.add_style("margin-left: 5px")
        save_button.add_style("margin-top: -5px")
        save_button.add_style("float: right")
        save_button.add_behavior( {
        'type': 'click_up',
        'is_insert': self.is_insert,
        'search_type': self.search_type,
        'cbjs_action': self._get_save_cbjs_action()
        } )
           

        title_div = DivWdg()
        top.add(title_div)
        title_div.add_color("background", "background", -3)
        title_div.add_style("margin-bottom: 10px")
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 8px")
        title_div.add_style("width: auto")
        title_div.add_style("height: 20px")
        title_div.add_border()
        if self.is_insert:
            title_div.add(IconWdg("New Element", IconWdg.NEW))
            title_div.add("New Column")
        else:
            title_div.add("Edit Column Definition")


        title_div.add(mode_wdg)

       
        # edit mode shouldn't use gear
        """
        gear = self.get_gear_menu()
        gear.add_style("float: right")
            
        # add gear menu 

        top.add(gear)

        """
        top.add(save_button)



        # add in the pure xml wdg
        xml_wdg = self.get_xml_wdg(xml_str)
        if mode != 'xml':
            xml_wdg.add_style("display: none")
        
        xml_wdg.add_class("spt_xml_top")
        top.add(xml_wdg)

        # add definition configs
        #tr, td = table.add_row_cell()

        config_wdg = self.get_definition_configs(edit_config_view, element_name)
        xml_wdg.add('<br/>')
        xml_wdg.add(config_wdg)



        # add the name
        from pyasm.web import Table
        table = Table()
        table.set_max_width()
        table.add_color("color", "color")
        table.add_class("spt_form_top")
        #table.add_style("width: 530px")
        if mode == 'xml':
            table.add_style("display: none")
        top.add(table)


        tr, td = table.add_row_cell()

        attr_wdg = DivWdg()
        attr_wdg.add_color("background", "background", -3)
        attr_wdg.add_style("margin-top: 10px")
        attr_wdg.add_style("padding: 10px")
        attr_wdg.add_border()
        #title_wdg = DivWdg()
        #title_wdg.add("Element Attributes")
        #title_wdg.add_style("margin-top: -25px")
        #attr_wdg.add(title_wdg)
        td.add(attr_wdg)


        attr_table = Table()
        attr_table.add_color("color", "color")

        attr_wdg.add(attr_table)

        # add the title
        attr_table.add_row()
      
       
        


        # add in the name widget
        attr_table.add_row()
        td = attr_table.add_cell("Name: ")
        td.add_style("padding: 5px")
        td = attr_table.add_cell()
        name = self.kwargs.get("element_name")
        if self.is_insert:
            name_text = TextWdg("name")
            name_text.add_class("spt_element_definition_name")
            name_text.add_attr("size", "50")

        else:
            name_text = DivWdg(element_name)
            name_text.add_style('font-weight: bold')
            name_text.add_style('display: inline-block')
            name_text.add_style('vertical-align: middle')
            hidden = HiddenWdg("name", element_name)
            td.add(hidden)
            if name:
                hidden.set_value(name)

        td.add(name_text)


     

        # add the editable
        #attr_table.add_row()
        tr, td = attr_table.add_row_cell()
        td.add_style("padding: 5px")

        td.add("Enable Edit: ")
        editable_wdg = CheckboxWdg("attr|editable")
        editable_wdg.add_attr("size", "50")
        if editable:
            editable_wdg.set_checked()
        elif is_editable == False:
            editable_wdg.set_option('disabled','disabled')


        editable_wdg.add_behavior({'type': 'click_up',
            'propagate_evt': True,
            'cbjs_action': '''
            var table = spt.get_cousin(bvr.src_el,'.spt_element_definition', '.spt_edit_definition');
            if (bvr.src_el.checked)
                spt.show(table);
            else
                spt.hide(table);
            '''
            })

        td.add(editable_wdg)

        td.add("&nbsp;"*3)


        # add a hidden Enable edit here when not in insert mode
        """
        color_wdg = CheckboxWdg("attr|color")
        color_wdg.add_style('display: none')
        if editable:
            color_wdg.set_checked()
        td.add(color_wdg)

        """
        #tr, td = table.add_row_cell()
        #td.add(SpanWdg("Widget Definition", css='small'))
        #td.add("<hr>")
        #td.add_style("padding-top: 20px")



        tr, td = table.add_row_cell()
        tr.add_class('spt_edit_definition')

        if editable == False: 
            tr.add_style("display: none")
        td.add(HtmlElement.br())

        title_wdg = DivWdg()
        swap = SwapDisplayWdg.get_triangle_wdg()
        title_wdg.add(swap)
        title_wdg.add("Edit")
        td.add(title_wdg)
     

        attr_wdg = DivWdg()
        
        SwapDisplayWdg.create_swap_title(title_wdg, swap, attr_wdg, is_open=self.is_edit_layout)
        attr_wdg.add_class("spt_element_edit")
        
        #attr_wdg.add_style("display: none")
        attr_wdg.add_color("background", "background", -3)
        #attr_wdg.add_style("margin-top: 5px")
        attr_wdg.add_style("margin-left: 5px")
        attr_wdg.add_style("padding: 10px")
        attr_wdg.add_border()
        td.add(attr_wdg)


        # add the widget information
        #class_labels = ['Default', 'Text', 'List', 'Color', '-- Class Path --']
        #class_values = ['', 'text', 'select', 'color', '__class__']
        class_labels = ['Default', 'Text', 'Select', 'Calendar' ,'Calendar Time', 'Time', '-- Class Path --']
        class_values = ['', 'text', 'select', 'calendar','calendar_time', 'time', '__class__']
        prefix = 'edit'
        default_class=''
        
        widget_class_wdg = WidgetClassSelectorWdg(widget_key=edit_widget_key, display_class=edit_class, display_options=edit_options,class_labels=class_labels,class_values=class_values, prefix=prefix, default_class=default_class, action_class=action_class, action_options = action_options)
        attr_wdg.add(widget_class_wdg)


        # add definition configs
        tr, td = table.add_row_cell()

        #td.add(HtmlElement.br())

        config_wdg = self.get_definition_configs(edit_config_view, element_name)
        td.add(config_wdg)
       
        # set the main xml value if one with display handler is found
        if self.main_xml:
            self.main_xml_text.set_value(self.main_xml)
        

        return top



    def get_xml_wdg(self, xml_str):

        xml_wdg = DivWdg()
        xml_wdg.add_style("width: 100%")
        xml_wdg.add_style("box-sizing: border-box")

        xml_wdg.add_style("margin-top: 50px")
        xml_wdg.add_style("padding: 10px")
        xml_wdg.add_border()
        title_wdg = DivWdg()
        title_wdg.add("XML Definition")
        title_wdg.add_style("margin-top: -23px")
        xml_wdg.add(title_wdg)


        self.main_xml_text = TextAreaWdg("xml_def")
        self.main_xml_text.add_style("box-sizing: border-box")
        self.main_xml_text.add_style('overflow: auto')
        self.main_xml_text.add_style("margin: 10px")
        self.main_xml_text.set_option("rows", "20")
        self.main_xml_text.add_style("width: 100%")

        if xml_str:
            self.main_xml_text.set_value(xml_str)

        xml_wdg.add(self.main_xml_text)

       
        

        return xml_wdg




__all__.append('WidgetClassSelectorWdg')
class WidgetClassSelectorWdg(BaseRefreshWdg):
    ''' Choice of Table Layout, Tile Layout, Custom Layout'''


    def get_display(self):
        widget_key = self.kwargs.get("widget_key")
        display_class = self.kwargs.get("display_class")
        view = self.kwargs.get("view")
        display_options = self.kwargs.get("display_options")
        action_class = self.kwargs.get("action_class")
        action_options = self.kwargs.get("action_options")
        show_action = self.kwargs.get('show_action')

        # pass in an optional element name.  some widgets make use of this
        # display extra options (ie: CustomLayoutElementWdg)
        element_name = self.kwargs.get("element_name")

        class_labels = self.kwargs.get("class_labels") or []
        class_values = self.kwargs.get("class_values") or []
        default_class = self.kwargs.get("default_class")
        prefix = self.kwargs.get("prefix")
        if not prefix:
            prefix = 'option'



        column_config_view = self.kwargs.get("column_config_view")
        if column_config_view:
            search = Search("config/widget_config")
            search.add_filter("view", column_config_view)
            search.add_filter("category", "ElementDefinitionWdg")
            column_config = search.get_sobject()

            if column_config:
                element_names = column_config.get_element_names()

                class_values = []
                for element_name in element_names:
                    handler = column_config.get_display_handler(element_name)
                    if not handler:
                        class_values.append(element_name)
                    else:
                        class_values.append(handler)


                class_labels = column_config.get_element_titles()


        if default_class and not widget_key and not display_class:
            widget_key = default_class
            

        # add the widget
        top = DivWdg()
        top.add_class("spt_widget_selector_top")
        self.set_as_panel(top)

        table = Table()

        table.add_color("color", "color")
        table.add_style("margin-top", "10px")
        table.add_style("width", "100%")
        top.add(table)

        tr = table.add_row()
        #tr.add_style("display: none")
        if len(class_values) == 1 and class_values[0] == '__class__':
            tr.add_style("display: none")

        td = table.add_cell()

        td.add("Widget Type: ")
        td.add_style("padding: 5px")
        td.add_style("padding-left: 14px")


        # put xxx_ in front to separate from other options
        widget_select = SelectWdg("xxx_%s|widget_key" % prefix)
        widget_select.add_class("spt_widget_key")
        widget_select.add_style("width: 230px")
        #if not default_class:
        #    widget_select.add_empty_option()

        widget_select.set_option("labels", class_labels)
        widget_select.set_option("values", class_values)
        load_event = False
        if widget_key:
            widget_select.set_value(widget_key)
        elif display_class in class_values:
            widget_select.set_value(display_class)
        elif display_class:
            widget_select.set_value('__class__')
        elif default_class:
            widget_select.set_value(default_class)
        else:
            #td.add("No display widget has been selected for this column<br/>")
            load_event = True

        #widget_select.add_empty_option("-- Select --")
        cbjs_action = '''
            var value = bvr.src_el.value;
            var top = bvr.src_el.getParent(".spt_widget_selector_top");
            var ui_top = bvr.src_el.getParent(".spt_element_top")
            if (!ui_top) {
                spt.alert('ui_top not found');
                return;
            }
            var wdg = top.getElement(".spt_widget_selector_class");
            var wdg_text = top.getElement(".spt_widget_display_class");
            wdg_text.value = '';

            //var view_el = top.getElement(".spt_widget_selector_view");
            //var view_text = top.getElement(".spt_widget_view");
            //view_text.value = '';


            if (value == '__class__') {
                spt.show(wdg);
            }
            else if (value == 'custom_layout') {
                spt.hide(wdg);
            }
 
            else if (value == '') {
                spt.hide(wdg);
            }
            else {
                spt.hide(wdg);
            }

            var values = spt.api.Utility.get_input_values(top, null, false);
            var wdg = top.getElement(".spt_widget_options_top");
            spt.show(wdg);
            spt.panel.refresh_element(wdg, values);

            // there could be 2
            var edits = ui_top.getElements('input[name=attr|editable]');
            // Manage Side Bar doesnt run the following
            // applicable only for the View Mode widget key select
            if (edits.length > 0 && bvr.prefix=='option') {
                for (var k=0; k< edits.length; k ++) {
                var edit = edits[k];
                    var edit_orig_state = edit.getAttribute('orig');
                    var form_top = spt.get_cousin(edit,'.spt_element_definition', '.spt_edit_definition');
                    // dynamically toggle edit widget ui based on chosen widget key
                    if (['hidden_row','gantt','button','custom_layout','expression'].contains(value))           
                    {
                        edit.checked = false;
                        if (value != 'expression')
                            edit.setAttribute('disabled', 'disabled');
                        else {
                            edit.removeAttribute('disabled');
                            if (edit_orig_state == 'true') 
                                edit.checked = true;
                            
                        }
                        spt.hide(form_top);
                    }
                    else {
                        edit.checked = true;
                        edit.removeAttribute('disabled');
                        spt.show(form_top);
                        
                    }
                }
            }

        '''
        if load_event:
            widget_select.add_behavior( {
                'type': 'load',
                'prefix': prefix,
                'cbjs_action': cbjs_action
            } )
        widget_select.add_behavior( {
            'type': 'change',
            'prefix': prefix,
            'cbjs_action': cbjs_action
        } )

        
        td = table.add_cell()
        td.add_class("spt_widget_top")
        td.add_style("padding: 5px 0px")

        if Project.get().is_admin():
            help_div = DivWdg()
            td.add(help_div)
            help_div.add_style("float: right")
            help_div.add_style("margin-top: -7px")

            help_wdg = ActionButtonWdg(title="?", tip="Show Help", size='small')
            help_div.add(help_wdg)

            handler = WidgetClassHandler()
            attrs = handler.get_all_elements_attributes("help")

            help_wdg.add_behavior( {
                'type': 'click_up',
                'attrs': attrs,
                'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_widget_top");
                    var key_el = top.getElement(".spt_widget_key");
                    var key = key_el.value;
                    spt.help.set_top();
                    var alias = bvr.attrs[key];
                    if (alias == null) {
                        spt.alert("No documentation for this widget defined");
                    }
                    else {
                        spt.help.load_alias(alias);
                    }
                '''
            } )

        td.add(widget_select)

        #table.add_row_cell("&nbsp;&nbsp;&nbsp;&nbsp;- or -")

        # add the class
        tr = table.add_row()
        if widget_key or (display_class in class_values) or (not display_class) or view:
            tr.add_style("display: none")
        tr.add_class("spt_widget_selector_class")
        td = table.add_cell()
        td.add("Class Name: ")
        td.add_style("padding: 5px")
        td.add_style("padding-left: 14px")

        class_text = TextInputWdg(name="xxx_%s|display_class" % prefix)
        table.add_cell(class_text)

        class_text.add_class("spt_widget_display_class")
        class_text.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_widget_selector_top");
            var values = spt.api.Utility.get_input_values(top, null, false);
            var wdg = top.getElement(".spt_widget_options_top");
            spt.panel.refresh(wdg, values);
            '''
        } )
        class_text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_widget_selector_top");
            var values = spt.api.Utility.get_input_values(top, null, false);
            var wdg = top.getElement(".spt_widget_options_top");
            spt.panel.refresh(wdg, values);
            '''
        } )
 
        if display_class:
            class_text.set_value(display_class)
        class_text.add_attr("size", "50")


        # add the view
        """
        tr = table.add_row()
        if widget_key or not view:
            tr.add_style("display: none")
        tr.add_class("spt_widget_selector_view")
        td = table.add_cell()
        td.add("View: ")
        td.add_style("padding: 5px")
        td.add_style("padding-left: 14px")

        view_text = TextInputWdg(name="xxx_%s|view" % prefix)
        table.add_cell(view_text)

        view_text.add_class("spt_widget_view")
        view_text.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_widget_selector_top");
            var values = spt.api.Utility.get_input_values(top, null, false);
            var wdg = top.getElement(".spt_widget_options_top");
            spt.panel.refresh(wdg, values);
            '''
        } )
        view_text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_widget_selector_top");
            var values = spt.api.Utility.get_input_values(top, null, false);
            var wdg = top.getElement(".spt_widget_options_top");
            spt.panel.refresh(wdg, values);
            '''
        } )
 
        if view:
            view_text.set_value(view)
        view_text.add_attr("size", "50")
        """












        # introspect the widget
        #if not display_class:
        #    display_class = "pyasm.widget.SimpleTableElementWdg"
        #display_class = "tactic.ui.panel.ViewPanelWdg"
        widget_options_wdg = WidgetClassOptionsWdg(widget_key=widget_key, display_class=display_class, display_options=display_options, prefix=prefix, element_name=element_name, column_config_view=column_config_view, mode="layout")
        table.add_row()
        td = table.add_cell()
        td.add(widget_options_wdg)

        if not display_class and not widget_key:
            widget_options_wdg.get_top_wdg().add_style("display: none")

        if show_action != False:
            tr = table.add_row()
            td = table.add_cell("Action: ")
            td.add_style("padding: 5px")
            td.add_style("padding-left: 14px")
        
            action_options_wdg = ActionClassOptionsWdg(action_class=action_class, action_options=action_options, prefix='action')
            if action_class:
                table.add_row()
                td = table.add_cell()
                action_options_wdg = action_options_wdg.get_buffer_display()
                td.add(action_options_wdg)
            else:   
                span = SpanWdg(HtmlElement.i('-- Default --'))
                span.add_style('padding-left: 5px')
                
                swap = SwapDisplayWdg.get_triangle_wdg()
                div = DivWdg(action_options_wdg.get_buffer_display())
                swap.create_swap_title(span, swap, div=div) 
                td.add(swap)
                td.add(span)
              
                td.add(div)
        '''
        action_text = TextWdg("xxx_%s|action_class" % prefix)
        action_text.add_attr('size','50')
        action_text.add_class("spt_widget_action_class")
        if action_class:
            action_text.set_value(action_class)
        else:
            # hide the row
            tr.add_style('display: none')
        class_text.add_attr("size", "50")
        table.add_cell(action_text)
        '''

        return top


class ActionClassOptionsWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
        'action_class': 'the display class to show all of the options',
        'action_options': 'the display options for this class',
        'prefix': 'the prefix to put before the input names'
        }

    def init(self):
        self.table = Table()


    def add_style(self, style):
        self.table.add_style(style)

    def get_display(self):

        prefix = self.kwargs.get('prefix')
        if not prefix:
            prefix = 'action'


        # introspect the widget
        web = WebContainer.get_web()
        action_class = ''
       
        is_default = False

        if not action_class:
            action_class = web.get_form_value("xxx_%s|action_class" % prefix)
        if not action_class:
            action_class = self.kwargs.get("action_class")

        if not action_class:
            action_class = "pyasm.command.DatabaseAction"
            is_default = True

        
        action_options = self.kwargs.get("action_options")
        
        #if is_default:
        #    return None
        
        if isinstance(action_options, basestring):
            try:
                action_options = eval(action_options)
            except:
                # !!!! Lost the options
                action_options = {}
        if not action_options:
            action_options = {}

        table = self.table
        table.add_class('spt_action')
        table.add_color("color", "color")
        table.add_style("margin-top", "10px")
        table.add_style("width", "100%")

        action_text = TextWdg("xxx_%s|action_class" % prefix)
        action_text.add_attr('size','50')
        action_text.add_class("spt_widget_action_class")
        if action_class and not is_default:
            action_text.set_value(action_class)
        tr = table.add_row()
        tr.add_class("spt_widget_selector_class")
        

        td = table.add_blank_cell()
        td = table.add_cell()
        td.add('> Class Name: ')

        table.add_cell(action_text)

        #td.add_style("padding: 5px")
        for key, value in action_options.items():
            action_option = TextWdg("%s|%s|value" %(prefix, key))
            action_option.set_value(value)
            tr = table.add_row()
            td = table.add_blank_cell()
            td.add_style("padding: 15px")
            table.add_cell('%s:'%key)
            table.add_cell(action_option)

        return table





class WidgetClassOptionsWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
        'widget_key': 'the widget key to map the display class to',
        'display_class': 'the display class to show all of the options',
        'display_options': 'the display options for this class',
        'prefix': 'the prefix to put before the input names',
        'args_keys': 'explicitly set an args_keys data structure',
        'mode': 'column|layout'
        }


    def init(self):
        top = DivWdg()
       
        top.add_class("spt_widget_options_top")
        self.set_as_panel(top)


    # sort
    def options_sort(a, b):
        if isinstance(a, basestring):
            return 1
        elif isinstance(b, basestring):
            return -1

        acategory = a.get('category')
        bcategory = b.get('category')
        if acategory == '':
            return -1
        if bcategory == '':
            return 1

        if acategory == 'kwargs':
            return -1
        if bcategory == 'kwargs':
            return 1


        if acategory == 'Required':
            acategory = '1.Required'
        if acategory == None:
            acategory = ''
        if bcategory == 'Required':
            bcategory = '1.Required'
        if bcategory == None:
            bcategory = ''

        aorder = a.get('order') or 99
        border = b.get('order') or 99

        int_cmp = True
        if isinstance(aorder, basestring):
            try:
                aorder = int(aorder)
            except:
                int_cmp = False
        if isinstance(border, basestring):
            try:
                border = int(border)
            except:
                int_cmp = False

        if int_cmp:
            avalue = "%s|%0.2d" % (acategory, aorder)
            bvalue = "%s|%0.2d" % (bcategory, border)
        else:
            avalue = "%s|%s" % (acategory, aorder)
            bvalue = "%s|%s" % (bcategory, border)

        if avalue == None:
            return 1
        if bvalue == None:
            return -1

        return cmp(avalue, bvalue)

    options_sort = staticmethod(options_sort)



    def get_display(self):

        top = self.top

        prefix = self.kwargs.get('prefix')
        if not prefix:
            prefix = 'option'



        web = WebContainer.get_web()

        # introspect the widget
        widget_key = self.kwargs.get("xxx_%s|widget_key" % prefix)
        if not widget_key:
            widget_key = web.get_form_value("xxx_%s|widget_key" % prefix)


        mode = self.kwargs.get("mode") or "column"

        display_class = ''

        if widget_key and widget_key not in ['__class__']:

            if widget_key.find(".") != -1:
                # This is really a class
                display_class = widget_key

            else:
                display_class = ""

                # get from a config xml
                #config_view = "custom_config"
                #config = WidgetConfig.get(view, xml=xml)

                column_config_view = self.kwargs.get("column_config_view")
                if column_config_view:
                    search = Search("config/widget_config")
                    search.add_filter("view", column_config_view)
                    search.add_filter("category", "ElementDefinitionWdg")
                    column_config = search.get_sobject()

                    if column_config:
                        display_class = column_config.get_display_handler(widget_key)

                if not display_class:
                    # or get from the central class handler
                    if mode == "layout":
                        handler = WidgetClassHandler()
                    else:
                        handler = TableElementClassHandler()

                    display_class = handler.get_display_handler(widget_key)


        if not display_class:
            display_class = web.get_form_value("xxx_%s|display_class" % prefix)
        if not display_class:
            display_class = self.kwargs.get("display_class")

        assert(mode == "layout")

        if not display_class:
            if mode == "layout":
                display_class = "tactic.ui.panel.CustomLayoutWdg"
            else:
                display_class = "pyasm.widget.SimpleTableElementWdg"



        display_options = self.kwargs.get("display_options") or {}

        import types
        if isinstance(display_options, list):
            try:
                display_options = eval(display_options)
            except:
                # !!!! Lost the options
                display_options = {}
        elif isinstance(display_options, basestring):
            display_options = display_options.replace("'", '"')
            display_options = jsonloads(display_options)

        if not display_options:
            display_options = {}


        class_options = self.kwargs.get("args_keys")
        category_options = self.kwargs.get("category_keys") or {}



        # if we have a view from a custom layout
        #view = None
        #view = "job.test.task_detail.sample_data"
        view = web.get_form_value("xxx_%s|view" % prefix)
        if widget_key != 'custom_layout' and view:
            search = Search("config/widget_config")
            search.add_filter("view", view)
            search.add_filter("category", "CustomLayoutWdg")
            config = search.get_sobject()
            if config:
                config_xml = config.get_xml()
                node = config_xml.get_node("config//kwargs")
                value = config_xml.get_node_value(node)
                if value:
                    class_options = jsonloads(value)
                else:
                    class_options = None
            else:
                top.add("Cannot find view [%s]" % view)
                return top
                


        if not class_options:
            class_options = {}
            import_stmt = Common.get_import_from_class_path(display_class)
            try:
                if import_stmt:
                    exec(import_stmt)
                else:
                    exec("from pyasm.widget import %s" % display_class)
            except ImportError:
                error = DivWdg()
                error.add_style('color: red')
                error.add("WARNING: could not import display class [%s]" % display_class)
                top.add(error)
            except Exception as e:
                error = DivWdg()
                error.add_style('color: red')
                error.add("WARNING: %s" % str(e) )
                top.add(error)

            else:            
                try:
                    class_options = eval("%s.get_args_keys()" % display_class)
                    # prevent the ARG_KEYS from getting modifed later on when appending kwargs
                    class_options = class_options.copy()

                except Exception as e:
                    error = DivWdg()
                    error.add_style('color: red')
                    error.add("WARNING: could not get options.  Failed on get_args_keys() for %s" %display_class)
                    top.add(error)
                    return top

                try:
                    category_options = eval("%s.get_category_keys()" % display_class)
                except Exception as e:
                    pass


        # special consideration is made for Custom Layouts where options
        # can be defined in the widget config
        if display_class in ['tactic.ui.table.CustomLayoutElementWdg']:
            # get the custom layout defintion
            element_name = display_options.get("view")
            if not element_name:
                element_name = self.kwargs.get("element_name")

            search = Search("config/widget_config")
            search.add_filter("view", element_name)
            config = search.get_sobject()
            if config:
                xml = config.get_xml_value("config")
                node = xml.get_node("config/%s/kwargs" % element_name)
                if node is not None:
                    xml_value =  xml.get_node_value(node)
                    data = {}
                    try:
                        xml_value = eval(xml_value)
                        data = jsondumps(xml_value)
                        data = jsonloads(data)
                    except Exception as e:
                        print("Error loading kwargs", xml_value)
                        print(e)
                        data = {}
                        value = {}
                        value['category'] = 'kwargs'
                        
                    for name, value in data.items():
                        
                        if (isinstance(value, basestring)):
                            value = {
                                'description': value
                            }
                        if not value.get("category"):
                            value['category'] = "kwargs"
                        class_options[name] = value


        if class_options:
            top.add("<br/>")
        #    title = DivWdg()
        #    title.add_style("margin: 10px 0 10px 0")
        #    title.add("Widget Options:")
        #    top.add(title)


        # convert to an array
        class_options_array = []
        for name, value in class_options.items():
            if isinstance(value, basestring):
                new_value = {
                    'name': name,
                    'description': value
                }
                class_options_array.append(new_value)

                if name in ['expression', 'cbjs_action']:
                    new_value['type'] = 'TextAreaWdg'
                elif name == 'icon':
                    new_value['type'] = 'IconSelectWdg'
                else:
                    new_value['type'] = 'TextWdg'
                    new_value['size'] = '50'

            else:
                # somehow getting tuples, unpack it for now
                if (isinstance(value, tuple)):
                    (value,) = value
                value['name'] = name
                if not value.get('description'):
                    value['description'] = 'No description'

                class_options_array.append(value)

        class_options_array.sort(key=functools.cmp_to_key(self.options_sort))

        current_div = DivWdg()
        top.add(current_div)


        has_recursive = False
        last_category = None
        is_open = True

        for option in class_options_array:

            category = option.get('category')
            option_name = option.get('name')
            default_value = option.get("default")



            if category is None:
                category = "Other Options"
                is_open = False


            if category != '' and category != last_category:

                current_div = DivWdg()
                top.add(current_div)

                if category in ['deprecated','internal','_internal','_deprecated']:
                    current_div.add_style("display: none")
                    # this is for FormatDefinitionEditWdg
                    if option_name == 'format':
                        continue

                last_category = category

                category_div = DivWdg()
                current_div.add(category_div)
                #category_div.add_color("background", "background3", -2)
                #category_div.add_style("margin-bottom", "5px")
                category_div.add_style("padding-top", "2px")
                #category_div.add("<hr/>")
                category_div.add_class("tactic_hover")

                script = '''
                var top = bvr.src_el.getParent(".spt_widget_section_top");
                var edits = top.getElements(".spt_widget_section_edit");

                for (var i = 0; i < edits.length; i++) {
                    spt.toggle_show_hide(edits[i]);
                }
                '''
                swap = SwapDisplayWdg.get_triangle_wdg()
                category_div.add(swap)
                category_div.add(category)
                SwapDisplayWdg.create_swap_title(category_div, swap, is_open=is_open, action_script=script)

                #category_div.add("<hr/>")
                category_div.add_style("padding-bottom: 5px")
                category_div.add_style("font-weight: bold")



            current_div.add_class("spt_widget_section_top")

            if category in ['deprecated','internal']:
                current_div.add_style("display: none")

            title = option_name
            title = Common.get_display_title(title)

            widget_type = option.get('type')
            if widget_type == 'recursive':
                has_recursive = True
                title_wdg = DivWdg()
                title_wdg.add( "")
                title_wdg.add_style("width: 10px")

            else:
                title_wdg = DivWdg()
                title_wdg.add("%s: " % title)
                title_wdg.add_style("width: 160px")
                title_wdg.add_style("margin-top: 5px")
                title_wdg.add_style("margin-bottom: 1px")
                description = option.get('description')
                description = description.replace('  ', '')
                description = description.replace('\n', ' ')
                description = "(%s) %s" % (option_name, description)
                title_wdg.set_attr('title', description )
                title_wdg.add_style('cursor: help')

                if category == '':
                    title_wdg.add_style("font-weight: bold")
                else:
                    title_wdg.add_style("padding-left: 0px")


            value = display_options.get(option_name)
            name = "%s|%s|value" % (prefix, option_name)

	   
            # TextWdg can't display " well
            if value and isinstance(value, basestring) and value.find('"') != -1:
                if widget_type in [None, 'TextWdg']:
                    widget_type = 'TextAreaWdg'

            if widget_type == 'recursive':
                edit_wdg = DivWdg()

                # add the widget information
                sub_widget_key = ''

                sub_display_class = display_options.get(option_name)
                if not sub_display_class:
                    sub_display_class = 'tactic.ui.panel.FastTableLayoutWdg'
                else:
                    # remove the recursive widget from the list
                    del(display_options[option_name])


                sub_display_options = display_options
                sub_class_labels = ['Table Layout', 'Fast Table Layout', 'Custom Layout', 'Tile Layout', '-- Class Path --']
                sub_class_values = ['table_layout', 'fast_table_layout', 'custom_layout', 'tile_layout', '__class__']
                sub_prefix = 'option'
                default_class = 'table_layout'

                widget_class_wdg = WidgetClassSelectorWdg(widget_key=sub_widget_key, display_class=sub_display_class, display_options=sub_display_options, class_labels=sub_class_labels,class_values=sub_class_values, prefix=sub_prefix, default_class=default_class)
                edit_wdg.add(widget_class_wdg)


            elif widget_type == 'CacheWdg' or option_name == 'use_cache':
                edit_wdg = DivWdg()
                edit_wdg.add_class("spt_cache")
                select = SelectWdg(name)
                edit_wdg.add(select)
                select.add_empty_option('-- Select --')
                values = option.get('values')
                select.set_option('values', values)
                if value:
                    select.set_value(value)


                select.add_behavior( {
                'type': 'change',
                #'search_type': self.search_type,
                #'element_name': element_name,
                'search_type': "prod/asset",
                'element_name': "file_usage",
                'cbjs_action': '''
                kwargs = {
                  'search_type': bvr.search_type,
                  'element_name': bvr.element_name,
                }
                //spt.panel.load_popup("Aggregate", "tactic.ui.app.aggregate_wdg.AggregateWdg", kwargs)

                var top = bvr.src_el.getParent(".spt_cache");
                var element = top.getElement(".spt_cache_interval");
                if (bvr.src_el.value == 'true') {
                    element.setStyle("display", "");
                }
                else {
                    if (confirm("Are you sure you wish to remove the caching?"))
                    {
                        element.setStyle("display", "none");
                        // FIXME: remove the column?
                    }
                }
                '''
                } )

                interval_wdg = DivWdg()
                interval_wdg.add_class("spt_cache_interval")
                if value != 'true':
                    interval_wdg.add_style("display: none")
                edit_wdg.add(interval_wdg)
                interval_wdg.add("-> Recalculate every: ")

                # TODO: get this info from the trigger
                interval = 120
                text = TextWdg("interval")
                text.add_style("width: 30px")
                text.set_value(interval)
                interval_wdg.add(text)

                unit_select = SelectWdg("unit")
                unit_select.set_value(interval)
                unit_select.set_option("values", "seconds|minutes|hours|days")
                interval_wdg.add(" ")
                interval_wdg.add(unit_select)

                type_select = SelectWdg("data_type")
                type_select.set_option("values", "string|text|integer|float|boolean|timestamp")
                interval_wdg.add('<br/>')
                interval_wdg.add("Data Type: ")
                interval_wdg.add(type_select)



            elif widget_type == 'SelectWdg':
                edit_wdg = SelectWdg(name)
                edit_wdg.add_style("width: 450px")
                edit_wdg.add_empty_option('-- Select --')
                values = option.get('values')
                edit_wdg.set_option('values', values)

                if default_value and not value:
                    value = default_value

                if value:
                    edit_wdg.set_value(value)
                    #edit_wdg.add_style("background: #a3d991")
                else:
                    edit_wdg.add_style("opacity: 0.5")

                labels = option.get('labels')
                if labels:
                    edit_wdg.set_option('labels', labels)

            elif widget_type == 'TextAreaWdg':
                edit_wdg = TextAreaWdg(name)
                if value:
                    edit_wdg.set_value(value)
                edit_wdg.add_style("width", "450px")
                edit_wdg.add_class("form-control")

            elif widget_type == 'CheckboxWdg':
                edit_wdg = CheckboxWdg(name)
                if value:
                    edit_wdg.set_checked()
                edit_wdg.set_option("value", "true")

            elif widget_type == 'IconSelectWdg':
                from tactic.ui.input import IconSelectWdg
                edit_wdg = IconSelectWdg(name)

                if default_value and not value:
                    value = default_value
                if value:
                    edit_wdg.set_value(value)

            elif widget_type == 'TextWdg':
                edit_wdg = DivWdg()
                select = TextInputWdg(name=name)
                edit_wdg.add(select)
                if default_value and not value:
                    value = default_value

                if value:
                    select.set_value(value)
                select.add_style("width: 450px")
                #select.add_style("float: right")
                #edit_wdg.add("<br clear='all'/>")

            elif widget_type == 'CalendarInputWdg':
                cal_wdg = CalendarInputWdg(name)

                cal_wdg.set_option('show_activator','true')
                if value:
                    cal_wdg.set_value(value)
                edit_wdg = DivWdg(cal_wdg)
                edit_wdg.add(HtmlElement.br(clear="all"))
            elif not widget_type:
                edit_wdg = None

            else:
                edit_wdg = None
                try:
                    kwargs = {
                        'prefix': prefix,
                        'name': name,
                        'option': option,
                        'display_options': display_options,
                    }
                    edit_wdg = Common.create_from_class_path(widget_type, [], kwargs)
                    edit_wdg.add_class("form-control")
                    edit_wdg.add_style("width: 450px")
                    if value and hasattr(edit_wdg,'set_value'):
                        edit_wdg.set_value(value)
                except Exception as e:
                    print("Cannot create widget: [%s]" % widget_type, e, e.message)

            if not edit_wdg:
                edit_wdg = TextWdg(name)
                edit_wdg.add_class("form-control")
                edit_wdg.add_style("width: 450px")
                if value:
                    edit_wdg.set_value(value)


           

            edit_div = DivWdg()
            edit_div.add_class("spt_widget_section_edit")
            if is_open == False:
                edit_div.add_style("display: none")
            edit_div.add_style("box-sizing: border-box")
            edit_div.add(title_wdg)
           
            edit_div.add_style("padding-bottom: 5px")
            edit_div.add_style("padding-left: 30px")

            #title_wdg.add_style("float: left")
            current_div.add_style("padding-left: 10px")
            current_div.add_style("padding-bottom: 10px")

            edit_div.add(edit_wdg)
            current_div.add(edit_div)



        # If the type is recursive, then all options are passed to the child
        # widget
        if has_recursive:
            return top


        # find any display_options that are not in the options list
        options_keys = class_options.keys()
        display_options_keys = display_options.keys()

        sub_keys = []
        for class_option in class_options.values():
            if isinstance(class_option, basestring):
                continue

            if (isinstance(class_option, tuple)):
                (class_option,) = class_option

            class_sub_keys = class_option.get("sub_keys")
            if class_sub_keys:
                sub_keys.extend( class_sub_keys )

        not_defined_keys = []
        for display_key in display_options_keys:
            if display_key in ['class_name', 'widget_key']:
                continue

            if display_key in options_keys:
                continue

            # check for any subkeys that need to be ignored
            if display_key in sub_keys:
                continue

            not_defined_keys.append(display_key)

        current_div = DivWdg()
        top.add(current_div)
        current_div.add_style("padding-left: 10px")
        current_div.add_style("padding-bottom: 10px")
        if not_defined_keys:
            category = "Extra Options<br/>"
            current_div.add(HtmlElement.br())
            current_div.add(HtmlElement.b(category))
            last_category = category



        for display_key in not_defined_keys:
            name = "%s|%s|value" % (prefix, display_key)

            table = Table()
            current_div.add(table)

            #tr.add_style("color: red")
            title = Common.get_display_title(display_key)

            td = table.add_cell('%s:' %title)
            value = display_options.get(display_key)
            td.add_style("vertical-align: top")
            td.add_style("padding: 5px 5px 5px 20px")
            td.add_style("width: 150px")

            #hidden = HiddenWdg(name, value)
            td = table.add_cell()
            hidden = TextInputWdg(name=name)
            #hidden.add_style("width: 250px")
            hidden.set_value(value)
            td.add(hidden)
            td.add_style("padding: 5px 5px 5px 110px")

            current_div.add(table)

        return top




class SimpleElementDefinitionCbk(Command):

    EDIT_VIEW = 'edit_definition'
    def get_title(self):
        return "Element definition update"


    def execute(self):
        web = WebContainer.get_web()
        self.is_insert = self.kwargs.get('is_insert')
        self.is_edit_layout = self.kwargs.get('is_edit_layout') == 'true'

        self.search_type = self.kwargs.get("search_type")

        # get the view
        user_view = web.get_form_value('view')
        view = self.kwargs.get('view')
        
        # one exception:
        if user_view=='edit_definition':
            view = 'edit_definition'
        

        # usually there is user_view chosen
        if not view:
            view = web.get_form_value("view")
            
        if not view:
            view = 'definition'

        self.element_name = web.get_form_value("name")
        self.element_name = self.element_name.strip()
        if not self.element_name:
            raise TacticException('Column name cannot be empty')
        try:
            self.element_name.encode('ascii')
        except UnicodeEncodeError:
            raise TacticException('Column name needs to be in English.. Non-English characters can be used in Title.')
        assert self.element_name



        mode = web.get_form_value("mode")
        if mode == 'xml':
            xml_str = web.get_form_value("xml_def")

            element_xml = Xml()
            element_xml.read_string(xml_str)
            self.element_name = element_xml.get_value("element/@name")
           
            if self.is_edit_layout:
                view = self.EDIT_VIEW
            self.save_to_view(self.search_type, view, self.element_name, element_xml)
            
        else:
            # put an xxx in front to separate it from the normal options
            widget_key = web.get_form_value("xxx_option|widget_key")
            edit_widget_key = web.get_form_value("xxx_edit|widget_key")
            display_class = web.get_form_value("xxx_option|display_class")
            edit_class = web.get_form_value("xxx_edit|display_class")
            action_class = web.get_form_value("xxx_action|action_class")

            if display_class == 'None':
                display_class = ''
            if edit_class == 'None':
                edit_class = ''

            # During insert, we save both view and edit.
            if self.is_insert:
                # only if it's not edit layout, we save the definition view

                if not self.is_edit_layout:
                    self.save(self.search_type, view, self.element_name, widget_key, display_class)

                # hard code for drop_item to include the DropElementAction
                if widget_key=='drop_item':
                    action_class = "tactic.ui.table.DropElementAction"
                    options = self.get_options("option")
                    web.set_form_value('action|instance_type', options.get('instance_type'))
                self.save(self.search_type, self.EDIT_VIEW, self.element_name, edit_widget_key, edit_class, action_class)
            else:
                if self.is_edit_layout:
                    self.save(self.search_type, self.EDIT_VIEW, self.element_name, edit_widget_key, edit_class, action_class, user_view=view)
                else:
                    self.save(self.search_type, view, self.element_name, widget_key, display_class)


        # save the color

        if not self.is_edit_layout:
            self.save_color()


    def save(self, search_type, view, element_name, widget_key, display_class, action_class=None, user_view=''):
        '''user_view is the view the user is looking at'''
        web = WebContainer.get_web()
        
        width = web.get_form_value("attr|width")
        title = web.get_form_value("attr|title")
        editable = web.get_form_value("attr|editable") == 'on'
        show_color = web.get_form_value("attr|color") == 'on'
        # get a specific element
        

        # build the xml element
        element_xml = Xml()
        element_xml.create_doc("element")
        root = element_xml.get_root_node()
        element_xml.set_attribute(root, "name", element_name)

        # add non-edit element properties
        if view != self.EDIT_VIEW:
            if title:
                element_xml.set_attribute(root, "title", title)
            else:
                element_xml.del_attribute(root, "width")
            if width:
                element_xml.set_attribute(root, "width", width)
            else:
                element_xml.del_attribute(root, "width")

            if not editable:
                element_xml.set_attribute(root, "edit", "false")
            else:
                element_xml.set_attribute(root, "edit", "true")

            # keep it clean and not set color if not false
            if not show_color:
                element_xml.set_attribute(root, "color", "false")
            
            #else:
            #    element_xml.set_attribute(root, "color", "true")


        # create the display_node
        # FIXME: only admin should be allowed to save here
        display_node = element_xml.create_element("display")
        if widget_key and widget_key != '__class__':

            # HACK: if there is a "." in the key, this this is really a class
            if widget_key.find(".") != -1:
                element_xml.set_attribute(display_node, "class", widget_key)
            else:
                element_xml.set_attribute(display_node, "widget", widget_key)
            element_xml.append_child(root, display_node)
        elif display_class:
            element_xml.set_attribute(display_node, "class", display_class)
            element_xml.append_child(root, display_node)

        if view == self.EDIT_VIEW:
            # access the view mode user_view(usually definition for now) to change its edit attribute
            # if it's just a built-in view, ignore it now
            # prevent saving non-editable column to edit view
            config = WidgetDbConfig.get_by_search_type(search_type, user_view)
            if not editable:
                # remove the element from edit view
                self.process_edit_view(search_type, element_name, remove=True)
                # TODO: redefine user_view
                if config:
                    view_mode_xml = config.get_xml()
                    node = config.get_element_node(element_name)
                    # in case the element in the defintion has been removed
                    if node is None:
                        node = config.create_element(element_name)

                    element_xml.set_attribute(node, "edit", "false")
                    config.set_value('config', view_mode_xml.to_string())
                    config.commit()

                return
            else:
                if config:
                    view_mode_xml = config.get_xml()
                    node = config.get_element_node(element_name)

                    # in case the element in the defintion has been removed
                    if node is None:
                        node = config.create_element(element_name)
                    element_xml.set_attribute(node, "edit", "true")
                    config.set_value('config', view_mode_xml.to_string())
                    config.commit()
            
                
            options = self.get_options("edit")
            self.process_edit_view(search_type, element_name)
        else:
            options = self.get_options("option")

        for name, value in options.items():
            option_node = element_xml.create_text_element(name, value)
            element_xml.append_child(display_node, option_node)

    
        if view == self.EDIT_VIEW:
        
            # create the optional action node
            action_node = element_xml.create_element("action")
            options = self.get_options("action") 
            if action_class:
                element_xml.set_attribute(action_node, "class", action_class)
                element_xml.append_child(root, action_node)

                for name, value in options.items():
                    option_node = element_xml.create_text_element(name, value)
                    element_xml.append_child(action_node, option_node)
       
        self.save_to_view(search_type, view, element_name, element_xml)


    def process_edit_view(self, search_type, element_name, remove=False):
        ''' this one is special as it has to look for one in edit view first
           and strip it down to a plain element as the new one will be saved in the edit_definition
           view level'''

        # find edit view
        config_search_type = "config/widget_config"
        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", 'edit')
        config_sobj = search.get_sobject()

        if config_sobj:
            if not remove:
                node_xml = '<element name="%s"/>' %element_name
                config_sobj.alter_xml_element(element_name, config_xml=node_xml)
            else:
                config_sobj.remove_node(element_name)
            config_sobj.commit_config()
        else:
            node_xml = '<element name="%s"/>' %element_name
            xml = Xml()
            xml.read_string(node_xml)
            self.save_to_view(search_type, "edit", element_name, xml)
        
    
    def save_to_view(self, search_type, view, element_name, element_xml):

        # save to view
        search_type_obj = SearchType.get(search_type)
        base_search_type = search_type_obj.get_base_key()
        project = Project.get_by_search_type(search_type)
        project_code = project.get_code()

        #config_search_type = "config/widget_config?project=%s" % project_code
        config_search_type = "config/widget_config"
        search = Search(config_search_type)
        search.add_filter("search_type", base_search_type)
        search.add_filter("view", view)
        config_sobj = search.get_sobject()
        if not config_sobj:
            # build a new config_sobj
            config_sobj = SearchType.create(config_search_type)
            config_sobj.set_value('search_type', base_search_type)
            config_sobj.set_value('view', view)

            # create a new xml document
            xml = Xml()
            xml.create_doc("config")
            root = xml.get_root_node()
            view_node = xml.create_element(view)
            #root.appendChild(view_node)
            element_xml.append_child(root, view_node)
    
        else:
            xml = config_sobj.get_xml_value("config")


        config = WidgetConfig.get(view, xml=xml)
        try:
            config.alter_xml_element(element_name, config_xml=element_xml.to_string())
        except SetupException as e:
            raise TacticException("Incorrectly formatted widget config found. %s"%e.__str__())


        xml = config.get_xml()
        
        widget = None
        # actually create the element
        try:
            widget = config.get_display_widget(element_name)
        except:
            print("Warning: Cannot create widget for [%s]" % element_name)
            #raise
            #return

       
        if widget and view != self.EDIT_VIEW:
            try:
                # TODO: should check if the coluns exist! or only on insert
                project_code = Project.get_project_code()
                full_st = Project.get_full_search_type(search_type, project_code=project_code)
                widget.create_required_columns(full_st)
            except (TacticException, AttributeError) as e: # for add column sql error
                if self.is_insert: # will be caught in AlterTableCmd
                    raise
                else: # in edit mode, it's ok for now
                    print("WARNING when creating required columns: ", e)
                    pass
                #raise
            except AttributeError:
                # this is meant for the definition display, not for edit_definition view
                print("Warning: [%s] does not have create_required_columns method"%element_name)
                raise
            except Exception as e:
                print("Warning: ", e.message)
                raise

        # commit the config_sobj at the end if no exception is raised during insert
        config_sobj.set_value("config", xml)
        config_sobj.commit()

      

    def get_options(self, prefix):
        web = WebContainer.get_web()

        # get all of the options
        keys = web.get_form_keys()
        options = {}


        # HACK: this relies on the fact that the first form value
        # is the hidden row ...
        display_class = web.get_form_value("xxx_%s|display_class" % prefix)
        widget_key = web.get_form_value("xxx_%s|widget_key" % prefix)
        if 'HiddenRowElementWdg' in display_class or 'HiddenRowToggleWdg' in display_class  or widget_key == 'hidden_row':
            hidden_class = web.get_form_values("xxx_%s|display_class" % prefix)[0]

            # have to convert back to class_name:
            
            if not hidden_class:
                # we call this one hidden_class for now instead of hidden_key since
                # we have to convert it back to class_name anyways
                hidden_class = web.get_form_values("xxx_%s|widget_key" % prefix)[1]

            if hidden_class in ['table_layout','custom_layout','tile_layout', 'fast_table_layout']:
                handler = WidgetClassHandler()
                hidden_class = handler.get_display_handler(hidden_class)
            options['dynamic_class'] = hidden_class


        for key in keys:
            if not key.startswith("%s|" % prefix):
                continue

            parts = key.split("|")
            name = parts[1]

            # skip the class defs
            if name in ['display_class', 'widget_key', 'class_name']:
                continue

            # FIXME: a little hacky ... this is to compensate for that fact
            # that FormatDefinition returns a lot of empty values.
            # only the one with a value is valid
            values = web.get_form_values(key)
            for value in values:
                if value != '':
                    options[name] = value
                    break

            # put in some extra codes for use_cache
            # DISABLE for 3.0
            if name == 'use_cacheXXX':
                interval = web.get_form_value("interval")
                if not interval:
                    interval = 0
                else:
                    interval = int(interval)
                unit = web.get_form_value("unit")
                if not unit:
                    unit = 0

                if unit == 'minutes':
                    interval = interval * 60
                elif unit == 'hours':
                    interval = interval * 60*60
                elif unit == 'days':
                    interval = interval * 60*60*24

                from tactic.ui.app.aggregate_wdg import AggregateRegisterCmd
                kwargs = {
                    'search_type': self.search_type,
                    'element_name': self.element_name,
                    'interval': interval
                }
                cmd = AggregateRegisterCmd(**kwargs)
                cmd.execute()

        return options


    def save_color(self):
        web = WebContainer.get_web()

        search = Search("config/widget_config")
        search.add_filter("search_type", self.search_type)
        search.add_filter("view", "color")
        config = search.get_sobject()
        if not config:
            config = SearchType.create("config/widget_config")
            config.set_value("search_type", self.search_type)
            config.set_value("view", "color")
            config.set_value("config", "<config><color/></config>")
            config.set_view("color")
            config._init()


        bg_colors = [];
        text_colors = []


        columns = web.get_form_values("color|column")
        bg_color_list = web.get_form_values("bg_color")
        text_color_list = web.get_form_values("text_color")
        for i, column in enumerate(columns):
            color = bg_color_list[i]
            # color is empty from the template row
            if column == '' or color == '':
                continue
            bg_colors.append( [column, color] )
            #text_colors.append( [column, text_color_list[i]] )

        '''
        keys = web.get_form_keys()
        for key in keys:
            value = web.get_form_value(key)
            if not value:
                continue

            value = value.strip()

            if key.startswith("bg_color|"):
                prefix, name = key.split("|")
                bg_colors.append( [name, value] )
            elif key.startswith("text_color|"):
                prefix, name = key.split("|")
                text_colors.append( [name, value] )
        '''
 
        element_xml = []
        element_xml.append( '''<element name='%s'>''' % self.element_name )



        # bg colors
        if bg_colors:
            element_xml.append( '''  <colors>''')
            for name, value in bg_colors:
                element_xml.append( '''    <value name="%s">%s</value>''' % (name,value) )
            element_xml.append( '''  </colors>''')

        # text colors
        if text_colors:
            element_xml.append( '''  <text_colors>''')
            for name, value in text_colors:
                element_xml.append( '''    <value name="%s">%s</value>''' % (name,value) )
            element_xml.append( '''  </text_colors>''')

        element_xml.append( '''</element>''' )

        element_xml = "\n".join(element_xml)


        config.append_xml_element(self.element_name, element_xml)
        config.commit_config()



