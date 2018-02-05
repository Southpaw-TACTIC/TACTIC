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
__all__ = [ "ButtonForDropdownMenuWdg", "AttachContextMenuWdg" ]


from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ContextMenuWdg, DropdownMenuWdg, SubMenuWdg


class AttachContextMenuWdg(BaseRefreshWdg):

    def __init__(self, **kwargs):

        # get the them from cgi
        self.handle_args(kwargs)
        self.kwargs = kwargs
               
        # required args
        self.activator_wdg = kwargs['activator_wdg']
        self.menus = kwargs['menus']


    def get_args_keys(self):
        return {
            'activator_wdg': 'Pass in the html element based widget that will be assigned the behavior which ' \
                             'will launch the given context menu on right click. The menus are also added to ' \
                             'the activator_wdg',
            'menus': 'Array of "menu details" dictionaries of all needed menu information. Assumes the first one ' \
                     'in the array is the main context menu, with the rest being any needed sub-menus'
        }


    def handle_args(self, kwargs):
        # verify the args
        args_keys = self.get_args_keys()
        for key in kwargs.keys():
            if not args_keys.has_key(key):
                #raise WidgetException("Key [%s] not in accepted arguments" % key)
                pass

        web = WebContainer.get_web()
        args_keys = self.get_args_keys()
        for key in args_keys.keys():
            if not kwargs.has_key(key):
                value = web.get_form_value(key)
                kwargs[key] = value


    def get_display(self):
        hidden_div = DivWdg()
        hidden_div.add_class("SPT_MENU_ACTIVATOR_STUBS")
        hidden_div.add_style("display: none")  # be sure this display is 'none'!

        # Generate the main context menu ...
        ctx_map = self.menus[0]
        if not ctx_map.has_key('allow_icons'):
            ctx_map['allow_icons'] = True
        ctx_menu_wdg = ContextMenuWdg( activator_wdg=self.activator_wdg, menu_id=ctx_map['menu_id'],
                                       width=ctx_map['width'], opt_spec_list=ctx_map['opt_spec_list'],
                                       allow_icons=ctx_map['allow_icons'] )
        hidden_div.add( ctx_menu_wdg )

        # Generate any needed sub-menus for the context menu ...
        sm_map_list = self.menus[1:]
        for sm_map in sm_map_list:
            if not sm_map.has_key('allow_icons'):
                sm_map['allow_icons'] = True
            submenu_wdg = SubMenuWdg( menu_id=sm_map['menu_id'], width=sm_map['width'],
                                          opt_spec_list=sm_map['opt_spec_list'], allow_icons=sm_map['allow_icons'] )
            hidden_div.add( submenu_wdg )

        return hidden_div


    def attach_by_menu_id( activator_wdg, first_menu_id ):
        activator_wdg.add_event( "oncontextmenu",
                                 "return spt.ctx_menu.show_on_context_click_cbk(event,'%s');" % first_menu_id )
    attach_by_menu_id = staticmethod(attach_by_menu_id)



