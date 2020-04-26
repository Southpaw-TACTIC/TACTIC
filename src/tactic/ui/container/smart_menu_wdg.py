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
__all__ = ["SmartMenu"]

from pyasm.common import TacticException
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg

class SmartMenuWdg(BaseRefreshWdg):

    '''Container widget contains a menu.
    @usage
    '''

    def __init__(self, **kwargs):

        # get the them from cgi
        self.handle_args(kwargs)
        self.kwargs = kwargs

        # required args
        self.menu_tag_suffix = kwargs['menu_tag_suffix']
        self.width = kwargs['width']
        if not self.width or self.width < 250:
            self.width = 250


        self.opt_spec_list = kwargs['opt_spec_list']

        self.allow_icons = True
        if kwargs.has_key('allow_icons'):
            self.allow_icons = kwargs['allow_icons']
            if self.allow_icons in [ '', None ]:
                self.allow_icons = True

        self.setup_cbfn = kwargs.get('setup_cbfn')


    def get_args_keys(self):
        return {
            'menu_tag_suffix': 'This is one of "MAIN", "SUB_1", "SUB_2", etc. ... to distinguish between main ' \
                               'menu and submenus -- these only have to be unique within a sub-set of smart menus',
            'width': 'The total width (in pixels) for the menu',
            'opt_spec_list': 'Array of dictionaries, with each dict specifying each option on the menu',
            'allow_icons': 'This defaults to True; if False then the left column for icons is not generated',
            'setup_cbfn': 'Function name (no parentheses) for call-back that sets up information gathered ' \
                          'from inspection of the activator element'
        }


    def _add_spacer_row(self, menu_table, height, icon_width, icon_col_width, label_width):
        tbody = menu_table.add_tbody()
        tbody.add_style("display","table-row-group")
        tr = menu_table.add_row()
        #tr.add_looks( "smenu" )

        if self.allow_icons:
            td = menu_table.add_cell()
            td.add_styles("text-align: center; vertical-align: middle; height: %spx; width: %spx;" %
                            (height, icon_col_width) )
            #td.add_looks("smenu_icon_column")
            td.add_color("background", "background3")

        # label
        td = menu_table.add_cell()
        td.add_style("width", ("%spx" % label_width))
        td.add_style("height", ("%spx" % height))

        # Submenu arrow icon cell ...
        td = menu_table.add_cell()
        td.add_style("width", ("%spx" % icon_width))


    def get_display(self):

        smenu_div = DivWdg()
        smenu_div.add_class( "SPT_SMENU" )
        smenu_div.add_class( "SPT_SMENU_%s" % self.menu_tag_suffix )
        smenu_div.set_box_shadow()
        smenu_div.add_border()
        smenu_div.add_color("background", "background")
        smenu_div.add_color("color", "color")


        smenu_div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            spt.dom.load_js( ["ctx_menu.js"], function() {
                    spt.dom.load_js( ["smart_menu.js"], function() {
                } )
            } );
            '''
        } )

        if self.setup_cbfn:
            smenu_div.set_attr( "SPT_SMENU_SETUP_CBFN", self.setup_cbfn )

        smenu_div.set_z_start( 300 )
        #smenu_div.add_looks( "smenu border curs_default" )
        # smenu_div.add_styles( "padding-top: 3px; padding-bottom: 5px;" )

        m_width = self.width - 2
        smenu_div.add_style( ("width: %spx" % m_width) )

        smenu_div.add_style("overflow-x: hidden")

        icon_width = 16
        icon_col_width = 0
        if self.allow_icons:
            icon_col_width = icon_width + 2
        label_width = m_width - icon_col_width - icon_width

        menu_table = Table()
        menu_table.add_styles( "text-align: left; text-indent: 3px; border-collapse: collapse;" )
        #menu_table.add_color("background", "background")
        menu_table.add_color("color", "color")

        options = self.opt_spec_list
        opt_count = 0

        if options and options[0].get('type') != 'title':
            self._add_spacer_row(menu_table, 3, icon_width, icon_col_width, label_width)



        for opt in options:

            # if entry is a title, then add a spacer before
            if opt.get('type') == 'title' and opt_count:
                self._add_spacer_row(menu_table, 6, icon_width, icon_col_width, label_width)

            tbody = menu_table.add_tbody()
            tbody.add_style("display","table-row-group")

            tr = menu_table.add_row()
            #tr.add_looks( "smenu" )

            tr.add_class( "SPT_SMENU_ENTRY" )
            tr.add_class( "SPT_SMENU_ENTRY_%s" % opt['type'].upper() )

            if opt.has_key('enabled_check_setup_key'):
                tr.set_attr( "SPT_ENABLED_CHECK_SETUP_KEY", opt.get('enabled_check_setup_key') )

            if opt.has_key('hide_when_disabled') and opt.get('hide_when_disabled'):
                tr.set_attr( "SPT_HIDE_WHEN_DISABLED", "true" )

            if opt['type'] in [ 'action', 'toggle' ]:

                hover_bvr = {'type':'hover', 'add_looks': 'smenu_hilite',
                             'cbjs_action_over': 'spt.smenu.entry_over( evt, bvr );',
                             'cbjs_action_out': 'spt.smenu.entry_out( evt, bvr );' }
                if opt.has_key('hover_bvr_cb'):
                    hover_bvr.update( opt.get('hover_bvr_cb') )
                tr.add_behavior( hover_bvr )
                tr.add_class("hand")

            if opt['type'] == 'action':
                if opt.has_key('bvr_cb') and type(opt['bvr_cb']) == dict:
                    bvr = {}
                    bvr.update( opt['bvr_cb'] )
                    bvr['cbjs_action_for_menu_item'] = bvr['cbjs_action']
                    bvr['cbjs_action'] = 'spt.smenu.cbjs_action_wrapper( evt, bvr );'
                    bvr.update( { 'type': 'click_up' } )
                    tr.add_behavior( bvr )

            if opt['type'] == 'submenu':
                hover_bvr = { 'type': 'hover', 'add_looks': 'smenu_hilite',
                              'cbjs_action_over': 'spt.smenu.submenu_entry_over( evt, bvr );',
                              'cbjs_action_out': 'spt.smenu.submenu_entry_out( evt, bvr );',
                              'submenu_tag': "SPT_SMENU_%s" % opt['submenu_tag_suffix'],
                            }
                if opt.has_key('hover_bvr_cb'):
                    hover_bvr.update( opt.get('hover_bvr_cb') )
                tr.add_behavior( hover_bvr )
                # now trap click on submenu, so that it doesn't make the current menu disappear ...
                tr.add_behavior( { 'type': 'click', 'cbjs_action': ';', 'activator_type': 'smart_menu' } )

            tr.add_looks( "curs_default" )

            # Left icon cell ...
            if self.allow_icons:
                td = menu_table.add_cell()
                td.add_styles("text-align: center; vertical-align: middle; width: %spx;" % icon_col_width)
                #td.add_looks("smenu_icon_column")
                td.add_color("color", "color3")
                td.add_color("background", "background3")

                if opt.has_key( 'icon' ):
                    icon_wdg = IconWdg("", opt['icon'])
                    icon_wdg.add_class("SPT_ENABLED_ICON_LOOK")
                    td.add( icon_wdg )
                    #   if disabled:
                    #       icon_wdg.add_style( "opacity: .4" )
                    #       icon_wdg.add_style( "filter: alpha(opacity=40)" )

            # Menu option label cell ...
            td = menu_table.add_cell()
            td.add_style("width", ("%spx" % label_width))
            td.add_style("height", ("%spx" % icon_col_width))
            #if opt.get('type') != 'title':
            #    td.add_style( "padding-left: 6px" )
            #td.add_style( "padding-top: 2px" )
            td.add_style("padding: 6px 4px")

            if opt.has_key( 'label' ):
                label_str = opt.get('label').replace('"','&quot;')
                td.add_class("SPT_LABEL")
                td.add( label_str )
                td.set_attr( "SPT_ORIG_LABEL", label_str )
                #td.add_looks("fnt_text")
                td.add_style("font-size: 1.0em")
                if opt.get('type') == 'title':
                    #td.add_looks("smenu_title")
                    td.add_color("background", "background2")
                    td.add_color("color", "color2")
                    td.add_style("font-weight", "bold")
                    td.add_style("padding", "3px")
            elif opt.get('type') == 'separator':
                hr = HtmlElement("hr")
                hr.add_looks( "smenu_separator" )
                td.add( hr )

            td.add_class("SPT_ENABLED_LOOK")

            #   if disabled:
            #       td.add_style( "opacity: .2" )
            #       td.add_style( "filter: alpha(opacity=20)" )

            # Submenu arrow icon cell ...
            td = menu_table.add_cell()
            td.add_style("width", ("%spx" % icon_width))

            if opt['type'] == 'submenu':
                icon_wdg = IconWdg("", IconWdg.ARROWHEAD_DARK_RIGHT)
                td.add(icon_wdg)
                td.add_class("SPT_ENABLED_ICON_LOOK")

            # extend title entry styling into the submenu arrow cell and add some spacing after
            if opt.get('type') == 'title':
                #td.add_looks("smenu_title")
                td.add_color("background", "background2")
                td.add_color("color", "color2")
                td.add_style("font-weight", "bold")
                td.add_style("padding", "3px")
                self._add_spacer_row(menu_table, 3, icon_width, icon_col_width, label_width)

            #   if disabled:
            #       td.add_style( "opacity: .4" )
            #       td.add_style( "filter: alpha(opacity=40)" )

            opt_count += 1


        self._add_spacer_row(menu_table, 5, icon_width, icon_col_width, label_width)

        smenu_div.add( menu_table )
        smenu_div.add_style( "display: none" )
        smenu_div.add_style( "position: absolute" )
        return smenu_div



class SmartMenuSetWdg(BaseRefreshWdg):

    def __init__(self, **kwargs):

        self.match_subset = False

        # get the them from cgi
        self.handle_args(kwargs)
        self.kwargs = kwargs

        self.menu_specs_map = {}
        if kwargs.get('default_menu_specs'):
            self.menu_specs_map['SPT_SMENU_SUBSET__DEFAULT'] = kwargs.get('default_menu_specs')


    def get_args_keys(self):
        return {
            'default_menu_specs': 'List of menu specifcation maps for the default menu sub-set for the menu set.'
        }


    def add_subset_menu_specs(self, subset_tag_suffix, subset_menu_specs):
        self.menu_specs_map[ 'SPT_SMENU_SUBSET__%s' % subset_tag_suffix ] = subset_menu_specs
        self.match_subset = True


    def get_display(self):

        smenu_set_div = DivWdg()
        smenu_set_div.add_class("SPT_SMENU_SET")
        smenu_set_div.add_class("SPT_PUW")


        if self.match_subset:
            smenu_set_div.set_attr("SPT_SMENU_MATCH_SUBSET","true")

        # ??? div.set_attr("SPT_CONTEXT_CLASS_TAG", "spt_dg_row")

        # create default subset first ...
        subset_div = DivWdg()
        subset_div.add_class("SPT_SMENU_SUBSET SPT_SMENU_SUBSET__DEFAULT")

        # -- this needs to be added to activator element ...
        # subset_div.set_attr("SPT_SMENU_SUBSET_TAG", "SPT_SMENU_SUBSET__DEFAULT")

        menu_spec_list = self.menu_specs_map.get('SPT_SMENU_SUBSET__DEFAULT')
        if menu_spec_list:
            for menu_spec in menu_spec_list:
                smenu_wdg = SmartMenuWdg( menu_tag_suffix = menu_spec.get('menu_tag_suffix'),
                                          width = menu_spec.get('width'),
                                          opt_spec_list = menu_spec.get('opt_spec_list'),
                                          allow_icons = menu_spec.get('allow_icons'),
                                          setup_cbfn = menu_spec.get('setup_cbfn') )
                subset_div.add( smenu_wdg )

        smenu_set_div.add( subset_div )



        if self.match_subset:
        #{
            for subset_tag, menu_spec_list in self.menu_specs_map.iteritems():
                if subset_tag != 'SPT_SMENU_SUBSET__DEFAULT':
                    subset_div = DivWdg()
                    subset_div.add_class("SPT_SMENU_SUBSET %s" % subset_tag)
                    subset_div.set_attr("SPT_SMENU_SUBSET_TAG", subset_tag)

                    for menu_spec in menu_spec_list:
                        smenu_wdg = SmartMenuWdg( menu_tag_suffix = menu_spec.get('menu_tag_suffix'),
                                                  width = menu_spec.get('width'),
                                                  opt_spec_list = menu_spec.get('opt_spec_list'),
                                                  allow_icons = menu_spec.get('allow_icons'),
                                                  setup_cbfn = menu_spec.get('setup_cbfn') )
                        subset_div.add( smenu_wdg )

                    smenu_set_div.add( subset_div )
        #}



        return smenu_set_div


class SmartMenuButtonDropdownWdg(BaseRefreshWdg):

    def __init__(self, **kwargs):

        # get the them from cgi
        self.handle_args(kwargs)
        self.kwargs = kwargs
               
        # required args
        self.title = kwargs.get('title')
        self.icon_path = kwargs.get('icon_path')
        self.menus = kwargs.get('menus')
        self.width = kwargs.get('width')
        self.style = kwargs.get('style')

        self.match_width = False
        if kwargs.has_key('match_width'):
            self.match_width = kwargs.get('match_width')

        self.nudge_menu_horiz = 0;
        if kwargs.get('nudge_menu_horiz'):
            self.nudge_menu_horiz = int( kwargs.get('nudge_menu_horiz') )

        self.nudge_menu_vert = 0;
        if kwargs.get('nudge_menu_vert'):
            self.nudge_menu_vert = int( kwargs.get('nudge_menu_vert') )

    def get_args_keys(self):
        return {
            'title': 'Text for Button Title',
            'icon_path': 'path to icon image to use instead of text; the title in this case becomes the tool-tip. ' \
                         'This is ignored if it is an empty string.',
            'smart_menu_set': 'A SmartMenuSetWdg object, already created from menu information',
            'style': 'A string specifying style overrides for the button itself',
            'width': 'Integer specification for the width of the drop down button in pixels',
            'match_width': 'Optional boolean, if True then drop down menu will share same width ' \
                           'as button width. However the submenus maintain their own specified width regardless.',
            'nudge_menu_horiz': 'Use this to fine tune horizontal placement of drop down menu with respect to button',
            'nudge_menu_vert': 'Use this to fine tune vertical placement of drop down menu with respect to button'
        }


    def get_display(self):

        dd_activator = DivWdg()

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
        if self.icon_path:
            img = HtmlElement.img()
            img.set_attr("src", self.icon_path)
            img.set_attr("title", self.title)
            img.add_styles("padding: 0px; padding-bottom: 1px; margin: 0px; text-decoration: none;")
            title_div.add(img)
            title_div.add_looks("menu")
        else:
            title_div.add(self.title)
            title_div.add_looks("menu fnt_text")

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

        dd_activator.add( self.kwargs.get("smart_menu_set") )
        dd_activator.add_class("SPT_SMENU_ACTIVATOR")
        dd_activator.add_behavior( { 'type': 'click_up', 'activator_type' : 'smart_menu',
                                     'cbjs_action': 'spt.smenu.show_on_dropdown_click_cbk( evt, bvr )' } )

        return dd_activator



class SmartMenu(object):

    def add_smart_menu_set( html_wdg, menus_in ):
        from menu_wdg import Menu
        if type(menus_in) == list:
            # default_menu_specs
            smenu_set = SmartMenuSetWdg( default_menu_specs = menus_in )

            #smenu_set = SmartMenuSetWdg()
            #for menus_list in menus_in:
            #    if isinstance(menus_list, Menu):
            #        menus_list = [menus_list.get_data()]
            #    smenu_set.add_subset_menu_specs( ss_tag_suffix, menus_list )
 


        elif type(menus_in) == dict:
            smenu_set = SmartMenuSetWdg()
            for ss_tag_suffix, menus_list in menus_in.iteritems():
                if isinstance(menus_list, Menu):
                    menus_list = [menus_list.get_data()]
                    smenu_set.add_subset_menu_specs( ss_tag_suffix, menus_list )
                elif type(menus_list) == list:
                    new_menus_list = []
                    for x in menus_list:
                        if isinstance(x, Menu):
                            new_menus_list.append(x.get_data())
                        else:
                            new_menus_list.append(x)
                    smenu_set.add_subset_menu_specs( ss_tag_suffix, new_menus_list )
                else:
                    smenu_set.add_subset_menu_specs( ss_tag_suffix, menus_list )
        else:
            raise TacticException("SmartMenu.add_smart_menu_set() accepts only a list or dictionary as the " \
                                  "second parameter ('menus_in')")
        if html_wdg:
            html_wdg.add( smenu_set )
        return smenu_set
    add_smart_menu_set = staticmethod(add_smart_menu_set)


    # use after menus created and event activator is set ...
    def assign_as_local_activator( html_wdg, subset_tag_suffix=None, add_click_up=False ):
        html_wdg.add_class("SPT_SMENU_ACTIVATOR")
        if subset_tag_suffix:
            html_wdg.set_attr( "SPT_SMENU_SUBSET_TAG_SUFFIX", subset_tag_suffix )
        if add_click_up:
            html_wdg.add_behavior( { 'type': 'click_up', 'activator_type' : 'smart_menu',
                                     'cbjs_action': 'spt.smenu.show_on_dropdown_click_cbk( evt, bvr )' } )
    assign_as_local_activator = staticmethod(assign_as_local_activator)


    def attach_smart_context_menu( html_wdg, menus_in, is_local_activator=True, subset_tag_suffix=None ):
        #
        # menus_in can be a list (which will be DEFAULT subset)
        #    or a dictionary (containing multiple subsets)
        #
        smenu_set = SmartMenu.add_smart_menu_set( html_wdg, menus_in )
        if is_local_activator:
            SmartMenu.assign_as_local_activator( html_wdg, subset_tag_suffix )
        html_wdg.add_event( "oncontextmenu",
                                 "return spt.smenu.show_on_context_click_cbk(event);" )
        html_wdg.add_class( "SPT_SMENU_CONTAINER" )
    attach_smart_context_menu = staticmethod(attach_smart_context_menu)


    def get_smart_button_dropdown_wdg( title, menus_in, width=100, style='', icon_path='', match_width=False,
                                       nudge_horiz=0, nudge_vert=0 ):

        smenu_set = SmartMenu.add_smart_menu_set( None, menus_in )
        btn_dd_wdg = SmartMenuButtonDropdownWdg( title=title, smart_menu_set=smenu_set, style=style, width=width,
                                                 match_width=match_width, nudge_menu_horiz=nudge_horiz,
                                                 nudge_menu_vert=nudge_vert, icon_path=icon_path )
        return btn_dd_wdg
    get_smart_button_dropdown_wdg = staticmethod(get_smart_button_dropdown_wdg)



