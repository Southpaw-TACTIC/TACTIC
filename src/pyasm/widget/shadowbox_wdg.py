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

__all__ = ['ShadowBoxWdg', 'ModalBoxWdg', 'LayerWdg', 'OverlayWdg', 
        'IframeWdg','IframePlainWdg', 'PopupWindowWdg']


from pyasm.web import Widget, DivWdg, SpanWdg, HtmlElement, StringWdg, WebContainer, BaseAppServer
from pyasm.common import Container
from icon_wdg import *




class ShadowBoxWdg(Widget):

    HEADER = 'shad_header'
    CONTROL = 'shad_control'
    TITLE = 'shad_box_title'
    
    
    def __init__(self, name=None, width=None):
        self.width = width
        self.title_wdg = StringWdg()
        self.title_wdg.name = ShadowBoxWdg.TITLE
        self.shad_name = name
        super(ShadowBoxWdg, self).__init__()

    def init(self):
        div_main = DivWdg(css='module')
        if self.width != None:
            widthstr="width: %sem" % (self.width)
            div_main.add_style(widthstr)
            
        # reset self.name,  create the content widget
        if not self.shad_name:
            self.shad_name = "ShadowBox%s" % (self.generate_unique_id())
        div_main.set_id(self.shad_name)

        
        div_main.center()
              
        div_head = DivWdg(css='boxhead')

        # HACK to compensate for IE weird handling of CSS
        if WebContainer.get_web().is_IE() and 'password' in self.shad_name:
            div_head.add_style('left','-242px')

        div_head.add_style('padding-bottom: 2px')
        empty_header = Widget(name=self.HEADER)
        
        div_head.add(empty_header, empty_header.get_name())
        div_head.add(self.title_wdg, self.title_wdg.get_name())
        
        div_control = DivWdg(css='control')
        empty_control = Widget(name=self.CONTROL)
        
        div_control.add(empty_header, empty_control.get_name())
        
        div_container = DivWdg(css='container')
 
        ie_rect = HtmlElement('v:roundrect') 
        ie_rect.set_attr("arcsize", "1966f")
        ie_rect.set_attr("fillcolor", "white")
        ie_rect.set_attr("strokecolor", "#555")
        ie_rect.set_attr("strokeweight", "2pt")
        
        div_body = DivWdg(css='content')
        div_body.set_id("%s_cont" % self.shad_name)  
        div_body.center()
        div_body.add(div_head)
        div_body.add(div_control)
        
        self.content = div_main
        self.head = div_head
        self.control = div_control
        self.body = div_body
        
        div_container.add(ie_rect)
        ie_rect.add(div_body)

        #div_main.add(div_head)
        div_main.add(div_container)
        
    def get_on_script(self):
        return "toggle_overlay()"


    def get_off_script(self):
        return "toggle_overlay()"
    
    # title must be img or span
    def set_title_wdg(self, title_wdg):
        self.head.set_widget(title_wdg, self.title_wdg.get_name())
        self.head.add_style("border-bottom: 1px dotted #968d79")


    def set_header(self, widget):
        self.head.set_widget(widget, self.HEADER)
        
    def set_control(self, widget):
        self.control.set_widget(widget, self.CONTROL)

    def set_width(self, width):
        self.width = width

    def get_name(self):
        return self.shad_name

    def get_display(self):

        widgets = self.widgets
        self.widgets = []

        for widget in widgets:
            self.body.add(widget)
        self.add(self.content)
        return super(ShadowBoxWdg,self).get_display()
        

