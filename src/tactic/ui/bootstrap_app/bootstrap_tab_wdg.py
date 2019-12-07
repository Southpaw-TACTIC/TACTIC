
from pyasm.widget import WidgetConfig

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import TabWdg

__all__ = ['BootstrapTabWdg']


class BootstrapTabWdg(BaseRefreshWdg):

    def init(self):
        
        view = "tab"
        config_xml = '''<config>
            <tab>
                <element name="Index Page">
                    <display class="tactic.ui.bootstrap_app.BootstrapIndexPage"/>
                </element>
                <element name="Index Page2">
                    <display class="tactic.ui.bootstrap_app.BootstrapIndexPage"/>
                </element>
                <element name="Index Page3">
                    <display class="tactic.ui.bootstrap_app.BootstrapIndexPage"/>
                </element>
            </tab>
        </config>'''
        config = WidgetConfig.get(view=view, xml=config_xml)
        self.tab = TabWdg(config=config, view=view, use_default_style=False)
        
        for widget in self.widgets:
            tab.add(widget)

    def get_display(self):

        top = self.top
        top.add(self.tab)
        top.add_class("mx-1")


        return top
