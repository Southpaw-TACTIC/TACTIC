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
__all__ = ["SimpleSideBarWdg", "TabSideBarWdg"]

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

    def get_views(self):
        views = [] 

        view = self.kwargs.get('view')
        if not view:
            view = "project_view"
            views.append(view)
        else:
            extra_views = view.split("|")
            views.extend(extra_views)

        #view = "self_view_%s" % Environment.get_user_name()

        return views


    def get_subdisplay(self, views):
        div = DivWdg()
        div.set_attr('spt_class_name', Common.get_full_class_name(self))

        div.add( self.get_bookmark_menu_wdg("", None, views) )
        return div


    def get_bookmark_menu_wdg(self, title, config, view):

        use_href = self.kwargs.get("use_href")
        target = self.kwargs.get("target")
        link_mode = self.kwargs.get("link_mode")

        kwargs = {
            'title': title,
            'view': view,
            'config': config,
            'auto_size': self.kwargs.get('auto_size'),
            'class_name': self.kwargs.get('class_name'),
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

    def init(self):

        self.config_search_type = self.kwargs.get("config_search_type")
        if not self.config_search_type:
            self.config_search_type = "SideBarWdg"

        self.default = self.kwargs.get('default') == 'True'

        self.view = self.kwargs.get("view")
        if type(self.view) in types.StringTypes:
            self.view = [self.view]

        web = WebContainer.get_web()
        self.palette = web.get_palette()
        self.project = Project.get()


    def get_display(self):
        top = self.top
        content_div = top

        class_name = self.kwargs.get("class_name")
        if not class_name:
            class_name = "web_menu_wdg"
        top.add_class(class_name)

        ul = HtmlElement.ul()
        top.add(ul)
        ul.add_class("main_ul")


        # add in a context smart menu for all links
        show_context_menu = self.kwargs.get("show_context_menu")
        if show_context_menu in ['true', True]:
            self.add_link_context_menu(content_div)

        for view_item in self.view:
            is_personal = False
            if view_item.startswith('my_view_'):
                is_personal = True


            info = { 'counter' : 10, 'view': view_item, 'level': 1 }

            config = self.get_config(self.config_search_type, view_item, default=self.default, personal=is_personal)
            if not config:
                continue
            ret_val = self.generate_section( config, ul, info, personal=is_personal)

            if ret_val == 'empty':
                pass


        return top


    def get_separator_wdg(self, element_name, config, options):
        #return HtmlElement.br()
        return None


    def get_title_wdg(self, element_name, config, options):
        li = HtmlElement.li()
        li.add_class("spt_side_bar_title")
        li.add_class("main_title")

        title = self._get_title(config, element_name)
        title_wdg = DivWdg()
        title_wdg.add_class("menu_header")
        li.add(title_wdg)
        title_wdg.add(title)

        li.add_style("list-style-type: none")
        li.add_style("display: block")
        li.add_style("font-weight: bold")

        return li



    def get_folder_wdg(self, element_name, config, options, base_path, current_path, info, personal, use_same_config):

        attributes = config.get_element_attributes(element_name)
        if attributes.get("is_visible") == "false":
            return


        li = HtmlElement.li()
        li.add_class("spt_side_bar_link")
        li.add_class("main_li unselectable")


        title = self._get_title(config, element_name)
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
                sub_config = self.get_config( self.config_search_type, options_view_name, default=self.default, personal=personal)

            info['level'] += 1
            self.generate_section( sub_config, ul, info, base_path=current_path, personal=personal, use_same_config=use_same_config )
            info['level'] -= 1

        return li


    def get_link_wdg(self, element_name, config, options, info):
        attributes = config.get_element_attributes(element_name)
        if attributes.get("is_visible") == "false":
            return

        if options.get("popup") in [True, 'true']:
            popup = True
        else:
            popup = False

        #display_options = config.get_display_options(element_name)
        #class_name = display_options.get("class_name")
        #print(element_name)
        #print(display_options)
        #print(class_name)
        #print("---")


        li = HtmlElement.li()
        li.add_class("spt_side_bar_link")

        level = info.get("level")
        if level == 1:
            li.add_class("menu_header")
            li.add_class("main_link unselectable")
        else:
            li.add_class("sub_li")


        title = self._get_title(config, element_name)

        show_icons = self.kwargs.get("show_icons")
        if show_icons in [True, 'true']:
            icon = attributes.get("icon")
            if not icon:
                icon = "view"
            icon_path = IconWdg.get_icon_path(icon.upper())
            li.add(HtmlElement.img(icon_path))
            li.add(" ")


        link_mode = self.kwargs.get("link_mode")
        if not link_mode:
            use_href = self.kwargs.get("use_href")
            if use_href in ['true', True]:
                link_mode = 'href'
            link_mode = 'tab'



        target = self.kwargs.get("target")
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
                    var target = document.id(document.body).getElement(target_class);
                }
                else if (target_class.indexOf(".") != -1) {
                    var parts = target_class.split(".");
                    var top = bvr.src_el.getParent("."+parts[0]);
                    var target = top.getElement("."+parts[1]);  
                }
                else {
                    var target = document.id(document.body).getElement("."+target_class);
                }

                //var content = document.id(document).getElement(bvr.target);
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
                'popup': popup,
                'target': target,
                'cbjs_action': '''

                var target_class = bvr.target;

                if (target_class.indexOf("#") != -1) {
                    var target = document.id(document.body).getElement(target_class);
                }
                else if (target_class.indexOf(".") != -1) {
                    var parts = target_class.split(".");
                    var top = bvr.src_el.getParent("."+parts[0]);
                    var target = top.getElement("."+parts[1]);  
                }
                else {
                    var target = document.id(document.body).getElement("."+target_class);
                }


                //var content = document.id(document).getElement(bvr.target);
                var content = target;

                var tab_top = null;;
                // check if there even is a tab
                if (spt.tab) {
                    tab_top = spt.tab.set_tab_top(content);
                }
                if (tab_top) {

                    var link = bvr.src_el.getAttribute("spt_link");
                    var class_name = 'tactic.ui.panel.HashPanelWdg';
                    var kwargs = {
                        hash: link
                    }
                    // Note: hash is different from link
                    hash = "/link/" + bvr.element_name;

                    if (bvr.popup) {
                        spt.panel.load_popup(bvr.title, class_name, kwargs)
                    }
                    else {
                        spt.tab.add_new(bvr.element_name,bvr.title,class_name,kwargs, null, hash);
                    }
                }
                else {
                    spt.panel.load_link(content, bvr.link);
                }

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

            self.add_link_behavior(li, element_name, config, options)


        return li




class TabSideBarWdg(SideBarBookmarkMenuWdg):

    def get_display(self):

        top = self.top

        self.config_search_type = self.kwargs.get("config_search_type")
        if not self.config_search_type:
            self.config_search_type = "SideBarWdg"


        view_item = self.kwargs.get("view")
        if not view_item:
            view_item = "definition"
        self.default = self.kwargs.get('default') == 'True'



        use_default_style = self.kwargs.get("use_default_style")

        is_personal = False
 
        # get the config
        config = self.get_config(self.config_search_type, view_item, default=self.default, personal=is_personal)
        element_names = config.get_element_names()

        new_config_xml = []
        new_config_xml.append('''<config>''')
        new_config_xml.append('''<tab>''')

        from pyasm.common import Environment
        from pyasm.biz import Project
        from tactic.ui.common import WidgetClassHandler


        security = Environment.get_security()
        user = Environment.get_user_name()


        self.project = Project.get()

        class_handler = WidgetClassHandler()
        for element_name in element_names:


            # handle security
            # TODO: put this in the base class
            key = {'project': self.project.get_code(), 'element': element_name}
            key2 = {'element': element_name}
            key3 = {'project': self.project.get_code(), 'element': '*'}
            key4 = {'element': '*'}
            keys = [key, key2, key3, key4]
            if element_name.startswith('%s.'%user):
                # personal view is default to be viewable
                if not security.check_access("link", keys, "view", default="view"):
                    continue
            elif not security.check_access("link", keys, "view", default="deny"):
                continue


            display_handler = config.get_display_handler(element_name)
            display_options = config.get_display_options(element_name)

            # the sidebar currently uses a different structure than the
            # tab widget so we have to translate

            widget_key = display_options.get("widget_key")
            if widget_key:
                class_name = class_handler.get_display_handler(widget_key)
            else:
                class_name = display_options.get("class_name")

            new_config_xml.append('''<element name="%s">''' % element_name)

            if class_name:
                new_config_xml.append('''<display class="%s">''' % class_name)
            else:
                new_config_xml.append('''<display widget_key="%s">''' % widget_key)


            for name, value in display_options.items():
                if name in ['widget_key', 'class_name']:
                    continue
                new_config_xml.append('''<%s>%s</%s>''' % (name, value, name))


            new_config_xml.append('''</display>''')

            new_config_xml.append('''</element>''')

        new_config_xml.append('''</tab>''')
        new_config_xml.append('''</config>''')

        new_config_xml_str = "\n".join( new_config_xml )


        from tactic.ui.container import TabWdg
        tab = TabWdg(config_xml=new_config_xml_str, view="tab", show_add=False, show_remove=False, use_default_style=use_default_style)
        top.add(tab)




        return top




