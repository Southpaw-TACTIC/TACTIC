
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
__all__ = ['SearchTypeToolWdg', 'SearchTypeCreatorWdg', 'SearchTypeCreatorCmd']

import re, os
from pyasm.common import Common, Environment
from pyasm.web import *
from pyasm.biz import Project, Schema
from pyasm.widget import *
#from pyasm.admin import *
from pyasm.command import *
from pyasm.search import SearchType, Search, WidgetDbConfig, CreateTable, DbContainer, TableUndo, SObjectFactory, SqlException
from pyasm.common import Xml, TacticException

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg, DynamicListWdg
from tactic.ui.widget import SearchTypeSelectWdg, ActionButtonWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.input import UploadButtonWdg 
from tactic.ui.panel import TableLayoutWdg, SearchTypeManagerWdg

class SearchTypeToolWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
        'database': 'the database',
        'schema': 'the schema'
        }

    def init(self):

        database = self.kwargs.get("database")
        schema = self.kwargs.get("schema")

        if not database:
            self.database = Project.get_project_code()
        else:
            self.database = database

        if not schema:
            self.schema = "public"
        else:
            self.schema = schema

        # FIXME: hack this in for now to handle "public"
        if self.schema == "public":
            self.namespace = self.database
        else:
            self.namespace = "%s/%s" % (self.database,self.schema)


    def get_display(self):

        div = HtmlElement.div()

        from tactic.ui.widget import TitleWdg
        subtitle = TitleWdg(name_of_title='sType Table Manager',help_alias='stype-register')
        div.add(subtitle)
        
        div.set_id('SearchTypeToolWdg')
        div.add_class('spt_stype_tool_top')
        div.set_attr('spt_class_name','tactic.ui.app.SearchTypeToolWdg')
        div.add_style("padding: 10px")
        div.add_style("max-width: 800px")

        div.add_color("background", "background")
        div.add_color("color", "color")

        error_div = PopupWdg(id='error')
        error_div.add("Error", 'title')
        error_div.add("&nbsp;", 'content')
        div.add(error_div)


        #div.add( self.create_div() )
        div.add(self.get_search_type_manager())
        #div.add( self.get_existing_wdg() )


        return div


    def get_search_type_manager(self):
        widget = Widget()
        div = DivWdg(id='SearchTypeManagerContainer')
        #select = SearchTypeSelectWdg(mode=SearchTypeSelectWdg.ALL_BUT_STHPW)
        #widget.add(select)


        wizard = SearchTypeCreatorWdg(namespace=self.namespace, database=self.database, schema=self.schema)
        popup = PopupWdg(id='create_search_type_wizard')
        popup.add_title('Register New sType')
        popup.add(wizard)
        div.add(popup)
        project = Project.get()
        project_schema_type = project.get_type()
        project_type = project.get_value('type')

        project_code = project.get_code()

        # add a search_type filter
        search_type_span = SpanWdg()
        search_type_span.add("sType: " )
        select = SelectWdg("search_type")
        search_type = self.kwargs.get("search_type")
        if search_type:
            select.set_value(search_type)
        select.set_option("query", "sthpw/search_object|search_type|search_type")
        select.set_option("query_filter", "\"namespace\" in ('%s', '%s', '%s')" % (project_code, project_type, project_schema_type))
        #select.set_persistence()
        select.add_empty_option("-- Select --")
        select.add_behavior({'type': "change", 
            'cbjs_action': '''var values = spt.api.Utility.get_input_values('SearchTypeManagerContainer');

                var top = bvr.src_el.getParent('.spt_stype_tool_top')
                var target;
                if (top)
                    target = top.getElement('.spt_view_manager_top');
                spt.panel.refresh(target, values)'''})
        search_type = select.get_value()
        search_type_span.add(select)
        
        #create_button = ProdIconButtonWdg('Create New')
        #create_button.add_behavior({'type':'click_up',
        #    'cbjs_action': "spt.popup.open('create_search_type_wizard')"})
        #search_type_span.add(create_button)

        div.add(search_type_span)
        div.add(HtmlElement.br(2))
        widget.add(div)


        # check that this table exists
        #project = Project.get()
        #if not project.has_table(search_type):
        #    div.add("No table for [%s] exists in this project" % search_type)
        #    return div


        manager = SearchTypeManagerWdg(search_type=search_type, show_definition=False)
        widget.add(manager)
        return widget

    def get_existing_wdg(self):

        div = DivWdg()
        title = DivWdg("Existing Custom sTypes")
        title.add_style("margin: 20px 0 10px 0")
        title.set_class("maq_search_bar")
        div.add(title)

        search_type = SearchType.SEARCH_TYPE

        search = Search( search_type )
        search.add_filter("namespace", self.namespace)
        sobjects = search.get_sobjects()

        table_wdg = TableLayoutWdg( search_type=search_type, view="table" )
        table_wdg.set_sobjects(sobjects)
        div.add(table_wdg)

        return div



class SearchTypeCreatorWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
        # DEPRECATED
        'database': 'the database???',
        'namespace': 'the namespace???',
        'schema': 'the schema???',


        'search_type':  'prefilled search type',
        'title':        ' prefilled title',
        'on_register_cbk': 'Callback for when register is clicked'
        }


    def get_display(self):

        self.database = self.kwargs.get("database")
        self.namespace = self.kwargs.get("namespace")
        self.schema = self.kwargs.get("schema")

        project_code = Project.get_project_code()
        if not self.database:
            self.database = project_code
        if not self.namespace:
            self.namespace = project_code
        if not self.schema:
            self.schema = "public"

        project = Project.get()
        project_type = project.get_value("type")
        if project_type and project_type != 'default':
            namespace = project_type
        else:
            namespace = project_code

        self.search_type = self.kwargs.get("search_type")
        if self.search_type and self.search_type.find("/") == -1:
            self.search_type = "%s/%s" % (namespace, self.search_type)


        top = DivWdg()
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("padding: 15px")
        top.add_class("spt_create_search_type_top")



        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias='stype-register|tactic-anatomy-lesson|project-workflow-introduction')
        top.add( help_button )
        help_button.add_style("float: right")

        
        from tactic.ui.container import WizardWdg
        #wizard = WizardWdg(title="Register a new sType", height="400px", width="550px")
        wizard = WizardWdg(title="none", height="400px", width="600px")
        top.add(wizard)


        create_div = HtmlElement.div()
        wizard.add(create_div, "Info")
        self.set_as_panel(create_div)

        #name_input = TextWdg("search_type_name")
        name_input = TextInputWdg(name="search_type_name")
        name_input.add_class("spt_name_input")
        # as long as we allow this to be displayed in Manage Search Types, it should be editable
        name_input.add_class("spt_input")
        name_input.add_class("SPT_DTS")
        if self.search_type:
            name_input.set_value(self.search_type)
            name_input.set_attr("readonly", "readonly")
            name_input.add_color("background", "background", -10)


        search = Search( SearchType.SEARCH_TYPE )
        search.add_filter("namespace", self.namespace)

        template_select = SelectWdg("copy_from_template")
        template_select.add_empty_option()
        template_select.set_search_for_options( \
                search, "search_type", "table_name")
        #template_select.set_option("labels", "---|People")

        title_text = TextInputWdg(name="asset_title")
        title_text.add_class("spt_input")
        title_value = self.kwargs.get("title")
        if not title_value and self.search_type:
            parts = self.search_type.split("/")
            if len(parts) > 1:
                title_value = parts[1]
                title_value = Common.get_display_title(title_value)
            else:
                project_code = Project.get_project_code()
                title_value = "%s/%s" % (project_code, parts[0])
            
        if title_value:
            title_text.set_value(title_value)


        title_text.add_behavior( {
            'type': 'blur',
            'project_type': project_type,
            'project_code': project_code,
            'cbjs_action': '''
            var value = bvr.src_el.value;
            if (!value) return;

            var top = bvr.src_el.getParent(".spt_create_search_type_top");
            var el = top.getElement(".spt_name_input");
            if (el.value) {
                return;
            }

            value = spt.convert_to_alpha_numeric( value );

            var checkbox = top.getElement(".spt_project_specific_checkbox");
            var checked = checkbox.checked;
            if (checked) {
                el.value = bvr.project_code + "/" + value;
            }
            else {
                el.value = bvr.project_type + "/" + value;
            }
            '''
        } )


        from tactic.ui.input import TextAreaInputWdg
        description = TextAreaInputWdg(name="asset_description")
        #description = TextAreaWdg("asset_description")
        #description.add_class("spt_input")



        table = Table()
        create_div.add(table)
        table.add_color("color", "color")
        table.add_col().set_attr('width','140')
        table.add_col().set_attr('width','250')


        table.add_row()
        tr, td = table.add_row_cell()
        td.add('''Registering a Searchable Type (sType) creates a corresponding table in the database.  This table is used to store the data for items of this SType.<br/><br/>''')



        # determines whether this search_type is local to this project
        #local_checkbox = CheckboxWdg("search_type_local")
        #local_checkbox.add_class("spt_input")
        #table.add_row()
        #table.add_header("Is Local to Project? ").set_attr('align','left')
        #table.add_cell(local_checkbox)

        tr = table.add_row()

        checkbox = CheckboxWdg("project_specific")
        th = table.add_header("Project Specific: ")
        checkbox.add_class("spt_project_specific_checkbox")
        th.add_style("min-width: 150px")
        th.set_attr('align','left')
        td = table.add_cell(checkbox)


        if project_type in ['default']:
            #tr.add_style("opacity: 0.6")
            tr.add_style("display: none")
            checkbox.set_option("disabled", "1")
            checkbox.set_checked()

        tr, td = table.add_row_cell()
        td.add("&nbsp;")

        checkbox.add_behavior( {
        'type': 'change',
        'project_type': project_type,
        'project_code': project_code,
        'cbjs_action': '''
        var checked = bvr.src_el.checked;
        var top = bvr.src_el.getParent(".spt_create_search_type_top");
        var el = top.getElement(".spt_name_input");

        var search_type = el.value;
        if (!search_type) return;

        var parts = search_type.split("/");

        if (checked) {
            el.value = bvr.project_code + "/" + parts[1];
        }
        else {
            el.value = bvr.project_type + "/" + parts[1];
        }
        '''
        } )


        table.add_row()
        th = table.add_header("Title: ")
        th.set_attr('align','left')
        th.add_style("vertical-align: top")
        td = table.add_cell(title_text)

        table.add_row_cell("&nbsp;")

        table.add_row()
        th = table.add_header("Searchable Type: ")
        th.add_style("min-width: 150px")
        th.add_style("vertical-align: top")
        th.set_attr('align','left')
        td = table.add_cell(name_input)

        table.add_row_cell("&nbsp;")

        table.add_row()
        table.add_header("Description: ").set_attr('align','left')
        table.add_cell(description)

        create_div.add( self.get_preview_wdg() )



        # Layout page 
        layout_wdg = self.get_layout_wdg()
        wizard.add(layout_wdg, "Layout")



        # Workflow page
        pipeline_div = DivWdg()
        wizard.add(pipeline_div, "Workflow")


        # determines whether sobject has a pipline
        pipeline_div.add_class("spt_create_search_type_pipeline")

        pipeline_checkbox = CheckboxWdg("sobject_pipeline")

        pipeline_div.add("All sType items can have pipelines which dictate the workflow of an sType. ")
        pipeline_div.add("Pipelines contain processes that dictate the workflow of an sType.  Add proccess that need to be tracked.")
        pipeline_div.add("<br/>"*2)
        pipeline_div.add("&nbsp;&nbsp;&nbsp;<b>Items have a Pipeline?</b> ")
        pipeline_div.add(pipeline_checkbox)
        pipeline_div.add("<br/>")

        pipeline_checkbox.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_create_search_type_pipeline");
            var el = top.getElement(".spt_create_search_type_processes");
            var inputs = el.getElements(".spt_input");
            if (bvr.src_el.checked == true) {
                //spt.show(el)
                el.setStyle("opacity", "1.0");
                for (var i = 0; i < inputs.length; i++) {
                    inputs[i].disabled = false;
                }
            }
            else {
                //spt.hide(el)
                el.setStyle("opacity", "0.5");
                for (var i = 0; i < inputs.length; i++) {
                    inputs[i].disabled = true;
                }
            }
            '''
        } )



        # add processes to the pipeline
        processes_div = DivWdg()
        pipeline_div.add(processes_div)
        processes_div.add_class("spt_create_search_type_processes")
        #processes_div.add_style("display: none")
        processes_div.add_style("opacity: 0.5")
        processes_div.add_style("padding-left: 20px")

        processes_div.add("<br/>")

        dynamic_list = DynamicListWdg()
        processes_div.add(dynamic_list)


        process_wdg = DivWdg()
        process_wdg.add_style("padding-left: 40px")
        process_wdg.add("Process: ")
        process_wdg.add( TextWdg("process") )
        dynamic_list.add_template(process_wdg)

        for i in range(0,3):
            process_wdg = DivWdg()
            process_wdg.add_style("padding-left: 40px")
            process_wdg.add("Process: ")
            text = TextWdg("process")
            text.add_attr("disabled", "disabled")
            process_wdg.add( text )
            dynamic_list.add_item(process_wdg)




        pipeline_div.add("<br/>"*2)
        pipeline_div.add("<hr/>")
        pipeline_div.add("<br/>"*2)
        pipeline_div.add("Items can be grouped into different collections to help searching and organizing.")
        pipeline_div.add("<br/>"*2)
        pipeline_div.add("&nbsp;&nbsp;&nbsp;<b>Support Collections?</b> ")
        collection_checkbox = CheckboxWdg("sobject_collection")
        pipeline_div.add(collection_checkbox)
        pipeline_div.add("<br/>")



        #pipeline_div.add("<br/>"*2)


        # Page 4
        column_div = DivWdg()
        wizard.add(column_div, "Columns")

        # determines whether sobject shows a preview by default
        preview_checkbox = CheckboxWdg("sobject_preview")
        preview_checkbox.set_checked()

        column_div.add("All sType items can have preview images associated with them.")
        column_div.add("<br/>"*2)
        column_div.add("&nbsp;&nbsp;&nbsp;<b>Include Preview Image?</b> ")
        column_div.add(preview_checkbox)
        column_div.add("<br/>"*2)


        column_div.add( self.get_columns_wdg() )


        # Page 3
        naming_wdg = self.get_naming_wdg()
        wizard.add(naming_wdg, "Naming")


        # Page 4
        """
        finish_wdg = DivWdg()
        wizard.add(finish_wdg, "Finish")
        finish_wdg.add("<br/>"*5)
        finish_wdg.add("Click 'Register' button below to complete")
        """


        # submit button
        submit_input = self.get_submit_input()
        wizard.add_submit_button(submit_input)

        return top


    def get_layout_wdg(self):
        div = DivWdg()
        div.add_class("spt_choose_layout_top")

        div.add("Choose a default layout: ")
        div.add("<br/>")


        titles = ['Table', 'Tile', 'File Browser', 'Check-in', 'Card']
        values = ['table', 'tile', 'browser', 'check-in', 'card']
        images = [
            "/context/images/table_layout.jpg",
            "/context/images/tile_layout.jpg",
            "/context/images/browser_layout.jpg",
            "/context/images/checkin_layout.jpg",
            "/context/images/card_layout.jpg",
        ]


        for title, value, image in zip(titles,values, images):
            option_div = DivWdg()
            div.add(option_div)
            radio = RadioWdg("layout")
            option_div.add(radio)
            if value == "table":
                radio.set_checked()
            radio.add_style("margin-top: -5px")
            option_div.add(" &nbsp;%s" % title)
            radio.add_attr("value", value)
            option_div.add_style("margin-top: 10px")
            option_div.add_style("margin-bottom: 10px")
            option_div.add_style("margin-left: 15px")
            radio.add_attr("spt_image", image)
            radio.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_choose_layout_top");
            var img_el = top.getElement(".spt_image");

            var path = bvr.src_el.getAttribute("spt_image");
            img_el.setAttribute("src", path);
            '''
            } )


        div.add("<br/>")

        img_div = DivWdg()
        div.add(img_div)
        img_div.add_style("text-align: center")

        img = HtmlElement.img(src=images[0])
        img_div.add(img)
        img.add_class("spt_image")
        img.add_border()
        img.set_box_shadow("0px 0px 5px")



        return div



    def get_naming_wdg(self):

        div = DivWdg()

        div.add("Naming conventions dictate where in the repository files are placed during a check-in.  TACTIC allows configuration for both directory and file naming conventions.")

        div.add("<br/>")
        div.add("<br/>")


        folder_div = DivWdg()
        div.add(folder_div)

        checkbox = CheckboxWdg("has_folder_naming")
        folder_div.add(checkbox)
        span = SpanWdg(HtmlElement.b("enforce directory naming conventions"), css='small')
        folder_div.add(span)

        dirname_div = DivWdg()
        div.add(dirname_div)
        unique_id = dirname_div.set_unique_id()
        dirname_div.add_style("display: none")
        dirname_div.add_style("padding: 15px 0px 15px 25px")

        checkbox.add_behavior( {
            'type': 'click_up',
            'unique_id': unique_id,
            'cbjs_action': '''
            spt.toggle_show_hide( $(bvr.unique_id) )
            '''
        } )


        dirname_div.add("Choose where you wish files to be checked into: ")
        dirname_div.add("<br/>")


        expr = "/{project.code}/{search_type.table_name}/{sobject.name}"
        dirname_div.add( self.get_naming_item_wdg(expr, "Name", is_checked=True) )

        expr = "/{project.code}/{search_type.table_name}/{sobject.code}"
        dirname_div.add( self.get_naming_item_wdg(expr, "Project/Job") )

        expr = "/{project.code}/{search_type.table_name}/{sobject.category}/{sobject.code}"

        expr = "/{project.code}/{search_type.table_name}/{sobject.code}/{snapshot.process}"
        dirname_div.add( self.get_naming_item_wdg(expr, "Asset with Workflow") )


        div.add("<br/>")



        # file naming conventions

        folder_div = DivWdg()
        div.add(folder_div)

        checkbox = CheckboxWdg("has_file_naming")
        folder_div.add(checkbox)
        span = SpanWdg(HtmlElement.b("enforce file naming conventions"), css='small')
        folder_div.add(span)

        dirname_div = DivWdg()
        div.add(dirname_div)
        unique_id = dirname_div.set_unique_id()
        dirname_div.add_style("display: none")
        dirname_div.add_style("padding: 15px 0px 15px 25px")

        checkbox.add_behavior( {
            'type': 'click_up',
            'unique_id': unique_id,
            'cbjs_action': '''
            spt.toggle_show_hide( $(bvr.unique_id) )
            '''
        } )

        dirname_div.add("Choose how checked-in files should be named: ")
        dirname_div.add("<br/>")


        expr = "{sobject.name}_{basefile}_v{version}.{ext}"
        dirname_div.add( self.get_naming_item_wdg(expr, "Name", mode="file", is_checked=True) )


        expr = "{sobject.code}_{basefile}_v{version}.{ext}"
        dirname_div.add( self.get_naming_item_wdg(expr, "Code", mode="file") )

        expr = "{sobject.code}_{basefile}_{process}_v{version}.{ext}"
        dirname_div.add( self.get_naming_item_wdg(expr, "Code with Process", mode="file") )



        """
        div.add("<br/>")

        radio = RadioWdg("naming")
        div.add(radio)
        radio.add_style("margin-top: -5px")
        div.add("<b>Custom</b>")
        radio.add_attr("value", "_CUSTOM")

        div.add("<br/>")
        text = TextAreaWdg(name="custom_naming")
        #text.add_style("display: none")
        text.add_style("width: 400px")
        text.add_style("margin-left: 30px")
        div.add(text)
        text.add_behavior( {
            'type': 'blur',
            'cbjs_action': r'''
            var value = bvr.src_el.value;
            value = value.replace(/\/([ \t])+/g, "/");
            value = value.replace(/([ \t])+\//g, "/");
            bvr.src_el.value = value;
            '''
        } )
        """

        return div


    def _example(self, expr):
        project_code = Project.get_project_code()

        sample_data = {
            "project.code": project_code,
            "search_type.table_name": "asset",
            "sobject.category": "cars!sports",
            "snapshot.process": "WIP",
            "sobject.code": "JOB00586",
            "sobject.name": "Tradeshow-Brochure-Aug2013",
            "sobject.relative_dir": "%s!asset!vehicles!cars!sports" % project_code,
            "basefile": "DSC0123",
            "version": "003",
            "ext": "png",
            "process": "delivery"
        }

        sample_expr = expr
        for name, value in sample_data.items():
            sample_expr = sample_expr.replace("{%s}" % name, value)

        return sample_expr

    def get_naming_item_wdg(self, expr, title, mode="directory", is_checked=False):

        new_expr = self._example(expr)

        div = DivWdg()
        div.add_style("margin-top: 10px")

        title_wdg = DivWdg()
        div.add(title_wdg)

        from pyasm.widget import RadioWdg
        radio = RadioWdg("%s_naming" % mode)
        title_wdg.add(radio)
        #if title == "Default":
        if False:
            radio.set_checked()
            radio.add_attr("value", "_DEFAULT")
        else:
            radio.add_attr("value", expr)
            if is_checked:
                radio.set_checked()
        radio.add_style("margin-top: -5px")

        title_wdg.add(title)
        title_wdg.add_style("padding: 3px")
        title_wdg.add_style("font-weight: bold")

        table = Table()
        table.add_style("font-size: 0.80em")
        table.add_style("margin-left: 25px")
        div.add(table)

        import re
        if mode == "directory":
            delimiter = "/"
        else:
            delimiter = "!!!"

        tr = table.add_row()
        #tr.add_style("display: none")
        parts = re.split(re.compile("[%s]" % delimiter), new_expr)
        for i, item in enumerate(parts):
            item = item.replace("!", "/")
            td = table.add_cell(item)
            td.add_style("text-align: left")
            td.add_style("padding-right: 15px")
            if i < len(parts) - 1:
                table.add_cell(delimiter)

        parts = re.split(re.compile("[%s]" % delimiter), expr)
        tr = table.add_row()
        #tr.add_style("display: none")
        tr.add_style("opacity: 0.5")
        for i, item in enumerate(parts):
            td = table.add_cell(item)
            td.add_style("text-align: left")
            td.add_style("padding-right: 15px")
            if i < len(parts) - 1:
                table.add_cell(delimiter)

        return div



    def get_preview_wdg(self):

        # add an icon for this project
        image_div = DivWdg()
        image_div.add_class("spt_image_top")
        image_div.add_color("background", "background")
        image_div.add_color("color", "color")
        image_div.add_style("padding: 0px 0px 10px 0px")


        image_div.add("<br/><b>Preview Image: </b>")

        on_complete = '''var server = TacticServerStub.get();
        var file = spt.html5upload.get_file(); 
        if (file) { 

            var top = bvr.src_el.getParent(".spt_image_top");
            var text = top.getElement(".spt_image_path");
            var display = top.getElement(".spt_path_display");
            var check_icon = top.getElement(".spt_check_icon");

            var server = TacticServerStub.get();
            var ticket = spt.Environment.get().get_ticket();


            display.innerHTML = "Uploaded: " + file.name;
            display.setStyle("padding", "10px");
            check_icon.setStyle("display", "");
          
          
            var filename = file.name;
            
            // allow any name for now
            //filename = spt.path.get_filesystem_name(filename);
            var kwargs = {
                ticket: ticket,
                filename: filename
            }
            try {
           
                
                var ret_val = server.execute_cmd("tactic.command.CopyFileToAssetTempCmd", kwargs);

                var info = ret_val.info;
                var path = info.web_path;
                text.value = info.lib_path;
            
                display.innerHTML = display.innerHTML + "<br/><br/><div style='text-align: center'><img style='width: 80px;' src='"+path+"'/></div>";
            }
            catch(e) {
                spt.alert(spt.exception.handler(e));
            }
            spt.app_busy.hide();
            }
        else {
            spt.alert('Error: file object cannot be found.') 
        }
            spt.app_busy.hide();
        '''
        ticket = Environment.get_ticket()
        button = UploadButtonWdg(title="Browse", on_complete=on_complete, ticket=ticket) 
        image_div.add(button)
        button.add_style("margin-left: 215px")
        button.add_style("margin-right: auto")



        text = HiddenWdg("image_path")
        #text = TextWdg("image_path")
        text.add_class("spt_image_path")
        image_div.add(text)

        check_div = DivWdg()
        image_div.add(check_div)
        check_div.add_class("spt_check_icon")
        check_icon = IconWdg("Image uploaded", IconWdg.CHECK)
        check_div.add(check_icon)
        check_div.add_style("display: none")
        check_div.add_style("float: left")
        check_div.add_style("padding-top: 8px")

        path_div = DivWdg()
        image_div.add(path_div)
        path_div.add_class("spt_path_display")

        image_div.add(HtmlElement.br())
        span = DivWdg()
        image_div.add(span)
        span.add_style("padding: 10px 20px 10px 20px")
        span.add_color("background", "background3")
        span.add(IconWdg("INFO", IconWdg.CREATE))
        span.add("The preview image is a small image that will be used in verious places as a visual representation of this searchable type.")

        return image_div








    def get_submit_input(self):
        submit_input = ActionButtonWdg(title='Register >>', tip="Register New sType")

        behavior = {
            'type':         'click_up',
            'mouse_btn':    'LMB',
            'options':      {
                'database':     self.database,
                'namespace':    self.namespace,
                'schema':       self.schema,
            },

            'cbjs_action':  '''

           

            var top = bvr.src_el.getParent(".spt_create_search_type_top");

            var options = bvr.options;
            var class_name = 'tactic.ui.app.SearchTypeCreatorCmd';
            var values = spt.api.Utility.get_input_values(top);

            var search_type = values.search_type_name;
            options.search_type = search_type[0];

           
            var yes = function(){
                spt.app_busy.show("Registering sType");
                var server = TacticServerStub.get();
                server.start({title: "Registered new sType", 'description': 'Registered new sType [' + search_type + ']'})
                try {
                    var response = server.execute_cmd(class_name, options, values);


                    var dialog = spt.popup.get_popup(top);
                    //spt.hide(dialog);

                    if (dialog.on_register_cbk) {
                        dialog.on_register_cbk();
                    }

                    spt.popup.close(dialog);

                    // fire stype create
                    var event_name = "stype|create";
                    spt.named_events.fire_event(event_name, bvr );

                    server.finish()
                    
                    spt.panel.refresh("side_bar");

                    spt.app_busy.hide();
                }
                catch(e) {
                    spt.alert("Error: " + spt.exception.handler(e));
                    server.abort();
                    spt.app_busy.hide();
                    return;
                }
            }

            if (search_type[0].test(/^sthpw/) )
                spt.confirm('sthpw is designed for internal use. If you need to create an sType to be shared by other projects, you can create such sType with a different prefix. Do you still want to continue creating this sType in the sthpw database?', yes, null);

            else
                yes();

            ''',
        }
        submit_input.add_behavior(behavior)
        #submit_input.add_event("onclick", "new spt.CustomProject().create_search_type_cbk()")
        #submit_input.set_text('Create')
        submit_input.add_style("float: right")

        return submit_input



    def get_columns_wdg(self):
        '''widget to create columns'''

        div = DivWdg()

        div.add("<hr/>")

        div.add("Extra attributes can be added here.  These are direct columns to the corresponding table of the sType.  Each column will be mapped directly to an attribute of the sType.<br/><br/>")

        div.add("A number of columns are created by default for every sType.  These include: id, code, name, description, login and timestamp.<br/><br/>")


        title = DivWdg()
        div.add(title)
        title.add("<b>Add Columns to sType:</b>")



        dynamic_list = DynamicListWdg()
        div.add(dynamic_list)


        column_wdg = Table()
        dynamic_list.add_template(column_wdg)

        column_wdg.add_cell( "Name: ")
        name_text = TextWdg("column_name")
        column_wdg.add_cell( name_text )
        column_wdg.add_cell("&nbsp;"*5)
        column_wdg.add_cell( "Type: ")

        #type_select = SelectWdg("column_type")
        #column_wdg.add(type_select)
        #type_select.set_option("values", "varchar(256)|varchar(1024)|integer|float|text|timestamp")
        from tactic.ui.manager import FormatDefinitionEditWdg
        option = {
        'name': 'xxx',
        'values': 'integer|float|percent|currency|date|time|scientific|boolean|text|timecode',
        }
        format_wdg = FormatDefinitionEditWdg(option=option)
        td = column_wdg.add_cell(format_wdg)
        td.add_style("width: 250px")




        column_wdg = Table()
        dynamic_list.add_item(column_wdg)

        column_wdg.add_cell( "Name: ")
        name_text = TextWdg("column_name")
        column_wdg.add_cell( name_text )
        column_wdg.add_cell("&nbsp;"*5)
        column_wdg.add_cell( "Type: ")

        #type_select = SelectWdg("column_type")
        #column_wdg.add(type_select)
        #type_select.set_option("values", "varchar(256)|varchar(1024)|integer|float|text|timestamp")
        option = {
        'name': 'xxx',
        'values': 'integer|float|percent|currency|date|time|scientific|boolean|text|timecode',
        }
        format_wdg = FormatDefinitionEditWdg(option=option)
        td = column_wdg.add_cell(format_wdg)
        td.add_style("width: 250px")

        return div





