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

__all__ = ['CustomLayoutEditWdg', 'CustomLayoutEditTestWdg','CustomLayoutHelpWdg', 'CustomLayoutEditSaveCmd', 'CustomLayoutActionCbk']
from pyasm.common import  jsondumps, jsonloads, TacticException, Environment
from pyasm.search import Search, SearchType
from pyasm.biz import Project
from pyasm.web import DivWdg, Table, HtmlElement, SpanWdg, Widget, WebContainer
from pyasm.widget import IconWdg
from pyasm.widget import TextWdg, TextAreaWdg, XmlWdg, HiddenWdg, SelectWdg
from pyasm.command import Command
from pyasm.common import XmlException, Xml,  TacticException
from tactic.ui.container import Menu, MenuItem, SmartMenu
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg

from tactic.ui.widget import ButtonRowWdg, ButtonNewWdg, ActionButtonWdg, SwapDisplayWdg, IconButtonWdg


class CustomLayoutHelpWdg(BaseRefreshWdg):
    '''Showing sample code when clicking on the Show hint button'''
    def get_display(my):
        data = my.kwargs.get('data')

        widget = TextAreaWdg()
        widget.add_styles("max-width: 600px; width: 500px; height: 300px")
        # don't parse it as it doesn't like <%, since we are providing these, should be safe.
        """
        # parse the xml to see if it is valid
        try:
            Xml(string=data, strip_cdata=True)
        except XmlException, e:
            widget.add( IconWdg("XML Parse Error", IconWdg.ERROR) )
            span = SpanWdg()
            span.add_style('color: #f44')
            span.add( "Error parsing xml [%s]:" % e.__str__() )
            widget.add(span)
        """
        value = Xml.to_html(data)
       
        widget.add(value)
        return widget



__all__.append("WidgetEditorWdg")
class WidgetEditorWdg(BaseRefreshWdg):
    def add_style(my, name, value=None):
        my.top.add_style(name, value)


    def get_display(my):
        element_name = my.kwargs.get("element_name")
        display_handler = my.kwargs.get("display_handler")
        display_options = my.kwargs.get("display_options")

        top = my.top
        top.add_class("spt_widget_editor_top")
        top.add_style("padding: 10px")
        top.add_style("width: 450px")
        top.add_color("background", "background")


        action_wdg = DivWdg()
        top.add(action_wdg)
        action_wdg.add_gradient("background", "background", -10)
        action_wdg.add_style("margin: -10px -10px 10px -10px")
        action_wdg.add_style("padding: 5px")

        """
        delete = ActionButtonWdg(title='Remove', tip='Remove from Canvas')
        action_wdg.add(delete)
        delete.add_style("float: right")
        delete.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var attr_top = bvr.src_el.getParent(".spt_widget_editor_top");
        var values = spt.api.get_input_values(attr_top, null, false);
        '''
        })
        """


        inject = ActionButtonWdg(title='Inject')
        action_wdg.add(inject)

        editor_id = my.kwargs.get("editor_id")


        inject.add_behavior( {
        'type': 'click_up',
        'editor_id': editor_id,
        'cbjs_action': r'''
        var attr_top = bvr.src_el.getParent(".spt_widget_editor_top");
        var values = spt.api.get_input_values(attr_top, null, false);

        //console.log(values);

        // load the widget
        var class_name = values['xxx_option|display_class'];


        // build up a kwargs
        var kwargs = {};
        for (key in values) {
            var parts = key.split("|");
            if (parts[0] == 'option') {
                var value = values[key];
                console.log(value);
                kwargs[parts[1]] = value;
            }
        }


        var activator = bvr.src_el;
        var top = activator.getParent(".spt_widget_editor_top");
        var view = activator.getAttribute("spt_view");

        var element = []
        if (view) {
            element.push("<element name='"+view+"'>");
        }
        else {
            element.push("<element>");
        }
        element.push("  <display class='"+class_name+"'>");
        for (key in kwargs) {
            if (!kwargs.hasOwnProperty(key) ) { continue; }
            var value = kwargs[key];
            if (value == "") { continue; }

            element.push("    <"+key+">" + value + "</"+key+">");
        }
        element.push("  </display>");
        element.push("</element>");

        spt.ace_editor.set_editor(bvr.editor_id);
        spt.ace_editor.insert_lines(element);

        var popup = bvr.src_el.getParent( ".spt_popup" );
        if (popup)
            spt.popup.close(popup);

        '''
        } )





        table = Table()
        top.add(table)
        table.add_color("color", "color")
        table.add_style("width: 100%")
        table.add_style("margin: 10px" )

        table.add_row()
        td = table.add_cell()
        td.add("Name:")
        td.add_style("width: 150px")
        td = table.add_cell()
        text = TextWdg("element_name")
        if element_name:
            text.set_value(element_name)
        td.add(text)


        widget_key = ''
        display_class = display_handler

        div = DivWdg()
        top.add(div)
        div.add_class("spt_element_top")

        from tactic.ui.manager import WidgetClassSelectorWdg

        class_labels = ['-- Class Path--']
        class_values = ['__class__']

        # add the widget information
        #class_labels = ['Raw Data', 'Formatted', 'Expression', 'Expression Value', 'Button', 'Link', 'Gantt', 'Hidden Row', 'Custom Layout', '-- Class Path --']
        #class_values = ['raw_data', 'format', 'expression', 'expression_value', 'button', 'link', 'gantt', 'hidden_row', 'custom_layout', '__class__']
        widget_class_wdg = WidgetClassSelectorWdg(widget_key=widget_key, display_class=display_class, display_options=display_options,class_labels=class_labels,class_values=class_values, prefix='option', show_action=False)

        div.add(widget_class_wdg)


        return top










