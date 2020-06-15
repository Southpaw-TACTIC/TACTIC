import six

from pyasm.biz import Project
from pyasm.common import Environment, Common
from pyasm.web import HtmlElement, DivWdg, WebContainer, SpanWdg, Palette
from pyasm.widget import WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ButtonNewWdg, ActionButtonWdg, BootstrapButtonRowWdg
from tactic.ui.app import PageHeaderWdg, PageNavContainerWdg, ProjectSelectWdg
from tactic.ui.container import SmartMenu

from .bootstrap_tab_wdg import *


__all__ = ['BootstrapIndexWdg', 'BootstrapSideBarPanelWdg', 'BootstrapTopNavWdg', 'BootstrapProjectSelectWdg', 'BootstrapPortalTopNavWdg', 'BootstrapPortalIndexWdg']


from tactic.ui.panel import SideBarPanelWdg, SideBarBookmarkMenuWdg
class BootstrapSideBarBookmarkMenuWdg(SideBarBookmarkMenuWdg):
    

    def get_display(self):
        
        self.config_search_type = self.kwargs.get("config_search_type")
        if not self.config_search_type:
            self.config_search_type = "SideBarWdg"
        self.default = self.kwargs.get('default') == 'True'

        self.project = Project.get()

        title = self.kwargs.get('title')
        config = self.kwargs.get('config')
        view = self.kwargs.get('view')
        parent_view = self.kwargs.get('parent_view')
        sortable = self.kwargs.get('sortable')

        self.prefix = self.kwargs.get("prefix")
        if not self.prefix:
            self.prefix = "side_bar"

        self.mode = self.kwargs.get("mode")
        if not self.mode:
            self.mode = 'view'

        # get the content div
        section_div = HtmlElement("nav")
        section_div.add_class("spt_bs_left_sidebar_inner") 

        section_div.set_attr('spt_class_name', Common.get_full_class_name(self))
        for name, value in self.kwargs.items():
            if name == "config":
                continue
            section_div.set_attr("spt_%s" % name, value)
        
        content_div = HtmlElement.ul()
        section_div.add(content_div)
        content_div.add_class("spt_side_bar_content")
        content_div.add_class("list-unstyled components")

        # add in a context smart menu for all links
        self.add_link_context_menu(content_div)
        if isinstance(view, six.string_types):
            view = [view]

        # draw each view
        for view_item in view:
            is_personal = False
            if view_item.startswith('my_view_'):
                is_personal = True

            config = self.get_config(self.config_search_type, view_item, default=self.default, personal=is_personal)
            if not config:
                continue

            # make up a title
            title = HtmlElement.li()
            title.add_class("nav-item")

            view_attrs = config.get_view_attributes()
            tt = view_attrs.get("title")
            if not tt:
                if view_item.startswith("my_view_"):
                    tt = "My Views"
                else:
                    tt = view_item.replace("_", " ")
                tt = tt.capitalize()

            title_label = HtmlElement("a")
            title_label.add_class("nav-link")
            title.add( title_label )
            title_label.add("""<h6>%s</h6>""" % tt)

            content_div.add( title )
            if sortable:
                title.add_behavior({'type': 'click_up',
                    'cbjs_action': "spt.panel.refresh('ManageSideBarBookmark_%s')" % view_item})
            info = { 'counter' : 10, 'view': view_item, 'level': 1 }

            ret_val = self.generate_section( config, content_div, info, personal=is_personal )
            if ret_val == 'empty':
                title.add_style("display: none")

            """
            #TODO: What does this do?
            error_list = Container.get_seq(self.ERR_MSG)
            if error_list:
                span = SpanWdg()
                span.add_style('background', 'red')
                span.add('<br/>'.join(error_list))
                content_div.add(span)
                Container.clear_seq(self.ERR_MSG)
            """
            self.add_dummy(config, content_div)

        # display the schema links on the bottom of the the admin views
        if view_item == "admin_views":
            config_xml = self.get_schema_xml()
            config = WidgetConfig.get(xml=config_xml, view='schema')
            self.generate_section( config, content_div, info, personal=False, use_same_config=True )

        return section_div


    def get_separator_wdg(self, element_name, config, options):
        div = DivWdg()
        div.add_attr("spt_view", config.get_view() )
        div.add_class("spt_side_bar_element")
        div.add_class("spt_side_bar_separator")
        div.add_attr("spt_element_name", element_name)
        div.add_class("dropdown-divider")
        div.add_style("margin: 3px 30px 3px 20px")
        div.add_style("opacity: 0.5")
        
        options = config.get_display_options(element_name)
        self.add_separator_behavior(div, element_name, config, options)

        return div



    def get_folder_wdg(self, element_name, config, options, base_path, current_path, info, personal, use_same_config):
        security = Environment.get_security()
        default_access = "view"

        title = self._get_title(config, element_name)

        attributes = config.get_element_attributes(element_name)

        if self.mode != 'edit' and attributes.get("is_visible") == "false":
            return

        options = config.get_display_options(element_name)

        state = attributes.get("state")

        paths = []
        if current_path in paths:
            is_open = True
        elif state == 'open':
            is_open = True
        else:
            is_open = False


        config_view = config.get_view()

        current_path = "%s/%s" % (base_path, element_name)

        outer_div = HtmlElement.li()

        if self.mode == 'edit' and attributes.get("is_visible") == "false":
            outer_div.add_style("opacity: 0.5")

        outer_div.add_attr("spt_view", config_view )
        outer_div.add_class("spt_side_bar_element")
        outer_div.add_class("spt_side_bar_section")
        outer_div.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        outer_div.add_attr("spt_element_name", element_name)
        outer_div.add_attr("spt_title", title)

        outer_div.add_class("nav_item")

        # add an invisible drop widget
        outer_div.add(self.get_drop_wdg())


        # Create the link
        s_link_div = HtmlElement("a")
        s_link_div.add_class("SPT_DTS")
        s_link_div.add_class("spt_side_bar_section_link")
        s_link_div.add_attr("data-toggle", "collapse")
        s_link_div.add_attr("aria-expanded", "false")
        s_link_div.add_class("dropdown-toggle")
        s_link_div.add_class("nav-link")

        icon = attributes.get("sb_icon")
        if icon:
            s_link_div.add('<i class="%s"></i>' % icon)
        
        
        s_content_div = HtmlElement.ul()
        s_content_div.add_class("list-unstyled collapse")
        content_id = s_content_div.set_unique_id()
        s_link_div.set_attr("href", "#%s" % content_id)

        # add an icon if applicable
        icon = attributes.get("icon")
        if icon:
            icon = icon.upper()
            try:
                icon_wdg =  IconWdg(title, icon)
                s_link_div.add(icon_wdg)
            except:
                pass
        s_link_div.add(title)

        # create the content of the link div
        info['counter'] = info['counter'] + 1
        s_content_div.add_class("SPT_DTS")

        s_content_div.add_attr("spt_path", current_path)

        s_content_div.add_class("spt_side_bar_section_content")

        # add the behaviors
        self.add_folder_behavior(s_link_div, element_name, config, options)

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
            self.generate_section( sub_config, s_content_div, info, base_path=current_path, personal=personal, use_same_config=use_same_config )
            info['level'] -= 1


        outer_div.add(s_link_div)

        inner_div = DivWdg()
        outer_div.add(inner_div)
        inner_div.add(s_content_div)
        inner_div.add_style("overflow: hidden")

        return outer_div


    def get_link_wdg(self, element_name, config, options, info):
        attributes = config.get_element_attributes(element_name)

        if self.mode != 'edit' and attributes.get("is_visible") == "false":
            return

        title = self._get_title(config, element_name)

        default_access = "view"
        path = options.get('path')



        link_wdg = HtmlElement.li()


        if self.mode == 'edit' and attributes.get("is_visible") == "false":
            link_wdg.add_style("opacity: 0.5")

        link_wdg.add_attr("spt_title", title)
        link_wdg.add_attr("spt_icon", attributes.get("icon"))
        link_wdg.add_attr("spt_view", config.get_view() )
        link_wdg.add_attr("spt_element_name", element_name)
        link_wdg.add_attr("spt_path", options['path'])
        link_wdg.add_attr("spt_view", config.get_view() )

        link_wdg.add_class("spt_side_bar_element")
        link_wdg.add_class("spt_side_bar_link")
        link_wdg.add_class("hand")
 
        link_wdg.add_class("nav-item")

        # add the mouseover color change
        link_wdg.add_class("SPT_DTS")

        # add an invisible drop widget
        drop_wdg = self.get_drop_wdg()
        link_wdg.add(drop_wdg)


        span = HtmlElement("a")
        span.add_class("spt_side_bar_title")
        span.add_class("nav-link")


        # add an icon if applicable
        icon = attributes.get("icon")
        if icon:
            icon = icon.upper()
            try:
                icon_wdg =  IconWdg(title, icon)
                span.add(icon_wdg)
            except:
                pass





        icon = attributes.get("sb_icon")
        if icon:
            span.add('<i class="%s"></i>' % icon)

        span.add(title)
        link_wdg.add(span)

        inputs = options
        inputs['element_name'] = element_name
        inputs['title'] = title
        inputs["widget_key"] = "__WIDGET_UNKNOWN__"

        widget_key = link_wdg.generate_widget_key(options["class_name"], inputs=options)
        options["widget_key"] = widget_key


        self.add_link_behavior(link_wdg, element_name, config, options)


        return link_wdg



