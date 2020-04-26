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
    
    def __init__(self, display_id=None):
        super(AjaxLoader,self).__init__()

        # ensure a unique display id for those who don't wish to manage it
        if not display_id:
            display_id = Widget.generate_unique_id( base='dynamic_display', \
                    wdg='DyanmicLoaderWdg', is_random=True)
           
        self.display_id = display_id
        # define the loaded class
        self.load_class = None
        self.load_args = None
        self.options = {}

        self.element_names = []

        web = WebContainer.get_web()
        self.loader_url = web.get_widget_url()
        self.marshallers = []
        self.is_command = False
        self.loader_url.set_option("ajax", "true")


    def set_option(self, name, value):
        self.options[name] = value

    def get_option(self, name):
        return self.options.get(name)


    def add_element_name(self, element_name):
        '''adds an element name in the dom whose value needs to be passed
        through'''
        self.element_names.append(element_name)


    def register_cmd(self, cmd_class):
        self.is_command = True
        marshaller = Marshaller(cmd_class)
        
        self.marshallers.append( marshaller ) 

        return marshaller


    def set_display_id(self, display_id):
        '''set the id that will be replaced'''
        self.display_id = display_id

    def get_display_id(self):
        return self.display_id


    def generate_div(self):
        ''' this is meant to be called to get the container div for the 
            ajax widget '''
        div = DivWdg()
        div.set_id(self.display_id)
        div.add_style("display: block")
        return div


    def get_loader_url(self):
        return self.loader_url

    def set_load_class(self, load_class, load_args=None):
        '''self.load_args will be converted to a string with a '||' delimiter
        at the end'''
        self.load_class = load_class
        self.load_args = load_args
        if isinstance(load_args, dict):
            self.loader_url.set_option("arg_type", "dict")
            arg_list = []
            for key, value in self.load_args.items():
                arg_list.append('%s=%s'%(key, value))
            self.load_args = '||'.join(arg_list)    


    def set_load_method(self, method_name):
        self.loader_url.set_option("method", method_name)


    def is_refresh(self):
        refresh_id = self.get_refresh_id()

        if refresh_id:
            return True
        else:
            return False

    def get_refresh_id(self):
        '''gets the id of the element that was used to refresh'''
        web = WebContainer.get_web()
        return web.get_form_value("ajax_refresh")




    def get_refresh_script(self, is_cmd=False, show_progress=True, load_once=False):
        # this function differs from get_on_scrpit() in that it should be use
        # for function that will refresh the widget instead of turning the
        return self.get_on_script(is_cmd, show_progress, load_once, is_refresh=True)


    def get_on_script(self, is_cmd=False, show_progress=True, load_once=False, is_refresh=False):

        if is_refresh:
            self.loader_url.set_option('ajax_refresh', self.display_id)
        else:
            self.loader_url.set_option('ajax_refresh', "")
            
        
        for marshaller in self.marshallers:
            self.loader_url.set_option('marshalled', marshaller.get_marshalled())

        if self.load_class == None:
            if self.is_command:
                self.set_load_class("pyasm.widget.CmdReportWdg")
            else:
                raise AjaxLoaderException("Load class is None")

        self.loader_url.set_option('widget', self.load_class)
        
        if self.load_args != None:
            self.loader_url.set_option(WebEnvironment.ARG_NAME, self.load_args)

        for name,value in self.options.items():
            self.loader_url.set_option(name, value)
            
        self.loader_url.add_web_state()
        url = self.loader_url.to_string() 

        # handle element names
        element_names_str = "||".join(self.element_names)
        script = ''
        if show_progress:
            show_progress = 'true'
        else:
            show_progress = 'false'
        if is_cmd:
            script = "AjaxLoader_execute_cmd('%s', '%s', this, '%s','%s');" \
                %(self.display_id, url, element_names_str, show_progress )
        else:
            base_script = "AjaxLoader_load_cbk('%s','%s','%s','%s')" \
                %(self.display_id, url, element_names_str, show_progress)
            if load_once:
                script = "var x=$('%s'); if (x.getAttribute('loaded') !='true') {%s}; set_display_on('%s')"\
                        %(self.display_id, base_script, self.display_id)
            else:
                script = "%s; set_display_on('%s')" %(base_script, self.display_id)
                
        return script

    
    def get_off_script(self):
        return "set_display_off(\'%s\')" % self.display_id




