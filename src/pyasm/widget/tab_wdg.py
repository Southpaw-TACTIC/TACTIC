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

__all__ = ['TabWdg', 'DynTabWdg','TabExtendWdg']

import types, sys, re

from pyasm.common import Common, Marshaller, Container, Environment, Xml
from pyasm.web import Widget, WebContainer, WidgetSettings, HtmlElement, \
        SpanWdg, DivWdg, AjaxLoader, MethodWdg, ClassWdg
from input_wdg import HiddenWdg, PopupMenuWdg

from pyasm.prod.biz import ProdSetting
from pyasm.biz import Project


# DEPRECATED: use tactic.ui.container.TabWdg


class TabWdg(Widget):
    '''The standard widget to display tabs.  Most sites use this widget as
    the outer container widget for navigation.  It has special exception
    handling code to ensure the even if a stack trace occurs within it,
    the tabs are still displayed.
    
    Note: TabWdg respects whether there is a database in existence, so this
    widget can be used in SimpleAppServer'''

    # there are 2 tab sizes
    REG = 'regular'
    SMALL = 'small'
    TAB_REDIRECT = 'tab_redirect'
    def __init__(self, dynamic_load=0, tab_key="tab", css=REG):

        self.tab_names = []
        self.wdg_dict = {}
        self.dynamic_load = dynamic_load
        self.set_tab_key(tab_key)
        self.tab_style = css
        self.content_height = 0

        self.mode = Container.get("tab_mode")

        # setting tab path
        self.tab_path = Container.get("tab_path")
        if not self.tab_path:
            self.tab_path = "Main"

        self.error_wdg = None
        self.div = DivWdg(css='left_content')

        if Environment.has_tactic_database():
            self.invisible_list = ProdSetting.get_seq_by_key('invisible_tabs')
        else:
            self.invisible_list = []

        super(TabWdg,self).__init__()

    def class_init(self):
        '''this is used for tab redirection. The set_redirect() takes
        presecedence'''
        tab_redirect = HiddenWdg(self.TAB_REDIRECT)
        self.div.add(tab_redirect)


    def set_mode(mode):
        assert mode in ['normal', 'check']
        Container.put("tab_mode", mode)
    set_mode = staticmethod(set_mode)

    def get_tab_names(self):
        return self.tab_names
    
    def get_tab_key(self):
        return self.tab_key

    def get_tab_value(self):
        return self.tab_value

    def set_tab_style(self, style):
        self.tab_style = style

    def set_content_height(self, height):
        self.content_height = height


    def set_tab_key(self,tab_key):
        ''' set the name of the tab for redirection. If one value is passed in,
        it assumes it's one the current set of subtabs. To jump to a tab from 
        a totally different category, pass in a dict using set_redirect or 
        get_redirect_script'''
        web = WebContainer.get_web()
        self.tab_key = tab_key
        redirect = Container.get(self.TAB_REDIRECT)
        if not redirect:
            # find it from the web form
            redirect = web.get_form_value(self.TAB_REDIRECT)
            if redirect:
                redirect_dict = {}
                redirect = redirect.split(',')
                # expecting key, value pairs
                for idx, item in enumerate(redirect):
                    if idx % 2 == 0:
                        redirect_dict[item] = redirect[idx+1]
        
                redirect = redirect_dict

        if redirect:
            
            if isinstance(redirect, dict):
                for key, value in redirect.items():
                    # set only the relevant key
                    if key == tab_key:
                        web.set_form_value(key, value)
                        break
            else:
                web.set_form_value(tab_key, redirect)
                
            web.set_form_value('is_form_submitted','init')

        # this implicitly sets the tab value
        class_name = self.__class__.__name__
        self.tab_value = WidgetSettings.get_key_value(class_name,self.tab_key)


    def handle_exception(self, e):
        '''The tab widget is a special widget concerning exceptions because
        it usually represents the outer skin of the content of the web page.
        The titles of the tab must be displayed in order for the site to remain
        functional in the case of an exception'''
        from web_wdg import ExceptionWdg
        widget = ExceptionWdg(e)
        self.error_wdg = Widget()
        self.error_wdg.add(widget)
        

        



    def init(self):
        try:
            super(TabWdg,self).init()
        except Exception as e:
            self.handle_exception(e)



    def do_search(self):
        try:
            super(TabWdg,self).do_search()
        except Exception as e:
            self.handle_exception(e)



    def add_widget(self,widget,title=None):
        return self.add(widget,title)

    def add(self,widget,title=None,index=None):
        if title == None:
            title = widget.__class__.__name__

        # determine the url and check security
        # DEPRECATED!!!! use "tab" security
        url_selector = WebContainer.get_web().get_request_url().get_selector()
        check = "%s|%s" % (url_selector,title)

        # check tab security
        if self.mode != "check":
            security = WebContainer.get_security()
            if not security.check_access("url", check, "view"):
                return
            # new security mechanism
            if not security.check_access("tab_title", title, "view"):
                return
            # new, new security mechanism
            tab_path = self.get_tab_path(title)
            if not security.check_access("tab", tab_path, "view"):
                return

            # check if this tab is invisible
            if not self.check_visibility(tab_path):
                return

        if index == None:
            self.tab_names.append(title)
        else:
            self.tab_names.insert(index,title)

        self.wdg_dict[title] = widget
        # for tabs, the widget passed in can be None.  Only the
        # title is added
        if widget == None:
            return

        # only the selected one really gets added
        if not self.tab_value or title == self.tab_value:
            Container.put("tab_path", self.get_tab_path(title))

            widget = self.init_widget(widget, title)
            # the very first time user click on the main tab
            if not self.tab_value:
                self.tab_value = title

            super(TabWdg,self)._add_widget(widget, title)



    def init_widget(self, widget, title=None):
        ''' instantiate the widget if selected. This can be called externally
            to instantiate any widgets added to a TabWdg'''
        try:
            # if a method was passed in, then execute it
            if self.mode == "check":
                from base_tab_wdg import BaseTabWdg
                try:
                    if not issubclass(widget, BaseTabWdg):
                        return Widget()
                except:
                    return Widget()


            if type(widget) == types.MethodType:
                widget = widget()
            elif isinstance(widget, basestring):
                widget = Common.create_from_class_path(widget)
            elif not isinstance(widget, Widget):
                widget = widget()

            # handle docs for the help widget
            """
            from header_wdg import DocMapping
            from web_wdg import HelpItemWdg
            help_url = ProdSetting.get_value_by_key("project_doc_url")
            if help_url:
                widget.add(HelpItemWdg('SOOT Docs', help_url))
            # add the help item automatically
            doc = DocMapping()
            widget.add(HelpItemWdg('%s Tab' % title, doc.get_mapping(title)))
            """

        # catch all exceptions and log them
        except Exception as e:
            self.handle_exception(e)


        return widget


    def check_visibility(self, tab_path):
        ''' determine if a tab is visible or not '''
        if not Environment.has_tactic_database():
            return True

        if self.invisible_list and tab_path in self.invisible_list:
            return False
        else:
            return True


    def get_tab_path(self, title=None):
        if title:
            if self.tab_path == "Main":
                return title
            else:
                return "%s/%s" % (self.tab_path, title)
        else:
            return self.tab_path


    def get_display(self):

        new_tab_names = self.tab_names
        
        app_css = app_style = None    
        if WebContainer.get_web().get_app_name_by_uri() != 'Browser':
            app_css = 'smaller'
            app_style = 'padding: 0px 2px 3px 2px' 
            
        div = self.div
        div.set_style("margin-top: 10px; margin-bottom: 20px")
        
        # add some spacing
        span = SpanWdg(css='tab_front')
        div.add(span)

        selected_widget = None

        # figure out which is the selected one
        selected_index = 0
        for i in range(0, len(new_tab_names)):
            tab_name = new_tab_names[i]
            if tab_name == self.tab_value:
                selected_index = i
                break

        for i in range(0, len(new_tab_names)):
            tab_name = new_tab_names[i]
            widget = self.get_widget(tab_name)

            tab = SpanWdg()
            if i == selected_index:
                # selected tab
                tab.set_class("%s_selected" %self.get_style_prefix())
                if app_style:
                    tab.add_style(app_style)
                selected_widget = widget
            else:
                # unselected tab
                tab.set_class("%s_unselected" %self.get_style_prefix())
                if app_style:
                    tab.add_style(app_style)
            tab.add( self.get_header(tab_name, selected_index, app_css))
            div.add(tab)

        # FIXME: hide this for now 
        #div.add( self.get_add_tab_wdg() )


        tab_hidden = HiddenWdg(self.tab_key)
        tab_hidden.set_persistence()
        # explicitly records this value for init-type submit
        tab_hidden._set_persistent_values([self.tab_value])

        # TODO: not sure if this is legal ... This is rather redundant,
        # but set_value is a pretty complex function.  In the end this
        # forces it to be set to a value even though widget settings is disabled
        value = tab_hidden.get_value()
        if value:
            tab_hidden.set_value(value)

        div.add(tab_hidden)
        
        
        
        # if an error occured, draw the error 
        if self.error_wdg:
            div.add(self.error_wdg)
        else:
            # display the content
            content_div = HtmlElement.div()
            if self.content_height:
                content_div.add_style("height: %spx" % self.content_height)
                content_div.add_style("padding: 10px 0 10px 0")
                content_div.add_style("overflow: auto")
                content_div.add_style("border-style: solid")
            
            content_div.set_class("%s_content" %self.get_style_prefix())
            content_div.add_style("display: block")

            try:
                content = self.get_content(selected_widget)
                if isinstance( content, Widget):
                    content = content.get_buffer_display()
            except Exception as e:
                self.handle_exception(e)

                # TODO: need some way to make this automatic in Widget.
                #if self.tab_path:
                #    last_buffer = len(self.tab_path)+1
                #    buffer = self.get_buffer_on_exception(last_buffer)
                #else:
                buffer = self.get_buffer_on_exception()

                div.add(buffer)


                content = self.error_wdg

            content_div.add( content )
            div.add(content_div)

        return div

    def get_style_prefix(self):
        if self.tab_style == self.SMALL:
            return "tab_sm"
        else:
            return "tab"
   
    def get_header(self, tab_name, selected_index, app_css):
        #link = HtmlElement.href(tab_name,"?%s=%s" % (self.tab_key,tab_name) )
        link = HtmlElement.js_href("document.form.elements['%s'].value='%s';\
            document.form.is_form_submitted.value='init';document.form.submit()"
            %(self.tab_key, tab_name), tab_name, ref='#')
        if app_css:
            link.add_class(app_css)
        self.add_event_to_header(tab_name, link)
        return link


    def add_event_to_header(self, tab_name, link):
        '''provides the opportunity to add javascript calls to clicking on a
        tab link'''
        pass

    
    def get_content(self, selected_widget):
        return selected_widget


    def get_add_tab_wdg(self):
        span = SpanWdg(css="hand")
        span.add("+Add+")

        from web_wdg import EditLinkWdg
        link = EditLinkWdg(search_type="sthpw/widget_extend", search_id=-1, text="Create New Tab", config_base="tab_extend", action='CreateTabCmd')
        link.set_refresh_mode("page")
        span.add(link)

        popup = PopupMenuWdg("add_tab");
        popup.add("Add New Tab")
        span.add(popup)

        span.add_event("onclick", "toggle_display('add_tab')")

        return span


    # static functions
    
    def set_redirect(tab_name):
        ''' this does simple top level tab redirection if a string is passed in.
        To do multiple-level redirections, tab_name should be a dict.
        e.g. dict[<tab_key>] = <tab_name>'''
        data = tab_name
        Container.put(TabWdg.TAB_REDIRECT, data)

    set_redirect = staticmethod(set_redirect)
   
    def get_redirect_script(tab_dict, is_child=True):
        ''' get the script to redirect to a differernt tab'''
        if not isinstance(tab_dict, dict):
            raise TacticException('a dict is required.')
        if is_child:
            js = ["var a=window.parent.document.form.elements['%s']" %TabWdg.TAB_REDIRECT]
        else:
            js = ["var a=document.form.elements['%s']" %TabWdg.TAB_REDIRECT]
        pair = []
        for key, value in tab_dict.items():
            pair.append('%s,%s' %(key, value))
        line = "a.value='%s'" %(','.join(pair))
        js.append(line)
        return ';'.join(js)
    get_redirect_script = staticmethod(get_redirect_script)




