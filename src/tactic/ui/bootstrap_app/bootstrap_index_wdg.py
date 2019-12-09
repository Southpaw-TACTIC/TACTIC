import six

from pyasm.biz import Project
from pyasm.common import Environment, Common
from pyasm.web import HtmlElement, DivWdg, WebContainer, SpanWdg
from pyasm.widget import WidgetConfig

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ButtonNewWdg
from tactic.ui.app import PageHeaderWdg, PageNavContainerWdg
from tactic.ui.container import SmartMenu

from .bootstrap_tab_wdg import *


__all__ = ['BootstrapIndexWdg', 'BootstrapIndexPage']


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
        section_div.set_id("sidebar")
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
                if view_item.startswith("self_view_"):
                    tt = "My Views"
                else:
                    tt = view_item.replace("_", " ");
                tt = tt.capitalize()

            title_label = HtmlElement("a")
            title_label.add_class("nav-link")
            title.add( title_label )
            title_label.add("""<h6>%s</h6>""" % tt)

            content_div.add( title )
            if sortable:
                title.add_behavior({'type': 'click_up',
                    'cbjs_action': "spt.panel.refresh('ManageSideBarBookmark_%s')" % view_item});
            info = { 'counter' : 10, 'view': view_item, 'level': 1 }

            ret_val = self.generate_section( config, content_div, info, personal=is_personal )
            if ret_val == 'empty':
                title.add_style("display: none")

            """
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
        
        
        s_content_div = HtmlElement.ul()
        s_content_div.add_class("list-unstyled collapse")
        content_id = s_content_div.set_unique_id()
        s_link_div.set_attr("href", "#%s" % content_id)

        """
        # add an icon if applicable
        icon = attributes.get("icon")
        if icon:
            icon = icon.upper()
            from pyasm.widget import IconWdg
            try:
                icon_wdg =  IconWdg(title, eval("IconWdg.%s" % icon) )
                s_link_div.add(icon_wdg)
            except:
                pass
        """

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

        """
        # add an icon
        icon = attributes.get("icon")
        if not icon:
            icon = "VIEW"

        if icon:
            icon = icon.upper()
            from pyasm.widget import IconWdg
            try:
                span.add( IconWdg(title, eval("IconWdg.%s" % icon) ) )
            except:
                pass
        """

        span.add(title)
        link_wdg.add(span)


        self.add_link_behavior(link_wdg, element_name, config, options)


        return link_wdg



class BootstrapSideBarPanelWdg(SideBarPanelWdg):

    def get_bootstrap_styles(self):
        style = HtmlElement.style("""

/*
    DEMO STYLE
*/

/* -------------------------------------------------
    GLOBAL OVERRIDES
---------------------------------------------------*/

body {
    overflow-y: hidden;
}

.bg-spt-blue {
    background: #114e8a
}

