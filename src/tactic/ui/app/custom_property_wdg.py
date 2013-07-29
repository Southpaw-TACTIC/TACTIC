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

__all__ = ['CustomPropertyAdderWdg', 'CustomPropertyAdderCbk']

from pyasm.common import Environment, TacticException, Xml, Common
from pyasm.biz import Project
from pyasm.command import Command, ColumnAddCmd
from pyasm.search import WidgetDbConfig, SearchType, Search
from pyasm.web import WebContainer, DivWdg, SpanWdg, Table, HtmlElement
from pyasm.widget import HiddenWdg, TextWdg, SelectWdg, TextAreaWdg, CheckboxWdg, WidgetConfigView

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg


TEMPLATE_VIEW = "custom"
DEFAULT_VIEW = "definition"
PREDEFINED_ELEMENTS = ['history', 'info', 'preview', 'thumb_publish', 'notes','publish', 'task_list', 'task_status', 'update']
PREDEFINED_EDIT_ELEMENTS = ['preview']

def get_template_view():
    user = Environment.get_user_name()
    view = "%s_%s" % (TEMPLATE_VIEW, user)
    return view


class CustomPropertyAdderWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'The search type that this property will be added to',
        'view': 'The current view',
        'is_aux_title': 'True if it is in title mode'
        }

    def init(my):
        my.search_type = my.kwargs.get('search_type')
        assert my.search_type
        my.view = my.kwargs.get("view")
        my.is_aux_title = my.kwargs.get("is_aux_title")
    
    def get_display(my):
        web = WebContainer.get_web()

        database = Project.get_project_code()
        
        if my.is_aux_title == 'true':
            return HtmlElement.b("Add Property for %s [%s]" \
                %(SearchType.get(my.search_type).get_title(), my.search_type))
        
        
        if not my.view:
            my.view = get_template_view()
        

        # show current custom
        div = DivWdg(id="add_property_wdg")
        div.add_class("spt_panel")

        div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

spt.custom_property_adder = {}


// Called when a type selection is made when creating a new property type
spt.custom_property_adder.property_type_select_cbk = function(el) {
    var panel = el.getParent(".spt_panel");
    var kwargs = { top_el: panel };

    spt.simple_display_hide('.foreign_key_options', kwargs);
    spt.simple_display_hide('.list_options', kwargs);
    spt.simple_display_hide('.button_options', kwargs);


    if (el.value == "foreign_key") {
        spt.simple_display_show('.foreign_key_options', kwargs);
    }
    else if (el.value == "list") {
        spt.simple_display_show('.list_options', kwargs);
    }
    else if (el.value == "button") {
        spt.simple_display_show('.button_options', kwargs);
    }
}




// called when the mode of "add property" is switched"
spt.custom_property_adder.switch_property_mode = function(evt, bvr) {
    var src_el = bvr.src_el;
    var value = src_el.value;

    var panel = src_el.getParent(".spt_panel")

    var element = panel.getElement(".spt_custom_simple")
    spt.simple_display_hide(element);
    //var element = panel.getElement(".spt_custom_widget")
    //spt.simple_display_hide(element);
    var element = panel.getElement(".spt_custom_xml")
    spt.simple_display_hide(element);

    var element = panel.getElement(".spt_custom_" + value)
    spt.simple_display_show(element);
}


