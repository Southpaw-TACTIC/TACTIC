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
__all__ = ["CustomLayoutWdg", "SObjectHeaderWdg"]

import os, types, re
import cStringIO

from pyasm.common import Xml, XmlException, Common, TacticException, Environment, Container, jsonloads
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
        'id': 'id of the sobject to be displayed',

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

        'state': 'state surrounding the widget',
        'show_resize_scroll': 'true|false - determines wether to show the scroll resize widget on elements',

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
            'category': 'Options'
        }
    }


    def __init__(my, **kwargs):
        super(CustomLayoutWdg, my).__init__(**kwargs)


    def init(my):
        my.server = TacticServerStub.get(protocol='local')

        sobjects_expr = my.kwargs.get("sobjects_expr")
        if sobjects_expr:
            my.sobjects = Search.eval(sobjects_expr)

        my.data = {}

        # NOTE: this is is for the FilterElement Functionality
        my.show_title = True

        my.layout_wdg = None
        my.config = None
        my.def_config = None
        my.sobject_dicts = None
        my.is_table_element = False

        my.sequence_data = []


    def preprocess(my):
        code = my.kwargs.get('data')
        if not code:
            my.data = {}
            return
        
        # preprocess using mako
        #include_mako = my.kwargs.get("include_mako")
        #if not include_mako:
        #    include_mako = my.view_attrs.get("include_mako")

        from tactic.command import PythonCmd
        python_cmd = PythonCmd(code=code)
        my.data = python_cmd.execute()



    # NOTE: this is so that a custom layout can be used as a filter ....
    # however, this is not ideal because a filter requires a number of
    # methods that should not be present in this class
    def alter_search(my, search):
        script_path = my.get_option("alter_search_script_path")
        script_code = my.get_option("alter_search_script_code")

        from tactic.command import PythonCmd
        if script_path:
            cmd = PythonCmd(script_path=script_path, values=my.values, search=search, show_title=my.show_title)
        elif script_code:
            cmd = PythonCmd(script_code=script_code, values=my.values, search=search, show_title=my.show_title)

        cmd.execute()


    def set_values(my, values):
        my.values = values

    def set_show_title(my, flag):
        my.show_title = flag




    def get_display(my):
        my.sobject = my.get_current_sobject()
        if not my.sobject:
            my.sobject = my.get_sobject_from_kwargs()

        if my.sobject and my.sobject.is_insert():
            return DivWdg()



        if my.sobject:
            my.search_key = SearchKey.get_by_sobject(my.sobject)
            my.kwargs['search_key'] = my.search_key

        else:
            my.search_key = my.kwargs.get('search_key')


        html = my.kwargs.get('html')
        if not html:
            html = ""

        # DEPRECATED
        my.state = my.kwargs.get("state")
        my.state = BaseRefreshWdg.process_state(my.state)
        if not my.state:
            my.state = my.kwargs
            my.state['search_key'] = my.search_key



        my.view = my.kwargs.get('view')
        my.view = my.view.replace("/", ".")
        my.view_folder = ""

        if my.view.startswith("."):
            my.view_folder = my.kwargs.get("__view_folder__")
            if my.view_folder:
                my.view = "%s%s" % (my.view_folder, my.view)

        parts = my.view.split(".")
        my.view_folder = ".".join(parts[:-1])



        if not my.view and not html:
            raise TacticException("No view defined in custom layout")

        # If html is not a string, then convert it?
        if not isinstance(html, basestring):
            html = str(html)

        my.view_attrs = {}

        my.category = my.kwargs.get("category")
        my.search_type = my.kwargs.get("search_type")
        my.encoding = my.kwargs.get("encoding")
        if not my.encoding:
             my.encoding = 'utf-8'
        my.plugin = None


        xml = None

        
        # if html is not provided, then get it from the config
        config = None
        if not html:

            if my.config != None:
                config = my.config
            else:
                config = my.kwargs.get("config")
                if not config:
                    config = my.get_config()



            if not config:
                #div = DivWdg()
                #div.add("No config defined for view [%s] for custom layout" % my.view)
                #return div
                raise TacticException("No config defined for view [%s] for custom layout" % my.view)

            if isinstance(config, WidgetDbConfig):
                config_str = config.get_value("config")
            else:
                config_str = ''

            if config_str.startswith("<html>"):
                html = config_str
                my.def_config = None
            else:
                xml = config.get_xml()

                if my.def_config == None:
                    my.def_config = my.get_def_config(xml)

                # get the view attributes
                if isinstance(config, WidgetConfigView):
                    top_config = config.get_configs()[0]
                else:
                    top_config = config
                view_node = top_config.get_view_node()
                if view_node is None:
                    div = DivWdg("No view node found in xml. Invalid XML entry found")
                    return div
                my.view_attrs = xml.get_attributes(view_node)

                nodes = xml.get_nodes("config/%s/html/*" % my.view)
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


        my.config = config
        #my.def_config = config    # This is unnessary?

        # find out if there is a plugin associated with this
        my.plugin = my.kwargs.get("plugin")
        if not my.plugin or my.plugin == '{}':
            my.plugin = {}



        """
        if not my.plugin and isinstance(my.config, SObject):
            my.plugin = Search.eval("@SOBJECT(config/plugin_content.config/plugin)", my.config, single=True)
        """


        # try to get the sobject if this is in a table element widget
        if my.search_key:
            try:
                # this will raise an exception if it is not in a table element
                sobject = my.get_current_sobject()
            except:
	        sobject = SearchKey.get_by_search_key(my.search_key)
            sobjects = [sobject]
        else:
            try:
                # this will raise an exception if it is not in a table element
                sobject = my.get_current_sobject()
                if sobject:
                    sobjects = [sobject]
                else:
                    sobjects = []
            except:
                sobject = my.sobjects


        my.layout = my.get_layout_wdg()



        # preprocess using mako
        include_mako = my.kwargs.get("include_mako")
        if not include_mako:
            include_mako = my.view_attrs.get("include_mako")


        if xml:
            mako_node = xml.get_node("config/%s/mako" % my.view)
            if mako_node is not None:
                mako_str = xml.get_node_value(mako_node)
                html = "<%%\n%s\n%%>\n%s" % (mako_str, html)



        from pyasm.web import Palette
        num_palettes = Palette.num_palettes()


        #if include_mako in ['true', True]:
        if include_mako not in ['false', False]:
            html = html.replace("&lt;", "<")
            html = html.replace("&gt;", ">")

            html = my.process_mako(html)



        # preparse out expressions

        # use relative expressions - [expr]xxx[/expr]
        p = re.compile('\[expr\](.*?)\[\/expr\]')
        parser = ExpressionParser()
        matches = p.finditer(html)
        for m in matches:
            full_expr = m.group()
            expr = m.groups()[0]
            result = parser.eval(expr, sobjects, single=True, state=my.state)
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
        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_custom_top")


        # create the content div
        content = DivWdg()
        content.add_class("spt_custom_content")
        content.add_style("position: relative")
        top.add(content)
        my.content = content


        is_test = Container.get("CustomLayout::is_test")
        if not is_test:
            is_test = my.kwargs.get("is_test") in [True, 'true']

        if is_test:
            Container.put("CustomLayout::is_test", True)
            my.handle_is_test(content)



        html = my.replace_elements(html)
        content.add(html)

        if xml:
            my.add_behaviors(content, xml)


        # remove all the extra palettes created
        while True:
            extra_palettes = Palette.num_palettes() - num_palettes
            if extra_palettes > 0:
                Palette.pop_palette()
            else:
                break


        if my.kwargs.get("is_refresh"):
            return content
        else:
            return top



    def handle_is_test(my, content):

        content.add_behavior( {
            'type': 'mouseover',
            'cbjs_action': '''
            bvr.src_el.setStyle("border", "solid 1px blue");
            bvr.src_el.setStyle("margin", "-1px");
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

            bvr.src_el.setStyle("border", "none");
            bvr.src_el.setStyle("margin", "0px");
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
        div.add(my.view)
        div.add_class("spt_test")
        div.add_border()
        div.set_box_shadow("1px 1px 1px 1px")
        div.add_style("display: none")
        div.add_style("padding: 3px")
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
        menu = my.get_test_context_menu()
        menus = [menu.get_data()]
        menus_in = {
            'TEST_CTX': menus,
        }
        SmartMenu.attach_smart_context_menu( div, menus_in, False )
        SmartMenu.assign_as_local_activator( div, 'TEST_CTX' )



    def get_test_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Refresh')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'view': my.view,
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
            'view': my.view,
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

        return menu

     






    HEADER = '''<%def name='expr(expr)'><% result = server.eval(expr) %>${result}</%def>'''






    def process_mako(my, html):

        from mako.template import Template
        from mako import exceptions
        html = '%s%s' % (CustomLayoutWdg.HEADER, html)

        # remove CDATA tags
        html = html.replace("<![CDATA[", "")
        html = html.replace("]]>", "")
        #html = html.decode('utf-8')
      
        if my.encoding == 'ascii':
            template = Template(html)
        else:
            template = Template(html, output_encoding=my.encoding, input_encoding=my.encoding)

        # get the api version of the sobject
        if not my.is_table_element:
            if my.sobject_dicts == None:
                my.sobject_dicts = []
                for sobject in my.sobjects:
                    sobject_dict = sobject.get_sobject_dict()
                    my.sobject_dicts.append(sobject_dict)

        if my.sobject:
            sobject = my.sobject.get_sobject_dict()
        else:
            sobject = {}

        if my.plugin:
            if isinstance(my.plugin, dict):
                plugin = my.plugin
            else:
                plugin = my.plugin.get_sobject_dict()
            plugin_code = plugin.get("code")
            plugin_dir = my.server.get_plugin_dir(plugin)
        else:
            plugin_code = ""
            plugin_dir = ""
            plugin = {}
        my.kwargs['plugin_dir'] = plugin_dir
        my.kwargs['plugin_code'] = plugin_code

        try:
            html = template.render(server=my.server, search=Search, sobject=sobject, sobjects=my.sobject_dicts, data=my.data, plugin=plugin, kwargs=my.kwargs)


            # we have to replace all & signs to &amp; for it be proper html
            html = html.replace("&", "&amp;")
            return html
        except Exception, e:
            if str(e) == """'str' object has no attribute 'caller_stack'""":
                raise TacticException("Mako variable 'context' has been redefined.  Please use another variable name")
            else:
                print "Error in view [%s]: " % my.view, exceptions.text_error_template().render()
                #html = exceptions.html_error_template().render(css=False)
                html = exceptions.html_error_template().render()
                html = html.replace("body { font-family:verdana; margin:10px 30px 10px 30px;}", "")
                return html

    def handle_layout_behaviors(my, layout):
        '''required for BaseTableElementWdg used by fast table'''
        pass


    def add_test(my, xml):
        # add a test env in
        text_node = xml.get_nodes("config/%s/test" % my.view)




    def add_kwargs(my, widget, xml):
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


        kwargs_nodes = xml.get_nodes("config/%s/kwargs/kwarg" % my.view)
        for kwarg_node in kwargs_node:
            pass




    def add_behaviors(my, widget, xml):

        behavior_nodes = xml.get_nodes("config/%s/behavior" % my.view)

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
                    bvr['kwargs'] = my.kwargs
                    bvr['class_name'] = Common.get_full_class_name(my)


                    if relay_class:
                        bvr['bvr_match_class'] = relay_class
                        if not bvr.get("type"):
                            bvr['type'] = 'mouseup'
                        my.content.add_relay_behavior( bvr )
                    else:
                        bvr['_handoff_'] = '@.getParent(".spt_custom_content").getElements(".%s")' % css_class
                        if not bvr.get("type"):
                            bvr['type'] = 'click_up'
                        bvr_div.add_behavior( bvr )

                except Exception, e:
                    print "Error: ", e
                    raise TacticException("Error parsing behavior [%s]" % behavior_str)


    def get_config(my):
        config = None
        config_xml = my.kwargs.get('config_xml')
        if config_xml:
            config = WidgetConfig.get(xml=config_xml, view=my.view)
            return config


        # this is the new preferred way of defining CustomLayoutWdg
        search = Search("config/widget_config")
        if my.category:
            search.add_filter("category", my.category)
        else:
            search.add_filter("category", 'CustomLayoutWdg')
        if my.search_type:
            search.add_filter("search_type", my.search_type)

        search.add_filter("view", my.view)

        config = search.get_sobject()
        if config:
            return config
        # if it is not defined in the database, look at a config file
        
        includes = my.kwargs.get("include")
        if includes:
            includes = includes.split("|")

            for include in includes:
                tmp_path = __file__
                dir_name = os.path.dirname(tmp_path)
                file_path="%s/../config/%s" % (dir_name, include)
                config = WidgetConfig.get(file_path=file_path, view=my.view)
                if config and config.has_view(my.view):
                    return config

        # deprecated approach, assuming a "CustomLayoutWdg" as search_type,
        # is deprecated
        if not config:
            search = Search("config/widget_config")
            if my.category:
                search.add_filter("category", my.category)
            if my.search_type:
                search.add_filter("search_type", "CustomLayoutWdg")

            search.add_filter("view", my.view)

            config = search.get_sobject()
        
        #if not config and my.search_type and my.view:
        #    config = WidgetConfigView.get_by_search_type(my.search_type, my.view)
        # this is the new preferred way of defining CustomLayoutWdg
        # NOTE: this finds a definition where search type is not explicitly
        # given>
        if not config:
            search = Search("config/widget_config")
            search.add_filter("view", my.view)
            search.add_filter("search_type", None)
            config = search.get_sobject()


        return config



    def get_def_config(my, def_xml=None):
        def_confg = None

        my.def_view = my.kwargs.get('definition')
        if my.def_view:
            #raise TacticException("No definition view defined in custom layout with view [%s]" % my.view)

            my.search_type = "CustomLayoutWdg"
            search = Search("config/widget_config")
            search.add_filter("search_type", my.search_type)
            search.add_filter("view", my.def_view)
            def_db_config = search.get_sobject()
            if not def_db_config:
                raise TacticException("Definition config [%s] not defined" % my.def_view)
            def_xml = def_db_config.get_xml()
            def_config = WidgetConfig.get("definition", xml=def_xml)


        # also look inline to see if there are any definitions        
        if def_xml:
            # just use the passed in xml for a definition
            def_config = WidgetConfig.get(my.view, xml=def_xml)


        return def_config

   
    def replace_elements(my, html_str):

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
                element_wdg = my.get_element_wdg(xml, my.def_config)
                element_html = element_wdg.get_buffer_display()
            except Exception, e:
                from pyasm.widget import ExceptionWdg
                element_html = ExceptionWdg(e).get_buffer_display()

            xml = Xml()
            try:
                xml.read_string(element_html)
            except Exception, e:
                print "Error: ", e
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

            except XmlException, e:
                parse_context = 'element'
                #raise e
                continue

            try:
                element_wdg = my.get_element_wdg(xml, my.def_config)
                if element_wdg:
                    element_html = element_wdg.get_buffer_display()
                else:
                    element_html = ''
            except Exception, e:
                from pyasm.widget import ExceptionWdg
                element_html = ExceptionWdg(e).get_buffer_display()

            # Test to ensure that the html produced is "xml" conforming
            """
            try:
                new_xml = Xml()
                new_xml.read_string(element_html)
            except Exception, e:
                f = open("/tmp/error", 'w')
                f.write(element_html)
                f.close()
                #print element_html
                print "Error: ", e
            """

            if element_html:
                html.writeln(element_html)

        sequence_wdg = my.get_sequence_wdg()
        html.writeln(sequence_wdg.get_buffer_display() )
        

        return html.to_string()





    # FIXME: this is all necessary because CustomLayoutWdg is not derived from
    # BaseTableElementWdg ...  CustomLayoutWdg should probably not be used
    # as a table elementj
    # NOTE: Use tactic.ui.table.CustomLayoutElementWdg for adding custom layouts
    # to layouts
    def set_parent_wdg(my, name):
        pass
    def is_in_column(my):
        return True
    def is_groupable(my):
        return False

    def set_layout_wdg(my, widget):
        my.layout_wdg = widget
    def get_layout_wdg(my):
        return my.layout_wdg 


    def get_title(my):
        '''Returns a widget containing the title to be displayed for this
        column'''
        if my.title:
            title = my.title
            return title

        title = my.name
        if not title:
            title = ""
            return title

        title = Common.get_display_title(title)
        return title


    def get_value(my):
        return None

    def get_text_value(my):
        '''for csv export'''
        sobject = my.get_current_sobject()
        text_expr = my.kwargs.get("text_value")
        text_expr = "@GET(.id)"
        if not text_expr:
            return ''
        value = Search.eval(text_expr, sobject, single=True)
        return value

    def is_sortable(my):
        return False
    def is_searchable(my):
        return False
    def handle_th(my, th, xx=None):
        pass
    def handle_td(my, td):
        pass
    def handle_tr(my, tr):
        pass
    def is_editable(my):
        return False
    def get_bottom_wdg(my):
        return None
    def get_group_bottom_wdg(my, sobjects=None):
        return None
    def get_header_option_wdg(my):
        return None
    def get_generator(my):
        return my.generator_element
    def set_generator(my, element_name):
        my.generator_element = element_name

    ## END TableElementWdg methods

 

    def get_sequence_wdg(my):

        funcs = []

        div = DivWdg()
        if not my.sequence_data:
            return div

        div.add_behavior( {
            'type': 'load',
            'data': my.sequence_data,
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

 


    def get_async_element_wdg(my, xml, element_name, load):

        tmp_config = WidgetConfig.get('tmp', xml=xml)
        display_handler = tmp_config.get_display_handler(element_name)
        display_options = tmp_config.get_display_options(element_name)

        div = DivWdg()
        unique_id = div.set_unique_id()

        if load == "sequence":
            my.sequence_data.append( {
                'class_name': display_handler,
                'kwargs': display_options,
                'unique_id': unique_id
            } )
        else:
            div.add_behavior( {
                'type': 'load',
                'class_name': display_handler,
                'kwargs': display_options,
                'cbjs_action': '''
                spt.panel.async_load(bvr.src_el, bvr.class_name, bvr.kwargs);
                '''
            } )

        loading_div = DivWdg()
        loading_div.add_style("margin: auto auto")
        loading_div.add_style("width: 150px")
        loading_div.add_style("text-align: center")
        loading_div.add_style("padding: 20px")
        div.add(loading_div)
        loading_div.add('''<img src="/context/icons/common/indicator_snake.gif" border="0"/> <b>Loading ...</b>''')

        return div



    def get_element_wdg(my, xml, def_config):

        element_node = xml.get_node("config/tmp/element")
        attrs = Xml.get_attributes(element_node)
        element_name = attrs.get("name")


        if not element_name:
            import random
            num = random.randint(0, 100000)
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
                my.config = WidgetConfigView.get_by_search_type(search_type, view)
                # check if definition has no name.  Don't use element_name
                if not attrs.get("name"):
                    return

                element_wdg = my.config.get_display_widget(element_name, extra_options=attrs)
                container = DivWdg()
                container.add(element_wdg)
                return container

            if not view:
                element_wdg = my.config.get_display_widget(element_name, extra_options=attrs)
                container = DivWdg()
                container.add(element_wdg)
                return container







            # look at the attributes
            class_name = attrs.get("display_class")
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
        if load in ["async", "sequence"]:
            return my.get_async_element_wdg(xml, element_name, load)




        use_container = attrs.get('use_container') == 'true'
        if use_container:
            # DEPRECATED
            container = my.get_container(xml)
        else:
            container = DivWdg()

        # add in attribute from the element definition
        # DEPRECATED: does this make any sense to have this here?
        for name, value in attrs.items():
            if name == 'name':
                continue
            container.add_style(name, value)






        # add the content
        try:
            view_node = xml.get_node("config/tmp/element/display/view")
            if view_node is not None:
                view = xml.get_node_value(view_node)
                if view.startswith("."):
                    if my.view_folder:
                        xml.set_node_value(view_node, "%s%s" %(my.view_folder,view))
            tmp_config = WidgetConfig.get('tmp', xml=xml)
            configs = []
            configs.append(tmp_config)

            # add the def_config if it exists
            if def_config:
                configs.append(def_config)

            config = WidgetConfigView('CustomLayoutWdg', 'tmp', configs, state=my.state)

            # NOTE: this doesn't work too well when we go to an abasolute
            # view.
            parent_view = my.kwargs.get("parent_view")
            if parent_view:
                parent_view = parent_view.replace(".", "/")
                parent_view = "%s/%s" % (parent_view, my.view)
            else:
                parent_view = my.view

            # NOTE: need some protection code for infinite loops


            includes = my.kwargs.get("include")
            element_wdg = config.get_display_widget(element_name, extra_options={"include":includes, "parent_view":parent_view})

            element_top = element_wdg.get_top()
            for name, value in attrs.items():
                if name == 'class':
                    for item in value.split(" "):
                        element_top.add_class(item)

                elif name == 'style':
                    for item in value.split(";"):
                        element_top.add_style(item)

                else:
                    element_top.set_attr(name, value)




            # make a provision if this custom widget is in a table
            if my.layout:
                sobject = my.get_current_sobject()
                element_wdg.set_sobject(sobject)



        except Exception, e:
            from pyasm.widget import ExceptionWdg
            log = ExceptionWdg(e)
            element_wdg = log

        container.add(element_wdg)
        return container



    def get_container(my, xml):
        # handle the container

        element_node = xml.get_node("config/tmp/element")
        attrs = Xml.get_attributes(element_node)
        element_name = attrs.get("name")

        show_resize_scroll = attrs.get("show_resize_scroll")
        if not show_resize_scroll:
            show_resize_scroll = my.kwargs.get("show_resize_scroll")
        if not show_resize_scroll:
            show_resize_scroll = "false"


        # look for attributes in the element tag for specifying a title action button to plug
        # into the title bar of the custom section ...
        #
        title_action_icon = attrs.get("title_action_icon")
        title_action_script = attrs.get("title_action_script")
        title_action_label = attrs.get("title_action_label")
        if title_action_script and not title_action_label:
            title_action_label = '[action]'


        # get the width and height for the element content ...
        width = attrs.get("width")
        height = attrs.get("height")


        if width and height:
            container = ContainerWdg( inner_width=width, inner_height=height, show_resize_scroll=show_resize_scroll )
        else:
            container = ContainerWdg(show_resize_scroll=show_resize_scroll)

        # create the title
        title = attrs.get("title")
        if not title:
            title = Common.get_display_title(element_name)
        title_wdg = DivWdg()
        SmartMenu.assign_as_local_activator( title_wdg, 'HEADER_CTX' )
        title_wdg.add_style("margin: 0px 0px 5px 0px")
        title_wdg.add_gradient("background", "background", 0)
        title_wdg.add_color("color", "color")
        title_wdg.add_style("padding", "5px")


        if title_action_script:
            # add an action button if an action script code was found in the attributes of the element
            proj = Project.get_project_code()
            script_search = Search("config/custom_script")
            script_sobj = script_search.get_by_search_key( "config/custom_script?project=%s&code=%s" %
                                                           (proj, title_action_script) )
            script = script_sobj.get_value('script')
            icon_str = "HELP"
            if title_action_icon:
                icon_str = title_action_icon
            action_btn = HtmlElement.img( IconWdg.get_icon_path(icon_str) )
            action_btn.set_attr('title',title_action_label)
            # action_btn = IconWdg( title_action_label, icon=icon)
            action_btn.add_behavior( {'type': 'click_up', 'cbjs_action':  script } )
            action_btn.add_styles( "cursor: pointer; float: right;" )

            title_wdg.add( action_btn )


        title_wdg.add(title)
        container.add(title_wdg)

        return container







    def get_smart_header_context_menu_data(my):
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

    def get_display(my):
        my.top.add(my.kwargs)
        my.top.add("<hr/>")
        if my.sobjects:
            my.top.add(my.sobjects[0].get_code())
        else:
            my.top.add("No sobjects")
        return my.top



# DEPRECATED

class ContainerWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            'inner_width': 'Inner width, sans rounded corner wrapper ... numeric value only',
            'inner_height': 'Inner height, sans rounded corner wrapper ... numeric value only',
            'show_resize_scroll': 'true|false: determines whether to show scroll bars or not'
        }


    def init(my):

        my.top = DivWdg()
        my.content_wdg = DivWdg()

        is_IE = WebContainer.get_web().is_IE()

        # get the width and height of the contents (the inner part of the container) ...
        my.inner_width = my.kwargs.get('inner_width')
        my.inner_height = my.kwargs.get('inner_height')

        if my.inner_width:
            my.inner_width = int(my.inner_width)
            if is_IE:
                my.inner_width -= 20  # adjust for rounded corner wrapper
        else:
            my.inner_width = 600
        if my.inner_height:
            my.inner_height = int(my.inner_height)
            if is_IE:
                my.inner_height -= 20  # adjust for rounded corner wrapper
        else:
            my.inner_height = 200

        # Now place a ResizeScrollWdg within a RoundedCornerDivWdg ... the ResizeScrollWdg will contain
        # the actual contents of this container, so that the contents can be scrolled and resized ...
        #
        from tactic.ui.container import RoundedCornerDivWdg
        color = my.top.get_color("background")
        my.rc_wdg = RoundedCornerDivWdg(hex_color_code=color,corner_size=10)

        #show_scrollbars = my.kwargs.get("show_resize_scroll")
        #if show_scrollbars in ['', 'false']:
        #    my.inner_wdg = DivWdg()
        #else:
        #    from tactic.ui.container import ResizeScrollWdg
        #    my.inner_wdg = ResizeScrollWdg( width=my.inner_width, height=my.inner_height, scroll_bar_size_str='medium', scroll_expansion='inside' )
        my.inner_wdg = DivWdg()
        my.inner_wdg.add_style("width: %s" % my.inner_width)
        my.inner_wdg.add_style("height: %s" % my.inner_height)
        my.inner_wdg.add_style("overflow-y: auto")
        my.inner_wdg.add_style("overflow-x: hidden")

        my.rc_wdg.add( my.inner_wdg )

        my.content_wdg.add(my.rc_wdg)


        my.table = Table(css="minimal")
        my.table.add_row()
        my.content_td = my.table.add_cell()
        my.content_td.add_class("spt_content")
        my.content_td.add_style('padding: 2px')



    def add_style(my, name, value=None):
        if name.startswith("height"):
            my.content_td.add_style(name, value)
        elif name.startswith("width"):
            my.content_td.add_style(name, value)
        else:
            my.top.add_style(name, value)


    def get_display(my):

        # fill in the content widget
        for widget in my.widgets:
            my.inner_wdg.add(widget)

        my.top.add_class("spt_container")

        my.content_wdg.add_style("float: left")

        # -- DO NOT SET THE WIDTH AND HEIGHT of the content_wdg! Commenting out these lines ...
        # my.content_wdg.add_style("width: 100%")
        # my.content_wdg.add_style("height: 100%")


        # add the content
        my.content_td.add_style("vertical-align: top")
        my.content_td.add(my.content_wdg)

        my.top.add(my.table)

        return my.top


    def get_divider_wdg(my, activator, mode='vertical'):
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




class SObjectHeaderWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        "parent_key": "the search key of the sobject that the header will display"
        }



    def get_display(my):

        search_key = my.kwargs.get('parent_key')

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











