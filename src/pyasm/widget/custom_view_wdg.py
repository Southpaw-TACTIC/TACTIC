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

__all__ = ['CustomViewWdg', 'CustomViewAction','CustomAddPropertyWdg', 'CustomAddPropertyCbk', 'CustomCreateViewCbk', 'CsvDownloadWdg', 'CsvGenerator', 'CustomAddPropertyLinkWdg', 'CustomEditViewPopupWdg', 'CustomAddElementWdg']

import os
from pyasm.common import *
from pyasm.command import *
from pyasm.biz import Project
from pyasm.search import WidgetDbConfig, SearchType, SObjectFactory, Search
from pyasm.web import *
from pyasm.widget import BaseTableElementWdg, BaseInputWdg, TextWdg, WidgetConfigView, WidgetConfig, BaseConfigWdg, HintWdg, PopupWdg, PopupMenuWdg, IconWdg, IconSubmitWdg, IconButtonWdg, TextWdg, HiddenWdg, CheckboxWdg, SelectWdg, GeneralFilterWdg, TextAreaWdg, EditLinkWdg, FilterSelectWdg
from tactic.ui.common import BaseRefreshWdg

TEMPLATE_VIEW = "custom"
DEFAULT_VIEW = "definition"
PREDEFINED_ELEMENTS = ['history', 'info', 'preview', 'thumb_publish', 'notes','publish', 'task_list', 'task_status','repo_action_wdg', 'update' ]
PREDEFINED_EDIT_ELEMENTS = ['preview']

def get_template_view():
    user = Environment.get_user_name()
    view = "%s_%s" % (TEMPLATE_VIEW, user)
    return view


class CustomViewWdg(Widget):

    '''Provides the ability to create custom view for sobjects'''
    def __init__(my, search_type):
        my.search_type = search_type
        my.mode = "admin"
        super(CustomViewWdg,my).__init__()

    def set_mode(my, mode):
        my.mode = mode


    def get_display(my):
        if not my.search_type:
            return "No search type found"

        web = WebContainer.get_web()
        my.view = web.get_form_value("view")
        if not my.view:
            my.view = web.get_form_value("filter|view")
        if not my.view:
            my.view = get_template_view()

        widget = Widget()

        widget.add( HiddenWdg("search_type", my.search_type) )

        element_names = []

        # see if there is an override
        search_type_obj = SearchType.get(my.search_type)  
        config = WidgetConfigView.get_by_search_type(my.search_type,"browser_list")
        if config:
            element_names = config.get_element_names()


        search = Search("sthpw/widget_config")
        search.add_filter("search_type", my.search_type)
        search.add_filter("view", my.view)
        widget_config = search.get_sobject()
        if widget_config:
            edit_link_wdg = EditLinkWdg("sthpw/widget_config", widget_config.get_id(), text="Edit XML", long=True)
            edit_link_wdg.set_iframe_width(95)
            widget.add(edit_link_wdg)


        custom_config = WidgetConfigView.get_by_search_type(my.search_type,my.view)
        custom_element_names = custom_config.get_element_names()


        # get the custom properties
        search = Search("prod/custom_property")
        search.add_filter("search_type", my.search_type)
        custom_properties = search.get_sobjects()


        # action popup
        action_popup = PopupMenuWdg("table_action", multi=True, width='12em')
        action_popup.set_auto_hide(False)
        action_popup.set_submit(False)

        
        action_popup.add( HtmlElement.href("Add ...", "javascript:document.form.submit()") )


        for custom_property in custom_properties:
            element_name = custom_property.get_name()
            if element_name not in custom_element_names:
                action_popup.add( " %s" % element_name, "add|%s" % element_name )

        # if there is an override
        if element_names:
            for element_name in element_names:
                if element_name not in custom_element_names:
                    action_popup.add( " %s" % element_name, "add|%s" % element_name )


        # get all of the columns
        else:
            search_type_obj = SearchType.get(my.search_type)
            element_names = search_type_obj.get_columns()

            for element_name in element_names:
                if element_name not in custom_element_names:
                    action_popup.add( " %s" % element_name, "add|%s" % element_name )

            # add some standard properties
            if my.view in ["edit", "insert"]:
                for element_name in PREDEFINED_EDIT_ELEMENTS:
                    if element_name not in custom_element_names:
                        action_popup.add( " %s" % element_name, "add|%s" % element_name )
            else:
                for element_name in PREDEFINED_ELEMENTS:
                    if element_name not in custom_element_names:
                        action_popup.add( " %s" % element_name, "add|%s" % element_name )

        action_popup.add_separator()
        action_popup.add( HtmlElement.href("Remove ...", "javascript:document.form.submit()") )
        for element_name in custom_element_names:
            action_popup.add( " %s" % element_name, "remove|%s" % element_name )
        action_popup.add_separator()

        span = SpanWdg("New Custom ...", css="hand")
        iframe = WebContainer.get_iframe()
        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "pyasm.widget.CustomAddPropertyWdg")
        url.set_option("search_type", my.search_type)
        url.set_option("view", my.view)
        action = iframe.get_on_script(url.to_string() )
        span.add_event("onclick", action)
        action_popup.add( span )


        # add the edit button
        edit = IconButtonWdg("Edit View", IconWdg.EDIT, True)

        edit.add_event("oncontextmenu", "%s;return false" % action_popup.get_on_script() )
        edit.add_event("onclick", "%s" % action_popup.get_on_script() )



        # lay it all out
        widget.add(SpanWdg(action_popup))
        widget.add(edit)

        # add the edit button
        #save = IconButtonWdg("Save", IconWdg.SAVE, True)
        #widget.add(save)

        # add the add property button
        if my.mode == "admin":
            add = CustomAddPropertyLinkWdg(my.search_type, my.view)
            widget.add(add)
            #add_element = CustomAddElementLinkWdg(my.search_type, my.view)
            #widget.add(add_element)


        # add the clear button
        if my.mode == "admin" or my.view.startswith("custom_"):
            clear = IconSubmitWdg("Clear", IconWdg.DELETE, True)
            widget.add(clear)

        
        widget.add(SpanWdg(css="small"))


        WebContainer.register_cmd("pyasm.widget.CustomViewAction")

        return widget



