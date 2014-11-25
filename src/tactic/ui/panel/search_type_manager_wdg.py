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
__all__ = ["SearchTypeManagerWdg", "ManageSearchTypeDetailWdg", "ManageSearchTypeMenuWdg",
        "AlterSearchTypeCbk"]

import os, types

from pyasm.common import Xml, Environment, Common, Container
from pyasm.command import Command, ColumnDropCmd, ColumnAlterCmd, ColumnAddCmd
from pyasm.search import Search, SearchType, WidgetDbConfig, SearchException, SqlException
from pyasm.biz import Project
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer, Widget, WidgetSettings
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg, CheckboxWdg, WidgetConfigView, WidgetConfig, \
TextAreaWdg, TextWdg, ButtonWdg, ProdIconButtonWdg, HiddenWdg, SwapDisplayWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.activator import ButtonForDropdownMenuWdg
from tactic.ui.widget import ActionButtonWdg

from manage_view_panel_wdg import ManageViewPanelWdg, ManageSideBarDetailWdg

class SearchTypeManagerWdg(ManageViewPanelWdg):
    '''Panel to manage search types ... this is meant to be a generic interface
    for manipulating the search types'''

    def init(my):
        my.search_type = my.kwargs.get('search_type')
        if not my.search_type:
            my.search_type = WebContainer.get_web().get_form_value('search_type')
        my.view = my.kwargs.get('view')
        if not my.view:
            my.view = "database_definition"
    
    def get_tool_bar(my):
        widget = Widget()
        trash_div = SpanWdg()
        trash_div.set_id('trash_me')

        trash_div.add(IconWdg('Trash', IconWdg.TRASH))
        trash_div.add("TRASH!")
        trash_div.add_class("hand")
        trash_div.add_class("spt_side_bar_trash")
      
        
        trash_div.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        bvr = { "type": "click_up",\
                'cbjs_action': "alert('Drag and drop element name here to remove it.')"}
        trash_div.add_behavior(bvr)

        widget.add(trash_div)
        
        save_div = SpanWdg(css='med hand spt_side_bar_trash')
        save_div.add(IconWdg('Save', IconWdg.SAVE))
        
        bvr = { "type": "click_up",\
                'cbjs_action': "spt.custom_project.manage_action_cbk({'value':'save'},'%s');" % my.view} 
        save_div.add_behavior(bvr)
        widget.add(save_div)
        return widget
 
    def get_display(my):
        div = DivWdg()

        
        top_div = DivWdg(id='SearchTypeManager', css='spt_panel')
        top_div.set_attr('spt_class_name','tactic.ui.panel.SearchTypeManagerWdg')
        top_div.add_class( "spt_view_manager_top" )
        
        div.add(top_div)

        top_div.add( my.get_action_wdg(my.search_type) ) 
        top_div.add(HtmlElement.br())

        div.add(HtmlElement.br())
        if not my.search_type:
            return div

        # check to see that the search type actually exists
        try:
            SearchType.get(my.search_type)
        except SearchException:
            return div

        # Create the Advanced Search Type table.    
        """
        from tactic.ui.panel import TableLayoutWdg
        table = TableLayoutWdg(search_type="sthpw/search_object",view="table",show_insert='false', show_row_select='false', do_search='false', show_gear='false', show_refresh='false', show_search_limit='false')
        search = Search("sthpw/search_object")
        search.add_filter("search_type", my.search_type)
        search_type_obj = search.get_sobject()
        table.set_sobject(search_type_obj)

        # Create the Advance bar and add the swap widget to it.
        advanced_bar = DivWdg()
        swap = SwapDisplayWdg()
        title = SpanWdg("Advanced")
        swap.create_swap_title(title, swap, advanced_bar, is_open=False)

        advanced_top = DivWdg(css="maq_search_bar")
        advanced_top.add_style("margin: 5px 0px 5px 0px")
        advanced_top.add_style("background-color: black")
        advanced_top.add_styles("background: white")
        advanced_top.add_style("padding: 3px")
        advanced_top.add(swap)
        advanced_top.add(title)
        
        # Wrap the Search Type Table in a div and add it to the advanced options.
        div_table = DivWdg()
        div_table.add_style("padding: 3px")
        div_table.add(table)
        div_table.add_style("background-color: #444")
        advanced_bar.add(div_table)
        advanced_top.add(advanced_bar)

        # Add the Advanced Search Type table.
        top_div.add(advanced_top)
        top_div.add(HtmlElement.br())
        """

        table = Table()
        table.add_color("color", "color")
        table.add_row()

        # add the sections
        td = table.add_cell()
        td.add_style("vertical-align: top")

        # add the template view containing the possible block items to be added
        # ie: New Column
        menu_div = DivWdg()
        menu_div.set_id("menu_item_template")
        menu_div.add_style("display: none")
        menu_div.add( my.get_section_wdg("template") )
        td.add(menu_div) 

        # add the widget column
        show_definition = my.kwargs.get("show_definition")
        if  not show_definition in ['false', False]:
            definition_view = DivWdg()
            definition_view.set_id("menu_item_list")
            definition_view.add( my.get_section_wdg("definition", title='Widget Column', editable=False, default=True) )
            td.add(definition_view)

        td.add("<br/>")

        # add the db_column
        definition_view = DivWdg()
        definition_view.add_style('min-width: 200px')
        definition_view.set_id("menu_item_list")
        definition_view.add( my.get_section_wdg("db_column", title='Database Columns', editable=False) )

        td.add(definition_view)
        td.add_style("vertical-align: top")
        td.add("<br/>")



        # add the custom definition containing the possible items to be added
        # ie: default columns
        """
        menu_div = DivWdg()
        menu_div.set_id("menu_item_custom_definition")
        menu_div.add_style("display: block")

        menu_div.add( my.get_section_wdg("custom_definition") )
        td.add(menu_div)
        """

        # add detail information
        detail_wdg = ManageSearchTypeDetailWdg(search_type=my.search_type)
        td = table.add_cell( detail_wdg )

        # set the panel information
        td.set_id("manage_side_bar_detail")
        td.add_class('spt_view_manager_detail')
        td.add_style("display", "table-cell")
        td.add_attr("spt_class_name", "tactic.ui.panel.ManageSearchTypeDetailWdg")
        td.add_attr("spt_search_type", my.search_type)

        td.add_style("padding: 0 20px 20px 20px")
        td.add_style("vertical-align: top")
        #td.add_attr("rowspan", "2")

        

        top_div.add(table)
        # add the predefined list
        predefined = my.get_predefined_wdg()
        top_div.add(predefined)

        return div

    def get_action_wdg(my, search_type):
        div = DivWdg()
        menus = [ my.get_action_menu_details(search_type) ]
        dd_activator = ButtonForDropdownMenuWdg( id="SideBarManagerActionDropDown", title="-- Action --", menus=menus,
                                                 width=150, match_width=True)


        """
        from tactic.ui.widget import ButtonNewWdg, ButtonRowWdg
        button_row = ButtonRowWdg()
        div.add(button_row)

        button = ButtonNewWdg(title="New Search Type", icon=IconWdg.NEW)
        button_row.add(button)

        button = ButtonNewWdg(title="New Search Type", icon=IconWdg.PIPELINE)
        button_row.add(button)
        """


        div.add( dd_activator )
        return div

    def get_action_menu_details(my, search_type):
        spec_list = [ { "type": "action", "label": "New SType...", "bvr_cb":
                    {'cbjs_action': "spt.popup.open('create_search_type_wizard');" } }]
        if search_type:
            spec_list.append({ "type": "action", "label": "New Table Column...", "bvr_cb":
                    {'cbjs_action': "spt.custom_project.manage_action_cbk({'value':'new_widget_column'},'%s', bvr);",
                        'search_type': search_type  } })

        return {
            'menu_id': 'SearchTypeManagerWdg_DropdownMenu', 'width': 250, 'allow_icons': False,
            'opt_spec_list': spec_list
            
        }
        ''' #TODO: add this back and work on the pp_action on dropping
         """
                { "type": "action", "label": "New Column", "bvr_cb":
                    {'cbjs_action': "spt.custom_project.manage_action_cbk({'value':'new_column'},'%s', bvr);" % my.view}},"""
                { "type": "separator" },
                { "type": "action", "label": "Show Predefined", "bvr_cb":
                    {'cbjs_action': "spt.custom_project.manage_action_cbk({'value':'predefined'},'%s');" % my.view} }'''  

    def get_predefined_wdg(my):
        project = Project.get()
        project_type = project.get_type()

        from tactic.ui.container import PopupWdg
        popup = PopupWdg(id="predefined_db_columns", allow_page_activity=True, width="320px")
        popup.add_title("Predefined Database Columns")
        popup.add( my.get_section_wdg(view='predefined', default=True))

        return popup
    
    def get_section_wdg(my, view, title='', editable=True, default=False):
        '''editable really means draggable'''
        if not title:
            title = view 
        target_id = "sobject_relation"
        if editable:
            edit_mode = 'edit'
        else:
            edit_mode = 'read'

        kwargs = {
            'title': title,
            'view': view,
            'target_id': target_id,
            'width': '300',
            'prefix': 'manage_side_bar',
            'mode': edit_mode,
            'default': str(default),
            'config_search_type': my.search_type
        }
        if view == "database_definition":
            kwargs['recurse'] = "false"

        id = "ManageSearchTypeMenuWdg_" + view
        section_div = DivWdg(id=id, css='spt_panel')
        section_div.add_style("display: block")
        section_div.set_attr('spt_class_name', "tactic.ui.panel.ManageSearchTypeMenuWdg")
        for name, value in kwargs.items():
            if name == "config":
                continue
            section_div.set_attr("spt_%s" % name, value)

        section_wdg = ManageSearchTypeMenuWdg(**kwargs)
        section_div.add(section_wdg)
        return section_div