class BootstrapSideBarPanelWdg(SideBarPanelWdg):

    def get_bootstrap_styles(self):
        style = HtmlElement.style('''

.spt_bs_left_sidebar a, a:hover, a:focus {
    color: inherit;
    text-decoration: none;
    transition: all 0.3s;
}

.spt_bs_left_sidebar {
    background: var(--spt_palette_md_primary);
    min-width: var(--left_modal_width, 300px);
    max-width: var(--left_modal_width, 300px);
    color: var(--spt_palette_side_bar_title_color);
    transition: all 0.3s;
    z-index: 1000;
    padding-top: 40px;
    height: 100vh;
    position: absolute;
    left: calc(-1 * var(--left_modal_width, 300px));
    top: 0;
}

.spt_bs_left_sidebar_overlay.active {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 999;
    width: 100vw;
    height: 100vh;
    background-color: #000;
    opacity: .26;
}


.spt_bs_left_sidebar.active {
    left: 0px;
}

.spt_bs_left_sidebar.active .sidebar-header h3,
.spt_bs_left_sidebar.active .CTAs {
    display: none;
}
        

.spt_bs_left_sidebar.active .sidebar-header strong {
    display: block;
}

.spt_bs_left_sidebar ul li a {
    text-align: left;
}

.spt_bs_left_sidebar.active ul li a {
    padding: 20px 10px;
    text-align: center;
    font-size: 0.85em;
}

.spt_bs_left_sidebar.active ul li a i {
    margin-right: 15px;
    font-size: 1.5em;
}

.spt_bs_left_sidebar.active ul ul ul a {
    padding-left: 90px !important;
}

.spt_bs_left_sidebar.active .dropdown-toggle::after {
    top: auto;
    bottom: 10px;
    right: 50%;
    -webkit-transform: translateX(50%);
    -ms-transform: translateX(50%);
    transform: translateX(50%);
}

.spt_bs_left_sidebar ul.components {
    padding: 20px 0;
}

.spt_bs_left_sidebar ul li a {
    padding: 10px;
    font-size: 1.1em;
    display: block;
}

.spt_bs_left_sidebar ul li .nav-link:hover {
    background: var(--spt_palette_md_primary_dark);
}

.spt_bs_left_sidebar ul li a i {
    margin-right: 10px;
}

.spt_bs_left_sidebar ul li .nav-link[aria-expanded="true"] {
    background: var(--spt_palette_md_primary_dark);
}

.spt_bs_left_sidebar a[data-toggle="collapse"] {
    position: relative;
}

.spt_bs_left_sidebar .dropdown-toggle::after {
    display: block;
    position: absolute;
    top: 50%;
    right: 20px;
    transform: translateY(-50%);
}

/* Submenu */
.spt_bs_left_sidebar ul ul a {
    font-size: 0.9rem !important;
    //padding-left: 20px !important;
    background: var(--spt_palette_md_primary_dark);
}

/* Dropdown divider */
.spt_bs_left_sidebar ul ul .dropdown-divider {
    margin: 0rem 0rem;
    padding: .5rem 0rem;
}


/* Sub-sub-menu style */
.spt_bs_left_sidebar ul ul ul a {
    font-size: 0.9rem !important;
    //padding-left: 40px !important;
    background: var(--spt_palette_md_primary_dark);
}


.spt_bs_left_sidebar ul.CTAs {
    padding: 20px;
}

.spt_bs_left_sidebar ul.CTAs a {
    text-align: center;
    font-size: 0.9em !important;
    display: block;
    border-radius: 5px;
    margin-bottom: 5px;
}

/* Sidebar item hover */
.spt_bs_left_sidebar ul li .nav-link:hover {
    color: var(--spt_palette_side_bar_title_color);
    background: var(--spt_palette_md_primary_dark);
}

.spt_side_bar_element .nav-link {
    text-transform: none;
}

.spt_side_bar_element .spt_side_bar_title {
    display: flex;
    align-items: center;
}


@media (max-width: 768px) {


    .spt_bs_left_sidebar .dropdown-toggle::after {
        top: auto;
        bottom: 10px;
        right: 50%;
        -webkit-transform: translateX(50%);
        -ms-transform: translateX(50%);
        transform: translateX(50%);
    }
    
    .spt_bs_left_sidebar.active {
        margin-left: 0 !important;
    }
    
    .spt_bs_left_sidebar .sidebar-header h3,
    .spt_bs_left_sidebar .CTAs {
        display: none;
    }
    
    
    .spt_bs_left_sidebar .sidebar-header strong {
        display: block;
    }
    
    .spt_bs_left_sidebar ul li a {
        padding: 20px 10px;
    }
    
    .spt_bs_left_sidebar ul li a span {
        font-size: 0.85em;
    }
    
    .spt_bs_left_sidebar ul li a i {
        margin-right: 0;
        display: block;
    }
    
    .spt_bs_left_sidebar ul ul a {
        padding: 10px !important;
    }
    
    .spt_bs_left_sidebar ul li a i {
        font-size: 1.3em;
    }
    
    .spt_bs_left_sidebar {
        margin-left: 0;
    }
    
    .spt_bs_left_sidebarCollapse span {
        display: none;
    }
    
}

@media (max-width: 575.98px) {
    
    .spt_bs_left_sidebar {
        display: none;
    }

    .spt_bs_left_sidebar_overlay {
        display: none;
    }


}    


        ''')


        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        is_admin_page = web.is_admin_page()
        is_admin_page = True
        if is_admin_page:

            style.add('''
/* (for admin site) */
.spt_bs_left_sidebar.active ul li a {
    background: var(--spt_palette_md_primary);
    padding: 10px 0px;
    padding-left: 50px;
    font-size: 0.9rem;
    font-weight: 300;
    text-align: left;
}


.spt_bs_left_sidebar.active ul ul li a {
    padding-left: 70px;
}

.spt_bs_left_sidebar .nav-link h6 {
    margin-left: -35px;
    margin-top: 15px;
    padding-left: 10px;
    border-bottom: solid 1px #e9ecef;
    font-weight: bold;
    font-size: 1.2rem;
}


.spt_bs_left_sidebar .dropdown-toggle::after {
    top: 50%;
    right: 15px;
}
.spt_bs_left_sidebar.active .dropdown-toggle::after {
    top: 50%;
    right: 15px;
}



            ''')


        return style



    def get_subdisplay(self, views):

        div = DivWdg()
        div.add_class("spt_bs_left_sidebar")
        div.set_id("side_bar")
        div.set_attr('spt_class_name', Common.get_full_class_name(self))

        outer_div = DivWdg()
        div.add(outer_div)

        load_div = DivWdg()
        outer_div.add(load_div)
        load_div.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        } )


        outer_div.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            spt.named_events.fire_event("side_bar|toggle")
            //bvr.src_el.getParent().setStyle("overflow-y", "hidden");
            '''
        } )

        # add the down button
        down = DivWdg()
        down.set_id("side_bar_scroll_down")
        down.add_class("hand")
        down.add_looks("navmenu_scroll")
        down.add_style("display: none")
        down.add_style("height: 10px")
        down.add("<div style='margin-bottom: 4px; text-align: center'>" \
                 "<img class='spt_order_icon' src='/context/icons/common/order_array_up_1.png'></div>")
        down.add_event("onclick", "new Fx.Tween('side_bar_scroll').start('margin-top', 0);" \
                       "document.id(this).setStyle('display', 'none');")
        outer_div.add(down)


        
        inner_div = DivWdg()
        inner_div.set_id("side_bar_scroll")
        outer_div.add(inner_div)

        # Try regular scroll for now
        """
        div.add_style("overflow-y: hidden")
        div.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            bvr.src_el.setStyle("overflow-y", "auto");
            '''
        } )
        """


        behavior = {
            'type': 'wheel',
            'cbjs_action': 'spt.side_bar.scroll(evt,bvr)',
        }
        inner_div.add_behavior(behavior)

        styles = self.get_bootstrap_styles()
        inner_div.add(styles)

        inner_div.add( self.get_bookmark_menu_wdg("", None, views) )
        inner_div.add(HtmlElement.br())

        if self.kwargs.get("is_refresh"):
            return outer_div
        else:
            return div



    def get_bookmark_menu_wdg(self, title, config, views):

        kwargs = {
            'title': title,
            'view': views,
            'config': config,
            'auto_size': self.kwargs.get('auto_size')
        }
        section_wdg = BootstrapSideBarBookmarkMenuWdg(**kwargs)
        
        return section_wdg


class BootstrapTopNavWdg(BaseRefreshWdg, PageHeaderWdg):

    def get_bootstrap_styles(self):

        style = HtmlElement.style("""

            .spt_bs_top_nav {
                background: var(--spt_palette_md_primary_dark);
            }

            .spt_bs_top_nav .spt_side_bar_content {
                display: flex;
                flex-direction: column;
                padding-left: 0;
                margin-bottom: 0;
                list-style: none;
            }

            .spt_bs_top_nav a.nav-link {
                color: #f5f5f5;
                padding: .5321rem;
                font-size: .875rem;
                font-weight: 400;
            }

            .spt_bs_top_nav a.nav-link:hover {
                color: #dcdcdc;
            }

            .spt_bs_top_nav {
                z-index: 10;
            }

            .spt_bs_top_nav_content {
                max-height: calc(100vh - 56px);
                overflow-y: auto;
            }
        """)

        return style

    def get_display(self):

        top_nav_wdg =  HtmlElement("nav")
        
        styles = self.get_bootstrap_styles()
        top_nav_wdg.add(styles)

        top_nav_wdg.add_class("spt_bs_top_nav navbar navbar-dark fixed-top")
        
        nav_header = DivWdg()
        top_nav_wdg.add(nav_header)
        nav_header.add_class("spt_bs_top_nav_left d-flex")


        view_side_bar = self.kwargs.get("view_side_bar")
        if view_side_bar:
            toggle_div = DivWdg()
            nav_header.add(toggle_div)
            
            btn_class = "btn bmd-btn-icon"
            toggle_btn = ButtonNewWdg(
                icon="FA_TH", 
                title="Toggle Sidebar", 
                btn_class=btn_class,
                opacity="1.0",
                navbar_collapse_target="navbarCollapse"
            )
            toggle_div.add(toggle_btn)
            
            toggle_btn.add_class("spt_toggle_sidebar")
            toggle_btn.add_class("spt_nav_icon")

            toggle_div.add_behavior({
                'type': 'click',
                'cbjs_action': """
                    spt.named_events.fire_event("side_bar|toggle")
                """
            })


            toggle_div.add_behavior( {
                'type': 'listen',
                'event_name': 'side_bar|toggle',
                'cbjs_action': '''
                    spt.side_bar.toggle()
                '''
            } )

        logo_div = self.get_logo_div()
        nav_header.add(logo_div)

        right_wdg = self.get_right_wdg()
        right_wdg.add_class("spt_bs_top_nav_right")
        top_nav_wdg.add(right_wdg)

        if view_side_bar:
            hidden_nav = DivWdg()
            hidden_nav.add_class("spt_bs_top_nav_content")
            hidden_nav.add_class("collapse")
            hidden_nav.add_class("navbar-collapse")
            hidden_nav.set_id("navbarCollapse")
            
            hidden_nav.add_behavior({
                'type': 'load',
                'cbjs_action': '''
                    let app_top = bvr.src_el.getParent(".spt_bootstrap_top");
                    let left_sidebar = app_top.getElement(".spt_bs_left_sidebar");
                    let sidebar_content = left_sidebar.getElement(".spt_side_bar_content");
                    let mobile_sidebar = spt.behavior.clone(sidebar_content);

                    //FIX IDs since Bootstrap menus use IDs to target collapsing menus
                    let section_els = mobile_sidebar.getElements(".spt_side_bar_section");
                    let ID = function () {
                      return '_' + Math.random().toString(36).substr(2, 9);
                    };
                    let handle_section = function(section_el) {
                       let toggle = section_el.getElement(".spt_side_bar_section_link");
                       let dropdown = section_el.getElement(".spt_side_bar_section_content");
                       
                       let new_id = ID();
                       toggle.setAttribute("href", "#" + new_id);
                       dropdown.setAttribute("id", new_id);
                    }
                    section_els.forEach(handle_section);

                    mobile_sidebar.inject(bvr.src_el);
                '''
            })

            top_nav_wdg.add(hidden_nav)


        # HELP POPUP
        from tactic.ui.container import DialogWdg
        help_dialog = DialogWdg(z_index=900, show_pointer=False)
        top_nav_wdg.add(help_dialog)
        help_dialog.add_title("Help")
        help_dialog.add_class("spt_help")

        help_div = DivWdg()
        help_dialog.add(help_div)

        from tactic.ui.app import HelpWdg
        help_wdg = HelpWdg()
        help_div.add(help_wdg)

        # License Manager
        license = Environment.get_security().get_license()
        if not license.is_licensed():
            from tactic.ui.app import LicenseManagerWdg
            license_manager = LicenseManagerWdg(use_popup=True)
            top_nav_wdg.add(license_manager)


        return top_nav_wdg


    def get_logo_div(self):
        
        brand_div = DivWdg()
        brand_div.add_class("spt_logo")
       
        palette = Palette()
        sidebar_title_color = palette.color("side_bar_title_color")
        if sidebar_title_color == "#000000":
            src = "/context/logo/tactic_logo_black.svg"
        else:
            src=  "/context/logo/tactic_logo_white.svg"
        brand_div.add("""<a><img src="%s"/></a>""" % src)

        style = HtmlElement.style(""" 
            .spt_bs_top_nav .spt_logo {
                display: flex;
                align-items: center;
            }

            .spt_bs_top_nav .spt_logo img { 
                height: 16px;
            }
        """)
        brand_div.add(style)
        
        return brand_div



    def get_right_wdg(self):
        right_wdg = DivWdg()
        right_wdg.add_class("d-flex")

        btn_class = "btn bmd-btn-icon"
        toggle_btn = ButtonNewWdg(
            icon="FA_COG",
            title="Settings",
            btn_class=btn_class,
            opacity="1.0",
        )
        toggle_btn.add_class("ml-1 spt_nav_icon")
        button_row = BootstrapButtonRowWdg()
        button_row.set_toggle_btn(toggle_btn)

        right_wdg.add(button_row)

        project_select_wdg = BootstrapProjectSelectWdg()
        button_row.add(project_select_wdg)

        gear_menu_wdg = BootstrapIndexGearMenuWdg()
        button_row.add(gear_menu_wdg)

        user_wdg = self.get_user_wdg()
        right_wdg.add(user_wdg)

        tab_div = self.get_tab_manager()
        right_wdg.add(tab_div)
        
        return right_wdg



    def get_user_wdg(self):
       
        user_wdg = DivWdg()

        login = Environment.get_login()
        display_name = login.get_full_name()
        if not display_name:
            display_name = login.get_login()
       
        from pyasm.biz import Snapshot
        snapshot = Snapshot.get_latest_by_sobject(login)
        if snapshot:
            path = snapshot.get_web_path_by_type()
 
            user_wdg.add(HtmlElement.style("""
                .spt_hit_wdg.spt_nav_user_btn {                
                    background-image: url(%s);
                    background-size: cover;
                    background-repeat: no-repeat;
                } 
            """ % path))

            icon = "FA_USERX"
        else:
            icon = "FA_USER"

        title = "Logged in as %s" % display_name
        
        
        btn_class = "btn bmd-btn-icon"
        user_btn = ButtonNewWdg(
            icon=icon, 
            title=title, 
            btn_class=btn_class,
            opacity="1.0"
        )
        
        
        user_wdg.add(user_btn)
        user_btn.add_class("ml-1 spt_nav_user_btn spt_nav_icon")
        user_btn.get_collapsible_wdg().add_class("dropdown-toggle")
        
        menus = self.get_smart_menu()
        SmartMenu.add_smart_menu_set(user_btn.get_button_wdg(), [menus])
        SmartMenu.add_smart_menu_set(user_btn.get_collapsible_wdg(), [menus])
        SmartMenu.assign_as_local_activator(user_btn.get_button_wdg(), None, True)
        SmartMenu.assign_as_local_activator(user_btn.get_collapsible_wdg(), None, True)

        
        return user_wdg

    def get_tab_manager(self):


        tab_div = DivWdg()
        tab_div.add_class("spt_mobile_tab_manager")
        tab_div.add_class("dropdown d-block d-sm-none")

        btn_class = "btn bmd-btn-icon"
        tab_btn = ButtonNewWdg(
            icon="FA_CLONE",
            title="View Tabs",
            btn_class=btn_class,
            opacity="1.0",
        )
        tab_div.add(tab_btn)

        tab_btn.add_class("dropdown-toggle ml-1 spt_nav_icon")
        tab_btn.add_behavior({
            'type': 'click',
            'cbjs_action': '''
                
                // Dynamically build the tab menu
                tab_div = bvr.src_el.getParent(".spt_mobile_tab_manager");
                menu = tab_div.getElement(".dropdown-menu");
                
                // Reset menu
                menu.innerHTML = "";
                
                item_template = tab_div.getElement(".SPT_TEMPLATE");

                spt.tab.set_main_body_tab();
                var headers = spt.tab.get_headers();

 
                // TODO: Fix styling.
                handle_header = function(header) {
                    header.removeAttribute("style");
                }

                var new_items = [];
                headers.forEach(function(header) {
                    new_item = spt.behavior.clone(item_template);
                    handle_header(new_item);
                    new_item.removeClass("SPT_TEMPLATE");
                    new_header = header.clone();
                    new_header.inject(new_item)
                    new_items.push(new_item);
                });

                new_items.forEach(function(item){
                    item.inject(menu);
                });

            '''
        })

        # Dropdown behavior
        tab_btn_id = tab_btn.set_unique_id()
        tab_btn.add_attr("data-toggle", "dropdown")
        tab_btn.add_attr("aria-haspopup", "true")
        tab_btn.add_attr("aria-expanded", "false")

        tab_menu = DivWdg()
        tab_div.add(tab_menu)
        tab_menu.add_class("dropdown-menu dropdown-menu-right")
        tab_menu.add_attr("aria-labelledby", tab_btn_id)

        #HACK
        tab_menu.add_style("right", "0")
        tab_menu.add_style("left", "auto")

        item_template = HtmlElement("a")
        tab_div.add(item_template)
        item_template.add_class("SPT_TEMPLATE")
        item_template.add_class("dropdown-menu-item")
        
        main_body_tab_id = self.kwargs.get("main_body_tab_id")
        item_template.add_attr("spt_tab_id", main_body_tab_id)
        
        item_template.add_behavior({
            'type': 'click',
            'tab_id': main_body_tab_id,
            'cbjs_action': '''
                var tab_id = bvr.tab_id;
                spt.tab.top = document.id(tab_id);
                var header = bvr.src_el.getElement(".spt_tab_header");
                if (header.hasClass("spt_is_selected")) return;
                var element_name = header.getAttribute("spt_element_name");
                spt.tab.select(element_name);
            '''
        })

        
        item_template.add_relay_behavior({
            'type': 'click',
            'tab_id': main_body_tab_id,
            'bvr_match_class': 'spt_tab_remove',
            'cbjs_action': '''
                
                var mobile_header = bvr.src_el.getParent(".spt_tab_header");
                var element_name = mobile_header.getAttribute("spt_element_name");

                spt.tab.top = document.id(bvr.tab_id);
                orig_header = spt.tab.get_header(element_name);
                orig_tab_remove = orig_header.getElement(".spt_tab_remove"); 
                spt.tab.close(orig_tab_remove);
            '''
        })

        
        return tab_div


class BootstrapPortalTopNavWdg(BootstrapTopNavWdg):

    def get_logo_div(self):
        from tactic_client_lib import TACTIC

        server = TACTIC.get()
        plugin_path = server.get_plugin_dir("spt/modules/portal/user_project")
        portal_logo_path = "%s/media/portal-logo.png" % plugin_path

        brand_div = DivWdg()
        brand_div.add_class("spt_logo")
       
        palette = Palette()

        brand_div.add("""<a><img src="%s"/></a>""" % portal_logo_path)

        style = HtmlElement.style("""
            .spt_bs_top_nav .spt_logo {
                display: flex;
                align-items: center;
            }

            .spt_bs_top_nav .spt_logo img { 
                height: 16px;
            }
        """)
        brand_div.add(style)
        
        return brand_div
    

    def get_left_wdg(self):
        style = HtmlElement.style('''
        .spt_portal_header_btn_div {
            display: flex;
            align-items: center;
            margin-left: 10px;
        }

        @media (max-width: 550px) {
            .spt_portal_header_left_top {
                display: none !important;
            }
        }
        ''')
        left_wdg = DivWdg()
        left_wdg.add(style)
        left_wdg.add_class("spt_portal_header_left_top d-flex")

        
        # start_div.add("<div>Start New Project</div>")

        invite_div = DivWdg()
        invite_div.add_class("spt_portal_header_btn_div")
        left_wdg.add(invite_div)

        invite_btn = ButtonNewWdg(
            icon="FA_USER_PLUS",
            title="Invite Members",
            btn_class="btn bmd-btn-icon",
            opacity="1.0",
        )

        invite_btn.add_class("ml-1 spt_nav_icon")
        invite_div.add_attr("value", "Invite")
        invite_div.add_attr("target", "spt_header_top.spt_home_content")
        invite_div.add_attr("view", "user.site.members")
        invite_div.add_class("tactic_load")
        
        
        invite_div.add(invite_btn)
        # invite_div.add("<div>Invite Members</div>")

        roles_div = DivWdg()
        roles_div.add_class("spt_portal_header_btn_div")
        left_wdg.add(roles_div)

        roles_btn = ButtonNewWdg(
            icon="FA_USERS_COG",
            title="Assign Roles",
            btn_class="btn bmd-btn-icon",
            opacity="1.0",
        )

        roles_btn.add_class("ml-1 spt_nav_icon")
        roles_div.add_attr("value", "Collaborate")
        roles_div.add_attr("target", "spt_header_top.spt_home_content")
        roles_div.add_attr("view", "user.project.list")
        roles_div.add_class("tactic_load")
        
        roles_div.add(roles_btn)
        # roles_div.add("<div>Assign Roles</div>")
        

        return left_wdg
    

    def get_right_wdg(self):
        style = HtmlElement.style('''
            .spt_bell_orange_dot{
                width: 12px;
                height: 12px;
                border-radius:50%;
                background-color: #000;
                margin-left:-8px;
                margin-top:-20px;
                font-size: 9px;
                color: black;
            }

            .spt_invite_update {
                text-align: center;
                margin-top: 0px;
                margin-left: 0px;
                width: 100%;
                font-weight: bold;
            }

            .spt_bell_icon{
                font-size: 1.5em;
                margin-top: -5px;
                margin-right: 10px;
                -webkit-transform: rotate(-20deg); 
                -moz-transform: rotate(-20deg);  
                filter: progid:DXImageTransform.Microsoft.BasicImage(rotation=5); /*for IE*/
                -o-transform: rotate(-20deg);
            }
        ''')

        right_wdg = DivWdg()
        right_wdg.add(style)
        right_wdg.add_class("d-flex")
        right_wdg.add_style("align-items", "center")

        from pyasm.search import Search

        invite_count = Search.eval("@COUNT(portal/invite['login',$LOGIN]['status','pending']['type','site'])")

        start_div = DivWdg()
        start_div.add_class("spt_portal_header_btn_div")

        start_btn = ButtonNewWdg(
            icon="FA_FOLDER_PLUS",
            title="Start New Project",
            title2="Start New Project",
            btn_class="btn bmd-btn-icon",
            opacity="1.0",
        )

        start_btn.add_class("ml-1 spt_nav_icon")
        start_div.add_attr("value", "Start")
        start_div.add_attr("target", "spt_header_top.spt_home_content")
        start_div.add_attr("view", "user.project.select_product")
        start_div.add_class("tactic_load")

        start_div.add(start_btn)

        right_wdg.add(start_div)

        load_div = DivWdg()
        load_div.add_class("tactic_load")
        load_div.add_attr("target", "spt_header_top.spt_home_content")
        load_div.add_attr("view", "user.invite.list")
        load_div.add('<i class="fas fa-bell spt_bell_icon"></i>')
        badge_div = DivWdg()
        load_div.add(badge_div)
        badge_div.add_class("spt_bell_orange_dot")
        count_div = DivWdg(invite_count)
        count_div.add_class("spt_invite_update")
        count_div.add_behavior({
            "type": "load",
            "cbjs_action": '''
                if (parseInt(bvr.src_el.innerHTML, 10) > 0)
                bvr.src_el.getParent().setStyle('background', '#f59d1f');
                spt.update.add( bvr.src_el, {
                    expression: "@COUNT(portal/invite['login',$LOGIN]['status','pending']['type','site'])",
                    cbjs_action: "var count = bvr.value; var parent = bvr.src_el.getParent(); if (count > 0) {  parent.setStyle('background', '#f59d1f');} else { count = ''; parent.setStyle('background','transparent');} bvr.src_el.innerHTML = count; ",
                    interval: 3
                } );
            '''
        })
        badge_div.add(count_div)

        load_div.add_class("ml-1 spt_nav_icon")

        right_wdg.add(load_div)

        user_wdg = self.get_user_wdg()
        right_wdg.add(user_wdg)
        
        return right_wdg


    def get_user_wdg(self):
        styles = HtmlElement.style('''
            .spt_header_top {
                color: var(--spt_palette_color3);
            }

            .spt_header_menu_top{
                position: absolute;
                display: none; 
                z-index: 100; 
                font-size: 12px; 
                width: 175px; 
                top: 10px; 
                right: 20px; 
                color: #000; 
                text-align: center;
                margin-top: -4px;
            }

            .spt_popup_pointer{
                margin-top:30px;
                z-index:10;
            }

            .spt_first_arrow_div{
                border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) #ddd;
                top: -15px;
                z-index: 1;
                border-width: 0 15px 15px;
                height: 0;
                width: 0;
                border-style: dashed dashed solid;
                margin-top: 30px;
                margin-left: 95px;
                left: 15px;
            }

            .spt_second_arrow_div{
                border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) #fff;
                z-index: 1;
                border-width: 0 15px 15px;
                height: 0;
                width: 0;
                border-style: dashed dashed solid;
                margin-top: -14px;
                margin-left: 95px;
                position: absolute;
            }


            .spt_drop_down_cell{
                border: solid 1px #ddd;
                background-color:#fff;
                padding: 10px;
            }

            .spt_drop_down_cell:hover{
                background-color:#eee;
            }

            .spt_portal_header_user_top {
                display: flex;
                align-items: center;
            }

            @media (max-width: 600px) {
                .spt_portal_header_user_top .spt_user_name {
                    display: none;
                }
            }
        ''')

        user_wdg = DivWdg()
        user_wdg.add(styles)
        user_wdg.add_class("spt_portal_header_user_top")

        login = Environment.get_login()
        display_name = login.get_full_name()
        if not display_name:
            display_name = login.get_login()
       
        from pyasm.biz import Snapshot
        snapshot = Snapshot.get_latest_by_sobject(login)
        if snapshot:
            path = snapshot.get_web_path_by_type()
 
            user_wdg.add(HtmlElement.style("""
                .spt_hit_wdg.spt_nav_user_btn {                
                    background-image: url(%s);
                    background-size: cover;
                    background-repeat: no-repeat;
                } 
            """ % path))

            icon = "FA_USERX"
        else:
            icon = "FA_USER"

        title = "Logged in as %s" % display_name
        
        btn_class = "btn bmd-btn-icon"
        user_btn = ButtonNewWdg(
            icon=icon, 
            title=title, 
            btn_class=btn_class,
            opacity="1.0"
        )

        user_btn.add_behavior({
            "type": "click", 
            "cbjs_action": '''
                var el = document.id(document.body).getElement(".spt_header_menu_top");
                el.setStyle("display", "block");
                spt.body.add_focus_element(el);
            '''
        })

        
        user_wdg.add(user_btn)
        name_wdg = DivWdg(display_name)
        name_wdg.add_class("spt_user_name")
        user_wdg.add(name_wdg)

        user_btn.add_class("ml-1 spt_nav_user_btn spt_nav_icon")
        user_btn.get_collapsible_wdg().add_class("dropdown-toggle")

        user_wdg.add(user_btn)
        user_btn.add_class("ml-1 spt_nav_user_btn spt_nav_icon")

        user_menu = DivWdg()
        user_menu.add_class("spt_header_menu_top")

        menu_pointer = DivWdg()
        menu_pointer.add_class("spt_popup_pointer")

        left_pointer = DivWdg()
        left_pointer.add_class("spt_first_arrow_div")
        menu_pointer.add(left_pointer)
        right_pointer = DivWdg()
        right_pointer.add_class("spt_second_arrow_div")
        menu_pointer.add(right_pointer)

        user_menu.add(menu_pointer)


        menu_option1 = DivWdg("Dashboard")
        menu_option1.add_class("hand tactic_load spt_drop_down_cell tactic_load")
        menu_option1.add_attr("target", "spt_header_top.spt_home_content")
        menu_option1.add_attr("view", "user.home.dashboard")
        user_menu.add(menu_option1)

        menu_option2 = DivWdg("My Profile")
        menu_option2.add_class("hand tactic_load spt_drop_down_cell tactic_load")
        menu_option2.add_attr("target", "spt_header_top.spt_home_content")
        menu_option2.add_attr("view", "user.profile.main")
        user_menu.add(menu_option2)

        menu_option3 = DivWdg("Generate API Keys")
        menu_option3.add_class("hand tactic_load spt_drop_down_cell tactic_load")
        menu_option3.add_attr("target", "spt_header_top.spt_home_content")
        menu_option3.add_attr("view", "user.api.main")
        user_menu.add(menu_option3)

        menu_option4 = DivWdg("Sign Out")
        menu_option4.add_class("hand sign_out spt_drop_down_cell")
        data = {"login": display_name}
        menu_option4.generate_command_key("SignOutCmd", data)
        menu_option4.add_behavior({
            'type': 'click',
            'cbjs_action': '''
                var ok = function() {
                    var server = TacticServerStub.get();
                    var cmd_key = bvr.src_el.getAttribute("SPT_CMD_KEY");
                    server.execute_cmd(cmd_key);
                    var href = document.location.href;
                    var parts = href.split("#");
                    window.location.href=parts[0] + "default/user/sign_in";
                }
                spt.confirm("Are you sure you wish to sign out?", ok );
            '''
        })
        user_menu.add(menu_option4)

        user_wdg.add(user_menu)

        
        return user_wdg



class BootstrapIndexWdg(PageNavContainerWdg):
  
    def _get_tab_save_state(self):
        return "main_body_tab_state"

    def _get_top_nav_xml(self):
        return """
        <element name="top_nav">
              <display class="tactic.ui.bootstrap_app.BootstrapTopNavWdg">
              </display>
        </element>"""


    def _get_left_nav_xml(self):
         return """
         <element name="left_nav">
           <display class="tactic.ui.bootstrap_app.BootstrapSideBarPanelWdg">
           </display>
         </element> """

    def _get_startup_xml(self):
        security = Environment.get_security()
        start_link = security.get_start_link()
        if start_link:
            return """
                <element name="Startup">
                    <display class="tactic.ui.panel.HashPanelWdg">
                        <hash>%s</hash>
                    </display>
                </element>
            """ % start_link
        


        #start_view = "vfx.home.main"
        start_view = ""
        if start_view:
            return """
                <element name="Startup">
                    <display class="tactic.ui.panel.CustomLayoutWdg">
                        <view>%s</view>
                    </display>
                </element>
            """ % start_view


        is_admin = False
        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            is_admin = True

        if is_admin:
            return """
                <element name="Startup">
                  <display class="tactic.ui.startup.MainWdg"/>
                  <web/>
                </element>
            """
        else:
            # FIXME: add a default widget for non-admin users
            return ""



    def init(self):

        link = self.kwargs.get('link')
        hash = self.kwargs.get('hash')
        
        self.widget = None
        config = None

        if link:
            from tactic.ui.panel import SideBarBookmarkMenuWdg
            personal = False
            if '.' in link:
                personal = True

            config = SideBarBookmarkMenuWdg.get_config("SideBarWdg", link, personal=personal)
            options = config.get_display_options(link)
            title = config.get_element_title(link)
            if not title:
                attr_dict = config.get_element_attributes(link)
                title = attr_dict.get('title')

            hash = "/tab/%s" % link

        if hash:
            from tactic.ui.panel import HashPanelWdg
            self.widget = HashPanelWdg.get_widget_from_hash(hash, force_no_index=True)
        else:
            from pyasm.search import Search
            search = Search("config/widget_config")
            search.add_filter("category", "top_layout")
            search.add_filter("view", "welcome")
            config_sobj = search.get_sobject()
            if config_sobj:
                config = config_sobj.get_value("config")
            
        if not config:
            # get start link from default config
            config = self.get_default_config()
        
        from pyasm.common import Xml
        self.config_xml = Xml()
        self.config_xml.read_string(config)
 
        """
        if not self.widget:
            config = WidgetConfig.get(xml=self.config_xml, view="application")
            main_body_handler = config.get_display_handler("main_body")
            main_body_options = config.get_display_options("main_body")
            element_name = main_body_options.get("element_name")
            title = main_body_options.get("title")
            main_body_content = Common.create_from_class_path(main_body_handler, [], main_body_options)
            main_body_values = config.get_web_options("main_body")
            web = WebContainer.get_web()
            if isinstance(main_body_values, dict):
                for name, value in main_body_values.items():
                    web.set_form_value(name, value)
            main_body_content.set_name(element_name)

            self.widget = main_body_content
        """
 

    def get_default_config(self):
        use_sidebar = self.kwargs.get('use_sidebar')
        if use_sidebar==False:
            config = '''
            <config>
                <application>
                    %s
                    %s
                </application>
            </config>
            ''' % (self._get_top_nav_xml(), _get_startup_xml())
        else:
            config = '''
            <config>
                <application>
                    %s
                    %s
                    %s
                </application>
            </config>
            ''' % (self._get_top_nav_xml(), self._get_left_nav_xml(), self._get_startup_xml())

        return config




    def get_bootstrap_styles(self):

        # Declare CSS variables
        palette = Palette.get()
        keys = palette.get_keys()
        
        css_vars = ""
        for key in keys:
            value = palette.color(key)
            css_vars += "--spt_palette_%s: %s;" % (key, value)

        css_vars += "--left_modal_width: 300px;"
        style = ":root {%s}" % css_vars
        
        style += """
            body {overflow: hidden;}
            
            .spt_bootstrap_top {
                overflow: hidden;
                height: 100vh;
            }

            .spt_bs_content {
                width: 100vw;
                transition: all 0.3s;
            }

            @media (min-width: 576px) {

                .spt_bs_content {
                    padding-top: 40px
                }

                .spt_bs_top_nav {
                    height: 40px;
                }

                .spt_bs_top_nav.navbar {
                    padding: 0rem 1rem;
                }

                .spt_bs_top_nav_content {
                    display: none !important;
                }


            }
            
            @media (max-width: 575.98px) {

                .spt_bs_content {
                    padding-top: 49px;
                }
                
            }

            .spt_hit_wdg.spt_nav_icon {
                color: var(--spt_palette_side_bar_title_color) !important;
            }

            """


        return HtmlElement.style(style) 


    def get_onload_js(self):
        return ""


    def get_display(self):
        
        is_admin_project = Project.get().is_admin()
        security = Environment.get_security()
        if is_admin_project and not security.check_access("builtin", "view_site_admin", "allow"):
            from pyasm.widget import Error403Wdg
            return Error403Wdg()
        
        top = self.top
        top.add_class("d-flex")
        top.add_class("spt_bootstrap_top")

        top.add(self.get_bootstrap_styles())            

        view_side_bar = security.check_access("builtin", "view_side_bar", "allow", default='allow')
        if view_side_bar:
            config = WidgetConfig.get(xml=self.config_xml, view="application")
            left_nav_handler = config.get_display_handler("left_nav")
            left_nav_options = config.get_display_options("left_nav")
            if left_nav_handler:
                left_nav_wdg = Common.create_from_class_path(left_nav_handler, [], left_nav_options)
                # caching
                side_bar_cache = self.get_side_bar_cache(left_nav_wdg)
                
                top.add_class("spt_view_side_bar")
                top.add(left_nav_wdg)
                
                sidebar_overlay = DivWdg()
                top.add(sidebar_overlay)
                sidebar_overlay.set_id("side_bar_overlay")
                sidebar_overlay.add_class("spt_bs_left_sidebar_overlay")
                sidebar_overlay.add_behavior({ 
                    'type': 'click',
                    'cbjs_action': '''spt.side_bar.toggle();'''
                })

            else:
                view_side_bar = False
        

        self.view_side_bar = view_side_bar

        content_wdg = self.get_content_wdg()
        top.add(content_wdg)

        top.add_behavior( {                                                                      
            "type": "load",
            "cbjs_action": '''
                window.onresize = function() {
                    spt.named_events.fire_event("window_resize");
                }
        '''})

        top.add_behavior( {
            "type": "load",
            "cbjs_action": self.get_onload_js()
        })

        
        return top


    def get_content_wdg(self):
        main_body_panel = DivWdg()
        main_body_panel.set_id("main_body")
        main_body_panel.add_class("spt_main_panel")
        main_body_panel.add_class("spt_bs_content")

        # add the content to the main body panel
        try:
            startup_xml = """
            <config>
                <tab>
                    %s
                </tab>
            </config>
            """ % self._get_startup_xml()

            # Sets default xml when no WidgetSetting exists
            save_state = self._get_tab_save_state()
            tab = BootstrapTabWdg(config_xml=startup_xml, save_state=save_state)
            
            # Hash is additive
            if self.widget:
                tab.add(self.widget)


            """
            main_body_panel.add_behavior( {
                'type': 'load',
                'element_name': element_name,
                'cbjs_action': '''
                if (spt.help)
                    spt.help.set_view(bvr.element_name);
                '''
            } )
            """

        except Exception as e:
            print(e)
            # handle an error in the drawing
            buffer = self.get_buffer_on_exception()
            error_wdg = self.handle_exception(e)
            main_body_content = DivWdg()
            main_body_content.add(error_wdg)
            main_body_content = main_body_content.get_buffer_display()
            tab = BootstrapTabWdg()
            tab.add(main_body_content, "error", "Error")
        
        
        tab_id = tab.get_tab_id()
        config = WidgetConfig.get(xml=self.config_xml, view="application")
        top_nav_handler = config.get_display_handler("top_nav")
        top_nav_options = config.get_display_options("top_nav")
        top_nav_options['main_body_tab_id'] = tab_id
        top_nav_options['view_side_bar'] = self.view_side_bar
        top_nav_wdg = Common.create_from_class_path(top_nav_handler, [], top_nav_options)
        
        main_body_panel.add(top_nav_wdg)
        main_body_panel.add(tab)


        is_admin = False
        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            is_admin = True

        if is_admin:
            from tactic.ui.app.quick_box_wdg import QuickBoxWdg
            quick_box = QuickBoxWdg()
            main_body_panel.add(quick_box)


        # TEST for Bootstrap Modal 
        modal_container = DivWdg()
        modal_container.add("""