class CustomViewAction(Command):

    def get_title(my):
        return "Custom View"

    def execute(my):

        web = WebContainer.get_web()
        actions = web.get_form_values("table_action_hidden")
        if not actions:
            clear = web.get_form_value("Clear")
            if clear:
                actions = ["clear"]

        if not actions:
            return

        search_type = web.get_form_value("search_type")
        assert search_type

        view = web.get_form_value("view")
        if not view:
            view = web.get_form_value("filter|view")
        if not view:
            view = get_template_view()
       
        for action in actions:

            parts = action.split("|")
            action = parts[0]

            if action not in ['add', 'remove', 'clear', 'move_left', 'move_right']:
                print "WARNING: action [%s] not known" % action
                return

            # get the view config 
            search = Search("sthpw/widget_config")
            search.add_filter("search_type", search_type)
            search.add_filter("view", view)
            config = search.get_sobject()
            if not config:
                config = WidgetDbConfig.create(search_type, view)

            

            
            if action == "add":
                elem_name = parts[1]

                # FIXME: these should be coded as defaults somewhere
                options = {}
                cls_name = None
                if elem_name == "notes":
                    cls_name = "DiscussionWdg"
                    options['context'] = 'default'
                elif elem_name == "thumb_publish":
                    cls_name = "pyasm.prod.web.ThumbPublishWdg"


                config.append_display_element(elem_name, cls_name, options)
                config.commit_config()

                # handle some defaults
                if elem_name in PREDEFINED_ELEMENTS and \
                        elem_name not in PREDEFINED_EDIT_ELEMENTS:
                    continue

                #edit_config.append_display_element(elem_name)
                #edit_config.commit_config()

                my.description = "Added [%s] to [%s] view" % (elem_name, view)

            elif action == "remove":
                elem_name = parts[1]
                config.remove_display_element(elem_name)
                config.commit_config()

                #edit_config.remove_display_element(elem_name)
                #edit_config.commit_config()

                my.description = "Removed [%s] from [%s] view" % (elem_name, view)

            elif action == "clear":
                config.clear()
                config.commit_config()

                # TODO: not sure what to do about the edit config on clear??

                my.description = "Cleared view [%s]" % (view)


            elif action == "move_left":
                elem_name = parts[1]
                config.move_element_left(elem_name)
                config.commit_config()
                my.description = "Removed [%s] to the left" % elem_name

            elif action == "move_right":
                elem_name = parts[1]
                config.move_element_right(elem_name)
                config.commit_config()
                my.description = "Removed [%s] to the right" % elem_name


            elif action == "order_by":
                print "order by!!!"



