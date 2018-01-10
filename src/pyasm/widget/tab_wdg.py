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
    def __init__(my, dynamic_load=0, tab_key="tab", css=REG):

        my.tab_names = []
        my.wdg_dict = {}
        my.dynamic_load = dynamic_load
        my.set_tab_key(tab_key)
        my.tab_style = css
        my.content_height = 0

        my.mode = Container.get("tab_mode")

        # setting tab path
        my.tab_path = Container.get("tab_path")
        if not my.tab_path:
            my.tab_path = "Main"

        my.error_wdg = None
        my.div = DivWdg(css='left_content')

        if Environment.has_tactic_database():
            my.invisible_list = ProdSetting.get_seq_by_key('invisible_tabs')
        else:
            my.invisible_list = []

        super(TabWdg,my).__init__()

    def class_init(my):
        '''this is used for tab redirection. The set_redirect() takes
        presecedence'''
        tab_redirect = HiddenWdg(my.TAB_REDIRECT)
        my.div.add(tab_redirect)


    def set_mode(mode):
        assert mode in ['normal', 'check']
        Container.put("tab_mode", mode)
    set_mode = staticmethod(set_mode)

    def get_tab_names(my):
        return my.tab_names
    
    def get_tab_key(my):
        return my.tab_key

    def get_tab_value(my):
        return my.tab_value

    def set_tab_style(my, style):
        my.tab_style = style

    def set_content_height(my, height):
        my.content_height = height


    def set_tab_key(my,tab_key):
        ''' set the name of the tab for redirection. If one value is passed in,
        it assumes it's one the current set of subtabs. To jump to a tab from 
        a totally different category, pass in a dict using set_redirect or 
        get_redirect_script'''
        web = WebContainer.get_web()
        my.tab_key = tab_key
        redirect = Container.get(my.TAB_REDIRECT)
        if not redirect:
            # find it from the web form
            redirect = web.get_form_value(my.TAB_REDIRECT)
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
        class_name = my.__class__.__name__
        my.tab_value = WidgetSettings.get_key_value(class_name,my.tab_key)


    def handle_exception(my, e):
        '''The tab widget is a special widget concerning exceptions because
        it usually represents the outer skin of the content of the web page.
        The titles of the tab must be displayed in order for the site to remain
        functional in the case of an exception'''
        from web_wdg import ExceptionWdg
        widget = ExceptionWdg(e)
        my.error_wdg = Widget()
        my.error_wdg.add(widget)
        

        



    def init(my):
        try:
            super(TabWdg,my).init()
        except Exception as e:
            my.handle_exception(e)



    def do_search(my):
        try:
            super(TabWdg,my).do_search()
        except Exception as e:
            my.handle_exception(e)



    def add_widget(my,widget,title=None):
        return my.add(widget,title)

    def add(my,widget,title=None,index=None):
        if title == None:
            title = widget.__class__.__name__

        # determine the url and check security
        # DEPRECATED!!!! use "tab" security
        url_selector = WebContainer.get_web().get_request_url().get_selector()
        check = "%s|%s" % (url_selector,title)

        # check tab security
        if my.mode != "check":
            security = WebContainer.get_security()
            if not security.check_access("url", check, "view"):
                return
            # new security mechanism
            if not security.check_access("tab_title", title, "view"):
                return
            # new, new security mechanism
            tab_path = my.get_tab_path(title)
            if not security.check_access("tab", tab_path, "view"):
                return

            # check if this tab is invisible
            if not my.check_visibility(tab_path):
                return

        if index == None:
            my.tab_names.append(title)
        else:
            my.tab_names.insert(index,title)

        my.wdg_dict[title] = widget
        # for tabs, the widget passed in can be None.  Only the
        # title is added
        if widget == None:
            return

        # only the selected one really gets added
        if not my.tab_value or title == my.tab_value:
            Container.put("tab_path", my.get_tab_path(title))

            widget = my.init_widget(widget, title)
            # the very first time user click on the main tab
            if not my.tab_value:
                my.tab_value = title

            super(TabWdg,my)._add_widget(widget, title)



    def init_widget(my, widget, title=None):
        ''' instantiate the widget if selected. This can be called externally
            to instantiate any widgets added to a TabWdg'''
        try:
            # if a method was passed in, then execute it
            if my.mode == "check":
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
            my.handle_exception(e)


        return widget


    def check_visibility(my, tab_path):
        ''' determine if a tab is visible or not '''
        if not Environment.has_tactic_database():
            return True

        if my.invisible_list and tab_path in my.invisible_list:
            return False
        else:
            return True


    def get_tab_path(my, title=None):
        if title:
            if my.tab_path == "Main":
                return title
            else:
                return "%s/%s" % (my.tab_path, title)
        else:
            return my.tab_path


    def get_display(my):

        new_tab_names = my.tab_names
        
        app_css = app_style = None    
        if WebContainer.get_web().get_app_name_by_uri() != 'Browser':
            app_css = 'smaller'
            app_style = 'padding: 0px 2px 3px 2px' 
            
        div = my.div
        div.set_style("margin-top: 10px; margin-bottom: 20px")
        
        # add some spacing
        span = SpanWdg(css='tab_front')
        div.add(span)

        selected_widget = None

        # figure out which is the selected one
        selected_index = 0
        for i in range(0, len(new_tab_names)):
            tab_name = new_tab_names[i]
            if tab_name == my.tab_value:
                selected_index = i
                break

        for i in range(0, len(new_tab_names)):
            tab_name = new_tab_names[i]
            widget = my.get_widget(tab_name)

            tab = SpanWdg()
            if i == selected_index:
                # selected tab
                tab.set_class("%s_selected" %my.get_style_prefix())
                if app_style:
                    tab.add_style(app_style)
                selected_widget = widget
            else:
                # unselected tab
                tab.set_class("%s_unselected" %my.get_style_prefix())
                if app_style:
                    tab.add_style(app_style)
            tab.add( my.get_header(tab_name, selected_index, app_css))
            div.add(tab)

        # FIXME: hide this for now 
        #div.add( my.get_add_tab_wdg() )


        tab_hidden = HiddenWdg(my.tab_key)
        tab_hidden.set_persistence()
        # explicitly records this value for init-type submit
        tab_hidden._set_persistent_values([my.tab_value])

        # TODO: not sure if this is legal ... This is rather redundant,
        # but set_value is a pretty complex function.  In the end this
        # forces it to be set to a value even though widget settings is disabled
        value = tab_hidden.get_value()
        if value:
            tab_hidden.set_value(value)

        div.add(tab_hidden)
        
        
        
        # if an error occured, draw the error 
        if my.error_wdg:
            div.add(my.error_wdg)
        else:
            # display the content
            content_div = HtmlElement.div()
            if my.content_height:
                content_div.add_style("height: %spx" % my.content_height)
                content_div.add_style("padding: 10px 0 10px 0")
                content_div.add_style("overflow: auto")
                content_div.add_style("border-style: solid")
            
            content_div.set_class("%s_content" %my.get_style_prefix())
            content_div.add_style("display: block")

            try:
                content = my.get_content(selected_widget)
                if isinstance( content, Widget):
                    content = content.get_buffer_display()
            except Exception as e:
                my.handle_exception(e)

                # TODO: need some way to make this automatic in Widget.
                #if my.tab_path:
                #    last_buffer = len(my.tab_path)+1
                #    buffer = my.get_buffer_on_exception(last_buffer)
                #else:
                buffer = my.get_buffer_on_exception()

                div.add(buffer)


                content = my.error_wdg

            content_div.add( content )
            div.add(content_div)

        return div

    def get_style_prefix(my):
        if my.tab_style == my.SMALL:
            return "tab_sm"
        else:
            return "tab"
   
    def get_header(my, tab_name, selected_index, app_css):
        #link = HtmlElement.href(tab_name,"?%s=%s" % (my.tab_key,tab_name) )
        link = HtmlElement.js_href("document.form.elements['%s'].value='%s';\
            document.form.is_form_submitted.value='init';document.form.submit()"
            %(my.tab_key, tab_name), tab_name, ref='#')
        if app_css:
            link.add_class(app_css)
        my.add_event_to_header(tab_name, link)
        return link


    def add_event_to_header(my, tab_name, link):
        '''provides the opportunity to add javascript calls to clicking on a
        tab link'''
        pass

    
    def get_content(my, selected_widget):
        return selected_widget


    def get_add_tab_wdg(my):
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
    def __init__(my, xml_string):

        my.xml_string = xml_string
        my.xml = Xml(string=my.xml_string)
        super(CustomXmlWdg, my).__init__()

    def init(my):
        my.widget_class = my.xml.get_value("widget/display/@class")
        my.draw = my.xml.get_value("widget/display/@draw")
        my.title = my.xml.get_value("widget/@name")
        my.name = my.title


        # convert the widget data
        options = {}
        nodes = my.xml.get_nodes("widget/display/*")
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

        my.options = options
        my.widget = Common.create_from_class_path(my.widget_class, [my.title])
   


    def get_child_widget_class(my):
        return my.xml.get_value("widget/display/@class")

    def get_child_widget(my):
        return my.widget


    def get_title(my): 
        my.widget = Common.create_from_class_path(my.widget_class, [my.title])
        my.widget.options = my.options
        my.widget.set_title(my.title)
        my.widget.set_name(my.title)
        Container.put_dict("widgets", my.title, my.widget)

        index = my.get_current_index()
        my.widget.set_sobjects(my.sobjects)
        my.widget.set_current_index(index)
        if my.draw == "false":
            return ""
        else:
            return my.widget.get_title()
        

    def get_display_widget(my):
        return my.widget

    def get_display(my):
        my.widget.options = my.options
        my.widget.set_title(my.title)
        my.widget.set_name(my.title)
        my.widget.parent_wdg = my.parent_wdg
        Container.put_dict("widgets", my.title, my.widget)

        index = my.get_current_index()
        my.widget.set_sobjects(my.sobjects)
        my.widget.set_search(my.search)
        my.widget.set_current_index(index)
        if my.draw == "false":
            return None
        else:
            return my.widget
            


