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

__all__ = ['ButtonRowWdg', 'ButtonWdg', 'ButtonNewWdg', 'ActionButtonWdg', 'IconButtonWdg', 'IconButtonElementWdg', 'SingleButtonWdg']

import os

from pyasm.common import Container
from pyasm.search import Search, SObjectConfig, SearchType, SObjectFactory
from pyasm.web import HtmlElement, SpanWdg, DivWdg, Table, WebContainer
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg

import os

BASE = '/context/themes2'
ALPHA = "1.0"

import six


class ButtonRowWdg(BaseRefreshWdg):

    def init(self):
        self.top = DivWdg(css='spt_button_row')

    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def get_num_buttons(self):
        return len(self.widgets)

    def get_display(self):

        top = self.top
        top.add_class("SPT_DTS")
        # make it focusable
        top.set_attr('tabIndex','-1')
        buttons = []

        show_title = self.kwargs.get("show_title")
        show_title = show_title in ['True', True]

        for button in self.widgets:
            if isinstance(button, ButtonNewWdg):
                button.set_show_title(show_title)
            buttons.append(button)

        #top.add( self.get_row_wdg(buttons, show_title=show_title) )
        top.add( self.get_row_wdg_new(buttons, show_title=show_title) )
        #top.add( self.get_row_wdgXX(buttons, show_title=show_title) )
        return top


    def get_row_wdg_new(self, buttons, show_title=False):

        div = DivWdg()
        div.add_class("d-flex")
        for button in buttons:
            div.add(button)
        return div

    


    def get_row_wdg(self, buttons, show_title=False):

        table = Table()
        table.set_round_corners(20)
        table.add_style("margin-top: -3px")
        table.add_attr("cellspacing", "0px")
        table.add_attr("cellpadding", "0px")
        table.add_row()

        base = "%s/%s" % (BASE, self.top.get_theme() )

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




    def get_row_wdgXX(self, buttons, show_title=False):

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
        right.add_style("border-width: 1px 1px 1px 0px")
        top.add(right)


        return top