class CustomAddPropertyWdg(BaseInputWdg):
    def get_display(my):
        web = WebContainer.get_web()

        if web.get_form_value("Insert/Exit"):
            widget = Widget()
            iframe = WebContainer.get_iframe()
            widget.add( HtmlElement.script(iframe.get_off_script()) )
            widget.add( HtmlElement.script("window.parent.document.form.submit()") )
            return widget


        database = Project.get_project_code()
        search_type = web.get_form_value("search_type")
        assert search_type

        view = web.get_form_value("view")
        if not view:
            view = get_template_view()
        
        widget = DivWdg()

        WebContainer.register_cmd("pyasm.widget.CustomAddPropertyCbk")

        # remember some parameters
        widget.add( HiddenWdg("search_type", search_type) )
        widget.add( HiddenWdg("view", view) )

        # Get the definition widget and list all of the custom elements
        #config = WidgetConfigView.get_by_search_type(search_type,DEFAULT_VIEW)
        #element_names = config.get_element_names()

        # show current custom
        widget.add("<h3>Add Property for [%s]</h3>" % search_type)

        widget.add( my.get_new_custom_widget(view) )

        return widget


    def get_new_custom_widget(my, view):

        custom_table = Table(css="table")
        name_text = TextWdg("new_custom_name")
        custom_table.add_row()
        custom_table.add_cell("Name: ")
        custom_table.add_cell(name_text)

        type_select = SelectWdg("new_custom_type")
        #type_select.add_empty_option("-- Select --")
        type_select.set_option("values", "Name/Code|Foreign Key|List|Checkbox|Text|Number|Date|Date Range")
        custom_table.add_row()
        custom_table.add_cell("Predefined Type: ")
        td = custom_table.add_cell(type_select)
        td.add( HtmlElement.script('''
        function property_type_select(el) {
            if (el.value == "Foreign Key") {
                set_display_on('foreign_key_options')
            }
            else if (el.value == "List") {
                set_display_on('list_options')
            }
            else {
                set_display_off('foreign_key_options')
                set_display_off('list_options')
            }
        }
        ''') )
        type_select.add_event("onchange", "property_type_select(this)")


        # extra info for foreign key
        custom_table.add_row()
        div = DivWdg()
        div.set_id("foreign_key_options")
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


        # extra info for foreign key
        custom_table.add_row()
        div = DivWdg()
        div.set_id("list_options")
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


        #custom_table.add_row()
        #private_wdg = CheckboxWdg("new_private")
        #custom_table.add_cell("Make Private: ")
        #custom_table.add_cell(private_wdg)

        # add options
        #custom_table.add_row()
        #description_wdg = TextAreaWdg("new_options")
        #custom_table.add_cell( "Options: " )
        #custom_table.add_cell( description_wdg )


        custom_table.add_row()
        description_wdg = TextAreaWdg("new_description")
        custom_table.add_cell( "Description: " )
        custom_table.add_cell( description_wdg )

        # add to current view
        if view not in ['edit', 'insert']:
            custom_table.add_row()
            current_view_wdg = CheckboxWdg("add_to_current_view")
            current_view_wdg.set_checked()
            custom_table.add_cell("Add To Current View: ")
            td = custom_table.add_cell(current_view_wdg)

        
        # add to edit view
        custom_table.add_row()
        edit_view_wdg = CheckboxWdg("add_to_edit_view")
        edit_view_wdg.set_checked()
        custom_table.add_cell("Add To Edit View: ")
        custom_table.add_cell(edit_view_wdg)

        custom_table.add_row()
        custom_table.add_blank_cell()
        custom_table.add_cell(SpanWdg('If you check this for a search type already in the system, it will create an edit view that overrides the built-in edit view. This may affect its editability. You can always delete the edit view in the Configure Widgets tab afterwards.', css='warning smaller'))

        from pyasm.prod.web import ProdIconSubmitWdg, ProdIconButtonWdg
        submit = ProdIconSubmitWdg("Insert/Next")
        tr, td = custom_table.add_row_cell(submit)
        td.add_style("text-align: center")

        submit = ProdIconSubmitWdg("Insert/Exit")
        td.add(submit)

        iframe = WebContainer.get_iframe()
        cancel = ProdIconButtonWdg("Cancel")
        iframe_close_script = "window.parent.%s" % iframe.get_off_script() 
        cancel.add_event("onclick", iframe_close_script)


        td.add(cancel)
        
        return custom_table