class CustomLayoutEditWdg(BaseRefreshWdg):

    def get_title_wdg(my, title, content_id=None, is_on=True):
        title_wdg = DivWdg()
        title_wdg.add_style("margin: -1")
        title_wdg.add_style("height: 25px")

        title_wdg.add_color("background", "background", -10)
        title_wdg.add_styles("padding: 5px")
        title_wdg.add_border()


        table = Table()
        title_wdg.add(table)
        table.add_row()
        table.add_cell("<b>%s:</b>" % title)

        hint = None

        if title == "Behaviors":
            hint = IconButtonWdg(title="Show Example", icon=IconWdg.HELP)
            data = '''<behavior class="custom_css_class">
                    { "type": "click_up", 
                    "cbjs_action": "spt.alert('clicked')"}
</behavior>''' 
 
    
          
        elif title == "Styles":
            hint = ButtonNewWdg(title="Show Example", icon=IconWdg.HELP)
            data = '''
.frame_container {
            border: 1px solid #000000;
            margin: 12px; 
            padding: 10px;
          }
.heading {
        color: gold;
}
'''
        elif title == "kwargs":
            hint = ButtonNewWdg(title="Show Example", icon=IconWdg.HELP)
            data = '''
    This is where you can define keyword arguments (options) for your Custom Layout:

    {
    'basic_option': 'You can describe your option here',
    'advanced_option': { 'descriptiom' : 'You can describe your option here and in type specify what type of edit widget is used to display the option.',
                         'category': 'kwargs',
                         'type': 'TextWdg'
                    }
}
'''
           
            
        elif title == "HTML":
            hint = IconButtonWdg(title="Show Example", icon=IconWdg.HELP)

            data = '''<div><div><b>Layout Title</b></div><br/>
<%
    x = 7
    y = 28
%>     
<br/>
<div class="heading">Sub-heading</div>
<br/>
</div>

<%

    context.write("<div>You can also add some content using context.write() to show the value of the variable x : %s. If outside the %% tag, you can do ${y} as shown below.<div>"%x)

%>


            
<element name="user_list" title="Users" width="100%">
  <display class="tactic.ui.panel.FastTableLayoutWdg">
    <search_type>sthpw/login</search_type>
    <view>table</view>
    <do_search>true</do_search>
    <expression>@SOBJECT(sthpw/login['@LIMIT', ${y}])</expression>
    <show_select>false</show_select>
  </display>
</element>



    '''
        if hint:
            td = table.add_cell(hint)
            td.add_style("padding-left: 10px")

            hint.add_behavior({
                'type': 'click_up',
                'data' : data,
                'cbjs_action': '''spt.api.load_popup('%s Example', 'tactic.ui.tools.CustomLayoutHelpWdg', {data : bvr.data});'''% title
                })

        return title_wdg




    def get_display(my):
        my.editor_id = ''
        top = my.top
        top.add_class("spt_custom_layout_top")
        #top.add_style("padding: 20px")
        top.add_color("color", "color")
        top.add_color("background", "background")
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)
        inner.add_style("margin: -1px")
        inner.add_class("spt_custom_layout_inner")


        my.plugin = None

        # Disabling for now until we can actually get this working.
        """
        inner.add_behavior( {
            'type': 'unload',
            'cbjs_action': '''
            if (bvr.src_el.hasClass("SPT_CHANGED") ) {
                if (!confirm("Changes have been made.  Are you sure?") ) {
                    throw("Aborting changes");
                }
            }
            var top = bvr.src_el.getParent(".spt_custom_layout_top");
            if (!top) {
                return;
            }
            var tab_top = spt.tab.set_tab_top(top);
            // it's possible there is no tab 
            if (tab_top) {
                var element_name = spt.tab.get_selected_element_name();
                top.setAttribute("spt_selected", element_name);
            }

            '''
        } )
        """


        inner.add_relay_behavior( {
            'type': 'change',
            'bvr_match_class': 'spt_input',
            'cbjs_action': '''
            var inner = bvr.src_el.getParent(".spt_custom_layout_inner");
            inner.addClass("SPT_CHANGED");
            '''
        } )


        table = Table()
        table.set_max_width()
        inner.add(table)
        table.add_row()

        search = Search("config/widget_config")
        search.add_op('begin')
        search.add_filter("category", "CustomLayoutWdg")
        search.add_filter("search_type", "CustomLayoutWdg")
        search.add_op('or')
        #search.add_order_by("folder")
        search.add_order_by("view")

        configs = search.get_sobjects()

        folders = []
        no_folders = []
        templates = []
        # reorder based on folders
        for config in configs:
            view = config.get_value("view")
            if view.startswith("__template__"):
                templates.append(config)
            elif view.find(".") == -1:
                no_folders.append(config)
            else:
                folders.append(config)

        configs = templates
        configs.extend(folders)
        configs.extend(no_folders)



        view = my.kwargs.get("view")
        if view:
            view = view.replace("/", ".")
        if view == '__new__':
            cur_config = None
        if view:
            search = Search("config/widget_config")
            search.add_op('begin')
            search.add_filter("category", "CustomLayoutWdg")
            search.add_filter("search_type", "CustomLayoutWdg")
            search.add_op('or')

            search.add_filter("view", view)
            cur_config = search.get_sobject()
        else:
            view = ""
            cur_config = None



        table.add_row()

        table.add_border()


        left = table.add_cell()
        right = table.add_cell()


        left.add_color("background", "background3")
        left.add_color("color", "color3")
        #left.add_style("max-width: 250px")
        # use width instead so the left div doesn't jiggle when clicked on
        left.add_style("width: 250px")
        left.add_style("min-width: 200px")


        # add in a context menu
        menu = my.get_context_menu()
        menus = [menu.get_data()]

        dir_menu = my.get_dir_context_menu()
        dir_menus = [dir_menu.get_data()]

        menus_in = {
            'LAYOUT_CTX': menus,
            'DIR_LAYOUT_CTX': dir_menus,
        }
        SmartMenu.attach_smart_context_menu( left, menus_in, False )



        left_div = DivWdg()
        left_div.add_class("spt_views_top")
        left.add(left_div)
        left.add_style("vertical-align: top")
        left_div.add_style("width: 250px")
        left_div.add_style("height", "100%")

        left_div.add_style("padding-bottom: 15px")
        left_div.set_unique_id()
        left_div.add_smart_styles( "spt_custom_layout_item", {
            'padding': '3px 6px 3px 10px'
        } )


        left_div.add_relay_behavior( { 
            'type': 'click',
            'bvr_match_class': 'spt_custom_layout_item',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_custom_layout_top");
            var content = top.getElement(".spt_custom_layout_content");
            var view = bvr.src_el.getAttribute("spt_view");

            top.setAttribute("spt_view", view)
            spt.app_busy.show("Loading view ["+view+"]");
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        } )


        bg_color = left_div.get_color("background3")
        bg_color2 = left_div.get_color("background3", -10)

        left_div.add_relay_behavior( {
            'type': 'mouseover',
            'bg_color': bg_color2,
            'bvr_match_class': 'spt_custom_layout_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", bvr.bg_color);
            '''
        } )

        left_div.add_relay_behavior( {
            'type': 'mouseout',
            'bg_color': bg_color2,
            'bvr_match_class': 'spt_custom_layout_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", "");
            '''
        } )
        
        error_msgs = []


        title_wdg = DivWdg()
        left_div.add(title_wdg)
        title_wdg.add("<b>Views</b>")
        title_wdg.add_color("color", "color")
        title_wdg.add_color("background", "background", -10)
        title_wdg.add_color("color", "color")
        title_wdg.add_style("padding: 15px 10px 10px 10px")
        title_wdg.add_style("height: 16px")
        title_wdg.add_style("margin: -2px -1px 10px -2px")
        title_wdg.add_border()
        left_div.add_style("width: 100%")


        web = WebContainer.get_web();
        folder_states = web.get_form_value("folder_states")
        if folder_states:
            try:
                folder_states = jsonloads(folder_states)
            except Exception, e:
                print "WARNINIG: can't parse json string [%s]" % folder_states
                folder_states = {}
        else:
            folder_states = {}

        folder_text = TextAreaWdg("folder_states")
        folder_text.add_style("display: none")
        folder_text.set_value( jsondumps(folder_states) )
        left_div.add(folder_text)
        folder_text.add_class("spt_folder_states")

        left_div.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_folder',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_views_top");
            var states_el = top.getElement(".spt_folder_states");
            value = states_el.value;
            states = JSON.parse(value);

            var swap_top = bvr.src_el;
            var state = swap_top.getAttribute("spt_state");
            var folder = bvr.src_el.getAttribute("spt_folder");

            if (state == "on") {
                states[folder] = "closed";
            }
            else {
                states[folder] = "open";     
            }

            states_el.value = JSON.stringify(states);
            
            '''
        } )


        content_div = DivWdg()
        left_div.add_widget(content_div, "content")
        content_div.add_color("color", "color3")


        last_folder = None
        folder_wdgs = {}
        folder_wdgs["/"] = left_div
        my.num_views = len(configs)
        for config in configs:

            folder = config.get_value("folder", no_exception=True)
            config_view = config.get_value("view")
            display_view = config_view

            if not folder:
                parts = config_view.split(".")
                if len(parts) > 1:
                    folder = "/".join(parts[:-1])
                    display_view = parts[-1]
                else:
                    #folder = "-- no folder --"
                    folder = "/"

            if folder == "__templates__":
                is_template = True
            else:
                is_template = False


            folder_wdg = folder_wdgs.get(folder)
            if folder_wdg:
                folder_content = folder_wdg.get_widget("content")
            else:
                parts = folder.split("/")

                # need to find the leaf folder, creating on the way, if
                # necessary
                parent_wdg = folder_wdgs.get("/")
                for i in range(1, len(parts)+1):

                    # find the folder, if it exists
                    folder = "/".join(parts[0:i])
                    folder_wdg = folder_wdgs.get(folder)

                    if folder_wdg:
                        parent_wdg = folder_wdg
                        continue

                    title = parts[i-1]


                    # else create a new one
                    folder_wdg = DivWdg()
                    if i != 1:
                        folder_wdg.add_style("padding-left: 13px")

                    # add it to the parent and remember this as the last parent
                    parent_wdg.get_widget("content").add(folder_wdg)
                    parent_wdg = folder_wdg

                    # add it to the list
                    folder_wdgs[folder] = folder_wdg

                    # remember it as the parent
                    parent_wdg = folder_wdg

                    # fill it in
                    icon = IconWdg(folder, IconWdg.FOLDER, inline=False)
                    icon.add_style("margin-top: -2px")
                    icon.add_style("margin-left: -5px")

                    folder_header = DivWdg()
                    folder_content = DivWdg()


                    from tactic.ui.widget import SwapDisplayWdg
                    swap = SwapDisplayWdg()
                    folder_wdg.add(swap)
                    swap.set_title_wdg(folder_header)
                    folder_wdg.add_widget(folder_content, "content")
                    swap.add_class("spt_folder")
                    swap.add_attr("spt_folder", folder)

                    if folder_states.get(folder) == "open":
                        is_on = True
                    else:
                        is_on = False

                    swap.set_on(is_on)
                    if not is_on:
                        folder_content.add_style("display: none")


                    unique_id = folder_content.set_unique_id("content")
                    swap.set_content_id(unique_id)

                    folder_header.add(icon)
                    folder_header.add(title)
                    folder_header.add_style("margin-top: 3px")
                    folder_header.add_style("margin-bottom: 3px")
                    folder_header.add_color("color", "color3")
                    if folder == "-- no folder --":
                        folder_header.add_style("opacity: 0.5")
                        folder_header.add_style("font-style: italic")
                    else:
                        SmartMenu.assign_as_local_activator( folder_header, 'DIR_LAYOUT_CTX' )
                        folder_header.add_attr("spt_folder", folder)



            config_div = DivWdg()
            folder_content.add(config_div)
            if folder != "/":
                config_div.add_style("padding-left: 32px")
            else:
                config_div.add_style("padding-left: 5px")

            config_div.add_class("spt_custom_layout_item")
            icon = IconWdg("Custom Layout View", IconWdg.VIEW, inline=False)
            config_div.add(icon)

            config_div.add(display_view)
            config_div.add_attr("spt_view", config_view)
            config_div.add_attr("spt_search_key", config.get_search_key())

            config_div.add_class("hand")

            SmartMenu.assign_as_local_activator( config_div, 'LAYOUT_CTX' )



        right.add_style("vertical-align: top")
        right.add_color("background", "background", -3)
        right_div = DivWdg()
        right.add(right_div)
        right_div.add_color("color", "color")
        right_div.add_style("min-width: 800px")
        right_div.add_style("min-height: 500px")
        right_div.add_class("spt_custom_layout_content")

      

        #right_div.add_style("padding: 20px")
        is_new = False
        if view == '__new__':
            is_new = True
            

            """
            #TODO: include this Click to Add feature back.
            if not my.num_views:
                arrow_div = DivWdg()
                right_div.add(arrow_div)
                icon = IconWdg("Click to Add", IconWdg.ARROW_UP_LEFT_32)
                icon.add_style("margin-top: -20")
                icon.add_style("margin-left: -15")
                icon.add_style("position: absolute")
                arrow_div.add(icon)
                arrow_div.add("&nbsp;"*5)
                arrow_div.add("<b>Click to Add</b>")
                arrow_div.add_style("position: relative")
                arrow_div.add_style("margin-top: -5px")
                arrow_div.add_style("margin-left: 90px")
                arrow_div.add_style("float: left")
                arrow_div.add_style("padding: 25px")
                arrow_div.set_box_shadow("1px 1px 4px 4px")
                arrow_div.set_round_corners(30)
                arrow_div.add_color("background", "background")

                nothing_wdg = DivWdg()
                right_div.add(nothing_wdg)
                nothing_wdg.add_border()
                nothing_wdg.add("<b>No View Created</b>")
                nothing_wdg.add("<b>View Created</b>")
                nothing_wdg.add_style("padding: 30px")
                nothing_wdg.add_color("color", "color3")
                nothing_wdg.add_color("background", "background3")
                nothing_wdg.add_style("width: 300px")
                nothing_wdg.add_style("text-align: center")
                nothing_wdg.add_style("margin: 60px auto")

            else:

                nothing_wdg = DivWdg()
                right_div.add(nothing_wdg)
                nothing_wdg.add_border()
                nothing_wdg.add("<b>No View Selected</b>")
                nothing_wdg.add_style("padding: 30px")
                nothing_wdg.add_color("color", "color3")
                nothing_wdg.add_color("background", "background3")
                nothing_wdg.add_style("width: 300px")
                nothing_wdg.add_style("text-align: center")
                nothing_wdg.add_style("margin: 60px auto")

            """
        shelf_wdg = DivWdg('place holder')
        right_div.add(shelf_wdg, "shelf_wdg")

       
        if not view:
            shelf_wdg = my.get_shelf_wdg()
            right_div.add(shelf_wdg, "shelf_wdg")

            # at the first widget load, don't draw the view text input 
            nothing_wdg = DivWdg()
            
            nothing_wdg.add_border()
            nothing_wdg.add("<b>No View Selected</b>")
            nothing_wdg.add_style("padding: 30px")
            nothing_wdg.add_color("color", "color3")
            nothing_wdg.add_color("background", "background3")
            nothing_wdg.add_style("width: 300px")
            nothing_wdg.add_style("text-align: center")
            nothing_wdg.add_style("margin: 60px auto")
            right_div.add(nothing_wdg)

            
        else:
            if is_new:
                html = ''
                style = ''
                behavior_nodes = []
                htmls = []
                mako = ''
                kwargs = ''
                widget_type = ''
                my.plugin = None
            else:

                pretty = True
                remove_blank_text = True

                xml = cur_config.get_xml_value("config", strip_cdata=True, remove_blank_text=remove_blank_text)

                widget_type = cur_config.get_value("widget_type")

                style_node = xml.get_value("config/%s/html/style" % view)
                style = style_node

                mako = xml.get_value("config/%s/mako" % view)
                kwargs = xml.get_value("config/%s/kwargs" % view)

                behavior_nodes = xml.get_nodes("config/%s/behavior" % view)

                html_nodes = xml.get_nodes("config/%s/html/*" % view)
                htmls = []
                for node in html_nodes:
                    if xml.get_node_name(node) == 'style':
                        continue
                    # check for user error of putting behavior nodes inside html
                    if xml.get_node_name(node) == 'behavior':
                        bvr_html = xml.to_string(node)
                        error_msgs.append("behavior node found inside html node [%s]. <br><br>It should be on the same level as the html node. Please put them in the Behaviors section in the Custom Layout Editor.<br> "%bvr_html)
                        #continue

                    html = xml.to_string(node, pretty=pretty)
                    htmls.append(html)

                if not html_nodes:
                    try:
                        raw_data = cur_config.get_value('config')
                        Xml(string=raw_data, strip_cdata=True)
                    except XmlException, e:
                        for text in ['config', view, 'html']:
                            raw_data = raw_data.replace('<%s>' %text, '')
                            raw_data = raw_data.replace('</%s>'%text, '')
                            raw_data = raw_data.replace( "<![CDATA[\n<%", "<%")
                            raw_data = raw_data.replace( "%> ]]>", "%>")
                        htmls.append(raw_data)
                        
                        value = Xml.to_html(raw_data)
                        pre = HtmlElement.pre(value)
                        pre.add_attr("wrap", "true")
                        error_msgs.append("Syntax error found: <br> %s<br><br> %s" %(e.__str__(), pre.get_buffer_display()))




                # find out if this custom layout belongs to a plugin
                expr = "@SOBJECT(config/plugin_content.config/plugin)"
                my.plugin = Search.eval(expr, cur_config, single=True)


            if error_msgs:
                left_div.add_behavior({
                    'type': 'load',
                    'error_msg' : error_msgs,
                    'cbjs_action' : '''spt.alert(bvr.error_msg.join('<br>'), {type : 'html'});'''
                })



            # html
            html_div = DivWdg()
            
            html_div.set_name("HTML")
            html_div.add_style("height: 600px")


            text = TextAreaWdg("html")
            content_id = text.set_unique_id()
            title_wdg = my.get_title_wdg("HTML", content_id)
            html_div.add(title_wdg)

            # add in a context menu
            button = ActionButtonWdg(title="Image")
            html_div.add(button)

            text.add_style("width: 100%")
            text.add_style("height: 600px")
            text.add_style("min-height: 400px")
            text.add_style("font-size: 12px")
            text.add_style("font-family: courier")
            html = ''.join(htmls)
            html = html.replace( "&amp;", "&")

            # a final html conversion to ensure textarea draws properly
            html = Xml.to_html(html, allow_empty=True)
            if html:
                text.set_value(html)


            # add the editor
            from tactic.ui.app import AceEditorWdg
            editor = AceEditorWdg(width="100%", language="xml", code=html, show_options=False, editor_id='custom_layout_html')
            my.editor_id = editor.get_editor_id()
            html_div.add(editor)

            if cur_config:
                my.handle_image_inject(cur_config, button)

            shelf_wdg = my.get_shelf_wdg()
            right_div.set_widget(shelf_wdg, "shelf_wdg")

            shelf_wdg.add_style("overflow-x: hidden")
            shelf_wdg.add_style("overflow-y: hidden")
           

            view_wdg = DivWdg()
            shelf_wdg.add(view_wdg)

            view_wdg.add("<b>View: &nbsp;</b>")
            text = TextInputWdg(name="view")
            view_wdg.add(text)
            text.add_style("width: 350px")
            view_wdg.add_style("margin-top: 4px")
            view_wdg.add_style("margin-left: 10px")
            view_wdg.add_style("padding-left: 230px")
            text.add_class("spt_view")
            text.add_style("font-family: courier")
            if view != '__new__':
                text.set_value(view.replace(".", "/"))


            select = SelectWdg(name="widget_type")
            if widget_type:
                select.set_value(widget_type)
            view_wdg.add("<b>Type: &nbsp;</b>")
            view_wdg.add(select)
            select.set_option("values", "widget|theme|column|chart|report|dashboard")
            select.add_empty_option("-- None ---")

 

            # some hidden elements
            hidden = HiddenWdg("code")
            view_wdg.add(hidden)
            if cur_config:
                hidden.set_value(cur_config.get_code())





            hidden = HiddenWdg("selected")
            view_wdg.add(hidden)
            selected = web.get_form_value("selected")
            if not selected:
                selected = my.kwargs.get("selected")
            if not selected:
                selected = "HTML"

            # start tab here
            from tactic.ui.container import TabWdg
            tab = TabWdg(selected=selected, show_add=False, show_remove=False, tab_offset="10px", show_context_menu=False, allow_drag=False)
            tab.add_style("margin: 0px -2px 0px -2px")
            right_div.add(tab)


            tab.add(html_div)

            # Mako
            mako_div = DivWdg()
            tab.add(mako_div)
            mako_div.set_name("python")

            # replace the placeholder
            
            text = TextAreaWdg("mako")
            text.add_class("spt_mako")
            text.add_class("spt_python")
            content_id = text.set_unique_id()

            title_wdg = my.get_title_wdg("Python", content_id, is_on=True)
            mako_div.add(title_wdg)

            mako_div.add(text)
            text.add_style("width: 100%")
            text.add_style("height: 300px")
            text.add_style("min-height: 300px")
            text.add_style("font-size: 12px")
            text.add_style("font-family: courier")
            text.set_value(mako)

            # styles
            style_div = DivWdg()
            tab.add(style_div)
            style_div.set_name("Styles")

            text = TextAreaWdg("style")
            text.add_class("spt_style")
            content_id = text.set_unique_id()
            #text.add_style("display: none")

            title_wdg = my.get_title_wdg("Styles", content_id, is_on=True)
            style_div.add(title_wdg)

            style_div.add(text)
            text.add_style("width: 100%")
            text.add_style("height: 300px")
            text.add_style("min-height: 300px")
            text.add_style("font-size: 12px")
            text.add_style("font-family: courier")
            text.set_value(style)

            #right_div.add("<br/>"*2)

            # behaviors
            behavior_div = DivWdg()
            tab.add(behavior_div)
            behavior_div.set_name("Behaviors")

            text = TextAreaWdg("behavior")
            text.add_class("spt_behavior")
            content_id = text.set_unique_id()
            #text.add_style("display: none")

            title_wdg = my.get_title_wdg("Behaviors", content_id, is_on=True)
            behavior_div.add(title_wdg)

            behavior_div.add(text)
            text.add_style("width: 100%")
            text.add_style("height: 450px")
            text.add_style("min-height: 300px")
            text.add_style("font-size: 12px")
            text.add_style("font-family: courier")

            value = []
            for behavior_node in behavior_nodes:
                value.append( xml.to_string(behavior_node))
            behavior_str = "\n\n".join(value)

            text.set_value(behavior_str)

            # This breaks the beahviors into separate intefaces
            """
            behavior_div.add_color("background", "background", -5)
            table = Table()
            behavior_div.add(table)
            if not behavior_nodes:
                behavior_nodes.append("__new__")

            from tactic.ui.widget import SwapDisplayWdg
            for behavior_node in behavior_nodes:
                table.add_row()

                if behavior_node == "__new__":
                    name = ""
                    value = ""
                else:
                    name = Xml.get_attribute(behavior_node, "class")
                    value = xml.to_string(behavior_node)


                td = table.add_cell()
                td.add_style("vertical-align: top")
                swap = SwapDisplayWdg()
                td.add(swap)
                
                bvr_name_text = TextInputWdg(name="behavior_name")
                #td.add(bvr_name_text)
                swap.set_title_wdg(bvr_name_text)
                bvr_name_text.set_value(name)

                content_div = DivWdg()
                td.add(content_div)
                unique_id = content_div.set_unique_id("behavior")
                swap.set_content_id(unique_id)
                content_div.add_style("display: none")

                bvr_text = TextAreaWdg("behavior_content")
                content_div.add(bvr_text)
                bvr_text.set_value( value )
                bvr_text.add_style("width: 600px")
                bvr_text.add_style("min-height: 400px")
                bvr_text.add_style("padding: 5px")
                bvr_text.add_style("margin: 10 20 20 25")

            """



            # kwargs
            kwargs_div = DivWdg()
            tab.add(kwargs_div)
            kwargs_div.set_name("kwargs")

            text = TextAreaWdg("kwargs")
            text.add_class("spt_kwargs")
            content_id = text.set_unique_id()

            title_wdg = my.get_title_wdg("kwargs", content_id, is_on=True)
            kwargs_div.add(title_wdg)

            kwargs_div.add(text)
            text.add_style("width: 100%")
            text.add_style("height: 300px")
            text.add_style("min-height: 300px")
            text.add_style("font-size: 12px")
            text.add_style("font-family: courier")
            if kwargs:
                text.set_value(kwargs)







            # check-in
            files_div = DivWdg()
            tab.add(files_div)
            files_div.set_name("Files")

            text = TextAreaWdg("Files")
            content_id = text.set_unique_id()
            #text.add_style("display: none")

            title_wdg = my.get_title_wdg("Files", content_id, is_on=True)
            files_div.add(title_wdg)

            search = Search("config/widget_config")
            search.add_filter("category", "CustomLayoutWdg")
            search.add_filter("view", view)
            config = search.get_sobject()

            if config:

                button = ActionButtonWdg(title="Check-in")
                files_div.add(button)
                search_key = config.get_search_key()
                button.add_behavior( {
                    'type': 'click_up',
                    'search_key': search_key,
                    'cbjs_action': '''
                    var class_name = 'tactic.ui.widget.CheckinWdg';
                    var kwargs = {
                        search_key: bvr.search_key
                    };
                    spt.panel.load_popup("Check-In", class_name, kwargs);
                    '''
                } )

                search = Search("sthpw/snapshot")
                search.add_filter("version", -1)
                search.add_parent_filter(config)
                search.set_limit(10)
                snapshots = search.get_sobjects()

                element_names = ['preview','files', 'web_path', 'file_size']


                from tactic.ui.panel import FastTableLayoutWdg
                panel = FastTableLayoutWdg(search_type="sthpw/snapshot",view="table",show_shelf=False, element_names=element_names, edit=False)
                panel.set_sobjects(snapshots)
                files_div.add(panel)
            else:


                msg_div = DivWdg()
                files_div.add(msg_div)
                msg_div.add("Custom Layout must be saved before files can be checked in")
                msg_div.add_color("background", "background")
                msg_div.add_style("padding: 30px")

 



        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top



    def get_shelf_wdg(my):

        shelf_wdg = DivWdg()

        shelf_wdg.add_style("height: 35px")
        shelf_wdg.add_color("background", "background", -10)
        shelf_wdg.add_style("padding: 3px")
        shelf_wdg.add_style("margin: -2px -2px 8px -2px")
        shelf_wdg.add_border(size="1px 1px 1px 0px")


        # refresh button
        button_row = ButtonRowWdg()
        shelf_wdg.add(button_row)
        button_row.add_style("float: left")
        button = ButtonNewWdg(title="Refresh", icon=IconWdg.REFRESH)
        button_row.add(button)

        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Refreshing ...")
            var top = bvr.src_el.getParent(".spt_custom_layout_top");
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        } )


        # Save button
        button = ButtonNewWdg(title="Save", icon=IconWdg.SAVE)
        button_row.add(button)

        button.add_behavior( {
            'type': 'click_up',
            'editor_id': my.editor_id,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_custom_layout_top");
            var values = spt.api.Utility.get_input_values(top, null, false);

            var cmd = 'tactic.ui.tools.CustomLayoutEditSaveCmd';

            //var html = values.html;
            if (!bvr.editor_id) {
                spt.alert('There is no view to save. Please create a view or select an exixting view.');
                return;
            }

            spt.ace_editor.set_editor_top(top);
            var html = spt.ace_editor.get_value();

            var view = values.view;
            var widget_type = values.widget_type;
            var code = values.code;
            var style = values.style;
            var behavior = values.behavior;
            var mako = values.mako;
            var kwargs = values.kwargs;

            if (!view) {
                spt.alert("A view name must be provided to save. e.g. 'custom/task_list' will create a custom folder with a task_list view");
                return;
            }

            spt.app_busy.show("Saving ["+view+"] ...")

            var kwargs = {
                code: code,
                view: view,
                widget_type: widget_type,
                html: html,
                style: style,
                behavior: behavior,
                mako: mako,
                kwargs: kwargs

            }
            spt.app_busy.show("Saving Custom Layout");
            var server = TacticServerStub.get();
            try {
                server.execute_cmd(cmd, kwargs);
                spt.app_busy.hide();
            } catch(e) {
                spt.app_busy.hide();
                spt.error(spt.exception.handler(e));
                return;
            }
            

            top.setAttribute("spt_view", view);
            spt.panel.refresh(top);

            '''
        } )


        # add new button
        button = ButtonNewWdg(title="Add New", icon=IconWdg.ADD)
        button_row.add(button)


        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_custom_layout_top");
            top.setAttribute("spt_view", "__new__");
            spt.panel.refresh(top);
            '''
        } )


        # add new button
        button = ButtonNewWdg(title="Add Elements", icon=IconWdg.GEAR, show_arrow=True)
        button_row.add(button)

        # add in a context menu
        menu = my.get_inject_menu()
        menus = [menu.get_data()]
        SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'DG_BUTTON_CTX': menus } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "DG_BUTTON_CTX", True )





        button = ButtonNewWdg(title="Test", icon=IconWdg.ARROW_RIGHT)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_custom_layout_top");
            var values = spt.api.Utility.get_input_values(top, null, false);

            spt.ace_editor.set_editor_top(top);
            values.html = spt.ace_editor.get_value();
            values.is_test = true;

            if (!values.view && !values.html) {
                spt.alert('No view on the left has been selected.');
                values.view = "__test__";
            }

            if (!values.view) {
                values.view = "__test__"
            }



            var class_name = 'tactic.ui.tools.CustomLayoutEditTestWdg';
            try {
                var popup = spt.panel.load_popup("Test Custom Layout", class_name, values);
                popup.top = top;
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }

        ''' } )

        #help_button = ActionButtonWdg(title="?", tip="Show Layout Editor Help", size='s')
        #shelf_wdg.add(help_button)
        #help_button.add_style("float: left")

        button = ButtonNewWdg(title="Link Actions", icon=IconWdg.LINK, show_arrow=True)
        button_row.add(button)

        menu = my.get_link_menu()
        menus = [menu.get_data()]
        SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'DG_BUTTON_CTX': menus } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "DG_BUTTON_CTX", True )





        help_button = ButtonNewWdg(title="Help", icon=IconWdg.HELP)
        button_row.add(help_button)
        help_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.help.set_top();
            spt.help.load_alias("custom-layout-editor|tactic-developer_developer_custom-layout-editor");
            '''
        } )




        return shelf_wdg



    def get_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Test View')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_custom_layout_top");
            var view = activator.getAttribute("spt_view");

            var kwargs = {
                view: view,
                include_mako: true,
                is_test: true
            }

            var class_name = 'tactic.ui.tools.CustomLayoutEditTestWdg';
            try {
                spt.panel.load_popup("Test Custom Layout", class_name, kwargs);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }

            top.last_view = view;

        ''' } )

        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Inject Compact View')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_custom_layout_top");
            var view = activator.getAttribute("spt_view");

            var values = []
            values.push("<element view='"+view+"'/>");
            spt.ace_editor.set_editor_top(top);
            spt.ace_editor.insert_lines(values);

        ''' } )

        menu_item = MenuItem(type='action', label='Inject Detailed View')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_custom_layout_top");
            var view = activator.getAttribute("spt_view");

            var values = []
            values.push("<element name='"+view+"'>");
            values.push("  <display class='tactic.ui.panel.CustomLayoutWdg'>");
            values.push("    <view>" + view + "</view>");
            values.push("  </display>");
            values.push("</element>");

            spt.ace_editor.set_editor_top(top);
            spt.ace_editor.insert_lines(values);

        ''' } )

        # FIXME: this doesn't work because the xml must be changed as well
        """
        menu_item = MenuItem(type='action', label='Copy View')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_custom_layout_top");
            var view = activator.getAttribute("spt_view");
            var parts = view.split(".");
            var last = parts[parts.length-1];

            var new_view = "copy_of_" + last;
            var search_key = activator.getAttribute("spt_search_key");

            var server = TacticServerStub.get();
            server.clone_sobject(search_key, {view: new_view} );
             

            var top = activator.getParent(".spt_custom_layout_top");
            spt.panel.refresh(top);
            spt.app_busy.hide();
        ''' } )
        """



        menu_item = MenuItem(type='separator')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Copy View')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);

            var view = activator.getAttribute("spt_view");
            var kwargs = {
                'action': 'copy_view',
                'view': view
            }
            var class_name = 'tactic.ui.tools.CustomLayoutActionCbk';

            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

            var top = activator.getParent(".spt_custom_layout_top");
            spt.panel.refresh(top);
            spt.app_busy.hide();
        ''' } )



        menu_item = MenuItem(type='action', label='Delete View')
        menu.add(menu_item)
        if False:
            # Disabled for now
            menu_item.add_behavior({
                'type': 'click_up',
                'plugin': my.plugin.get_value("code"),
                'cbjs_action': '''
                alert("View belongs to plugin ["+bvr.plugin+"]");
                '''
            } )
        else:
            menu_item.add_behavior({
                'type': 'click_up',
                'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var top = activator.getParent(".spt_custom_layout_top");

                var view = activator.getAttribute("spt_view");
                var search_key = activator.getAttribute("spt_search_key");

                if (!confirm("Are you sure you wish to delete view["+view+"]?")) {
                    return;
                }

                spt.app_busy.show("Deleting view ["+view+"]");
                var server = TacticServerStub.get();
                server.delete_sobject(search_key);

                top.setAttribute("spt_view", "");
                top.setAttribute("spt_widget_type", "");

                var top = activator.getParent(".spt_custom_layout_top");
                spt.panel.refresh(top);
                spt.app_busy.hide();
            ''' } )



        menu_item = MenuItem(type='separator')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Add to Side Bar')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
 
            var activator = spt.smenu.get_activator(bvr);

            var view = activator.getAttribute("spt_view");

            var element_name = view.replace(/\//g, "_");
            var kwargs = {
                class_name: 'LinkWdg',
                display_options: {
                    widget_key: 'custom_layout',
                    view: view
                }
            }

            var server = TacticServerStub.get();
            var info = server.add_config_element("SideBarWdg", "definition", element_name, kwargs);
            var info = server.add_config_element("SideBarWdg", "project_view", element_name, kwargs);

            spt.panel.refresh("side_bar");
        '''
        } )



        return menu


    def get_dir_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Copy Folder')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''

            var activator = spt.smenu.get_activator(bvr);

            var folder = activator.getAttribute("spt_folder");
            var kwargs = {
                'action': 'copy_folder',
                'folder': folder
            }
            var class_name = 'tactic.ui.tools.CustomLayoutActionCbk';

            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

            var top = activator.getParent(".spt_custom_layout_top");
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        })

 
        menu_item = MenuItem(type='separator')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Delete Folder')
        menu.add(menu_item)
        menu_item.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''

            var activator = spt.smenu.get_activator(bvr);

            var folder = activator.getAttribute("spt_folder");

            if (! confirm("Delete folder ["+folder+"]") ) {
                return;
            }

            var kwargs = {
                'action': 'delete_folder',
                'folder': folder,
            }
            var class_name = 'tactic.ui.tools.CustomLayoutActionCbk';

            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

            var top = activator.getParent(".spt_custom_layout_top");
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        })

        return menu





    def get_link_menu(my):
        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        search = Search("config/url")
        search.add_filter("url", "/index")
        url = search.get_sobject()
        if url:
            widget = url.get_xml_value("widget")
            view = widget.get_value("element/display/view")

            project_code = Project.get_project_code()
            url_str = "/tactic/%s/" % project_code

            menu_item = MenuItem(type='action', label='Open Index URL')
            menu.add(menu_item)

            menu_item.add_behavior( {
                'type': 'click_up',
                'url': url_str,
                'cbjs_action': '''
                window.open(bvr.url);
                '''
            } )


            menu_item = MenuItem(type='separator')
            menu.add(menu_item)


        if my.plugin:

            menu_item = MenuItem(type='action', label='Edit Plugin')
            menu.add(menu_item)

            plugin_dir = Environment.get_plugin_dir()

            menu_item.add_behavior( {
                'type': 'click_up',
                'dirname': my.plugin.get('rel_dir'),
                'plugin_dir': plugin_dir,
                'cbjs_action': '''
                var class_name = 'tactic.ui.app.PluginEditWdg';
                var kwargs = {
                    plugin_dir: bvr.plugin_dir + "/" + bvr.dirname
                };
                //spt.tab.set_main_body_tab();
                //spt.tab.add_new("Plugin Manager", "Plugin Manager", class_name, kwargs);
                spt.panel.load_popup("Plugin Manager", class_name, kwargs);
                '''
            } )


        else:


            menu_item = MenuItem(type='action', label='Create Plugin')
            menu.add(menu_item)

            plugin_dir = Environment.get_plugin_dir()

            menu_item.add_behavior( {
                'type': 'click_up',
                'plugin_dir': plugin_dir,
                'cbjs_action': '''
                var class_name = 'tactic.ui.app.PluginEditWdg';
                var kwargs = {
                    mode: "insert"
                };
                //spt.tab.set_main_body_tab();
                //spt.tab.add_new("Plugin Manager", "Plugin Manager", class_name, kwargs);
                spt.panel.load_popup("Plugin Manager", class_name, kwargs);
                '''
            } )



        menu_item = MenuItem(type='action', label='Open Plugin Manager')
        menu.add(menu_item)

        plugin_dir = Environment.get_plugin_dir()

        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.app.PluginWdg';
            var kwargs = {};
            spt.tab.set_main_body_tab();
            spt.tab.add_new("Plugin Manager", "Plugin Manager", class_name, kwargs);
            '''
        } )



        menu_item = MenuItem(type='separator')
        menu.add(menu_item)








        menu_item = MenuItem(type='action', label='Add to Side Bar', icon=IconWdg.LINK)
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_custom_layout_top");
            var values = spt.api.Utility.get_input_values(top, null, false);

            var view = values.view;

            var element_name = view.replace(/\//g, "_");
            var kwargs = {
                class_name: 'LinkWdg',
                display_options: {
                    widget_key: 'custom_layout',
                    view: view
                }
            }

            var server = TacticServerStub.get();
            var info = server.add_config_element("SideBarWdg", "definition", element_name, kwargs);
            var info = server.add_config_element("SideBarWdg", "project_view", element_name, kwargs);

            spt.panel.refresh("side_bar");


            '''
            } )



        menu_item = MenuItem(type='action', label='Set as Project URL', icon=IconWdg.LINK)
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': r'''

            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_custom_layout_top");
            var values = spt.api.Utility.get_input_values(top, null, false);

            var view = values.view;

            if (!view) {
                spt.alert("No view selected");
                return;
            }

            spt.app_busy.show("Saving index URL")

            var widget = [];
            widget.push( "<element name='index'>" );
            widget.push( "  <display class='tactic.ui.panel.CustomLayoutWdg'>" );
            widget.push( "      <view>"+view+"</view>" );
            widget.push( "  </display>" );
            widget.push( "</element>");
            widget = widget.join("\n");

            var server = TacticServerStub.get();
            var data = {
                url: '/index',
                widget: widget,
                description: 'Index Page'
            };

            var config = server.query("config/url", {filters:[['url','/index']], single:true})
            if (!config) {
                if (!confirm("Index already exists.  Do you wish to replace?")) {
                    return;
                }
                server.update(config, data);
            }
            else {
                server.insert("config/url", data);
            }

            spt.app_busy.hide();

            ''' } )





        menu_item = MenuItem(type='action', label='Add as Custom URL', icon=IconWdg.LINK)
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': r'''

            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_custom_layout_top");
            var values = spt.api.Utility.get_input_values(top, null, false);

            var html = values.html;
            var style = values.style;
            var view = values.view;
            var behavior = values.behavior;

            if (!view) {
                spt.alert("No view selected");
                return;
            }

            var widget = [];
            widget.push( "<element name='"+view+"'>" );
            widget.push( "  <display class='tactic.ui.panel.CustomLayoutWdg'>" );
            widget.push( "      <view>"+view+"</view>" );
            widget.push( "  </display>" );
            widget.push( "</element>");
            widget = widget.join("\n");


            var class_name = 'tactic.ui.panel.EditWdg';
            var kwargs = {
                search_type: "config/url",
                default: {
                    url: "/" + view,
                    widget: widget
                }
            }
            spt.panel.load_popup("Create URL", class_name, kwargs);
            '''
        } )


        menu_item = MenuItem(type='action', label='Show Custom URLs', icon=IconWdg.LINK)
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': r'''

            spt.tab.set_main_body_tab();

            var class_name = 'tactic.ui.panel.ViewPanelWdg';
            var kwargs = {
                search_type: 'config/url',
                view: 'table'
            };

            spt.app_busy.show("Loading Custom URLs");
            spt.tab.add_new("custom_url", "Custom URL", class_name, kwargs);
            spt.app_busy.hide();

            ''' } )

 

        return menu


         

    def get_inject_menu(my):
        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        # add login
        template = SimpleLoginTemplate()
        menu_item = MenuItem(type='action', label='Add Login Template')
        menu.add(menu_item)

        menu_item.add_behavior( {
            'type': 'click_up',
            'html': template.html,
            'style': template.style,
            'behavior': template.behavior,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            spt.app_busy.show("Adding login template");
            var top = activator.getParent(".spt_custom_layout_top");
            top.setAttribute("spt_view", "__new__");
            spt.panel.refresh(top);
            var server = TacticServerStub.get();

            var style_el = top.getElement(".spt_style");
            var behavior_el = top.getElement(".spt_behavior");
            style_el.value = bvr.style;
            behavior_el.value = bvr.behavior;

            setTimeout( function() {
                spt.ace_editor.set_editor_top(top);
                spt.ace_editor.set_value(bvr.html);
                spt.app_busy.hide();
            }, 500);
            '''
        } )



        # add raw side bar 
        template = RawMenuTemplate()
        menu_item = MenuItem(type='action', label='Add Raw Menu Template')
        menu.add(menu_item)

        menu_item.add_behavior( {
            'type': 'click_up',
            'html': template.html,
            'style': template.style,
            'behavior': template.behavior,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            spt.app_busy.show("Adding sidebar template");
            var top = activator.getParent(".spt_custom_layout_top");
            top.setAttribute("spt_view", "__new__");
            spt.panel.refresh(top);
            var server = TacticServerStub.get();

            var style_el = top.getElement(".spt_style");
            var behavior_el = top.getElement(".spt_behavior");
            style_el.value = bvr.style;
            behavior_el.value = bvr.behavior;

            setTimeout( function() {
                spt.ace_editor.set_editor_top(top);
                spt.ace_editor.set_value(bvr.html);
                spt.app_busy.hide();
            }, 500);
            '''
        } )




        # add menu 
        template = SimpleMenuTemplate()
        menu_item = MenuItem(type='action', label='Add Menu Template')
        menu.add(menu_item)

        menu_item.add_behavior( {
            'type': 'click_up',
            'html': template.html,
            'style': template.style,
            'behavior': template.behavior,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            spt.app_busy.show("Adding menu template");
            var top = activator.getParent(".spt_custom_layout_top");
            top.setAttribute("spt_view", "__new__");
            spt.panel.refresh(top);
            var server = TacticServerStub.get();

            var style_el = top.getElement(".spt_style");
            var behavior_el = top.getElement(".spt_behavior");
            style_el.value = bvr.style;
            behavior_el.value = bvr.behavior;

            setTimeout( function() {
                spt.ace_editor.set_editor_top(top);
                spt.ace_editor.set_value(bvr.html);
                spt.app_busy.hide();
            }, 500);
            '''
        } )



        # add sidebar 
        template = SimpleSidebarTemplate()
        menu_item = MenuItem(type='action', label='Add Side Bar Template')
        menu.add(menu_item)

        menu_item.add_behavior( {
            'type': 'click_up',
            'html': template.html,
            'style': template.style,
            'python': template.python,
            'behavior': template.behavior,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            spt.app_busy.show("Adding sidebar template");
            var top = activator.getParent(".spt_custom_layout_top");
            top.setAttribute("spt_view", "__new__");
            spt.panel.refresh(top);
            var server = TacticServerStub.get();

            var style_el = top.getElement(".spt_style");
            var behavior_el = top.getElement(".spt_behavior");
            var python_el = top.getElement(".spt_python");
            style_el.value = bvr.style;
            behavior_el.value = bvr.behavior;
            python_el.value = bvr.python;

            setTimeout( function() {
                spt.ace_editor.set_editor_top(top);
                spt.ace_editor.set_value(bvr.html);
                spt.app_busy.hide();
            }, 500);
            '''
        } )



        menu_item = MenuItem(type='separator')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Inject Widget')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'editor_id': my.editor_id,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.WidgetEditorWdg';
        var kwargs = {
            'editor_id': bvr.editor_id,
        };
        spt.panel.load_popup("Widget Editor", class_name, kwargs);
        '''
        } )


        menu_item = MenuItem(type='action', label='Inject Thumbnail')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'editor_id': my.editor_id,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.WidgetEditorWdg';
        var kwargs = {
            'editor_id': bvr.editor_id,
            'display_handler': 'pyasm.widget.ThumbWdg'
        }
        spt.panel.load_popup("Widget Editor", class_name, kwargs);
        '''
        } )

        menu_item = MenuItem(type='action', label='Inject Text Input')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'editor_id': my.editor_id,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.WidgetEditorWdg';
        var kwargs = {
            'editor_id': bvr.editor_id,
            'display_handler': 'tactic.ui.input.TextInputWdg'
        }
        spt.panel.load_popup("Widget Editor", class_name, kwargs);
        '''
        } )


        menu_item = MenuItem(type='action', label='Inject Look Ahead Text Input')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'editor_id': my.editor_id,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.WidgetEditorWdg';
        var kwargs = {
            'editor_id': bvr.editor_id,
            'display_handler': 'tactic.ui.input.LookAheadTextInputWdg'
        }
        spt.panel.load_popup("Widget Editor", class_name, kwargs);
        '''
        } )



        menu_item = MenuItem(type='action', label='Inject Layout')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'editor_id': my.editor_id,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.WidgetEditorWdg';

        var kwargs = {
            'editor_id': bvr.editor_id,
            'display_handler': 'tactic.ui.panel.ViewPanelWdg',
            'name': '',
            'display_options': {
            }
        };
        spt.panel.load_popup("Widget Editor", class_name, kwargs);
        '''
        } )



        menu_item = MenuItem(type='action', label='Inject Table')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'editor_id': my.editor_id,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.WidgetEditorWdg';

        var kwargs = {
            'editor_id': bvr.editor_id,
            'display_handler': 'tactic.ui.panel.FastTableLayoutWdg',
            'name': '',
            'display_options': {
                'show_shelf': 'false'
            }
        };
        spt.panel.load_popup("Widget Editor", class_name, kwargs);
        '''
        } )


        menu_item = MenuItem(type='action', label='Inject Calendar')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'editor_id': my.editor_id,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.WidgetEditorWdg';

        var kwargs = {
            'editor_id': bvr.editor_id,
            'display_handler': 'tactic.ui.widget.SObjectCalendarWdg',
            'name': '',
            'display_options': {
            }
        };
        spt.panel.load_popup("Widget Editor", class_name, kwargs);
        '''
        } )



        menu_item = MenuItem(type='action', label='Inject Search')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'editor_id': my.editor_id,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.WidgetEditorWdg';

        var kwargs = {
            'editor_id': bvr.editor_id,
            'display_handler': 'tactic.ui.input.GlobalSearchWdg',
            'name': '',
            'display_options': {
            }
        };
        spt.panel.load_popup("Widget Editor", class_name, kwargs);
        '''
        } )




        menu_item = MenuItem(type='separator')
        menu.add(menu_item)




        menu_item = MenuItem(type='action', label='Repeat Last Test')
        menu.add(menu_item)

        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            spt.app_busy.show("Loading Last Test");
            var top = activator.getParent(".spt_custom_layout_top");
            var view = top.last_view;
            if (!view) {
                spt.alert("No last test found");
            }

            var kwargs = {
                view: view,
                include_mako: true,
                is_test: true
            }

            var class_name = 'tactic.ui.tools.CustomLayoutEditTestWdg';
            try {
                spt.panel.load_popup("Test Custom Layout", class_name, kwargs);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }

            spt.app_busy.hide();

            '''
        } )

        return menu




    def handle_image_inject(my, config, button):

        from tactic.ui.container import DialogWdg
        dialog = DialogWdg()

        button.add(dialog)
        dialog.set_as_activator(button)

        # TODO: make it so that dialogs have no titles
        dialog.add_title("Inject images")

        div = DivWdg()
        dialog.add(div)

        search = Search("sthpw/snapshot")
        search.add_filter("version", -1)
        #search.add_parent_filter(config)
        search.set_limit(10)
        snapshots = search.get_sobjects()

        element_names = ['preview','files', 'web_path', 'file_size']


        config_xml = '''
        <config>
        <inject>
        <element name="inject">
          <display class="tactic.ui.tools.AddImageElementWdg">
            <editor_id>%s</editor_id>
          </display>
        </element>
        <element name="preview"/>
        <element name="files"/>
        <element name="file_size"/>
        </inject>
        </config>
        ''' % my.editor_id
        config_xml = config_xml.replace('"', "'")


        from tactic.ui.panel import FastTableLayoutWdg
        panel = FastTableLayoutWdg(config_xml=config_xml, search_type="sthpw/snapshot",view="inject",show_shelf=False, element_names=element_names, edit=False, show_select=False)
        panel.set_sobjects(snapshots)
        div.add(panel)


