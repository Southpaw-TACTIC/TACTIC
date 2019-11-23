
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
        self.tab = TabWdg(config=config, view=view, mode="hidden")
        
        for widget in self.widgets:
            tab.add(widget)

    def get_display(self):

        top = self.top
        
        top.add("""<ul class="nav nav-tabs">
  <li class="nav-item">
    <a class="nav-link active" href="#">Active</a>
  </li>
  <li class="nav-item">
    <a class="nav-link" href="#">Link</a>
  </li>
  <li class="nav-item">
    <a class="nav-link" href="#">Another link</a>
  </li>
  <li class="nav-item">
    <a class="nav-link disabled" href="#">Disabled</a>
  </li>
</ul>""")

        top.add(self.tab)


        return top