class CustomAddPropertyCbk(Command):

    def get_title(my):
        return "Custom Add Property"

    def execute(my):
        web = WebContainer.get_web()
        if not web.get_form_value("Insert/Next") and not web.get_form_value("Insert/Exit"):
            return


        search_type = web.get_form_value("search_type")
        view = web.get_form_value("view")
        project = web.get_form_value("project")
        name = web.get_form_value("new_custom_name")
        if not name:
            raise TacticException("No name specified")
        type = web.get_form_value("new_custom_type")
        description = web.get_form_value("new_description")
        add_to_current_view = web.get_form_value("add_to_current_view")
        add_to_edit_view = web.get_form_value("add_to_edit_view")

        assert search_type

        if not view:
            view = get_template_view()

        # create the column
        cmd = ColumnAddCmd(search_type, name, type)
        cmd.execute()

        # create the type
        class_name = None
        options = {}
        edit_class_name = None
        edit_options = {}

        if type == "Date Range":
            class_name = "GanttWdg"
            options["start_date_column"] = "%s_start_date" % name
            options["end_date_column"] = "%s_end_date" % name
        elif type == "Date":
            class_name = "DateWdg"
            edit_class_name = "CalendarWdg"
        elif type == "Checkbox":
            class_name = "CheckTableElementWdg"
            edit_class_name = "CheckboxWdg"
        elif type == "Foreign Key":
            class_name = ""
            edit_class_name = "SelectWdg"
            foreign_search_type = web.get_form_value("foreign_key_search_select")
            edit_options["query"] = '%s|code|code' % foreign_search_type
        elif type == "List":
            class_name = ""
            edit_class_name = "SelectWdg"
            list_values = web.get_form_value("list_values")
            edit_options['values'] = list_values




        # get the config file
        if add_to_current_view:
            config = WidgetDbConfig.get_by_search_type(search_type, view)
            if not config:
                config = WidgetDbConfig.create(search_type, view)
            config.append_display_element(name)
            config.commit_config()

        # handle the "default" view
        view = DEFAULT_VIEW
        config = WidgetDbConfig.get_by_search_type(search_type, view)
        if not config:
            config = WidgetDbConfig.create(search_type, view)
        config.append_display_element(name, class_name, options)
        config.commit_config()


        # handle the "edit"
        if add_to_edit_view and view != "edit":
            config = WidgetDbConfig.get_by_search_type(search_type, "edit")
            if not config:
                config = WidgetDbConfig.create(search_type, "edit")
            config.append_display_element(name, edit_class_name, edit_options)
            config.commit_config()


        # create the sobject for now
        sobject = SObjectFactory.create("prod/custom_property")
        sobject.set_value("search_type", search_type)
        sobject.set_value("name", name)
        sobject.set_value("description", description)
        sobject.commit()


        my.description = "Added Property [%s] of type [%s] to [%s]" % \
            (name, type, search_type)