class TabExtendWdg(Widget):
    '''class that uses the database to extend widgets'''
    def set_tab(my, parent):
        my.parent_wdg = parent

    def set_search_type(my, search_type):
        my.search_type = search_type


    def get_display(my):

        #parent_class = "TabWdg"
        my.parent_class = my.parent_wdg.__class__.__name__
        if my.parent_class == "TbodyWdg":
            my.parent_class = "TableWdg"
        elif my.parent_class == "MayaTabWdgImpl":
            my.parent_class = "TabWdg"

        # get the key
        if my.parent_class == "TabWdg":
            key = my.parent_wdg.get_tab_path()
        elif my.parent_class == "TableWdg":
            key = "%s|%s" % (my.search_type, my.parent_wdg.get_view() )
        else:
            key = my.parent_wdg.get_name()

        # set sobjects from the parent, if there are any
        my.sobjects = my.parent_wdg.get_sobjects()
        
        # search for these
        from pyasm.search import Search
        search = Search("sthpw/widget_extend")
        search.add_project_filter()
        search.add_filter("type", my.parent_class)
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
                    if my.sobjects:
                        child_widget.set_sobjects(my.sobjects)
                    widget.add(child_widget)


            else:
                widget = CustomXmlWdg(xml.to_string())
                if my.sobjects:
                    widget.set_sobjects(my.sobjects)

            
            if my.parent_class == 'TableWdg':
                table_element = widget.get_display_widget()
                table_element.set_parent_wdg(my.parent_wdg)
            my.parent_wdg.add(widget, title, index=index)
            






