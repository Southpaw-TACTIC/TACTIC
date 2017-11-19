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
__all__ = ['WidgetClassHandler']

import tacticenv

from pyasm.common import Container


class WidgetClassHandler(object):

    def __init__(my):

        key = "WidgetClassHandler:config"
        my.config = Container.get(key)
        if my.config != None:
            return

        base_config = '''
        <config>
        <widget_definition>
        <element name='simple'>
            <display class='tactic.ui.common.SimpleTableElementWdg'/>
        </element>

        <element name='default'>
            <display class='tactic.ui.common.SimpleTableElementWdg'/>
        </element>



        <element name='raw_data' help='main'>
            <display class='tactic.ui.common.RawTableElementWdg'/>
        </element>


        <element name='format' help='format-element-wdg'>
            <display class='tactic.ui.table.FormatElementWdg'/>
        </element>


        <element name='expression' help='search'>
            <display class='tactic.ui.table.ExpressionElementWdg'/>
        </element>

        <element name='expression_value' help='expression-value-element-wdg'>
            <display class='tactic.ui.table.ExpressionValueElementWdg'/>
        </element>
        <element name='link' help='link-element-wdg'>
            <display class='tactic.ui.table.LinkElementWdg'/>
        </element>



        <element name='completion' help='task-completion-wdg'>
            <display class='tactic.ui.table.TaskCompletionWdg'/>
        </element>

        <element name='gantt' help='gantt-wdg'>
            <display class='tactic.ui.table.GanttElementWdg'/>
        </element>
        <element name='button'>
            <display class='tactic.ui.table.ButtonElementWdg'/>
        </element>


        <element name='custom_layout' help='custom-layout-wdg'>
        <!--
            <display class='tactic.ui.panel.CustomLayoutWdg'/>
        -->
            <display class='tactic.ui.table.CustomLayoutElementWdg'/>
        </element>

        <element name='freeform_layout'>
            <display class='tactic.ui.table.FreeFormLayoutElementWdg'/>
        </element>

        <element name='delete'>
            <display class='tactic.ui.table.DeleteElementWdg'/>
        </element>

        <element name='edit_layout'>
            <display class='tactic.ui.panel.EditWdg'/>
        </element>

        <element name='table_layout'>
            <display class='tactic.ui.panel.TableLayoutWdg'/>
        </element>
        <element name='fast_table_layout'>
            <display class='tactic.ui.panel.FastTableLayoutWdg'/>
        </element>
        <element name='tile_layout'>
            <display class='tactic.ui.panel.TileLayoutWdg'/>
        </element>
        <element name='fast_layout'>
            <display class='tactic.ui.panel.table_layout_wdg.FastTableLayoutWdg'/>
        </element>
        <element name='view_panel'>
            <display class='tactic.ui.panel.ViewPanelWdg'/>
        </element>

        <element name='freeform_layout'>
            <display class='tactic.ui.tools.freeform_layout_wdg.FreeFormLayoutWdg'/>
        </element>



        <element name='explorer'>
            <display class='tactic.ui.table.ExploreElementWdg'/>
        </element>

        <element name='hidden_row'>
            <!--
            <display class='pyasm.widget.HiddenRowToggleWdg'/>
            -->
            <display class='tactic.ui.table.HiddenRowElementWdg'/>
        </element>

        <element name='text'>
            <display class='tactic.ui.input.TextInputWdg'/>
        <!--
            <display class='pyasm.widget.TextWdg'/>
        -->
        </element>
        <element name='select'>
            <display class='pyasm.widget.SelectWdg'/>
        </element>
        <element name='calendar'>
            <display class='tactic.ui.widget.CalendarInputWdg'/>
        </element>
        <element name='calendar_time'>
            <display class='tactic.ui.widget.CalendarInputWdg'>
              <show_time>true</show_time>
            </display>
        </element>
        <element name='time'>
            <display class='tactic.ui.widget.TimeInputWdg'/>
        </element>

        <element name='color'>
            <display class='tactic.ui.input.ColorInputWdg'/>
        </element>

        <element name='drop_item' help='drop-element-wdg'>
            <display class='tactic.ui.table.DropElementWdg'/>
        </element>

        <element name='file_list'>
            <display class="tactic.ui.table.SObjectFilesElementWdg"/>
        </element>

        <element name='metadata'>
            <display class="tactic.ui.table.MetadataElementWdg"/>
        </element>

        <element name='python'>
            <display class="tactic.ui.table.PythonElementWdg"/>
        </element>


        </widget_definition>
        </config>
        '''
        from pyasm.widget import WidgetConfig
        my.config = WidgetConfig.get(view='widget_definition', xml=base_config)

        # customize config to register widgets
        #path = "xxx.conf"

        Container.put(key, my.config)




    def get_display_handler(my, key):
        return my.config.get_display_handler(key)



    def get_element_attributes(my, key):
        return my.config.get_element_attributes(key)


    def get_all_elements_attributes(my, attr):
        xml = my.config.get_xml()

        attrs = {}
        nodes = xml.get_nodes("config/widget_definition/element")
        for node in nodes:
            name = xml.get_attribute(node, "name")
            value = xml.get_attribute(node, attr)
            attrs[name] = value

        return attrs


if __name__ == '__main__':

    handler = WidgetClassHandler()
    print handler.get_display_handler('expression')
    print handler.get_display_handler('button')