class CustomAddElementWdg(BaseInputWdg):
    def get_display(my):
        web = WebContainer.get_web()

        if web.get_form_value("Insert/Exit"):
            widget = Widget()
            iframe = WebContainer.get_iframe()
            widget.add( HtmlElement.script(iframe.get_off_script()) )
            widget.add( HtmlElement.script("window.parent.document.form.submit()") )
            return widget


        database = Project.get_project_code()
        search_type = web.get_form_value("search_type")
        assert search_type

        view = web.get_form_value("view")
        if not view:
            view = get_template_view()
        
        widget = DivWdg()

        WebContainer.register_cmd("pyasm.widget.CustomAddElementCbk")

        # remember some parameters
        widget.add( HiddenWdg("search_type", search_type) )
        widget.add( HiddenWdg("view", view) )

        # Get the definition widget and list all of the custom elements
        config = WidgetConfigView.get_by_search_type(search_type,DEFAULT_VIEW)
        element_names = config.get_element_names()

        # show current custom
        widget.add("<h3>Add Element for [%s]</h3>" % search_type)

        widget.add( my.get_new_custom_widget(view) )

        return widget


    def get_new_custom_widget(my, view):

        custom_table = Table(css="table")
        name_text = TextWdg("new_custom_name")
        custom_table.add_row()
        custom_table.add_cell("Name: ")
        custom_table.add_cell(name_text)

        type_select = SelectWdg("new_custom_type")
        #type_select.add_empty_option("-- Select --")
        type_select.set_option("values", "Name/Code|Foreign Key|List|Checkbox|Text|Number|Date|Date Range")
        custom_table.add_row()
        custom_table.add_cell("Predefined Type: ")
        td = custom_table.add_cell(type_select)
        td.add( HtmlElement.script('''
        function property_type_select(el) {
            if (el.value == "Foreign Key") {
                set_display_on('foreign_key_options')
            }
            else if (el.value == "List") {
                set_display_on('list_options')
            }
            else {
                set_display_off('foreign_key_options')
                set_display_off('list_options')
            }
        }
        ''') )
        type_select.add_event("onchange", "property_type_select(this)")


        # extra info for foreign key
        custom_table.add_row()
        div = DivWdg()
        div.set_id("foreign_key_options")
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


        # extra info for foreign key
        custom_table.add_row()
        div = DivWdg()
        div.set_id("list_options")
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


        custom_table.add_row()
        description_wdg = TextAreaWdg("new_description")
        custom_table.add_cell( "Description: " )
        custom_table.add_cell( description_wdg )

        # add to current view
        if view not in ['edit', 'insert']:
            custom_table.add_row()
            current_view_wdg = CheckboxWdg("add_to_current_view")
            current_view_wdg.set_checked()
            custom_table.add_cell("Add To Current View: ")
            td = custom_table.add_cell(current_view_wdg)


        
        custom_table.add_row()
        edit_view_wdg = CheckboxWdg("add_to_edit_view")
        edit_view_wdg.set_checked()
        custom_table.add_cell("Add To Edit View: ")
        custom_table.add_cell(edit_view_wdg)

        # add to edit view
        custom_table.add_row()
        custom_table.add_blank_cell()
        custom_table.add_cell(SpanWdg('If you check this for a search type already in the system, it will create an edit view that overrides the built-in edit view. This may affect its editability. You can always delete the edit view in the Configure Widgets tab afterwards.', css='warning smaller'))

        custom_table.add_row()
       


        from pyasm.prod.web import ProdIconSubmitWdg, ProdIconButtonWdg
        submit = ProdIconSubmitWdg("Insert/Next")
        tr, td = custom_table.add_row_cell(submit)
        td.add_style("text-align: center")

        submit = ProdIconSubmitWdg("Insert/Exit")
        td.add(submit)

        iframe = WebContainer.get_iframe()
        cancel = ProdIconButtonWdg("Cancel")
        iframe_close_script = "window.parent.%s" % iframe.get_off_script() 
        cancel.add_event("onclick", iframe_close_script)


        td.add(cancel)
        
        return custom_table








class CustomCreateViewCbk(Command):

    def get_title(my):
        return "Custom Create View"

    def execute(my):
        web = WebContainer.get_web()
        view = web.get_form_value("create_view_name")
        if not view:
            print("WARNING: Create View name not found")
            return

        search_type = web.get_form_value("search_type")
        project = web.get_form_value("project")

        description = web.get_form_value("new_description")

        # TODO: where to get the template view from?
        #copy_from_template = web.get_form_value("copy_from_template")

        # get the current custom view
        #print "keys: ", web.get_form_keys()
        template_view = web.get_form_value("template_view")
        if template_view:
            current_view = template_view
        else:
            current_view = "custom"

        config = WidgetDbConfig.get_by_search_type(search_type, current_view)
        if not config:
            # create a new one
            config = WidgetDbConfig.create(search_type, current_view)

        # clean up view so that it has legal characters for xml
        title = view
        view = Common.get_filesystem_name(view)

        # get the config file
        new_config = WidgetDbConfig.create(search_type, view)

        xml = config.get_value("config")
        if xml:
            xml = xml.replace("<%s" % current_view, "<%s" % view)
            xml = xml.replace("/%s>" % current_view, "/%s>" % view)
            xml = xml.replace("<%s/>" % current_view, "<%s/>" % view)
        new_config.set_value("config", xml)
        new_config.commit()

        auto_create_edit = web.get_form_value('auto_create_edit') == 'on'
        # auto-create the edit config
        if auto_create_edit:    
            search = Search("sthpw/widget_config")
            search.add_filter("search_type", search_type)
            search.add_filter("view", "edit")
            edit_config = search.get_sobject()
            if not edit_config:
                edit_config = WidgetDbConfig.create(search_type, "edit") 

        my.description = "Created view [%s] for search_type [%s]" % (view, search_type)

