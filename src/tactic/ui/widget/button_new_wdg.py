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

__all__ = ['ButtonRowWdg', 'ButtonNewWdg', 'ActionButtonWdg', 'IconButtonWdg', 'IconButtonElementWdg', 'SingleButtonWdg']

import os

from pyasm.common import Container
from pyasm.search import Search, SObjectConfig, SearchType, SObjectFactory
from pyasm.web import HtmlElement, SpanWdg, DivWdg, Table, WebContainer
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg

import os

BASE = '/context/themes2'
ALPHA = "1.0"

class ButtonRowWdg(BaseRefreshWdg):

    def init(my):
        my.top = DivWdg(css='spt_button_row')

    def add_style(my, name, value=None):
        my.top.add_style(name, value)

    def get_num_buttons(my):
        return len(my.widgets)

    def get_display(my):

        top = my.top
        top.add_class("SPT_DTS")
        # make it focusable
        top.set_attr('tabIndex','-1')
        buttons = []

        show_title = my.kwargs.get("show_title")
        show_title = show_title in ['True', True]

        for button in my.widgets:
            if isinstance(button, ButtonNewWdg):
                button.set_show_title(show_title)
            buttons.append(button)

        #top.add( my.get_row_wdg(buttons, show_title=show_title) )
        top.add( my.get_row_wdg_new(buttons, show_title=show_title) )
        #top.add( my.get_row_wdgXX(buttons, show_title=show_title) )
        return top


    def get_row_wdg_new(my, buttons, show_title=False):

        div = DivWdg()

        """
        div.set_round_corners(8)
        div.add_border()
        div.add_style("padding-top: 1px")
        div.add_style("padding-left: 5px")
        div.add_style("padding-right: 5px")
        div.add_gradient("background", "background", 5, -30)
        """



        div = DivWdg()
        div.set_round_corners(3)
        #div.add_border()
        div.add_style("padding-top: 1px")
        div.add_style("padding-left: 5px")
        div.add_style("padding-right: 5px")
        #div.add_gradient("background", "background", -5, -10)





        web = WebContainer.get_web()
        browser = web.get_browser()

        table = Table()
        div.add(table)
        div.add_style("overflow: hidden")

        table.add_attr("cellspacing", "0px")
        table.add_attr("cellpadding", "0px")
        table.add_row()


        if browser == "Mozilla":
            table.add_style("margin-top: -5px")
            div.add_style("height: 30px")
        else:
            table.add_style("margin-top: -5px")



        base = "%s/%s" % (BASE, my.top.get_theme() )

        for count, button in enumerate(buttons):
            td = table.add_cell()
            td.add(button)

            if button.get_show_arrow_menu():
                spacer = DivWdg()
                table.add_cell(spacer)
                spacer.add_style("width: 6px")


            if count < len(buttons)-1:
                spacer = DivWdg()
                table.add_cell(spacer)
                spacer.add_style("width: 6px")



        return div




    def get_row_wdg(my, buttons, show_title=False):

        table = Table()
        table.set_round_corners(20)
        table.add_style("margin-top: -3px")
        table.add_attr("cellspacing", "0px")
        table.add_attr("cellpadding", "0px")
        table.add_row()

        base = "%s/%s" % (BASE, my.top.get_theme() )

        img = "<img src='%s/MainButtonSlices_left.png'/>" % base
        left = DivWdg(img)
        left.add_style("opacity", ALPHA)
        table.add_cell(left)

        td = table.add_cell()
        td.add_style("border-size: 0")
        for count, button in enumerate(buttons):
            button.add_style("float: left")
            td.add(button)

            if button.get_show_arrow_menu():
                spacer = DivWdg()
                spacer.add_style("float: left")
                td.add(spacer)
                img = "<img src='%s/MainButtonSlices_between.png'/>" % base
                spacer.add(img)
                spacer.add_style("opacity", ALPHA)



            if count < len(buttons)-1:
                spacer = DivWdg()
                spacer.add_style("float: left")
                td.add(spacer)
                img = "<img src='%s/MainButtonSlices_between.png'/>" % base
                spacer.add(img)
                spacer.add_style("opacity", ALPHA)


        img = "<img src='%s/MainButtonSlices_right.png'/>" % base
        right = DivWdg(img)
        right.add_style("opacity", ALPHA)
        table.add_cell(right)

        return table




    def get_row_wdgXX(my, buttons, show_title=False):

        top = DivWdg()
        #top.add_style("-moz-transform: scale(1.0)")
        top.add_style("float: left")
        top.add_style("margin-left: 3px")
        top.add_style("margin-right: 3px")

        if show_title:
            top.add_style("height: 29px")
        else:
            top.add_style("height: 23px")
        top.add_style("height: 33px")

        left = DivWdg()
        left.set_round_corners(20)
        #left.add_style("-moz-border-radius-topleft: 20px")
        #left.add_style("-moz-border-radius-bottomleft: 20px")
        left.add_border()
        left.add_gradient("background", "background", 20, -35)
        #left.add_style("background: black")
        left.add_style("float: left")
        left.add_style("height: 100%")
        left.add_style("width: 5px")
        left.add_style("z-index: 0")
        left.add_style("margin-right: -1")
        top.add(left)

        for button in buttons:
            button.add_style("float: left")
            top.add(button)


        right = DivWdg()
        right.add_style("-moz-border-radius-topright: 20px")
        right.add_style("-moz-border-radius-bottomright: 20px")
        right.add_gradient("background", "background", 20, -35)
        #right.add_style("background: black")
        right.add_style("float: left")
        right.add_style("height: 100%")
        right.add_style("width: 5px")
        #right.add_style("margin-left: -1px")
        right.add_style("z-index: 0")
        right.add_style("border-style: solid")
        right.add_style("border-color: %s" % right.get_color("border") )
        right.add_style("border-width: 1 1 1 0")
        top.add(right)


        return top


