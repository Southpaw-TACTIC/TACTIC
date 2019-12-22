
from pyasm.widget import WidgetConfig
from pyasm.web import DivWdg, HtmlElement

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import TabWdg

__all__ = ['BootstrapTabWdg']


class BootstrapTabWdg(BaseRefreshWdg):


    def init(self):
        
        config_xml = "<config><tab/></config>"
        view = "tab"
        config = WidgetConfig.get(view=view, xml=config_xml)
        self.tab = TabWdg(config=config, view=view, use_default_style=False, save_state="main_body_tab_state")
        self.unique_id = self.tab.get_tab_id()
        self.header_id = self.tab.get_header_id()
        

    def get_tab_id(self):
        return self.unique_id

    def get_header_id(self):
        return self.header_id

    def get_bootstrap_styles(self):

        header_id = self.get_header_id()
        style = """
            #%(header_id)s {
                height: 40px;
                display: none !important;
            }

            @media (min-width: 576px) {
                #%(header_id)s {
                    display: flex !important;
                }
            }


        """ % {'header_id': header_id}
            
        
        style += """
            .spt_tab_content_top {
                overflow-y: auto;
                height: calc(100% - 80px);
            }
            
            @media (max-width: 575.98px) {
                .spt_tab_content_top {
                    height: 100%;
                }
            }
            

            .nav-pills .nav-link, .nav-tabs .nav-link {
                padding: .5em .8575em;
                font-size: 12px;
                height: 40px;
            }

            /* TODO REMOVE and put in TabWdg */
            .spt_tab_selected {
                border-bottom: solid .214rem #114e8a;
                height: 40px;
            }

            /* TODO REMOVE and put in TabWdg */
            .nav-tabs .spt_tab_selected .nav-link {
                color: rgba(0,0,0,.87);
            }
        """

        return HtmlElement.style(style)


    def get_display(self):

        top = self.top

        top.add(self.get_bootstrap_styles())

        top.add(self.tab)

        for widget in self.widgets:
            self.tab.add(widget)
        
        # HACK set the current one active
        div = DivWdg()
        div.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        spt.tab.set_main_body_top();
        var headers = spt.tab.get_headers();
        // if there are no headers, then there was an error
        if (headers.length == 0) {
            return;
        }

        var name = headers[headers.length-1].getAttribute("spt_element_name");
        spt.tab.select(name);
        '''
        } )
        top.add(div)

        return top
