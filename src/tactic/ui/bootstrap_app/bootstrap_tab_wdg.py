
from pyasm.widget import WidgetConfig
from pyasm.web import DivWdg

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
        

    def get_tab_id(self):
        return self.unique_id

    def get_display(self):

        top = self.top
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
