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


__all__ = ['ButtonElementWdg']

from pyasm.common import TacticException
from pyasm.search import Search, SearchType, SearchKey
from pyasm.web import DivWdg
from pyasm.widget import IconWdg, IconButtonWdg, SelectWdg, TextWdg
from pyasm.biz import ExpressionParser

from tactic.ui.common import BaseTableElementWdg


class ButtonElementWdg(BaseTableElementWdg):


    ARGS_KEYS = {

    'script_path': {
        'description': '''Points to the script path that is executed when the button is clicked''',
        'type': 'TextWdg',
        'category': 'Options',
        'order': 0
    },

    'javascript': {
        'description': 'javascript script to run when button is clicked',
        'type': 'TextAreaWdg',
        'category': 'Options',
        'order': 1,
    },
 
   'icon': {
        'description': 'The icon to display for the button',
        'type': 'IconSelectWdg',
        'category': "Options",
        'order': 2
    },

    'hint': {
        'description': 'Text to display as a tool-tip when mouse is hovering over button',
        'category': "Options",
        'order': 3
    },
    'expression': {
        'description': 'Text do display beside the icon',
        'category': "Options",
        'order': 4
    },






    'script_code': {
        'description': '''Points to the script code that is executed when the button is clicked (Deprecated)''',
        'category': 'deprecated'
    },
    'path': {
        'description': 'Points to the folder/script_name (script_path) of the config/custom_script to be executed when the button is clicked',
        'category': 'deprecated'
    },

    'enable': 'Expression to determine whether the button is enabled or not',

    'icon_tip': {
        'description': 'Text to display as a tool-tip when mouse is hovering over icon',
        'category': "deprecated"
    },



    'cbjs_action': {
        'description': 'Inline script',
        'type': 'TextAreaWdg',
        'order': 0,
        'category': 'deprecated'
    },


    }


    def is_editable(self):
        return False

    def is_sortable(self):
        return False

    def get_width(self):
        return 30

    def init(self):
        self.behavior = {}

        self.script = None
        self.script_obj = None
        super(ButtonElementWdg,self).init()


    def get_input_by_arg_key(self, key):
        if key == 'icon':
            input = SelectWdg("option_icon_select")
            input.set_option("values", IconWdg.get_icons_keys())
            input.add_empty_option("-- Select --")
        elif key == 'script':
            input = SelectWdg("option_script_select")
            input.set_option("query", "config/custom_script|code|code" )
            input.add_empty_option("-- Select --")
        else:
            input = TextWdg("value")
        return input
    get_input_by_arg_key = classmethod(get_input_by_arg_key)



    def handle_layout_behaviors(self, layout):

        # Basic button behaviors
        layout.add_relay_behavior( {
        'type': 'mouseover',
        'bvr_match_class': 'spt_button_hit_wdg',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_button_top")
            var over = top.getElement(".spt_button_over");
            var click = top.getElement(".spt_button_click");
            click.setStyle("display", "none");
        '''
        } )

        layout.add_relay_behavior( {
        'type': 'mouseout',
        'bvr_match_class': 'spt_button_hit_wdg',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_button_top")
            var over = top.getElement(".spt_button_over");
            var click = top.getElement(".spt_button_click");
            click.setStyle("display", "none");
        '''
        } )

        layout.add_relay_behavior( {
        'type': 'mousedown',
        'bvr_match_class': 'spt_button_hit_wdg',
        'cbjs_action': '''
            var top = src_el.getParent(".spt_button_top")
            var over = top.getElement(".spt_button_over");
            var click = top.getElement(".spt_button_click");
            click.setStyle("display", "");
        '''
        } )
        layout.add_relay_behavior( {
        'type': 'mouseup',
        'bvr_match_class': 'spt_button_hit_wdg',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_button_top")
            var over = top.getElement(".spt_button_over");
            var click = top.getElement(".spt_button_click");
            click.setStyle("display", "none");
        '''
        } )


        # handle custom behavior for button

        script_code = self.get_option("script_code")
        # deprecated
        if not script_code:
            script_code = self.get_option("script")


        path = self.get_option("path")
        if not path:
            path = self.get_option("script_path")


        inline = self.get_option("cbjs_action")
        if not inline:
            inline = self.get_option("javascript")


        if script_code:
            search = Search("config/custom_script")
            search.add_filter("code", script_code)
            self.script_obj = search.get_sobject()
        elif path:
            parts = path.split("/")
            folder = "/".join( parts[:-1])
            title = parts[-1]
            search = Search("config/custom_script")
            search.add_filter("folder", folder)
            search.add_filter("title", title)
            self.script_obj = search.get_sobject()
        elif inline:
            self.script = inline



        # NOTE: self.behavior can contain a lot of goodies which are
        # ignored here. ie: CheckinButtonElementWdg

        if self.behavior.get('cbjs_action'):
            self.script = self.behavior.get('cbjs_action')

        #behavior = {}
        behavior = self.behavior
        behavior['type'] = 'mouseup'
        #self.behavior['search_key'] = search_key
        behavior['bvr_match_class'] = "spt_button_%s" % self.name

        if self.script:
            behavior['cbjs_action'] = '''
                var layout = bvr.src_el.getParent(".spt_layout");
                var sk;
                if (layout.getAttribute("spt_version") == "2") {
                    var row = bvr.src_el.getParent('.spt_table_row');
                    sk = row.getAttribute('spt_search_key');
                }
                else {
                    var td = bvr.src_el.getParent('td');
                    sk = td.getAttribute('search_key');
                }
                bvr.search_key = sk;
                %s'''% self.script
        elif self.script_obj:
            behavior['cbjs_action'] = '''
                var layout = bvr.src_el.getParent(".spt_layout");
                var sk;
                if (layout.getAttribute("spt_version") == "2") {
                    var row = bvr.src_el.getParent('.spt_table_row');
                    sk = row.getAttribute('spt_search_key');
                }
                else {
                    var td = bvr.src_el.getParent('td');
                    sk = td.getAttribute('search_key');
                }
                bvr.search_key = sk;
                spt.CustomProject.custom_script(evt,bvr);
                '''
            script_code = self.script_obj.get_code()
            behavior['script_code'] = script_code
        else:
            behavior['cbjs_action'] = '''spt.alert("No script defined for this button");'''

        layout.add_relay_behavior(behavior)



    def handle_td(self, td):
        sobject = self.get_current_sobject()
        search_key = SearchKey.build_by_sobject(sobject)
        td.set_attr('search_key', search_key)



    def preprocess(self):

        # need to be able to set these globally
        layout = self.get_layout_wdg()
        if layout:
            layout.get_table()
        return

        layout.set_unique_id()
        layout.add_smart_style("spt_button_over", "position", "absolute")
        layout.add_smart_style("spt_button_over", "top", "-18px")
        layout.add_smart_style("spt_button_over", "left", "0px")
        layout.add_smart_style("spt_button_over", "height", "36px")
        layout.add_smart_style("spt_button_over", "width", "26px")
        #layout.add_smart_style("spt_button_over", "display", "none")

        #layout.add_smart_style("spt_button_click", "position", "absolute")
        layout.add_smart_style("spt_button_click", "margin-top", "-9px")
        layout.add_smart_style("spt_button_click", "height", "36px")
        layout.add_smart_style("spt_button_click", "width", "26px")
        #layout.add_smart_style("spt_button_click", "display", "none")

        BASE = '/context/themes2/default/'
        layout.add_smart_style( "spt_button_over", "background-image", "url(%s/MainButton_over.png)" % BASE)
        layout.add_smart_style( "spt_button_click", "background-image", "url(%s/MainButton_click.png)" % BASE)


    def add_to_button_behavior(self, name, value):
        self.behavior[name] = value




    def get_display(self):
        sobject = self.get_current_sobject()
        search_key = SearchKey.build_by_sobject(sobject)

        display = DivWdg()
        display.add_style("position: relative")
        display.add_class("spt_button_top")
        display.add_style("width: 26px")
        display.add_style("margin-left: auto")
        display.add_style("margin-right: auto")


        BASE = '/context/themes2/default/'
        over_div = DivWdg()
        display.add(over_div)
        over_div.add_class("spt_button_over")
        over_img = "<img src='%s/MainButton_over.png'/>" % BASE
        over_div.add(over_img)
        over_div.add_style("position: absolute")
        over_div.add_style("top: -9px")
        over_div.add_style("left: 0px")
        over_div.add_style("display: none")

        click_div = DivWdg()
        display.add(click_div)
        click_div.add_class("spt_button_click")
        click_img = "<img src='%s/MainButton_click.png'/>" % BASE
        click_div.add(click_img)
        click_div.add_style("position: absolute")
        click_div.add_style("top: -9px")
        click_div.add_style("left: 0px")
        click_div.add_style("display: none")





        if self.get_option('align') =='left':
            display.add_style("text-align: left")
        else:
            display.add_style("text-align: center")

        icon = self.get_option("icon")
        if not icon:
            icon = "create"


        icon_tip = self.get_option("icon_tip")
        if not icon_tip:
            icon_tip = self.get_option("hint")
        if not icon_tip:
            icon_tip = ""

        enable = self.get_option("enable")
        if enable:
            result = ExpressionParser().eval(enable, sobject)
            if not result:
                return "&nbsp;"


        if not self.script_obj and not self.script:
            icon_wdg = IconButtonWdg("No Script Found", IconWdg.ERROR)
        else:
            icon_link = icon.upper()

            icon_wdg = IconButtonWdg(icon_tip, icon=icon_link)
            if not sobject.is_insert():
                icon_wdg.add_class("hand")
                #icon_wdg.add_behavior(self.behavior)
                icon_wdg.add_class("spt_button_%s" % self.name)


        icon_div = DivWdg()
        icon_div.add(icon_wdg)
        icon_div.add_style("position: absolute")
        icon_div.add_style("top: 2px")
        icon_div.add_style("left: 5px")
        display.add(icon_div)

        hit_wdg = icon_div
        hit_wdg.add_class("spt_button_hit")

        if sobject.is_insert():
            hit_wdg.add_style("opacity: 0.4")
        else:
            hit_wdg.add_class("spt_button_hit_wdg")


        display.add_style("height: 18px")
        display.add_style("min-width: 21px")
        #display.add_style("overflow: hidden")
        display.add_style("margin-top: 0px")


        expression = self.kwargs.get('expression')
        if expression:
            value = Search.eval(expression, sobject, single=True)

            if value:

                badge = DivWdg()
                badge.add_style("position: absolute")

                badge.add_style("right: -30px")
                badge.add_style("top: -2px")
                badge.add_style("margin: 4px 3px 3px 6px")
                badge.add_style("opacity: 0.5")
                badge.add_style("font-size: 0.7em")
                badge.add_class("badge")
                badge.add(value)

                display.add(badge)
                display.add_style("position: relative")

                #return top


        return display



