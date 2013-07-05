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

__all__ = ['LoadOptionsWdg', 'ShotLoadOptionsWdg']


from pyasm.common import Container
from pyasm.web import Widget, DivWdg, Table, SpanWdg, HtmlElement, WebContainer
from pyasm.widget import SwapDisplayWdg, CheckboxWdg, IconWdg, TextWdg


class LoadOptionsWdg(Widget):

    def init(my):
        my.prefix = "prod/asset"
        my.hide_proxy = False
        my.hide_connection = False
        my.hide_instantiation = False
        my.hide_dependencies = False

    def set_prefix(my, prefix):
        my.prefix = prefix


    def get_element_name(my, name):
        if my.prefix:
            return "%s_%s" % (my.prefix, name)
        else:
            return name

    def get_default_setting(my):
        '''get default setting for options'''
        setting = {'instantiation': 'reference',
                'connection': 'http',
                'texture_dependency': 'as checked in'}
        return setting

    def get_display(my):
    
        widget = Widget()
        
        div = DivWdg(css='spt_ui_options')
        div.set_unique_id()
        table = Table()
        div.add(table)
        table.add_style("margin: 5px 15px")
        table.add_color('color','color')

        swap = SwapDisplayWdg()
        #swap.set_off()
        app = WebContainer.get_web().get_selected_app()
        outer_span = SpanWdg()
        outer_span.add_style('float: right')
        span = SpanWdg(app, css='small')
        icon = IconWdg(icon=eval("IconWdg.%s"%app.upper()), width='13px')
        outer_span.add(span)
        outer_span.add(icon)
        
        title = SpanWdg("Loading Options")
        title.add(outer_span)

        SwapDisplayWdg.create_swap_title(title, swap, div, is_open=False)

        widget.add(swap)
        widget.add(title)
        widget.add(div)

        if not my.hide_instantiation:
            table.add_row()
            table.add_blank_cell()
            div = DivWdg(HtmlElement.b("Instantiation: "))
            table.add_cell(div)
            div = my.get_instantiation_wdg()
            table.add_cell(div)


        setting = my.get_default_setting()
        default_instantiation = setting.get('instantiation')
        default_connection = setting.get('connection')
        default_dependency = setting.get('texture_dependency')

        if not my.hide_connection:
            table.add_row()
            table.add_blank_cell()
            con_div = DivWdg(HtmlElement.b("Connection: "))
            table.add_cell(con_div)
            td = table.add_cell()

            is_unchecked = True
            default_cb = None
            for value in ['http', 'file system']:
                name = my.get_element_name("connection")
                checkbox = CheckboxWdg( name )
                checkbox.set_option("value", value)
                checkbox.set_persistence()
                if value == default_connection:
                    default_cb = checkbox
                if checkbox.is_checked():
                    is_unchecked = False
                checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                     "cbjs_action": "spt.toggle_checkbox(bvr, '.spt_ui_options', '%s')" %name}) 
                span = SpanWdg(checkbox, css='small')
                span.add(value)

                td.add(span)
            if is_unchecked:
                default_cb.set_checked()



        if not my.hide_dependencies:
            table.add_row()
            table.add_blank_cell()
            div = DivWdg(HtmlElement.b("Texture Dependencies: "))
            table.add_cell(div)
            td = table.add_cell()
            
            is_unchecked = True
            default_cb = None
            for value in ['as checked in', 'latest', 'current']:
                name = my.get_element_name("dependency")
                checkbox = CheckboxWdg( name )

                
                checkbox.set_option("value", value)
                checkbox.set_persistence()
                checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                     "cbjs_action": "spt.toggle_checkbox(bvr, '.spt_ui_options', '%s')" %name}) 
                if value == default_dependency:
                    default_cb = checkbox
                if checkbox.is_checked():
                    is_unchecked = False

                span = SpanWdg(checkbox, css='small')
                span.add(value)
                td.add(span)
            if is_unchecked:
                default_cb.set_checked()



        from connection_select_wdg import ConnectionSelectWdg
        table.add_row()
        table.add_blank_cell()
        div = DivWdg(HtmlElement.b("Connection Type: "))
        table.add_cell(div)
        table.add_cell( ConnectionSelectWdg() )

        table.add_row()
        table.add_blank_cell()
        div = DivWdg(HtmlElement.b("Connection Port: "))
        table.add_cell(div)
        port_div = DivWdg()
        port_text = TextWdg("port")
        port_text.set_option('size','6')
        port_div.add(port_text)
        port_div.add_style("padding-left: 7px")
        port_div.add_style("width: 40px")
        table.add_cell( port_div )

        from pyasm.prod.web import WidgetSettings
        value = WidgetSettings.get_value_by_key("CGApp:connection_port")
        if value:
            port_text.set_value(value)
        elif WebContainer.get_web().get_selected_app() == 'Houdini':
            port_text.set_value("13000")
        else:
            port_text.set_value("4444")

        port_text.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
                var value = bvr.src_el.value;
                value = parseInt(value);
                var kwargs = {
                    'data': value,
                    'key': 'CGApp:connection_port'
                }
                var cmd = "pyasm.web.WidgetSettingSaveCbk"
                var server = TacticServerStub.get();
                server.execute_cmd(cmd, kwargs);

                // FIXME: this is dangerous use of a global var
                app.port = value;
            '''
        } )


        return widget

    def get_instantiation_wdg(my):
        setting = my.get_default_setting()
        default_instantiation = setting.get('instantiation')

        div = DivWdg()
        is_unchecked = True
        default_cb = None
        for value in my.get_instantiation_options():
            name = my.get_element_name("instantiation")
            checkbox = CheckboxWdg( name )
            if value == default_instantiation:
                default_cb = checkbox
            
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                     "cbjs_action": "spt.toggle_checkbox(bvr, '.spt_ui_options', '%s')" %name}) 
            span = SpanWdg(checkbox, css='small')
            span.add(value)
            div.add(span)
        if is_unchecked:
            default_cb.set_checked()
        return div

    def get_instantiation_options(my):
        options = ['reference', 'import', 'open']
        if WebContainer.get_web().get_selected_app() == 'Houdini':
            options = ['reference']
        
        return options

class AnimLoadOptionsWdg(LoadOptionsWdg):

    def __init__(my):
        super(AnimLoadOptionsWdg,my).__init__()
        # this should match the PREFIX in InstanceLoaderWdg
        my.prefix = "instance"
        my.hide_proxy = True
        my.hide_dependencies = True


    def get_instantiation_options(my):
        return ['reference', 'import', 'open']

class ShotLoadOptionsWdg(LoadOptionsWdg):

    def __init__(my):
        super(ShotLoadOptionsWdg,my).__init__()
        my.prefix = "shot"

    def get_instantiation_options(my):
        options = ['reference', 'import', 'open']
        if WebContainer.get_web().get_selected_app() == 'Houdini':
            options = ['import', 'open']
        elif WebContainer.get_web().get_selected_app() == 'XSI':
            options = ['open']
        return options

    def get_default_setting(my):
        '''get default setting for options'''
        setting = {'instantiation': 'open',
                'connection': 'http',
                'texture_dependency': 'as checked in'}
        return setting

   