class ButtonNewWdg(BaseRefreshWdg):
    ARGS_KEYS = {
        'tip': {
            'description': 'The tool tip of the button',
            'category': 'Option',
        },
        'icon': {
            'description': 'The icon key to be used for the button',
            'category': 'Option',
        },
        'title': 'The title of the button',
        'show_menu': 'True|False - determines whether or not to show the menu',
        'show_title': 'True|False - determines whether or not to show the title',
        'is_disabled': 'True|False - determines whether or not the button is disabled'
    }

    def init(my):
        #my.inner = DivWdg()
        my.dialog = None
        my.button = DivWdg()
        my.hit_wdg = DivWdg()
        my.hit_wdg.add_class("spt_button_hit_wdg")
        my.arrow_div = DivWdg()
        my.arrow_menu = IconButtonWdg(title="More Options", icon=IconWdg.ARROWHEAD_DARK_DOWN)

        my.show_arrow_menu = False
        # for icon decoration
        my.icon_div = DivWdg()

        my.is_disabled = my.kwargs.get("is_disabled") in [True,"true"]


        if not Container.get_dict("JSLibraries", "spt_button"):
            doc_top = Container.get("TopWdg::top")
            if doc_top:
                doc_top.add_behavior( {
                    'type': 'load',
                    'cbjs_action': '''
                    spt.Environment.get().add_library("spt_button");
                    '''
                } )
                bvr_wdg = doc_top
            else:
                bvr_wdg = my.top

            # change to a relay behavior
            bvr_wdg.add_relay_behavior( {
            'type': 'mousedown',
            'bvr_match_class': 'spt_button_hit_wdg',
            'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_button_top")
                var over = top.getElement(".spt_button_over");
                var click = top.getElement(".spt_button_click");
                over.setStyle("display", "none");
                click.setStyle("display", "");
            '''
            } )

            bvr_wdg.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_button_hit_wdg',
            'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_button_top")
                var over = top.getElement(".spt_button_over");
                var click = top.getElement(".spt_button_click");
                over.setStyle("display", "");
                click.setStyle("display", "none");
            '''
            } )


            bvr_wdg.add_relay_behavior( {
            'type': 'mouseenter',
            'bvr_match_class': 'spt_button_hit_wdg',
            'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_button_top")
                var over = top.getElement(".spt_button_over");
                var click = top.getElement(".spt_button_click");
                over.setStyle("display", "");
                click.setStyle("display", "none");
            ''',
            } )

            bvr_wdg.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_button_hit_wdg',
            'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_button_top")
                var over = top.getElement(".spt_button_over");
                var click = top.getElement(".spt_button_click");
                over.setStyle("display", "none");
                click.setStyle("display", "none");
            '''
            } )




    def add_style(my, name, value=None):
        my.top.add_style(name, value)

    def add_behavior(my, behavior):
        my.hit_wdg.add_behavior(behavior)

    def add_class(my, class_name):
        my.hit_wdg.add_class(class_name)

    def set_attr(my, attr, name):
        my.hit_wdg.set_attr(attr, name)


    

    def add_arrow_behavior(my, behavior):
        my.arrow_menu.add_behavior(behavior)
        my.show_arrow_menu = True

    def set_show_arrow_menu(my, flag):
        my.show_arrow_menu = flag

    def get_arrow_wdg(my):
        return my.arrow_menu

    def get_show_arrow_menu(my):
        return my.show_arrow_menu

    def set_show_title(my, flag):
        my.kwargs['show_title' ] = flag

    def add_dialog(my, dialog):
        my.dialog = dialog


    def get_button_wdg(my):
        return my.hit_wdg

    def get_icon_wdg(my):
        return my.icon_div


    def get_display(my):

        top = my.top
        top.add_style("white-space: nowrap")
        #top.add_style("position: relative")

        base = "%s/%s" % (BASE, my.top.get_theme() )


        show_menu = my.kwargs.get("show_menu")
        is_disabled = my.kwargs.get("is_disabled")

        button = DivWdg()
        button.add_style("float: left")
        
        my.inner = button
        top.add(button)
        my.inner.add_class("hand")

        button.add_class("spt_button_top")
        button.add_style("position: relative")

        #img = "<img src='%s/MainButtonSlices_button.png'/>" % base
        #img_div = DivWdg(img)
        #button.add(img_div)
        #img_div.add_style("opacity", ALPHA)

        img_div = DivWdg()
        button.add(img_div)
        img_div.add_style("width: 30px")
        img_div.add_style("height: 35px")
       
       

        over_div = DivWdg()
        button.add(over_div)
        over_div.add_class("spt_button_over")
        over_img = "<img src='%s/MainButton_over.png'/>" % base
        over_div.add(over_img)
        over_div.add_style("position: absolute")
        over_div.add_style("top: 0px")
        over_div.add_style("left: 0px")
        over_div.add_style("display: none")

        click_div = DivWdg()
    
        button.add(click_div)
        click_div.add_class("spt_button_click")
        click_img = "<img src='%s/MainButton_click.png'/>" % base
        click_div.add(click_img)
        click_div.add_style("position: absolute")
        click_div.add_style("top: 0px")
        click_div.add_style("left: 0px")
        click_div.add_style("display: none")


        title = my.kwargs.get("title")
       
        tip = my.kwargs.get("tip")
        if not tip:
            tip = title

        icon_div = my.icon_div
        button.add(icon_div)
        #icon_div.add_class("spt_button_click")
        icon_str = my.kwargs.get("icon")
        icon = IconWdg(tip, icon_str, right_margin=0, width=16)
        icon.add_class("spt_button_icon")
        icon_div.add(icon)
        icon_div.add_style("position: absolute")
        #TODO: removed this top attr after we trim the top and bottom whitespace of the over image
        icon_div.add_style("top: 12px")
        icon_div.add_style("left: 6px")

        if my.is_disabled:
            icon_div.add_style("opacity: 0.5")
        

        my.icon_div = icon_div
        
       

        my.show_arrow = my.kwargs.get("show_arrow") in [True, 'true']
        if my.show_arrow or my.dialog:
            arrow_div = DivWdg()
            button.add(arrow_div)
            arrow_div.add_style("position: absolute")
            arrow_div.add_style("top: 24px")
            arrow_div.add_style("left: 20px")

            arrow = IconWdg(tip, IconWdg.ARROW_MORE_INFO)
            arrow_div.add(arrow)


        web = WebContainer.get_web()
        is_IE = web.is_IE()

        #my.hit_wdg.add_style("height: 100%")
        my.hit_wdg.add_style("width: 100%")
        if is_IE:
            my.hit_wdg.add_style("filter: alpha(opacity=0)")
            my.hit_wdg.add_style("height: 40px")
        else:
            my.hit_wdg.add_style("height: 100%")
            my.hit_wdg.add_style("opacity: 0.0")

        if my.is_disabled:
            my.hit_wdg.add_style("display: none")

        button.add(my.hit_wdg)


        my.hit_wdg.add_style("position: absolute")
        my.hit_wdg.add_style("top: 0px")
        my.hit_wdg.add_style("left: 0px")
        my.hit_wdg.add_attr("title", tip)


        """
        my.hit_wdg.add_behavior( {
        'type': 'hover',
        'cbjs_action_over': '''
            var top = bvr.src_el.getParent(".spt_button_top")
            var over = top.getElement(".spt_button_over");
            var click = top.getElement(".spt_button_click");
            over.setStyle("display", "");
            click.setStyle("display", "none");
        ''',
        'cbjs_action_out': '''
            var top = bvr.src_el.getParent(".spt_button_top")
            var over = top.getElement(".spt_button_over");
            var click = top.getElement(".spt_button_click");
            over.setStyle("display", "none");
            click.setStyle("display", "none");
        '''
        } )
        """



        # add a second arrow widget
        if my.show_arrow_menu:
            my.inner.add(my.arrow_div)
            my.arrow_div.add_attr("title", "More Options")
            my.arrow_div.add_style("position: absolute")
            my.arrow_div.add_style("top: 11px")
            my.arrow_div.add_style("left: 20px")
            my.arrow_div.add(my.arrow_menu)






        if my.dialog:
            top.add(my.dialog)
            dialog_id = my.dialog.get_id()
            my.hit_wdg.add_behavior( {
            'type': 'click_up',
            'dialog_id': dialog_id,
            'cbjs_action': '''
            var dialog = $(bvr.dialog_id);
            var pos = bvr.src_el.getPosition();
            var size = bvr.src_el.getSize();
            //var dialog = $(bvr.dialog_id);
            dialog.setStyle("left", pos.x);
            dialog.setStyle("top", pos.y+size.y);
            spt.toggle_show_hide(dialog);

            '''
            } )




        return top




    def get_displayxx(my):

        show_menu = my.kwargs.get("show_menu")
        is_disabled = my.kwargs.get("is_disabled")

        show_title = my.kwargs.get("show_title")
        show_title = show_title in ['True', True]

        width = 35 
        if show_title:
            height = 26
        else:
            height = 20
        height = 30

        top = my.top
        top.add_class("spt_button_top")
        top.add_style("overflow: hidden")


        #border = top.get_color("border")
        #top.add_border(-20)
        top.add_gradient("background", "background", 20, -35)
        top.add_style("border-width: 1px 0 1px 0")
        top.add_style("border-style: solid")
        top.add_style("border-color: %s" % top.get_color('border'))
        #top.add_style("margin-left: -1px")

        inner = my.inner
        top.add(inner)
        inner.add_color("color", "color3")
        inner.add_style("padding-top: 3px")
        inner.add_style("overflow: hidden")

        title = my.kwargs.get("title")

        inner.add_class("hand")
        inner.add_style("z-index: 20")
        #inner.add_style("overflow: hidden")
        #inner.add_style("opacity: 0.5")
        inner.add_attr("title", title)

        my.button.add_style("margin-top: 5px")
        inner.add(my.button)
        icon_str = my.kwargs.get("icon")
        icon = IconWdg(title, icon_str)
        my.button.add(icon)
        icon.add_class("spt_button_icon")

        my.show_arrow = my.kwargs.get("show_arrow") in [True, 'true']
        if my.show_arrow or my.dialog:
            arrow = IconWdg(title, IconWdg.ARROW_MORE_INFO)
            inner.add(arrow)
            arrow.add_style("position: absolute")
            arrow.add_style("float: left")
            arrow.add_style("margin-left: 2px")
            arrow.add_style("margin-top: -10px")




        inner.add_style("font-size: 8px")
        inner.add_style("height: %spx" % height)
        inner.add_style("width: %spx" % width)
        inner.add_style("text-align: center")

        show_title = False
        if show_title:
            title_div = DivWdg()
            title_div.add(title)
            inner.add(title_div)



        inner.add_behavior( {
        'type': 'click',
        'width': width,
        'cbjs_action': '''
            var button = bvr.src_el;
            button.setStyle("border-style", "ridge");
            button.setStyle("width", bvr.width-2);
        '''
        } )


        inner.add_behavior( {
        'type': 'click_up',
        'width': width,
        'cbjs_action': '''
            var button = bvr.src_el;
            button.setStyle("border-style", "none");
            button.setStyle("width", bvr.width);
        '''
        } )


        inner.add_behavior( {
        'type': 'hover',
        'width': width,
        'cbjs_action_over': '''
            var button = bvr.src_el;
            var icon = button.getElement(".spt_button_icon");
            icon.setStyle('opacity', '1');
        ''',
        'cbjs_action_out': '''
            var button = bvr.src_el;
            button.setStyle("border-style", "none");
            var icon = button.getElement(".spt_button_icon");
            icon.setStyle('opacity', '0.5');

            button.setStyle("width", bvr.width);

        '''
 
        } )


        if show_menu in ['true', True]:
            inner.add_style("float: left")
            arrow_div = DivWdg()
            top.add(arrow_div)
            arrow_div.add_style("opacity: 0.5")
            arrow_div.add_style("z-index: 100")
            arrow_div.add_style("height: %spx" % height)
            arrow_div.add_style("border-left: dotted 1px %s" % arrow_div.get_color("border") )
            #arrow_div.add_style("margin-left: -15px")
            arrow_div.add_style("float: left")

            arrow = DivWdg(IconWdg("More Options", IconWdg.ARROW_MORE_INFO))
            arrow.add_style("margin-top: 8px")
            arrow_div.add(arrow)
            arrow_div.add_style("position: relative")


            arrow_div.add_behavior( {
            'type': 'hover',
            'cbjs_action_over': '''
                var button = bvr.src_el;
                var height = parseInt(button.getStyle("height").replace("px",""));
                var width = parseInt(button.getStyle("width").replace("px",""));
                button.setStyle('opacity', '1');
                button.setStyle('border', 'solid 1px red');
                button.setStyle("height", height-2);
                button.setStyle("width", width-2);
            ''',
            'cbjs_action_out': '''
                var button = bvr.src_el;

                var height = parseInt(button.getStyle("height").replace("px",""));
                var width = parseInt(button.getStyle("width").replace("px",""));

                button.setStyle('opacity', '0.5');
                button.setStyle('border', '');
                button.setStyle("height", height+2);
                button.setStyle("width", width+2);
            '''
     
            } )

            my.add_menu_wdg(arrow_div)



        if is_disabled in ['true', True]:
            disabled_div = DivWdg()
            disabled_div.add_class("spt_save_button_disabled")
            disabled_div.set_attr("title", "%s (Disabled)" % title)
            disabled_div.add_style("position: relative")
            disabled_div.add_style("height: %spx" % (height+3))
            disabled_div.add_style("width: %spx" % width)
            #disabled_div.add_style("margin-left: -%spx" % width)
            disabled_div.add_style("margin-top: -%spx" % (height+3))
            disabled_div.add_style("opacity", "0.6")
            disabled_div.add_style("background", "#AAA")
            inner.add_style("opacity", "1")
            top.add(disabled_div)



        if my.dialog:
            top.add(my.dialog)
            dialog_id = my.dialog.get_id()
            inner.add_behavior( {
            'type': 'load',
            'height': height,
            'dialog_id': dialog_id,
            'cbjs_action': '''
            var pos = bvr.src_el.getPosition();
            var el = $(bvr.dialog_id);
            el.setStyle("left", pos.x);
            el.setStyle("top", pos.y+bvr.height+13);
            '''
            } )

            my.inner.add_behavior( {
            'type': 'click_up',
            'dialog_id': dialog_id,
            'cbjs_action': '''
            var dialog = $(bvr.dialog_id);
            spt.toggle_show_hide(dialog);
            '''
            } )


        return top



    def add_menu_wdg(my, button, menus):

        from tactic.ui.container import SmartMenu

        my.menus = []
        my.menus.append(menu.get_data())

        smenu_set = SmartMenu.add_smart_menu_set( button, { 'BUTTON_MENU': my.menus } )
        SmartMenu.assign_as_local_activator( button, "BUTTON_MENU", True )
 






