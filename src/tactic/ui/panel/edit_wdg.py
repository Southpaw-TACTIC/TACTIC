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

__all__ = [ 'EditTitleWdg', 'EditCustomWdg', 'EditWdg', 'PublishWdg','FileAppendWdg']

from pyasm.biz import CustomScript, Project
from pyasm.security import Sudo
from pyasm.common import Environment, Common, TacticException, jsonloads, Container, jsondumps
from pyasm.search import SearchType, Search, SearchKey, WidgetDbConfig
from pyasm.web import DivWdg, Table, SpanWdg, WebContainer, HtmlElement
from pyasm.widget import WidgetConfigView, WidgetConfig, BaseInputWdg
from pyasm.widget import HiddenWdg, EditAllWdg, SubmitWdg, ButtonWdg, EditCheckboxWdg, HintWdg, DateTimeWdg, TextWdg, TextAreaWdg, TextAreaWdg, CheckboxWdg, SelectWdg


from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg, Menu, MenuItem, SmartMenu
from tactic.ui.widget import TextBtnSetWdg, CalendarInputWdg, ActionButtonWdg
from tactic.ui.input import TextInputWdg

import six
basestring = six.string_types


class EditException(Exception):
    pass


class EditTitleWdg(BaseInputWdg):
    def __init__(self, name=None, **kwargs):
        super(EditTitleWdg,self).__init__(name=name, type="edit_title", **kwargs)
        self.level = self.get_option("level") or "0"

        self.title = self.get_title()

        if self.get_option("no_text") in [True, "true"]:
            self.no_text = True
        else:
            self.no_text = False

    def get_display(self):

        #mode = self.kwargs.get("mode")

        if not self.title:
            self.title = self.get_name()
            self.title = Common.get_display_title(self.title)


        #description = self.get_description()
        #print("description: ", description)


        """
        div = DivWdg()
        div.add(title)
        div.add_style("font-weight: bold")
        div.add_style("margin", "20px -10px")
        div.add_color("background", "background", -5)
        div.add_style("height", "20px")
        div.add_style("padding", "10px 10px")
        """



        div = DivWdg()
        if not self.no_text:
            font_size = str(16-int(self.level)*2)
            margin_top = str(20-int(self.level)*2)
            div.add_style("font-size: %spx" % font_size)
            div.add_style("font-weight: bold")
            div.add_style("margin-top: %spx" % margin_top)
            div.add(self.title)
        div.add("<hr/>")

        return div


    def get_default_action(self):
        return "pyasm.command.NullAction"



class EditCustomWdg(BaseInputWdg):

    ARGS_KEYS = {
        "view": {
            'description': "The custom view to be displayed here",
            'type': 'TextWdg',
            'category': 'Options'
        },
    }


    def get_display(self):

        view = self.kwargs.get("view")
        if not view:
            return

        sobject = self.get_current_sobject()
        if sobject:
            search_key = sobject.get_search_key()
            self.kwargs['search_key'] = search_key

        from tactic.ui.panel import CustomLayoutWdg
        layout = CustomLayoutWdg(**self.kwargs)


        try:
            display = layout.get_buffer_display()
        except Exception as e:
            display = str(e)


        div = DivWdg()
        div.add(display)
        return div




    def get_default_action(self):
        return "pyasm.command.NullAction"