__all__.append("AddImageElementWdg")
from tactic.ui.table import ButtonElementWdg
class AddImageElementWdg(ButtonElementWdg):


    def preprocess(my):
        editor_id = my.get_option("editor_id")
        my.set_option( "cbjs_action", """
        spt.ace_editor.set_editor("%s");

        expression = "/assets/{@GET(sthpw/file.relative_dir)}/{@GET(sthpw/file.file_name)}";
        server = TacticServerStub.get();
        var row = bvr.src_el.getParent(".spt_table_row");
        var search_key = row.getAttribute("spt_search_key");
        var result = server.eval(expression, {search_keys:search_key, single: true});

        var doc = spt.ace_editor.get_document();
        var editor = spt.ace_editor.get_editor();
        var position = editor.getCursorPosition();
        doc.insertInLine(position, result);

        var dialog = bvr.src_el.getParent(".spt_dialog_top");
        spt.hide(dialog);
        """ % editor_id )

        my.set_option("icon", "ADD")




class CustomLayoutEditTestWdg(BaseRefreshWdg):

    def get_display(my):

        html = my.kwargs.get("html")
        style = my.kwargs.get("style")
        view = my.kwargs.get("view")
        view = view.replace("/", ".")

        mako = my.kwargs.get("mako")
        behavior = my.kwargs.get("behavior")
        kwargs = my.kwargs.get("kwargs")
        is_test = my.kwargs.get("is_test")

        # find out if there is a plugin associated with this
        code = my.kwargs.get("code")
        plugin = Search.eval("@SOBJECT(config/plugin_content['search_code','%s'].config/plugin)" % code, single=True)



        from tactic.ui.panel import CustomLayoutWdg
        top = my.top
        #top.add_style("padding: 20px")
        top.add_border()
        top.add_color("color", "color")
        top.add_color("background", "background")

        if not html:
            layout = CustomLayoutWdg(view=view, include_mako=True, is_test=is_test, kwargs=kwargs, plugin=plugin)
            top.add(layout)
            return top



        config_xml = CustomLayoutEditSaveCmd.build_xml(view, html, style, behavior, mako=mako, kwargs=kwargs)
        layout = CustomLayoutWdg(config_xml=config_xml, view=view, include_mako=True, is_test=is_test, kwargs=kwargs, plugin=plugin)
        top.add(layout)


        return top