class AjaxWdg(Widget):
    '''functions to make a widget "Ajaxable".   These widgets inherently
    know how to update themselves through ajax.
    These classes have prerequesites:
        - All input elements require names
        - The top node to be replaced has to have an id
    '''
    def __init__(self, check_name=False):
        self.web = WebContainer.get_web()
        self.ajax = None
        super(AjaxWdg,self).__init__()

        if self.is_from_ajax(check_name=check_name):
            self.init_cgi()

        self.top_id = None


    def is_from_ajax(self, check_name=False):
        ajax_class = self.web.get_form_value("widget")
        ajax = self.web.get_form_value("ajax")
        if ajax != "":
            if check_name and ajax_class != Common.get_full_class_name(self):
                return False
            return True
        else:
            return False


    def init_cgi(self):
        '''function that will get the necessary parameters to recreate this
        widget from cgi values'''
        pass

    def reset_ajax(self):
        ''' this could be called in get_display() when the AjaxWdg is used as a BaseTableElement
            depending on implementation'''
        self.ajax = None

    def get_ajax(self):
        if not self.ajax:
            self.ajax = AjaxLoader()
            class_path = Common.get_full_class_name(self)
            self.ajax.set_load_class( class_path )
            self.ajax.set_option("is_form_submitted", "true")
        return self.ajax


    def get_top_id(self):
        return self.top_id

  
    def set_ajax_top_id(self, id):
        self.get_ajax().set_display_id(id)
        self.top_id = id

    def set_ajax_top(self, widget):
        ''' it is mandatory for this widget to have an unique id, especially
        if there are multiple AjaxWdgs instantiated in the same page'''
        ajax = self.get_ajax()

        # get the id of the top widget.  If there is none, then generate one
        top_id = widget.get_id()
        if not top_id:
            top_id = self.generate_unique_id("top_wdg")
            widget.set_id(top_id)
        ajax.set_display_id( top_id )

        # make sure that the display style is set
        widget.add_style("display: block")

        self.top_id = top_id


    def add_ajax_input(self, widget):
        ajax = self.get_ajax()
        ajax.add_element_name( widget.get_input_name() )

    def add_ajax_input_name(self, element_name ):
        ajax = self.get_ajax()
        ajax.add_element_name( element_name )



    def set_ajax_option(self, name, value):
        ajax = self.get_ajax()
        ajax.set_option(name, value)

    def register_cmd(self, cmd_class):
        ajax = self.get_ajax()
        ajax.register_cmd(cmd_class)


    def get_on_script(self, show_progress=True):
        ajax = self.get_ajax() 
        return ajax.get_refresh_script(show_progress=show_progress)
        
    def get_refresh_script(self, show_progress=True):
        ajax = self.get_ajax() 
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
    
    def get_on_script(self, show_progress=True):
        return super(AjaxCmd, self).get_on_script(is_cmd=True, \
            show_progress=show_progress)
        



class DragDropWdg(Widget):
    '''gives the ability for any element to have drag and drop capabilities.
    This is a wrapper around wz_dropdrop.js'''

    def alter_search(self, search):
        '''override this.  These elements should not be getting a search
        at all because they may have already affected a search before.
        This is not completely necessary as the drag drop widget is 
        a global widget and should not get any searches in the first place'''
        pass


    def get_display(self):

        if len(self.widgets) == 0:
            return ""

        script = HtmlElement.script()

        script.add( 'SET_DHTML( ' )
        args = []
        for widget in self.widgets:
            args.append('"%s"' % widget.get_id() )

        script.add( ", ".join(args) )
        script.add( ' )\n' )

        return script.get_display()



class WikiUtil(object):
    '''Converts text into a wiki style'''

    def __init__(self, process_url=False, replace_tag=True):
        self.process_url = process_url
        self.replace_tag = replace_tag

    xxx = 0
        
    def convert(self, text):
        if not type(text) in types.StringTypes:
            text = str(text)
      
        text = self._replace_tag(text)

        # convert <> inside <code/>
        '''
        code_pat = re.compile(r'((?:.|\n)*)(<code>((?:.|\n)*)</code>)((?:.|\n)*)', re.M+re.I)
        m = code_pat.match(text)
        if m:
            group0 = m.groups()[0]
            group1 = m.groups()[1]
            group2 = m.groups()[2]
            group3 = m.groups()[3]
            group2 = self._replace_tag(group2)
            text = '%s<code>%s</code>%s' %(group0, group2, group3)
        else:    
            text = self._replace_linebreak(text)
        '''

        #text = r"%s" %text
        #text = re.sub(r"\\", "/", text)
        if self.process_url:
            proc = "((?:http|ftp)://)"
            url_part = "([a-z0-9\-.]+\.[a-z0-9\-]+)([\/]([a-z0-9_\/\-.?&%=+])*)"
            url_pat = re.compile(proc + url_part, re.IGNORECASE)
            m = url_pat.search(text)
           
            text = re.sub(url_pat, r"<a href='\1\2\3'><u>[\1\2...]</u></a>", text)
        return text


    def _replace_linebreak(self, text):
        text = text.replace("\n", "<br/>")
        return text

    def _replace_tag(self, text):
        text = text.replace("<", "&spt_lt;")
        text = text.replace(">", "&spt_gt;")
        #text = text.replace("<", "&lt;")
        #text = text.replace(">", "&gt;")
        text = text.replace("\n", "<br/>")
        return text