spt.custom_property_adder.add_property_cbk = function(evt, bvr) {

    var search_type = bvr['search_type'];
    var view = bvr['view'];
    var exit = bvr['exit'];

    var panel = bvr.src_el.getParent(".spt_panel");
    var popup = bvr.src_el.getParent(".spt_popup");

    var mode = panel.getElement(".spt_custom_mode").value;
    var input_top = panel.getElement(".spt_custom_"+mode);
    var values = spt.api.Utility.get_input_values(input_top);

    // add the mode value
    values['custom_mode'] = mode;

    var class_name = "tactic.ui.app.CustomPropertyAdderCbk";
    var options = {
        'search_type': search_type,
        'view': view
    };

    var server = TacticServerStub.get();
    try {
        server.start({title:"Add new property"});
        var response = server.execute_cmd(class_name, options, values);
        if (exit == "true") {

            $('add_property_wdg').setStyle("display", "none");
            // this may or may not exist
            if (popup)
                spt.popup.close(popup);
        }
        else {
            // erase all of the inputs
            for (var i = 0; i < input_list.length; i++) {
                var filter = input_list[i];
                filter.value = "";
            }
        }
        var st_view = "definition";
        spt.panel.refresh("ManageSearchTypeMenuWdg_" + st_view);

        var st_view = 'db_column';
        spt.panel.refresh("ManageSearchTypeMenuWdg_" + st_view);
    }
    catch (e) {
        server.abort();
        alert(spt.exception.handler(e));
    }

}


            '''
        } )




        div.add_style("padding: 10px")
        div.add_color("color", "color")
        div.add_color("background", "background")
        div.add_border()

        div.add( my.get_new_custom_widget(my.search_type, my.view) )


        return div


    def get_new_custom_widget(my, search_type, view):

        div = DivWdg()
        div.add_style('width: 500px')
        
        mode_select = SelectWdg("custom_mode")
        mode_select.add_class("spt_custom_mode")
        mode_select.set_option("values", "simple|xml")
        mode_select.set_option("labels", "Simple|XML")
        mode_select.add_class("spt_input")
        behavior = {
            'type': 'change',
            'cbfn_action': 'spt.custom_property_adder.switch_property_mode'
        }
        mode_select.add_behavior(behavior)

        div.add("Mode: ")
        div.add(mode_select)
        div.add("<br/><br/>")


        custom_table = Table()
        custom_table.add_color("color", "color")

        custom_table.set_max_width()
        mode = "simple"
        my.handle_simple_mode(custom_table, mode)
        #my.handle_widget_mode(custom_table, mode)
        my.handle_xml_mode(custom_table, mode)
        div.add(custom_table)

        div.add("<br/>")

        custom_table = Table()
        custom_table.center()
        custom_table.add_row()


        from tactic.ui.widget import ActionButtonWdg
        submit = ActionButtonWdg(title="Add/Next")
        behavior = {
            'type': 'click',
            'mouse_btn': 'LMB',
            'cbfn_action': 'spt.custom_property_adder.add_property_cbk',
            'search_type': my.search_type,
            'view': view

        }
        submit.add_behavior(behavior)
        td = custom_table.add_cell(submit)

        behavior['exit'] = 'true'
        submit_exit = ActionButtonWdg(title="Add/Exit")
        submit_exit.add_behavior(behavior)
        custom_table.add_cell(submit_exit)

        cancel = ActionButtonWdg(title="Cancel")
        behavior = {
            'type': 'click_up',
            'cbjs_action': "spt.popup.close('New Table Column')"
        }
        cancel.add_behavior(behavior)
        custom_table.add_cell(cancel)

        div.add(custom_table)

        return div



    def handle_simple_mode(my, custom_table, mode):

        tbody = custom_table.add_tbody()
        tbody.add_class("spt_custom_simple")
        if mode != 'simple':
            tbody.add_style('display: none')


        name_text = TextWdg("custom_name")
        name_text.add_class("spt_input")
        tr = custom_table.add_row()
        tr.add_color("background", "background", -7)
        td = custom_table.add_cell("Name: ")
        td.add_style("min-width: 150px")
        custom_table.add_cell(name_text)


        # add title
        custom_table.add_row()
        title_wdg = TextWdg("custom_title")
        title_wdg.add_attr("size", "50")
        custom_table.add_cell( "Title: " )
        custom_table.add_cell( title_wdg )

        # add description
        tr = custom_table.add_row()
        tr.add_color("background", "background", -7)
        description_wdg = TextAreaWdg("custom_description")
        custom_table.add_cell( "Description: " )
        custom_table.add_cell( description_wdg )


        type_select = SelectWdg("custom_type")
        type_select.add_class("spt_input")
        #type_select.add_empty_option("-- Select --")
        type_select.set_option("values", "string|text|integer|float|boolean|currency|date|foreign_key|list|button|empty")
        type_select.set_option("labels", "String(db)|Text(db)|Integer(db)|Float(db)|Boolean(db)|Currency(db)|Date(db)|Foreign Key(db)|List(db)|Button|Empty")
        #type_select.set_option("labels", "String|Integer|Boolean|Currency|Timestamp|Link|Foreign Key|List|Checkbox|Text|Number|Date|Date Range")
        tr = custom_table.add_row()
        custom_table.add_cell("Property Type: ")
        td = custom_table.add_cell(type_select)
        type_select.add_event("onchange", "spt.custom_property_adder.property_type_select_cbk(this)")



        # extra info for foreign key
        custom_table.add_row()
        div = DivWdg()
        div.add_class("foreign_key_options")
        div.add_style("display: none")
        div.add_style("margin-top: 10px")
        div.add("Options")
        div.add(HtmlElement.br())
        # TODO: this class should not be in prod!!
        from pyasm.prod.web import SearchTypeSelectWdg
        div.add("Relate to: ")
        search_type_select = SearchTypeSelectWdg("foreign_key_search_select", mode=SearchTypeSelectWdg.CURRENT_PROJECT)
        div.add(search_type_select)
        td.add(div)



        # extra info for list
        custom_table.add_row()
        div = DivWdg()
        div.add_class("list_options")
        div.add_style("display: none")
        div.add_style("margin-top: 10px")
        div.add("Options")
        div.add(HtmlElement.br())
        # TODO: this class should not be in prod!!
        from pyasm.prod.web import SearchTypeSelectWdg
        div.add("Values: ")
        search_type_text = TextWdg("list_values")
        div.add(search_type_text)
        td.add(div)




        # extra info for button
        custom_table.add_row()
        div = DivWdg()
        div.add_class("button_options")
        div.add_style("display: none")
        div.add_style("margin-top: 10px")

        class_path = "tactic.ui.table.ButtonElementWdg"
        button = Common.create_from_class_path(class_path)
        args_keys = button.get_args_keys()


        div.add("Options")
        div.add(HtmlElement.br())

        for key in args_keys.keys():
            div.add("Name: ")
            option_name_text = TextWdg("option_name")
            option_name_text.add_attr("readonly", "true")
            option_name_text.set_value(key)
            div.add(option_name_text)

            div.add(" &nbsp; ")

            div.add("Value: ")
            input = button.get_input_by_arg_key(key)
            div.add(input)

            #option_value_text = TextWdg("option_value")
            #div.add(option_value_text)
            div.add(HtmlElement.br())
        td.add(div)






        # is searchable checkbox
        tr = custom_table.add_row()
        tr.add_color("background", "background", -7)
        current_searchable_wdg = CheckboxWdg("is_searchable")
        #current_view_wdg.set_checked()
        custom_table.add_cell("Is Searchable? ")
        td = custom_table.add_cell(current_searchable_wdg)

        custom_table.close_tbody()







    def handle_widget_mode(my, custom_table, mode):

        tbody = custom_table.add_tbody()
        tbody.add_class("spt_custom_widget")
        if mode != 'widget':
            tbody.add_style('display: none')

        # add the name
        name_text = TextWdg("custom_name")
        name_text.add_class("spt_input")
        custom_table.add_row()
        custom_table.add_cell("Name: ")
        custom_table.add_cell(name_text)

        # add title
        custom_table.add_row()
        title_wdg = TextWdg("custom_title")
        title_wdg.add_attr("size", "50")
        custom_table.add_cell( "Title: " )
        custom_table.add_cell( title_wdg )

        # add description
        custom_table.add_row()
        description_wdg = TextAreaWdg("custom_description")
        custom_table.add_cell( "Description: " )
        custom_table.add_cell( description_wdg )


        # add widget class
        custom_table.add_row()
        class_wdg = TextWdg("custom_class")
        class_wdg.add_attr("size", "50")
        custom_table.add_cell( "Widget Class: " )
        custom_table.add_cell( class_wdg )


        # add options
        custom_table.add_row()
        td = custom_table.add_cell()
        td.add("Options")
        td = custom_table.add_cell()

        div = DivWdg()
        div.set_id("another_list_options")
        div.add_style("display: block")
        div.add_style("margin-top: 10px")
        # TODO: this class should not be in prod!!
        from pyasm.prod.web import SearchTypeSelectWdg

        div.add("Name: ")
        option_name_text = TextWdg("option_name")
        div.add(option_name_text)

        div.add(" &nbsp; ")

        div.add("Value: ")
        option_value_text = TextWdg("option_value")
        div.add(option_value_text)

        td.add(div)
        td.add(div)
        td.add(div)

        custom_table.close_tbody()


    def handle_xml_mode(my, custom_table, mode):

        tbody = custom_table.add_tbody()
        tbody.add_class("spt_custom_xml")
        if mode != 'xml':
            tbody.add_style('display: none')

        # extra for custom config_xml
        custom_table.add_row()

        td = custom_table.add_cell()
        td.add("Config XML Definition")


        div = DivWdg()
        div.set_id("config_xml_options")
        #div.add_style("display: none")
        div.add_style("margin-top: 10px")


        default = '''
