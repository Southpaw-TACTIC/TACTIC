###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['ColumnEditWdg', 'ColumnEditCbk']

from pyasm.biz import Pipeline, Project
from pyasm.command import Command, CommandException
from pyasm.search import Search, SearchType
from pyasm.web import DivWdg, Table
from pyasm.widget import TextWdg, IconWdg, SelectWdg, HiddenWdg, WidgetConfigView
from pyasm.common import TacticException

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import SingleButtonWdg, ActionButtonWdg, IconButtonWdg


class ColumnEditWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_color("background", "background")
        top.add_class("spt_columns_top")
        self.set_as_panel(top)
        top.add_style("padding: 10px")

        search_type = self.kwargs.get("search_type")
        search_type_obj = SearchType.get(search_type)

        inner = DivWdg()
        top.add(inner)
        inner.add_style("width: 800px")

        #text = TextWdg("search_type")
        text = HiddenWdg("search_type")
        inner.add(text)
        text.set_value(search_type)

        title_wdg = DivWdg()
        inner.add(title_wdg)
        title_wdg.add( search_type_obj.get_title() )
        title_wdg.add(" <i style='font-size: 9px;opacity: 0.5'>(%s)</i>" % search_type)
        title_wdg.add_style("padding: 5px")
        title_wdg.add_color("background", "background3")
        title_wdg.add_color("color", "color3")
        title_wdg.add_style("margin: -10px -10px 10px -10px")
        title_wdg.add_style("font-weight: bold")





        shelf_wdg = DivWdg()
        inner.add(shelf_wdg)
        shelf_wdg.add_style("height: 35px")
        button = ActionButtonWdg(title='Create', color="default", icon="BS_SAVE")
        shelf_wdg.add(button)
        shelf_wdg.add_style("float: right")




        button.add_behavior( {
            'type': 'click_up',
            'search_type': search_type,
            'cbjs_action': '''
            var class_name = 'tactic.ui.startup.ColumnEditCbk';
            var top = bvr.src_el.getParent(".spt_columns_top");

            var elements = top.getElements(".spt_columns_element");

            var values = [];
            for (var i = 0; i < elements.length; i++ ) {
                var data = spt.api.Utility.get_input_values(elements[i], null, false);
                values.push(data)
            }

            var kwargs = {
                search_type: bvr.search_type,
                values: values
            }


            var server = TacticServerStub.get();
            try {
                server.execute_cmd(class_name, kwargs);

                var names = [];
                for (var i = 0; i < values.length; i++) {
                    var name = values[i].name;
                    name = name.strip();
                    if (name == '') { continue; }
                    names.push(name);
                }

                // Unless there is a table here, we should not do this.
                // Better handled with a callback
                //spt.table.add_columns(names)

                // prevent grabbing all values, pass in a dummy one
                spt.panel.refresh(top, {'refresh': true});

            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }

            '''
        } )
        

        # add the headers
        table = Table()
        inner.add(table)
        table.add_style("width: 100%")
        tr = table.add_row()
        tr.add_color("background", "background", -5)
        th = table.add_header("Column Name")
        th.add_style("width: 190px")
        th.add_style("text-align: left")
        th.add_style("padding: 8px 0px")
        th = table.add_header("Format")
        th.add_style("text-align: left")
        th.add_style("padding: 8px 0px")


        from tactic.ui.container import DynamicListWdg
        dyn_list = DynamicListWdg()
        inner.add(dyn_list)


        from tactic.ui.manager import FormatDefinitionEditWdg

        for i in range(0, 4):
            column_div = DivWdg()
            column_div.add_class("spt_columns_element")
            if i == 0:
                dyn_list.add_template(column_div)
            else:
                dyn_list.add_item(column_div)

            column_div.add_style("padding: 3px")
            column_div.add_style("float: left")

            table = Table()
            column_div.add(table)
            table.add_row()

            from tactic.ui.input import TextInputWdg
            text_wdg = TextInputWdg(name="name", height="30px", width="170px")
            text_wdg.add_class("form-control")
            text_wdg.add_class("display: inline-block")
            td = table.add_cell(text_wdg)
            text_wdg.add_behavior( {
                'type': 'blur',
                'cbjs_action': '''
                var value = bvr.src_el.value;
                var code = spt.convert_to_alpha_numeric(value);
                bvr.src_el.value = code;
                '''
            } )

            option = {
            'name': '_dummy',
            'values': 'integer|float|percent|currency|date|time|scientific|boolean|text|timecode',
            }
            format_wdg = FormatDefinitionEditWdg(option=option)

            td = table.add_cell(format_wdg)
            td.add_style("width: 550px")
            td.add_style("padding-left: 10px")


        # show the current columns
        title_wdg = DivWdg()
        inner.add(title_wdg)
        title_wdg.add_style("margin-top: 25px")
        title_wdg.add("<b>Existing Columns</b>")
        title_wdg.add_style("padding: 5px")
        title_wdg.add_style("margin: 20px -10px 10px -10px")

        inner.add("<hr/>")


        config = WidgetConfigView.get_by_search_type(search_type, "definition")
        element_names = config.get_element_names()

        table = Table()
        inner.add(table)
        table.add_style("width: 100%")

        tr = table.add_row()
        tr.add_color("background", "background", -5)
        th = table.add_header("Column")
        th.add_style("text-align: left")
        th.add_style("padding: 5px 0px")
        th = table.add_header("Data Type")
        th.add_style("text-align: left")
        th.add_style("padding: 5px 0px")
        th = table.add_header("Format")
        th.add_style("text-align: left")
        th.add_style("padding: 5px 0px")
        th = table.add_header("Edit")
        th.add_style("text-align: left")
        th.add_style("padding: 5px 0px")

        count = 0
        for element_name in element_names:
            display_class = config.get_display_handler(element_name)

            if display_class != 'tactic.ui.table.FormatElementWdg':
                continue

            table.add_row()

            display_options = config.get_display_options(element_name)
            format = display_options.get("format")
            if not format:
                format = '<i>text</i>'
            data_type = display_options.get("type")

            table.add_cell(element_name)
            table.add_cell(data_type)
            table.add_cell(format)

            td = table.add_cell()
            button = IconButtonWdg(title="Edit Definition", icon="BS_EDIT")
            td.add(button)

            button.add_behavior( {
            'type': 'click_up',
            'search_type': search_type,
            'element_name': element_name,
            'cbjs_action': '''

            var class_name = 'tactic.ui.manager.ElementDefinitionWdg';
            var kwargs = {
                search_type: bvr.search_type,
                view: 'definition',
                element_name: bvr.element_name
            };
            spt.panel.load_popup("Element Definition", class_name, kwargs);
            '''
            } )

            count += 1


        if not count:
            table.add_row()
            td = table.add_cell()
            td.add_style("height: 80px")
            td.add("No existing columns found")
            td.add_style("text-align: center")
            td.add_color("background", "background", -2)





        if self.kwargs.get("is_refresh"):
            return inner
        else:
            return top