from table_element_wdg import BaseTableElementWdg
class CustomXmlWdg(BaseTableElementWdg):
    '''Creates an widget from xml
    <widget name="Filter">
        <display class="FilterSelectWdg">
            <values>Sc01|Sc02|Sc03</values>
        </display>
    </widget>
    '''
    def __init__(self, xml_string):

        self.xml_string = xml_string
        self.xml = Xml(string=self.xml_string)
        super(CustomXmlWdg, self).__init__()

    def init(self):
        self.widget_class = self.xml.get_value("widget/display/@class")
        self.draw = self.xml.get_value("widget/display/@draw")
        self.title = self.xml.get_value("widget/@name")
        self.name = self.title


        # convert the widget data
        options = {}
        nodes = self.xml.get_nodes("widget/display/*")
        for node in nodes:
            name = node.nodeName
            value = Xml.get_node_value(node)

            if options.has_key(name):
                # turn this into an array
                array = []
                array.append(options.get(name))
                array.append(value)
                options[name] = array
            else:
                options[name] = value

        self.options = options
        self.widget = Common.create_from_class_path(self.widget_class, [self.title])
   


    def get_child_widget_class(self):
        return self.xml.get_value("widget/display/@class")

    def get_child_widget(self):
        return self.widget


    def get_title(self): 
        self.widget = Common.create_from_class_path(self.widget_class, [self.title])
        self.widget.options = self.options
        self.widget.set_title(self.title)
        self.widget.set_name(self.title)
        Container.put_dict("widgets", self.title, self.widget)

        index = self.get_current_index()
        self.widget.set_sobjects(self.sobjects)
        self.widget.set_current_index(index)
        if self.draw == "false":
            return ""
        else:
            return self.widget.get_title()
        

    def get_display_widget(self):
        return self.widget

    def get_display(self):
        self.widget.options = self.options
        self.widget.set_title(self.title)
        self.widget.set_name(self.title)
        self.widget.parent_wdg = self.parent_wdg
        Container.put_dict("widgets", self.title, self.widget)

        index = self.get_current_index()
        self.widget.set_sobjects(self.sobjects)
        self.widget.set_search(self.search)
        self.widget.set_current_index(index)
        if self.draw == "false":
            return None
        else:
            return self.widget
            