class EditWdg(BaseRefreshWdg):

    CLOSE_WDG = "close_wdg"

    ARGS_KEYS = {
        "mode": {
            'description': "The mode of this widget",
            'type': 'SelectWdg',
            'values': 'insert|edit|view',
            'default': 'insert',
            'category': 'Options'
        },
        "search_type": {
            'description': "SType that will be inserted or edited",
            'category': 'Options',
            'order': 0,
        },
        "title": {
            'description': "The title to appear at the top of the layout",
            'category': 'Options',
        },
        "view": {
            'description': "View of item to be edited",
            'category': 'Options',
            'order': 1,
        },
        "width": {
            'description': "Width of the widget",
            'category': 'Options',
        },
        "show_header": {
            'description': "Determines whether or not to show the header",
            'type': 'SelectWdg',
            'values': 'true|false',
            'category': 'Options',
        },

        "show_action": {
            'description': "Determines whether or not to show action buttons",
            'type': 'SelectWdg',
            'values': 'true|false',
            'category': 'Options',
        },
        "title_width": {
            'description': "Width of the attribute titles column",
            'type': 'TextWdg',
            'category': 'Options',
        },




        "search_id": "id of the sobject to be edited",
        "code": "code of the sobject to be edited",

        "search_key": "search key of the sobject to be edited",

        "input_prefix": "prefix of any input widget",
        "access": 'override the default access',

        'cbjs_insert_path': 'override script path for the insert callback',
        'cbjs_edit_path': 'override script path for the edit callback',
        'cbjs_cancel': 'override for the cancel callback',

        "config_base": "view (DEPRECATED)",

        "default": "default data in a JSON or dictionary form to be used for new entry",
        "single": "when in insert mode, determine if only one entry can be inserted",
        "ignore": "A list of element names to ignore",
        "source": "Source element"
        }


    def init(self):
        self.is_refresh = self.kwargs.get("refresh")
        self.search_key = self.kwargs.get("search_key")
        self.ticket_key = self.kwargs.get("ticket")
        self.parent_key = self.kwargs.get("parent_key")
        self.expression = self.kwargs.get("expression")
        
        self.disables = self.kwargs.get("disables")
        if not self.disables:
            self.disables = {}

        self.code = self.kwargs.get("code")
        sobject = None
        if self.search_key:
            sudo = Sudo()
            try:
                sobject = Search.get_by_search_key(self.search_key)
            finally:
                sudo.exit()

            if not sobject:
                raise Exception("No sobject found for search_key [%s]" % self.search_key)
            self.search_id = sobject.get_id()
            self.search_type = sobject.get_base_search_type()
            if sobject.is_insert():
                self.mode = 'insert'
            else:
                self.mode = 'edit'
        elif self.expression:
            sobject = Search.eval(self.expression, single=True)
            self.search_id = sobject.get_id()
            self.search_type = sobject.get_base_search_type()
            self.mode = 'edit'

        elif self.ticket_key:
            raise Exception("EditWdg: ticket_key no long supported")
            """
            from pyasm.security import Ticket, Login
            ticket = Ticket.get_by_valid_key(self.ticket_key)
            if not ticket:
                raise TacticException("No valid ticket")
            login_code = ticket.get_value("login")
            login = Login.get_by_code(login_code)
            self.search_type = "sthpw/login"
            self.search_id = login.get_id()
            self.mode = 'edit'
            """

        elif self.code:
            self.search_type = self.kwargs.get("search_type")
            search = Search(self.search_type)
            search.add_filter("code", self.code)
            sobject = search.get_sobject()
            
            self.search_id = sobject.get_id()
            self.search_type = sobject.get_base_search_type()
            self.mode = 'edit'


        else:
            self.search_type = self.kwargs.get("search_type")
            self.search_id = self.kwargs.get("search_id")
            if not self.search_id:
                self.search_id = -1
            self.search_id = int(self.search_id)
            if self.search_id != -1:
                self.mode = "edit"
            else:
                self.mode = "insert"
        
        assert(self.search_type)

        # explicit override
        if self.kwargs.get("mode"):
            self.mode = self.kwargs.get("mode")


        self.view = self.kwargs.get("view")
        if not self.view:
            self.view = self.kwargs.get("config_base")
        if not self.view:
            self.view = "edit"


        self.display_mode = self.kwargs.get("display_mode")
        if not self.display_mode:
            self.display_mode = "default"


        default_data = self.kwargs.get('default')
        
        if not default_data:
            default_data = {}
        elif isinstance(default_data, basestring):
            try:
                default_data = jsonloads(default_data)
            except:
                #may be it's regular dictionary
                try:
                    default_data = eval(default_data)
                except:
                    print("Warning: Cannot evaluate [%s]" %default_data)
                    default_data = {}

        if sobject:
            self.set_sobjects([sobject], None)
        else:
            self.do_search()

        # TODO: get_config() is going the right direction (less features) but the more complicated method is biased 
        # towards edit and insert view.. and so it needs improvement as well

        if self.view not in ["insert", "edit"]:
            # try a new smaller way to get config only when an explicit view
            # is set
            self.config = self.get_config()
        else:
            self.config = WidgetConfigView.get_by_search_type(self.search_type, self.view, use_cache=False)

        # for inline config definitions
        config_xml = self.kwargs.get("config_xml")
        if config_xml:
            #from pyasm.common import Xml
            #xml = Xml()
            #xml.read_string(config_xml)
            #node = xml.get_node("config/%s" % self.view)
            #xml.set_attribute(node, "class", "tactic.ui.panel.EditWdg")
            #config = WidgetConfig.get(view=self.view, xml=xml)
            config_xml = config_xml.replace("&", "&amp;")

            config = WidgetConfig.get(view="tab", xml=config_xml)
            self.config.insert_config(0, config)

        
        self.skipped_element_names = []

        # if there is a layout view, then find the element names using that
        layout_view = self.kwargs.get("layout_view")
        if layout_view:
            layout_view = layout_view.replace("/", ".")
            search = Search("config/widget_config")
            search.add_filter("view", layout_view)
            layout_config = search.get_sobject()
             
            xml = layout_config.get_xml_value("config")
            self.element_names = xml.get_values("config//html//element/@name")
        else:
            self.element_names = self.config.get_element_names()


        override_element_names = self.kwargs.get("element_names")
        if override_element_names:
            self.element_names = override_element_names
            self.element_names = self.element_names.split(",")

        ignore = self.kwargs.get("ignore")
        if isinstance(ignore, basestring):
            ignore = ignore.split("|")
        if not ignore:
            ignore = []

        self.element_titles = []
        self.element_descriptions = []
        for element_name in self.element_names:
            self.element_titles.append( self.config.get_element_title(element_name) )
            self.element_descriptions.append( self.config.get_element_description(element_name) )

        #self.element_titles = self.config.get_element_titles()  
        #self.element_descriptions = self.config.get_element_descriptions()  


        # MongoDb
        # Default columns
        if not self.element_names:
            impl = SearchType.get_database_impl_by_search_type(self.search_type)
            if impl.get_database_type() == "MongoDb":
                self.element_names = impl.get_default_columns()
                self.element_titles = ['Code', 'Name', 'Description']
                self.element_descriptions = ['Code', 'Name', 'Description']




        self.input_prefix = self.kwargs.get('input_prefix')
        if not self.input_prefix:
            self.input_prefix = 'edit'
        
        security = Environment.get_security()
        default_access = "edit"
        project_code = Project.get_project_code()


        if self.parent_key:
            from pyasm.biz import Schema
            schema = Schema.get()
            parent_stype = SearchKey.extract_base_search_type(self.parent_key)
            #relationship = schema.get_relationship_attrs(parent_stype, self.search_type, type="hierarchy")
            relationship = schema.get_relationship_attrs(parent_stype, self.search_type)
            for element_name in self.element_names:

                # If parent_key is available, data associated with the parent table does not need
                # to be specified by the user, and their widgets can be excluded from the edit widget
                if element_name == relationship.get("from_col"):
                    ignore.append(element_name)


        #extra_data = self.kwargs.get("extra_data") or {}

        for i, element_name in enumerate(self.element_names):

            if element_name in ignore:
                self.skipped_element_names.append(element_name)
                continue


            # check security access
            access_key2 = {
                'search_type': self.search_type,
                'project': project_code
            }
            access_key1 = {
                'search_type': self.search_type,
                'key': element_name, 
                'project': project_code

            }
            access_keys = [access_key1, access_key2]
            is_editable = security.check_access('element', access_keys, "edit", default=default_access)

            
            if not is_editable:
                self.skipped_element_names.append(element_name)
                continue

            widget = self.config.get_display_widget(element_name, kbd_handler=False)


            # some element could be disabled due to its data_type e.g. sql_timestamp
            if not widget:
                self.skipped_element_names.append(element_name)
                continue



            widget.set_sobject(self.sobjects[0])

            default_value = default_data.get(element_name)
            if default_value:
                widget.set_value(default_value)
           
            attrs = self.config.get_element_attributes(element_name)
            editable = widget.is_editable()
            if editable:
                editable = attrs.get("edit")
                editable = editable != "false"
            
            if not editable:
                self.skipped_element_names.append(element_name)
                continue

            # set parent
            widget.set_parent_wdg(self)
            
            # set parent_key in insert mode for now
            if self.mode =='insert' and self.parent_key:
                widget.set_option('parent_key', self.parent_key)
            
            
            title = self.element_titles[i]
            if title:
                widget.set_title(title)

            description = attrs.get("description")
            if description:
                widget.add_attr("description", description)

            self.widgets.append(widget)

            description = self.element_descriptions[i]
            widget.add_attr("title", description)




    def get_config(self):
        # look in the db first
        configs = []
        config = WidgetDbConfig.get_by_search_type(self.search_type, self.view)
        get_edit_def = False
        if config:
            configs.append(config)
            get_edit_def = True
            config = WidgetDbConfig.get_by_search_type(self.search_type, "edit_definition")
            if config:
                configs.append(config)

        else:
            if self.mode == 'insert':
                config = WidgetDbConfig.get_by_search_type(self.search_type, "insert")
                if config:
                    configs.append(config)
            # look for the edit
            config = WidgetDbConfig.get_by_search_type(self.search_type, "edit")
            if config:
                configs.append(config)


        file_configs = WidgetConfigView.get_configs_from_file(self.search_type, self.view)
        configs.extend(file_configs)

        file_configs = WidgetConfigView.get_configs_from_file(self.search_type, "edit")
        configs.extend(file_configs)

        #TODO: add edit_definition    
        #file_configs = WidgetConfigView.get_configs_from_file(self.search_type, "edit_definition")
        #configs.extend(file_configs)
        if not get_edit_def:
            config = WidgetDbConfig.get_by_search_type(self.search_type, "edit_definition")
            if config:
                configs.append(config)
   
        config = WidgetConfigView(self.search_type, self.view, configs, layout="EditWdg")
        return config


 


    def get_display(self):

        search_type_obj = SearchType.get(self.search_type)
        sobj_title = search_type_obj.get_title()
        sobj_title = Common.pluralize(sobj_title)

        self.color_mode = self.kwargs.get("color_mode")
        if not self.color_mode:
            self.color_mode = "default"


        top_div = self.top
        top_div.add_class("spt_edit_top")

        if not self.is_refresh:
            self.set_as_panel(top_div)
        content_div = DivWdg()
        content_div.add_class("spt_edit_top")
        content_div.add_class("spt_edit_form_top")
        content_div.set_attr("spt_search_key", self.search_key)

        if not Container.get_dict("JSLibraries", "spt_edit"):
            content_div.add_behavior( {
                'type': 'load',
                'cbjs_action': self.get_onload_js()
            } )



        layout_view = self.kwargs.get("layout_view")
        if layout_view:
            layout_wdg = self.get_custom_layout_wdg(layout_view)
            content_div.add(layout_wdg)

            return content_div



        # add close listener
        # NOTE: this is an absolute search, but is here for backwards
        # compatibility
        content_div.add_named_listener('close_EditWdg', '''
            var popup = bvr.src_el.getParent( ".spt_popup" );
            if (popup)
                spt.popup.close(popup);
        ''')


        attrs = self.config.get_view_attributes()
        default_access = attrs.get("access")

        if not default_access:
            default_access = "edit"

        project_code = Project.get_project_code()

        security = Environment.get_security()
        base_key =  search_type_obj.get_base_key()
        key = {
            'search_type': base_key,
            'project': project_code
        }
        access = security.check_access("sobject", key, "edit", default=default_access)
        if not access:
            self.is_disabled = True
        else:
            self.is_disabled = False

        disable_wdg = None
        if self.is_disabled:
            # TODO: This overlay doesn't work in IE, size, position, 
            # and transparency all fail. 
            disable_wdg = DivWdg(id='edit_wdg')
            disable_wdg.add_style("position: absolute")
            disable_wdg.add_style("height: 90%")
            disable_wdg.add_style("width: 100%")
            disable_wdg.add_style("left: 0px")
            #disable_wdg.add_style("bottom: 0px")
            #disable_wdg.add_style("top: 0px")

            disable_wdg.add_style("opacity: 0.2")
            disable_wdg.add_style("background: #fff")
            #disable_wdg.add_style("-moz-opacity: 0.2")
            disable_wdg.add_style("filter: Alpha(opacity=20)")
            disable_wdg.add("<center>EDIT DISABLED</center>")
            content_div.add(disable_wdg)


        attrs = self.config.get_view_attributes()

        #inner doesn't get styled. 
        inner = DivWdg()
        content_div.add(inner)

        # Disable as it was never implemented
        """
        menu = self.get_header_context_menu()
        menus = [menu.get_data()]
        menus_in = {
            'HEADER_CTX': menus,
        }
        SmartMenu.attach_smart_context_menu( inner, menus_in, False )
        """

        #insert the header before body into inner
        show_header = self.kwargs.get("show_header")
        if show_header and show_header not in ['false', False]:
            self.add_header(inner, sobj_title)

        body_container = DivWdg()
        inner.add(body_container)
        body_container.add_class("spt_popup_body")

        table_div = DivWdg()
        body_container.add(table_div)
        table_div.add_style("margin: 0px 20px")

        table = Table()
        table_div.add(table)



        table.add_style("margin-left: auto")
        table.add_style("margin-right: auto")


        if self.color_mode == "default":
            #table.add_color("background", "background")
            pass

        elif self.color_mode == "transparent":
            table.add_style("background", "transparent")
        table.add_color("color", "color")



        width = attrs.get('width')
        if not width:
            width = self.kwargs.get("width")
        if not width:
            width = 600

        height = attrs.get('height')
        if height:
            table.add_style("height: %s" % height)


        tr = table.add_row()

        stype_type = search_type_obj.get_value("type", no_exception=True)
        if self.mode != 'insert' and stype_type in ['media'] and self.sobjects:

            td = table.add_cell()

            width += 300

            from tactic.ui.panel import ThumbWdg2
            thumb = ThumbWdg2()
            thumb.set_sobject(self.sobjects[0])
            td.add(thumb)
            thumb.add_style("margin: 0px 10px")
            path = thumb.get_lib_path()

            td.add_style("padding: 10px")
            td.add_attr("rowspan", len(self.widgets)+2)
            td.add_style("min-width: 250px")
            td.add_style("vertical-align: top")
            td.add_border(direction="right")

            if path:

                td.add("<h3>File Information</h3>")
                td.add("<br/>")

                from pyasm.checkin import BaseMetadataParser
                parser = BaseMetadataParser.get_parser_by_path(path)

                data = parser.get_tactic_metadata()
                data_table = Table()
                data_table.add_style("margin: 15px")
                td.add(data_table)
                for name, value in data.items():
                    data_table.add_row()
                    display_name = Common.get_display_title(name)
                    dtd = data_table.add_cell("%s: " % display_name)
                    dtd.add_style("width: 150px")
                    dtd.add_style("padding: 3px")
                    dtd = data_table.add_cell(value)
                    dtd.add_style("padding: 3px")

            else:
                td.add("<h3>No Image</h3>")
                td.add("<br/>")


        # set the width
        table.add_style("width: %s" % width)
        table.add_style("margin-top: 20px")
        table.add_style("margin-bottom: 20px")



        single = self.kwargs.get("single")
        if single in ['false', False] and self.mode == 'insert':
            multi_div = DivWdg()
            multi_div.add_style("text-align: left")
            multi_div.add_style("padding: 5px 10px")


            multi_div.add("<b>Specify number of new items to add: </b>")
            multi_div.add("&nbsp;"*4)


            multi_text = TextWdg("multiplier")
            multi_text.add_class("form-control")
            multi_div.add(multi_text)
            multi_text.add_style("display: inline-block")
            multi_text.add_style("width: 60px")

            tr, td = table.add_row_cell( multi_div )

            if self.color_mode == "defaultX":
                td.add_color("border-color", "table_border", default="border")
                td.add_style("border-width: 1px")
                td.add_style("border-style: solid")

            td.add_style("padding: 8px 3px 8px 3px")
            td.add_color("background", "background", -3)
            td.add_color("color", "color")
        
        security = Environment.get_security()

        # break the widgets up in columns
        num_columns = attrs.get('num_columns')
        if not num_columns:
            num_columns = self.kwargs.get('num_columns')

        if not num_columns:
            if len(self.widgets) > 8:
                num_columns = 2
            else:
                num_columns = 1
        else:
            num_columns = int(num_columns)

        # go through each widget and draw it
        index =  0
        for i, widget in enumerate(self.widgets):

            # since a widget name called code doesn't necessariy write to code column, it is commented out for now
            """
            key = { 'search_type' : search_type_obj.get_base_key(),
                'column' : widget.get_name(),
                'project': project_code}
            # check security on widget
            if not security.check_access( "sobject_column",\
                key, "edit"):
                self.skipped_element_names.append(widget.get_name())
                continue
            """

            if not hasattr(widget, 'set_input_prefix'): 
                msg = DivWdg("Warning: The widget definition for [%s] uses [%s] and is not meant for use in Edit Layout. Please revise the edit_definition in widget config."% (widget.get_name(), widget.__class__.__name__ ))
                msg.add_style('color: orange')
                content_div.add(msg)
                content_div.add(HtmlElement.br())
                continue
            if self.input_prefix:
                widget.set_input_prefix(self.input_prefix)

            # Bootstrap
            widget.add_class("form-control")

            if not isinstance(widget, CheckboxWdg):
                widget.add_style("width: 100%")


            if isinstance(widget, EditTitleWdg):
                tr, td = table.add_row_cell()

                td.add(widget)

                index = 0

                continue


           
            if isinstance(widget, HiddenWdg):
                content_div.add(widget)
                continue


            # Set up any validations configured on the widget ...
            from tactic.ui.app import ValidationUtil
            v_util = ValidationUtil( widget=widget )
            v_bvr = v_util.get_validation_bvr()
            if v_bvr:
                if (isinstance(widget, CalendarInputWdg)):
                    widget.set_validation( v_bvr.get('cbjs_validation'), v_bvr.get('validation_warning') );
                else:
                    widget.add_behavior( v_bvr )
                    widget.add_behavior( v_util.get_input_onchange_bvr() )
                  


            new_row = index % num_columns == 0
            if new_row:
                tr = table.add_row()


                #if self.color_mode == "default":
                #    if index % 2 == 0:
                #        tr.add_color("background", "background")
                #    else:
                #        tr.add_color("background", "background", -1 )


            index += 1

           
            show_title = widget.get_option("show_title")
            if not show_title:
                show_title = self.kwargs.get("show_title")

            if show_title in ['false', False]:
                show_title = False
            else:
                show_title = True


            if show_title:
                title = widget.get_title()
                if isinstance(title, basestring) and title.find("->") != -1:
                    parts = title.split("->")
                    title = parts[1]


                title_div = DivWdg()
                title_div.add(title)
                title_div.add_style("display: inline-block")
                title_div.add_class("spt_edit_title")
                title_div.add_style("font-size: 0.9em")
                title_div.add_style("text-transform: uppercase")
                title_div.add_style("opacity: 0.5")
                title_div.add_style("padding-right: 15px")


                td = table.add_cell(title_div)
                td.add_style("padding: 15px 15px 10px 5px")
                td.add_style("vertical-align: top")

 
                title_width = self.kwargs.get("title_width")
                if title_width:
                    td.add_style("width: %s" % title_width)
                else:
                    td.add_style("width: 150px")

                security = Environment.get_security()
                if security.check_access("builtin", "view_site_admin", "allow"):
                    SmartMenu.assign_as_local_activator( td, 'HEADER_CTX' )

                if self.color_mode == "defaultX":
                    td.add_color("border-color", "table_border", default="border")
                    td.add_style("border-width: 1" )
                    td.add_style("border-style: solid" )

                #td.add_style("text-align: right" )

                hint = widget.get_option("hint")
                if hint:
                    #hint_wdg = HintWdg(hint)
                    #hint_wdg.add_style("float: right")
                    #td.add( hint_wdg )
                    td.add_attr("title", hint)


            element_name = widget.get_name()

            if not show_title:
                th, td = table.add_row_cell( widget )
                td.add_class("spt_edit_cell")
                td.add_attr("spt_element_name", element_name)
                continue
            else:

                if self.display_mode == "horizontal":
                    td = table.add_cell()
                    td.add_style("min-width: 300px")
                    td.add_style("padding: 10px 25px 10px 5px")
                    td.add_style("vertical-align: top")

                td.add_class("spt_edit_cell")
                td.add_attr("spt_element_name", element_name)

                if (title in self.disables):
                    widget.add_attr("disabled", "disabled")

                widget.add_style("font-size: 1.2em")
                td.add(widget)


                # description
                description = widget.get_attr("description") or ""
                if description and description != "No description":
                    color = td.get_color("color", 40)

                    description_div = DivWdg()
                    td.add(description_div)
                    description_div.add_style("margin-top: 5px")
                    description_div.add_style("color: %s" % color)
                    description_div.add_style("font-style: italic")
                    description_div.add(description)




        if not self.is_disabled and not self.mode == 'view':
            inner.add( self.get_action_html() )

        if self.input_prefix:
            prefix = HiddenWdg("input_prefix", self.input_prefix)
            tr, td = table.add_row_cell()
            td.add(prefix)

        top_div.add(content_div) 
        return top_div


    def get_custom_layout_wdg(self, layout_view):

        content_div = DivWdg()

        from tactic.ui.panel import CustomLayoutWdg
        # build the kwargs, including custom ones
        kwargs2 = {}
        for key, value in self.kwargs.items():
            if key in ['search_key','view','config_xml']:
                continue
            kwargs2[key] = value
        kwargs2['search_key'] = self.search_key
        kwargs2['view'] = layout_view

        layout = CustomLayoutWdg(**kwargs2)
        #layout = CustomLayoutWdg(view=layout_view, search_key=self.search_key)
        content_div.add(layout)

        for widget in self.widgets:
            name = widget.get_name()
            if self.input_prefix:
                widget.set_input_prefix(self.input_prefix)

            layout.add_widget(widget, name)



        search_key = SearchKey.get_by_sobject(self.sobjects[0], use_id=True)
        search_type = self.sobjects[0].get_base_search_type()


        element_names = self.element_names[:]
        for element_name in self.skipped_element_names:
            element_names.remove(element_name)


        config_xml = self.kwargs.get("config_xml")
        bvr =  {
            'type': 'click_up',
            'mode': self.mode,
            'element_names': element_names,
            'search_key': search_key,
            'input_prefix': self.input_prefix,
            'view': self.view,
            'config_xml': config_xml
        }

        if self.mode == 'insert':
            bvr['refresh'] = 'true'
            # for adding parent relationship in EditCmd
            if self.parent_key:
                bvr['parent_key'] = self.parent_key


        hidden_div = DivWdg()
        hidden_div.add_style("display: none")
        content_div.add(hidden_div)

        hidden = TextAreaWdg("__data__")
        hidden_div.add(hidden)
        hidden.set_value( jsondumps(bvr) )

        show_action = self.kwargs.get("show_action")
        if show_action in [True, 'true']:
            content_div.add( self.get_action_html() )

        return content_div


   
    def get_header_context_menu(self):

        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.smenu_ctx.setup_cbk' )

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Edit Column Definition')
        menu_item.add_behavior( {
            'args' : {
                'search_type': self.search_type,
                'options': {
                    'class_name': 'tactic.ui.manager.ElementDefinitionWdg',
                    'popup_id': 'edit_column_defn_wdg',
                    'title': 'Edit Column Definition'
                }
            },
            'cbjs_action': '''
            return


            var activator = spt.smenu.get_activator(bvr);
            bvr.args.element_name = activator.getProperty("spt_element_name");
            bvr.args.view = activator.getAttribute('spt_view');
            var popup = spt.popup.get_widget(evt,bvr);
            popup.activator = activator;
            '''
        } )
        menu.add(menu_item)


        return menu



    def add_header(self, inner, sobj_title):
        header_div = DivWdg()

        title_str = self.kwargs.get("title")

        if not title_str:
            if self.mode == 'insert':
                action = 'Add New Item to'
            elif self.mode == 'edit':
                action = 'Update'
            else:
                action = self.mode
            
            title_str =  action.capitalize() + " " + sobj_title
            if self.mode == 'edit':
                title_str = '%s (%s)' %(title_str, self.sobjects[0].get_code())
            

        #header div text
        title_div = DivWdg()
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 7px")
        title_div.add_style("text-align: center")
        title_div.set_attr('title', self.view)
        title_div.add(title_str)

        #actual header div
        header_div.add(title_div)
        header_div.add_class("spt_popup_header")
        header_div.add_color("background", "background", -8)

        if self.color_mode == "default":
            header_div.add_color("border-color", "table_border", default="border")
            header_div.add_style("border-width: 1px")
            header_div.add_style("border-style: solid")
        header_div.set_attr("colspan", "2")
        header_div.add_style("height: 30px")
        header_div.add_style("padding: 3px 10px")

        header_div.add_style("margin: -1px -1px 10px -1px")

        inner.add(header_div)


    def add_hidden_inputs(self, div):
        '''TODO: docs ... what is this for???'''
        pass


    def do_search(self):
        '''this widget has its own search mechanism'''

        web = WebContainer.get_web()
        
        # get the sobject that is to be edited
        id = self.search_id

        # if no id is given, then create a new one for insert
        search = None
        sobject = None
        search_type_base = SearchType.get(self.search_type).get_base_key()
        if self.mode == "insert":
            sobject = SearchType.create(self.search_type)
            self.current_id = -1
            # prefilling default values if available
            value_keys = web.get_form_keys()
            if value_keys:
                
                for key in value_keys:
                    value = web.get_form_value(key)
                    sobject.set_value(key, value)
        else:
            search = Search(self.search_type)

            # figure out which id to search for
            if web.get_form_value("do_edit") == "Edit/Next":
                search_ids = web.get_form_value("%s_search_ids" %search_type_base)
                if search_ids == "":
                    self.current_id = id
                else:
                    search_ids = search_ids.split("|")
                    next = search_ids.index(str(id)) + 1
                    if next == len(search_ids):
                        next = 0
                    self.current_id = search_ids[next]

                    last_search = Search(self.search_type)
                    last_search.add_id_filter( id )
                    self.last_sobject = last_search.get_sobject()

            else:
                self.current_id = id

            search.add_id_filter( self.current_id )
            sobject = search.get_sobject()

        if not sobject and self.current_id != -1:
            raise EditException("No SObject found")

        # set all of the widgets to contain this sobject
        self.set_sobjects( [sobject], search )


    def get_action_html(self):


        search_key = SearchKey.get_by_sobject(self.sobjects[0], use_id=True)
        search_key_wo_id = SearchKey.get_by_sobject(self.sobjects[0])
        search_type = self.sobjects[0].get_base_search_type()


        div = DivWdg(css='centered')

        # construct the bvr
        element_names = self.element_names[:]
        for element_name in self.skipped_element_names:
            element_names.remove(element_name)

        bvr =  {
            'type': 'click_up',
            'mode': self.mode,
            'element_names': element_names,
            'search_key': search_key,
            'input_prefix': self.input_prefix,
            'view': self.view
        }

        if self.mode == 'insert':
            bvr['refresh'] = 'true'
            # for adding parent relationship in EditCmd
            if self.parent_key:
                bvr['parent_key'] = self.parent_key




        hidden_div = DivWdg()
        hidden_div.add_style("display: none")
        div.add(hidden_div)

        hidden = TextAreaWdg("__data__")
        hidden_div.add(hidden)
        hidden.set_value( jsondumps(bvr) )

        show_action = self.kwargs.get("show_action")
        if show_action in [False, 'false']:
            div.add_style("display: none")
            return div



        div.add_named_listener('close_EditWdg', '''
            var popup = spt.popup.get_popup( document.id('edit_popup') );
            if (popup != null) {
                spt.popup.destroy(popup);
            }
            ''')

     
        # custom callbacks
        cbjs_cancel = self.kwargs.get('cbjs_cancel')
        if not cbjs_cancel:
            cbjs_cancel = '''
            spt.named_events.fire_event('preclose_edit_popup', {});
            spt.named_events.fire_event('close_EditWdg', {})
            '''

        # custom callbacks
        cbjs_insert_path = self.kwargs.get('cbjs_%s_path' % self.mode)
        cbjs_insert = None
        if cbjs_insert_path:
            script_obj = CustomScript.get_by_path(cbjs_insert_path)
            if script_obj:
                cbjs_insert = script_obj.get_value("script")

        # get it inline
        if not cbjs_insert:
            cbjs_insert = self.kwargs.get('cbjs_%s' % self.mode)

        # use a default
        if not cbjs_insert:
            mode_label = self.mode.capitalize()
            cbjs_insert = '''
            spt.edit.edit_form_cbk(evt, bvr);
            spt.notify.show_message("%s item complete.");
            var kwargs = {options: {search_keys: "%s"}};
            spt.named_events.fire_event("delete|workflow/job", kwargs);
            '''% (mode_label, search_key_wo_id)

        save_event = self.kwargs.get('save_event')
        if not save_event:
            save_event = div.get_unique_event("save")
        bvr['save_event'] = save_event

        edit_event = self.kwargs.get('edit_event')
        if not edit_event:
            edit_event = div.get_unique_event("edit")
        bvr['edit_event'] = edit_event

        if self.search_key:
            cmd_key = div.generate_command_key( "tactic.ui.panel.EditCmd", {
                "search_key": self.search_key
            } )
        else:
            cmd_key = "tactic.ui.panel.EditCmd"

        
        bvr['cmd_class'] = cmd_key

        bvr['named_event'] = 'edit_pressed'

        bvr['source'] = self.kwargs.get("source")

        bvr['cbjs_action'] = cbjs_insert
        bvr['extra_data'] = self.kwargs.get("extra_data")

        self.top.add_attr("spt_save_event", save_event)

        ok_btn_label = self.mode.capitalize()
        if ok_btn_label == 'Edit':
            ok_btn_label = 'Save'
        if ok_btn_label == 'Insert':
            ok_btn_label = 'Add'

        if self.kwargs.get('ok_btn_label'):
            ok_btn_label = self.kwargs.get('ok_btn_label')

        ok_btn_tip = ok_btn_label
        if self.kwargs.get('ok_btn_tip'):
            ok_btn_tip = self.kwargs.get('ok_btn_tip')


        cancel_btn_label = 'Cancel'
        if self.kwargs.get('cancel_btn_label'):
            cancel_btn_label = self.kwargs.get('cancel_btn_label')

        cancel_btn_tip = cancel_btn_label
        if self.kwargs.get('cancel_btn_tip'):
            cancel_btn_tip = self.kwargs.get('cancel_btn_tip')


        # create the buttons
        insert_button = ActionButtonWdg(title=ok_btn_label, tip=ok_btn_tip, size=150)
        insert_button.add_behavior(bvr)



        cancel_button = ActionButtonWdg(title=cancel_btn_label, tip=cancel_btn_tip, size=150, color='secondary')
        cancel_button.add_behavior({
        'type': 'click_up',
        'cbjs_action': cbjs_cancel
        })

        table = Table()
        table.add_style("margin-left: auto")
        table.add_style("margin-right: auto")
        table.add_style("margin-top: 15px")
        table.add_style("margin-bottom: 15px")
        table.add_row()
        table.add_cell(insert_button)
        table.add_cell(cancel_button)
        div.add(table)
        div.add_class("spt_popup_footer")



        #div.add(SpanWdg(edit, css='med'))
        #div.add(SpanWdg(edit_close, css='med'))
        #div.add(SpanWdg(cancel, css='med'))

        return div


    def get_default_display_handler(cls, element_name):
        # This is handlerd in get_default_display_wdg
        return None
    get_default_display_handler = classmethod(get_default_display_handler)


    def get_default_display_wdg(cls, element_name, display_options, element_type, kbd_handler=False):

        if element_type in ["integer", "smallint", "bigint", "int"]:
            behavior = {
                'type': 'keyboard',
                'kbd_handler_name': 'DgTableIntegerTextEdit'
            }
            input = TextWdg("main")
            input.set_options(display_options)
            if kbd_handler:
                input.add_behavior(behavior)

        elif element_type in ["float"]:
            behavior = {
                'type': 'keyboard',
                'kbd_handler_name': 'DgTableFloatTextEdit'
            }
            input = TextAreaWdg("main")
            input.set_options(display_options)
            if kbd_handler:
                input.add_behavior(behavior)

        elif element_type in ["string", "link", "varchar", "character", "timecode"]:
            behavior = {
                'type': 'keyboard',
                'kbd_handler_name': 'DgTableMultiLineTextEdit'
            }
            input = TextWdg('main')
            input.set_options(display_options)
            if kbd_handler:
                input.add_behavior(behavior)


        elif element_type in ["text"]:
            behavior = {
                'type': 'keyboard',
                'kbd_handler_name': 'DgTableMultiLineTextEdit'
            }
            input = TextAreaWdg('main')
            input.set_options(display_options)
            if kbd_handler:
                input.add_behavior(behavior)

        elif element_type == "boolean":
            input = CheckboxWdg('main')
            input.set_options(display_options)
            input.add_behavior(
             {"type" : "click_up",
                    'propagate_evt': True})

        elif element_type in  ["timestamp", "date", "time", "datetime2"]:
            from tactic.ui.widget import CalendarInputWdg, CalendarWdg, TimeInputWdg
            # FIXME: take wild guess for the time
            if element_name.endswith("_time"):
                #input = TimeInputWdg()
                behavior = {
                    'type': 'keyboard',
                    'kbd_handler_name': 'DgTableMultiLineTextEdit'
                }
                input = TextWdg('main')
                input.set_options(display_options)
                if kbd_handler:
                    input.add_behavior(behavior)

            else:
                #input = CalendarWdg()
                input = CalendarInputWdg()
                input.set_option('show_activator', False)
            #input.set_options(display_options)

        elif element_type == 'datetime':
            from tactic.ui.widget import CalendarInputWdg
            input = CalendarInputWdg()
            input.set_option('show_time', 'true')

        elif element_type == "color":
            from tactic.ui.widget import ColorInputWdg
            input = ColorInputWdg()
            input.set_options(display_options)

        elif element_type =="sqlserver_timestamp":
            # NoneType Exception is prevented in WidgetConfig already
            input = None
        else:
            # else try to instantiate it as a class
            print("WARNING: EditWdg handles type [%s] as default TextWdg" %element_type)
            input = TextWdg()
            input.add("No input defined")

        return input 
    get_default_display_wdg = classmethod(get_default_display_wdg)



    def get_onload_js(self):
        return r'''

spt.Environment.get().add_library("spt_edit");

spt.edit = {}


spt.edit.save_changes = function(content, search_key, extra_data, values, trigger_mode) {

    if (!values) {
        values = spt.api.Utility.get_input_values(content, null, false, false, {cb_boolean: true});
    }

    bvr = JSON.parse(values.__data__);

    var class_name = "tactic.ui.panel.EditCmd";
    var kwargs = {};

    kwargs['element_names'] = bvr.element_names;

    if (!search_key) {
        search_key = bvr.search_key;
    }
    kwargs['search_key'] = search_key;


    if (bvr.parent_key)
        kwargs['parent_key'] = bvr.parent_key;
    kwargs['input_prefix'] = bvr.input_prefix;
    kwargs['view'] = bvr.view;
    if (extra_data) {
        kwargs['extra_data'] = extra_data;
    }
    if (trigger_mode) {
        kwargs['trigger_mode'] = trigger_mode;
    }

    var server = TacticServerStub.get();

    values['search_type'] = bvr.search_type;

    var ret_val = server.execute_cmd(class_name, kwargs, values);
    return ret_val.info.sobject;
}



// Called when the form is submitted
//
spt.edit.edit_form_cbk = function( evt, bvr )
{
    // first fire a named event
    var named_event = bvr.named_event;
    spt.named_events.fire_event(named_event, bvr);
    var content = bvr.src_el.getParent(".spt_edit_top");
    if (content == null) {
        content = bvr.src_el.getParent(".spt_popup_content");
    }

    //var values = spt.api.Utility.get_input_values(content, null, true, false, {cb_boolean: true});
    var values = spt.api.Utility.get_input_values(content, null, false, false, {cb_boolean: true});
    var server = TacticServerStub.get();

    var class_name = bvr.cmd_class;
    var args = {};

    args['element_names'] = bvr.element_names;
    args['search_key'] = bvr.search_key;
    if (bvr.parent_key)
        args['parent_key'] = bvr.parent_key;
    args['input_prefix'] = bvr.input_prefix;
    args['view'] = bvr.view;
    args['extra_data'] = bvr.extra_data;

    // this is needed as bvr turns null on error
    var src_el = bvr.src_el;
    try {
        var ret_val = server.execute_cmd(class_name, args, values);
        var info = ret_val.info;

        // add a callback after save
        var popup = bvr.src_el.getParent(".spt_popup");
        if (popup && popup.on_save_cbk ) {
            popup.on_save_cbk();
        }

        if (bvr.refresh == "true") {
            //refresh the panel above content
            var panel = spt.get_parent(content,'.spt_panel');
            if (panel) spt.panel.refresh(panel);
        }
        else {
        }
        spt.named_events.fire_event('close_EditWdg', {});
        // refresh the row

        if (bvr.mode == 'edit') {
            update_event = "update|" + bvr.search_key;
            
            spt.named_events.fire_event(update_event, {});
            // for fast table
            var tmps = spt.split_search_key(bvr.search_key)
            var tmps2 = tmps[0].split('?');
            var update_row_event = "update_row|" + tmps2[0];
            var update_st_event = "update|" + tmps2[0];

            var bvr_fire = {};
            bvr_fire.src_el = bvr.src_el;

            var kwargs = {update_data: values};
            var input = {
                search_key: info.search_key,
                sobject: info.sobject,
                kwargs: kwargs
            };
            bvr_fire.options = input;
            spt.named_events.fire_event(update_st_event, bvr_fire);
            spt.named_events.fire_event(update_row_event, bvr_fire);

            if (bvr.edit_event) {
                spt.named_events.fire_event(bvr.edit_event, bvr_fire);
            }

        }
        else {
            // update the table

            // FIXME: this search key is just LOST!!!
            bvr.options = {
                search_key: info.search_key,
                sobject: info.sobject,
            }
            if (bvr.save_event) {
                spt.named_events.fire_event(bvr.save_event, bvr);
            }

        }
    }
    catch(e) {
        var ok = function() {};
        var cancel = function(bvr){

            if( spt.validation.has_invalid_entries( src_el, ".spt_edit_top" ) )
                return;
            spt.named_events.fire_event('close_EditWdg', {});
           
        };

        var options = {}
        options.cancel_args = bvr;

        spt.confirm( "Error: " + spt.exception.handler(e) + "<br/>Try again?", ok, cancel, options);
    }
    return info;

}

        '''