class CsvDownloadWdg(BaseRefreshWdg):
    '''Dynamically generates a csv file to download'''

    def get_args_keys(my):
        return {'table_id': 'Table Id', 'search_type': 'Search Type', \
                'close_cbfn': 'Cbk function', \
                'view': 'View of search type',\
                'column_names': 'Column Names to export',\
                'filename': 'filename to export',\
                'search_keys': 'True if it is in title mode',\
                'search_type': 'Selected Search Keys',
                'include_id': 'Include an id in export'}     

    def init(my):
        my.filename = my.kwargs.get("filename")
        my.column_names = my.kwargs.get('column_names')
        my.view = my.kwargs.get('view')
        my.search_type = my.kwargs.get('search_type')
        my.close_cbfn = my.kwargs.get('close_cbfn')
        my.include_id = my.kwargs.get('include_id')
        my.search_keys = my.kwargs.get('search_keys')
        #if my.search_keys:
        #    my.search_keys = my.search_keys.split(',')

    def get_display(my):
        web = WebContainer.get_web()
      
        column_names = my.column_names
        column_names = [ x for x in column_names if x ]
        # create the file path
        tmp_dir = web.get_upload_dir()
        file_path = "%s/%s" % (tmp_dir, my.filename)

        from pyasm.command import CsvExportCmd
        cmd = CsvExportCmd(my.search_type, my.view, column_names, file_path)
        if my.search_keys:
            cmd.set_search_keys(my.search_keys)

        cmd.set_include_id(my.include_id)
        try:
            cmd.execute()
        except Exception, e:
            raise
        
        return file_path


class CsvGenerator(Widget):
    ''' A simple class that takes the csv file (filepath) generated and serves it back '''
    def get_display(my):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        context_dir = web.get_context_dir()
        file_path = web.get_form_value('filepath')
        file_path = file_path.strip('\n')
        
        # set the header properly
        web.set_csv_download(file_path) 

        content = my.get_content(file_path)
        try:
            os.unlink(file_path)
        except IOError, e:
            print "Unable to remove the temp csv file [%s]" %file_path

        return content

    def get_content(my, file_path):
        file = open(file_path)
        content = file.read()
        file.close()
        return content

__all__.append('PicLensRssWdg')
class PicLensRssWdg(Widget):
    '''Dynamically generates a csv file to download'''
    def get_display(my):
        web = WebContainer.get_web()

        search_type = web.get_form_value("search_type")
        search_ids = web.get_form_value("search_ids")
        #print "PicLens why am I begin run???"

        if not search_type or not search_ids:
            return ""


        from pyasm.search import Search

        search = Search(search_type)
        search.add_filters('id', search_ids.split("|"))
        search.add_enum_order_by('id', search_ids.split("|") )
        sobjects = search.get_sobjects()


        xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss">
<channel>

<title></title>
<link></link>
<description></description>
        '''
    
        from pyasm.biz import Snapshot
        for sobject in sobjects:
            snapshot = Snapshot.get_latest_by_sobject(sobject, "icon")
            if not snapshot:
                snapshot = Snapshot.get_latest_by_sobject(sobject, "publish")
            if not snapshot:
                continue

            web = snapshot.get_name_by_type(".swf")
            if not web:
                web = snapshot.get_name_by_type("web")

            icon = snapshot.get_name_by_type("icon")
                
            web_dir = snapshot.get_web_dir()

            web_path = "%s/%s" % (web_dir, web)
            icon_path = "%s/%s" % (web_dir, icon)

            title = "%s - %s" % (sobject.get_code(), sobject.get_name() )

            xml += '''
            <item>
		<title>%s</title>
		<link>%s</link>
		<media:thumbnail url="%s" />
		<media:content url="%s" type="" />
            </item>
            ''' % (title, web_path, icon_path, web_path)

        xml += '''