class CustomLayoutEditSaveCmd(Command):

    def build_xml(cls, view, html, style=None, behavior=None, mako=None, kwargs=None):

        # build up the custom layout
        if not html:
            html = "<div>No html</div>"
        html = html.strip()
        html = html.replace("<%", "<![CDATA[\n<%")
        html = html.replace("%>", "%>]]>")
        html = html.replace("&", "&amp;")



        if style:
            style = style.strip()
            style = style.replace("<%", "<![CDATA[\n<%")
            style = style.replace("%>", "%>]]>")
            style = style.replace("&", "&amp;")

        if kwargs:
            kwargs = kwargs.strip()
            kwargs = kwargs.replace("<%", "<![CDATA[\n<%")
            kwargs = kwargs.replace("%>", "%>]]>")
            kwargs = kwargs.replace("&", "&amp;")
            # check if kwargs is a proper dictionary
            try:
                kwargs_test = eval(kwargs)
            except Exception, e:
                raise TacticException('kwargs contains syntax error: %s' %(e))
            for key, value in kwargs_test.items():
                if not isinstance(value, basestring) and not isinstance(value, dict):
                    raise TacticException('It needs to be a dictionary or string for the value of each kwarg. Click on "Show Examples" button for details.')

        if mako:
            mako = mako.strip()
            mako = mako.replace("&", "&amp;")
            mako = mako.replace("<", "&lt;")
            mako = mako.replace(">", "&gt;")

            #mako = mako.replace("<%", "<![CDATA[\n<%")
            #mako = mako.replace("%>", "%>]]>")
            mako = "\n".join( ["<![CDATA[", mako, "]]>"] )



        layout = []
        layout.append("<config>")
        layout.append("<%s>" % view)

        if kwargs:
            layout.append("<kwargs>")
            layout.append(kwargs)
            layout.append("</kwargs>")


        if mako:
            layout.append("<mako>")
            layout.append(mako)
            layout.append("</mako>")


        layout.append("<html>")


        if style:
            if style.find('<style type') != -1 or style.find('</style>') != -1:
                raise TacticException("<style> tag is automatically added when it is saved. Do not include any <style> tags in styles section.")
            layout.append('''<style type="text/css">''')
            layout.append(style)
            layout.append('''</style>''')
        if html:
            layout.append(html)




        layout.append("</html>")

        # FIXME: this is very tenuous
        if behavior:
            if behavior.find('<![CDATA[') != -1:
                raise TacticException("CDATA is automatically added when it is saved. Do not include any CDATA tag in behavior.")
            import re
            behavior = behavior.strip()
            #behavior = behavior.replace("\\", "\\\\")

            p = re.compile("(<behavior.*?>)")
            behavior = p.sub("\\1<![CDATA[", behavior)
            behavior = behavior.replace("</behavior>", "]]></behavior>")

            layout.append(behavior)


        layout.append("</%s>" % view)
        layout.append("</config>")

        config_xml = "\n".join(layout)



        #f = open("/tmp/tt.xml", 'w')
        #f.write(config_xml)
        #f.close()

        #f = open("/tmp/tt.xml")
        #config_xml = f.read()
        #f.close()

        return config_xml

    build_xml = classmethod(build_xml)



    def execute(my):

        html = my.kwargs.get("html")
        style = my.kwargs.get("style")
        kwargs = my.kwargs.get("kwargs")

        view = my.kwargs.get("view")
        view = view.replace("/", ".")

        widget_type = my.kwargs.get("widget_type")

        code = my.kwargs.get("code")

        behavior = my.kwargs.get("behavior")
        mako = my.kwargs.get("mako")

        if html and html.find('<![CDATA[') != -1:
            raise TacticException("CDATA is automatically added when it is saved. Do not include any CDATA tag in HTML section.")

        if style and style.find('<![CDATA[') != -1:
            raise TacticException("Do not include any CDATA tag in Styles section.")

        config_xml = my.build_xml(view, html, style, behavior, mako, kwargs)

        xml = Xml()
        xml.read_string(config_xml)


        if code:
            search = Search("config/widget_config")
            search.add_filter("code", code)
            sobject = search.get_sobject()
        else:
            sobject = None

        if not sobject:
            sobject = SearchType.create("config/widget_config")
            sobject.set_value("category", "CustomLayoutWdg")
            #sobject.set_value("search_type", "CustomLayoutWdg")
        else:
            # fill in category for existing entries
            if not sobject.get_value('category'):
                sobject.set_value("category", "CustomLayoutWdg")
        sobject.set_value("view", view)
        if widget_type:
            sobject.set_value("widget_type", widget_type)
        sobject.set_view(view)
        sobject.set_value("config", config_xml)
        sobject.commit()

        my.add_description("Saved Custom Layout view [%s]" % view)



