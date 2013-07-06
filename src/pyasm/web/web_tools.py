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

__all__ = ['AjaxLoaderException', 'AjaxLoader', 'AjaxWdg', 'AjaxCmd', 'DragDropWdg', 'WikiUtil']

from pyasm.common import *
from pyasm.web import Widget, WebContainer, DivWdg, WebEnvironment, HtmlElement, SpanWdg
import re, types

class AjaxLoaderException(Exception):
    pass



class AjaxLoader(Base):
    '''helper class to interact with the server by ajax'''
    
    def __init__(my, display_id=None):
        super(AjaxLoader,my).__init__()

        # ensure a unique display id for those who don't wish to manage it
        if not display_id:
            display_id = Widget.generate_unique_id( base='dynamic_display', \
                    wdg='DyanmicLoaderWdg', is_random=True)
           
        my.display_id = display_id
        # define the loaded class
        my.load_class = None
        my.load_args = None
        my.options = {}

        my.element_names = []

        web = WebContainer.get_web()
        my.loader_url = web.get_widget_url()
        my.marshallers = []
        my.is_command = False
        my.loader_url.set_option("ajax", "true")


    def set_option(my, name, value):
        my.options[name] = value

    def get_option(my, name):
        return my.options.get(name)


    def add_element_name(my, element_name):
        '''adds an element name in the dom whose value needs to be passed
        through'''
        my.element_names.append(element_name)


    def register_cmd(my, cmd_class):
        my.is_command = True
        marshaller = Marshaller(cmd_class)
        
        my.marshallers.append( marshaller ) 

        return marshaller


    def set_display_id(my, display_id):
        '''set the id that will be replaced'''
        my.display_id = display_id

    def get_display_id(my):
        return my.display_id


    def generate_div(my):
        ''' this is meant to be called to get the container div for the 
            ajax widget '''
        div = DivWdg()
        div.set_id(my.display_id)
        div.add_style("display: block")
        return div


    def get_loader_url(my):
        return my.loader_url

    def set_load_class(my, load_class, load_args=None):
        '''my.load_args will be converted to a string with a '||' delimiter
        at the end'''
        my.load_class = load_class
        my.load_args = load_args
        if isinstance(load_args, dict):
            my.loader_url.set_option("arg_type", "dict")
            arg_list = []
            for key, value in my.load_args.items():
                arg_list.append('%s=%s'%(key, value))
            my.load_args = '||'.join(arg_list)    


    def set_load_method(my, method_name):
        my.loader_url.set_option("method", method_name)


    def is_refresh(my):
        refresh_id = my.get_refresh_id()

        if refresh_id:
            return True
        else:
            return False

    def get_refresh_id(my):
        '''gets the id of the element that was used to refresh'''
        web = WebContainer.get_web()
        return web.get_form_value("ajax_refresh")




    def get_refresh_script(my, is_cmd=False, show_progress=True, load_once=False):
        # this function differs from get_on_scrpit() in that it should be use
        # for function that will refresh the widget instead of turning the
        return my.get_on_script(is_cmd, show_progress, load_once, is_refresh=True)


    def get_on_script(my, is_cmd=False, show_progress=True, load_once=False, is_refresh=False):

        if is_refresh:
            my.loader_url.set_option('ajax_refresh', my.display_id)
        else:
            my.loader_url.set_option('ajax_refresh', "")
            
        
        for marshaller in my.marshallers:
            my.loader_url.set_option('marshalled', marshaller.get_marshalled())

        if my.load_class == None:
            if my.is_command:
                my.set_load_class("pyasm.widget.CmdReportWdg")
            else:
                raise AjaxLoaderException("Load class is None")

        my.loader_url.set_option('widget', my.load_class)
        
        if my.load_args != None:
            my.loader_url.set_option(WebEnvironment.ARG_NAME, my.load_args)

        for name,value in my.options.items():
            my.loader_url.set_option(name, value)
            
        my.loader_url.add_web_state()
        url = my.loader_url.to_string() 

        # handle element names
        element_names_str = "||".join(my.element_names)
        script = ''
        if show_progress:
            show_progress = 'true'
        else:
            show_progress = 'false'
        if is_cmd:
            script = "AjaxLoader_execute_cmd('%s', '%s', this, '%s','%s');" \
                %(my.display_id, url, element_names_str, show_progress )
        else:
            base_script = "AjaxLoader_load_cbk('%s','%s','%s','%s')" \
                %(my.display_id, url, element_names_str, show_progress)
            if load_once:
                script = "var x=$('%s'); if (x.getAttribute('loaded') !='true') {%s}; set_display_on('%s')"\
                        %(my.display_id, base_script, my.display_id)
            else:
                script = "%s; set_display_on('%s')" %(base_script, my.display_id)
                
        return script

    
    def get_off_script(my):
        return "set_display_off(\'%s\')" % my.display_id