class FileAppendWdg(EditWdg):

    def init(self):
        super(FileAppendWdg, self).init()
        self.mode = 'Append'


    def add_header(self, table, title):
        table.add_style('width', '50em')
        
        parent_st = self.kwargs.get('search_type')
        parent_sid =  self.kwargs.get('search_id')

        sobj = Search.get_by_id(parent_st, parent_sid)
        sobj_code = 'New'
        sobj_title = ''
        if sobj:
            sobj_code = sobj.get_code()
            sobj_title = sobj.get_search_type_obj().get_title()
        th = table.add_header( "Append File for %s [%s]" % (sobj_title, sobj_code))
        th.set_attr("colspan", "2")
     
        
        if sobj:
            hidden = HiddenWdg('parent_search_key', SearchKey.get_by_sobject(sobj) )
            th.add(hidden)
        
    def get_action_html(self):
        search_key = SearchKey.get_by_sobject(self.sobjects[0])
        behavior_submit = {
            'type': 'click_up',
            'cb_fire_named_event': 'append_pressed',
            'element_names': self.element_names,
            'search_key': search_key,
            'input_prefix': self.input_prefix

        }
        behavior_cancel = {
            'type': 'click_up',
            'cb_fire_named_event': 'preclose_edit_popup',
            'cbjs_postaction': "spt.popup.destroy( spt.popup.get_popup( document.id('edit_popup') ) );"
        }
        button_list = [{'label':  "%s/Close" % self.mode.capitalize(),
            'bvr': behavior_submit},
            {'label':  "Cancel", 'bvr': behavior_cancel}]        
        edit_close = TextBtnSetWdg( buttons=button_list, spacing =6, size='large', \
                align='center',side_padding=10)
        
       
        div = DivWdg()
        div.add_styles('height: 35px; margin-top: 10px;')
       
        div.center()
        div.add(edit_close)

        return div