class SimpleLoginTemplate(object):

    def __init__(my):
        from pyasm.biz import Project
        project = Project.get()
        title = project.get_value("title")

        my.html = r'''
<div class="custom_login">
  <div class="title">
    <h1>[expr]@GET(project.title)[/expr]</h1>
  </div>
  <form>
Name:
    <element name="login"><display class="tactic.ui.input.TextInputWdg"/></element>

<br/>


Password:
    <element name="password"><display class="tactic.ui.input.PasswordInputWdg"/></element>

<br/>


<div style="float: right" class="custom_button" onclick="document.form.submit()"><input type="button" value="Enter >>"/></div>

</form>
</div>
        '''


        my.style = r'''
body {
    background: #FFF !important;
}


.custom_login {
    width: 350px;
    font-size: 14px;
    padding: 50px;
    margin-left: auto;
    margin-right: auto;
    margin-top: 100px;
    margin-bottom: 100px;
    background: [expr]@GRADIENT('background', 10)[/expr];
    border: solid 1px black;
}

.custom_login .title {
    color: #000;
    background-color: [expr]@COLOR('background3')[/expr];
    padding: 20px;
    width: 410px;
    height: 100px;
    margin: -50 -50 30 -50;
    text-align: center;
}

        '''

        my.behavior = ' '