class ActionButtonWdgOld(DivWdg):


    ARGS_KEYS = {
    'title': {
        'description': 'Value to show on actual button',
        'type': 'TextWdg',
        'order': 0,
        'category': 'Options'
    },
    'tip': {
        'description': 'Tool tip info to show when mouse hovers over button',
        'type': 'TextWdg',
        'order': 1,
        'category': 'Options'
    },
    'width': {
        'description': 'Button Width',
        'type': 'TextWdg',
        'order': 2,
        'category': 'Options'
    },
    'size': {
        'description': 'Button size, Medium (m) or Large (l)',
        'type': 'SelectWdg',
        'values' : 'm|l',
        'order': 3,
        'category': 'Options'
    },
    'action': {
        'description': 'Javascript callback',
        'type': 'TextAreaWdg',
        'order': 4,
        'category': 'Options'
    }
    }
 
    def __init__(my, **kwargs):
        #my.top = DivWdg()
        my.kwargs = kwargs
        my.text_wdg = DivWdg()
        my.table = Table()
        my.table.add_row()
        my.table.add_style("color", "#333")
        my.td = my.table.add_cell()
        my.td.add_class("spt_action_button")
        super(ActionButtonWdgOld,my).__init__()

        web = WebContainer.get_web() 
        my.browser = web.get_browser()
        

    def add_behavior(my, behavior):
        my.td.add_behavior(behavior)

    """
    def add_style(my, name, value=None):
        my.add_style(name, value)
    """

    def add_top_behaviors(my, top):
        top.add_relay_behavior( {
        'type': 'mouseover',
        'bvr_match_class': 'spt_action_button_hit',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_button_top");
            var img = top.getElement(".spt_button_img");
            img.src = bvr.src_el.getAttribute("spt_img_src_over");
        '''
        } ) 

        top.add_relay_behavior( {
        'type': 'mouseout',
        'bvr_match_class': 'spt_action_button_hit',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_button_top");
            if (top) {
                var img = top.getElement(".spt_button_img");
                img.src = bvr.src_el.getAttribute("spt_img_src_up");
            }
        '''
        } )

        top.add_relay_behavior( {
        'type': 'mousedown',
        'bvr_match_class': 'spt_action_button_hit',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_button_top");
            var img = top.getElement(".spt_button_img");
            img.src = bvr.src_el.getAttribute("spt_img_src_click");
        '''
        } )
        top.add_relay_behavior( {
        'type': 'mouseup',
        'bvr_match_class': 'spt_action_button_hit',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_button_top");
            if (top) {
                var img = top.getElement(".spt_button_img");
                img.src = bvr.src_el.getAttribute("spt_img_src_up");
            }
        '''
        } )





    def get_display(my):
        my.add_class("spt_button_top")
        # no need to define top
        #my.add(top)

        opacity = my.kwargs.get("opacity")
        if not opacity:
            opacity = 1.0 
        my.add_style("opacity: %s" % opacity)

        base = "%s/%s" % (BASE, my.get_theme() )

        # medium or large only
        size = my.kwargs.get("size")
        if not size:
            size = 'medium'
        size = size[:1]
        img_src = {
            'over': '%s/btn_%s_over.png' % (base, size),
            'click': '%s/btn_%s_click.png' % (base, size),
            'up': '%s/btn_%s_up.png' % (base, size),
        }

        
        if size == 'm':
            top_width = 83
            my.add_style("width: %spx"%top_width)
        if size == 'l':
            top_width = 127
            my.add_style("width: %spx"%top_width)

        my.add(my.table)
        td = my.td
        button_div = DivWdg()
        td.add(button_div)
        button_div.add_style("position: relative")
        button_div.add_style("text-align: center")
        button_div.add_style("width: 100%")


        # FIXME: this does not work when trying to do a global view
        # There are issues with mutiple behavior clashing within
        # the relay hierarchy.

        #request_top_wdg = Container.get("request_top_wdg")
        #if not request_top_wdg:
        #    request_top_wdg = my.table
        request_top_wdg = my.table

        try:
            button_bvr = request_top_wdg.has_class("spt_button_behaviors")
            if not button_bvr:
                my.add_top_behaviors(request_top_wdg)
                request_top_wdg.add_class("spt_button_behaviors")
        except Exception, e:
            print "WARNING: ", e


        title = my.kwargs.get("title")
        if not title:
            title = "No Title"

        img = HtmlElement.img(src=img_src.get('up'))
        button_div.add(img)
        img.add_class("spt_button_img")
        img.add_style("opacity: 1.0")
        # stretch it wider in case the text is longer, 
        # don't make it too long though
        if len(title) > 10:
            width = len(title)/8.0 * 60
            if width < top_width:
                width = top_width
            img.add_style('width', width)
            img.add_style('height', '28px')
        if not title:
            title = "(No title)"
        #title = "Search"
        tip = my.kwargs.get("tip")
        if not tip:
            tip = title
        my.add_attr("title", tip)


        title2 = my.kwargs.get("title2")
        if title2:
            td.add_behavior( {
            'type': 'click_up',
            'title1': title,
            'title2': title2,
            'cbjs_action': '''
            var label_el = bvr.src_el.getElement(".spt_label");
            var label1 = "<b>" + bvr.title1 + "</b>";
            var label2 = "<b>" + bvr.title2 + "</b>";
            if (label_el.innerHTML == label1) {
                label_el.innerHTML = label2;
            }
            else {
                label_el.innerHTML = label1;
            }
            '''
            } )


        text_div = my.text_wdg
        button_div.add(text_div)
        text_div.add_class("spt_label")
        text_div.add_style("position: absolute")
        text_div.add("<b>%s</b>" % title)
        text_div.add_style("width: 100%")

	if my.browser == 'Qt' and os.name != 'nt':
            text_div.add_style("top: 8px")
        else:
	    text_div.add_style("top: 6px")


        text_div.add_style("z-index: 10")
        text_div.add_attr('spt_text_label', title)
        #text_div.add_style("border: solid 1px blue")


        td.add_attr("spt_img_src_over", img_src.get('over'))
        td.add_attr("spt_img_src_click", img_src.get('click'))
        td.add_attr("spt_img_src_up", img_src.get('up'))
        td.add_class("spt_action_button_hit")

        text_div.add_class("hand")


        return super(ActionButtonWdgOld,my).get_display()