class ModalBoxWdg(Widget):

    
    def __init__(self, name=None, title_wdg=None, width=None, xpos=None, ypos=None,\
            nav_links=True, display=False, iframe_name=''):

        self.title_wdg = title_wdg
        self.width = width
        self.xpos = xpos
        self.ypos = ypos
        self.nav_links = nav_links
        self.display = display
        self.shad_name = name 
        self.iframe_name = iframe_name
        super(ModalBoxWdg, self).__init__()

    def init(self):
        
        self.layer = LayerWdg(self.xpos, self.ypos, self.display)
        if not self.width:
            self.shadowbox = ShadowBoxWdg(self.shad_name)
        else:
            self.shadowbox = ShadowBoxWdg(self.shad_name, self.width)

        # do not enable it for the Login page
        web = WebContainer.get_web()
        if self.shad_name and not web.is_IE():
            BaseAppServer.add_onload_script("Move.drag('%s','%s')" \
                    %(self.shadowbox.get_name(), self.iframe_name))

        div = DivWdg()
        
        from pyasm.widget import IconButtonWdg
        
        move_button = IconWdg(name='move me', icon=IconWdg.NAV)
        move_button.set_id("%s_handle" % (self.shad_name))
        move_button.add_class('move')

        move_button.add_style('float: left')
        move_button.add_style('padding: 2px 0 0 6px')
        if not web.is_IE():
            div.add(move_button)

        mbutton = IconButtonWdg(name='close window', icon=IconWdg.KILL)
        mbutton.set_class("moduleKillBtn")
        mbutton.add_event("onclick", self.layer.get_off_script() )
        
        div.add(mbutton)
        
        if self.nav_links:
            back_link = HtmlElement.href("&lt;&lt;", "javascript:history.back()")
            back_link.add_style("font-size", "1.4em")
            
            for_link = HtmlElement.href("&gt;&gt;", "javascript:history.forward()")
            for_link.add_style("font-size", "1.4em")
           
            div.add(SpanWdg(back_link, css='med'))
            div.add(SpanWdg(for_link, css='med'))
        
        self.shadowbox.set_header(div)
        
        # add button and title_wdg to shadow box
        if self.title_wdg:
            title_wdg = DivWdg()
            title_wdg.set_class("moduleTitle")
            title_wdg.add(self.title_wdg)
            self.shadowbox.set_title_wdg(title_wdg)
        
       
        self.layer.add(self.shadowbox)
        self._add_widget(self.layer)
        

    def get_on_script(self):
        on_script = ["Overlay.init(true)"]
        on_script.append(self.layer.get_on_script())
        return ";".join(on_script)

    def get_off_script(self):
        return self.layer.get_off_script()
    
    def add_widget(self,widget,name=None, wdgtype=None):
        self.shadowbox.add(widget)

    def add(self,widget,name=None, wdgtype=None):
        self.shadowbox.add(widget)

    def get_shadow_box(self):
        return self.shadowbox

class LayerWdg(HtmlElement):
    
    YPOS = 2
    def __init__(self, xpos=None, ypos=None, display=False):
        self.xpos = xpos
        self.ypos = ypos
        self.display = display
        super(LayerWdg, self).__init__("div")

    def init(self):

        # Set up the base div
        self.add_class('full')
        
        # add display setting
        if self.display:
            self.add_style("display: block")
        else:
            self.add_style("display: none")
        
        self.add_style("z-index: 1000")

        # add positioning settings
        if self.xpos == None:
            self.add_style("left", "0px")
        else:
            self.add_style("left", self.xpos)
        
        if self.ypos == None:
            self.add_style("top", str(LayerWdg.YPOS) + 'px')
        else:    
            self.add_style("top", self.ypos)
         
        name = "layer%s" % (self.generate_unique_id())
        self.set_id(name)
        
        self.onscript = "toggle_display('%s');" % (name)
        self.offscript = "toggle_display('%s');" % (name)

    def get_on_script(self):
        return self.onscript

    def get_off_script(self):
        return self.offscript
        

class OverlayWdg(ModalBoxWdg):
    pass


