###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["FreeFormCanvasWdg", "FreeFormLayoutToolWdg", "FreeFormAttrWdg"]

from pyasm.common import Common, jsonloads
from pyasm.biz import Project
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table, WebContainer, HtmlElement
from pyasm.widget import ThumbWdg, IconWdg, WidgetConfig, TextWdg, TextAreaWdg, SelectWdg, HiddenWdg, WidgetConfig

from tactic.ui.widget import SingleButtonWdg, ActionButtonWdg, ButtonRowWdg, ButtonNewWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg

import random


class FreeFormLayoutToolWdg(BaseRefreshWdg):

    def get_value(self, name):
        value = self.kwargs.get(name)
        if value == None:
            web = WebContainer.get_web()
            value = web.get_form_value(name)

        return value


    def get_display(self):


        category = "FreeformWdg"

        search_type = self.get_value("search_type")
        if not search_type:
            search_type = "sthpw/login"


        view = self.get_value("view")
        if not view:
            view = 'freeform'

        search = Search("config/widget_config")
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        config_sobj = search.get_sobject()
        if config_sobj:
            config_xml = config_sobj.get_value("config")
        else:
            config_xml = "<config/>"

        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_freeform_top")

        inner = DivWdg()
        top.add(inner)



        table = ResizableTableWdg()
        table.add_color("background", "background")
        inner.add(table)
        table.add_row()
        table.set_max_width()

        td = table.add_cell()
        td.add_attr("colspan", "5")
        td.add_color("background", "background3")
        td.add_color("color", "color")
        td.add_style("padding", "10px")

        td.add("Search Type: ")
        select = SelectWdg("search_type")
        project = Project.get()
        search_types = project.get_search_types()
        values = [x.get_base_key() for x in search_types]
        labels = ["%s (%s)" % (x.get_title(), x.get_base_key()) for x in search_types]
        select.set_option("values", values)
        select.set_option("labels", labels)
        if search_type:
            select.set_value(search_type)
        td.add(select)
        td.add("&nbsp;"*10)
        td.add("View: ")
        text = TextWdg("view")
        td.add(text)
        if view:
            text.set_value(view)

        button = ActionButtonWdg(title="Load")
        button.add_style("float: left")
        td.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.app_busy.show("Loading View");
        var top = bvr.src_el.getParent(".spt_freeform_top");
        spt.panel.refresh(top);
        spt.app_busy.hide();
        '''
        } )


        table.add_row()

        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_border()
        left.add_color("color", "color")
        left.add_color("background", "background")
        left.add_style("min-width: 150px")

        left_div = DivWdg()
        left.add(left_div)
        left_div.add_style("min-height: 300px")
        left_div.add_style("min-width: 150px")
        left_div.add_style("width: 150px")

        title = DivWdg()
        left_div.add(title)
        title.add_style("font-weight: bold")
        title.add_style("font-size: 14px")
        title.add_style("width: 100%")
        title.add("Elements")
        title.add_gradient("background", "background", -5)
        title.add_style("padding: 10px 5px 5px 5px")
        title.add_style("height: 25px")
        title.add_style("margin-bottom: 10px")


        left.add_behavior( {
        'type': 'smart_click_up',
        'bvr_match_class': 'SPT_ELEMENT_CLICK',
        'cbjs_action': r'''
        var top = bvr.src_el.getParent(".spt_freeform_top");
        var template_top = top.getElement(".spt_freeform_template_top");
        var canvas_top = top.getElement(".spt_freeform_canvas_top");
        var canvas = canvas_top.getElement(".spt_freeform_canvas");

        var element_name = bvr.src_el.getAttribute("spt_element_name");

        var template_els = template_top.getElements(".spt_element");
        var els = canvas.getElements(".spt_element");

        // get the highest number
        var number = 0;
        for ( var i = 0; i < els.length; i++) {
            var el = els[i];
            var name = el.getAttribute("spt_element_name");
            var num = name.match(/(\d+)/);
            if (!num)
                continue;
            num = parseInt(num);
            if (num > number) {
                number = num;
            }
        }
        number = number + 1;

        for ( var i = 0; i < template_els.length; i++) {
            var el = template_els[i];
            if (el.getAttribute("spt_element_name") == element_name) {
                var clone = spt.behavior.clone(el);
                canvas.appendChild(clone);
                clone.setStyle("top", "30px");
                clone.setStyle("left", "30px");
                clone.setStyle("position", "absolute");
                var new_name = element_name + number;
                clone.setAttribute("spt_element_name", new_name)
                clone.attrs = {};

                var number = Math.floor(Math.random()*10001)
                clone.setAttribute("spt_element_id", "element"+number);

                spt.freeform.select(clone);


                break;
            }
        }
        '''
        } )




        values = ['Label', 'Box', 'Text', 'TextArea', 'Button', 'Preview', 'Image', 'HTML', 'Table', 'Border', 'Custom Layout']
        names = ['label', 'box', 'text', 'textarea', 'button', 'preview', 'image', 'html', 'table', 'border', 'custom']
        icons = [IconWdg.VIEW]

        for name, value in zip(names, values):


            element_div = DivWdg()
            left_div.add(element_div)
            element_div.add_style("padding: 3px")
            element_div.add_class("SPT_DTS")
            element_div.add_class("hand")

            icon = IconWdg( name, IconWdg.VIEW )
            element_div.add(icon)


            element_div.add(value)
            element_div.add_class("SPT_ELEMENT_CLICK")
            element_div.add_attr("spt_element_name", name)
            element_div.add_style("padding-left: 10px")

            hover = element_div.get_color("background", -10)
            element_div.add_behavior( {
                'type': 'hover',
                'hover': hover,
                'cbjs_action_over': '''bvr.src_el.setStyle("background", bvr.hover)''',
                'cbjs_action_out': '''bvr.src_el.setStyle("background", "")'''
            } )
            element_div.add_class("hand")

            element_div.add_behavior( {
            'type': 'drag',
            "drag_el": '@',
            "cb_set_prefix": 'spt.freeform.create_element_drag'
            } )


        """
        button = ActionButtonWdg(title="Save")
        left_div.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_freeform_top");
        var canvas_top = top.getElement(".spt_freeform_canvas_top");
        var canvas = canvas_top.getElement(".spt_freeform_canvas");
        spt.freeform.init(canvas);
        var xml = spt.freeform.export();
        var search_type = canvas.getAttribute("spt_search_type");
        var view = canvas.getAttribute("spt_view");
        if (!search_type || !view) {
            alert("Cannot find search type or view");
            return;
        }

        var server = TacticServerStub.get();
        var sobject = server.get_unique_sobject("config/widget_config", {search_type: search_type, view: view} );
        server.update(sobject, {config: xml} );

        '''
        } )
        """
        

        from tactic.ui.container import DialogWdg
        dialog = DialogWdg(display=False, show_pointer=False)
        dialog.add_title("Properties")
        self.dialog_id = dialog.get_id()
        left.add(dialog)
        attr_div = self.get_attr_wdg()
        dialog.add(attr_div)


        template_div = DivWdg()
        left.add(template_div)
        template_div.add_class("spt_freeform_template_top")
        template_div.add_style("display: none")
        template_config_xml = self.get_template_config_xml()
        freeform_layout = FreeFormCanvasWdg(search_type=search_type, view="freeform", config_xml=template_config_xml, dialog_id=self.dialog_id)
        template_div.add(freeform_layout)


        # handle the canvas
        canvas = table.add_cell(resize=False)
        canvas.add( self.get_action_wdg() )
        canvas.add_style("overflow: hidden")

        canvas.add_style("vertical-align: top")
        canvas.add_color("background", "background")
        canvas.add_color("color", "color")

        canvas_div = DivWdg()
        canvas_div.add_style("margin: 20px")
        canvas_div.add_style("width: 90%")
        canvas_div.add_style("min-width: 300px")
        canvas_div.add_style("padding: 10px")
        canvas_div.add_style("height: 100%")
        canvas_div.add_class("spt_freeform_canvas_top")
        canvas.add(canvas_div)
        freeform_layout = FreeFormCanvasWdg(search_type=search_type, view=view, config_xml=config_xml, dialog_id=self.dialog_id)
        canvas_div.add(freeform_layout)



        table.add_resize_row()

        if self.kwargs.get("is_refresh") in [True, "true"]:
            return inner
        else:
            return top 



    def get_action_wdg(self):
        div = DivWdg()
        div.add_gradient("background", "background", -5)
        div.add_border()
        div.add_style("padding: 3px")


        button_row = ButtonRowWdg()
        div.add(button_row)
        button_row.add_style("float: left")
        div.add("<br clear='all'/>")

        button = ButtonNewWdg(title='Save Layout' , icon=IconWdg.SAVE)
        button_row.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.app_busy.show("Saving ...");
        var top = bvr.src_el.getParent(".spt_freeform_top");
        var canvas_top = top.getElement(".spt_freeform_canvas_top");
        var canvas = canvas_top.getElement(".spt_freeform_canvas");
        spt.freeform.init(canvas);
        var xml = spt.freeform.export();
        var search_type = canvas.getAttribute("spt_search_type");
        var view = canvas.getAttribute("spt_view");
        if (!search_type || !view) {
            alert("Cannot find search type or view");
            return;
        }

        var server = TacticServerStub.get();
        var sobject = server.get_unique_sobject("config/widget_config", {search_type: search_type, view: view} );
        server.update(sobject, {config: xml} );
        spt.app_busy.hide();

        '''
        } )
        





        button = ButtonNewWdg(title='Add' , icon=IconWdg.ADD, show_arrow=True)
        button_row.add(button)

        from tactic.ui.container import SmartMenu
        smenu_set = SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': self.get_add_menu() } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )


        button = ButtonNewWdg(title='Remove' , icon=IconWdg.DELETE)
        button_row.add(button)




        button = ButtonNewWdg(title='Clear' , icon=IconWdg.KILL)
        button_row.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_freeform_top");
        var canvas_top = top.getElement(".spt_freeform_canvas_top");
        var canvas = canvas_top.getElement(".spt_freeform_canvas");
        spt.freeform.init(canvas);

        if ( !confirm("Are you sure you wish to clear the canvas?") ) {
            return;
        }
        spt.freeform.clear_canvas();


        '''
        } )


        return div


    def get_add_menu(self):
        from tactic.ui.container import Menu, MenuItem
        menu = Menu(width=180)
        menu.set_allow_icons(False)
        #menu.set_setup_cbfn( 'spt.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Add Item')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Label')
        menu_item.add_behavior( {
            'element_name': 'label',
            'cbjs_action': self.get_add_bvr_action()
        } )
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Text')
        menu_item.add_behavior( {
            'element_name': 'text',
            'cbjs_action': self.get_add_bvr_action()
        } )
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='TextArea')
        menu_item.add_behavior( {
            'element_name': 'textarea',
            'cbjs_action': self.get_add_bvr_action()
        } )
        menu.add(menu_item)


        return menu


    def get_add_bvr_action(self):
        cbjs_action = '''
        var activator = spt.smenu.get_activator(bvr);

        var top = activator.getParent(".spt_freeform_top");
        var template_top = top.getElement(".spt_freeform_template_top");
        var canvas_top = top.getElement(".spt_freeform_canvas_top");
        var canvas = canvas_top.getElement(".spt_freeform_canvas");

        var element_name = bvr.element_name;

        var template_els = template_top.getElements(".spt_element");
        var els = canvas.getElements(".spt_element");

        for ( var i = 0; i < template_els.length; i++) {
            var el = template_els[i];
            if (el.getAttribute("spt_element_name") == element_name) {
                var clone = spt.behavior.clone(el);
                canvas.appendChild(clone);
                clone.setStyle("top", "30px");
                clone.setStyle("left", "30px");
                clone.setStyle("position", "absolute");
                var new_name = element_name + els.length;
                clone.setAttribute("spt_element_name", new_name)
                clone.attrs = {};

                var number = Math.floor(Math.random()*10001)
                clone.setAttribute("spt_element_id", "element"+number);
                break;
            }
        }
        '''

        return cbjs_action 


    def get_attr_wdg(self):
        div = DivWdg()
        div.add_border();
        #div.add_style("padding: 10px")
        div.add_color("color", "color")
        div.add_color("background", "background")
        div.add_style("height: 100%")
        div.add_style("min-height: 500px")
        div.add_style("min-width: 500px")
        div.add("&nbsp;")

        div.add_class("spt_freeform_attr_top")


        return div



    def get_template_config_xml(self):

        return '''
<config>
<freeform width='500px' height='500px'>
<element name='preview' xpos='300px' ypos='200px'>
  <display class='pyasm.widget.ThumbWdg'>
  </display>
</element>
<element name='label' xpos='100px' ypos='100px'>
  <display class='tactic.ui.tools.freeform_layout_wdg.LabelWdg'>
      <html>Label</html>
  </display>
</element>

<element name='box' xpos='100px' ypos='100px'>
  <display class='tactic.ui.tools.freeform_layout_wdg.FreeFormBoxWdg'>
  </display>
</element>
<element name='image' xpos='100px' ypos='100px'>
  <display class='tactic.ui.tools.freeform_layout_wdg.FreeFormImageWdg'>
  </display>
</element>



<element name='select' xpos='250px' ypos='100px'>
  <display class='SelectWdg'>
    <values>model|texture|rig|anim</values>
  </display>
</element>
<element name='button' xpos='100px' ypos='200px'>
  <display class='tactic.ui.widget.ActionButtonWdg'>
    <title>Submit</title>
  </display>
</element>
<element name='text' xpos='100px' ypos='200px'>
  <display class='tactic.ui.input.TextInputWdg'>
  </display>
</element>
<element name='textarea' xpos='100px' ypos='200px'>
  <display class='pyasm.widget.TextAreaWdg'>
  </display>
</element>
<element name='data' xpos='100px' ypos='200px'>
  <display class='tactic.ui.table.FormatElementWdg'>
    <format>text</format>
  </display>
</element>
<element name='table' xpos='100px' ypos='200px'>
  <display class='tactic.ui.panel.TableLayoutWdg'>
    <search_type>sthpw/login</search_type>
    <view>table</view>
  </display>
</element>
<element name='border' xpos='100px' ypos='200px'>
  <display class='tactic.ui.tools.BorderWdg'>
    <width>200px</width>
    <height>100px</height>
  </display>
</element>
<element name='html' xpos='100px' ypos='200px'>
  <display class='tactic.ui.tools.HtmlWdg'>
    <width>200px</width>
    <height>100px</height>
  </display>
</element>
<element name='custom' xpos='100px' ypos='200px'>
  <display class='tactic.ui.panel.CustomLayoutWdg'>
    <html>No content</html>
  </display>
</element>


<behavior name='select'>
    <cbjs_action>alert('hello')</cbjs_action>
</behavior>
</freeform>
</config>
        '''

class FreeFormCanvasWdg(BaseRefreshWdg):

    def get_display(self):

        search_type = self.kwargs.get("search_type")
        view = self.kwargs.get("view")
        assert search_type
        assert view

        #self.handle_search()

        config_xml = self.kwargs.get("config_xml")
        if not config_xml:
            config_xml = "<config/>"


        # extraneous variables inherited from TableLayoutWdg
        self.edit_permission = False

        top = DivWdg()
        top.add_class("spt_freeform_layout_top")
        self.set_as_panel(top)
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("height: 100%")
        top.add_style("width: 100%")
        border_color = top.get_color("border")
        top.add_style("border: dashed 1px %s" % border_color)


        is_refresh = self.kwargs.get("is_refresh")

        config = WidgetConfig.get(view=view, xml=config_xml)

        # define canvas
        canvas = top
        canvas.add_class("spt_freeform_canvas")
        canvas.add_style("position: relative")

        self.kwargs['view'] = view


        element_names = config.get_element_names()
        view_attrs = config.get_view_attributes()

        canvas_height = view_attrs.get("height")
        if not canvas_height:
            canvas_height = '400px'
        canvas.add_style("height: %s" % canvas_height)

        canvas_width = view_attrs.get("width")
        if not canvas_width:
            width = '600px'
        canvas.add_style("width: %s" % canvas_width)
  
        if not self.sobjects:
            search = Search(search_type)
            sobject = search.get_sobject()
        else:
            sobject = self.sobjects[0]


        dialog_id = self.kwargs.get("dialog_id")

        canvas.add_behavior( {
        'type': 'smart_click_up',
        'search_type': search_type,
        'view': view,
        'bvr_match_class': 'SPT_ELEMENT_SELECT',
        'cbjs_action': '''
        var element = bvr.src_el;
        var top = bvr.src_el.getParent(".spt_freeform_top");
        var attr = top.getElement(".spt_freeform_attr_top");

        var element_id = element.getAttribute("spt_element_id");
        var attrs = element.attrs;
        if (!attrs) {
            attrs = {};
        }

        var class_name = 'tactic.ui.tools.freeform_layout_wdg.FreeFormAttrWdg';
        var kwargs = {
            element_id: element_id,
            element_name: element.getAttribute("spt_element_name"),
            display_handler: element.getAttribute("spt_display_handler"),
            display_options: attrs
        }
        spt.panel.load(attr, class_name, kwargs);

        var dialog_id = '%s';
        spt.show( document.id(dialog_id) );

        ''' % dialog_id
        } )



        canvas.add_behavior( {
        'type': 'load',
        'cbjs_action': self.get_onload_js()
        } )


        canvas.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        var top = bvr.src_el;
        spt.freeform.init(top);
        '''
        } )



        for element_name in element_names:

            widget_div = DivWdg()
            canvas.add(widget_div)
            widget_div.add_style("position: absolute")
            widget_div.add_style("vertical-align: top")

            widget_div.add_class("SPT_ELEMENT_SELECT")


            widget_div.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                bvr.src_el.makeDraggable()
                '''
            } )


            el_attrs = config.get_element_attributes(element_name)
            height = el_attrs.get("height")
            if height:
                widget_div.add_style("height: %s" % height)

            width = el_attrs.get("width")
            if width:
                widget_div.add_style("width: %s" % width)

            display_handler = config.get_display_handler(element_name)
            display_options = config.get_display_options(element_name)

            widget_div.add_attr("spt_display_handler", display_handler)

            widget_div.add_behavior( {
            'type': 'load',
            'display_options': display_options,
            'cbjs_action': '''
            bvr.src_el.attrs = bvr.display_options;
            '''
            } )




            try:
                widget = config.get_display_widget(element_name)
            except:
                continue

            widget.set_sobject(sobject)
            widget_div.add_attr("spt_element_name", element_name)
            widget_div.add_class("spt_element")


            content = DivWdg()
            widget_div.add(content)
            content.add_class("spt_element_content")
            content.add(widget)


            try:
                is_resizable = widget.is_resizable()
            except: 
                is_resizable = False


            number = random.randint(0, 10000)
            element_id = "element%s" % number
            widget_div.set_attr("spt_element_id", element_id)


            # HACK for action button widget.  This widget takes over the
            # mouse hover very strongly, so need some padding to have
            # the widget_div trigger first
            if isinstance(widget, ActionButtonWdg):
                widget_div.add_style("padding: 2px")
                widget_div.add_style("height: 30px")



            # right now, the hover behavior has to be put on each element
            widget_div.add_behavior( {
            'type': 'hover',
            'cbjs_action_over': '''
            var size = bvr.src_el.getSize();
            var buttons = bvr.src_el.getElement(".spt_freeform_button_top");
            var buttons_size = buttons.getSize();
            spt.show(buttons);
            if (size.y < 32) {
                size.y = 32;
            }
            buttons.setStyle("width", size.x + 20);
            buttons.setStyle("height", size.y );
            buttons.setStyle("border", "solid 1px blue");
            ''',
            'cbjs_action_out': '''
            var buttons = bvr.src_el.getElement(".spt_freeform_button_top");
            spt.hide(buttons);
            buttons.setStyle("width", "100%")
            buttons.setStyle("height", "100%")
            '''
            } )



            dummy = TextWdg("foo")
            widget_div.add(dummy)
            dummy.add_class("spt_foo")
            dummy.add_style("position: absolute")
            dummy.add_style("left: -100000")
            widget_div.add_behavior( {
            'type': 'mouseover',
            'cbjs_action': '''
            var foo = bvr.src_el.getElement(".spt_foo");
            foo.focus();
            '''
            } )
            widget_div.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            var foo = bvr.src_el.getElement(".spt_foo");
            foo.blur();
            '''
            } )




            dummy.add_behavior( {
            'type': 'keyup',
            'cbjs_action': '''
            var keys = ['tab','enter','delete','left','right','up','down'];
            var key = evt.key;
            //console.log(key);
            if (keys.indexOf(key) > -1) evt.stop();

            var element = bvr.src_el.getParent(".SPT_ELEMENT_SELECT");
            var canvas = bvr.src_el.getParent(".spt_freeform_canvas");
            var pos = element.getPosition();
            var cpos = canvas.getPosition();
            pos = { x: pos.x - cpos.x -1, y: pos.y - cpos.y -1 };

            if (key == 'delete') {
                element.destroy()
            }

            var step = 1;
            if (evt.shift == true) {
                step = 10;
            }

            if (key == 'left') {
                pos.x = pos.x - step;
            }
            else if (key == 'right') {
                pos.x = pos.x + step;
            }
            else if (key == 'up') {
                pos.y = pos.y - step;
            }
            else if (key == 'down') {
                pos.y = pos.y + step;
            }

            element.position(pos);

            '''
            } )



            xpos = el_attrs.get("xpos")
            if not xpos:
                xpos = '100px'
            widget_div.add_style("left: %s" % xpos)

            ypos = el_attrs.get("ypos")
            if not ypos:
                ypos = '100px'
            widget_div.add_style("top: %s" % ypos)


            buttons_div = DivWdg()
            widget_div.add(buttons_div)
            buttons_div.add_class("spt_freeform_button_top")
            buttons_div.add_style("display: none")
            buttons_div.add_style("position: absolute")
            buttons_div.add_style("top: 0px")
            buttons_div.add_style("left: -10px")
            buttons_div.add_style("height: 100%")
            buttons_div.add_style("width: 105%")
            buttons_div.add_class("hand")

            buttons_div.add_border()

            #icon = IconWdg('Move', icon=IconWdg.ADD)
            #buttons_div.add(icon)
            #icon.add_class("move")

            is_resizable = True
            if is_resizable:
                icon_div = DivWdg()
                icon_div.add_style("cursor: move")
                buttons_div.add(icon_div)
                icon_div.add_style("position: absolute")
                icon_div.add_style("bottom: 0px")
                icon_div.add_style("right: 0px")
                icon = IconWdg('Scale', icon=IconWdg.RESIZE_CORNER)
                icon_div.add(icon)
                icon_div.add_behavior( {
                'type': 'drag',
                "drag_el": '@',
                "cb_set_prefix": 'spt.freeform.resize_element_drag'
                } )


                #icon.add_class("spt_resize_element")



        # for TableLayoutWdg??
        top.add_class("spt_table_top");
        class_name = Common.get_full_class_name(self)
        top.add_attr("spt_class_name", class_name)

        top.add("<br clear='all'/>")

        icon_div = DivWdg()
        top.add(icon_div)

        icon_div.add_class("spt_resize_canvas")
        icon_div.add_style("cursor: nw-resize")
        icon_div.add_style("z-index: 1000")
        icon_div.add_class("spt_popup_resize")
        icon_div.add_style("top: %s" % canvas_height)
        icon_div.add_style("left: %s" % canvas_width)
        icon_div.add_style("margin-left: -15px")
        icon_div.add_style("margin-top: -15px")
        icon_div.add_style("position: absolute")
        icon_div.add_behavior( {
        'type': 'drag',
        "drag_el": '@',
        "cb_set_prefix": 'spt.freeform.resize_drag'
        } )

        icon = IconWdg( "Resize", IconWdg.RESIZE_CORNER )
        icon_div.add(icon)

        size_div = DivWdg()
        icon_div.add(size_div)
        size_div.add_class("spt_resize_title")
        size_div.add_style("display: none")
        size_div.add_style("margin-left: -60px")
        size_div.add_style("margin-top: -30px")
        size_div.add_style("width: 150px")
 
        return top



    def get_onload_js(self):
        return '''

spt.freeform = {};

spt.freeform.data = {};
spt.freeform.selected = [];

spt.freeform.init = function(top) {
    spt.freeform.data.top = top;
    spt.freeform_selected = [];
}

spt.freeform.get_top = function() {
    return spt.freeform.data.top;
}



spt.freeform.get_elements = function() {
    var top = spt.freeform.get_top();
    var elements = top.getElements(".spt_element");
    return elements;
}

spt.freeform.get_element = function(element_name) {
    var top = spt.freeform.get_top();
    var elements = top.getElements(".spt_element");

    for (var i = 0; i < elements.length; i++) {
        if (elements[i].getAttribute("spt_element_name") == element_name) {
            return elements[i];
        }
    }
    return null;
}




spt.freeform.clear_canvas = function() {
    var elements = spt.freeform.get_elements();
    for (var i = 0; i < elements.length; i++) {
        spt.behavior.destroy_element( elements[i] );
    }
}




// selection methods
spt.freeform.select = function(el)
{
    spt.freeform.selected.push(el);
    el.setStyle("border", "solid 1px green");
}

spt.freeform.unselect = function(el)
{
    for (var i = 0; i < spt.freeform.selected.length; i++) {
    }
}


spt.freeform.unselect_all = function(el)
{
    for (var i = 0; i < spt.freeform.selected.length; i++) {
        var el = spt.freeform.selected[i];
        el.setStyle("border", "");
    }
    spt.freeform.selected = [];
}




spt.freeform.start_pos;
spt.freeform.start_size;
spt.freeform.resize_el;
spt.freeform.resize_drag_setup = function(evt, bvr, mouse_411) {
    var canvas = bvr.src_el.getParent(".spt_freeform_canvas");
    spt.freeform.init(canvas);

    spt.freeform.resize_el = canvas.getElement(".spt_resize_canvas");

    spt.freeform.start_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};
    spt.freeform.start_size = canvas.getSize();

    var title_el = spt.freeform.resize_el.getElement(".spt_resize_title");
    title_el.setStyle("display", "");
}



spt.freeform.resize_drag_motion = function(evt, bvr, mouse_411) {
    var top = spt.freeform.get_top();

    var mouse_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};
    var rel_pos = {};
    rel_pos.x = mouse_pos.x - spt.freeform.start_pos.x;
    rel_pos.y = mouse_pos.y - spt.freeform.start_pos.y;

    var size = {};
    size.x = spt.freeform.start_size.x + rel_pos.x;
    size.y = spt.freeform.start_size.y + rel_pos.y;

    top.setStyle("width", size.x);
    top.setStyle("height", size.y);

    spt.freeform.resize_el.setStyle("left", size.x);
    spt.freeform.resize_el.setStyle("top", size.y);

    var title_el = spt.freeform.resize_el.getElement(".spt_resize_title");
    var title = "("+size.x+", "+size.y+")";
    title_el.innerHTML = title;
}

spt.freeform.resize_drag_action = function(evt, bvr, mouse_411) {
    var title_el = spt.freeform.resize_el.getElement(".spt_resize_title");
    title_el.setStyle("display", "none");
}



spt.freeform.resize_element_drag_setup = function(evt, bvr, mouse_411) {
    var canvas = bvr.src_el.getParent(".spt_freeform_canvas");
    spt.freeform.init(canvas);

    spt.freeform.resize_el = bvr.src_el.getParent(".spt_element");

    spt.freeform.start_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};
    spt.freeform.start_size = spt.freeform.resize_el.getSize();

}



spt.freeform.resize_element_drag_motion = function(evt, bvr, mouse_411) {
    var top = spt.freeform.get_top();

    var mouse_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};
    var rel_pos = {};
    rel_pos.x = mouse_pos.x - spt.freeform.start_pos.x;
    rel_pos.y = mouse_pos.y - spt.freeform.start_pos.y;

    var size = {};
    size.x = spt.freeform.start_size.x + rel_pos.x;
    size.y = spt.freeform.start_size.y + rel_pos.y;

    spt.freeform.resize_el.setStyle("width", size.x);
    spt.freeform.resize_el.setStyle("height", size.y);

    //spt.freeform.resize_el.setStyle("left", size.x);
    //spt.freeform.resize_el.setStyle("top", size.y);

}


spt.freeform.create_el = null;
spt.freeform.create_element_drag_setup = function(evt, bvr, mouse_411) {

    spt.freeform.create_el = spt.behavior.clone(bvr.src_el);
    spt.freeform.start_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};
    spt.freeform.create_el.setStyle("padding", "5px");
    spt.freeform.create_el.setStyle("border", "solid 1px #444");

    var canvas = bvr.src_el.getParent(".spt_freeform_top");
    canvas.appendChild(spt.freeform.create_el);
    spt.freeform.create_el.setStyle("position", "absolute");

    //spt.freeform.init(canvas);
}


spt.freeform.create_element_drag_motion = function(evt, bvr, mouse_411) {

    var mouse_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};
    var rel_pos = {};
    rel_pos.x = mouse_pos.x - spt.freeform.start_pos.x;
    rel_pos.y = mouse_pos.y - spt.freeform.start_pos.y;

    var start_pos = spt.freeform.start_pos;
    var pos = { x: start_pos.x + rel_pos.x, y: start_pos.y + rel_pos.y };

    spt.freeform.create_el.position(pos);
}

spt.freeform.create_element_drag_action = function(evt, bvr, mouse_411) {
    spt.freeform.create_el.destroy();
}











spt.freeform.export = function() {
    var top = spt.freeform.get_top();

    var elements = spt.freeform.get_elements();
    var view = top.getAttribute("spt_view");

    var size = top.getSize();

    var xml = "";
    xml += "<config>\\n";
    xml += '<'+view+' width="'+size.x+'" height="'+size.y+'">\\n';
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        var xpos = element.getStyle("left");
        var ypos = element.getStyle("top");

        var element_name = element.getAttribute("spt_element_name");
        var class_name = element.getAttribute("spt_display_handler");

        xml += '<element name="'+element_name+'" xpos="'+xpos+'" ypos="'+ypos+'">\\n';
        xml += '  <display class="'+class_name+'">\\n';

        var attrs = element.attrs;
        if (!attrs) {
            attrs = {};
        }
        for (name in attrs) {
            var value = attrs[name];
            if (value == '') {
                continue;
            }
            xml += '    <'+name+'>'+value+'</'+name+'>\\n';
        }

        xml += '  </display>\\n';
        xml += '</element>\\n';
        
    }
    xml += "</"+view+">\\n";
    xml += "</config>\\n";

    return xml;

}
        '''


class FreeFormAttrWdg(BaseRefreshWdg):

    def add_style(self, name, value=None):
        self.top.add_style(name, value)


    def get_display(self):
        element_name = self.kwargs.get("element_name")
        element_id = self.kwargs.get("element_id")
        display_handler = self.kwargs.get("display_handler")
        display_options = self.kwargs.get("display_options")

        top = self.top
        top.add_class("spt_freeform_attr_top")
        top.add_style("padding: 10px")


        action_wdg = DivWdg()
        top.add(action_wdg)
        #action_wdg.add_gradient("background", "background", -10)

        delete = ActionButtonWdg(title='Remove', tip='Remove from Canvas')
        action_wdg.add(delete)
        delete.add_style("float: right")
        delete.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''

        var attr_top = bvr.src_el.getParent(".spt_freeform_attr_top");
        var values = spt.api.get_input_values(attr_top, null, false);
        var top = bvr.src_el.getParent(".spt_freeform_top");
        var canvas_top = top.getElement(".spt_freeform_canvas_top");
        var canvas = canvas_top.getElement(".spt_freeform_canvas");
        spt.freeform.init(canvas);

        var element_id = values.element_id;

        var element = null;
        var elements = spt.freeform.get_elements();
        for (var i = 0; i < elements.length; i++) {
            if ( elements[i].getAttribute("spt_element_id") == element_id) {
                element = elements[i];
            }
        }

        if (element == null) {
            alert("Element "+element_id+" does not exist on canvas");
            return;
        }

        element.destroy()
        '''
        })




        update = ActionButtonWdg(title='Update')
        action_wdg.add(update)


        update.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var attr_top = bvr.src_el.getParent(".spt_freeform_attr_top");
        var values = spt.api.get_input_values(attr_top, null, false);
        var top = bvr.src_el.getParent(".spt_freeform_top");
        var canvas_top = top.getElement(".spt_freeform_canvas_top");
        var canvas = canvas_top.getElement(".spt_freeform_canvas");
        spt.freeform.init(canvas);

        var element_id = values.element_id;

        var element = null;
        var elements = spt.freeform.get_elements();
        for (var i = 0; i < elements.length; i++) {
            if ( elements[i].getAttribute("spt_element_id") == element_id) {
                element = elements[i];
            }
        }

        if (element == null) {
            alert("Element "+element_id+" does not exist on canvas");
            return;
        }

        element.setAttribute("spt_element_name", values["element_name"]);
        for (var name in values) {

            if (name.substr(0,3) == 'opt') {
                var parts = name.split("|");
                var attr_name = parts[1];
                var value = values[name];
                if (typeof(element.attrs) == 'undefined') {
                    element.attrs = {};
                }
                element.attrs[attr_name] = value;

            }
        }

        // set the values
        element.element_settings = values;

        // load the widget
        var class_name = values['xxx_option|display_class'];

        var kwargs = {};
        for (key in values) {
            var parts = key.split("|");
            if (parts[0] == 'option') {
                kwargs[parts[1]] = values[key];
            }

        }

        var server = TacticServerStub.get();
        var html = server.get_widget(class_name, {args: kwargs});

        var element_name = values['element_name'];
        var el = spt.freeform.get_element(element_name);
        var content = el.getElement(".spt_element_content");
        spt.behavior.replace_inner_html(content, html);




        '''
        } )


        top.add("<hr/>")






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
        #td.add(element_name)
        hidden = TextWdg("element_name")
        hidden.set_value(element_name)
        td.add(hidden)
        hidden = HiddenWdg("element_id")
        hidden.set_value(element_id)
        td.add(hidden)


        widget_key = ''
        display_class = display_handler

        from tactic.ui.manager import WidgetClassSelectorWdg

        class_labels = ['-- Class Path--']
        class_values = ['__class__']

        # add the widget information
        #class_labels = ['Raw Data', 'Formatted', 'Expression', 'Expression Value', 'Button', 'Link', 'Gantt', 'Hidden Row', 'Custom Layout', '-- Class Path --']
        #class_values = ['raw_data', 'format', 'expression', 'expression_value', 'button', 'link', 'gantt', 'hidden_row', 'custom_layout', '__class__']
        widget_class_wdg = WidgetClassSelectorWdg(widget_key=widget_key, display_class=display_class, display_options=display_options,class_labels=class_labels,class_values=class_values, prefix='option')
        top.add(widget_class_wdg)


        return top






__all__.append("HtmlWdg")
class HtmlWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'html': {
        'description': 'HTML',
        'category': 'Options',
        'type': 'TextAreaWdg',
        'order': 0
    },
    }


    def is_resizable(self):
        return True


    def add_style(self, name, value=None):
        self.top.add_style(name, value)



    def get_display(self):
        top = self.top

        html = self.kwargs.get("html")
        if not html:
            html = "<i>No content</i>"

        top.add(html)

        return top




__all__.append("BorderWdg")
class BorderWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'width': {
        'description': 'Width of widget',
        'category': 'Options',
        'order': 0
    },
    'height': {
        'description': 'Height of widget',
        'category': 'Options',
        'order': 1
    },
    'label': {
        'description': 'Label on border',
        'category': 'Options',
        'order': 2
    },
 

    }


    def get_display(self):

        top = self.top
        top.add_style("position: relative")

        width = self.kwargs.get("width")
        if not width:
            width = "200px"
        height = self.kwargs.get("height")
        if not height:
            height = "100px"
        label = self.kwargs.get("label")
        if label and self.sobjects:
            label = Search.eval(label, self.sobjects[0], single=True)
        if not label:
            label = "No Label"

        top.add_border()
        top.add_style("width: %s" % width)
        top.add_style("height: %s" % height)

        if label:
            label_div = DivWdg()
            top.add(label_div)
            label_div.add(label)

            label_div.add_style("position: absolute")
            label_div.add_style("top: -13px")
            label_div.add_style("left: 6px")


        return top




__all__.append("LabelWdg")
__all__.append("FreeFormBoxWdg")
__all__.append("FreeFormImageWdg")

class LabelWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'label': {
        'description': 'Label to display',
        'category': 'Options',
        'order': 0
    },
    'font-size': {
        'description': 'Size of the font',
        'category': 'Options',
        'order': 1
    }
    }


    def is_resizable(self):
        return True


    def add_style(self, name, value=None):
        self.top.add_style(name, value)



    def get_display(self):
        top = self.top
        #top.add_border()

        label = self.kwargs.get("label")

        if label.startswith("{") and label.endswith("}"):
            if self.sobjects:
                label = Search.eval(label, self.sobjects[0], single=True)
        if not label:
            label = "No Label"

        font_size = self.kwargs.get("font-size")
        if font_size:
            top.add_style("font-size: %s" % font_size)

        top.add(label)


        return top




class FreeFormBoxWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'label': {
        'description': 'Label to display',
        'category': 'Options',
        'order': 0
    },
    'font-size': {
        'description': 'Size of the font',
        'category': 'Options',
        'order': 1
    },
    'width': {
        'description': 'Width of image',
        'category': 'Options',
        'order': 2
    },
    'height': {
        'description': 'Height of image',
        'category': 'Options',
        'order': 3
    },
    'class': {
        'description': 'Class of top element',
        'category': 'Options',
        'order': 4
    },
    'css': {
        'description': 'Top level styling',
        'category': 'Options',
        'type': 'TextAreaWdg',
        'order': 5
    },


    }


    def is_resizable(self):
        return True


    def add_style(self, name, value=None):
        self.top.add_style(name, value)



    def get_display(self):
        top = self.top
        #top.add_border()

        width = self.kwargs.get("width")
        if not width:
            width = '50px'
        height = self.kwargs.get("height")
        if not height:
            height = '50px'

        class_name = self.kwargs.get("class")
        if class_name:
            top.add_class(class_name)


        top.add_style("width: 100%")
        top.add_border()
        top.add_color("background", "background3")


        font_size = self.kwargs.get("font-size")
        if font_size:
            top.add_style("font-size: %s" % font_size)




        css = self.kwargs.get("css")
        if css:
            css = jsonloads(css)
            for name, value in css.items():
                top.add_style(name, value)


        top.add_style("height: %s" % height)
        top.add_style("width: %s" % width)

        return top


class FreeFormImageWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'src': {
        'description': 'Image to display',
        'category': 'Options',
        'order': 0
    },
    'height': {
        'description': 'Height of image',
        'category': 'Options',
        'order': 2
    },
    'width': {
        'description': 'Width of image',
        'category': 'Options',
        'order': 1
    },



    }


    def is_resizable(self):
        return True


    def add_style(self, name, value=None):
        self.top.add_style(name, value)



    def get_display(self):
        top = self.top

        height = self.kwargs.get("height")
        if not height:
            height = "100%"
        width = self.kwargs.get("width")
        if not width:
            width = "100%"

        border = self.kwargs.get("border")


        src = self.kwargs.get("src")

        img = HtmlElement.img(src)
        img.add_style("width: %s" % width)
        img.add_style("height: %s" % height)
        top.add(img)
        top.add_style("width: %s" % width)
        top.add_style("height: %s" % height)
        top.add_style("min-width: 20px")
        top.add_style("min-height: 20px")
        top.add_border()


        return top




class FreeFormTextWdg(BaseRefreshWdg):


    ARGS_KEYS = {
        'label': 'Label to display'
    }


    def is_resizable(self):
        return True



    def get_display(self):
        top = DivWdg()
        #top.add_border()

        label = self.kwargs.get("label")
        if not label:
            label = 'No Label'

        top.add(label)


        return top





class DataWdg(BaseRefreshWdg):

    def get_display(self):
        top = DivWdg()

        column = self.kwargs.get("column")
        if not column:
            column = "code"

        sobject = self.get_current_sobject()
        if not sobject:
            value = 'No sobject'
        else:
            value = sobject.get_value(column)

        top.add(value)

        return top