class ActionButtonWdg(DivWdg):


    ARGS_KEYS = {
    'title': {
        'description': 'Value to show on actual button',
        'type': 'TextWdg',
        'order': 0,
        'category': 'Options'
    },
    'title2': {
        'description': 'Alt Value to show on actual button when clicked on',
        'type': 'TextWdg',
        'order': 0,
        'category': 'Options'
    },
    'tip': {
        'description': 'Tool tip info to show when mouse hovers over button',
        'type': 'TextWdg',
        'order': 1,
        'category': 'Options'
    },
    'action': {
        'description': 'Javascript callback',
        'type': 'TextAreaWdg',
        'order': 1,
        'category': 'Options'
    }
    }
 
    def __init__(my, **kwargs):
        web = WebContainer.get_web() 
        is_Qt_OSX = web.is_Qt_OSX()
        my.browser = web.get_browser()

        #is_Qt_OSX = False
        if is_Qt_OSX:
            my.redirect = ActionButtonWdgOld(**kwargs)
        else:
            my.redirect = None

        #my.top = DivWdg()
        my.kwargs = kwargs
        my.text_wdg = DivWdg()
        my.table = Table()
        my.table.add_row()
        my.table.add_style("color", "#333")
        my.td = my.table.add_cell()
        my.td.add_class("spt_action_button")
        super(ActionButtonWdg,my).__init__()


    def add_behavior(my, behavior):
        if my.redirect:
            return my.redirect.add_behavior(behavior)

        my.td.add_behavior(behavior)


    def add_style(my, name, value=None):
        if my.redirect:
            return my.redirect.add_style(name, value)

        super(ActionButtonWdg,my).add_style(name, value)

    def add_class(my, value):
        if my.redirect:
            return my.redirect.add_class(value)

        super(ActionButtonWdg,my).add_class(value)





    def add_top_behaviors(my, top):
        if my.redirect:
            return my.redirect.add_top_behavior(top)


    def get_display(my):
        if my.redirect:
            return my.redirect.get_display()


        my.add_class("spt_button_top")
        # no need to define top
        #my.add(top)

        my.add_style("margin: 0px 3px")

        opacity = my.kwargs.get("opacity")
        if not opacity:
            opacity = 1.0 
        my.add_style("opacity: %s" % opacity)

        base = "%s/%s" % (BASE, my.get_theme() )

        my.add(my.table)
        td = my.td
        td.add_style("text-align: center")

        size = my.kwargs.get("size")
        if not size:
            size = 'medium'
        size = size[:1]


        width = my.kwargs.get("width")
        if width:
            top_width = int(width)
            my.add_style("width: %s"%top_width)
        else:
            top_width = 40
            if size == 'm':
                top_width = 83
                my.add_style("width: %spx"%top_width)
            if size == 'l':
                top_width = 127
                my.add_style("width: %spx"%top_width)

        



        #request_top_wdg = Container.get("request_top_wdg")
        #if not request_top_wdg:
        #    request_top_wdg = my.table
        request_top_wdg = my.table

        try:
            button_bvr = request_top_wdg.has_class("spt_button_behaviors")
            if not button_bvr:
                my.add_top_behaviors(request_top_wdg)
                request_top_wdg.add_class("spt_button_behaviors")
        except Exception, e:
            print "WARNING: ", e


        title = my.kwargs.get("title")
        if not title:
            title = "No Title"

        # stretch it wider in case the text is longer, 
        # don't make it too long though
        if len(title) > 10:
            width = len(title)/8.0 * 60
            if width < top_width:
                width = top_width
            td.add_style('width', width)
            td.add_style('height', '28px')
        if not title:
            title = "(No title)"

        #title = "Search"
        tip = my.kwargs.get("tip")
        if not tip:
            tip = title
        my.add_attr("title", tip)


        title2 = my.kwargs.get("title2")
        if title2:
            td.add_behavior( {
            'type': 'click_up',
            'title1': title,
            'title2': title2,
            'cbjs_action': '''
            var label_el = bvr.src_el.getElement(".spt_label");
            var label1 = "<b>" + bvr.title1 + "</b>";
            var label2 = "<b>" + bvr.title2 + "</b>";
            if (label_el.innerHTML == label1) {
                label_el.innerHTML = label2;
            }
            else {
                label_el.innerHTML = label1;
            }
            '''
            } )


        from pyasm.widget import ButtonWdg
        button = ButtonWdg()
        button.add_style("width: %s" % top_width)
        button.add_class('spt_label')

        icon = my.kwargs.get("icon")
        if icon:
            icon_div = DivWdg() 
            icon = IconWdg(title, icon, width=16 )
            icon_div.add(icon)
            button.add(icon_div)
            my.table.add_style("position: relative")
            icon_div.add_style("position: absolute")
            icon_div.add_style("left: 5px")
            icon_div.add_style("top: 6px")
            title = " &nbsp; &nbsp; %s" % title
            button.add_style("padding: 2px")

        button.set_name(title)

        td.add(button)
        #button.add_border()
        #button.set_box_shadow("0px 0px 1px", color=button.get_color("shadow"))



        if my.browser == 'Qt' and os.name != 'nt':
            button.add_style("top: 8px")
        else:
            button.add_style("top: 6px")

        # BOOTSTRAP
        color = my.kwargs.get("color")
        button.add_class('btn')
        if color:
            if color.startswith("#"):
                button.add_style("background", color)
            else:
                button.add_class('btn-%s' % color)
        else:
            button.add_class('btn-default')
        button.add_class('btn-sm')
        button.add_style("top: 0px")


        button.add_attr('spt_text_label', title)
        td.add_class("spt_action_button_hit")
        button.add_class("hand")

        return super(ActionButtonWdg,my).get_display()