__all__.append("PredefinedSearchTypesWdg")
class PredefinedSearchTypesWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top

        top.add_border()
        top.add_color("background", "background")
        #top.add_style("padding: 10px")

        table = Table()
        top.add(table)
        table.add_color("color", "color3")
        table.add_row()

        left = table.add_cell()
        left.add(self.get_stypes_list())
        left.add_style("vertical-align: top")
        left.add_style("min-width: 150px")
        left.add_color("background", "background3")
        left.add_style("padding", "10px")
        left.add_border()

        right = table.add_cell()
        right.add_style("vertical-align: top")
        right.add_border()

        right_div = DivWdg()
        right.add(right_div)
        right_div.add_style("width: 500px")
        right_div.add_style("height: 400px")
        right_div.add_style("padding: 10px")
        right_div.add(self.get_plugin_info_wdg())

        return top


    def get_plugin_info_wdg(self):
        div = DivWdg()

        div.add('''<b style='font-size: 14px'>vfx/shot</b>
        <hr/>
        This search type is used to track shots.  It contains a large number of predefined attributes that are particular to shots used in the VFX industry.
        <br/></br/>

        <b>Attributes</b>
        <br/></br/>

        start_frame<br/>
        end_frame<br/>
        f_stop<br/>
        lens<br/>
        status<br/>

        <br/></br/>

        <b>Views</b>
        <br/></br/>

        Shot Tracking - view to manage all shot information<br/>
        <br/></br/>
        ''')


        div.add("<hr/>")

        create_div = DivWdg()
        div.add(create_div)

        create_button = ActionButtonWdg(title="Create")
        create_div.add(create_button)
        create_button.add_style("margin-right: auto")
        create_button.add_style("margin-left: auto")

        create_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.alert("CREATE");
            '''
        } )

        return div



    def get_stypes_list(self):

        div = DivWdg()



        title_div = DivWdg()
        div.add(title_div)
        title_div.add("Current Project")
        title_div.add_style("font-weight: bold")
        title_div.add_style("font-size: 14px")
        title_div.add("<hr/>")

        content_div = DivWdg()
        div.add(content_div)

        # each of these should be plugins???
        search_types = ['sequence', 'shot', 'asset', 'camera', 'layer']
        plugin_code = 'vfx'
        for search_type in search_types:
            search_type_div = DivWdg()
            content_div.add(search_type_div)
            search_type_div.add(search_type)

            search_type_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.alert("Loading shot...!")
                '''
            } )


        div.add("<br/>"*2)


        title_div = DivWdg()
        div.add(title_div)
        title_div.add("Predefined sTypes")
        title_div.add_style("font-weight: bold")
        title_div.add_style("font-size: 14px")
        title_div.add("<hr/>")


        from tactic.ui.widget.swap_display_wdg import SwapDisplayWdg as NewSwapDisplayWdg
        categories = ["VFX", "Consumer Products", "Advertising", "Book Publishing"]
        for category in categories:
            category_div = DivWdg()
            div.add(category_div)

            category = category
            swap = NewSwapDisplayWdg(title=category, icon='FILM')
            category_div.add(swap)


        content_div = DivWdg()
        div.add(content_div)

        # each of these should be plugins???
        search_types = ['sequence', 'shot', 'asset', 'camera', 'layer']
        plugin_code = 'vfx'
        for search_type in search_types:
            search_type_div = DivWdg()
            content_div.add(search_type_div)
            search_type_div.add(search_type)

            search_type_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.alert("Loading shot...!")
                '''
            } )



        config = '''
        <sType name='VFX/shot'/>
        <column name='start_frame' type='int'/>
        <column name='end_frame' type='int'/>
        <column name='f_stop' type='int'/>
        <column name='aperture' type='varchar(256)'/>

        </sType>
        '''

        # plugins
        manifest_xml = '''
        <manifest code='vfx' version='1.0.a01'>
          <search_type code='project/asset_category'/>
          <search_type code='project/asset'/>
          <sobject search_type='config/widget_config' expression="@SOBJECT(config/widget_config['category','HelpWdg']['view','asset_list'])"/>
        </manifest>
        '''

        from tactic.command import PluginCreator
        cmd = PluginCreator(manifest=manifest_xml)
        cmd.execute()



        return div





class SearchTypeCreatorCmd(Command):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.database = kwargs.get('database')
        self.namespace = kwargs.get('namespace')
        self.schema = kwargs.get('schema')

        if not self.database:
            self.project = Project.get()
            self.database = self.project.get_code()
        else:
            # need to have a project with this database name
            # essentially: project == database
            self.project = Project.get_by_code(self.database)

        self.search_type_name = self.get_value("search_type_name") 
        self.db_resource = self.project.get_project_db_resource()
        # Advanced mode: special condition for sthpw/.. sType
        if self.search_type_name.startswith('sthpw/'):
            sql = DbContainer.get('sthpw')
            self.db_resource = sql.get_db_resource()
            self.database = 'sthpw'
            self.namespace = 'sthpw'

        if not self.namespace:
            self.namespace = project_code

        if not self.schema:
            self.schema = 'public'

        super(SearchTypeCreatorCmd,self).__init__(**kwargs)

        self.column_names = self.get_values("column_name")
        if not self.column_names:
            self.column_names = []
        #self.column_types = self.get_values("column_type")
        self.column_types = self.get_values("data_type")
        if not self.column_types:
            self.column_types = []
        self.formats = self.get_values("format")
        if not self.formats:
            self.formats = []

        self.search_type_obj = None

    def get_title(self):
        return "sType Creator"


    def set_database(self, database):
        self.database = database

    def set_schema(self, schema):
        self.schema = schema


    def get_value(self, name):
        web = WebContainer.get_web()

        value = self.kwargs.get(name)
        if not value:
            value = web.get_form_value(name)

        return value

    def get_values(self, name):
        web = WebContainer.get_web()

        value = self.kwargs.get(name)
        if not value:
            value = web.get_form_values(name)

        return value




    def get_sobject(self):
        return self.sobject
        


    def execute(self):
        if not self.database or not self.schema:
            raise CommandException("Either database nor schema is not defined")



        # FIXME: hack this in for now to handle "public"
        if not self.namespace:
            if self.schema == "public":
                self.namespace = self.database
            else:
                self.namespace = "%s/%s" % (self.database,self.schema)

        web = WebContainer.get_web()

        
        if self.search_type_name == "":
            raise CommandExitException("No search type supplied")

        if self.search_type_name.find("/") != -1:
            self.namespace, self.search_type_name = self.search_type_name.split("/", 1)
            # check if it is a valid namespace
            #proj = Project.get_by_code(self.namespace)
            #if not proj:
            #    raise TacticException('[%s] is not a valid namespace'%self.namespace)

        if re.search(r'\W', self.namespace):
            raise TacticException("No special characters or spaces allowed in the namespace of sType.")
        if re.search(r'\W', self.search_type_name):
            raise TacticException("No special characters or spaces allowed in the sType name.")

        #if re.search(r'[A-Z]', self.namespace):
        #    raise TacticException("No upper case letters allowed in the namespace of sType.")
        #if re.search(r'[A-Z]', self.search_type_name):
        #    raise TacticException("No uppercase letters allowed in the sType name.")


        #self.asset_description = web.get_form_value("asset_description")
        self.asset_description = self.get_value("asset_description")
        if self.asset_description == "":
            self.asset_description == "No description"

        #self.asset_title = web.get_form_value("asset_title")
        self.asset_title = self.get_value("asset_title")
        if self.asset_title == "":
            self.asset_title == "No title"

        #copy_from_template = web.get_form_value("copy_from_template")
        copy_from_template = self.get_value("copy_from_template")
        search_type = "%s/%s" % (self.namespace, self.search_type_name)
        

        # don't auto lower it cuz the same sType name may get added to the schema
        #search_type = search_type.lower()

        # Save the newly created search_type to info so we can get it and
        # display it when we are ready to refresh the SearchTypeToolWdg.
        self.info['search_type'] = search_type

        
        self.register_search_type(search_type)
        if not self.search_type_obj:
            self.search_type_obj = SearchType.get(search_type)
        #if web.get_form_value("sobject_pipeline"):
        if self.get_value("sobject_pipeline"):
            self.has_pipeline = True
        else:
            self.has_pipeline = False


        if self.get_value("sobject_collection"):
            self.has_collection = True
        else:
            self.has_collection = False



        if self.get_value("sobject_preview"):
            self.has_preview = True
        else:
            self.has_preview = False


        # add naming first because create table needs it
        self.add_naming()


        #self.parent_type = web.get_form_value("sobject_parent")
        self.parent_type = self.get_value("sobject_parent")

        if not copy_from_template:
            self.create_table()
            # for sthpw sType, create the table only
            if not self.namespace == 'sthpw':
                self.create_config()
                self.create_pipeline()
        else:
            # FIXME: don't copy config yet ... should really copy all
            # ... or have an option
            #self.copy_template_config(copy_from_template)
            self.copy_template_table(copy_from_template)

        
        # add this search_type to the schema for this project
        project_code = Project.get_project_code()
        
        schema = Schema.get_by_code(project_code)

        # if it doesn't exist, then create an empty one
        if not schema:
            schema = Schema.create(project_code, "%s project schema" % project_code )

        if schema:
            schema.add_search_type(search_type, self.parent_type)
            schema.commit()
        else:
            raise CommandException("No schema defined for [%s]" % self.database)


        self.add_sidebar_views()

        self.checkin_preview()

        


    def register_search_type(self, search_type):
        # first check if it already exists
        search = Search( SearchType.SEARCH_TYPE )
        search.add_filter("search_type", search_type)
        test_sobject = search.get_sobject()
        if test_sobject:
            self.search_type_obj = SearchType.get(search_type)
            is_project_specific = self.get_value("project_specific") == "on"
            if self.table_exists() and not is_project_specific:
                msg = "Search type [%s] already exists." % search_type
                if search_type.startswith('sthpw/'):
                    msg = '%s If you are trying to add this to the Project Schema, use the Save button instead of the Register button.'%msg
           
                raise CommandException(msg)
            else: # continue to add table to current project
                return

        
        # create the search type
        sobject = SearchType( SearchType.SEARCH_TYPE )

        sobject.set_value("search_type", search_type)

        sobject.set_value("namespace", self.namespace)

        if self.get_value("project_specific") == "on":
            sobject.set_value("database", self.database)
        else:
            if self.namespace == 'sthpw':
                sobject.set_value("database", "sthpw")
            else:
                sobject.set_value("database", "{project}")

        layout = self.get_value("layout")
        if layout:
            sobject.set_value("default_layout", layout)

        sobject.set_value("schema", self.schema)

        if self.schema == "public":
            table = self.search_type_name
        else:
            table = "%s.%s" % (self.schema, self.search_type_name)
        sobject.set_value("table_name", table)
        sobject.set_value("class_name", "pyasm.search.SObject")
        sobject.set_value("title", self.asset_title)
        sobject.set_value("description", self.asset_description)

        sobject.commit()

        self.sobject = sobject


    

    def create_config(self):
        search_type = self.search_type_obj.get_base_key()
        columns = SearchType.get_columns(search_type)
        #if self.has_pipeline:
        #    columns.remove("pipeline_code")
        #    columns.append("pipeline")

        # preview is always first
        if self.has_preview:
            columns.insert(0, "preview")

        # remove some of the defaults columns
        columns.remove("id")
        if 's_status' in columns:
            columns.remove("s_status")
        if 'login' in columns:
            columns.remove("login")
        if 'timestamp' in columns:
            columns.remove("timestamp")
        if 'keywords' in columns:
            columns.remove("keywords")

        self.show_code = False
        if not self.show_code:
            columns.remove("code")


        if self.has_preview:
            default_columns = ['preview', 'name', 'description']
        else:
            default_columns = ['name', 'description']


        # create the xml document
        for view in ["definition", "table"]:
            xml = Xml()
            xml.create_doc("config")
            root = xml.get_root_node()
            view_node = xml.create_element(view)
            xml.append_child(root, view_node)
            # definition has to be the last in the loop
            #if view == "definition":
            #    columns.append('update')


            for column in default_columns:
                element = xml.create_element("element")
                Xml.set_attribute(element, "name", column)
                xml.append_child(view_node, element)


            for column in columns:

                # skip relative_dir
                if column == 'relative_dir':
                    continue

                # skip pipeline
                if column in ['pipeline_code'] or column in default_columns:
                    continue

                if column in self.column_names:
                    continue

                element = xml.create_element("element")
                Xml.set_attribute(element, "name", column)
                xml.append_child(view_node, element)


            # handle the custom columns
            for column_name, column_type, format in zip(self.column_names, self.column_types, self.formats):
                if not column_name:
                    continue

                element = xml.create_element("element")
                xml.append_child(view_node, element)
                Xml.set_attribute(element, "name", column_name)

                # need to use xml to add to the config
                if view == 'definition':
                    display = xml.create_element("display")
                    xml.append_child(element, display)
                    Xml.set_attribute(display, "widget", "format")

                    xml.create_text_element("format", format, node=display)
                    xml.create_text_element("type", column_type, node=display)

            # add view if there is a pipeline
            if self.has_pipeline and view == 'table':
                element = xml.create_element("element")
                Xml.set_attribute(element, "name", "pipeline")
                xml.append_child(view_node, element)

                element = xml.create_element("element")
                Xml.set_attribute(element, "name", "task_status_edit")
                xml.append_child(view_node, element)


            element = xml.create_element("element")
            Xml.set_attribute(element, "name", "notes")
            xml.append_child(view_node, element)


            WidgetDbConfig.create(search_type, view, xml.get_xml() )



 
        # create the edit view
        view = "edit"
        xml = Xml()
        xml.create_doc("config")
        root = xml.get_root_node()
        view_node = xml.create_element(view)
        xml.append_child(root, view_node)

        columns.append("keywords")

        for column in default_columns:
            element = xml.create_element("element")
            Xml.set_attribute(element, "name", column)
            xml.append_child(view_node, element)


        # create code element
        for column in columns:
            if column in ['pipeline_code'] or column in default_columns:
                continue

            if column == 'relative_dir':
                continue

            element = xml.create_element("element")
            Xml.set_attribute(element, "name", column)
            #view_node.appendChild(element)
            xml.append_child(view_node, element)



        WidgetDbConfig.create(search_type, view, xml.get_xml() )

      



    def _create_element(self, xml, view_node, name):
        element = xml.create_element("element")
        element.setAttribute("name", name)
        #view_node.appendChild(element)
        xml.append_child(view_node, element)



    def copy_template_table(self, template):
        template_type_obj = SearchType.get(template)
        template_table = template_type_obj.get_table()
        table = self.search_type_obj.get_table()

        database = self.search_type_obj.get_database()

        sql = DbContainer.get(database)
        sql.copy_table_schema(template_table, table)

        # log that this table was creatd
        TableUndo.log(database, table)


    def table_exists(self):
        '''check if table exists'''
        if self.schema == "public":
            table = self.search_type_name
        else:
            table = "%s.%s" % (self.schema, self.search_type_name)
        
        sql = DbContainer.get(self.db_resource)
        impl = sql.get_database_impl()
        exists = impl.table_exists(self.db_resource, table)
        return exists
    

    def create_table(self):

        if self.schema == "public":
            table = self.search_type_name
        else:
            table = "%s.%s" % (self.schema, self.search_type_name)

        if self.namespace == 'sthpw': 
            search_type = "%s/%s" % (self.namespace, self.search_type_name)
        else:    
            search_type = "%s/%s?project=%s" % (self.namespace, self.search_type_name, self.database)
        create = CreateTable(search_type=search_type)

        create.set_table( table )

        # create primary
        create.add("id", "serial", primary_key=True)

        create.add("code", "varchar")
        if self.has_pipeline:
            create.add("pipeline_code", "varchar")
        if self.has_collection:
            create.add("_is_collection", "boolean")


        # add default columns
        create.add("name", "varchar")
        create.add("description", "text")
        create.add("keywords", "text")
        create.add("login", "varchar")
        create.add("timestamp", "timestamp")
        create.add("s_status", "varchar")
        create.add_constraint(["code"], mode="UNIQUE")


        for column_name, column_type in zip(self.column_names, self.column_types):
            if not column_name:
                continue

            data_type = ColumnAddCmd.get_data_type(search_type, column_type)
            create.add(column_name, data_type)
 

        if self.folder_naming.find("{sobject.relative_dir}") != -1:
            create.add("relative_dir", "text")
        elif self.folder_naming.find("{sobject.category}") != -1:
            create.add("category", "text")



        # DEPRECATED
        #create.set_primary_key("id")

        statement = create.get_statement()

        sql = DbContainer.get(self.db_resource)
        database = sql.get_database_name()
        impl = sql.get_database_impl()
        exists = impl.table_exists(self.db_resource, table)
        if exists:
            #raise TacticException('This table [%s] already exists.'%table)
            pass
        else:
            create.commit(sql)
            TableUndo.log(self.search_type_obj.get_base_key(), database, table)
        '''
            # add columns 
            db_resource = Project.get_db_resource_by_search_type(search_type)

            sql = DbContainer.get(db_resource)

            
            # put a unique constraint on code, which works automatically with Plugin creation
            statement = 'ALTER TABLE "%s" ADD CONSTRAINT "%s_code_unique" UNIQUE ("code")' % (table, table)
            #statement = 'CREATE UNIQUE INDEX "%s_code_idx" ON "%s" ("code")' % (table, table)
            sql.do_update(statement)

        '''


    def add_sidebar_views(self):

        search_type = self.search_type_obj.get_base_key()
        namespace, table = search_type.split("/")
        title = self.search_type_obj.get_title()

        # _list view
        class_name = "tactic.ui.panel.ViewPanelWdg"
        display_options = {
            "class_name": class_name,
            "search_type": search_type,
            "layout": "default"
        }
        
        # this is now handled by the "default" setting
        """
        layout = self.get_value("layout")

        if layout == "tile":
            class_name = "tactic.ui.panel.ViewPanelWdg"
            display_options = {
                "class_name": class_name,
                "search_type": search_type,
                "layout": "tile"
            }

        elif layout == "card":
            class_name = "tactic.ui.panel.ViewPanelWdg"
            display_options = {
                "class_name": class_name,
                "search_type": search_type,
                "layout": "card"
            }

        elif layout == "browser":
            class_name = "tactic.ui.panel.ViewPanelWdg"
            display_options = {
                "class_name": class_name,
                "search_type": search_type,
                "layout": "browser"
            }



        else:
            class_name = "tactic.ui.panel.ViewPanelWdg"
            display_options = {
                "class_name": class_name,
                "search_type": search_type,
                "view": "table",
                "layout": "default"
            }
        """

        action_options = {}
        action_class_name = {}

        element_attrs = {
            'title': title
        }

        view = "definition"
        element_name = "%s_list" % table

        config = WidgetDbConfig.append( "SideBarWdg", view, element_name, class_name="LinkWdg", display_options=display_options, element_attrs=element_attrs)

        view = "project_view"
        element_name = "%s_list" % table
        config = WidgetDbConfig.append( "SideBarWdg", view, element_name)



    def create_pipeline(self):

        if not self.has_pipeline:
            return

        search_type = self.search_type_obj.get_base_key()
        namespace, table = search_type.split("/")
        project_code = Project.get_project_code()

        pipeline_code = "%s/%s" % (project_code, table)

        title = table.replace("_", " ").title()

        # create a pipeline
        search = Search("sthpw/pipeline")
        search.add_filter("code", title)
        search.add_filter("code", pipeline_code)
        pipeline = search.get_sobject()

        # TODO: check for search types??
        if pipeline:
            return


        processes = self.get_values("process")
        filtered = []
        for process in processes:
            if process:
                filtered.append(process)
        processes = filtered


        pipeline_sobj = SearchType.create("sthpw/pipeline")
        pipeline_sobj.set_value("code", pipeline_code)
        if not processes:
            # create an empty pipeline
            pipeline = '''<?xml version="1.0" encoding="UTF-8"?>