class AjaxWdg(Widget):
    '''functions to make a widget "Ajaxable".   These widgets inherently
    know how to update themselves through ajax.
    These classes have prerequesites:
        - All input elements require names
        - The top node to be replaced has to have an id
    '''
    def __init__(my, check_name=False):
        my.web = WebContainer.get_web()
        my.ajax = None
        super(AjaxWdg,my).__init__()

        if my.is_from_ajax(check_name=check_name):
            my.init_cgi()

        my.top_id = None


    def is_from_ajax(my, check_name=False):
        ajax_class = my.web.get_form_value("widget")
        ajax = my.web.get_form_value("ajax")
        if ajax != "":
            if check_name and ajax_class != Common.get_full_class_name(my):
                return False
            return True
        else:
            return False


    def init_cgi(my):
        '''function that will get the necessary parameters to recreate this
        widget from cgi values'''
        pass

    def reset_ajax(my):
        ''' this could be called in get_display() when the AjaxWdg is used as a BaseTableElement
            depending on implementation'''
        my.ajax = None

    def get_ajax(my):
        if not my.ajax:
            my.ajax = AjaxLoader()
            class_path = Common.get_full_class_name(my)
            my.ajax.set_load_class( class_path )
            my.ajax.set_option("is_form_submitted", "true")
        return my.ajax


    def get_top_id(my):
        return my.top_id

  
    def set_ajax_top_id(my, id):
        my.get_ajax().set_display_id(id)
        my.top_id = id

    def set_ajax_top(my, widget):
        ''' it is mandatory for this widget to have an unique id, especially
        if there are multiple AjaxWdgs instantiated in the same page'''
        ajax = my.get_ajax()

        # get the id of the top widget.  If there is none, then generate one
        top_id = widget.get_id()
        if not top_id:
            top_id = my.generate_unique_id("top_wdg")
            widget.set_id(top_id)
        ajax.set_display_id( top_id )

        # make sure that the display style is set
        widget.add_style("display: block")

        my.top_id = top_id


    def add_ajax_input(my, widget):
        ajax = my.get_ajax()
        ajax.add_element_name( widget.get_input_name() )

    def add_ajax_input_name(my, element_name ):
        ajax = my.get_ajax()
        ajax.add_element_name( element_name )



    def set_ajax_option(my, name, value):
        ajax = my.get_ajax()
        ajax.set_option(name, value)

    def register_cmd(my, cmd_class):
        ajax = my.get_ajax()
        ajax.register_cmd(cmd_class)


    def get_on_script(my, show_progress=True):
        ajax = my.get_ajax() 
        return ajax.get_refresh_script(show_progress=show_progress)
        
    def get_refresh_script(my, show_progress=True):
        ajax = my.get_ajax() 
        return ajax.get_refresh_script(show_progress=show_progress)
        
   
    # class methods
    def get_self_refresh_script(cls, show_progress=True):
        '''this is meant for the simplest widget with an ID attribute.
        The ID is assumed to be the top ajax id. The widget should not 
        require any ajax option or input to construct'''
            
        ajax = AjaxLoader(cls.ID)
        class_path = '%s.%s' %(cls.__module__, cls.__name__)
        ajax.set_load_class( class_path )
        ajax.set_option("is_form_submitted", "true")
        return ajax.get_on_script(show_progress=show_progress)

    get_self_refresh_script=classmethod(get_self_refresh_script)
    
        
class AjaxCmd(AjaxLoader):
    '''An ajax call to execute a tactic command'''
    
    def get_on_script(my, show_progress=True):
        return super(AjaxCmd, my).get_on_script(is_cmd=True, \
            show_progress=show_progress)
        



class DragDropWdg(Widget):
    '''gives the ability for any element to have drag and drop capabilities.
    This is a wrapper around wz_dropdrop.js'''

    def alter_search(my, search):
        '''override this.  These elements should not be getting a search
        at all because they may have already affected a search before.
        This is not completely necessary as the drag drop widget is 
        a global widget and should not get any searches in the first place'''
        pass


    def get_display(my):

        if len(my.widgets) == 0:
            return ""

        script = HtmlElement.script()

        script.add( 'SET_DHTML( ' )
        args = []
        for widget in my.widgets:
            args.append('"%s"' % widget.get_id() )

        script.add( ", ".join(args) )
        script.add( ' )\n' )

        return script.get_display()



class WikiUtil(object):
    '''Converts text into a wiki style'''

    def __init__(my, process_url=False, replace_tag=True):
        my.process_url = process_url
        my.replace_tag = replace_tag

    xxx = 0
        
    def convert(my, text):
        if not type(text) in types.StringTypes:
            text = str(text)
      
        text = my._replace_tag(text)

        # convert <> inside <code/>
        '''
        code_pat = re.compile(r'((?:.|\n)*)(<code>((?:.|\n)*)</code>)((?:.|\n)*)', re.M+re.I)
        m = code_pat.match(text)
        if m:
            group0 = m.groups()[0]
            group1 = m.groups()[1]
            group2 = m.groups()[2]
            group3 = m.groups()[3]
            group2 = my._replace_tag(group2)
            text = '%s<code>%s</code>%s' %(group0, group2, group3)
        else:    
            text = my._replace_linebreak(text)
        '''

        #text = r"%s" %text
        #text = re.sub(r"\\", "/", text)
        if my.process_url:
            proc = "((?:http|ftp)://)"
            url_part = "([a-z0-9\-.]+\.[a-z0-9\-]+)([\/]([a-z0-9_\/\-.?&%=+])*)"
            url_pat = re.compile(proc + url_part, re.IGNORECASE)
            m = url_pat.search(text)
           
            text = re.sub(url_pat, r"<a href='\1\2\3'><u>[\1\2...]</u></a>", text)
        return text


    def _replace_linebreak(my, text):
        text = text.replace("\n", "<br/>")
        return text

    def _replace_tag(my, text):
        text = text.replace("<", "&spt_lt;")
        text = text.replace(">", "&spt_gt;")
        #text = text.replace("<", "&lt;")
        #text = text.replace(">", "&gt;")
        text = text.replace("\n", "<br/>")
        return text