<!-- The Modal -->
  <div class="modal fade right" id="myModal">
    <div class="modal-dialog modal-side modal-top-right">
      <div class="modal-content">
      
        <!-- Modal Header -->
        <div class="modal-header">
          <h4 class="modal-title">Modal Heading</h4>
          <button type="button" class="close" data-dismiss="modal">&times;</button>
        </div>
        
        <!-- Modal body -->
        <div class="modal-body">
          Modal body..
        </div>
        
        <!-- Modal footer -->
        <div class="modal-footer">
          <button type="button" class="btn btn-danger" data-dismiss="modal">Close</button>
        </div>
        
      </div>
    </div>
  </div>""")
        main_body_panel.add(modal_container)

 
        return main_body_panel



class BootstrapPortalIndexWdg(BootstrapIndexWdg):
    def _get_top_nav_xml(self):
        return """
        <element name="top_nav">
              <display class="tactic.ui.bootstrap_app.BootstrapPortalTopNavWdg">
              </display>
        </element>"""
    
    def _get_tab_save_state(self):
        return "portal_tab_state"
    
    def _get_startup_xml(self):

         return """
            <element name="main_body">
                <display class="tactic.ui.panel.CustomLayoutWdg">
                    <view>spt02_theme.tabs</view>
                </display>
            </element>
         """
    
    def get_content_wdg(self):
        from tactic.ui.panel import CustomLayoutWdg

        main_body_panel = DivWdg()
        main_body_panel.set_id("main_body")
        main_body_panel.add_class("spt_main_panel")
        main_body_panel.add_class("spt_bs_content")

        config = WidgetConfig.get(xml=self.config_xml, view="application")
        top_nav_handler = config.get_display_handler("top_nav")
        top_nav_options = config.get_display_options("top_nav")
        top_nav_options['view_side_bar'] = self.view_side_bar
        top_nav_wdg = Common.create_from_class_path(top_nav_handler, [], top_nav_options)

        main_body_panel.add(top_nav_wdg)


        custom_layout_div = CustomLayoutWdg(view="spt02_theme.tabs")
        footer = CustomLayoutWdg(view="spt02_theme.footer", name="web_footer")
        footer.add_style("position", "fixed")
        footer.add_style("bottom", "0px")
        footer.add_style("width", "100%")

        main_body_panel.add(custom_layout_div)
        main_body_panel.add(footer)

        return main_body_panel
    


from tactic.ui.widget import PageHeaderGearMenuWdg
class BootstrapIndexGearMenuWdg(PageHeaderGearMenuWdg):

    def get_display(self):

        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            menus = [ self.get_main_menu(), self.get_add_menu(), self.get_edit_menu(), self.get_tools_menu(), self.get_help_menu() ]
        else:
            menus = [ self.get_main_menu(), self.get_edit_menu(), self.get_help_menu() ]

        btn_class = "btn bmd-btn-icon"
        btn = ButtonNewWdg(
            icon="FA_COG", 
            title="Global Options", 
            btn_class=btn_class,
            opacity="1.0",
        )
        btn.add_class("ml-1 spt_nav_icon")
        
        smenu_set = SmartMenu.add_smart_menu_set( btn.get_button_wdg(), { 'DG_TABLE_GEAR_MENU': menus } )
        SmartMenu.assign_as_local_activator( btn.get_button_wdg(), "DG_TABLE_GEAR_MENU", True )
        
        smenu_set = SmartMenu.add_smart_menu_set( btn.get_collapsible_wdg(), { 'DG_TABLE_GEAR_MENU': menus } )
        SmartMenu.assign_as_local_activator( btn.get_collapsible_wdg(), "DG_TABLE_GEAR_MENU", True )
        
        return btn




class BootstrapProjectSelectWdg(ProjectSelectWdg):


    def get_activator(self, menus):

        project = Project.get()
        activator = ActionButtonWdg(title=project.get_value("title"), btn_class = "btn")
        activator.add_class("dropdown-toggle")
        activator.button_wdg.add_class("spt_nav_icon")

        #HACK
        activator.button_wdg.add_style("margin-bottom: unset")
        
        smenu_set = SmartMenu.add_smart_menu_set( activator.get_button_wdg(), { 'BUTTON_MENU': menus } )
        SmartMenu.assign_as_local_activator( activator.get_button_wdg(), "BUTTON_MENU", True )
        
        smenu_set = SmartMenu.add_smart_menu_set( activator.get_collapsible_wdg(), { 'BUTTON_MENU': menus } )
        SmartMenu.assign_as_local_activator( activator.get_collapsible_wdg(), "BUTTON_MENU", True )
        
        
        
        return activator