<pipeline/>
'''
        else:
            p = []
            p.append('''<?xml version="1.0" encoding="UTF-8"?>''')
            p.append('''<pipeline>''')

            for i, process in enumerate(processes):
                p.append('''  <process name="%s"/>''' % process)

                # create the process entry
                process_sobj = SearchType.create("config/process")
                process_sobj.set_value("pipeline_code", pipeline_code)
                process_sobj.set_value("process", process)
                process_sobj.set_value("sort_order", i)
                process_sobj.commit()

            last_process = None
            for i, process in enumerate(processes):
                if last_process:
                    p.append('''  <connect from="%s" to="%s"/>''' % (last_process, process) )
                last_process = process





            p.append('''</pipeline>''')

            pipeline = "\n".join(p)


        pipeline_sobj.set_value("pipeline", pipeline)
        pipeline_sobj.set_value("project_code", project_code)
        pipeline_sobj.set_value("search_type", search_type)

        pipeline_sobj.commit()



 
    def checkin_preview(self):
        # if there is an image, check it in
        image_path = self.get_values("image_path")
        if image_path:
            image_path = image_path[0]
            if not image_path:
                return

            image_path = image_path.replace("\\", "/")
            # Can't use upload path because the transaction has changed
            #basename = os.path.basename(image_path)
            # and the ticket is lost
            #upload_dir = Environment.get_upload_dir()
            #upload_path = "%s/%s" % (upload_dir, basename)
            parts = image_path.split("/")
            basename = parts[-1]
            ticket = parts[-2]

            asset_dir = Environment.get_asset_dir()
            upload_path = "%s/temp/%s/%s" % (asset_dir, ticket, basename)

            file_type = 'main'

            file_paths = [upload_path]
            file_types = [file_type]

            source_paths = [upload_path]
            from pyasm.biz import IconCreator
            if os.path.isfile(upload_path):
                icon_creator = IconCreator(upload_path)
                icon_creator.execute()

                web_path = icon_creator.get_web_path()
                icon_path = icon_creator.get_icon_path()
                if web_path:
                    file_paths = [upload_path, web_path, icon_path]
                    file_types = [file_type, 'web', 'icon']

            from pyasm.checkin import FileCheckin
            checkin = FileCheckin(self.search_type_obj, context='icon', file_paths=file_paths, file_types=file_types)
            checkin.execute()



    def add_naming(self):

        naming_expr = self.get_value("directory_naming")
        file_naming_expr = self.get_value("file_naming")


        if naming_expr == "_CUSTOM":
            naming_expr = self.get_value("custom_naming")

        if not naming_expr or naming_expr == "_DEFAULT":
            naming_expr = "{project.code}/{search_type.table_name}/{sobject.code}"
        # fix the slashes
        naming_expr = naming_expr.strip("/")

        if not file_naming_expr or file_naming_expr == "_DEFAULT":
            file_naming_expr = "{sobject.name}_v{version}.{ext}"



        has_folder_naming = self.get_value("has_folder_naming") == "on"
        has_file_naming = self.get_value("has_file_naming") == "on"

        naming = SearchType.create("config/naming")
        if not has_folder_naming:
            naming_expr = "{sobject.relative_dir}"
        naming.set_value("dir_naming", naming_expr)

        if not has_file_naming:
            file_naming_expr = "{sobject.name}_v{version}.{ext}"

        naming.set_value("file_naming", file_naming_expr)


        naming.set_value("checkin_type", "auto")

        search_type = self.search_type_obj.get_base_key()
        naming.set_value("search_type", search_type)


        naming.commit()


        self.folder_naming = naming_expr
        self.file_naming = file_naming_expr