class IframeWdg(HtmlElement):
    # units in em
    WIDTH = 45 
    HEIGHT = 80 
    
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.src = None
        self.width = width
        self.height = height
        super(IframeWdg, self).__init__("div")

    def init(self):
        self.name = "iframe%s" % (self.generate_unique_id())
        self.img_span_name = '%s_loading' %self.name
        self.iframe = HtmlElement.iframe()
        self.iframe.set_id(self.name)
        self.iframe.set_attr('name',self.name)
        # To adjust the real-time size of the overlay box, do it in get_on_script
        
        self.overlay = OverlayWdg(name='%s_shadowbox'%self.name, \
            width=self.width * 1.0, display=False, iframe_name=self.name )

        
        self.overlay.add(self.iframe)
        
        self.shadowbox = self.overlay.get_shadow_box()

        


        tall_control = IconButtonWdg(name='taller', icon='/context/icons/common/dn_button.png')
        tall_control.add_style("float: right")
        
       
        tall_control.add_event("onclick", self.get_taller_script(self.name, self.shadowbox.name) )
       
        short_control = IconButtonWdg(name='shorter', icon='/context/icons/common/up_button.png')
        short_control.add_style("float: right")
        short_control.add_style("padding-bottom: 4px")
        
        short_control.add_event("onclick", self.get_shorter_script(self.name, self.shadowbox.name) )
        
        control = DivWdg()
        control.add_style('margin-top: -30px')
        control.add(short_control)
        control.add(tall_control)
        
        if not WebContainer.get_web().is_IE():
            self.shadowbox.set_control(control)
        self.overlay.add(self._get_loading_span()) 
        self.add(self.overlay)

    
    def _get_loading_span(self):
        span = SpanWdg()
        span.add_style("display","none")
        img = HtmlElement.img('/context/icons/common/loading.gif')
        img.add_style("height","10px")
        msg_span = SpanWdg('loading')
        msg_span.set_class('small')
        span.add(msg_span)
        span.add(img) 
        span.set_id(self.img_span_name)
        return span



    
    def get_on_script(self, src, dynamic_element=[]):
        '''A script to display the iframe. this is not called on init'''
        scripts = []
        shadow_on_script = self.overlay.get_on_script()
   
        iframe_script = "IframeLoader_display('%s','%s','%s','%s')" % \
            (self.img_span_name, self.name, src, '||'.join(dynamic_element))
        
        scripts.append(iframe_script)
        scripts.append(shadow_on_script)
        resize_iframe = IframeWdg.get_resize_script(self.name, self.width)
        resize_shadow = IframeWdg.get_resize_script(self.shadowbox\
            .get_name(), self.width * 0.9)
            
        
        scripts.append(resize_shadow)
        scripts.append(resize_iframe)

        return ";".join(scripts)

    def get_off_script(self):
        shadow_off_script = self.overlay.get_off_script()
        return shadow_off_script 

    def get_display(self):
        self.iframe.center()
        self.iframe.add_style("max-width", "950px")
        self.iframe.add_style("max-height", "750px")
        self.iframe.add_style("height", str(self.height) + 'em')
        self.iframe.add_style("width", str(self.width) + 'em')
        self.iframe.add("WARNING: iframes are not supported")
        self.iframe.set_attr("scrolling", "auto")
       
        return super(IframeWdg, self).get_display()

    def set_width(self, width):
        self.width = width

    
    def get_taller_script(self, iframe_name, shad_name):
        taller_script = "Overlay.taller('%s','%s')"% (iframe_name, shad_name) 
        return taller_script
    
    def get_shorter_script(self, iframe_name, shad_name):
        shorter_script = "Overlay.shorter('%s','%s')"% (iframe_name, shad_name) 
        return shorter_script
        
    # static method
    def get_resize_script(name, width=None, height=None ):
        
        resize = "document.getElementById('%s').style.width = '%sem'" \
            % (name, width)
        return resize
    get_resize_script = staticmethod(get_resize_script)
        
    def get_popup_script(msg='', css='', icon='', ref=None, width=70):
        ''' returns a javascript that will trigger a popup message box in
            an iframe '''
        if not ref:
            url = WebContainer.get_web().get_widget_url()
            url.set_option("widget", "MessageWdg")
            url.set_option("args", [msg, css, icon])
            
            ref = url.get_url()

        # open iframe
        iframe = WebContainer.get_iframe()
        iframe.set_width(width)
        action = iframe.get_on_script(ref)
        return action    
    get_popup_script = staticmethod(get_popup_script)
    
    
class IframePlainWdg(IframeWdg):
    ''' a plain iframe to be opened within an iframe '''
    
    def init(self):
        self.img_span_name = self.generate_unique_id('loadingplain')
        self.name = "iframeplain_%s" % (self.generate_unique_id())
        self.iframe = HtmlElement.iframe()
        self.iframe.set_id(self.name)
        self.iframe.set_attr('name',self.name)
        self.div = DivWdg(css='iframe_plain')
        self.div.add_style('display','none')
        self.div.set_id("iframeplain_cont_%s" % (self.generate_unique_id()))
        self.div.add(self.iframe)
        self.add(self.div)
        self.add(self._get_loading_span())
        
    def get_on_script(self, src, dynamic_element=[]):
        '''A script to display the iframe. this is not called on init'''
        scripts = []
        
        cont_on_script = "toggle_display('%s')" %self.div.get_id()
        iframe_script = "IframeLoader_display('%s','%s','%s','%s')" % \
            (self.img_span_name, self.name, src, '||'.join(dynamic_element))
        
        scripts.append(iframe_script)
        scripts.append(cont_on_script)
        
        resize_iframe = IframeWdg.get_resize_script(self.name, self.width)
     
        scripts.append(resize_iframe)
        return ";".join(scripts)

    def get_off_script(self):
        return "toggle_display('%s')" %self.div.get_id()

class PopupWindowWdg(Widget):

    def get_on_script( src, dynamic_element):
        script = "PopupWindow_display('%s','%s')" \
            % (src, '||'.join(dynamic_element) )
        return script
    get_on_script = staticmethod(get_on_script)
    