class DynTabWdg(TabWdg):
    # there are 2 tab sizes
    REG = 'regular'
    SMALL = 'small'
    XS = 'xsmall' # unused now
    def __init__(my, tab_key="tab", css=REG):
        super(DynTabWdg,my).__init__(True, tab_key, css)
        my.inputs = []
        my.options = {}
        my.preload_script = None
        my.tab_group_name = my.generate_unique_id(tab_key)
        my.content_div_id = "%s|tab_content" % my.tab_group_name
        my.content_div = HtmlElement.div()

    def add_ajax_input(my, widget):
        my.inputs.append(widget)

    def add_preload_script(my, script):
        my.preload_script = script

    def set_option(my, name, value):
        my.options[name] = value

    def get_content_div(my):
        return my.content_div
    
    def add(my,widget,title=None):
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

        my.tab_names.append(title)

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
            my.handle_exception(e)

        super(DynTabWdg,my)._add_widget(widget, title)


    def get_display(my):

        div = DivWdg(css='left_content')
        div.set_style("margin-top: 10px; margin-bottom: 20px;")

        # add some spacing
        span = SpanWdg()
        span.set_class('tab_front')
        div.add(span)

        # figure out which is the selected one
        selected_index = 0
        for i in range(0, len(my.tab_names)):
            tab_name = my.tab_names[i]
            if tab_name == my.tab_value:
                selected_index = i
                break
            
        
        for i in range(0, len(my.tab_names)):
            tab_name = my.tab_names[i]
            widget = my.get_widget(tab_name)

            tab = HtmlElement.span()
            tab.set_attr('name', my.tab_group_name)
            # required by IE
            tab.set_id(my.tab_group_name)
            
            tab.set_attr('tab', tab_name)
           
            if i == selected_index:
                # selected tab
                tab.set_class("%s_selected" %my.get_style_prefix())
                my.content_div.add(widget)
            else:
                # unselected tab
                tab.set_class("%s_unselected" %my.get_style_prefix())
            
            tab.add( my.get_header(tab_name) )
            div.add(tab)
       
        

        # display the content
        
        my.content_div.set_id(my.content_div_id)
        my.content_div.set_class("%s_content" %my.get_style_prefix())
        my.content_div.add_style("display: block")
        div.add(my.content_div)

        return div

    def get_style_prefix(my):
        if my.tab_style == my.SMALL:
            return "tab_sm"
        else:
            return "tab"

    def get_ajax_script(my, tab_name):

        widget = my.get_widget(tab_name)    
        # load tab thru ajax
        ajax = AjaxLoader(my.content_div_id)
        
        load_args = None
        widget_class = widget.get_class_name()
        ajax.set_load_class(widget_class, load_args)
        
        if isinstance(widget, MethodWdg):
            ajax.set_option('method',  widget.get_function_name())

        for input in my.inputs:
            ajax.add_element_name(input)

        for name, value in my.options.items():
            ajax.set_option(name, value)
        script = []
        if my.preload_script:
            script.append(my.preload_script)
        script.append(ajax.get_on_script())
        script.append(my._get_update_script(tab_name)) 
         
        return ';'.join(script)

    def get_header(my, tab_name):
        script = my.get_tab_script(tab_name)
        return HtmlElement.js_href(script, tab_name, '#')

    def get_tab_script(my, tab_name):
        
        script = [my.get_ajax_script(tab_name)]
        script.append("var a=get_elements('%s');a.tab_me('%s','%s_selected','%s_unselected');" \
            %(my.tab_group_name, tab_name, my.get_style_prefix(), \
            my.get_style_prefix()))

        return ";".join(script)
    
    def _get_update_script(my, tab_name ):
        '''script to update widget settings'''
        ajax = AjaxLoader('update')
        
        marshaller = ajax.register_cmd("pyasm.command.WidgetSettingsCmd")
        marshaller.set_option("widget_name", my.tab_key)
        #marshaller.set_option("key", my.url.get_base())
        marshaller.set_option("key", my.__class__.__name__)
        marshaller.set_option("value", tab_name)
        
        return ajax.get_on_script(True)

    def get_content(my, selected_widget):
        return ''