</channel>
</rss>
        '''
        return xml




class CustomAddPropertyLinkWdg(Widget):
    def __init__(my, search_type, view):
        my.search_type = search_type
        my.view = view

    def get_display(my):
        # add the add property button
        iframe = WebContainer.get_iframe()
        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "pyasm.widget.CustomAddPropertyWdg")
        url.set_option("search_type", my.search_type)
        url.set_option("view", my.view)
        action = iframe.get_on_script(url.to_string() )
        add = IconButtonWdg("Add Property", IconWdg.INSERT, True)

        add.add_event("oncontextmenu", "%s;return false" % action )
        add.add_event("onclick", "%s" % action )

        widget = Widget()
        widget.add(add)
        return widget





class CustomEditViewPopupWdg(Widget):
    def __init__(my, search_type, view):
        my.search_type = search_type
        my.view = view
        my.action_popup = PopupMenuWdg("table_action", multi=True, width='11em')
        super(CustomEditViewPopupWdg,my).__init__()

    def get_on_script(my):
        return my.action_popup.get_on_script()

    def get_display(my):
        web = WebContainer.get_web()
        if not my.view:
            my.view = web.get_form_value("view")
        if not my.view:
            my.view = get_template_view()

        widget = Widget()
        widget.add( HiddenWdg("search_type", my.search_type) )

        # get a list of all of the element names possible
        search_type_obj = SearchType.get(my.search_type)  
        config = WidgetConfigView.get_by_search_type(my.search_type,DEFAULT_VIEW)
        if config:
            element_names = config.get_element_names()

        # FIXME: also get those from the default (not sure about this)
        config = WidgetConfigView.get_by_search_type(my.search_type,"default")
        if config:
            element_names.extend( config.get_element_names() )

        if not element_names:
            element_names = []


        # get the custom element names from config
        custom_config = WidgetConfigView.get_by_search_type(my.search_type,my.view)
        custom_element_names = custom_config.get_element_names()




        # get the custom properties
        search = Search("prod/custom_property")
        search.add_filter("search_type", my.search_type)
        custom_properties = search.get_sobjects()


        # action popup
        action_popup = my.action_popup
        action_popup.set_auto_hide(False)
        action_popup.set_submit(False)
        action_popup.add( HtmlElement.href("Add ...", "javascript:document.form.submit()") )


        for custom_property in custom_properties:
            element_name = custom_property.get_name()
            if element_name not in custom_element_names:
                action_popup.add( " %s" % element_name, "add|%s" % element_name )

        for element_name in element_names:
            if element_name not in custom_element_names:
                action_popup.add( " %s" % element_name, "add|%s" % element_name )

        # add some standard properties
        if my.view in ["edit", "insert"]:
            for element_name in PREDEFINED_EDIT_ELEMENTS:
                if element_name not in custom_element_names:
                    action_popup.add( " %s" % element_name, "add|%s" % element_name )
        else:
            for element_name in PREDEFINED_ELEMENTS:
                if element_name not in custom_element_names:
                    action_popup.add( " %s" % element_name, "add|%s" % element_name )

        action_popup.add_separator()
        action_popup.add( HtmlElement.href("Remove ...", "javascript:document.form.submit()") )
        for element_name in custom_element_names:
            action_popup.add( " %s" % element_name, "remove|%s" % element_name )
        action_popup.add_separator()

        span = SpanWdg("New Custom ...", css="hand")
        iframe = WebContainer.get_iframe()
        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "pyasm.widget.CustomAddPropertyWdg")
        url.set_option("search_type", my.search_type)
        url.set_option("view", my.view)
        action = iframe.get_on_script(url.to_string() )
        span.add_event("onclick", action)
        action_popup.add( span )

        WebContainer.register_cmd("pyasm.widget.CustomViewAction")

        widget.add(action_popup)
        return widget



class CustomAddElementLinkWdg(Widget):
    def __init__(my, search_type, view):
        my.search_type = search_type
        my.view = view

    def get_display(my):
        # add the add property button
        iframe = WebContainer.get_iframe()
        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "pyasm.widget.CustomAddElementWdg")
        url.set_option("search_type", my.search_type)
        url.set_option("view", my.view)
        action = iframe.get_on_script(url.to_string() )
        add = IconButtonWdg("Add Element", IconWdg.INSERT, True)

        add.add_event("oncontextmenu", "%s;return false" % action )
        add.add_event("onclick", "%s" % action )

        widget = Widget()
        widget.add(add)
        return widget