class RawMenuTemplate(object):

    def __init__(my):

        my.html = '''
<div class="menu">
  <div>
    <element name="menu" id="side_bar">
      <display class="tactic.ui.panel.SimpleSideBarWdg">
        <use_href>true</use_href>
        <view>project_view</view>
        <target>spt_custom</target>
      </display>
    </element>
  </div>
</div>
        '''


        my.style = '''

.web_menu_wdg {
}

.web_menu_wdg .main_link {
  cursor: pointer;
}

.web_menu_wdg .main_ul {
}

.web_menu_wdg .main_li {
  cursor: pointer;
}

.web_menu_wdg .menu_header {
}

.web_menu_wdg .sub_ul {
}

.web_menu_wdg .sub_ul li {
}

.web_menu_wdg a {
}

.web_menu_wdg .sub_ul a:link {
}

        '''



        my.behavior = '''
        '''




class SimpleMenuTemplate(object):

    def __init__(my):

        my.html = '''
<div class="menu">
  <div>
    <element name="menu" id="side_bar">
      <display class="tactic.ui.panel.SimpleSideBarWdg">
        <use_href>true</use_href>
        <view>project_view</view>
        <target>spt_custom</target>
      </display>
    </element>
  </div>
</div>
        '''

        my.python = ''


        my.style = '''
<%
num_menus = 4;
menu_width = 150;
%>

.web_menu_wdg {
    color: #FFF;
    text-align: center;
    margin-left: auto;
    margin-right: auto;
    position: relative;
    padding: 0px;
    
    width: ${num_menus*(menu_width+12)};
 
}

.web_menu_wdg .main_link {
  list-style-type: none;
  display: block;
  background: [expr]@GRADIENT('background', -50, -20)[/expr];
  height: 28px;
  cursor: pointer;
}

.web_menu_wdg .main_ul {
  list-style-type: none;
  display: block;
  margin: 0px;
  padding: 0px;
  background: [expr]@GRADIENT('background', -50, -20)[/expr];
  height: 30px;
}

.web_menu_wdg .main_li {
  margin-left: 0px;
  padding: 0px;
  cursor: pointer;
}

.web_menu_wdg .menu_header {
    float: left;
    padding: 6px 1px 5px 10px;
    font-weight: bold;
    border-style: solid;
    border-width: 0 1 0 1;
    border-color: #000;
    margin-left: -1px;
    height: 19px;

    width: 150px;
}

.web_menu_wdg .sub_ul {
    list-style-type: none;
    display: block;
    border-style: solid;
    border-width: 0 1 1 1;
    border-color: #000;
    padding: 3px;
    display: none;
    //border: solid 1px red;
    float: left;
    margin-left: -163;
    margin-top: 30px;
    background: [expr]@COLOR('background', -70)[/expr];
    position: relative;
    z-index: 1000;

    max-height: 250px;
    overflow-y: auto;
    overflow-x: hidden;

    width: 155px;
}

.web_menu_wdg .sub_ul li {
  padding: 5px;
  text-align: left;
}

.web_menu_wdg a {
  text-decoration: none;
}

.web_menu_wdg .sub_ul a:link {
    color: #FFF;
}

        '''



        my.behavior = '''

<behavior class="main_li" event="mouseenter">
// make sure they are all closed
var top = bvr.src_el.getParent(".main_ul");
var sub_els = top.getElements(".sub_ul");
for ( var i = 0; i < sub_els.length; i++) {
    sub_els[i].setStyle("display", "none");
}

var sub_el = bvr.src_el.getElement(".sub_ul");
if (sub_el) {
    sub_el.setStyle("opacity", 0);
    new Fx.Tween(sub_el, {duration: "short"}).start('opacity', 1.0);
    sub_el.setStyle("display", "block");
}
</behavior>


<behavior class="main_li" event="mouseleave">
var sub_el = bvr.src_el.getElement(".sub_ul");
if (sub_el) {
    sub_el.setStyle("display", "none");
}
</behavior>


<behavior class="sub_li" event="mouseenter">
bvr.src_el.setStyle("background-color", "#333");
</behavior>


<behavior class="sub_li" event="click_up">
var el = bvr.src_el.getParent(".sub_ul");
el.setStyle("display", "none");
</behavior>


<behavior class="sub_li" event="mouseleave">
bvr.src_el.setStyle("background-color", "");
</behavior>


<behavior class="menu" event="mouseleave">
var els = bvr.src_el.getElements(".sub_ul");
for ( var i = 0; i < els.length; i++) {
    els[i].setStyle("display", "none");
}
</behavior>
        '''