class TabExtendWdg(Widget):
    '''class that uses the database to extend widgets'''
    def set_tab(self, parent):
        self.parent_wdg = parent

    def set_search_type(self, search_type):
        self.search_type = search_type


    def get_display(self):

        #parent_class = "TabWdg"
        self.parent_class = self.parent_wdg.__class__.__name__
        if self.parent_class == "TbodyWdg":
            self.parent_class = "TableWdg"
        elif self.parent_class == "MayaTabWdgImpl":
            self.parent_class = "TabWdg"

        # get the key
        if self.parent_class == "TabWdg":
            key = self.parent_wdg.get_tab_path()
        elif self.parent_class == "TableWdg":
            key = "%s|%s" % (self.search_type, self.parent_wdg.get_view() )
        else:
            key = self.parent_wdg.get_name()

        # set sobjects from the parent, if there are any
        self.sobjects = self.parent_wdg.get_sobjects()
        
        # search for these
        from pyasm.search import Search
        search = Search("sthpw/widget_extend")
        search.add_project_filter()
        search.add_filter("type", self.parent_class)
        search.add_filter("key", key)
        extends = search.get_sobjects()

        for extend in extends:
            xml = extend.get_xml_value("data")
            index = xml.get_value("widget/@index")
            if index:
                index = int(index)
            else:
                index = None

            title = xml.get_value("widget/@name")

            nodes = xml.get_nodes("widget/widget")
            if nodes:
                widget = Widget()
                for node in nodes:
                    node_string = Xml.get_node_xml(node)
                    child_widget = CustomXmlWdg(node_string)
                    if not child_widget:
                        continue
                    if self.sobjects:
                        child_widget.set_sobjects(self.sobjects)
                    widget.add(child_widget)


            else:
                widget = CustomXmlWdg(xml.to_string())
                if self.sobjects:
                    widget.set_sobjects(self.sobjects)

            
            if self.parent_class == 'TableWdg':
                table_element = widget.get_display_widget()
                table_element.set_parent_wdg(self.parent_wdg)
            self.parent_wdg.add(widget, title, index=index)
            