__all__.extend(['BootstrapButtonRowWdg'])
class BootstrapButtonRowWdg(BaseRefreshWdg):

    def init(self):

        icon = self.kwargs.get("collapse_icon") or "FA_ELLIPSIS_V"
        collapse_title = self.kwargs.get("collapse_title") or "Tools"
        self.toggle_btn = ButtonNewWdg(title="Tools", icon=icon)

    def set_toggle_btn(self, wdg):
        self.toggle_btn = wdg

    def get_display(self):

        top = self.top
        top.add_class("spt_bs_btn_row_top")
        top.add(self.get_bootstrap_styles())

        top.add(self.get_collapse_display())
        top.add(self.get_button_display())


        return top


    def get_bootstrap_styles(self):
        style = HtmlElement.style("""
        
        @media (min-width: 576px)
            .d-sm-flex {
                display: flex !important;
            }
        }

        """)
        
        return style

    def get_button_display(self):

        button_row_wdg = DivWdg()
        button_row_wdg.add_class("d-none d-sm-flex")
        button_row_wdg.add_class("spt_bs_btn_row")

        for button in self.widgets:
            button_row_wdg.add(button)

        return button_row_wdg
        
        
    def get_collapse_display(self):

        collapse_div = DivWdg()
        collapse_div.add_class("dropdown d-block d-sm-none")
        collapse_div.add_class("spt_bs_collapse_top")

        toggle_btn = self.toggle_btn
        toggle_btn_id = toggle_btn.set_unique_id()
        collapse_div.add(toggle_btn)
        
        toggle_btn.add_class("dropdown-toggle") 
        # Dropdown behavior
        toggle_btn.add_attr("data-toggle", "dropdown")
        toggle_btn.add_attr("aria-haspopup", "true")
        toggle_btn.add_attr("aria-expanded", "false")

        button_menu = DivWdg()
        collapse_div.add(button_menu)
        button_menu.add_class("dropdown-menu")
        
        # HACK
        button_menu.add_style("right", "0")
        button_menu.add_style("left", "auto")


        button_menu.add_attr("aria-labelledby", toggle_btn_id)

        item_template = HtmlElement("a")
        collapse_div.add(item_template)
        item_template.add_class("SPT_TEMPLATE")
        item_template.add_class("d-none")
        item_template.add_class("dropdown-item")

        collapse_div.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            button_row_top = bvr.src_el.getParent(".spt_bs_btn_row_top");
            row_top = button_row_top.getElement(".spt_bs_btn_row");
            collapse_top = bvr.src_el;
            menu = collapse_top.getElement(".dropdown-menu")
 
            // Dynamically build the tab menu

            // Reset menu
            menu.innerHTML = "";

            item_template = collapse_top.getElement(".SPT_TEMPLATE");

            // TODO: Fix styling.
            handle_header = function(header) {
                header.removeAttribute("style");
            }

            var new_items = [];
            items = row_top.getElements(".spt_collapsible_btn");
            items.forEach(function(item) {
                new_item = spt.behavior.clone(item_template);
                new_item.removeClass("SPT_TEMPLATE");
                new_item.removeClass("d-none");
                
                item.removeClass("d-none");
                item.inject(new_item);
                new_items.push(new_item);
                
            });

            new_items.forEach(function(item){
                item.inject(menu);
            }); 
        
                 
            '''
        })

        return collapse_div


class ButtonWdg(BaseRefreshWdg):
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
        'is_disabled': 'True|False - determines whether or not the button is disabled',
        'sub_icon': {
            'description': 'The subscript icon key to be used for the button',
            'category': 'Option',
        },
    }

    def init(self):
        #self.inner = DivWdg()
        self.dialog = None
        self.button = DivWdg()
        self.hit_wdg = DivWdg()
        self.hit_wdg.add_class("spt_button_hit_wdg")
        self.arrow_div = DivWdg()
        self.arrow_menu = IconButtonWdg(title="More Options", icon=IconWdg.ARROWHEAD_DARK_DOWN)

        self.show_arrow_menu = self.kwargs.get("show_arrow") or False
        # for icon decoration
        self.icon_div = DivWdg()

        self.is_disabled = self.kwargs.get("is_disabled") in [True,"true"]

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
                bvr_wdg = self.top

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




    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def add_behavior(self, behavior):
        self.hit_wdg.add_behavior(behavior)

    def add_class(self, class_name):
        self.hit_wdg.add_class(class_name)

    def set_attr(self, attr, name):
        self.hit_wdg.set_attr(attr, name)

    def set_unique_id(self):
        return self.hit_wdg.set_unique_id()

    def add_arrow_behavior(self, behavior):
        self.arrow_menu.add_behavior(behavior)
        self.show_arrow_menu = True

    def set_show_arrow_menu(self, flag):
        self.show_arrow_menu = flag

    def get_arrow_wdg(self):
        return self.arrow_menu

    def get_show_arrow_menu(self):
        return self.show_arrow_menu

    def set_show_title(self, flag):
        self.kwargs['show_title' ] = flag

    def add_dialog(self, dialog):
        self.dialog = dialog


    def get_button_wdg(self):
        return self.hit_wdg

    def get_collapsible_wdg(self):
        return self.collapsible_btn

    def get_icon_wdg(self):
        return self.icon_div


    def get_display(self):

        top = self.top
        top.add_style("white-space: nowrap")
        #top.add_style("position: relative")

        base = "%s/%s" % (BASE, self.top.get_theme() )


        show_menu = self.kwargs.get("show_menu")
        is_disabled = self.kwargs.get("is_disabled")

        button = DivWdg()
        
        self.inner = button
        top.add(button)
        self.inner.add_class("hand")

        button.add_class("spt_button_top")
        button.add_style("position: relative")
        button.add_style("float: left")

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

        title = self.kwargs.get("title")
       
        tip = self.kwargs.get("tip")
        if not tip:
            tip = title

        icon_div = self.icon_div
        button.add(icon_div)
        #icon_div.add_class("spt_button_click")
        icon_str = self.kwargs.get("icon")
        icon = IconWdg(tip, icon_str, right_margin=0, width=16)
        icon.add_class("spt_button_icon")
        icon_div.add(icon)
        icon_div.add_style("position: absolute")
        #TODO: removed this top attr after we trim the top and bottom whitespace of the over image
        icon_div.add_style("top: 12px")
        icon_div.add_style("left: 6px")

        if self.is_disabled:
            icon_div.add_style("opacity: 0.5")
        

        self.icon_div = icon_div

        sub_icon = self.kwargs.get("sub_icon")
        if sub_icon:
            sub_icon = IconWdg(icon=sub_icon, size="8")
            button.add(sub_icon)
            sub_icon.add_style("position: absolute")
            sub_icon.add_style("bottom: 4px")
            sub_icon.add_style("right: 0px")
        
       

        if self.show_arrow_menu or self.dialog:
            arrow_div = DivWdg()
            button.add(arrow_div)
            arrow_div.add_style("position: absolute")
            arrow_div.add_style("top: 24px")
            arrow_div.add_style("left: 20px")

            arrow = IconWdg(tip, IconWdg.ARROW_MORE_INFO)
            arrow_div.add(arrow)


        web = WebContainer.get_web()
        is_IE = web.is_IE()

        #self.hit_wdg.add_style("height: 100%")
        self.hit_wdg.add_style("width: 100%")
        if is_IE:
            self.hit_wdg.add_style("filter: alpha(opacity=0)")
            self.hit_wdg.add_style("height: 40px")
        else:
            self.hit_wdg.add_style("height: 100%")
            self.hit_wdg.add_style("opacity: 0.0")

        if self.is_disabled:
            self.hit_wdg.add_style("display: none")

        button.add(self.hit_wdg)


        self.hit_wdg.add_style("position: absolute")
        self.hit_wdg.add_style("top: 0px")
        self.hit_wdg.add_style("left: 0px")
        self.hit_wdg.add_attr("title", tip)


        # add a second arrow widget
        if self.show_arrow_menu or self.dialog:
            self.inner.add(self.arrow_div)
            self.arrow_div.add_attr("title", "More Options")
            self.arrow_div.add_style("position: absolute")
            self.arrow_div.add_style("top: 11px")
            self.arrow_div.add_style("left: 20px")
            self.arrow_div.add(self.arrow_menu)


        if self.dialog:
            top.add(self.dialog)
            dialog_id = self.dialog.get_id()
            self.hit_wdg.add_behavior( {
            'type': 'click_up',
            'dialog_id': dialog_id,
            'cbjs_action': '''
            var dialog = document.id(bvr.dialog_id);
            var pos = bvr.src_el.getPosition();
            var size = bvr.src_el.getSize();
            //var dialog = document.id(bvr.dialog_id);
            dialog.setStyle("left", pos.x);
            dialog.setStyle("top", pos.y+size.y);
            spt.toggle_show_hide(dialog);

            '''
            } )




        return top


class ButtonNewWdg(ButtonWdg):

    def init(self):
        super(ButtonNewWdg, self).init()
        
        from pyasm.web import ButtonWdg as ButtonHtmlWdg
        self.hit_wdg = ButtonHtmlWdg()
        self.arrow_menu = ButtonHtmlWdg()
        self.arrow_menu.add_class("btn dropdown-toggle spt_arrow_hit_wdg")
        
        icon_str = self.kwargs.get("icon")

        title = self.kwargs.get("title")
        tip = self.kwargs.get("tip")
        if not tip:
            tip = title
        self.title = tip
        
        self.hit_wdg.add_attr("title", tip)

        size = self.kwargs.get("size")
        if not size:
            size = 14
        
        opacity = self.kwargs.get("opacity") or None
        icon = IconWdg(tip, icon_str, opacity=opacity, size=size)
        self.icon = icon

        self.collapsible_btn = DivWdg()

        self.btn_class = self.kwargs.get("btn_class") or "btn bmd-btn-icon"
        
        self.action_class = self.kwargs.get("action_class") or ""

        self.navbar_collapse_target = self.kwargs.get("navbar_collapse_target")

        self.dropdown_id = self.kwargs.get("dropdown_id")

    def add_behavior(self, behavior):              
        self.hit_wdg.add_behavior(behavior)
        self.collapsible_btn.add_behavior(behavior)
                                                   
    def add_class(self, class_name, redirect=True):
        if redirect:
            self.hit_wdg.add_class(class_name)        
            self.collapsible_btn.add_class(class_name)
        else:
            self.top.add_class(class_name)
                                                   
    def set_attr(self, attr, name):                
        self.hit_wdg.set_attr(attr, name)
        self.collapsible_btn.set_attr(attr, name)
                                                   
    def get_bootstrap_styles(self):

        style = HtmlElement.style("""
            .spt_arrow_hit_wdg {
                padding: 3px;
                opacity: 0.6;
                top: 17px;
                left: -11px;
                height: 4px;
            }

        """)


        return style

    def set_arrow_wdg(self, wdg):
        self.arrow_menu = wdg

    def get_display(self):
       
        top = self.top

        top.add(self.get_bootstrap_styles())
        
        top.add(self.collapsible_btn)
        self.collapsible_btn.add_class("spt_collapsible_btn d-none")
        if self.action_class:
            self.collapsible_btn.add_class(self.action_class)
        self.collapsible_btn.add(self.title)

        top.add(self.hit_wdg)
        width = self.kwargs.get("width")
        if width:
            self.hit_wdg.add_style("width: %spx" % width)
            self.hit_wdg.add_style("height: %spx" % width)
            self.hit_wdg.add_style("min-width: %spx" % width)
        self.hit_wdg.add_class(self.btn_class)
        if self.action_class:
            self.hit_wdg.add_class(self.action_class)
        self.hit_wdg.add_class("spt_hit_wdg")
        self.hit_wdg.add(self.icon)
        
        if self.show_arrow_menu or self.dialog:
            top.add(self.arrow_menu)
            top.add_class("d-flex")

        if self.dropdown_id:
            #FIXME: Cannot be combined with collapsible menu
            top.set_id(self.dropdown_id)
            top.set_attr("data-toggle", "dropdown")
            top.set_attr("aria-haspopup", "true")
            top.set_attr("aria-expanded", "false")

        if self.navbar_collapse_target:
            self.add_class("collapsed")
            self.set_attr("type", "button")
            self.set_attr("data-toggle", "collapse")
            self.set_attr("data-target", "#%s" % self.navbar_collapse_target)
            self.set_attr("aria-controls", self.navbar_collapse_target)
            self.set_attr("aria-expanded", "false")
            self.set_attr("aria-label", self.title)
        
        self.hit_wdg.add_behavior ( {
            "type": "load",
            "cbjs_action": """
                $(bvr.src_el).bmdRipples();
            """
        } )
        
        return top





class ActionButtonWdgOldX(DivWdg):


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
 
    def __init__(self, **kwargs):
        #self.top = DivWdg()
        self.kwargs = kwargs
        self.text_wdg = DivWdg()
        self.table = Table()
        self.table.add_row()
        self.table.add_style("color", "#333")
        self.td = self.table.add_cell()
        self.td.add_class("spt_action_button")
        super(ActionButtonWdgOldX,self).__init__()

        web = WebContainer.get_web() 
        self.browser = web.get_browser()
        

    def add_behavior(self, behavior):
        self.td.add_behavior(behavior)

    """
    def add_style(self, name, value=None):
        self.add_style(name, value)
    """

    def add_top_behaviors(self, top):
        top.add_relay_behavior( {
        'type': 'mouseenter',
        'bvr_match_class': 'spt_action_button_hit',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_button_top");
            var img = top.getElement(".spt_button_img");
            img.src = bvr.src_el.getAttribute("spt_img_src_over");
        '''
        } ) 

        top.add_relay_behavior( {
        'type': 'mouseleave',
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





    def get_display(self):
        self.add_class("spt_button_top")
        # no need to define top
        #self.add(top)

        opacity = self.kwargs.get("opacity")
        if not opacity:
            opacity = 1.0 
        self.add_style("opacity: %s" % opacity)

        base = "%s/%s" % (BASE, self.get_theme() )

        # medium or large only
        size = self.kwargs.get("size")
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
            self.add_style("width: %spx"%top_width)
        elif size == 'l':
            top_width = 127
            self.add_style("width: %spx"%top_width)
        elif size:
            self.add_style("width: %spx"%size)

        self.add(self.table)
        td = self.td
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
        #    request_top_wdg = self.table
        request_top_wdg = self.table

        try:
            button_bvr = request_top_wdg.has_class("spt_button_behaviors")
            if not button_bvr:
                self.add_top_behaviors(request_top_wdg)
                request_top_wdg.add_class("spt_button_behaviors")
        except Exception as e:
            print("WARNING: ", e)


        title = self.kwargs.get("title")
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
        tip = self.kwargs.get("tip")
        if not tip:
            tip = title
        self.add_attr("title", tip)


        title2 = self.kwargs.get("title2")
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


        text_div = self.text_wdg
        button_div.add(text_div)
        text_div.add_class("spt_label")
        text_div.add_style("position: absolute")
        text_div.add("<b>%s</b>" % title)
        text_div.add_style("width: 100%")

        if self.browser == 'Qt' and os.name != 'nt':
            text_div.add_style("top: 8px")


        text_div.add_style("z-index: 10")
        text_div.add_attr('spt_text_label', title)
        #text_div.add_style("border: solid 1px blue")


        td.add_attr("spt_img_src_over", img_src.get('over'))
        td.add_attr("spt_img_src_click", img_src.get('click'))
        td.add_attr("spt_img_src_up", img_src.get('up'))
        td.add_class("spt_action_button_hit")

        text_div.add_class("hand")


        return super(ActionButtonWdgOldX,self).get_display()


__all__.extend(['BootstrapButtonWdg'])
class BootstrapButtonWdg(BaseRefreshWdg):
    
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
        'btn_class': {
            'description': 'Bootstrap btn classes',
            'type': 'TextWdg',
            'order': '4',
            'category': 'Options',
            'default': 'btn btn-primary'
        }
    }


    #FIXME: Should this be moved to BaseRefreshWdg?
    def generate_command_key(self, cmd, kwargs={}, ticket=None):
        return self.top.generate_command_key(cmd, kwargs, ticket)
            
    def __init__(self, **kwargs):

        self.kwargs = kwargs

        self.top = DivWdg()

        from pyasm.web import ButtonWdg as ButtonHtmlWdg
        self.button_wdg = ButtonHtmlWdg()
        self.collapsible_wdg = DivWdg()

        self.top.add_class("spt_action_button")
        self.top.add_style("display: inline-block")


        super(BootstrapButtonWdg, self).__init__(**kwargs)

    def add_class(self, class_name, redirect=True):
        if redirect:
            self.button_wdg.add_class(class_name)
            self.collapsible_wdg.add_class(class_name)
        else:
            self.top.add_class(class_name)
    
    def add_behavior(self, behavior):
        self.button_wdg.add_behavior(behavior)
        self.collapsible_wdg.add_behavior(behavior)

    def add_event(self, name, action):
        self.button_wdg.add_event(name, action)
        self.collapsible_wdg.add_event(name, action)
       

    def get_collapsible_wdg(self):
        return self.collapsible_wdg

    def get_button_wdg(self):
        return self.button_wdg

    def get_display(self):
        
        title = self.kwargs.get("title")

        top = self.top
        
        top.add(self.button_wdg)
        self.button_wdg.add_class("btn")
        btn_class = self.kwargs.get("btn_class")
        if not btn_class:
            btn_class = self.kwargs.get("color")
            if btn_class:
                btn_class = "btn-%s" % btn_class
        if not btn_class:
            btn_class = "btn-primary"

        self.button_wdg.add_class(btn_class)
        self.button_wdg.add_class("spt_hit_wdg")
        self.button_wdg.add(title)
        self.button_wdg.add_behavior ( {
            "type": "load",
            "cbjs_action": '''
                $(bvr.src_el).bmdRipples();
           '''
        } )

        size = self.kwargs.get("size")
        if size:
            self.button_wdg.add_style("width", "%spx" % size)

        
        top.add(self.collapsible_wdg)
        self.collapsible_wdg.add_class("spt_collapsible_btn d-none")
        self.collapsible_wdg.add(title)
        
        self.dropdown_id = self.kwargs.get("dropdown_id")
        if self.dropdown_id:
            #FIXME: Cannot be combined with collapsible menu
            top.set_id(self.dropdown_id)
            top.set_attr("data-toggle", "dropdown")
            top.set_attr("aria-haspopup", "true")
            top.set_attr("aria-expanded", "false")

        return top
        



class ActionButtonWdg(BootstrapButtonWdg):
    pass


class ActionButtonWdgOld(DivWdg):


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
 
    def __init__(self, **kwargs):
        web = WebContainer.get_web() 
        is_Qt_OSX = web.is_Qt_OSX()
        self.browser = web.get_browser()

        #is_Qt_OSX = False
        if is_Qt_OSX:
            self.redirect = ActionButtonWdgOldX(**kwargs)
        else:
            self.redirect = None

        #self.top = DivWdg()
        self.kwargs = kwargs
        self.text_wdg = DivWdg()
        self.table = Table()
        self.table.add_row()
        self.table.add_style("color", "#333")
        self.td = self.table.add_cell()
        self.td.add_class("spt_action_button")
        super(ActionButtonWdgOld,self).__init__()


    def add_behavior(self, behavior):
        if self.redirect:
            return self.redirect.add_behavior(behavior)

        self.td.add_behavior(behavior)


    def add_style(self, name, value=None, override=True):
        if self.redirect:
            return self.redirect.add_style(name, value, override=override)

        super(ActionButtonWdg,self).add_style(name, value, override=override)

    def add_class(self, value):
        if self.redirect:
            return self.redirect.add_class(value)

        super(ActionButtonWdg,self).add_class(value)





    def add_top_behaviors(self, top):
        if self.redirect:
            return self.redirect.add_top_behavior(top)


    def get_display(self):
        if self.redirect:
            return self.redirect.get_display()


        self.add_class("spt_button_top")
        # no need to define top
        #self.add(top)

        self.add_style("margin: 0px 3px", override=False)

        opacity = self.kwargs.get("opacity")
        if not opacity:
            opacity = 1.0 
        self.add_style("opacity: %s" % opacity)

        base = "%s/%s" % (BASE, self.get_theme() )

        self.add(self.table)
        td = self.td
        td.add_style("text-align: center")

        size = self.kwargs.get("size")
        if not size:
            size = 'medium'
        size = size[:1]


        width = self.kwargs.get("width")
        if width:
            top_width = int(width)
            self.add_style("width: %spx"%top_width)
        else:
            top_width = 40
            if size == 'm':
                top_width = 83
                self.add_style("width: %spx"%top_width)
            if size == 'l':
                top_width = 127
                self.add_style("width: %spx"%top_width)
            if size == 'b':
                top_width = "100%"
                self.add_style("width: %spx"%top_width)
                self.table.add_style("width: 100%")


        



        #request_top_wdg = Container.get("request_top_wdg")
        #if not request_top_wdg:
        #    request_top_wdg = self.table
        request_top_wdg = self.table

        try:
            button_bvr = request_top_wdg.has_class("spt_button_behaviors")
            if not button_bvr:
                self.add_top_behaviors(request_top_wdg)
                request_top_wdg.add_class("spt_button_behaviors")
        except Exception as e:
            print("WARNING: ", e)


        title = self.kwargs.get("title")
        if not title:
            title = "No Title"

        # stretch it wider in case the text is longer, 
        # don't make it too long though
        if not isinstance(top_width, six.string_types) and len(title) > 10:
            width = len(title)/8.0 * 60
            if width < top_width:
                width = top_width
            td.add_style('width', width)
            td.add_style('height', '28px')
        if not title:
            title = "(No title)"

        #title = "Search"
        tip = self.kwargs.get("tip")
        if not tip:
            tip = title
        self.add_attr("title", tip)

        
        title2 = self.kwargs.get("title2")
        if title2:
            td.add_behavior( {
            'type': 'click_up',
            'title1': title,
            'title2': title2,
            'cbjs_action': '''
            var label_el = bvr.src_el.getElement(".spt_label");
            var label1 = bvr.title1;
            var label2 = bvr.title2;
            if (label_el.value == label1) {
                label_el.value = label2;
            }
            else {
                label_el.value = label1;
            }
            '''
            } )


        from pyasm.widget import ButtonWdg
        button = ButtonWdg()
        button.add_style("width: %spx" % top_width)
        button.add_class('spt_label')

        icon = self.kwargs.get("icon")
        if icon:
            icon_div = DivWdg() 
            icon = IconWdg(title, icon, width=16 )
            icon_div.add(icon)
            button.add(icon_div)
            self.table.add_style("position: relative")
            icon_div.add_style("position: absolute")
            icon_div.add_style("left: 5px")
            icon_div.add_style("top: 6px")
            title = " &nbsp; &nbsp; %s" % title
            button.add_style("padding: 2px")

        button.set_name(title)

        td.add(button)
        #button.add_border()
        #button.set_box_shadow("0px 0px 1px", color=button.get_color("shadow"))



        if self.browser == 'Qt' and os.name != 'nt':
            button.add_style("top: 8px")

        # BOOTSTRAP
        if self._use_bootstrap():
            button.add_class("btn btn-sm btn-block btn-outline-primary")
        else:
            color = self.kwargs.get("color")
            button.add_class('btn')
            if color:
                if color.startswith("#"):
                    button.add_style("background", color)
                else:
                    button.add_class('btn-%s' % color)
            else:
                button.add_class('btn-default')
            button.add_class('btn-default btn-secondary')

            if size == 'b':
                button.add_class('btn-block')
            else:
                button.add_class('btn-sm')
            button.add_style("top: 0px")


        button.add_attr('spt_text_label', title)
        td.add_class("spt_action_button_hit")
        button.add_class("hand")

        return super(ActionButtonWdgOld,self).get_display()








class IconButtonWdg(DivWdg):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(IconButtonWdg, self).__init__()
        self.base = "%s/%s" % (BASE, self.get_theme() )
        self.height = 20
        self.width = 28



    def init(self):

        self.show_arrow_menu = self.kwargs.get("show_arrow") or False

        # DEPRECATED when switching to BMD class.
        """
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
                bvr_wdg = self


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
        """




    def get_out_img(self):
        return None

    def get_over_img(self):
        return "<img src='%s/icon_button_over_bg.png'/>" % self.base

    def get_click_img(self):
        return "<img src='%s/icon_button_click_bg.png'/>" % self.base
        
    def get_offset(self):
        return (2, 0)


    def get_height(self):
        return self.height

    def get_width(self):
        return self.width


    def get_display(self):
        self.add_style("position: relative")
        self.add_class("spt_button_top")
        #self.add_style("height: %spx" % self.get_height() )
        #self.add_style("width: %spx" % self.get_width() )

        display = DivWdg()
        self.add(display)
        display.add_class("spt_icon_button_top")


        """
        offset = self.get_offset()

        out_div = DivWdg()
        #display.add(out_div)
        out_div.add_class("spt_button_out")
        out_img = self.get_out_img()
        out_div.add_style("left: %spx" % offset[0])
        out_div.add_style("top: %spx" % offset[1])
        if out_img:
            out_div.add(out_img)
        out_div.add_style("position: absolute")


        over_div = DivWdg()
        #display.add(over_div)
        over_div.add_class("spt_button_over")
        over_img = self.get_over_img()
        over_div.add_style("left: %spx" % offset[0])
        over_div.add_style("top: %spx" % offset[1])
        over_div.add(over_img)
        over_div.add_style("position: absolute")
        over_div.add_style("display: none")


        click_div = DivWdg()
        #display.add(click_div)
        click_div.add_class("spt_button_click")
        click_img = self.get_click_img()
        click_div.add_style("left: %spx" % offset[0])
        click_div.add_style("top: %spx" % offset[1])
        click_div.add(click_img)
        click_div.add_style("position: absolute")
        click_div.add_style("display: none")

        """



        icon_str = self.kwargs.get("icon")
        title = self.kwargs.get("title")
        tip = self.kwargs.get("tip")
        if not tip:
            tip = title

        icon_div = DivWdg()
        display.add_class("btn bmd-btn-icon")
        icon_div.add_style("top: 8px")
        icon_div.add_style("left: 8px")
        display.add(icon_div)
        icon_div.add_style("position: absolute")
        if self.get_width() < 30:
            width = 16
        else:
            width = None

        if self.kwargs.get("size"):
            width = self.kwargs.get("size")

        icon = IconWdg(title, icon_str, size=width)
        icon_div.add(icon)

        if tip:
            display.add_attr("title", tip)


        if self.show_arrow_menu:
            arrow_div = DivWdg()
            icon_div.add(arrow_div)
            arrow_div.add_style("position: absolute")
            arrow_div.add_style("top: 2px")
            arrow_div.add_style("left: 14px")

            arrow = IconWdg(title, "FA_CARET_DOWN")
            arrow_div.add(arrow)



        #spacer = DivWdg()
        #display.add(spacer)
        #spacer.add("")


        return super(IconButtonWdg, self).get_display()



from tactic.ui.common import BaseTableElementWdg
class IconButtonElementWdg(BaseTableElementWdg):
    def get_display(self):
        return IconButtonWdg(**self.options)



class SingleButtonWdg(IconButtonWdg):

    pass

    """
    def get_out_img(self):
        if self.kwargs.get("show_out") in [False, "false"]:
            return None
        img = "<img src='%s/Opaque_MainButton_out.png'/>" % self.base
        return img

    def get_over_img(self):
        return "<img src='%s/Opaque_MainButton_over.png'/>" % self.base

    def get_click_img(self):
        return "<img src='%s/Opaque_MainButton_click.png'/>" % self.base

    def get_offset(self):
        return (-1, -9)

    def get_height(self):
        #return 30 
        return 20
    """