.bg-spt-blue-fade {
    background: linear-gradient(0deg, #629bd3 40%, #114e8a 80%);
}

.nav-pills .nav-link, .nav-tabs .nav-link {
    padding: .5em .8575em;
    font-size: 12px;
    height: 40px;
}

.spt_tab_selected {
    border-bottom: solid .214rem #114e8a;
    height: 40px;
}

.nav-tabs .spt_tab_selected .nav-link {
    color: rgba(0,0,0,.87);
}


/* ---------------------------------------------------
    SIDEBAR STYLE
----------------------------------------------------- */
.spt_bs_left_sidebar a, a:hover, a:focus {
    color: inherit;
    text-decoration: none;
    transition: all 0.3s;
}

.spt_bs_left_sidebar {
    min-width: 175px;
    max-width: 175px;
    color: #fff;
    transition: all 0.3s;
    z-index: 1;
    border: 0;
    border-radius: 0;
    box-shadow: 0 2px 2px 0 rgba(0,0,0,.14), 0 3px 1px -2px rgba(0,0,0,.2), 0 1px 5px 0 rgba(0,0,0,.12);
    padding-top: 40px;
    height: 100vh;
}

.spt_bs_left_sidebar.active {
    min-width: 80px;
    max-width: 80px;
    text-align: center;
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
    margin-right: 0;
    display: block;
    font-size: 1.8em;
    margin-bottom: 5px;
}

.spt_bs_left_sidebar.active ul ul a {
    padding: 10px !important;
}

.spt_bs_left_sidebar.active .dropdown-toggle::after {
    top: auto;
    bottom: 10px;
    right: 50%;
    -webkit-transform: translateX(50%);
    -ms-transform: translateX(50%);
    transform: translateX(50%);
}

.spt_bs_left_sidebar .spt_logo {
    margin: 10px auto;
}

.spt_bs_left_sidebar .spt_toggle_sidebar {
    margin: 10px auto;
}

.spt_bs_left_sidebar.active .sidebar-header .spt_logo {
    display: none;
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
    color: #114e8a;
    background: #fff;
}

.spt_bs_left_sidebar ul li a i {
    margin-right: 10px;
}

.spt_bs_left_sidebar ul li.active>a, a[aria-expanded="true"] {
    color: #fff;
    background: #114e8a;
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

.spt_bs_left_sidebar ul ul a {
    font-size: 0.9em !important;
    padding-left: 20px !important;
    background: #114e8a;
}

.spt_bs_left_sidebar ul ul .dropdown-divider {
    margin: 0rem 0rem;
    padding: .5rem 0rem;
    background: #114e8a;
}


.spt_bs_left_sidebar ul ul ul a {
    font-size: 0.9em !important;
    padding-left: 40px !important;
    background: #0d355c;
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

.spt_bs_left_sidebar a.download {
    background: #fff;
    color: #7386D5;
}

.spt_bs_left_sidebar a.article, a.article:hover {
    background: #6d7fcc !important;
    color: #fff !important;
}

/* ---------------------------------------------------
    CONTENT STYLE
----------------------------------------------------- */

.spt_bootstrap_top {
    overflow: hidden;
    width: 100vw;
    height: 100vh;
}

.spt_bs_content {
    transition: all 0.3s;
}

/* ---------------------------------------------------
    MEDIAQUERIES
----------------------------------------------------- */

.spt_tab_content_top {
    overflow-y: auto;
}

@media (min-width: 575.98px) {

    .spt_bootstrap_top .spt_bs_content {
        width: calc(100vw - 175px);
    }
    
    .spt_bootstrap_top.spt_sidebar_collapse .spt_bs_content {
        width: calc(100vw - 80px);
    }

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

    .spt_tab_content_top {
        height: calc(100vh - 80px);
    }

    .navbar-toggler {
        font-size: 1rem;
        margin: .25rem 0rem;
    }
    
    .spt_toggle_sidebar {
        justify-items: center;
        display: flex;
    }


}


@media (max-width: 768px) {
  
    .spt_bootstrap_top .spt_bs_content {
        width: 100vw;
    }

    .spt_bootstrap_top.spt_sidebar_collapse .spt_bs_content {
        width: calc(100vw - 80px);
    }

    .spt_bs_left_sidebar {
        min-width: 80px;
        max-width: 80px;
        text-align: center;
        margin-left: -80px !important;
    }

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
    
    .spt_bs_content {
        padding-top: 56px;
    }
    
    .spt_tab_content_top {
        height: calc(100vh - 56px);
    }
    
    .spt_bootstrap_top .spt_bs_content {
        width: 100vw;
    }

    .spt_bootstrap_top.spt_sidebar_collapse .spt_bs_content {
        width: 100vw;
    }

}

        """)


        return style

    def get_subdisplay(self, views):

        div = DivWdg()
        div.add_class("bg-spt-blue-fade")
        div.add_class("spt_bs_left_sidebar")
        div.set_attr('spt_class_name', Common.get_full_class_name(self))
        div.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
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
        div.add(down)


        outer_div = DivWdg()
       
        div.add(outer_div)
        
        inner_div = DivWdg()
        inner_div.set_id("side_bar_scroll")
        outer_div.add(inner_div)

        behavior = {
            'type': 'wheel',
            'cbjs_action': 'spt.side_bar.scroll(evt,bvr)',
        }
        inner_div.add_behavior(behavior)

        styles = self.get_bootstrap_styles()
        inner_div.add(styles)

        inner_div.add( self.get_bookmark_menu_wdg("", None, views) )
        inner_div.add(HtmlElement.br())

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

            .spt_bs_top_nav .spt_logo img { 
                width: 10em;
                filter: invert(100%);
                margin: .5rem 1rem;
            }

            // Copy navbar-nav styles
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
                max-height: 100vh;
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

        top_nav_wdg.add_class("spt_bs_top_nav navbar navbar-dark fixed-top bg-spt-blue")
        
        nav_header = DivWdg()
        top_nav_wdg.add(nav_header)
        nav_header.add_class("d-flex")


        toggle_div = DivWdg()
        nav_header.add(toggle_div)
        toggle_div.add_class("spt_toggle_sidebar")

        toggle_div.add("""
        <button class="navbar-toggler collapsed" type="button" data-toggle="collapse" data-target="#navbarCollapse" 
             aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"> </span>
        </button>""")
      
        toggle_div.add_behavior({
            'type': 'click',
            'cbjs_action': """
                var app_top = bvr.src_el.getParent(".spt_bootstrap_top");
                app_top.toggleClass("spt_sidebar_collapse")
                
                var sidebar = app_top.getElement(".spt_bs_left_sidebar");
                sidebar.toggleClass("active");

            """
        })

        toggle_div.add_behavior( {
            'type': 'listen',
            'event_name': 'side_bar|toggle',
            'cbjs_action': '''
            var app_top = bvr.src_el.getParent(".spt_bootstrap_top");
            app_top.toggleClass("spt_sidebar_collapse")
            
            var sidebar = app_top.getElement(".spt_bs_left_sidebar");
            sidebar.toggleClass("active");
            '''
        } )

        
        brand_div = DivWdg()
        nav_header.add(brand_div)
        brand_div.add_class("spt_logo")
        brand_div.add("""
        <a>
            <img src="/tactic/plugins/community/theme/media/TACTIC_logo.svg"> 
        </a>""")
       
        right_wdg = self.get_right_wdg()
        top_nav_wdg.add(right_wdg)

        hidden_nav = DivWdg()
        hidden_nav.add_class("spt_bs_top_nav_content")
        hidden_nav.add_class("collapse")
        hidden_nav.add_class("navbar-collapse")
        hidden_nav.set_id("navbarCollapse")
        
        hidden_nav.add_behavior({
            'type': 'load',
            'cbjs_action': '''
                var app_top = bvr.src_el.getParent(".spt_bootstrap_top");
                var left_sidebar = app_top.getElement(".spt_bs_left_sidebar"); 
                var sidebar_content = left_sidebar.getElement(".spt_side_bar_content");
                var mobile_sidebar = spt.behavior.clone(sidebar_content);

                //FIX IDs since Bootstrap menus use IDs to target collapsing menus
                var section_els = mobile_sidebar.getElements(".spt_side_bar_section");
                var ID = function () {
                  return '_' + Math.random().toString(36).substr(2, 9);
                };
                handle_section = function(section_el) {
                   var toggle = section_el.getElement(".spt_side_bar_section_link");
                   var dropdown = section_el.getElement(".spt_side_bar_section_content");
                   
                   var new_id = ID();
                   toggle.setAttribute("href", "#" + new_id);
                   dropdown.setAttribute("id", new_id);
                }
                section_els.forEach(handle_section);

                mobile_sidebar.inject(bvr.src_el);
            '''
        })

        top_nav_wdg.add(hidden_nav)

        return top_nav_wdg

    def get_right_wdg(self):
        right_wdg = DivWdg()
        right_wdg.add_class("d-flex")

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
                .spt_nav_user_btn {                
                    background-image: url(%s);
                    background-size: cover;
                    background-repeat: no-repeat;
                } 
            """ % path))

            icon = "FA_USERX"
        else:
            icon = "FA_USER"

        title = "Logged in as %s" % display_name
        user_btn = ButtonNewWdg(title=title, icon=icon)
        user_wdg.add(user_btn)
        user_btn.add_class("bg-light ml-1 spt_nav_user_btn")
        
        menus = self.get_smart_menu()
        SmartMenu.add_smart_menu_set(user_wdg, [menus])
        SmartMenu.assign_as_local_activator(user_wdg, None, True)

        
        return user_wdg

    def get_tab_manager(self):


        tab_div = DivWdg()
        tab_div.add_class("spt_mobile_tab_manager")
        tab_div.add_class("dropdown d-block d-sm-none")

        tab_btn = ButtonNewWdg(title="View tabs", icon="FA_CLONE")
        tab_div.add(tab_btn)

        tab_btn.add_class("dropdown-toggle")
        tab_btn.add_class("bg-light")
        tab_btn.add_class("ml-1")
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

        
        # HACK
        tab_menu.add_style("position", "absolute")
        tab_menu.add_style("left", "-152px")

        return tab_div


class BootstrapIndexWdg(PageNavContainerWdg):

    def get_display(self):
        
        is_admin_project = Project.get().is_admin()
        security = Environment.get_security()
        if is_admin_project and not security.check_access("builtin", "view_site_admin", "allow"):
            from pyasm.widget import Error403Wdg
            return Error403Wdg()

        """
        TODO: This logic must be considered in BootstrapSidebarPanelWdg
        TODO: If user cannot view_side_bar, then do not template sidebar into view. 
        TODO: Add listener for sidebar hide and show events. 
        config = WidgetConfig.get(xml=self.config_xml, view="application")
        left_nav_handler = config.get_display_handler("left_nav")
        left_nav_options = config.get_display_options("left_nav")

        view_side_bar = None
        if left_nav_handler:
            left_nav_wdg = Common.create_from_class_path(left_nav_handler, [], left_nav_options)

            # caching
            side_bar_cache = self.get_side_bar_cache(left_nav_wdg)
        else:
            view_side_bar = False
        
        if view_side_bar == None:
            view_side_bar = security.check_access("builtin", "view_side_bar", "allow", default='allow')

        """
        
        
        top = self.top
        top.add_class("d-flex")
        top.add_class("spt_bootstrap_top")

        
                

        sidebar_wdg = BootstrapSideBarPanelWdg()
        top.add(sidebar_wdg)

        content_wdg = self.get_content_wdg()
        top.add(content_wdg)
        
        
        return top

    def get_content_wdg(self):
        main_body_panel = DivWdg()
        main_body_panel.set_id("main_body")
        main_body_panel.add_class("spt_main_panel")
        main_body_panel.add_class("spt_bs_content")

        tab = BootstrapTabWdg()
        tab_id = tab.get_tab_id()
        
        top_nav_wdg = BootstrapTopNavWdg(main_body_tab_id=tab_id)
        
        main_body_panel.add(top_nav_wdg)
        main_body_panel.add(tab)
        
        # add the content to the main body panel
        try:
            if self.widget:
                tab.add(self.widget)
                element_name = self.widget.get_name()
            else:
                config = WidgetConfig.get(xml=self.config_xml, view="application")
                main_body_handler = config.get_display_handler("main_body")
                main_body_options = config.get_display_options("main_body")
                element_name = main_body_options.get("element_name")
                title = main_body_options.get("title")

                main_body_content = Common.create_from_class_path(main_body_handler, [], main_body_options)
                # get the web values from top_layout
                main_body_values = config.get_web_options("main_body")
                web = WebContainer.get_web()
                if isinstance(main_body_values, dict):
                    for name, value in main_body_values.items():
                        web.set_form_value(name, value)

                main_body_content.set_name(element_name)
                tab.add(main_body_content, element_name, title)

                self.set_as_panel(main_body_panel, class_name=main_body_handler, kwargs=main_body_options)

            main_body_panel.add_behavior( {
                'type': 'load',
                'element_name': element_name,
                'cbjs_action': '''
                if (spt.help)
                    spt.help.set_view(bvr.element_name);
                '''
            } )

        except Exception as e:
            # handle an error in the drawing
            buffer = self.get_buffer_on_exception()
            error_wdg = self.handle_exception(e)
            main_body_content = DivWdg()
            main_body_content.add(error_wdg)
            main_body_content = main_body_content.get_buffer_display()
            tab.add(main_body_content, "error", title)


        # TODO: Fix the quick box.
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




class BootstrapIndexPage(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        from tactic.ui.panel import ViewPanelWdg
 
        wdg = ViewPanelWdg(search_type="config/widget_config", show_border=False)
        top.add(wdg)
        return top
