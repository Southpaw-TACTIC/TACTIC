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

    def get_display(my):

        top = my.top
        top.add_color("background", "background")
        top.add_class("spt_columns_top")
        my.set_as_panel(top)
        top.add_style("padding: 10px")

        search_type = my.kwargs.get("search_type")
        search_type_obj = SearchType.get(search_type)

        inner = DivWdg()
        top.add(inner)
        inner.add_style("width: 500px")

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
        shelf_wdg.add_style("height: 30px")
        button = ActionButtonWdg(title='Create >>', icon=IconWdg.SAVE)
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

                spt.table.add_columns(names)


                spt.panel.refresh(top);

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
        tr.add_gradient("background", "background3")
        tr.add_style("padding", "3px")
        th = table.add_header("Column Name")
        th.add_style("width: 170px")
        th.add_style("text-align: left")
        th = table.add_header("Format")
        th.add_style("text-align: left")


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

            text_wdg = NewTextWdg("name")
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
            'name': 'xxx',
            'values': 'integer|float|percent|currency|date|time|scientific|boolean|text|timecode',
            }
            format_wdg = FormatDefinitionEditWdg(option=option)

            td = table.add_cell(format_wdg)
            td.add_style("width: 260px")
            td.add_style("padding-left: 40px")


        # show the current columns
        title_wdg = DivWdg()
        inner.add(title_wdg)
        title_wdg.add_style("margin-top: 20px")
        title_wdg.add("<b>Existing Columns</b>")
        title_wdg.add_color("background", "background3")
        title_wdg.add_style("padding: 5px")
        title_wdg.add_style("margin: 20px -10px 10px -10px")


        config = WidgetConfigView.get_by_search_type(search_type, "definition")
        element_names = config.get_element_names()

        table = Table()
        inner.add(table)
        table.add_style("width: 100%")

        tr = table.add_row()
        tr.add_gradient("background", "background3")
        th = table.add_header("Column")
        th.add_style("text-align: left")
        th = table.add_header("Data Type")
        th.add_style("text-align: left")
        th = table.add_header("Format")
        th.add_style("text-align: left")
        th = table.add_header("Edit")
        th.add_style("text-align: left")

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
            button = IconButtonWdg(title="Edit Definition", icon=IconWdg.EDIT)
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
            td.add_style("height: 50px")
            td.add("No existing columns found")
            td.add_style("text-align: center")
            td.add_border()
            td.add_color("background", "background", -5)





        if my.kwargs.get("is_refresh"):
            return inner
        else:
            return top



class ColumnEditCbk(Command):

    def execute(my):

        search_type = my.kwargs.get("search_type")
        column_info = SearchType.get_column_info(search_type)

        values = my.kwargs.get("values")

        # get the definition config for this search_type
        from pyasm.search import WidgetDbConfig
        config = WidgetDbConfig.get_by_search_type(search_type, "definition")
        if not config:
            config = SearchType.create("config/widget_config")
            config.set_value("search_type", search_type)
            config.set_value("view", "definition")
            config.commit()
            config._init()

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
            #(my, search_type, attr_name, attr_type, nullable=True):


            class_name = 'tactic.ui.table.FormatElementWdg'
            options = {
                'format': format,
                'type': data_type,
                'fps': fps
            }


            # add a new widget to the definition
            config.append_display_element(name, class_name, options=options)

        config.commit_config()



class NewTextWdg(TextWdg):
    def init(my):

        #color = my.get_color("border", -20)
        color2 = my.get_color("border")
        color = my.get_color("border", -20)

        my.add_event("onfocus", "this.focused=true")
        my.add_event("onblur", "this.focused=false;$(this).setStyle('border-color','%s')" % color2)

        my.add_behavior( {
        'type': 'mouseover',
        'color': color,
        'cbjs_action': '''
        bvr.src_el.setStyle("border-color", bvr.color);
        '''
        } )
        my.add_behavior( {
        'type': 'mouseout',
        'color': color2,
        'cbjs_action': '''
        if (!bvr.src_el.focused) {
            bvr.src_el.setStyle("border-color", bvr.color);
        }
        '''
        } )

        super(NewTextWdg,my).init()