class SimpleSidebarTemplate(SimpleMenuTemplate):

    def __init__(my):

        my.html = ''' <div>
  <div class="menu">
    <element name="menu" id="side_bar">
      <display class="tactic.ui.panel.SimpleSideBarWdg">
        <use_href>true</use_href>
        <view>project_view</view>
        <target>web_content</target>
      </display>
    </element>
  </div>
</div>
        '''


        my.python = '''
bgcolor = server.eval("@COLOR('background3')")
bgcolor2 = server.eval("@COLOR('background3',-10)")

kwargs['bgcolor'] = bgcolor
kwargs['bgcolor2'] = bgcolor2
        '''

        my.style = '''
<%
num_menus = 5;
menu_width = 200;
menu_height = 30;


%>


.web_menu_wdg {
    color: [expr]@COLOR('color')[/expr];
    text-align: left;
    margin-left: 0px;
    //margin-bottom: -1px;
    position: relative;
    padding: 0px;
    
    width: ${menu_width + 13};
    height: 100%;
    //border: solid 1px green;
 
}


.web_menu_wdg .main_link {
  list-style-type: none;
  display: block;
  cursor: pointer;
}



.web_menu_wdg .main_ul {
  list-style-type: none;
  display: block;
  margin: -1px 0px 0px 0px;
  padding: 0px;
  background: [expr]@COLOR('background3')[/expr];
  height: 100%;
}


.web_menu_wdg .main_li {
    margin-left: 0px;
    padding: 0px;
    //background: #F00;
    background-image: url(/context/icons/silk/_spt_bullet_arrow_right_dark.png);
    background-repeat: no-repeat;
    background-position: center right;
}


.web_menu_wdg .menu_header {
    padding: 6px 1px 5px 5px;
    font-weight: bold;
    //border-style: solid;
    //border-width: 1 1 1 1;
    //border-color: [expr]@COLOR('border')[/expr];

    width: ${menu_width+5};
}


.web_menu_wdg .sub_ul {
    list-style-type: none;
    display: block;
    padding: 5px;
    border-style: solid;
    border-width: 1 1 1 1;
    border-color: [expr]@COLOR('border')[/expr];
    display: none;
    margin-left: ${menu_width+12};
    margin-top: ${-menu_height+2};
    background: [expr]@COLOR('background3')[/expr];
    position: absolute;
    z-index: 1000;

    max-height: 250px;
    overflow-y: auto;
    overflow-x: hidden;

    box-shadow: 0px 0px 15px [expr]@COLOR('shadow')[/expr];
    border-radius: 5px;

    width: ${menu_width};
}

.web_menu_wdg .sub_ul li {
  padding: 5px 5px;
  text-align: left;
  //border-style: solid;
  //border-width: 1 1 1 1;
  //border-color: [expr]@COLOR('border')[/expr];
  height: ${menu_height - 15};
  cursor: pointer;
}

.web_menu_wdg .main_title {
  margin-top: 15px;
  font-size: 1.2em;
  margin-left: -5px;
}

.web_menu_wdg a {
  text-decoration: none;
}

.web_menu_wdg .sub_ul a:link {
    color: #FFF;
}

        '''


        my.behavior = '''
<behavior class="web_menu_wdg" event="load">
var top = bvr.src_el.getParent(".spt_custom_top");
top.setAttribute("id", "side_bar");
</behavior>


<behavior class="main_li" event="mouseenter">
bvr.src_el.setStyle("background-color", bvr.kwargs.bgcolor2);
// make sure they are all closed
var top = bvr.src_el.getParent(".main_ul");
var sub_els = top.getElements(".sub_ul");
for ( var i = 0; i < sub_els.length; i++) {
    sub_els[i].setStyle("display", "none");
}

var sub_el = bvr.src_el.getElement(".sub_ul");
if (sub_el) {
    sub_el.setStyle("opacity", 0);
    new Fx.Tween(sub_el, {duration: "short"}).start('opacity', 1.0);
    sub_el.setStyle("display", "block");
}
</behavior>


<behavior class="main_li" event="mouseleave">
bvr.src_el.setStyle("background-color", "");
var sub_el = bvr.src_el.getElement(".sub_ul");
if (sub_el) {
    sub_el.setStyle("display", "none");
}
</behavior>


<behavior class="main_link" event="mouseenter">
bvr.src_el.setStyle("background-color", bvr.kwargs.bgcolor2);
</behavior>


<behavior class="main_link" event="mouseleave">
bvr.src_el.setStyle("background-color", "");
</behavior>


<behavior class="sub_li" event="mouseenter">
bvr.src_el.setStyle("background-color", bvr.kwargs.bgcolor2);
</behavior>


<behavior class="sub_li" event="click_up">
var el = bvr.src_el.getParent(".sub_ul");
el.setStyle("display", "none");
</behavior>


<behavior class="sub_li" event="mouseleave">
bvr.src_el.setStyle("background-color", "");
</behavior>


<behavior class="menu" event="mouseleave">
var els = bvr.src_el.getElements(".sub_ul");
for ( var i = 0; i < els.length; i++) {
    els[i].setStyle("display", "none");
}
</behavior>

        '''