from tactic.ui.manager import BaseSectionWdg
#from manage_view_panel_wdg import ManageSideBarBookmarkMenuWdg
class ManageSearchTypeMenuWdg(BaseSectionWdg):

    def get_detail_class_name(my):
        return "tactic.ui.panel.ManageSearchTypeDetailWdg"


    
    def get_config(cls, search_type, view, default=None, personal=False):
        # personal doesn't mean much here since this is only for Project view definition
        """
        if view == "__column__":
            xml == '''
            <config>
                <element name="tttt" type="__database__"/>
                <element name="uuuu" type="__database__"/>
                <element name="vvvv" type="__database__"/>
            </config>
            '''
        """
        widget_config = None
        config_view = None
        widget_config_list = []


        # get all the configs relevant to this search_type
        configs = []
       
        from pyasm.widget import WidgetConfigView
        if view == "definition":
            if default:
                try:
                    default_config_view = WidgetConfigView.get_by_search_type(search_type, view, use_cache=False, local_search=True)

                    user_config_view = WidgetConfigView.get_by_search_type(search_type, view)
                  
                    #merge the user config view from db into the default config view in xml file
                    default_config = default_config_view.get_definition_config()
                    user_config = user_config_view.get_definition_config()
                    if user_config:
                        user_element_names = user_config.get_element_names()
                        # make sure it's unique, there is a new validate function for
                        # WidgetDbConfig to ensure that also
                        user_element_names = Common.get_unique_list(user_element_names)
                        for elem in user_element_names:
                            user_node = user_config.get_element_node(elem)
                            default_config.append_xml_element(elem, node=user_node)
                except SqlException, e:
                     print "Search ERROR: ", e.__str__()
                     default_config = None
                
                if default_config:
                    default_config.get_xml().clear_xpath_cache()
                    widget_config_list = [default_config]

            else:
                config_view = WidgetConfigView.get_by_search_type(search_type, view, use_cache=True)

        elif view == "database_definition":
            schema_config = SearchType.get_schema_config(search_type)
            widget_config_list = [schema_config]
        elif view == 'template':
            base_dir = Environment.get_install_dir()
            file_path="%s/src/config2/search_type/search/DEFAULT-conf.xml" % base_dir
            if os.path.exists(file_path):
                widget_config = WidgetConfig.get(file_path=file_path, view=view)
                widget_config_list = [widget_config]
            '''
            elif default == True :
                base_dir = Environment.get_install_dir()
                file_path="%s/src/config2/search_type/search/DEFAULT-conf.xml" % base_dir
                if os.path.exists(file_path):
                    widget_config = WidgetConfig.get(file_path=file_path, view="default_definition")
                    widget_config_list = [widget_config]
            '''
        elif view == "custom_definition":
            # look for a definition in the database
            search = Search("config/widget_config")
            search.add_filter("search_type", 'SearchTypeSchema')
            search.add_filter("view", view)
            config = search.get_sobject()
            # this is really just a custom made definition
            #view = "definition"
            
            if config:
                widget_config_list = [config]
            else:
                widget_config_list = []

        elif view == "db_column":
            # look for a definition in the database
            """
            view = "definition"
            from pyasm.search import SObjectDefaultConfig
            default = SObjectDefaultConfig(search_type=search_type,view=view)
            xml = default.get_xml()
            config = WidgetConfig.get(view=view, xml=xml)
            widget_config_list = [config]
            """
            try:   
                # add the schema config definiiton
                schema_config = SearchType.get_schema_config(search_type)
                widget_config_list = [schema_config]
            except SqlException, e:
                widget_config_list = []
        if not config_view:
            config_view = WidgetConfigView(search_type, view, widget_config_list)
        return config_view

    get_config = classmethod(get_config)

    def add_link_behavior(my, link_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a link'''

        # check security
        #default_access = "view"
        #security = Environment.get_security()
        #if not security.check_access("side_bar", element_name, "edit", default=default_access):
        #    return

        # avoid editing id and s_status 
        if my.kwargs.get('view')=='db_column' and element_name in ['id','s_status']:
            link_wdg.add_style('color: black')
            return

        # make it draggable
        edit_allowed = True
        if my.mode == 'edit' and edit_allowed:
                # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp',
                'cbjs_action_onnomotion':  'spt.side_bar.display_element_info_cbk(evt,bvr);',
                'class_name':   my.get_detail_class_name()
            }
        else:
            behavior = {
                "type": 'click',
                #"drag_el": 'drag_ghost_copy',
                #"drop_code": 'manageSideBar',
                #"cb_set_prefix": 'spt.side_bar.pp',
                'cbjs_action':  'spt.side_bar.display_element_info_cbk(evt,bvr);',
                'class_name':   my.get_detail_class_name()
            }
        if config.get_view() == 'template':
            template_config = my._get_template_config()
            node = template_config.get_element_node('new_column')
            behavior['config_xml'] = template_config.get_xml().to_string(node)
        link_wdg.add_behavior(behavior)
        link_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        link_wdg.add_attr("spt_default", my.default)
        
    def _get_template_config(my):

        base_dir = Environment.get_install_dir()
        file_path="%s/src/config2/search_type/search/DEFAULT-conf.xml" % base_dir
        if os.path.exists(file_path):
            widget_config = WidgetConfig.get(file_path=file_path, view='template')
        return widget_config

class ManageSearchTypeDetailWdg(ManageSideBarDetailWdg):

    ADD_COLUMN = "Commit New Column"
    MODIFY_COLUMN = "Modify Column"
    REMOVE_COLUMN = "Remove Column"

    def get_config(my, search_type, view,  default=False, personal=False):
        config = ManageSearchTypeMenuWdg.get_config(search_type, view, default=default)
        return config


    def init(my):
        '''initialize the widget_config, and from there retrieve the schema_config'''
        web = WebContainer.get_web()
        my.search_type = my.kwargs.get('search_type')
        
        element_name = my.kwargs.get('element_name')
        my.view = my.kwargs.get('view')
        
        # FIXME: comment out the assert for now to avoid error screen
        if not my.view:
            my.view = 'table'
        #assert my.view

        my.config_xml = my.kwargs.get('config_xml')
        if not my.config_xml:
            my.config_xml = web.get_form_value('config_xml')
        
        my.default = my.kwargs.get('default') == 'True'

        cbk = ManageSearchTypeDetailCbk(search_type=my.search_type, view=my.view, \
                element_name=element_name)
        Command.execute_cmd(cbk)

        my.config_string = ""
        my.data_type_string = ""
        my.name_string = ""
        my.title_string = ""
        my.nullable_string = ""
        my.has_column = True


       
        if element_name:
            if my.config_xml:
                my.config_string = my.config_xml
                whole_config_string = "<config><%s>%s</%s></config>"%(my.view, my.config_xml, my.view)
                config = WidgetConfig.get(xml=whole_config_string, view=my.view)
                my.config = WidgetConfigView(my.search_type, my.view, [config])
            else:
                # don't pass in default here
                my.config = my.get_config(my.search_type, my.view)
                node = my.config.get_element_node(element_name)
                if node is not None:
                    config_xml = my.config.get_xml()
                    

                    my.config_string = config_xml.to_string(node)
                    my.title_string = config_xml.get_attribute(node, 'title')
            schema_config = SearchType.get_schema_config(my.search_type)
            
            attributes = schema_config.get_element_attributes(element_name)
            my.data_type_string = attributes.get("data_type")
            
            # double_precision is float
            if my.data_type_string == 'double precision':
                my.data_type_string = 'float'

            my.name_string = attributes.get("name")
            my.nullable_string = attributes.get("nullable")
            my.is_new_column = attributes.get("new") == 'True'

            # a database columnless widget
            if not my.name_string:
                my.has_column = False
                                
    def get_display(my):

        # add the detail widget
        detail_wdg = DivWdg(css='spt_detail_panel')
        if not my.name_string and not my.config_string:
            detail_wdg.add("<br/>"*3)
            detail_wdg.add('<- Click on an item on the left for modification.')
            detail_wdg.add_style("padding: 10px")
            detail_wdg.add_color("background", "background", -5)
            detail_wdg.add_style("width: 350px")
            detail_wdg.add_style("height: 400px")
            detail_wdg.add_border()

            return detail_wdg

        if my.kwargs.get("mode") == "empty":
            overlay = DivWdg()
            detail_wdg.add(overlay)

        detail_wdg.add_border()
        detail_wdg.add_color("color", "black")
        detail_wdg.add_style("padding: 10px")
        detail_wdg.add_color("background", "background", -5)

        detail_wdg.set_id('search_type_detail')

        # put in the selection for simple or advanced
        select = SelectWdg("config_mode", label='Mode: ')
        select.set_persistence()
        values = ['simple', 'advanced']
        select.set_option("values", values)
        config_mode = select.get_value()
        #select.add_behavior({"type": "change", "cbjs_action": "spt.simple_display_toggle( spt.get_cousin(bvr.src_el, '.spt_detail_panel','.config_simple') )"})
        select.add_behavior({"type": "change", "cbjs_action": \
            "spt.simple_display_toggle( spt.get_cousin(bvr.src_el, '.spt_detail_panel','.config_advanced')); %s" %select.get_save_script()})

        select.add_class('spt_config_mode')

        title_div = DivWdg("Column Detail")
        title_div.add_class("maq_search_bar")
        detail_wdg.add(title_div)
        detail_wdg.add("<br/>")
        detail_wdg.add(select)
        detail_wdg.add(HtmlElement.br(2))

        #simple_mode_wdg = WidgetDetailSimpleModeWdg()
        #detail_wdg.add(simple_mode_wdg)
        #detail_wdg.add(HtmlElement.br(2))

        if my.is_new_column:
            detail_wdg.add( my.get_new_definition_wdg() )
        else:
            
            simple_wdg = my.get_simple_definition_wdg()
           
            simple_wdg.add_class("config_simple")
            detail_wdg.add( simple_wdg )
            adv_wdg = my.get_advanced_definition_wdg()
            adv_wdg.add_class("config_advanced")
            if config_mode == 'simple':
                adv_wdg.add_style('display: none')
            detail_wdg.add(HtmlElement.br(2))
            detail_wdg.add( adv_wdg )

        detail_wdg.add(HtmlElement.br(2))


        security_wdg = my.get_security_wdg()
        detail_wdg.add(security_wdg)


        # add hidden input for view for panel refreshing
        # we are only interested in whether it is project_view or definition
        # sub-views of project_view is not of our interest

        #if my.view != 'project_view':
        #    my.view = 'custom_definition'
        detail_wdg.add(HiddenWdg('view', my.view))


        return detail_wdg

    def get_advanced_definition_wdg(my):
        # add the advanced entry
        advanced = DivWdg()
        advanced.add_style("margin-top: 10px")
        advanced.add_style("padding: 10px")
        advanced.add_border()
        title = DivWdg()
        title.add_style("color: black")
        title.add("Advanced - XML Column Definition")
        title.add_style("margin-top: -23")
        advanced.add(title)
        advanced.add("<br/>")

        input = TextAreaWdg("config_xml")
        input.set_id("config_xml")
        input.set_option("rows", "10")
        input.set_option("cols", "70")
        input.set_value(my.config_string)
        advanced.add(input)
        advanced.add(HtmlElement.br(2))

        button_div = DivWdg()
        button_div.add_style("text-align: center")
        

        button = ActionButtonWdg(title="Save Definition") 
        #button = ProdIconButtonWdg("Save Definition")
        button.add_event("onclick", "spt.custom_project.save_definition_cbk()")
        button_div.add(button)
        button_div.add_style("margin-left: 130px")
        advanced.add(button_div)

        return advanced

    def get_new_definition_wdg(my):
        detail_wdg = DivWdg()
        detail_wdg.add_style("color: black")
        detail_wdg.add_style("width: 350px")
        detail_wdg.add_style("margin-top: 10px")
        detail_wdg.add_style("padding: 10px")
        detail_wdg.add_border()
        title = DivWdg()
        title.add_style("color: black")
        title.add("Column Definition")
        title.add_style("margin-top: -22px")
        detail_wdg.add(title)


        # add a name entry
        title = SpanWdg()
        detail_wdg.add("Name: ")
        detail_wdg.add(title)
        input = SpanWdg()
        input.add_style('padding-top: 6px')
        input.set_id("config_element_name")
        text = TextWdg('column_name')
        text.set_value(my.name_string)
        input.add(text)
        detail_wdg.add(input)
        hidden = HiddenWdg('target_search_type', my.search_type)
        detail_wdg.add(hidden)

        detail_wdg.add(HtmlElement.br(2))

        # add data_type entry
        data_type = SpanWdg()
        default_data_types = ['varchar(256)','varchar', 'character', 'text', 'integer', 'float', 'boolean', 'timestamp', 'Other...']
        select = SelectWdg('config_data_type', label ='Data Type: ')
        #detail_wdg.add(": ")
        select.set_option('values', default_data_types )
        select.set_value(my.data_type_string)
        
        select.add_behavior({'type': 'change', 
            'cbjs_action': "if (bvr.src_el.value=='Other...') {spt.show('config_data_type_custom');}\
                    else {spt.hide('config_data_type_custom');}"})
        data_type.add(select) 

        text = TextWdg('config_data_type_custom')
        span = SpanWdg("Other: ", css='med')
        span.add(text)
        span.set_id('config_data_type_custom')
        span.add_style('display','none')
        text.set_value(my.data_type_string)

        data_type.add("<br/>")
        data_type.add(span)
        detail_wdg.add(data_type)
            
        detail_wdg.add("<br/>")
        # add a nullable entry
        nullable = DivWdg()
        checkbox = CheckboxWdg('config_nullable', label ='Allow null(empty) value: ')
        nullable.add(checkbox)

        if my.nullable_string in ['True', 'true']:
            checkbox.set_checked()
        
        detail_wdg.add(nullable)

        return detail_wdg

    def get_simple_definition_wdg(my):

        detail_wdg = DivWdg()
        detail_wdg.add_color("color", "color")
        detail_wdg.add_style("width: 350px")
        detail_wdg.add_style("margin-top: 10px")
        detail_wdg.add_style("padding: 10px")
        detail_wdg.add_border()
        title = DivWdg()
        title.add_style("margin-top: -23px")
        detail_wdg.add(title)
        if not my.name_string:
            title.add('No database column')
            return detail_wdg
        
        title.add("Column Definition")
       


        # add a name entry
        detail_wdg.add("<br/>")
        title = SpanWdg()
        detail_wdg.add("Name: ")
        detail_wdg.add(title)
        input = SpanWdg()
        input.add_style('padding-top: 6px')
        input.set_id("config_element_name")
        input.add(HtmlElement.b(my.name_string))
        detail_wdg.add(input)
        hidden = HiddenWdg('column_name', my.name_string)
        detail_wdg.add(hidden)
        hidden = HiddenWdg('target_search_type', my.search_type)
        detail_wdg.add(hidden)

        detail_wdg.add(HtmlElement.br(2))

        # add data_type entry
        data_type = SpanWdg()
        default_data_types = ['varchar(256)','varchar', 'character', 'text', 'integer', 'float', 'boolean', 'timestamp', 'Other...']
        select = SelectWdg('config_data_type', label ='Data Type: ')
        #detail_wdg.add(": ")
        select.set_option('values', default_data_types )
        select.set_value(my.data_type_string)
        
        select.add_behavior({'type': 'change', 
            'cbjs_action': "if (bvr.src_el.value=='Other...') {spt.show('config_data_type_custom');}\
                    else {spt.hide('config_data_type_custom');}"})
        data_type.add(select) 

        text = TextWdg('config_data_type_custom')
        span = SpanWdg("Other: ", css='med')
        span.add(text)
        span.set_id('config_data_type_custom')
        span.add_style('display','none')
        text.set_value(my.data_type_string)

        data_type.add("<br/>")
        data_type.add(span)
        detail_wdg.add(data_type)
            
        detail_wdg.add("<br/>")
        # add a nullable entry
        nullable = SpanWdg()
        checkbox = CheckboxWdg('config_nullable', label ='Allow null(empty) value: ')
        #detail_wdg.add(": ")
        nullable.add(checkbox)
   

        if my.nullable_string in ['True', 'true']:
            checkbox.set_checked()
        
        detail_wdg.add(nullable)


        #constraint = DivWdg()
        #detail_wdg.add(constraint)
        #constraint.add_style("margin-top: 10px")
        #constraint.add("Constraint: ")
        #select = SelectWdg("config_constraint")
        #constraint.add(select)
        #select.set_option("values", "unique|indexed")
        #select.add_empty_option("-- None --")




        button_div = DivWdg()
        button_div.add_style("text-align: center")


        button_div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
spt.manage_search_type = {};

spt.manage_search_type.change_column_cbk = function(bvr) {
    var class_name = 'tactic.ui.panel.AlterSearchTypeCbk';
    var options ={
        'alter_mode': bvr.alter_mode,
        'title': bvr.title
    };

    try {
        var server = TacticServerStub.get();
        var panel = $('search_type_detail');
        if (! panel.getAttribute("spt_class_name") ) {
            panel = panel.getParent(".spt_panel");
        }
        var values = spt.api.Utility.get_input_values(panel);
        rtn = server.execute_cmd(class_name, options, values);
        if (bvr.alter_mode == 'Remove Column')
            spt.info("Column [" + bvr.column + "] has been deleted.");
        else if (bvr.alter_mode == 'Modify Column')
            spt.notify.show_message("Column [" + bvr.column + "] has been modified.");
    }
    catch (e) {
        spt.alert(spt.exception.handler(e));
    }
    var view = 'db_column';
    spt.panel.refresh("ManageSearchTypeMenuWdg_" + view);
    var view = 'definition';
    spt.panel.refresh("ManageSearchTypeMenuWdg_" + view);
}


            '''
        } )


        detail_wdg.add(button_div)
        button_div.add("<hr/><br/>")
        if my.is_new_column:
            button = ActionButtonWdg(title="Commit") 
            #button = ProdIconButtonWdg("Commit New Column")
            button.add_behavior({"type": "click_up", 
                "cbjs_action": "spt.manage_search_type.change_column_cbk(bvr)", \
                        
                        "alter_mode": my.ADD_COLUMN})
            button_div.add(button)
        else:

            table = Table()
            button_div.add(table)
            table.add_row()
            table.center()

            button = ActionButtonWdg(title="Modify") 
            #button = ProdIconButtonWdg("Modify Column")
            button.add_behavior({"type": "click_up", 
            "cbjs_action": '''spt.manage_search_type.change_column_cbk(bvr);
                           ''',
                    "alter_mode": my.MODIFY_COLUMN,
                    "column": my.name_string,
                    "title": my.title_string
                    })
            table.add_cell(button)

            button = ActionButtonWdg(title="Delete") 
            #button = ProdIconButtonWdg("Delete Column")
            #button.add_style('background-color: #BF462E')
            button.add_behavior({"type": "click_up", 
                "cbjs_action": '''
                
                var yes = function() {
                    spt.manage_search_type.change_column_cbk(bvr);
                    
                }
                spt.confirm("Are you sure you wish to delete this column?", yes) 
                ''',
                "alter_mode": my.REMOVE_COLUMN,
                "column": my.name_string
                
                })
            table.add_cell(button)
            button_div.add(HiddenWdg('delete_column'))
            button_div.add(HiddenWdg('modify_column'))

        return detail_wdg

    def get_security_wdg(my):
        return None




class WidgetDetailSimpleModeWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'the search type that this detail belongs to',
        'view': 'the view that this detail belongs to',
        'name': 'the name of the element that detail belongs to'
        }

    def get_display(my):

        top_wdg = DivWdg()
        top_wdg.add_style("color: black")
        top_wdg.add_style("width: 350px")
        top_wdg.add_style("margin-top: 10px")
        top_wdg.add_style("padding: 10px")
        top_wdg.add_border()
        title = DivWdg()
        title.add_style("color: black")
        title.add_style("margin-top: -22px")

        top_wdg.add(title)
        #if not my.name_string:
        #    title.add('No database column')
        #    return top_wdg
        
        title.add("Widget Definition")

        widget_types = {
            'foreign_key': 'tactic.ui.table.ForeignKeyElementWdg',
            'button': 'tactic.ui.table.ButtonElementWdg',
            'expression': 'tactic.ui.table.ExpressionElementWdg'
        }


        web = WebContainer.get_web()
        config_string = web.get_form_value("config_xml")
        if not config_string:
            config_string = '<config/>'
        xml = Xml()
        xml.read_string(config_string)

        #print "config_string: ", config_string

        # get values from the config file
        element_name = xml.get_value('element/@name')

        config = WidgetConfig.get(view='element',xml='<config><element>%s</element></config>' % config_string)
        display_options = config.get_display_options(element_name)


        title = xml.get_value('element/@title')
        display_handler = xml.get_value('element/display/@class')
        if not display_handler:
            display_handler = 'tactic.ui.panel.TypeTableElementWdg'

        widget_name = xml.get_value('element/display/@widget')
        if not widget_name:
            widget_name = 'custom'

 
        custom_table = Table()
        custom_table.add_style("color: black")
        top_wdg.add(custom_table)

        name_text = DivWdg()
        name_text.add_style("color: black")
        name_text.add(element_name)
        custom_table.add_row()
        custom_table.add_cell("Name: ")
        custom_table.add_cell(name_text)



        # add title
        custom_table.add_row()
        title_wdg = TextWdg("custom_title")
        title_wdg.set_value(title)
        title_wdg.add_attr("size", "50")
        custom_table.add_cell( "Title: " )
        custom_table.add_cell( title_wdg )

        # add description
        #custom_table.add_row()
        #description_wdg = TextAreaWdg("custom_description")
        #td = custom_table.add_cell( "Description: " )
        #td.add_style("vertical-align: top")
        #custom_table.add_cell( description_wdg )


        type_select = SelectWdg("custom_type")
        #type_select.add_empty_option("-- Select --")

        type_select.set_option("values", "string|integer|float|boolean|currency|date|foreign_key|link|list|button|custom")
        type_select.set_option("labels", "String(db)|Integer(db)|Float(db)|Boolean(db)|Currency(db)|Date(db)|Foreign Key|Link|List|Button|Custom")
        type_select.set_value(widget_name)

        #type_select.set_option("values", "string|integer|float|boolean|currency|date|link|list|foreign_key|button|empty")
        #type_select.set_option("labels", "String|Integer|Float|Boolean|Currency|Date|Link|List|Foreign Key|Button|Empty")
        custom_table.add_row()
        td = custom_table.add_cell("Widget Type: ")
        td.add_style("vertical-align: top")
        td = custom_table.add_cell(type_select)
        type_select.add_event("onchange", "spt.CustomProject.property_type_select_cbk(this)")


        td.add(HtmlElement.br())
        display_handler_text = TextWdg("display_handler")
        display_handler_text.add_attr("size", "50")
        display_handler_text.set_value(display_handler)
        td.add(display_handler_text)



        # extra info for foreign key
        custom_table.add_row()
        div = DivWdg()
        div.add_class("foreign_key_options")
        div.add_style("display: none")
        div.add_style("margin-top: 10px")
        div.add("Options")
        div.add(HtmlElement.br())



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
        div.add_style("color: black")
        div.add_class("button_options")
        div.add_style("display: none")
        div.add_style("margin-top: 10px")

        #class_path = "tactic.ui.table.ButtonElementWdg"
        class_path = display_handler
        button = Common.create_from_class_path(class_path)
        args_keys = button.get_args_keys()


        div.add("Options")
        div.add(HtmlElement.br())

        for key in args_keys.keys():
            option_name_text = HiddenWdg("option_name")
            option_name_text.set_value(key)
            div.add(option_name_text)

            div.add("%s: " % key)
            div.add(" &nbsp; &nbsp;")

            input = button.get_input_by_arg_key(key)

            value = display_options.get(key)
            if value:
                input.set_value(value)

            div.add(input)
            div.add(HtmlElement.br())
        td.add(div)






        # is searchable checkbox
        #custom_table.add_row()
        #current_searchable_wdg = CheckboxWdg("is_searchable")
        #current_view_wdg.set_checked()
        #custom_table.add_cell("Searchable? ")
        #td = custom_table.add_cell(current_searchable_wdg)

        custom_table.close_tbody()


        return top_wdg






