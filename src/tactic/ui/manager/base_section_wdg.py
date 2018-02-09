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
__all__ = ["BaseSectionWdg"]

import os, types

from pyasm.common import Common, Environment, Container, Xml, XmlException
from pyasm.biz import Project
from pyasm.search import Search
from pyasm.web import WebContainer, DivWdg, SpanWdg, HtmlElement
from pyasm.widget import WidgetConfig, WidgetConfigView

from tactic.ui.container import RoundedCornerDivWdg, LabeledHidableWdg, PopupWdg
from tactic.ui.common import BaseRefreshWdg


class BaseSectionWdg(BaseRefreshWdg):
   
    ERR_MSG = 'SideBar_Error'


    def get_args_keys(cls):
        '''external settings which populate the widget'''
        return {
        'config_search_type': 'Search type parent of the view to be displayed',
        'view': 'Current View of the search type to be displayed',
        'title': 'The title that appears at the top of the section',
        'config': 'Explicit config xml',
        'width': 'The width of the sidebar',

        'prefix': 'A unique identifier for this widget',

        'recurse': 'Determines whether to recurse down sections',
        'mode': 'edit|view determines the mode of the widget',
        'default': "Determine whether to look just in default file",
        #'sortable' : "Determine whether it is sortable"
        }
    get_args_keys = classmethod(get_args_keys)



    def get_config(cls, config_search_type, view, default=False):
        # method to get the config view for this widget to display
        return WidgetConfigView.get_by_search_type(config_search_type, view)



    def get_display(self):
        self.config_search_type = self.kwargs.get("config_search_type")
        if not self.config_search_type:
            self.config_search_type = "SideBarWdg"

        title = self.kwargs.get('title')
        config = self.kwargs.get('config')
        view = self.kwargs.get('view')
        width = self.kwargs.get('width')
        #sortable = self.kwargs.get('sortable')
        if not width:
            width = "175"

        self.prefix = self.kwargs.get("prefix")
        if not self.prefix:
            self.prefix = "side_bar"

        self.mode = self.kwargs.get("mode")
        if not self.mode:
            self.mode = 'view'


        self.default = self.kwargs.get('default') == 'True'

        div = DivWdg()
        div.add_class("spt_section_top")
        div.set_attr("SPT_ACCEPT_DROP", "manageSideBar")


        # create the top widgets
        label = SpanWdg()
        label.add(title)
        label.add_style("font-size: 1.1em")
        section_div = LabeledHidableWdg(label=label)
        div.add(section_div)

        section_div.set_attr('spt_class_name', Common.get_full_class_name(self))
        for name, value in self.kwargs.items():
            if name == "config":
                continue
            section_div.set_attr("spt_%s" % name, value)

        bgcolor = label.get_color("background3")
        project_div = RoundedCornerDivWdg(hex_color_code=bgcolor,corner_size="10")
        project_div.set_dimensions( width_str='%spx' % width, content_height_str='100px' )
        content_div = project_div.get_content_wdg()

        #project_div = DivWdg()
        #content_div = project_div


        section_div.add( project_div )

        content_div.add_class("spt_side_bar_content")
        content_div.add_attr("spt_view", view)

        if type(view) in types.StringTypes:
            view = [view]

        view_margin_top = '4px'

        web = WebContainer.get_web()
        for viewx in view:
            config = self.get_config(self.config_search_type, viewx, default=self.default)
            if not config:
                continue

            # make up a title
            title = DivWdg()
            title.add_gradient( "background", "side_bar_title", 0, -15, default="background" )
            title.add_color( "color", "side_bar_title_color", default="color" )
            title.add_styles( "margin-top: %s; margin-bottom: 3px; vertical-align: middle" % view_margin_top )
            if not web.is_IE():
                title.add_styles( "margin-left: -5px; margin-right: -5px;")
            title.add_looks( "navmenu_header" )
            title.add_style( "height: 18px" )
            title.add_style( "padding-top: 2px" )
            """
            title = DivWdg()
            title.add_styles( "margin-top: %s; margin-bottom: 3px; vertical-align: middle" % view_margin_top )
            if not web.is_IE():
                title.add_styles( "margin-left: -10px; margin-right: -10px;")
            title.add_looks( "navmenu_header" )
            """

            # FIXME: not sure if this logic should be here. It basically
            # makes special titles for certain view names
            view_attrs = config.get_view_attributes()
            title_str = view_attrs.get("title")
            if not title_str:
                if viewx.startswith("self_view_"):
                    title_str = "My Views"
                else:
                    title_str = viewx

            title_str = Common.get_display_title(title_str)

            title_label = SpanWdg()
            title_label.add_styles( "margin-left: 6px; padding-bottom: 2px;" )
            title_label.add_looks( "fnt_title_5 fnt_bold" )
            title_label.add( title_str )
            title.add( title_label )

            content_div.add( title )

            info = { 'counter' : 10, 'view': viewx }
            self.generate_section( config, content_div, info )
            error_list = Container.get_seq(self.ERR_MSG)
            if error_list: 
                span = SpanWdg()
                span.add_style('background', 'red')
                span.add('<br/>'.join(error_list))
                content_div.add(span)
                Container.clear_seq(self.ERR_MSG)
            self.add_dummy(config, content_div) 

        return div


  
    def _get_title(self, config, element_name):
        attributes = config.get_element_attributes(element_name)
        title = attributes.get("title")
        if not title:
            title = Common.get_display_title(element_name)

            if '.' in title:
                parts  = title.split('.', 1)
                title = parts[1]

        if not title or title == ' ':
            title = "(%s)" % element_name

        return title



    def add_dummy(self, config, subsection_div):
        div = DivWdg()
        div.add_attr("spt_view", config.get_view() )
        div.add_class("spt_side_bar_element")
        div.add_class("spt_side_bar_dummy")
        div.add( self.get_drop_wdg() )
        subsection_div.add(div)



    def generate_section( self, config, subsection_div, info, base_path="" ):

        title = self.kwargs.get('title')
        view = self.kwargs.get('view')

        base_path_flag = True
        if not base_path:
            base_path = "/%s" % info.get('view').capitalize()
            base_path_flag = False
        current_path = base_path

        # add in the elements
        if config.get_view() == "definition":
            element_names = config.get_element_names()
            sort = False
            # not sorting for now
            if sort == True:
                element_names.sort()
        else:
            element_names = config.get_element_names()

        
        # if there are no elements, then just add a drop widget
        if not element_names:
            if self.mode == 'view':
                item_div = DivWdg()
                item_div.add_style("margin: 3px")
                item_div.add_style("color: #555")
                item_div.add("<i>-- No items --</i>")
                subsection_div.add(item_div)
            else:
                self.add_dummy(config, subsection_div)
            return

        for element_name in element_names:
            display_class = config.get_display_handler(element_name)

            if display_class == "SeparatorWdg":
                div = DivWdg()
                div.add_attr("spt_view", config.get_view() )
                div.add_class("spt_side_bar_element")
                div.add_class("spt_side_bar_separator")
                div.add_attr("spt_element_name", element_name)

                hr =  HtmlElement.hr()
                hr.add_style("size: 1px")
                div.add(hr)
                div.add_style("height", "5")
                subsection_div.add(div)

                options = config.get_display_options(element_name)
                self.add_separator_behavior(div, element_name, config, options)

                continue

            elif display_class in ["SideBarSectionLinkWdg","FolderWdg"]:

                security = Environment.get_security()
                default_access = "view"
                if not security.check_access("side_bar", element_name, "view", default=default_access):
                    continue

                title = self._get_title(config, element_name)
                

                paths = []
                if current_path in paths:
                    is_open = True
                else:
                    is_open = False


                options = config.get_display_options(element_name)
                config_view = config.get_view()

                current_path = "%s/%s" % (base_path, element_name)
                
                # create HTML elements for Section Link ...
                outer_div = DivWdg()
                outer_div.add_attr("spt_view", config_view )
                outer_div.add_class("spt_side_bar_element")
                outer_div.add_class("spt_side_bar_section")
                outer_div.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
                outer_div.add_attr("spt_element_name", element_name)
                outer_div.add_attr("spt_title", title)
                
                #if info.get('login') : 
                #    outer_div.add_attr("spt_login", info.get('login')) 

                # add an invisible drop widget
                outer_div.add(self.get_drop_wdg())


                # Create the link
                s_link_div = DivWdg()
                s_link_div.add_class("SPT_DTS")
                s_link_div.add_class("spt_side_bar_section_link")

                s_link_div.add_style("cursor: pointer")
                s_link_div.add_style( "padding-top: 4px" )

                s_link_div.add_looks("navmenu_section fnt_text fnt_bold")

                # FIXME: currently 'is_open' is hardcoded to be False (see above) ... the state of open or close
                #        of sections is currently stored in a cookie on the client machine. So, at some point if
                #        we decide to store the open/close state of side bar sections then we need to fix this.
                #        here ...
                #
                if is_open:
                    s_link_div.add( "<img src='/context/icons/silk/_spt_bullet_arrow_down_dark.png' " \
                            "style='float: top left; margin-left: -5px; margin-top: -4px;' />" \
                            "<span style=''>%s</span>" % title )
                else:
                    s_link_div.add( "<img src='/context/icons/silk/_spt_bullet_arrow_right_dark.png' " \
                            "style='float: top left; margin-left: -5px; margin-top: -4px;' />" \
                            "<span style=''>%s</span>" % title )

                # create the content of the link div
                s_content_div = DivWdg()
                info['counter'] = info['counter'] + 1
                s_content_div.add_class("SPT_DTS")

                s_content_div.add_attr("spt_path", current_path)
                
                s_content_div.add_class("spt_side_bar_section_content")

                s_content_div.add_style( "padding-left: 11px" )

                if is_open:
                    s_content_div.add_style( "display: block" )
                else:
                    s_content_div.add_style( "display: none" )


                # add the behaviors
                self.add_folder_behavior(s_link_div, element_name, config, options)

                # then get view name from options in order to read a new
                # config and recurse ...
                options_view_name = options.get('view')
                if options_view_name:
                    sub_config = self.get_config( self.config_search_type, options_view_name, default=self.default)
                    self.generate_section( sub_config, s_content_div, info, current_path )

                outer_div.add(s_link_div)
                outer_div.add(s_content_div)
                subsection_div.add( outer_div )

            else:
                # FIXME: specify LinkWdg, it's too loosely defined now
                options = config.get_display_options(element_name)
                options['path'] = '%s/%s' % (current_path, element_name)

                # put in a default class name
                if not options.get('class_name'):
                    options['class_name'] = "tactic.ui.panel.ViewPanelWdg"
                    #FIXME: this cause an error in xmlrpc
                    #options['haha'] = False
                link_wdg = self.get_link_wdg(element_name, config, options)

                if link_wdg:
                    self.add_link_behavior(link_wdg, element_name, config, options)
                    subsection_div.add(link_wdg)

        # ------------------------------------------
        # end of 'for element_name in element_names'
        # ------------------------------------------

        # @@@
        # if base_path_flag:
        #     subsection_div.add( "<div style='height: 8px;'><HR/></div>" )






    def get_drop_wdg(self):
        if self.mode == 'view':
            return SpanWdg()
        hr = DivWdg()
        hr.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        hr.add_style("height: 5px")
        hr.add_style("width: 150px")
        #hr.add_style("border: solid 1px black")
        hr.add_style("position: absolute")
        hr.add_event("onmouseover", "this.getChildren()[0].style.display=''")
        hr.add_event("onmouseout", "this.getChildren()[0].style.display='none'")
        hr.add("<hr style='margin-top: 2px; size: 1px; color: #222; display: none'/>")
        return hr

    def get_link_wdg(self, element_name, config, options):
        attributes = config.get_element_attributes(element_name)
        title = self._get_title(config, element_name)

        default_access = "view"
        path = options.get('path')
        security = Environment.get_security()
        if not security.check_access("side_bar", element_name, "view", default=default_access):
            return

        # backwards compatibility??
        #if not security.check_access("url", path, "view"):
        #    return


        link_wdg = DivWdg(css="hand")
        link_wdg.add_style( "padding-top: 4px" )

        link_wdg.add_attr("spt_title", title)
        link_wdg.add_attr("spt_icon", attributes.get("icon"))
        link_wdg.add_class("spt_side_bar_link")
        link_wdg.add_attr("spt_view", config.get_view() )
        link_wdg.add_attr("spt_element_name", element_name)
        link_wdg.add_attr("spt_path", options['path'])
       

        # add the mouseover color change
        link_wdg.add_style("color: #292929")
        link_wdg.add_class("SPT_DTS")
        hover = link_wdg.get_color("background3", -10)
        link_wdg.add_event("onmouseover", "this.style.background='%s'" % hover)
        link_wdg.add_event("onmouseout", "this.style.background=''")
        link_wdg.add_class("spt_side_bar_element")

        link_wdg.add_looks("fnt_text")

        link_wdg.add_attr("spt_view", config.get_view() )



        # add an invisible drop widget
        drop_wdg = self.get_drop_wdg()
        drop_wdg.add_style("margin-top: -3px")
        link_wdg.add(drop_wdg)

        span = SpanWdg()
        span.add_class("spt_side_bar_title")

        # add an icon
        icon = attributes.get("icon")
        if icon:
            icon = icon.upper()
            from pyasm.widget import IconWdg
            try:
                span.add( IconWdg(title, eval("IconWdg.%s" % icon) ) )
            except:
                pass


        span.add(title)
        link_wdg.add(span)


        return link_wdg



    #
    # behavior functions
    #
    def add_separator_behavior(self, separator_wdg, element_name, config, options):
        pass

    def add_folder_behavior(self, folder_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a folder'''
        pass


    def add_link_behavior(self, link_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a link'''
        pass







__all__.append("SideBarSectionWdg")
class SideBarSectionWdg(BaseSectionWdg):

    def get_config(cls, config_search_type, view, default=False):

        config = None
        configs = []
        login = None
        defined_view = view

        # this is really for the predefined view that shouldn't go to the db
        # otherwise, it is a never ending cycle.
        if default:
            views = [defined_view, 'definition']
            cls.add_internal_config(configs, views)
            
        # special condition for children
        elif view in ['children']:
            tmp_path = __file__
            dir_name = os.path.dirname(tmp_path)
            file_path="%s/../config/children-conf.xml" % (dir_name)
            config = WidgetConfig.get(file_path=file_path, view=defined_view)
            configs.append(config)

          
        elif view == "definition":
            # look for a definition in the database
            search = Search("config/widget_config")
            search.add_filter("search_type", config_search_type)
            search.add_filter("view", "definition")
            # lower the chance of getting some other definition files
            search.add_filter("login", None)
            config = search.get_sobject()
            if config:
                configs.append(config)
            # We should not allow redefinition of a predefined item
            # so it is fine to add internal config for definition
            # then look for a definition in the definition file
            cls.add_internal_config(configs, ['definition'])
        
       

        else:
            # first look in the database
            search = Search("config/widget_config")
            search.add_filter("search_type", config_search_type)
            search.add_filter("view", view)
            #search.add_filter("login", login)
            
            config = search.get_sobject()
            if config:
                configs.append(config)
            # then look for a file
            cls.add_internal_config(configs, [defined_view])
            
            # look for a definition in the database
            search = Search("config/widget_config")
            search.add_filter("search_type", config_search_type)
            search.add_filter("view", "definition")
            # lower the chance of getting some other definition files
            search.add_filter("login", None)
            config = search.get_sobject()
            if config:
                configs.append(config)


            # then look for a definition in the definition file
            cls.add_internal_config(configs, ['definition'])


        widget_config_view = WidgetConfigView(config_search_type, view, configs)
        return widget_config_view

    get_config = classmethod(get_config)



    def add_internal_config(cls, configs, views):
        '''add an internal config based on project base type'''
        project = Project.get()
        project_type = project.get_base_type()
        # catch potential invalid xpath error
        try:
            if project_type:
                tmp_path = __file__
                dir_name = os.path.dirname(tmp_path)
                file_path="%s/../config/%s-conf.xml" % (dir_name, project_type)
                if os.path.exists(file_path):
                    for view in views:
                        config = WidgetConfig.get(file_path=file_path, view=view)
                        if config.get_view_node():
                            configs.append(config)

            # finally, just look at the DEFAULT config
            tmp_path = __file__
            dir_name = os.path.dirname(tmp_path)
            file_path="%s/../config/%s-conf.xml" % (dir_name, "DEFAULT")
                
            if os.path.exists(file_path):
                for view in views:
                    config = WidgetConfig.get(file_path=file_path, view=view)
                    if config.get_view_node():
                        configs.append(config)

        except XmlException, e:
            msg = "Error with view [%s]"% ' '.join(views)
            error_list = Container.get_seq(cls.ERR_MSG)
            if msg not in error_list:
                Container.append_seq(cls.ERR_MSG, msg)
                print(e.__str__())


    add_internal_config = classmethod(add_internal_config)



    def add_separator_behavior(self, separator_wdg, element_name, config, options):
        pass

    def add_folder_behavior(self, folder_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a folder'''

        # determines whether the folder opens on click
        behavior = {
            'type':         'click_up',
            'cbfn_action':  'spt.side_bar.toggle_section_display_cbk',
        }
        folder_wdg.add_behavior( behavior )


    def add_link_behavior(self, link_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a link'''


        # if a parent key filter is specified, use it
        parent_key = self.kwargs.get("parent_key")
        if parent_key:
            options['parent_key'] = parent_key

        state = self.kwargs.get("state")
        if state:
            options['state'] = state


        options['element_name'] = element_name

        # send the title through
        title = self._get_title(config, element_name)

        header_title = options.get('header_title')
        if not header_title:
            header_title = title

        

        # FIXME: this is hard coded.  Not sure if it is used
        target_id = "main_body"


        values = config.get_web_options(element_name)
        behavior = {
            'type':         'click_up',
            'cbfn_action':  'spt.side_bar.display_link_cbk',
            'target_id':    target_id,
            'title':        header_title,
            'options':      options,
            'values':       values
        }
        link_wdg.add_behavior( behavior )

        options2 = options.copy()
        #if options2.get('class_name') == "tactic.ui.app.SearchTypeCreatorWdg":
        options2['inline_search'] = "true"


        behavior = {
            'type':         'click_up',
            'modkeys':      'SHIFT',
            'cbfn_action':  'spt.side_bar.display_link_cbk',
            'target_id':    element_name,
            'is_popup':     'true',
            'title':        title,
            'options':      options2,
            'values':       values
        }
        link_wdg.add_behavior( behavior )