class CustomLayoutActionCbk(Command):

    def execute(my):
        action = my.kwargs.get("action")

        if action == "copy_folder":
            my.copy_folder()

        elif action == "rename_folder":
            my.rename_folder()

        elif action == "delete_folder":
            my.delete_folder()
    
        elif action == "copy_view":
            my.copy_view()


        else:
            raise TacticException("Action [%s] not supported" % action)


    def new_view(my, view, new_folder):
        if view.startswith("."):
            return view

        count = view.count('.')
        parts = view.split(".")
        for i in range(0, count):
            parts.pop(0)
        parts.insert(0, new_folder)
        new_view = ".".join(parts)

        return new_view



    def copy_folder(my):

        folder = my.kwargs.get("folder")
        new_folder = my.kwargs.get("new_folder")
        if not new_folder:
            new_folder = "%s_copy" % folder

        search = Search("config/widget_config")
        search.add_filter("view", "%s.%%" % folder, op="like" )
        search.add_filter("category", "CustomLayoutWdg")
        configs = search.get_sobjects()

        for config in configs:
            view = config.get_value("view")
            new_view = my.new_view(view, new_folder)

            config_xml = config.get_xml_value("config")

            node = config_xml.get_node("config/%s" % view)
            config_xml.rename_node(node, new_view)

            elements = config_xml.get_nodes("//element")
            for element in elements:
                element_view = config_xml.get_attribute(element, "view")
                if element_view:
                    element_view = element_view.replace("/", ".")
                    new_element_view = my.new_view(element_view, new_folder)
                    config_xml.set_attribute(element, "view", new_element_view)

            new_config = SearchType.create("config/widget_config")
            new_config.set_value("category", "CustomLayoutWdg")
            new_config.set_value("config", config_xml)
            new_config.set_value("view", new_view)
            new_config.commit()


    def rename_folder(my):

        folder = my.kwargs.get("folder")
        new_folder = my.kwargs.get("new_folder")
        if not new_folder:
            new_folder = "%s_copy" % folder

        search = Search("config/widget_config")
        search.add_filter("view", "%s.%%" % folder, op="like" )
        search.add_filter("category", "CustomLayoutWdg")
        configs = search.get_sobjects()

        for config in configs:
            new_config = config

            view = config.get_value("view")
            new_view = my.new_view(view, new_folder)

            config_xml = config.get_xml_value("config")

            node = config_xml.get_node("config/%s" % view)
            config_xml.rename_node(node, new_view)

            config.set_view(new_view)

            elements = config_xml.get_nodes("//element")
            for element in elements:
                element_view = config_xml.get_attribute(element, "view")
                if element_view:
                    element_view = element_view.replace("/", ".")
                    new_element_view = my.new_view(element_view, new_folder)
                    config_xml.set_attribute(element, "view", new_element_view)

            new_config.set_value("category", "CustomLayoutWdg")
            new_config.set_value("view", new_view)
            new_config.set_value("config", config_xml)
            new_config.commit()




    def delete_folder(my):

        folder = my.kwargs.get("folder")
        folder = folder.replace("/", ".")

        search = Search("config/widget_config")
        search.add_filter("view", "%s.%%" % folder, op="like" )
        search.add_filter("category", "CustomLayoutWdg")
        configs = search.get_sobjects()

        for config in configs:
            config.delete() 




    def copy_view(my):

        view = my.kwargs.get("view")
        new_view = my.kwargs.get("new_view")
        if not new_view:
            new_view = "%s_copy" % view

        search = Search("config/widget_config")
        search.add_filter("view", view)
        search.add_filter("category", "CustomLayoutWdg")
        config = search.get_sobject()

        config_xml = config.get_xml_value("config")

        node = config_xml.get_node("config/%s" % view)
        config_xml.rename_node(node, new_view)

        new_config = SearchType.create("config/widget_config")
        new_config.set_value("category", "CustomLayoutWdg")
        new_config.set_value("config", config_xml)
        new_config.set_value("view", new_view)
        new_config.commit()


