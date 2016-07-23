###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["SimpleSideBarWdg"]

import os, types

from pyasm.common import Environment, Common, Container, Xml, XmlException
from pyasm.web import DivWdg, HtmlElement, WebContainer, SpanWdg
from pyasm.biz import Project, Schema
from pyasm.search import Search, WidgetDbConfig
from pyasm.widget import WidgetConfig, WidgetConfigView, IconWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu, Menu, MenuItem

from panel_wdg import SideBarPanelWdg, SideBarBookmarkMenuWdg
class SimpleSideBarWdg(SideBarPanelWdg):

    def get_views(my):
        views = [] 

        view = my.kwargs.get('view')
        if not view:
            view = "project_view"

        #view = "my_view_%s" % Environment.get_user_name()

        views.append(view)
        return view


    def get_subdisplay(my, views):
        div = DivWdg()
        div.set_attr('spt_class_name', Common.get_full_class_name(my))

        div.add( my.get_bookmark_menu_wdg("", None, views) )
        return div


    def get_bookmark_menu_wdg(my, title, config, view):

        use_href = my.kwargs.get("use_href")
        target = my.kwargs.get("target")
        link_mode = my.kwargs.get("link_mode")

        kwargs = {
            'title': title,
            'view': view,
            'config': config,
            'auto_size': my.kwargs.get('auto_size'),
            'class_name': my.kwargs.get('class_name'),
            'use_href': use_href,
            'target': target,
            'link_mode': link_mode
        }
        section_div = DivWdg()
        section_div.add_style("display: block")

        section_wdg = BaseSideBarBookmarkMenuWdg(**kwargs)
        section_div.add(section_wdg)
        return section_div

