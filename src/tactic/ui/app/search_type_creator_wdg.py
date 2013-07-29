
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
from tactic.ui.panel import TableLayoutWdg, SearchTypeManagerWdg
from tactic.ui.container import PopupWdg, DynamicListWdg
from tactic.ui.widget import SearchTypeSelectWdg, ActionButtonWdg
from tactic.ui.input import TextInputWdg

class SearchTypeToolWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'database': 'the database',
        'schema': 'the schema'
        }

    def init(my):

        database = my.kwargs.get("database")
        schema = my.kwargs.get("schema")

        if not database:
            my.database = Project.get_project_code()
        else:
            my.database = database

        if not schema:
            my.schema = "public"
        else:
            my.schema = schema

        # FIXME: hack this in for now to handle "public"
        if my.schema == "public":
            my.namespace = my.database
        else:
            my.namespace = "%s/%s" % (my.database,my.schema)


    def get_display(my):

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


        #div.add( my.create_div() )
        div.add(my.get_search_type_manager())
        #div.add( my.get_existing_wdg() )


        return div


    def get_search_type_manager(my):
        widget = Widget()
        div = DivWdg(id='SearchTypeManagerContainer')
        #select = SearchTypeSelectWdg(mode=SearchTypeSelectWdg.ALL_BUT_STHPW)
        #widget.add(select)


        wizard = SearchTypeCreatorWdg(namespace=my.namespace, database=my.database, schema=my.schema)
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
        search_type = my.kwargs.get("search_type")
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

    def get_existing_wdg(my):

        div = DivWdg()
        title = DivWdg("Existing Custom sTypes")
        title.add_style("margin: 20px 0 10px 0")
        title.set_class("maq_search_bar")
        div.add(title)

        search_type = SearchType.SEARCH_TYPE

        search = Search( search_type )
        search.add_filter("namespace", my.namespace)
        sobjects = search.get_sobjects()

        table_wdg = TableLayoutWdg( search_type=search_type, view="table" )
        table_wdg.set_sobjects(sobjects)
        div.add(table_wdg)

        return div



class SearchTypeCreatorWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        # DEPRECATED
        'database': 'the database???',
        'namespace': 'the namespace???',
        'schema': 'the schema???',


        'search_type':  'prefilled search type',
        'title':        ' prefilled title',
        'on_register_cbk': 'Callback for when register is clicked'
        }


    def get_display(my):

        my.database = my.kwargs.get("database")
        my.namespace = my.kwargs.get("namespace")
        my.schema = my.kwargs.get("schema")

        project_code = Project.get_project_code()
        if not my.database:
            my.database = project_code
        if not my.namespace:
            my.namespace = project_code
        if not my.schema:
            my.schema = "public"

        project = Project.get()
        project_type = project.get_value("type")
        if project_type and project_type != 'default':
            namespace = project_type
        else:
            namespace = project_code

        my.search_type = my.kwargs.get("search_type")
        if my.search_type and my.search_type.find("/") == -1:
            my.search_type = "%s/%s" % (namespace, my.search_type)


        from tactic.ui.container import WizardWdg
        top = DivWdg()
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("padding: 15px")
        top.add_class("spt_create_search_type_top")



        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias='stype-register|tactic-anatomy-lesson|project-workflow-introduction')
        top.add( help_button )
        help_button.add_style("float: right")

        
        wizard = WizardWdg(title="Register a new sType")
        top.add(wizard)


        create_div = HtmlElement.div()
        wizard.add(create_div, "Information")

        my.set_as_panel(create_div)

        
        name_input = TextWdg("search_type_name")
        name_input.add_class("spt_name_input")
        # as long as we allow this to be displayed in Manage Search Types, it should be editable
        name_input.add_class("spt_input")
        name_input.add_class("SPT_DTS")
        if my.search_type:
            name_input.set_value(my.search_type)
            name_input.set_attr("readonly", "readonly")
            name_input.add_color("background", "background", -10)


        search = Search( SearchType.SEARCH_TYPE )
        search.add_filter("namespace", my.namespace)

        template_select = SelectWdg("copy_from_template")
        template_select.add_empty_option()
        template_select.set_search_for_options( \
                search, "search_type", "table_name")
        #template_select.set_option("labels", "---|People")

        title_text = TextWdg("asset_title")
        title_text.add_class("spt_input")
        title_value = my.kwargs.get("title")
        if not title_value and my.search_type:
            parts = my.search_type.split("/")
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



        description = TextAreaWdg("asset_description")
        description.add_class("spt_input")



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
            tr.add_style("opacity: 0.6")
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
        table.add_header("Title: ").set_attr('align','left')
        table.add_cell(title_text)

        table.add_row_cell("&nbsp;")

        table.add_row()
        th = table.add_header("Searchable Type: ")
        th.add_style("min-width: 150px")
        th.set_attr('align','left')
        td = table.add_cell(name_input)

        table.add_row_cell("&nbsp;")

        table.add_row()
        table.add_header("Description: ").set_attr('align','left')
        table.add_cell(description)

        create_div.add( my.get_preview_wdg() )



        # Page 2
        pipeline_div = DivWdg()
        wizard.add(pipeline_div, "Workflow")


        # determines whether sobject has a pipline
        pipeline_div.add_class("spt_create_search_type_pipeline")

        pipeline_checkbox = CheckboxWdg("sobject_pipeline")

        pipeline_div.add("All sType items can have pipelines which dictate the workflow of an sType. ")
        pipeline_div.add("Pipelines contain processes that dictate the workflow of an sType.  Add proccess that need to be tracked for this sType.")
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


        column_div.add( my.get_columns_wdg() )


        # Page 3
        # DEPRECATED: this is not needed because layout switcher replaces this
        #wizard.add(my.get_view_wdg(), "Side Bar")
        # Page 3
        naming_wdg = my.get_naming_wdg()
        wizard.add(naming_wdg, "Naming")


        # Page 4
        finish_wdg = DivWdg()
        wizard.add(finish_wdg, "Finish")
        finish_wdg.add("<br/>"*5)
        finish_wdg.add("Click 'Register' button below to complete")


        # submit button
        submit_input = my.get_submit_input()
        wizard.add_submit_button(submit_input)

        return top



    def get_naming_wdg(my):

        div = DivWdg()

        div.add("Choose a directory naming convention for this sType:")
        div.add("<br/>")

        expr = "/{project.code}/{search_type.table_name}/{sobject.code}"
        div.add( my.get_naming_item_wdg(expr, "Default") )

        expr = "/{project.code}/{search_type.table_name}/{sobject.category}/{sobject.code}"
        div.add( my.get_naming_item_wdg(expr, "Library Asset") )

        expr = "/{project.code}/{search_type.table_name}/{sobject.code}/{snapshot.process}"
        div.add( my.get_naming_item_wdg(expr, "Asset with Workflow") )

        expr = "/{sobject.relative_dir}"
        div.add( my.get_naming_item_wdg(expr, "Free Form") )


        div.add("<br/>")

        from pyasm.widget import RadioWdg
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

        return div


    def _example(my, expr):
        project_code = Project.get_project_code()

        sample_data = {
            "project.code": project_code,
            "search_type.table_name": "asset",
            "sobject.category": "cars!sports",
            "snapshot.process": "delivery",
            "sobject.code": "CAR00586",
            "sobject.relative_dir": "%s!asset!vehicles!cars!sports" % project_code,
        }

        sample_expr = expr
        for name, value in sample_data.items():
            sample_expr = sample_expr.replace("{%s}" % name, value)

        return sample_expr

    def get_naming_item_wdg(my, expr, title):

        new_expr = my._example(expr)

        div = DivWdg()
        div.add_style("margin-top: 10px")

        title_wdg = DivWdg()
        div.add(title_wdg)

        from pyasm.widget import RadioWdg
        radio = RadioWdg("naming")
        title_wdg.add(radio)
        if title == "Default":
            radio.set_checked()
            radio.add_attr("value", "_DEFAULT")
        else:
            radio.add_attr("value", expr)
        radio.add_style("margin-top: -5px")

        title_wdg.add(title)
        title_wdg.add_style("padding: 3px")
        title_wdg.add_style("font-weight: bold")

        table = Table()
        table.add_style("font-size: 0.85em")
        table.add_style("margin-left: 15px")
        div.add(table)
        parts = expr.split("/")
        table.add_row()



        for item in parts:
            td = table.add_cell(item)
            td.add_style("text-align: left")
            td.add_style("padding-right: 15px")
            table.add_cell("/")

        tr = table.add_row()
        tr.add_style("opacity: 0.5")
        parts = new_expr.split("/")
        for item in parts:
            item = item.replace("!", "/")
            td = table.add_cell(item)
            td.add_style("text-align: left")
            td.add_style("padding-right: 15px")
            table.add_cell("/")

        return div



    def get_preview_wdg(my):

        # add an icon for this project
        image_div = DivWdg()
        #wizard.add(image_div, 'Preview Image')
        #create_div.add(image_div, 'Preview Image')
        image_div.add_class("spt_image_top")
        image_div.add_color("background", "background")
        image_div.add_color("color", "color")
        image_div.add_style("padding: 20px 0px 10px 0px")


        image_div.add("<b>Preview Image: </b>")
        button = ActionButtonWdg(title="Browse")
        image_div.add(button)
        button.add_style("margin-left: auto")
        button.add_style("margin-right: auto")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var applet = spt.Applet.get();
        var server = TacticServerStub.get();

        spt.app_busy.show("Browsing for preview image");
        var path = applet.open_file_browser();

        var top = bvr.src_el.getParent(".spt_image_top");
        var text = top.getElement(".spt_image_path");
        var display = top.getElement(".spt_path_display");
        var check_icon = top.getElement(".spt_check_icon");

        var ticket = spt.Environment.get().get_ticket();
        server.upload_file(path, ticket);

        display.innerHTML = "Uploaded: " + path;
        display.setStyle("padding", "10px");
        check_icon.setStyle("display", "");

        path = path + "";
        /*
        path = path.replace(/\\\\/g, "/");
        var parts = path.split("/");
        var filename = parts[parts.length-1];
        */

        var filename = spt.path.get_basename(path);
        filename = spt.path.get_filesystem_name(filename);
        var kwargs = {
            ticket: ticket,
            filename: filename
        }
        try {
            var ret_val = server.execute_cmd("tactic.command.CopyFileToAssetTempCmd", kwargs)
            var info = ret_val.info;
            var path = info.path;
            text.value = path;

            display.innerHTML = display.innerHTML + "<br/><br/><div style='text-align: center'><img style='width: 80px;' src='"+path+"'/></div>";

        } 
        catch(e) {
            spt.alert(spt.exception.handler(e));
        }
        spt.app_busy.hide();

        '''
        } )

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








    def get_submit_input(my):
        submit_input = ActionButtonWdg(title='Register >>', tip="Register New sType", icon=IconWdg.CREATE)

        behavior = {
            'type':         'click_up',
            'mouse_btn':    'LMB',
            'options':      {
                'database':     my.database,
                'namespace':    my.namespace,
                'schema':       my.schema,
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



    def get_columns_wdg(my):
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




    def get_view_wdg(my):
        '''widget to create predefined view'''

        div = DivWdg()
        div.add('''These predefined views for the newly registered search type will be added to the side bar.  They can be modified under "Manage Side Bar"''')
        div.add("<br/><br/>")

        title = DivWdg()
        div.add(title)
        title.add("<b>Add Predefined Links in Side Bar:</b><br/><br/>")


        predefined = [
        {
            'name': 'Content List',
            'description': 'View to manage the items in the list',
            'checked': True,
            'folder': 'manage'
        },
        {
            'name': 'Add Content Form',
            'description': 'Form to add to the list',
            'checked': False,
            'folder': 'forms',
        },
        {
            'name': 'Task Schedule',
            'description': 'View to manage schedules using a Gantt charts',
            'checked': False,
            'folder': 'schedules'
        },
        {
            'name': 'Tracking',
            'description': 'Generic View to track checkins and tasks.',
            'checked': False,
            'folder': ''
        },
        ]
        for view in predefined:
            view_wdg = DivWdg()
            div.add(view_wdg)
            view_wdg.add_style("margin-left: 5px")
            checkbox = CheckboxWdg("predefined_links")
            name = view.get("name")
            checkbox.set_option("value", name)
            view_wdg.add(checkbox)

            if view.get("checked"):
                checkbox.set_checked()

            view_wdg.add( "&nbsp;&nbsp;%s" % name )

        return div




__all__.append("PredefinedSearchTypesWdg")
class PredefinedSearchTypesWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        top.add_border()
        top.add_color("background", "background")
        #top.add_style("padding: 10px")

        table = Table()
        top.add(table)
        table.add_color("color", "color3")
        table.add_row()

        left = table.add_cell()
        left.add(my.get_stypes_list())
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
        right_div.add(my.get_plugin_info_wdg())

        return top


    def get_plugin_info_wdg(my):
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



    def get_stypes_list(my):

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

    def __init__(my, **kwargs):
        my.kwargs = kwargs

        my.database = kwargs.get('database')
        my.namespace = kwargs.get('namespace')
        my.schema = kwargs.get('schema')

        if not my.database:
            my.project = Project.get()
            my.database = my.project.get_code()
        else:
            # need to have a project with this database name
            # essentially: project == database
            my.project = Project.get_by_code(my.database)

        my.search_type_name = my.get_value("search_type_name") 
        my.db_resource = my.project.get_project_db_resource()
        # Advanced mode: special condition for sthpw/.. sType
        if my.search_type_name.startswith('sthpw/'):
            sql = DbContainer.get('sthpw')
            my.db_resource = sql.get_db_resource()
            my.database = 'sthpw'
            my.namespace = 'sthpw'

        if not my.namespace:
            my.namespace = project_code

        if not my.schema:
            my.schema = 'public'

        super(SearchTypeCreatorCmd,my).__init__(**kwargs)

        my.column_names = my.get_values("column_name")
        if not my.column_names:
            my.column_names = []
        #my.column_types = my.get_values("column_type")
        my.column_types = my.get_values("data_type")
        if not my.column_types:
            my.column_types = []
        my.formats = my.get_values("format")
        if not my.formats:
            my.formats = []

        my.search_type_obj = None

    def get_title(my):
        return "sType Creator"


    def set_database(my, database):
        my.database = database

    def set_schema(my, schema):
        my.schema = schema


    def get_value(my, name):
        web = WebContainer.get_web()

        value = my.kwargs.get(name)
        if not value:
            value = web.get_form_value(name)

        return value

    def get_values(my, name):
        web = WebContainer.get_web()

        value = my.kwargs.get(name)
        if not value:
            value = web.get_form_values(name)

        return value




    def get_sobject(my):
        return my.sobject
        


    def execute(my):
        if not my.database or not my.schema:
            raise CommandException("Either database nor schema is not defined")



        # FIXME: hack this in for now to handle "public"
        if not my.namespace:
            if my.schema == "public":
                my.namespace = my.database
            else:
                my.namespace = "%s/%s" % (my.database,my.schema)

        web = WebContainer.get_web()

        
        if my.search_type_name == "":
            raise CommandExitException("No search type supplied")

        if my.search_type_name.find("/") != -1:
            my.namespace, my.search_type_name = my.search_type_name.split("/", 1)
            # check if it is a valid namespace
            #proj = Project.get_by_code(my.namespace)
            #if not proj:
            #    raise TacticException('[%s] is not a valid namespace'%my.namespace)

        if re.search(r'\W', my.namespace):
            raise TacticException("No special characters or spaces allowed in the namespace of sType.")
        if re.search(r'\W', my.search_type_name):
            raise TacticException("No special characters or spaces allowed in the sType name.")

        #if re.search(r'[A-Z]', my.namespace):
        #    raise TacticException("No upper case letters allowed in the namespace of sType.")
        #if re.search(r'[A-Z]', my.search_type_name):
        #    raise TacticException("No uppercase letters allowed in the sType name.")


        #my.asset_description = web.get_form_value("asset_description")
        my.asset_description = my.get_value("asset_description")
        if my.asset_description == "":
            my.asset_description == "No description"

        #my.asset_title = web.get_form_value("asset_title")
        my.asset_title = my.get_value("asset_title")
        if my.asset_title == "":
            my.asset_title == "No title"

        #copy_from_template = web.get_form_value("copy_from_template")
        copy_from_template = my.get_value("copy_from_template")
        search_type = "%s/%s" % (my.namespace, my.search_type_name)
        

        # don't auto lower it cuz the same sType name may get added to the schema
        #search_type = search_type.lower()

        # Save the newly created search_type to info so we can get it and
        # display it when we are ready to refresh the SearchTypeToolWdg.
        my.info['search_type'] = search_type

        
        my.register_search_type(search_type)
        if not my.search_type_obj:
            my.search_type_obj = SearchType.get(search_type)
        #if web.get_form_value("sobject_pipeline"):
        if my.get_value("sobject_pipeline"):
            my.has_pipeline = True
        else:
            my.has_pipeline = False


        if my.get_value("sobject_preview"):
            my.has_preview = True
        else:
            my.has_preview = False



        #my.parent_type = web.get_form_value("sobject_parent")
        my.parent_type = my.get_value("sobject_parent")

        if not copy_from_template:
            my.create_table()
            # for sthpw sType, create the table only
            if not my.namespace == 'sthpw':
                my.create_config()
                my.create_pipeline()
        else:
            # FIXME: don't copy config yet ... should really copy all
            # ... or have an option
            #my.copy_template_config(copy_from_template)
            my.copy_template_table(copy_from_template)

        
        # add this search_type to the schema for this project
        project_code = Project.get_project_code()
        
        schema = Schema.get_by_code(project_code)

        # if it doesn't exist, then create an empty one
        if not schema:
            schema = Schema.create(project_code, "%s project schema" % project_code )

        if schema:
            schema.add_search_type(search_type, my.parent_type)
            schema.commit()
        else:
            raise CommandException("No schema defined for [%s]" % my.database)


        my.add_sidebar_views()

        my.checkin_preview()

        my.add_naming()
        


    def register_search_type(my, search_type):
        # first check if it already exists
        search = Search( SearchType.SEARCH_TYPE )
        search.add_filter("search_type", search_type)
        test_sobject = search.get_sobject()
        if test_sobject:
            my.search_type_obj = SearchType.get(search_type)
            is_project_specific = my.get_value("project_specific") == "on"
            if my.table_exists() and not is_project_specific:
                msg = "Search type [%s] already exists." % search_type
                if search_type.startswith('sthpw/'):
                    msg = '%s If you are trying to add this to the Project Schema, use the Save button instead of the Register button.'%msg
           
                raise CommandException(msg)
            else: # continue to add table to current project
                return

        
        # create the search type
        sobject = SearchType( SearchType.SEARCH_TYPE )

        sobject.set_value("search_type", search_type)

        sobject.set_value("namespace", my.namespace)

        if my.get_value("project_specific") == "on":
            sobject.set_value("database", my.database)
        else:
            if my.namespace == 'sthpw':
                sobject.set_value("database", "sthpw")
            else:
                sobject.set_value("database", "{project}")


        sobject.set_value("schema", my.schema)

        if my.schema == "public":
            table = my.search_type_name
        else:
            table = "%s.%s" % (my.schema, my.search_type_name)
        sobject.set_value("table_name", table)
        sobject.set_value("class_name", "pyasm.search.SObject")
        sobject.set_value("title", my.asset_title)
        sobject.set_value("description", my.asset_description)

        sobject.commit()

        my.sobject = sobject


    

    def create_config(my):
        search_type = my.search_type_obj.get_base_key()
        columns = SearchType.get_columns(search_type)
        #if my.has_pipeline:
        #    columns.remove("pipeline_code")
        #    columns.append("pipeline")

        # preview is always first
        if my.has_preview:
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

        my.show_code = False
        if not my.show_code:
            columns.remove("code")


        if my.has_preview:
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
                # skip pipeline
                if column in ['pipeline_code'] or column in default_columns:
                    continue

                if column in my.column_names:
                    continue

                element = xml.create_element("element")
                Xml.set_attribute(element, "name", column)
                xml.append_child(view_node, element)


            # handle the custom columns
            for column_name, column_type, format in zip(my.column_names, my.column_types, my.formats):
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
            if my.has_pipeline and view == 'table':
                element = xml.create_element("element")
                Xml.set_attribute(element, "name", "task_edit")
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

            element = xml.create_element("element")
            Xml.set_attribute(element, "name", column)
            #view_node.appendChild(element)
            xml.append_child(view_node, element)



        WidgetDbConfig.create(search_type, view, xml.get_xml() )

      



    def _create_element(my, xml, view_node, name):
        element = xml.create_element("element")
        element.setAttribute("name", name)
        #view_node.appendChild(element)
        xml.append_child(view_node, element)



    def copy_template_table(my, template):
        template_type_obj = SearchType.get(template)
        template_table = template_type_obj.get_table()
        table = my.search_type_obj.get_table()

        database = my.search_type_obj.get_database()

        sql = DbContainer.get(database)
        sql.copy_table_schema(template_table, table)

        # log that this table was creatd
        TableUndo.log(database, table)


    def table_exists(my):
        '''check if table exists'''
        if my.schema == "public":
            table = my.search_type_name
        else:
            table = "%s.%s" % (my.schema, my.search_type_name)
        
        sql = DbContainer.get(my.db_resource)
        impl = sql.get_database_impl()
        exists = impl.table_exists(my.db_resource, table)
        return exists
    

    def create_table(my):

        if my.schema == "public":
            table = my.search_type_name
        else:
            table = "%s.%s" % (my.schema, my.search_type_name)

        if my.namespace == 'sthpw': 
            search_type = "%s/%s" % (my.namespace, my.search_type_name)
        else:    
            search_type = "%s/%s?project=%s" % (my.namespace, my.search_type_name, my.database)
        create = CreateTable(search_type=search_type)

        create.set_table( table )

        # create primary
        create.add("id", "serial", primary_key=True)

        create.add("code", "varchar")
        if my.has_pipeline:
            create.add("pipeline_code", "varchar")


        # add default columns
        create.add("name", "varchar")
        create.add("description", "text")
        create.add("keywords", "text")
        create.add("login", "varchar")
        create.add("timestamp", "timestamp")
        create.add("s_status", "varchar")


        for column_name, column_type in zip(my.column_names, my.column_types):
            if not column_name:
                continue

            data_type = ColumnAddCmd.get_data_type(search_type, column_type)
            create.add(column_name, data_type)
 



        # DEPRECATED
        #create.set_primary_key("id")

        statement = create.get_statement()

        sql = DbContainer.get(my.db_resource)
        database = sql.get_database_name()
        impl = sql.get_database_impl()
        exists = impl.table_exists(my.db_resource, table)
        if exists:
            #raise TacticException('This table [%s] already exists.'%table)
            pass
        else:
            create.commit(sql)
            TableUndo.log(my.search_type_obj.get_base_key(), database, table)

        # add columns 
        db_resource = Project.get_db_resource_by_search_type(search_type)
        sql = DbContainer.get(db_resource)

        # put an index on code
        statement = 'CREATE UNIQUE INDEX "%s_code_idx" ON "%s" ("code")' % (table, table)
        sql.do_update(statement)
        

    def add_sidebar_views(my):
        #search = Search("config/widget_config")
        #search.add_filter("search_type", "SideBarWdg")
        #search.add_filter("view", "project_view")
        #config_sobj = search.get_sobject()

        predefined_links = my.get_values("predefined_links")


        # only need this now that it has been removed from the creator widget
        predefined_links = ['Content List']

        search_type = my.search_type_obj.get_base_key()
        namespace, table = search_type.split("/")
        title = my.search_type_obj.get_title()


        # get the various configs
        # NOT USED, commented out
        """
        if "Add Content Form" in predefined_links:
            # _edit view
            class_name = "tactic.ui.panel.EditWdg"
            display_options = {
                "class_name": class_name,
                "search_type": search_type,
                "view": "edit"
            }
            element_attrs = {
                'title': 'Add %s' % title
            }
            action_options = {}
            action_class_name = {}

            view = "definition"
            element_name = "%s_add" % table
            config = WidgetDbConfig.append( "SideBarWdg", view, element_name, class_name="LinkWdg", display_options=display_options, element_attrs=element_attrs)

            view = "project_view"
            element_name = "%s_add" % table
            config = WidgetDbConfig.append( "SideBarWdg", view, element_name)
        """


        if "Content List" in predefined_links:

            # _list view
            class_name = "tactic.ui.panel.ViewPanelWdg"
            display_options = {
                "class_name": class_name,
                "search_type": search_type,
                "view": "table",
                "layout": "fast_table"
            }
            element_attrs = {
                #'title': '%s List' % title
                'title': title
            }
            action_options = {}
            action_class_name = {}

            view = "definition"
            element_name = "%s_list" % table

            config = WidgetDbConfig.append( "SideBarWdg", view, element_name, class_name="LinkWdg", display_options=display_options, element_attrs=element_attrs)

            view = "project_view"
            element_name = "%s_list" % table
            config = WidgetDbConfig.append( "SideBarWdg", view, element_name)

        """
        if "Task Schedule" in predefined_links:

            # this is rather complicated
            view = 'project_view'
            element_name = '%s_tasks' % table

            element_attrs = {
                'title': '%s Tasks' % title,
                'icon': 'DATE'
            }

            display_options = {
                'search_type': 'sthpw/task',
                'view': 'table',
                'state': '<search_type>%s</search_type>' % search_type,
                'filter': '''[{"prefix":"main_body","main_body_enabled":"on","main_body_column":"project_code","main_body_relation":"is","main_body_value":"{$PROJECT}"},{"prefix":"main_body","main_body_enabled":"on","main_body_column":"search_type","main_body_relation":"starts with","main_body_value":"%s?"}, {"prefix": "group", "group": "true", "order": "parent"}]''' % search_type

            }


            config = WidgetDbConfig.append( "SideBarWdg", view, element_name, class_name="LinkWdg", display_options=display_options, element_attrs=element_attrs)
        """


        """
        if "Tracking" in predefined_links:

            class_name = "tactic.ui.panel.ViewPanelWdg"
            display_options = {
                "class_name": class_name,
                "search_type": search_type,
                "view": "tracking"
            }
            element_attrs = {
                'title': '%s Tracking' % title
            }
            action_options = {}
            action_class_name = {}

            view = "definition"
            element_name = "%s_tracking" % table

            config = WidgetDbConfig.append( "SideBarWdg", view, element_name, class_name="LinkWdg", display_options=display_options, element_attrs=element_attrs)

            xml = '''
