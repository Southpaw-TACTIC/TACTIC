
from pyasm.biz import Project
from pyasm.common import Environment, Common
from pyasm.web import HtmlElement, DivWdg
from pyasm.widget import WidgetConfig

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import IconButtonNewWdg

from tactic.ui.app.page_nav_container_wdg import PageNavContainerWdg

from .bootstrap_tab_wdg import *


__all__ = ['BootstrapIndexWdg', 'BootstrapIndexPage']

class BootstrapIndexWdg(PageNavContainerWdg):

    def get_display(self):
        
        top = self.top
        top.add_class("d-flex")
        top.add_class("spt_bootstrap_top")

        
        is_admin_project = Project.get().is_admin()
        security = Environment.get_security() 
        if is_admin_project and not security.check_access("builtin", "view_site_admin", "allow"):
            return Error403Wdg()
                

    
        sidebar_wdg = BootstrapSidebarPanelWdg()
        top.add(sidebar_wdg)

        content_wdg = self.get_content_wdg()
        top.add(content_wdg)
        
        
        return top

    def get_content_wdg(self):
        content_wdg = DivWdg()
        content_wdg.add_class("spt_bs_content")

        top_nav_wdg = BootstrapTopNavWdg()
        content_wdg.add(top_nav_wdg)

        tab = BootstrapTabWdg()
        tab.add(self.widget)
        content_wdg.add(tab)

        return content_wdg




class BootstrapTopNavWdg(BaseRefreshWdg):

    def get_styles(self):

        style = HtmlElement.style("""
.spt_bs_top_nav .spt_logo img { 
    width: 10em;
    filter: invert(100%);
    margin: .5rem 1rem;
}""")

        return style


    def get_display(self):
        
        top_nav_wdg =  HtmlElement("nav")
        
        styles = self.get_styles()
        top_nav_wdg.add(styles)

        top_nav_wdg.add_class("spt_bs_top_nav navbar navbar-dark fixed-top bg-dark")
        
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
                var sidebar = app_top.getElement(".spt_bs_left_sidebar");
                sidebar.toggleClass("active");
            """
        })
        
        brand_div = DivWdg()
        nav_header.add(brand_div)
        brand_div.add_class("spt_logo")
        brand_div.add("""
        <a>
            <img src="/tactic/plugins/community/theme/media/TACTIC_logo.svg"> 
        </a>""")
       
        right_wdg = self.get_right_wdg()
        top_nav_wdg.add(right_wdg)



        top_nav_wdg.add("""
        <div class="spt_bs_top_nav_content collapse navbar-collapse" id="navbarCollapse">
          <ul class="navbar-nav mr-auto">
            <li class="nav-item active">
              <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">Link</a>
            </li>
            <li class="nav-item">
              <a class="nav-link disabled" href="#">Disabled</a>
            </li>
          </ul>
          <form class="form-inline mt-2 mt-md-0">
            <input class="form-control mr-sm-2" type="text" placeholder="Search" aria-label="Search">
            <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
          </form>
        </div>
      """)
        return top_nav_wdg


    def get_right_wdg(self):
        right_wdg = DivWdg()

        button = IconButtonNewWdg(title="Show workflow info", icon="FA_USER")
        right_wdg.add(button)
        button.add_class("bg-light")

        return right_wdg



class BootstrapSidebarPanelWdg(BaseRefreshWdg):

    def get_styles(self):
        style = HtmlElement.style("""

/*
    DEMO STYLE
*/

.spt_bs_left_sidebar a, a:hover, a:focus {
    color: inherit;
    text-decoration: none;
    transition: all 0.3s;
}

/* ---------------------------------------------------
    SIDEBAR STYLE
----------------------------------------------------- */

.spt_bs_left_sidebar {
    min-width: 250px;
    max-width: 250px;
    color: #fff;
    transition: all 0.3s;
    z-index: 1;
    border: 0;
    border-radius: 0;
    box-shadow: 0 2px 2px 0 rgba(0,0,0,.14), 0 3px 1px -2px rgba(0,0,0,.2), 0 1px 5px 0 rgba(0,0,0,.12);
    padding-top: 60px;
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

.spt_bs_left_sidebar ul li a:hover {
    color: #424242;
    background: #fff;
}

.spt_bs_left_sidebar ul li a i {
    margin-right: 10px;
}

.spt_bs_left_sidebar ul li.active>a, a[aria-expanded="true"] {
    color: #fff;
    background: #262525;
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
    padding-left: 30px !important;
    background: #262525;
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

.spt_bs_content {
    padding-top: 56px;
    transition: all 0.3s;
}

/* ---------------------------------------------------
    MEDIAQUERIES
----------------------------------------------------- */

@media (min-width: 575.98px) {

    .spt_bs_top_nav_content {
        display: none !important;
    }


}

@media (max-width: 575.98px) {
    .spt_bs_left_sidebar {
        display: none;
    }

}


@media (max-width: 768px) {
   


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

        """)


        return style

    def get_display(self):
        nav = HtmlElement("nav")
        nav.set_id("sidebar")
        nav.add_class("spt_bs_left_sidebar bg-dark") 
        """
        TODO: Recreate sidebarpanelwdg with bootstrap like components
        # create the elements
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
        """

        # Header
        nav_header = DivWdg()
        nav.add(nav_header)

        nav_header.add_class("sidebar-header navbar-dark d-flex justify-content-between")

        # Links
        nav_list = HtmlElement.ul()
        nav.add(nav_list)

        nav_list.add_class("list-unstyled components")
        nav_list.add("""
            <li>
                <a href="#homeSubmenu" data-toggle="collapse" aria-expanded="false" class="dropdown-toggle">
                    <i class="fas fa-home"></i>
                    Home
                </a>
                <ul class="collapse list-unstyled" id="homeSubmenu">
                    <li>
                        <a href="#">Home 1</a>
                    </li>
                    <li>
                        <a href="#">Home 2</a>
                    </li>
                    <li>
                        <a href="#">Home 3</a>
                    </li>
                </ul>
            </li>
            <li>
                <a href="#">
                    <i class="fas fa-briefcase"></i>
                    About
                </a>
                <a href="#pageSubmenu" data-toggle="collapse" aria-expanded="false" class="dropdown-toggle">
                    <i class="fas fa-copy"></i>
                    Pages
                </a>
                <ul class="collapse list-unstyled" id="pageSubmenu">
                    <li>
                        <a href="#">Page 1</a>
                    </li>
                    <li>
                        <a href="#">Page 2</a>
                    </li>
                    <li>
                        <a href="#">Page 3</a>
                    </li>
                </ul>
            </li>
        """)

       
        styles = self.get_styles()
        nav.add(styles)

        return nav


class BootstrapIndexPage(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_class("container")
        from tactic.ui.panel import ViewPanelWdg
 
        wdg = ViewPanelWdg(search_type="config/widget_config", show_border=False)
        top.add(wdg)
        return top