class BaseSideBarBookmarkMenuWdg(SideBarBookmarkMenuWdg):

    def init(my):

        my.config_search_type = my.kwargs.get("config_search_type")
        if not my.config_search_type:
            my.config_search_type = "SideBarWdg"

        my.default = my.kwargs.get('default') == 'True'

        my.view = my.kwargs.get("view")
        if type(my.view) in types.StringTypes:
            my.view = [my.view]

        web = WebContainer.get_web()
        my.palette = web.get_palette()
        my.project = Project.get()


    def get_display(my):
        top = my.top
        content_div = top

        class_name = my.kwargs.get("class_name")
        if not class_name:
            class_name = "web_menu_wdg"
        top.add_class(class_name)

        ul = HtmlElement.ul()
        top.add(ul)
        ul.add_class("main_ul")


        # add in a context smart menu for all links
        show_context_menu = my.kwargs.get("show_context_menu")
        if show_context_menu in ['true', True]:
            my.add_link_context_menu(content_div)

        for view_item in my.view:
            is_personal = False
            if view_item.startswith('my_view_'):
                is_personal = True


            info = { 'counter' : 10, 'view': view_item, 'level': 1 }

            config = my.get_config(my.config_search_type, view_item, default=my.default, personal=is_personal)
            if not config:
                continue
            ret_val = my.generate_section( config, ul, info, personal=is_personal)

            if ret_val == 'empty':
                pass


        return top


    def get_separator_wdg(my, element_name, config, options):
        #return HtmlElement.br()
        return None


    def get_title_wdg(my, element_name, config, options):
        li = HtmlElement.li()
        li.add_class("spt_side_bar_title")
        li.add_class("main_title")

        title = my._get_title(config, element_name)
        title_wdg = DivWdg()
        title_wdg.add_class("menu_header")
        li.add(title_wdg)
        title_wdg.add(title)

        li.add_style("list-style-type: none")
        li.add_style("display: block")
        li.add_style("font-weight: bold")

        return li



    def get_folder_wdg(my, element_name, config, options, base_path, current_path, info, personal, use_same_config):

        attributes = config.get_element_attributes(element_name)
        if attributes.get("is_visible") == "false":
            return


        li = HtmlElement.li()
        li.add_class("spt_side_bar_link")
        li.add_class("main_li unselectable")


        title = my._get_title(config, element_name)
        title_wdg = DivWdg()
        title_wdg.add_class("menu_header")
        li.add(title_wdg)
        title_wdg.add(title)


        ul = HtmlElement.ul()
        li.add(ul)
        ul.add_class("spt_side_bar_section")
        ul.add_class("sub_ul unselectable")
        ul.add_style('cursor','pointer')

        # then get view name from options in order to read a new
        # config and recurse ...
        options_view_name = options.get('view')
        if options_view_name:
            if use_same_config:
                xml = config.get_xml()
                sub_config = WidgetConfig.get(xml=xml)
                sub_config.set_view(options_view_name)
            else:
                sub_config = my.get_config( my.config_search_type, options_view_name, default=my.default, personal=personal)

            info['level'] += 1
            my.generate_section( sub_config, ul, info, base_path=current_path, personal=personal, use_same_config=use_same_config )
            info['level'] -= 1

        return li


    def get_link_wdg(my, element_name, config, options, info):
        attributes = config.get_element_attributes(element_name)
        if attributes.get("is_visible") == "false":
            return


        #display_options = config.get_display_options(element_name)
        #class_name = display_options.get("class_name")
        #print element_name
        #print display_options
        #print class_name
        #print "---"


        li = HtmlElement.li()
        li.add_class("spt_side_bar_link")

        level = info.get("level")
        if level == 1:
            li.add_class("menu_header")
            li.add_class("main_link unselectable")
        else:
            li.add_class("sub_li")


        title = my._get_title(config, element_name)

        show_icons = my.kwargs.get("show_icons")
        if show_icons in [True, 'true']:
            icon = attributes.get("icon")
            if not icon:
                icon = "view"
            icon_path = IconWdg.get_icon_path(icon.upper())
            li.add(HtmlElement.img(icon_path))
            li.add(" ")


        link_mode = my.kwargs.get("link_mode")
        if not link_mode:
            use_href = my.kwargs.get("use_href")
            if use_href in ['true', True]:
                link_mode = 'href'
            link_mode = 'tab'



        target = my.kwargs.get("target")
        if not target:
            target = ".spt_content"
        else:
            if target[0] in ["."]:
                target = target[1:]

        #link = "/link/%s" % (element_name)
        link = "/tab/%s" % (element_name)
        li.add_attr("spt_link", link)




        if link_mode == 'href':
            project_code = Project.get_project_code()
            #li.add("<a href='/tactic/%s/#/tab/%s'>%s</a>" % (project_code, element_name, title) )
            li.add("<a>%s</a>" % title)
            li.add_behavior( {
                'type': 'click_up',
                'bvr_repeat_interval': 3,
                'title': title,
                'link': link,
                'target': target,
                'cbjs_action': '''

                var target_class = bvr.target;

                if (target_class.indexOf("#") != -1) {
                    var target = $(document.body).getElement(target_class);
                }
                else if (target_class.indexOf(".") != -1) {
                    var parts = target_class.split(".");
                    var top = bvr.src_el.getParent("."+parts[0]);
                    var target = top.getElement("."+parts[1]);  
                }
                else {
                    var target = $(document.body).getElement("."+target_class);
                }

                //var content = $(document).getElement(bvr.target);
                var content = target;
                spt.app_busy.show("Loading link "+bvr.title);
                spt.panel.load_link(content, bvr.link);
                spt.app_busy.hide();
                '''
            } )
        elif link_mode == 'tab':
            # find the tab below the target
            li.add("<a>%s</a>" % title)
            li.add_behavior( {
                'type': 'click',
                'bvr_repeat_interval': 3,
                'title': title,
                'link': link,
                'element_name': element_name,
                'target': target,
                'cbjs_action': '''

                var target_class = bvr.target;

                if (target_class.indexOf("#") != -1) {
                    var target = $(document.body).getElement(target_class);
                }
                else if (target_class.indexOf(".") != -1) {
                    var parts = target_class.split(".");
                    var top = bvr.src_el.getParent("."+parts[0]);
                    var target = top.getElement("."+parts[1]);  
                }
                else {
                    var target = $(document.body).getElement("."+target_class);
                }


                //var content = $(document).getElement(bvr.target);
                var content = target;

                var tab_top = null;;
                // check if there even is a tab
                if (spt.tab) {
                    tab_top = spt.tab.set_tab_top(content);
                }
                if (tab_top) {
                    setTimeout( function() {
                    spt.app_busy.show("Loading link "+bvr.title);
                    }, 0 );



                    var link = bvr.src_el.getAttribute("spt_link");
                    var class_name = 'tactic.ui.panel.HashPanelWdg';
                    var kwargs = {
                        hash: link
                    }
                    // Note: hash is different from link
                    hash = "/link/" + bvr.element_name;
                    spt.tab.add_new(bvr.element_name,bvr.title,class_name,kwargs, null, hash);
                }
                else {
                    spt.app_busy.show("Loading link "+bvr.title);
                    spt.panel.load_link(content, bvr.link);
                }

                spt.app_busy.hide();
                '''
            } )
 


        elif link_mode == 'custom':
            li.add("<a>%s</a>" % title)
            li.add_attr('spt_title', title)
            li.add_attr('spt_element_name', element_name)

        else:

            li.add(title)

            li.add_attr("spt_title", title)
            li.add_attr("spt_element_name", element_name)
            li.add_attr("spt_icon", attributes.get("icon"))
            li.add_attr("spt_view", config.get_view() )
            li.add_attr("spt_path", options['path'])
            li.add_attr("spt_view", config.get_view() )
            li.add_class("spt_side_bar_element")

            my.add_link_behavior(li, element_name, config, options)


        return li