class PublishWdg(EditWdg):

    def init(self):
        super(PublishWdg, self).init()
        self.mode = 'publish'

    def get_action_html(self):
      
        search_key = SearchKey.get_by_sobject(self.sobjects[0])
        search_type = self.sobjects[0].get_base_search_type()


        div = DivWdg(css='centered')
        div.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        } )
        
        div.add_styles('height: 35px; margin-top: 10px;')
        div.add_named_listener('close_EditWdg', '''
            var popup = bvr.src_el.getParent( ".spt_popup" );
            if (popup)
                spt.popup.close(popup);
        ''')


     
        # custom callbacks
        cbjs_cancel = self.kwargs.get('cbjs_cancel')
        if not cbjs_cancel:
            cbjs_cancel = '''
            spt.named_events.fire_event('preclose_edit_popup', {});
            spt.named_events.fire_event('close_EditWdg', {})
            '''

        # custom callbacks
        cbjs_insert_path = self.kwargs.get('cbjs_%s_path' % self.mode)
        cbjs_insert = None
        if cbjs_insert_path:
            script_obj = CustomScript.get_by_path(cbjs_insert_path)
            cbjs_insert = script_obj.get_value("script")
            cbjs_insert = cbjs_insert.replace("'", '"')

        # get it inline
        if not cbjs_insert:
            cbjs_insert = self.kwargs.get('cbjs_%s' % self.mode)

        # use a default
        if not cbjs_insert:
            cbjs_insert = '''
            spt.edit.edit_form_cbk(evt, bvr);
            '''

        element_names = self.element_names[:]
        for element_name in self.skipped_element_names:
            element_names.remove(element_name)
        # Must not have postaction which closes the EditWdg before upload finishes
        from tactic.ui.widget import TextBtnWdg, TextBtnSetWdg
        bvr =  {
                    'cbjs_action': cbjs_insert,
                    'named_event': 'close_EditWdg',
                    'element_names': element_names,
                    'search_key': search_key,
                    'input_prefix': self.input_prefix,
                    'view': self.view
                }
        keys = WebContainer.get_web().get_form_keys()
        for key in keys:
            bvr[key] = WebContainer.get_web().get_form_value(key)

        label = self.mode
        if label == 'edit':
            label = 'save'

        buttons_list = [
            {
                'label': label.capitalize(),
                'tip': label.capitalize(),
                'bvr': bvr
            },
            {
                'label': 'Cancel',
                'tip': 'Cancel',
                'bvr': {
                    'cbjs_action': cbjs_cancel
                }
            }
        ]
        buttons = TextBtnSetWdg( align="center", buttons=buttons_list, spacing=10, size='large', side_padding=4 )

        div.add(buttons)



        return div