class AlterSearchTypeCbk(Command):

    DEFAULT_VIEW = "definition"

    def check(my):
        return True

    def execute(my):
        web = WebContainer.get_web()
        alter_mode = my.kwargs.get("alter_mode")
        title = my.kwargs.get("title")
        config_mode = web.get_form_value("config_mode")
        view = web.get_form_value('view')
        constraint = web.get_form_value("config_constraint")
        data_type = ''

        if config_mode == "advanced" :
            config_string = web.get_form_value("config_xml")
            if config_string:
                xml = Xml()
                xml.read_string(config_string)
                node = xml.get_root_node()
                data_type = xml.get_attribute(node, "data_type")
                nullable = xml.get_attribute(node, "nullable") in ['true','True']
            
        else:
            data_type = web.get_form_value("config_data_type")
            if data_type == 'Other...':
                data_type = web.get_form_value("config_data_type_custom")
            cb = CheckboxWdg("config_nullable")
            nullable = cb.is_checked()

        # if advanced is selected in the Widget Column view, data_type is ''
        # read from UI
        if not data_type and view == 'definition':
            data_type = web.get_form_value("config_data_type")
            if data_type == 'Other...':
                data_type = web.get_form_value("config_data_type_custom")
            cb = CheckboxWdg("config_nullable")
            nullable = cb.is_checked()


        column_name = web.get_form_value("column_name")
        search_type = web.get_form_value("target_search_type")
        if alter_mode == ManageSearchTypeDetailWdg.REMOVE_COLUMN:
            cmd = ColumnDropCmd(search_type, column_name)
            Command.execute_cmd(cmd)
            # delete widget config from definition view
            widget_config = WidgetDbConfig.get_by_search_type(search_type, 'definition')
            if widget_config:
                config = WidgetConfig.get('definition', xml=widget_config.get_xml_value('config'))
                config.remove_xml_element(column_name)
                new_xml = config.get_xml().to_string()
                widget_config.set_value("config", new_xml)
                widget_config.commit()
                # set cache to {}
                from pyasm.common import Container
                 
                Container.put("WidgetConfigView:config_cache", {})
                #Container.put("WidgetConfig:config_cache", {})
        elif alter_mode == ManageSearchTypeDetailWdg.MODIFY_COLUMN:
            cmd = ColumnAlterCmd(search_type, column_name, data_type, nullable)
            Command.execute_cmd(cmd)
            element_options = {}
            element_options['type'] = data_type
            if title:
            	element_options['title'] = title
        

            # handle the "default" view
            # update the widget config data type in the xml
            view = my.DEFAULT_VIEW
            config = WidgetDbConfig.get_by_search_type(search_type, view)
            if config:
                config.append_display_element(column_name, options={}, \
                    element_attrs=element_options)
                config.commit_config()

        elif alter_mode == ManageSearchTypeDetailWdg.ADD_COLUMN:
            cmd = ColumnAddCmd(search_type, column_name, data_type, nullable)
            Command.execute_cmd(cmd)


        if constraint:
            # add constraint
            from pyasm.command import ColumnAddIndexWdg
            cmd = ColumnAddIndexWdg()
            cmd.execute()
        else:
            # remove constraint
            pass


        
