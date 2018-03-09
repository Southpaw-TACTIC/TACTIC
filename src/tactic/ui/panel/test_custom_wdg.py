
#import tacticenv
#from pyasm.security import Batch
#Batch(project_code='cg')

from pyasm.search import Search
from pyasm.common import Xml, Common
from pyasm.web import Widget, DivWdg
from tactic.ui.common import BaseRefreshWdg


class TestCustomWdg(BaseRefreshWdg):

    def get_display(self):
        

        self.kwargs['search_key'] = 'prod/asset?project=sample3d&code=chr001'



        custom = """<?xml version='1.0' encoding='UTF-8'?>
        <custom>

        <html>
        <div>
            This is html
            <textarea class='spt_test spt_input' name='description'>
</textarea>
            <input class='spt_input' type='text' name='title'/>
            <br/>
            <input class='spt_button1' type='button' value='Press Me'/>
            <input class='spt_button2' type='button' value='Press Me2'/>
            <input class='spt_button3' type='button' value='Calendar'/>
            <input class='spt_refresh' type='button' value='Refresh'/>


            <element>
              <display class='tactic.ui.widget.CalendarWdg'/>
            </element>
            Much simpler!!!
            <elemeent class='CalendarWdg' blah='adasf'/>

        </div>
        </html>
        <behavior class='spt_button1'>{
            "type": "click_up",
            "cbjs_action": '''
            app.mel('sphere');
            //var top = bvr.src_el.getParent(".spt_panel");
            //var values = spt.api.Utility.get_input_values(top);
            //console.log(values);
            '''
        }</behavior>
        <behavior class='spt_button2'>{
            "type": "click_up",
            "cbjs_action": "alert(bvr.kwargs.search_key);"
        }</behavior>
        <behavior class='spt_button3'>{
            "type": "click_up",
            "cbjs_action": '''
            spt.panel.load('main_body', bvr.class_name, bvr.kwargs);
            //spt.panel.load('main_body', 'tactic.ui.widget.CalendarWdg', bvr.kwargs);
            '''
        }</behavior>
        <behavior class='spt_refresh'>{
            "type": "click_up",
            "cbjs_action": '''
            var top = bvr.src_el.getParent(".spt_panel");
            spt.panel.refresh(top);
            '''

        }</behavior>

        </custom>

        """

        xml = Xml()
        xml.read_string(custom)

        top = DivWdg()
        self.set_as_panel(top)
        top.add_class("spt_panel")

        inner = DivWdg()
        top.add(inner)

        html_node = xml.get_node("custom/html")
        html = xml.to_string(html_node)
        inner.add(html)

        behaviors = xml.get_nodes("custom/behavior")
        for behavior in behaviors:
            css_class = Xml.get_attribute(behavior, 'class')
            value = Xml.get_node_value(behavior)
            value = eval(value)

            # add the kwargs to this so behaviors have access
            value['kwargs'] = self.kwargs
            value['class_name'] = Common.get_full_class_name(self)

            inner.add_behavior({
                'type': 'load',
                'value': value,
                'css_class': css_class,
                'cbjs_action': '''
                var el = bvr.src_el.getElement("."+bvr.css_class);
                if (!el) {
                    alert("WARNING: element ["+bvr.css_clsss+"] does not exist");
                }
                spt.behavior.add( el, bvr.value);
                '''
            })


        if self.kwargs.get("is_refresh"):
            return inner
        else:
            return top