class IconButtonWdg(DivWdg):
    def __init__(my, **kwargs):
        my.kwargs = kwargs
        super(IconButtonWdg, my).__init__()
        my.base = "%s/%s" % (BASE, my.get_theme() )
        my.height = 20
        my.width = 28


    def init(my):
        if not Container.get_dict("JSLibraries", "spt_icon_button"):
            doc_top = Container.get("TopWdg::top")
            if doc_top:
                doc_top.add_behavior( {
                    'type': 'load',
                    'cbjs_action': '''
                    spt.Environment.get().add_library("spt_icon_button");
                    '''
                } )
                bvr_wdg = doc_top
            else:
                bvr_wdg = my


            bvr_wdg.add_relay_behavior( {
            'type': 'mouseenter',
            'bvr_match_class': 'spt_icon_button_top',
            'cbjs_action': '''
                var out = bvr.src_el.getElement(".spt_button_out");
                var over = bvr.src_el.getElement(".spt_button_over");
                var click = bvr.src_el.getElement(".spt_button_click");
                out.setStyle("display", "none");
                over.setStyle("display", "");
                click.setStyle("display", "none");
            '''
            } )

            bvr_wdg.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_icon_button_top',
            'cbjs_action': '''
                var out = bvr.src_el.getElement(".spt_button_out");
                var over = bvr.src_el.getElement(".spt_button_over");
                var click = bvr.src_el.getElement(".spt_button_click");
                out.setStyle("display", "");
                over.setStyle("display", "none");
                click.setStyle("display", "none");
            '''
            } )
            
            bvr_wdg.add_relay_behavior( {
            'type': 'mousedown',
            'bvr_match_class': 'spt_icon_button_top',
            'cbjs_action': '''
                var out = bvr.src_el.getElement(".spt_button_out");
                var over = bvr.src_el.getElement(".spt_button_over");
                var click = bvr.src_el.getElement(".spt_button_click");
                out.setStyle("display", "none");
                over.setStyle("display", "none");
                click.setStyle("display", "");
            '''
            } )

            bvr_wdg.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_icon_button_top',
            'cbjs_action': '''
                var out = bvr.src_el.getElement(".spt_button_out");
                var over = bvr.src_el.getElement(".spt_button_over");
                var click = bvr.src_el.getElement(".spt_button_click");
                over.setStyle("display", "");
                over.setStyle("display", "none");
                click.setStyle("display", "none");
            '''
            } )




    def get_out_img(my):
        return None

    def get_over_img(my):
        return "<img src='%s/icon_button_over_bg.png'/>" % my.base

    def get_click_img(my):
        return "<img src='%s/icon_button_click_bg.png'/>" % my.base
        
    def get_offset(my):
        return (2, 0)


    def get_height(my):
        return my.height

    def get_width(my):
        return my.width


    def get_display(my):
        my.add_style("position: relative")
        my.add_class("spt_button_top")
        my.add_style("height: %spx" % my.get_height() )
        my.add_style("width: %spx" % my.get_width() )
        my.add_style("margin: 0px")

        display = DivWdg()
        my.add(display)
        display.add_class("spt_icon_button_top")

        offset = my.get_offset()


        out_div = DivWdg()
        display.add(out_div)
        out_div.add_class("spt_button_out")
        out_img = my.get_out_img()
        out_div.add_style("left: %spx" % offset[0])
        out_div.add_style("top: %spx" % offset[1])
        if out_img:
            out_div.add(out_img)
        out_div.add_style("position: absolute")


        over_div = DivWdg()
        display.add(over_div)
        over_div.add_class("spt_button_over")
        over_img = my.get_over_img()
        over_div.add_style("left: %spx" % offset[0])
        over_div.add_style("top: %spx" % offset[1])
        over_div.add(over_img)
        over_div.add_style("position: absolute")
        over_div.add_style("display: none")


        click_div = DivWdg()
        display.add(click_div)
        click_div.add_class("spt_button_click")
        click_img = my.get_click_img()
        click_div.add_style("left: %spx" % offset[0])
        click_div.add_style("top: %spx" % offset[1])
        click_div.add(click_img)
        click_div.add_style("position: absolute")
        click_div.add_style("display: none")



        icon_str = my.kwargs.get("icon")
        title = my.kwargs.get("title")
        tip = my.kwargs.get("tip")
        if not tip:
            tip = title

        icon_div = DivWdg()
        icon_div.add_class("hand")
        icon_div.add_style("top: 3px")
        icon_div.add_style("left: 5px")
        display.add(icon_div)
        icon_div.add_style("position: absolute")
        if my.get_width() < 30:
            width = 16
        else:
            width = None

        icon = IconWdg(title, icon_str, width=width)
        icon_div.add(icon)
        if tip:
            display.add_attr("title", tip)


        my.show_arrow = my.kwargs.get("show_arrow") in [True, 'true']
        #if my.show_arrow or my.dialog:
        if my.show_arrow:
            arrow_div = DivWdg()
            icon_div.add(arrow_div)
            arrow_div.add_style("position: absolute")
            arrow_div.add_style("top: 13px")
            arrow_div.add_style("left: 11px")

            arrow = IconWdg(title, IconWdg.ARROW_MORE_INFO)
            arrow_div.add(arrow)



        spacer = DivWdg()
        display.add(spacer)
        spacer.add("")


        return super(IconButtonWdg, my).get_display()


from tactic.ui.common import BaseTableElementWdg
class IconButtonElementWdg(BaseTableElementWdg):
    def get_display(my):
        return IconButtonWdg(**my.options)



class SingleButtonWdg(IconButtonWdg):

    def get_out_img(my):
        if my.kwargs.get("show_out") in [False, "false"]:
            return None
        img = "<img src='%s/Opaque_MainButton_out.png'/>" % my.base
        return img

    def get_over_img(my):
        return "<img src='%s/Opaque_MainButton_over.png'/>" % my.base

    def get_click_img(my):
        return "<img src='%s/Opaque_MainButton_click.png'/>" % my.base

    def get_offset(my):
        return (-1, -9)

    def get_height(my):
        #return 30 
        return 20