<element name=''>
  <display class=''>
    <option></option>
  </display>
</element>
        '''
        config_xml_wdg = TextAreaWdg("config_xml")
        config_xml_wdg.set_option("rows", "8")
        config_xml_wdg.set_option("cols", "50")
        config_xml_wdg.set_value(default)
        div.add( config_xml_wdg )

        custom_table.add_cell(div)

        # create columns
        custom_table.add_row()
        td = custom_table.add_cell()
        create_columns_wdg = CheckboxWdg("create_columns")
        create_columns_wdg.set_checked()
        td.add("Create required columns? ")

        td = custom_table.add_cell()
        td.add(create_columns_wdg)


        custom_table.close_tbody()






class CustomPropertyAdderCbk(Command):

    def get_args_keys(my):
        return {
        'search_type': 'the search type that this command will operate on',
        'view': 'the current view',
        }


    def get_title(my):
        return "Custom Add Property"

    def execute(my):

        web = WebContainer.get_web()

        # get command line options
        search_type = my.kwargs.get("search_type")
        assert search_type

        view = my.kwargs.get("view")
        if not view:
            view = get_template_view()



        # check if this is advanced mode
        mode = web.get_form_value("custom_mode")
        if not mode:
            mode = 'simple'

        if mode == 'xml':
            config_string = web.get_form_value("config_xml")

            # handle the "default" view
            view = DEFAULT_VIEW
            config = WidgetDbConfig.get_by_search_type(search_type, view)
            if not config:
                config = WidgetDbConfig.create(search_type, view)

            xml = Xml()
            xml.read_string(config_string)
            element_name = xml.get_value("element/@name")
            element_name = element_name.strip()
            assert element_name

            type = xml.get_value("element/@type")
            if not type:
                class_name = xml.get_value("element/display/@class")

                if not class_name:
                    raise TacticException("Either a type or class name needs to be defined in config xml.")

            config.append_xml_element(element_name,config_string)
            config.commit_config()

            # create the required columns
            widget = config.get_display_widget(element_name)
            columns = widget.get_required_columns()

            if columns:
                print "WARNING: need to create columns: ", columns

            my.info['element_name'] = element_name

            return



        type = web.get_form_value("custom_type")
        description = web.get_form_value("custom_description")
        if not description:
            description = "No descripton"

        title = web.get_form_value("custom_title")



        name = web.get_form_value("custom_name")
        name = name.strip()
        if not name:
            raise TacticException("No name specified")


        add_to_current_view = web.get_form_value("add_to_current_view")
        add_to_edit_view = web.get_form_value("add_to_edit_view")
        is_searchable = web.get_form_value("is_searchable")

        # create the column
        if type not in ['button', 'empty']:
            cmd = ColumnAddCmd(search_type, name, type)
            cmd.execute()

        
        # create the type
        class_name = None
        options = {}
        # this is actually element attrs
        element_options = {}
        edit_class_name = None
        edit_options = {}
        edit_attrs = {}

        element_type = type

        # Date Range is not used any more in the UI"
        if type == "Date Range":
            class_name = "GanttWdg"
            options["start_date_column"] = "%s_start_date" % name
            options["end_deate_column"] = "%s_end_date" % name

        elif type == "date":
            class_name = "DateWdg"
            #edit_class_name = "CalendarWdg"

            element_type = 'timestamp'
            edit_attrs['type'] = 'timestamp'
            edit_class_name = ""
            add_to_edit_view = True

        elif type == "foreign_key":
            class_name = ""
            edit_class_name = "SelectWdg"
            foreign_search_type = web.get_form_value("foreign_key_search_select")
            edit_options["query"] = '%s|code|code' % foreign_search_type

            # turn on add to edit view
            add_to_edit_view = True

        elif type == "button":
            class_name = "tactic.ui.table.ButtonElementWdg"
            script = web.get_form_value("option_script_select")
            if script:
                options['script'] = script
            icon = web.get_form_value("option_icon_select")
            if icon:
                options['icon'] = icon


            edit_class_name = ""

            # This does not have a type
            element_type = None


        elif type == "empty":
            element_type = None
            pass


        elif type == "list":
            class_name = ""
            edit_class_name = "SelectWdg"
            list_values = web.get_form_value("list_values")
            edit_options['values'] = list_values

            add_to_edit_view = True

        element_options['type'] = element_type
        element_options['title'] = title
        

        # handle the "default" view
        view = DEFAULT_VIEW
        config = WidgetDbConfig.get_by_search_type(search_type, view)
        if not config:
            config = WidgetDbConfig.create(search_type, view)
        config.append_display_element(name, class_name, options=options, \
                element_attrs=element_options)
        config.commit_config()


        # get the config file
        if add_to_current_view:
            config = WidgetDbConfig.get_by_search_type(search_type, view)

            if not config:
                # if it doesn't exist, the check to see, if there is a hard
                # coded view out there
                predefined_config = WidgetConfigView.get_by_search_type(search_type, view)
                xml = predefined_config.get_xml()

                # create a new db one
                config = WidgetDbConfig.create(search_type, view)

                if xml:
                    config.set_value("config", xml.to_string())
                    config._init()

            config.append_display_element(name)
            config.commit_config()

        # TODO: Need to make this searchable using simple search ?????
        if is_searchable:
            element_options['searchable'] = 'true'

        # handle the "edit"
        if add_to_edit_view and view != "edit":
            config = WidgetDbConfig.get_by_search_type(search_type, "edit")
            if not config:
                config = WidgetDbConfig.create(search_type, "edit")
            config.append_display_element(name, edit_class_name, edit_options,element_attrs=edit_attrs)
            config.commit_config()


        """
        # this sType has been deprecated
        sobject = SearchType.create("prod/custom_property")
        sobject.set_value("search_type", search_type)
        sobject.set_value("name", name)
        sobject.set_value("description", description)
        sobject.commit()
        """

        # set some information
        my.description = "Added Property [%s] of type [%s] to [%s]" % \
            (name, type, search_type)

        my.info['element_name'] = name