class ButtonForDropdownMenuWdg(BaseRefreshWdg):

    def __init__(self, **kwargs):

        # get the them from cgi
        self.handle_args(kwargs)
        self.kwargs = kwargs
               
        # required args
        self.title = kwargs['title']
        self.id    = kwargs['id']
        self.menus = kwargs['menus']
        self.width = kwargs['width']
        self.style = kwargs['style']

        self.match_width = False
        if kwargs.has_key('match_width'):
            self.match_width = kwargs['match_width']

        self.nudge_menu_horiz = 0;
        if kwargs.has_key('nudge_menu_horiz') and kwargs['nudge_menu_horiz']:
            self.nudge_menu_horiz = int( kwargs['nudge_menu_horiz'] )

        self.nudge_menu_vert = 0;
        if kwargs.has_key('nudge_menu_vert') and kwargs['nudge_menu_vert']:
            self.nudge_menu_vert = int( kwargs['nudge_menu_vert'] )

        # -- Here is an example of what the menus parameter should look like ...
        # -- (it'll be an array of "menu details" dictionaries as per the following)
        #
        #   [ { 'menu_id': 'MainMenu', 'width': 250, 'allow_icons': True,
        #       'opt_spec_list': [
        #           { "type": "title", "label": "A Nested Sub-menu" },
        #           { "type": "separator" },
        #           { "type": "action", "label": "Sub-menu 2 launch JS Logger",
        #                 "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },
        #           { "type": "action", "label": "Open Folder 2",
        #                 "bvr_cb": {'cbjs_action': "alert('Sub-menu 2 Open File clicked!');"}, "icon": IconWdg.LOAD },
        #           { "type": "action", "label": "Make Even More Awesome Popup ...",
        #                 "bvr_cb": {'cbjs_action': "alert('Popping up Much More Awesomeness!');"} }
        #       ]
        #   } ]


    def get_args_keys(self):
        return {
            'title': 'Text for Button Title',
            'id': 'The element ID for the drop down button',
            'menus': 'Array of "menu details" dictionaries of all needed menu information. Assumes the first one ' \
                     'in the array is the main drop down menu, with the rest being sub-menus',
            'style': 'A string specifying style overrides for the button itself',
            'width': 'Integer specification for the width of the drop down button in pixels',
            'match_width': 'Optional boolean, if True then drop down menu will share same width ' \
                           'as button width. However the submenus maintain their own specified width regardless.',
            'nudge_menu_horiz': 'Use this to fine tune horizontal placement of drop down menu with respect to button',
            'nudge_menu_vert': 'Use this to fine tune vertical placement of drop down menu with respect to button'
        }


    def handle_args(self, kwargs):
        # verify the args
        args_keys = self.get_args_keys()
        for key in kwargs.keys():
            if not args_keys.has_key(key):
                #raise WidgetException("Key [%s] not in accepted arguments" % key)
                pass

        web = WebContainer.get_web()
        args_keys = self.get_args_keys()
        for key in args_keys.keys():
            if not kwargs.has_key(key):
                value = web.get_form_value(key)
                kwargs[key] = value


    def get_display(self):

        dd_activator = DivWdg()
        dd_activator.set_id( self.id )

        if self.style:
            dd_activator.add_styles( self.style )

        dd_activator.add_style( "width: %spx" % self.width )
        dd_activator.add_class("SPT_DTS");

        if self.nudge_menu_horiz != 0:
            dd_activator.set_attr("spt_nudge_menu_horiz", self.nudge_menu_horiz)

        if self.nudge_menu_vert != 0:
            dd_activator.set_attr("spt_nudge_menu_vert", self.nudge_menu_vert)

        # Generate button ...
        #
        table = Table()
        table.add_row()
        table.add_styles("width: 100%; padding: 0px; margin: 0px;")
        td = table.add_cell()
        td.add_looks("menu border curs_default")
        td.add_styles( "padding: 0px; width: 100%; overflow: hidden; height: 12px; max-height: 12px;" )

        title_div = DivWdg()
        title_div.add_styles( "padding: 0px; margin-left: 4px; margin-top: 1px;" )
        title_div.add_looks("menu fnt_text")
        title_div.add(self.title)

        td.add( title_div )

        td = table.add_cell()
        # -- Example of setting only some of the borders with dotted style ...
        # td.add_looks( "menu_btn_icon clear_borders border_bottom border_right dotted" )
        td.add_looks( "menu_btn_icon border curs_default" )
        td.add_styles( "padding: 0px; text-align: center; overflow: hidden; " \
                       "width: 15px; min-width: 15px;" \
                       "height: 12px; max-height: 12px;" )

        arrow_img = HtmlElement.img("/context/icons/silk/_spt_bullet_arrow_down_dark_8x8.png")
        arrow_img.add_styles( "border: 0px; margin-left: 1px; margin-top: 0px;" )
        td.add( arrow_img )

        dd_activator.add(table)

        # Now generate the main drop down menu and any needed sub-menus ...
        #
        dd_map = self.menus[0]
        if not dd_map.has_key('allow_icons'):
            dd_map['allow_icons'] = True  # default is to allow icons
        if self.match_width:
            dd_map['width'] = self.width

        dd_menu_wdg = DropdownMenuWdg( activator_wdg=dd_activator, menu_id=dd_map['menu_id'],
                                       width=dd_map['width'], opt_spec_list=dd_map['opt_spec_list'],
                                       allow_icons=dd_map['allow_icons'] )
        dd_activator.add( dd_menu_wdg )

        sm_map_list = self.menus[1:]
        for sm_map in sm_map_list:
            if not sm_map.has_key('allow_icons'):
                sm_map['allow_icons'] = True
            submenu_wdg = SubMenuWdg( menu_id=sm_map['menu_id'], width=sm_map['width'],
                                          opt_spec_list=sm_map['opt_spec_list'], allow_icons=sm_map['allow_icons'] )
            dd_activator.add( submenu_wdg )

        return dd_activator