<config>
  <tracking layout="TableLayoutWdg" >
    <element name="preview"/>
    <element name="code"/>
    <element name="explorer"/>
    <element name="general_checkin"/>
    <element name="history"/>
    <element name="task_edit"/>
    <element name="task_status_edit"/>
  </tracking>
</config>
'''
            config = SearchType.create("config/widget_config")
            config.set_value("config", xml)
            config.set_value("search_type", search_type)
            config.set_value("view", "tracking")
            config.commit()




            view = "project_view"
            element_name = "%s_tracking" % table
            config = WidgetDbConfig.append( "SideBarWdg", view, element_name)

        """


    def create_pipeline(my):

        if not my.has_pipeline:
            return

        search_type = my.search_type_obj.get_base_key()
        namespace, table = search_type.split("/")
        project_code = Project.get_project_code()

        pipeline_code = "%s/%s" % (project_code, table)

        # create a pipeline
        search = Search("sthpw/pipeline")
        search.add_filter("code", pipeline_code)
        pipeline = search.get_sobject()

        # TODO: check for search types??
        if pipeline:
            return


        processes = my.get_values("process")
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



 
    def checkin_preview(my):
        # if there is an image, check it in
        image_path = my.get_values("image_path")
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
            checkin = FileCheckin(my.search_type_obj, context='icon', file_paths=file_paths, file_types=file_types)
            checkin.execute()



    def add_naming(my):

        naming_expr = my.get_value("naming")

        if naming_expr == "_CUSTOM":
            naming_expr = my.get_value("custom_naming")

        if not naming_expr or naming_expr == "_DEFAULT":
            naming_expr = "{project.code}/{search_type.table_name}/{sobject.code}"

        # fix the slashes
        naming_expr = naming_expr.strip("/")

        naming = SearchType.create("config/naming")
        naming.set_value("dir_naming", naming_expr)

        search_type = my.search_type_obj.get_base_key()
        naming.set_value("search_type", search_type)
        naming.commit()





