###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
from __future__ import print_function


__all__ = ["CustomLayoutWdg", "SObjectHeaderWdg"]

import os, types, re
import cStringIO

from pyasm.common import Xml, XmlException, Common, TacticException, Environment, Container, jsonloads, jsondumps
from pyasm.biz import Schema, ExpressionParser, Project
from pyasm.search import Search, SearchKey, WidgetDbConfig, SObject
from pyasm.web import DivWdg, SpanWdg, HtmlElement, Table, Widget, Html, WebContainer
from pyasm.widget import WidgetConfig, WidgetConfigView, IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu
from tactic.ui.container import Menu, MenuItem, SmartMenu

from tactic_client_lib import TacticServerStub


class CustomLayoutWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        'search_key': 'search key of the sobject to be displayed',
        # or
        'search_type': 'search type of the sobject to be displayed',
        'code': 'code of the sobject to be displayed',
        'id': {
            'description': 'id of the sobject to be displayed',
            'category': '_internal',
        },
        'sobjects_expr': 'expression to populate the sobjects for this widget',

        'category': {
            'description': 'category of the config to search for',
        },

        'search_type': {
            'description': 'search type of the sobject to be displayed',
            'type': 'TextWdg',
            'order': 1,
        },
        'view': {
            'description': 'The view defined in the widget config/Custom Layout Editor that contains the custom html',
            'type': 'TextWdg',
            'order': 2,
            'category': 'Options'
        },

        'state': {
            'description': 'State surrounding the widget',
            'category': '_deprecated'
        },
        'html': {
            'description': 'Explicitly define the html layout inline',
            'type': 'TextAreaWdg',
        },
        'include_mako': {
            'description': 'Boolean to turn on mako',
            'type': 'SelectWdg',
            'values': 'false|true',
        },
        'include': {
            'description': 'Include any other config files',
            'type': 'TextWdg',
            #'order': '1',
        }
    }


    def __init__(self, **kwargs):
        super(CustomLayoutWdg, self).__init__(**kwargs)


    def init(self):
        self.server = TacticServerStub.get(protocol='local')

        sobjects_expr = self.kwargs.get("sobjects_expr")
        if sobjects_expr:
            self.sobjects = Search.eval(sobjects_expr)

        self.data = {}

        # NOTE: this is is for the FilterElement Functionality
        self.show_title = True

        self.layout_wdg = None
        self.config = None
        self.def_config = None
        self.sobject_dicts = None
        self.is_table_element = False

        self.sequence_data = []


    def preprocess(self):
        code = self.kwargs.get('data')
        if not code:
            self.data = {}
            return
        
        # preprocess using mako
        #include_mako = self.kwargs.get("include_mako")
        #if not include_mako:
        #    include_mako = self.view_attrs.get("include_mako")

        from tactic.command import PythonCmd
        python_cmd = PythonCmd(code=code)
        self.data = python_cmd.execute()



    # NOTE: this is so that a custom layout can be used as a filter ....
    # however, this is not ideal because a filter requires a number of
    # methods that should not be present in this class
    def alter_search(self, search):
        script_path = self.get_option("alter_search_script_path")
        script_code = self.get_option("alter_search_script_code")

        from tactic.command import PythonCmd
        if script_path:
            cmd = PythonCmd(script_path=script_path, values=self.values, search=search, show_title=self.show_title)
        elif script_code:
            cmd = PythonCmd(script_code=script_code, values=self.values, search=search, show_title=self.show_title)

        cmd.execute()


    def set_values(self, values):
        self.values = values

    def set_show_title(self, flag):
        self.show_title = flag




    def get_display(self):
        self.sobject = self.get_current_sobject()
        if not self.sobject:
            self.sobject = self.get_sobject_from_kwargs()

        if self.sobject and self.sobject.is_insert():
            return DivWdg()



        if self.sobject:
            self.search_key = SearchKey.get_by_sobject(self.sobject)
            self.kwargs['search_key'] = self.search_key

        else:
            self.search_key = self.kwargs.get('search_key')


        html = self.kwargs.get('html')
        if not html:
            html = ""

        # DEPRECATED
        self.state = self.kwargs.get("state")
        self.state = BaseRefreshWdg.process_state(self.state)
        if not self.state:
            self.state = self.kwargs
            self.state['search_key'] = self.search_key



        self.view = self.kwargs.get('view')
        self.view = self.view.replace("/", ".")
        self.view_folder = ""

        if self.view.startswith("."):
            self.view_folder = self.kwargs.get("__view_folder__")
            if self.view_folder:
                self.view = "%s%s" % (self.view_folder, self.view)

        parts = self.view.split(".")
        self.view_folder = ".".join(parts[:-1])



        if not self.view and not html:
            raise TacticException("No view defined in custom layout")

        # If html is not a string, then convert it?
        if not isinstance(html, basestring):
            html = str(html)

        self.view_attrs = {}

        self.category = self.kwargs.get("category")
        self.search_type = self.kwargs.get("search_type")

        self.encoding = self.kwargs.get("encoding")
        if not self.encoding:
             self.encoding = 'utf-8'
        self.plugin = None

        xml = None

        
        # if html is not provided, then get it from the config
        config = None
        if not html:

            if self.config != None:
                config = self.config
            else:
                config = self.kwargs.get("config")
                if not config:
                    config = self.get_config()



            if not config:
                #div = DivWdg()
                #div.add("No config defined for view [%s] for custom layout" % self.view)
                #return div
                raise TacticException("No config defined for view [%s] for custom layout" % self.view)

            if isinstance(config, WidgetDbConfig):
                config_str = config.get_value("config")
            else:
                config_str = ''

            if config_str.startswith("<html>"):
                html = config_str
                self.def_config = None
            else:
                xml = config.get_xml()

                if self.def_config == None:
                    self.def_config = self.get_def_config(xml)

                # get the view attributes
                if isinstance(config, WidgetConfigView):
                    top_config = config.get_configs()[0]
                else:
                    top_config = config
                view_node = top_config.get_view_node()
                if view_node is None:
                    div = DivWdg("No view node found in xml. Invalid XML entry found")
                    return div
                self.view_attrs = xml.get_attributes(view_node)

                nodes = xml.get_nodes("config/%s/html/*" % self.view)
                if not nodes:
                    div = DivWdg("No definition found")
                    return div

                # convert html tag to a div
                html = cStringIO.StringIO()
                for node in nodes:
                    # unfortunately, html does not recognize <textarea/>
                    # so we have to make sure it becomes <textarea></textarea>
                    text = xml.to_string(node)
                    text = text.encode('utf-8')
                    keys = ['textarea','input']
                    for key in keys:
                        p = re.compile("(<%s.*?/>)" % key)
                        m = p.search(text)
                        if m:
                            for group in m.groups():
                                xx = group.replace("/", "")
                                xx = "%s</%s>" % (xx, key)
                                text = text.replace(group, xx)

                        text = text.replace("<%s/>" % key, "<%s></%s>" % (key, key))

                    # add linebreaks to element tag
                    key = 'element'

                    # reg full tag <element><display...></element>
                    p = re.compile(r"(<%s\b[^>]*>(?:.*?)</%s>)" % (key, key))
                    # short-hand tag <element/>
                    p1 =  re.compile("(</%s>|<%s.*?/>)" %(key, key))
                    m = p.search(text)
                    m1 = p1.search(text)
                    if m:
                        for group in m.groups():
                            if group:
                                text = text.replace(group, '\n%s\n'%group)
                    if m1:
                        for group in m1.groups():
                            if group:
                                text = text.replace(group, '\n%s\n'%group)
                       
                    html.write(text)

                html = html.getvalue()


        self.config = config
        #self.def_config = config    # This is unnessary?

        # try to get the sobject if this is in a table element widget
        if self.search_key:
            try:
                # this will raise an exception if it is not in a table element
                sobject = self.get_current_sobject()
            except:
                sobject = SearchKey.get_by_search_key(self.search_key)
            sobjects = [sobject]
        else:
            try:
                # this will raise an exception if it is not in a table element
                sobject = self.get_current_sobject()
                if sobject:
                    sobjects = [sobject]
                else:
                    sobjects = []
            except:
                sobject = self.sobjects


        self.layout = self.get_layout_wdg()



        # preprocess using mako
        include_mako = self.kwargs.get("include_mako")
        if not include_mako:
            include_mako = self.view_attrs.get("include_mako")


        if xml:
            mako_node = xml.get_node("config/%s/mako" % self.view)
            if mako_node is not None:
                mako_str = xml.get_node_value(mako_node)
                html = "<%%\n%s\n%%>\n%s" % (mako_str, html)



        from pyasm.web import Palette
        num_palettes = Palette.num_palettes()


        #if include_mako in ['true', True]:
        if include_mako not in ['false', False]:
            html = html.replace("&lt;", "<")
            html = html.replace("&gt;", ">")

            html = self.process_mako(html)



        # preparse out expressions

        # use relative expressions - [expr]xxx[/expr]
        p = re.compile('\[expr\](.*?)\[\/expr\]')
        parser = ExpressionParser()
        matches = p.finditer(html)
        for m in matches:
            full_expr = m.group()
            expr = m.groups()[0]
            result = parser.eval(expr, sobjects, single=True, state=self.state)
            if isinstance(result, basestring):
                result = Common.process_unicode_string(result)
            else:
                result = str(result)
            html = html.replace(full_expr, result )


        # use absolute expressions - [expr]xxx[/expr]
        p = re.compile('\[abs_expr\](.*?)\[\/abs_expr\]')
        parser = ExpressionParser()
        matches = p.finditer(html)
        for m in matches:
            full_expr = m.group()
            expr = m.groups()[0]
            result = parser.eval(expr, single=True)
            if isinstance(result, basestring):
                result = Common.process_unicode_string(result)
            else:
                result = str(result)
            html = html.replace(full_expr, result )



        # need a top widget that can be used to refresh
        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_custom_top")
        top.add_class("spt_panel")

        ignore_events = self.kwargs.get("ignore_events") in ['true', True]

        if ignore_events:
            top.add_style("pointer-events: none")


        # create the content div
        content = DivWdg()
        content.add_class("spt_custom_content")
        content.add_style("position: relative")
        if ignore_events:
            content.add_style("pointer-events: none")
        top.add(content)
        self.content = content


        is_test = Container.get("CustomLayout::is_test")
        if not is_test:
            is_test = self.kwargs.get("is_test") in [True, 'true']

        if is_test:
            Container.put("CustomLayout::is_test", True)
            self.top.add_style("margin: 0px 5px")
            self.handle_is_test(content)



        html = self.replace_elements(html)
        content.add(html)

        if xml:
            self.add_behaviors(content, xml)


        # remove all the extra palettes created
        while True:
            extra_palettes = Palette.num_palettes() - num_palettes
            if extra_palettes > 0:
                Palette.pop_palette()
            else:
                break

            
        if self.kwargs.get("is_top") in ['true', True]:
            return html

        elif self.kwargs.get("is_refresh"):
            return content
        else:
            return top



    def handle_is_test(self, content):

        content.add_behavior( {
            'type': 'mouseover',
            'cbjs_action': '''
            //bvr.src_el.setStyle("border", "solid 1px blue");
            bvr.src_el.setStyle("box-shadow", "0px 0px 5px rgba(0, 0, 0, 0.5)");
            //bvr.src_el.setStyle("margin", "-1px");
            var els = bvr.src_el.getElements(".spt_test");
            for (var i = 0; i < els.length; i++) {
                els[i].setStyle("display", "");
                break;
            }

            '''
        } )


        content.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''

            bvr.src_el.setStyle("box-shadow", "");
            //bvr.src_el.setStyle("margin", "0px");
            var els = bvr.src_el.getElements(".spt_test");
            for (var i = 0; i < els.length; i++) {
                els[i].setStyle("display", "none");
                break;
            }
            '''
        } )


        div = DivWdg()
        content.add(div)
        div.add_style("position: absolute")
        div.add("View: %s" % self.view)
        div.add_class("spt_test")
        div.add_border()
        #div.set_box_shadow("1px 1px 1px 1px")
        div.add_style("display: none")
        div.add_style("padding: 3px")
        div.add_style("margin-left: 3px")
        div.add_style("left: 0px")
        div.add_style("top: -15px")
        #div.add_style("opacity: 0.5")
        div.add_style("inherit: false")
        div.add_style("z-index: 1000")
        div.add_style("background-color: white")
        div.add_class("hand")


        div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_custom_top");
            top.setAttribute("spt_is_test", "true");
            var size = top.getSize();
            top.innerHTML = "<div style='width: "+size.x+";height: "+size.y+";padding: 10px; font-weight: bold'>Loading ...</div>";
            spt.panel.refresh(top);
            '''
        } )


        # add in a context menu
        menu = self.get_test_context_menu()
        menus = [menu.get_data()]
        menus_in = {
            'TEST_CTX': menus,
        }
        SmartMenu.attach_smart_context_menu( div, menus_in, False )
        SmartMenu.assign_as_local_activator( div, 'TEST_CTX' )



    def get_test_context_menu(self):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Refresh')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'view': self.view,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_custom_top");
            top.setAttribute("spt_is_test", "true");
            var size = top.getSize();
            top.innerHTML = "<div style='width: "+size.x+";height: "+size.y+";padding: 10px; font-weight: bold'>Loading ...</div>";
            spt.panel.refresh(top);
 

            '''
        } )

        menu_item = MenuItem(type='action', label='Edit')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'view': self.view,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var popup_top = activator.getParent(".spt_popup");
            var top = popup_top.top;
            if (top) {
                top.setAttribute("spt_view", bvr.view);
                spt.app_busy.show("Loading view: " + bvr.view);
                spt.panel.refresh(top);
                spt.app_busy.hide();
            }
            '''
        } )


        menu_item = MenuItem(type='action', label='Open in Main Tab')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'view': self.view,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var popup_top = activator.getParent(".spt_popup");
            spt.popup.close(popup_top);

            var top = activator.getParent(".spt_custom_top");
            var class_name = top.getAttribute("spt_class_name");
            var kwargs = spt.panel.get_element_options(top);
            //kwargs['is_test'] = true;

            var title = "Test: " + bvr.view;

            spt.tab.set_main_body_tab();
            spt.tab.add_new(title, title, class_name, kwargs);
            '''
        } )




        return menu

     






    HEADER = '''<%def name='expr(expr)'><% result = server.eval(expr) %>${result}</%def>'''





    def process_mako(self, html):

        from mako.template import Template
        from mako import exceptions
        html = '%s%s' % (CustomLayoutWdg.HEADER, html)

        # remove CDATA tags
        html = html.replace("<![CDATA[", "")
        html = html.replace("]]>", "")
        #html = html.decode('utf-8')
      
        if self.encoding == 'ascii':
            template = Template(html)
        else:
            template = Template(html, output_encoding=self.encoding, input_encoding=self.encoding)

        # get the api version of the sobject
        if not self.is_table_element:
            if self.sobject_dicts == None:
                self.sobject_dicts = []
                for sobject in self.sobjects:
                    sobject_dict = sobject.get_sobject_dict()
                    self.sobject_dicts.append(sobject_dict)

        if self.sobject:
            sobject = self.sobject.get_sobject_dict()
        else:
            sobject = {}



        # find out if there is a plugin associated with this
        plugin = self.kwargs.get("plugin")
        if not plugin or plugin == '{}':
            plugin = {}

        """
        if not plugin and isinstance(self.config, SObject):
            plugin = Search.eval("@SOBJECT(config/plugin_content.config/plugin)", self.config, single=True)
        """

        if plugin:
            if isinstance(plugin, dict):
                pass
            else:
                plugin = plugin.get_sobject_dict()
            plugin_code = plugin.get("code")
            plugin_dir = self.server.get_plugin_dir(plugin)
        else:
            plugin_code = ""
            plugin_dir = ""
            plugin = {}
        self.kwargs['plugin_dir'] = plugin_dir
        self.kwargs['plugin_code'] = plugin_code

        try:
            html = template.render(server=self.server, search=Search, sobject=sobject, sobjects=self.sobject_dicts, data=self.data, plugin=plugin, kwargs=self.kwargs)


            # we have to replace all & signs to &amp; for it be proper html
            html = html.replace("&", "&amp;")
            return html
        except Exception as e:
            if str(e) == """'str' object has no attribute 'caller_stack'""":
                raise TacticException("Mako variable 'context' has been redefined.  Please use another variable name")
            else:
                print("Error in view [%s]: " % self.view, exceptions.text_error_template().render())
                #html = exceptions.html_error_template().render(css=False)
                html = exceptions.html_error_template().render()
                html = html.replace("body { font-family:verdana; margin:10px 30px 10px 30px;}", "")
                return html

    def handle_layout_behaviors(self, layout):
        '''required for BaseTableElementWdg used by fast table'''
        pass


    def add_test(self, xml):
        # add a test env in
        text_node = xml.get_nodes("config/%s/test" % self.view)




    def add_kwargs(self, widget, xml):
        """
        ARGS_KEYS = {
        'category': {
            'description': 'category of the config to search for',
        },
        'view': {
            'description': 'The view defined in the widget config/Custom Layout Editor that contains the custom html',
            'type': 'TextWdg',
            'order': 2,
            'category': 'Options'
        },
        }

        <kwargs>
          <kwarg name="category">
            <description>category of the config to search for</description>
          </kwarg>
          <kwarg name="view">
            <description>The view defined in the widget config/Custom Layout Editor that contains the custom html</description>
            <type>TextWdg</type>
            <order>2</order>
            <category>Options</category>
          </kwarg>
        </kwargs>
        """


        kwargs_nodes = xml.get_nodes("config/%s/kwargs/kwarg" % self.view)
        for kwarg_node in kwargs_node:
            pass




    def add_behaviors(self, widget, xml):

        behavior_nodes = xml.get_nodes("config/%s/behavior" % self.view)

        if behavior_nodes:
            hidden_div = DivWdg()
            hidden_div.add_styles("display: none");
            hidden_div.add_class("spt_customlayoutwdg_handoffs")
            widget.add( hidden_div )

            widget.add_behavior({
                'type': 'load',
                'cbjs_action': '''
                    // handle embedded load behaviors!
                    var el_load_list = bvr.src_el.getElements(".SPT_BVR_LOAD_PENDING");
                    spt.behavior.process_load_behaviors( el_load_list );
                '''
            })



            # remove objects that cannot be json marshalled
            view_kwargs = self.kwargs.copy()
            for key, value in view_kwargs.items():
                try:
                    test = jsondumps(value)
                except Exception as e:
                    del(view_kwargs[key])


            for behavior_node in behavior_nodes:

                bvr_div = DivWdg()
                hidden_div.add( bvr_div )

                css_class = Xml.get_attribute(behavior_node, 'class')
                behavior_str = Xml.get_node_value(behavior_node)
                behavior_str = behavior_str.strip()

                # if the event is specified in the xml, then use that
                event = Xml.get_attribute(behavior_node, 'event')

                modkeys = Xml.get_attribute(behavior_node, 'modkeys')

                relay_class = Xml.get_attribute(behavior_node, 'relay_class')

                if not behavior_str:
                    continue

                try:
                    try:
                        bvr = eval(behavior_str)
                    except:
                        # try it as a string
                        bvr_str = eval("'''\n%s\n'''" % behavior_str)

                        if bvr_str:
                            bvr = {}
                            bvr['cbjs_action'] = bvr_str

                    if event:
                        bvr['type'] = event

                    if modkeys:
                        bvr['modkeys'] = modkeys



                    # add the kwargs to this so behaviors have access
                    bvr['kwargs'] = view_kwargs
                    bvr['class_name'] = Common.get_full_class_name(self)

                    if relay_class:
                        bvr['bvr_match_class'] = relay_class
                        if not bvr.get("type"):
                            bvr['type'] = 'mouseup'
                        self.content.add_relay_behavior( bvr )

                    elif bvr.get("type") == "smart_drag":
                        bvr['bvr_match_class'] = css_class
                        self.content.add_behavior(bvr)

                    elif bvr.get("type") == "listen":
                        bvr['bvr_match_class'] = css_class
                        bvr['event_name'] = Xml.get_attribute(behavior_node,'event_name')
                        self.content.add_behavior(bvr)

                    else:
                        bvr['_handoff_'] = '@.getParent(".spt_custom_content").getElements(".%s")' % css_class
                        if not bvr.get("type"):
                            bvr['type'] = 'click_up'
                        bvr_div.add_behavior( bvr )



                except Exception as e:
                    print("Error: ", e)
                    raise TacticException("Error parsing behavior [%s]" % behavior_str)


    def get_config(self):
        config = None
        config_xml = self.kwargs.get('config_xml')
        if config_xml:
            config = WidgetConfig.get(xml=config_xml, view=self.view)
            return config


        # this is the new preferred way of defining CustomLayoutWdg
        search = Search("config/widget_config")
        if self.category:
            search.add_filter("category", self.category)
        else:
            search.add_filter("category", 'CustomLayoutWdg')
        if self.search_type:
            search.add_filter("search_type", self.search_type)

        search.add_filter("view", self.view)

        configs = search.get_sobjects()

        # annoyingly NULL is always higher than any number, so we have
        # put them at the end
        if configs and configs[0].column_exists("priority"):
            configs = sorted(configs, key=lambda x: x.get("priority"))
            configs.reverse()

        if configs:
            config = configs[0]
            return config

        # if it is not defined in the database, look at a config file
        includes = self.kwargs.get("include")
        if includes:
            includes = includes.split("|")

            for include in includes:
                if include.find('/') != -1:
                    file_path = include
                else:
                    tmp_path = __file__
                    dir_name = os.path.dirname(tmp_path)
                    file_path ="%s/../config/%s" % (dir_name, include)
                config = WidgetConfig.get(file_path=file_path, view=self.view)
                if config and config.has_view(self.view):
                    return config

        # deprecated approach, assuming a "CustomLayoutWdg" as search_type,
        # is deprecated
        if not config:
            search = Search("config/widget_config")
            if self.category:
                search.add_filter("category", self.category)
            if self.search_type:
                search.add_filter("search_type", "CustomLayoutWdg")

            search.add_filter("view", self.view)

            config = search.get_sobject()
        
        #if not config and self.search_type and self.view:
        #    config = WidgetConfigView.get_by_search_type(self.search_type, self.view)
        # this is the new preferred way of defining CustomLayoutWdg
        # NOTE: this finds a definition where search type is not explicitly
        # given>
        if not config:
            search = Search("config/widget_config")
            search.add_filter("view", self.view)
            search.add_filter("search_type", None)
            config = search.get_sobject()


        return config



    def get_def_config(self, def_xml=None):
        def_confg = None

        self.def_view = self.kwargs.get('definition')
        if self.def_view:
            #raise TacticException("No definition view defined in custom layout with view [%s]" % self.view)

            self.search_type = "CustomLayoutWdg"
            search = Search("config/widget_config")
            search.add_filter("search_type", self.search_type)
            search.add_filter("view", self.def_view)
            def_db_config = search.get_sobject()
            if not def_db_config:
                raise TacticException("Definition config [%s] not defined" % self.def_view)
            def_xml = def_db_config.get_xml()
            def_config = WidgetConfig.get("definition", xml=def_xml)


        # also look inline to see if there are any definitions        
        if def_xml:
            # just use the passed in xml for a definition
            def_config = WidgetConfig.get(self.view, xml=def_xml)


        return def_config

   
    def replace_elements(self, html_str):

        """
        # NOTE: this likely is a better way to extract elements, but still
        # need to find a way to inject html back into the xml
        xml = Xml()
        xml.read_string("<div>%s</div>" % html_str)
        elements = xml.get_nodes("//element")

        for element in elements:
            # create a complete config
            full_line_str = xml.to_string(element)
            tmp_config = '''<config><tmp>%s</tmp></config>''' % full_line_str

            try:
                element_wdg = self.get_element_wdg(xml, self.def_config)
                element_html = element_wdg.get_buffer_display()
            except Exception as e:
                from pyasm.widget import ExceptionWdg
                element_html = ExceptionWdg(e).get_buffer_display()

            xml = Xml()
            try:
                xml.read_string(element_html)
            except Exception as e:
                print("Error: ", e)
                xml.read_string("<h1>%s</h1>" % str(e) )
            root = xml.get_root_node()

            parent = xml.get_parent(element)
            xml.replace_child(parent, element, root)

        return xml.to_string()
        """


        # a simple readline interpreter
        html = Html()
        full_line = []
        parse_context = None
        for line in html_str.split("\n"):
            line2 = line.strip()


            #if not parse_context and not line2.startswith('<element '):
            index = line2.find('<element>')
            if index == -1:
                index = line2.find('<element ')


            if not parse_context and index == -1:
                #line = Common.process_unicode_string(line)
                html.writeln(line)
                continue

            if index != -1:
                part1 = line2[:index]
                html.write(part1)
                line2 = line2[index:]

            full_line.append(line2)
            xml = Xml()
            # determine if this is valid xml
            try:
                # create a complete config
                full_line_str = "".join(full_line)
                tmp_config = '''<config><tmp>%s</tmp></config>''' % full_line_str
                xml.read_string(tmp_config, print_error=False)

                full_line = []
                parse_context = ''

            except XmlException as e:
                parse_context = 'element'
                #raise e
                continue

            try:

                if Xml.get_value(xml, "config/tmp/element/@enabled") == "false":
                    continue


                element_wdg = self.get_element_wdg(xml, self.def_config)
                if element_wdg:
                    element_html = element_wdg.get_buffer_display()
                else:
                    element_html = ''
            except Exception as e:
                from pyasm.widget import ExceptionWdg
                element_html = ExceptionWdg(e).get_buffer_display()

            # Test to ensure that the html produced is "xml" conforming
            """
            try:
                new_xml = Xml()
                new_xml.read_string(element_html)
            except Exception as e:
                f = open("/tmp/error", 'w')
                f.write(element_html)
                f.close()
                #print(element_html)
                print("Error: ", e)
            """

            if element_html:
                html.writeln(element_html)

        sequence_wdg = self.get_sequence_wdg()
        html.writeln(sequence_wdg.get_buffer_display() )
        

        return html.to_string()





    # FIXME: this is all necessary because CustomLayoutWdg is not derived from
    # BaseTableElementWdg ...  CustomLayoutWdg should probably not be used
    # as a table elementj
    # NOTE: Use tactic.ui.table.CustomLayoutElementWdg for adding custom layouts
    # to layouts
    def set_parent_wdg(self, name):
        pass
    def is_in_column(self):
        return True
    def is_groupable(self):
        return False

    def set_layout_wdg(self, widget):
        self.layout_wdg = widget
    def get_layout_wdg(self):
        return self.layout_wdg 


    def get_title(self):
        '''Returns a widget containing the title to be displayed for this
        column'''
        if self.title:
            title = self.title
            return title

        title = self.name
        if not title:
            title = ""
            return title

        title = Common.get_display_title(title)
        return title


    def get_value(self):
        return None

    def get_text_value(self):
        '''for csv export'''
        sobject = self.get_current_sobject()
        text_expr = self.kwargs.get("text_value")
        text_expr = "@GET(.id)"
        if not text_expr:
            return ''
        value = Search.eval(text_expr, sobject, single=True)
        return value

    def is_sortable(self):
        return False
    def is_searchable(self):
        return False
    def handle_th(self, th, xx=None):
        pass
    def handle_td(self, td):
        pass
    def handle_tr(self, tr):
        pass
    def is_editable(self):
        return False
    def get_bottom_wdg(self):
        return None
    def get_group_bottom_wdg(self, sobjects=None):
        return None
    def get_header_option_wdg(self):
        return None
    def get_generator(self):
        return self.generator_element
    def set_generator(self, element_name):
        self.generator_element = element_name

    ## END TableElementWdg methods

 

    def get_sequence_wdg(self):

        funcs = []

        div = DivWdg()
        if not self.sequence_data:
            return div

        div.add_behavior( {
            'type': 'load',
            'data': self.sequence_data,
            'cbjs_action': '''

            var count = -1;

            var func = function() {
                if (count == bvr.data.length-1) {
                    return;
                }
                count += 1;

                var item = bvr.data[count];
                var unique_id = item.unique_id;
                var class_name = item.class_name;
                var kwargs = item.kwargs;

                var options = {
                    async: true,
                    callback: func
                }
                spt.panel.load($(unique_id), class_name, kwargs, {}, options);

            }

            func();

            '''
        } )
        return div

 


    def get_async_element_wdg(self, xml, element_name, load):

        tmp_config = WidgetConfig.get('tmp', xml=xml)
        display_handler = tmp_config.get_display_handler(element_name)
        display_options = tmp_config.get_display_options(element_name)

        div = DivWdg()
        unique_id = div.set_unique_id()
        div.add_class("spt_manual_load")

        show_loading = self.kwargs.get("show_loading")

        if load == "sequence":
            self.sequence_data.append( {
                'class_name': display_handler,
                'kwargs': display_options,
                'unique_id': unique_id
            } )
        elif load == "manual":

            show_loading = False
            div.add_behavior( {
                'type': 'load',
                'class_name': display_handler,
                'kwargs': display_options,
                'cbjs_action': '''
                bvr.src_el.load = function() {
                    spt.panel.async_load(bvr.src_el, bvr.class_name, bvr.kwargs);
                }

                '''
            } )
            msg = DivWdg()
            div.add(msg)
            msg.add_style("padding", "20px")
            msg.add_style("margin", "10px auto")
            msg.add_style("width", "150px")
            msg.add_style("border", "solid 1px #DDD")
            msg.add_style("text-align", "center")
            msg.add("Loading ...")


        else:
            div.add_behavior( {
                'type': 'load',
                'class_name': display_handler,
                'kwargs': display_options,
                'cbjs_action': '''
                spt.panel.async_load(bvr.src_el, bvr.class_name, bvr.kwargs);
                '''
            } )

        if show_loading not in ["False", False, "false"]:
            loading_div = DivWdg()
            loading_div.add_style("margin: auto auto")
            loading_div.add_style("width: 150px")
            loading_div.add_style("text-align: center")
            loading_div.add_style("padding: 20px")
            div.add(loading_div)
            loading_div.add('''<img src="/context/icons/common/indicator_snake.gif" border="0"/> <b>Loading ...</b>''')

        return div



    def get_element_wdg(self, xml, def_config):

        element_node = xml.get_node("config/tmp/element")
        attrs = Xml.get_attributes(element_node)
        element_name = attrs.get("name")

        widget = self.get_widget(element_name)
        if widget:
            return widget


        if not element_name:
            import random
            num = random.randint(0, 1000000)
            element_name = "element%s" % num
            xml.set_attribute(element_node, "name", element_name)


        # enable an ability to have a widget only loaded once in a request
        if attrs.get('load_once') in ['true', True]:
            widgets = Container.get("CustomLayoutWdg:widgets")
            if widgets == None:
                widgets = {}
                Container.put("CustomLayoutWdg:widgets", widgets)
            else:
                if widgets[element_name] == True:
                    return None

                widgets[element_name] = True


        # provide the ability to have shorthand format 
        # ie: <element display_class="tactic.ui..." />
        display_node = xml.get_node("config/tmp/element/display")
        if display_node is None:
            view = attrs.get("view")
            type = attrs.get("type")

            if type == "reference":
                search_type = attrs.get("search_type")
                self.config = WidgetConfigView.get_by_search_type(search_type, view)
                # check if definition has no name.  Don't use element_name
                if not attrs.get("name"):
                    return

                element_wdg = self.config.get_display_widget(element_name, extra_options=attrs)
                container = DivWdg()
                container.add(element_wdg)
                return container


            class_name = attrs.get("display_class")

            # if no class name is defined and not view is defined look
            # at predefined elements
            if not view and not class_name:
                element_wdg = self.config.get_display_widget(element_name, extra_options=attrs)
                container = DivWdg()
                container.add(element_wdg)
                return container


            # look at the attributes
            if not class_name:
                class_name = "tactic.ui.panel.CustomLayoutWdg"
            display_node = xml.create_element("display")
            xml.set_attribute(display_node, "class", class_name)
            xml.append_child(element_node, display_node)

            for name, value in attrs.items():
                # replace the spt_ in the name.
                # NOTE: should this be restricted to only spt_ attributes?
                name = name.replace("spt_", "")
                attr_node = xml.create_element(name)
                xml.set_node_value(attr_node, value)
                xml.append_child(display_node, attr_node)


        load = attrs.get("load")

        if load in ["none"]:
            return None

        elif load in ["async", "sequence","manual"]:
            return self.get_async_element_wdg(xml, element_name, load)



        # add the content
        try:
            view_node = xml.get_node("config/tmp/element/display/view")
            if view_node is not None:
                view = xml.get_node_value(view_node)
                if view.startswith("."):
                    if self.view_folder:
                        xml.set_node_value(view_node, "%s%s" %(self.view_folder,view))
            tmp_config = WidgetConfig.get('tmp', xml=xml)
            configs = []
            configs.append(tmp_config)

            # add the def_config if it exists
            if def_config:
                configs.append(def_config)

            config = WidgetConfigView('CustomLayoutWdg', 'tmp', configs, state=self.state)

            # NOTE: this doesn't work too well when we go to an abasolute
            # view.
            parent_view = self.kwargs.get("parent_view")
            if parent_view:
                parent_view = parent_view.replace(".", "/")
                parent_view = "%s/%s" % (parent_view, self.view)
            else:
                parent_view = self.view

            # NOTE: need some protection code for infinite loops


            includes = self.kwargs.get("include")
            extra_options = {"parent_view": parent_view}
            if includes:
                extra_options['include'] = includes

            element_wdg = config.get_display_widget(element_name, extra_options=extra_options)

            element_top = element_wdg.get_top()
            for name, value in attrs.items():
                if name == 'class':
                    for item in value.split(" "):
                        element_top.add_class(item)

                elif name == 'style':
                    for item in re.split(";\ ?", value):
                        element_top.add_style(item)

                else:
                    element_top.set_attr(name, value)




            # make a provision if this custom widget is in a table
            if self.layout:
                sobject = self.get_current_sobject()
                element_wdg.set_sobject(sobject)



        except Exception as e:
            from pyasm.widget import ExceptionWdg
            log = ExceptionWdg(e)
            element_wdg = log

        return element_wdg

        container.add(element_wdg)
        return container




    def get_smart_header_context_menu_data(self):
        from pyasm.widget import IconWdg
        menu_data = { 'menu_tag_suffix': 'MAIN', 'width': 200 }

        opt_spec_list = []


        opt_spec_list.append( {
            "type": "action",
            "label": "Edit Definition",
            "icon": IconWdg.EDIT,
            "bvr_cb": {
                'cbjs_action': 'alert("Edit Definition")'
            }
        })

        opt_spec_list.append( {
            "type": "separator"
        } )


        opt_spec_list.append( {
            "type": "action",
            "label": "Split Horizontal",
            "icon": IconWdg.TABLE_ROW_INSERT,
            "bvr_cb": {
                'cbjs_action': 'spt.custom_project.split_horizontal(evt, bvr)'
            }
        })

        opt_spec_list.append( {
            "type": "action",
            "label": "Split Vertical",
            "bvr_cb": {'cbjs_action': "spt.js_log.show();"}
        })


        opt_spec_list.append( {
            "type": "action",
            "label": "Remove Panel",
            "icon": IconWdg.TABLE_ROW_DELETE,
            "bvr_cb": {
                'cbjs_action': 'spt.custom_project.remove_panel(evt, bvr)'
            }
        })

        opt_spec_list.append( {
            "type": "separator"
        } )



        opt_spec_list.append( {
            "type": "action",
            "label": "Save Layout",
            "icon": IconWdg.SAVE,
            "bvr_cb": {
                'cbjs_action': 'spt.custom_project.save_layout(evt, bvr)'
            }
        })


        menu_data['opt_spec_list'] = opt_spec_list

        return menu_data



__all__.append("TestStateWdg")
class TestStateWdg(BaseRefreshWdg):

    def get_display(self):
        self.top.add(self.kwargs)
        self.top.add("<hr/>")
        if self.sobjects:
            self.top.add(self.sobjects[0].get_code())
        else:
            self.top.add("No sobjects")
        return self.top



# DEPRECATED
"""
class ContainerWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
            'inner_width': 'Inner width, sans rounded corner wrapper ... numeric value only',
            'inner_height': 'Inner height, sans rounded corner wrapper ... numeric value only',
            'show_resize_scroll': 'true|false: determines whether to show scroll bars or not'
        }


    def init(self):

        self.top = DivWdg()
        self.content_wdg = DivWdg()

        is_IE = WebContainer.get_web().is_IE()

        # get the width and height of the contents (the inner part of the container) ...
        self.inner_width = self.kwargs.get('inner_width')
        self.inner_height = self.kwargs.get('inner_height')

        if self.inner_width:
            self.inner_width = int(self.inner_width)
            if is_IE:
                self.inner_width -= 20  # adjust for rounded corner wrapper
        else:
            self.inner_width = 600
        if self.inner_height:
            self.inner_height = int(self.inner_height)
            if is_IE:
                self.inner_height -= 20  # adjust for rounded corner wrapper
        else:
            self.inner_height = 200

        # Now place a ResizeScrollWdg within a RoundedCornerDivWdg ... the ResizeScrollWdg will contain
        # the actual contents of this container, so that the contents can be scrolled and resized ...
        #
        from tactic.ui.container import RoundedCornerDivWdg
        color = self.top.get_color("background")
        self.rc_wdg = RoundedCornerDivWdg(hex_color_code=color,corner_size=10)

        #show_scrollbars = self.kwargs.get("show_resize_scroll")
        #if show_scrollbars in ['', 'false']:
        #    self.inner_wdg = DivWdg()
        #else:
        #    from tactic.ui.container import ResizeScrollWdg
        #    self.inner_wdg = ResizeScrollWdg( width=self.inner_width, height=self.inner_height, scroll_bar_size_str='medium', scroll_expansion='inside' )
        self.inner_wdg = DivWdg()
        self.inner_wdg.add_style("width: %s" % self.inner_width)
        self.inner_wdg.add_style("height: %s" % self.inner_height)
        self.inner_wdg.add_style("overflow-y: auto")
        self.inner_wdg.add_style("overflow-x: hidden")

        self.rc_wdg.add( self.inner_wdg )

        self.content_wdg.add(self.rc_wdg)


        self.table = Table(css="minimal")
        self.table.add_row()
        self.content_td = self.table.add_cell()
        self.content_td.add_class("spt_content")
        self.content_td.add_style('padding: 2px')



    def add_style(self, name, value=None):
        if name.startswith("height"):
            self.content_td.add_style(name, value)
        elif name.startswith("width"):
            self.content_td.add_style(name, value)
        else:
            self.top.add_style(name, value)


    def get_display(self):

        # fill in the content widget
        for widget in self.widgets:
            self.inner_wdg.add(widget)

        self.top.add_class("spt_container")

        self.content_wdg.add_style("float: left")

        # -- DO NOT SET THE WIDTH AND HEIGHT of the content_wdg! Commenting out these lines ...
        # self.content_wdg.add_style("width: 100%")
        # self.content_wdg.add_style("height: 100%")


        # add the content
        self.content_td.add_style("vertical-align: top")
        self.content_td.add(self.content_wdg)

        self.top.add(self.table)

        return self.top


    def get_divider_wdg(self, activator, mode='vertical'):
        divider_div = DivWdg()
        divider_div.add_style("border-style", "dashed")
        divider_div.add_style("border-color", "#999")

        if mode == 'vertical':
            divider_div.add_style("margin-left", "3px")
            divider_div.add_style("height", "100%")
            divider_div.add_style("width", "1px")
            divider_div.add_style("border-width", "0 0 0 1px")
        else:
            divider_div.add_style("margin-top", "3px")
            divider_div.add_style("width", "100%")
            divider_div.add_style("height", "1px")
            divider_div.add_style("border-width", "1px 0 0 0")

        divider_div.add_class("hand")
        divider_div.add_class("content")
        divider_div.add_style("display", "none")

        activator.add_event("onmouseover", "$(this).getElement('.content').setStyle('display', '');")
        activator.add_event("onmouseout", "$(this).getElement('.content').setStyle('display', 'none');")

        return divider_div

"""



class SObjectHeaderWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
        "parent_key": "the search key of the sobject that the header will display"
        }



    def get_display(self):

        search_key = self.kwargs.get('parent_key')

        div = DivWdg()

        if not search_key:
            div.add("Search Key for SObjectHeaderHdg is empty")
            return div

        sobject = Search.get_by_search_key( search_key )
        if not sobject:
            div.add("SObject with Search Key [%s] does not exist" % search_key)
            return div


        search_type_obj = sobject.get_search_type_obj()
        title = search_type_obj.get_title()
        title_wdg = DivWdg()
        title_wdg.add_style("font-size: 1.8em")

        name = sobject.get_display_value()
        title_wdg.add("%s: %s" % (title, name ))

        div.add(title_wdg)
        div.add(HtmlElement.hr())

        return div