class DynTabWdg(TabWdg):
    # there are 2 tab sizes
    REG = 'regular'
    SMALL = 'small'
    XS = 'xsmall' # unused now
    def __init__(self, tab_key="tab", css=REG):
        super(DynTabWdg,self).__init__(True, tab_key, css)
        self.inputs = []
        self.options = {}
        self.preload_script = None
        self.tab_group_name = self.generate_unique_id(tab_key)
        self.content_div_id = "%s|tab_content" % self.tab_group_name
        self.content_div = HtmlElement.div()

    def add_ajax_input(self, widget):
        self.inputs.append(widget)

    def add_preload_script(self, script):
        self.preload_script = script

    def set_option(self, name, value):
        self.options[name] = value

    def get_content_div(self):
        return self.content_div
    
    def add(self,widget,title=None):
        if title == None:
            title = widget.__class__.__name__

        # determine the url and check security
        request_url = WebContainer.get_web().get_request_url()
        base = request_url.get_base()
        if base.endswith("/"):
            base = "%sIndex" % base 
        check = "%s|%s" % (base,title)

        security = WebContainer.get_security()
        if not security.check_access("url", check, "view"):
            return


        if not security.check_access("tab", title, "view"):
            return

        self.tab_names.append(title)

        # for tabs, the widget passed in can be None.  Only the
        # title is added
        assert widget != None

        # only the selected one really gets added
        try:
            # if a method was passed in, then execute it
            if type(widget) == types.MethodType:
                widget = MethodWdg(widget)
            elif isinstance(widget, basestring):
                widget = Common.create_from_class_path(widget)
            elif not isinstance(widget, Widget):
                widget = ClassWdg(widget)
                
        # catch all exceptions and log them
        except Exception as e:
            self.handle_exception(e)

        super(DynTabWdg,self)._add_widget(widget, title)


    def get_display(self):

        div = DivWdg(css='left_content')
        div.set_style("margin-top: 10px; margin-bottom: 20px;")

        # add some spacing
        span = SpanWdg()
        span.set_class('tab_front')
        div.add(span)

        # figure out which is the selected one
        selected_index = 0
        for i in range(0, len(self.tab_names)):
            tab_name = self.tab_names[i]
            if tab_name == self.tab_value:
                selected_index = i
                break
            
        
        for i in range(0, len(self.tab_names)):
            tab_name = self.tab_names[i]
            widget = self.get_widget(tab_name)

            tab = HtmlElement.span()
            tab.set_attr('name', self.tab_group_name)
            # required by IE
            tab.set_id(self.tab_group_name)
            
            tab.set_attr('tab', tab_name)
           
            if i == selected_index:
                # selected tab
                tab.set_class("%s_selected" %self.get_style_prefix())
                self.content_div.add(widget)
            else:
                # unselected tab
                tab.set_class("%s_unselected" %self.get_style_prefix())
            
            tab.add( self.get_header(tab_name) )
            div.add(tab)
       
        

        # display the content
        
        self.content_div.set_id(self.content_div_id)
        self.content_div.set_class("%s_content" %self.get_style_prefix())
        self.content_div.add_style("display: block")
        div.add(self.content_div)

        return div

    def get_style_prefix(self):
        if self.tab_style == self.SMALL:
            return "tab_sm"
        else:
            return "tab"

    def get_ajax_script(self, tab_name):

        widget = self.get_widget(tab_name)    
        # load tab thru ajax
        ajax = AjaxLoader(self.content_div_id)
        
        load_args = None
        widget_class = widget.get_class_name()
        ajax.set_load_class(widget_class, load_args)
        
        if isinstance(widget, MethodWdg):
            ajax.set_option('method',  widget.get_function_name())

        for input in self.inputs:
            ajax.add_element_name(input)

        for name, value in self.options.items():
            ajax.set_option(name, value)
        script = []
        if self.preload_script:
            script.append(self.preload_script)
        script.append(ajax.get_on_script())
        script.append(self._get_update_script(tab_name)) 
         
        return ';'.join(script)

    def get_header(self, tab_name):
        script = self.get_tab_script(tab_name)
        return HtmlElement.js_href(script, tab_name, '#')

    def get_tab_script(self, tab_name):
        
        script = [self.get_ajax_script(tab_name)]
        script.append("var a=get_elements('%s');a.tab_me('%s','%s_selected','%s_unselected');" \
            %(self.tab_group_name, tab_name, self.get_style_prefix(), \
            self.get_style_prefix()))

        return ";".join(script)
    
    def _get_update_script(self, tab_name ):
        '''script to update widget settings'''
        ajax = AjaxLoader('update')
        
        marshaller = ajax.register_cmd("pyasm.command.WidgetSettingsCmd")
        marshaller.set_option("widget_name", self.tab_key)
        #marshaller.set_option("key", self.url.get_base())
        marshaller.set_option("key", self.__class__.__name__)
        marshaller.set_option("value", tab_name)
        
        return ajax.get_on_script(True)

    def get_content(self, selected_widget):
        return ''