class ManageSearchTypeDetailCbk(Command):

    '''FIXME: this function doesn't do anything'''
    def get_args_key(my):
        return {
        'element_name': 'name of the element to get information from',
        'search_type': 'search_type',
        'view': 'view of the search type'
        }

    def execute(my):

        web = WebContainer.get_web()
        # this is set through js
        if web.get_form_value("update") != "true":
            return

        my.element_name = my.kwargs.get('element_name')
        my.search_type = my.kwargs.get('search_type')
        my.view = web.get_form_value("view")
        my.config_xml = web.get_form_value("config_xml")
        #if my.config_xml:
        #    my.config_xml = "<config><%s>%s</%s></config>" %(my.view, my.config_xml, my.view)
        my.handle_config()


    def handle_config(my):
        '''for search type display config'''
        web = WebContainer.get_web()
        WidgetDbConfig.append(my.search_type, my.view, my.element_name, config_xml=my.config_xml)
         
    def handle_config2(my):
        '''for db column search config stuff, not used yet'''
        web = WebContainer.get_web()

        search_type = "SearchTypeSchema"
        view = "definition"
        
        config_search_type = "config/widget_config"

        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        config = search.get_sobject()
        if not config:
            config = SearchType.create(config_search_type)
            config.set_value("search_type", search_type )
            config.set_value("view", view )
            xml = config.get_xml_value("config", "config")
            root = xml.get_root_node()
            # reinitialize
            config._init()

            # build a new config
            view_node = xml.create_element(view)
            root.appendChild(view_node)




        config_mode = web.get_form_value("config_mode")
        if config_mode == "advanced":
            config_string = web.get_form_value("config_xml")
        else:
            config_data_type = web.get_form_value("config_data_type")
            if config_data_type == 'Other...':
                config_data_type = web.get_form_value("config_data_type_custom")
            config_nullable = web.get_form_value("config_nullable")
            
            # TAKEN FROM API: should be centralized or something
            from tactic.ui.panel import SideBarBookmarkMenuWdg
            config_view = SideBarBookmarkMenuWdg.get_config(search_type, view)
            node = config_view.get_element_node(my.element_name)
            if node:
                config_xml = config_view.get_xml()

                node = config_view.get_element_node(my.element_name)
                Xml.set_attribute(node, "data_type", config_data_type)
                Xml.set_attribute(node, "nullable", config_nullable)
                Xml.set_attribute(node, "new", "True")

                config_string = config_xml.to_string(node)
            else:
                config_string = '''
                <element name="%s" data_type="%s" nullable="%s" new="True"/>
                ''' %(my.element_name, config_data_type, config_nullable)
        
        config.append_xml_element(my.element_name,config_string)
        config.commit_config()
        #WidgetDbConfig.append(search_type, view, my.element_name, class_name, display_options, element_attrs)





class ManageSideBarSecurityCbk(Command):

    def get_args_key(my):
        return {
        'element_name': 'name of the element to get information from',
        }


    def execute(my):

        web = WebContainer.get_web()
        if web.get_form_value("update") != "true":
            return

        my.element_name = my.kwargs.get("element_name")

        security_groups = web.get_form_values("security")
        from pyasm.security import AccessRuleBuilder, AccessManager

        rule_group = "side_bar"

        for security_group in security_groups:
            if not security_group:
                continue

            search = Search("sthpw/login_group")
            search.add_filter("login_group", security_group)
            login_group = search.get_sobject()
            assert login_group

            access_rules = login_group.get_xml_value("access_rules")

            # add the rule to each group
            builder = AccessRuleBuilder(access_rules)
            builder.add_rule(rule_group, my.element_name, "deny")

            login_group.set_value("access_rules", builder.to_string())
            login_group.commit()