class ColumnEditCbk(Command):

    def execute(self):

        search_type = self.kwargs.get("search_type")
        column_info = SearchType.get_column_info(search_type)

        values = self.kwargs.get("values")

        # get the definition config for this search_type
        from pyasm.search import WidgetDbConfig
        config = WidgetDbConfig.get_by_search_type(search_type, "definition")
        if not config:
            config = SearchType.create("config/widget_config")
            config.set_value("search_type", search_type)
            config.set_value("view", "definition")
            config.commit()
            config._init()


        # add to the edit definition 
        edit_config = WidgetDbConfig.get_by_search_type(search_type, "edit_definition")
        if not edit_config:
            edit_config = SearchType.create("config/widget_config")
            edit_config.set_value("search_type", search_type)
            edit_config.set_value("view", "edit_definition")
            edit_config.commit()
            edit_config._init()


        for data in values:

            name = data.get("name")
            name = name.strip()
            if name == '':
                continue

            try:
                name.encode('ascii')
            except UnicodeEncodeError:
                raise TacticException('Column name needs to be in English. Non-English characters can be used in Title when performing [Edit Column Definition] afterwards.')


            if column_info.get(name):
                raise CommandException("Column [%s] is already defined" % name)

            format = data.get("format")
            fps = data.get("fps")
            data_type = data.get("data_type")

            from pyasm.command import ColumnAddCmd
            cmd = ColumnAddCmd(search_type, name, data_type)
            cmd.execute()
            #(self, search_type, attr_name, attr_type, nullable=True):


            class_name = 'tactic.ui.table.FormatElementWdg'
            options = {
                'format': format,
                'type': data_type,
                'fps': fps
            }


            # add a new widget to the definition
            config.append_display_element(name, class_name, options=options)



            edit_class_name = 'TextWdg'
            edit_options = {}


            # add a new widget to the definition
            edit_config.append_display_element(name, edit_class_name, options=edit_options)

        config.commit_config()
        edit_config.commit_config()


        # views to add it to
        table_views = []
        edit_views = []




class NewTextWdg(TextWdg):
    def init(self):

        #color = self.get_color("border", -20)
        color2 = self.get_color("border")
        color = self.get_color("border", -20)

        self.add_event("onfocus", "this.focused=true")
        self.add_event("onblur", "this.focused=false;$(this).setStyle('border-color','%s')" % color2)

        self.add_behavior( {
        'type': 'mouseover',
        'color': color,
        'cbjs_action': '''
        bvr.src_el.setStyle("border-color", bvr.color);
        '''
        } )
        self.add_behavior( {
        'type': 'mouseout',
        'color': color2,
        'cbjs_action': '''
        if (!bvr.src_el.focused) {
            bvr.src_el.setStyle("border-color", bvr.color);
        }
        '''
        } )

        super(NewTextWdg,self).init()


