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
    
    
    def __init__(my, name=None, width=None):
        my.width = width
        my.title_wdg = StringWdg()
        my.title_wdg.name = ShadowBoxWdg.TITLE
        my.shad_name = name
        super(ShadowBoxWdg, my).__init__()

    def init(my):
        div_main = DivWdg(css='module')
        if my.width != None:
            widthstr="width: %sem" % (my.width)
            div_main.add_style(widthstr)
            
        # reset my.name,  create the content widget
        if not my.shad_name:
            my.shad_name = "ShadowBox%s" % (my.generate_unique_id())
        div_main.set_id(my.shad_name)

        
        div_main.center()
              
        div_head = DivWdg(css='boxhead')

        # HACK to compensate for IE weird handling of CSS
        if WebContainer.get_web().is_IE() and 'password' in my.shad_name:
            div_head.add_style('left','-242px')

        div_head.add_style('padding-bottom: 2px')
        empty_header = Widget(name=my.HEADER)
        
        div_head.add(empty_header, empty_header.get_name())
        div_head.add(my.title_wdg, my.title_wdg.get_name())
        
        div_control = DivWdg(css='control')
        empty_control = Widget(name=my.CONTROL)
        
        div_control.add(empty_header, empty_control.get_name())
        
        div_container = DivWdg(css='container')
 
        ie_rect = HtmlElement('v:roundrect') 
        ie_rect.set_attr("arcsize", "1966f")
        ie_rect.set_attr("fillcolor", "white")
        ie_rect.set_attr("strokecolor", "#555")
        ie_rect.set_attr("strokeweight", "2pt")
        
        div_body = DivWdg(css='content')
        div_body.set_id("%s_cont" % my.shad_name)  
        div_body.center()
        div_body.add(div_head)
        div_body.add(div_control)
        
        my.content = div_main
        my.head = div_head
        my.control = div_control
        my.body = div_body
        
        div_container.add(ie_rect)
        ie_rect.add(div_body)

        #div_main.add(div_head)
        div_main.add(div_container)
        
    def get_on_script(my):
        return "toggle_overlay()"


    def get_off_script(my):
        return "toggle_overlay()"
    
    # title must be img or span
    def set_title_wdg(my, title_wdg):
        my.head.set_widget(title_wdg, my.title_wdg.get_name())
        my.head.add_style("border-bottom: 1px dotted #968d79")


    def set_header(my, widget):
        my.head.set_widget(widget, my.HEADER)
        
    def set_control(my, widget):
        my.control.set_widget(widget, my.CONTROL)

    def set_width(my, width):
        my.width = width

    def get_name(my):
        return my.shad_name

    def get_display(my):

        widgets = my.widgets
        my.widgets = []

        for widget in widgets:
            my.body.add(widget)
        my.add(my.content)
        return super(ShadowBoxWdg,my).get_display()
        

class ModalBoxWdg(Widget):

    
    def __init__(my, name=None, title_wdg=None, width=None, xpos=None, ypos=None,\
            nav_links=True, display=False, iframe_name=''):

        my.title_wdg = title_wdg
        my.width = width
        my.xpos = xpos
        my.ypos = ypos
        my.nav_links = nav_links
        my.display = display
        my.shad_name = name 
        my.iframe_name = iframe_name
        super(ModalBoxWdg, my).__init__()

    def init(my):
        
        my.layer = LayerWdg(my.xpos, my.ypos, my.display)
        if not my.width:
            my.shadowbox = ShadowBoxWdg(my.shad_name)
        else:
            my.shadowbox = ShadowBoxWdg(my.shad_name, my.width)

        # do not enable it for the Login page
        web = WebContainer.get_web()
        if my.shad_name and not web.is_IE():
            BaseAppServer.add_onload_script("Move.drag('%s','%s')" \
                    %(my.shadowbox.get_name(), my.iframe_name))

        div = DivWdg()
        
        from pyasm.widget import IconButtonWdg
        
        move_button = IconWdg(name='move me', icon=IconWdg.NAV)
        move_button.set_id("%s_handle" % (my.shad_name))
        move_button.add_class('move')

        move_button.add_style('float: left')
        move_button.add_style('padding: 2px 0 0 6px')
        if not web.is_IE():
            div.add(move_button)

        mbutton = IconButtonWdg(name='close window', icon=IconWdg.KILL)
        mbutton.set_class("moduleKillBtn")
        mbutton.add_event("onclick", my.layer.get_off_script() )
        
        div.add(mbutton)
        
        if my.nav_links:
            back_link = HtmlElement.href("&lt;&lt;", "javascript:history.back()")
            back_link.add_style("font-size", "1.4em")
            
            for_link = HtmlElement.href("&gt;&gt;", "javascript:history.forward()")
            for_link.add_style("font-size", "1.4em")
           
            div.add(SpanWdg(back_link, css='med'))
            div.add(SpanWdg(for_link, css='med'))
        
        my.shadowbox.set_header(div)
        
        # add button and title_wdg to shadow box
        if my.title_wdg:
            title_wdg = DivWdg()
            title_wdg.set_class("moduleTitle")
            title_wdg.add(my.title_wdg)
            my.shadowbox.set_title_wdg(title_wdg)
        
       
        my.layer.add(my.shadowbox)
        my._add_widget(my.layer)
        

    def get_on_script(my):
        on_script = ["Overlay.init(true)"]
        on_script.append(my.layer.get_on_script())
        return ";".join(on_script)

    def get_off_script(my):
        return my.layer.get_off_script()
    
    def add_widget(my,widget,name=None, wdgtype=None):
        my.shadowbox.add(widget)

    def add(my,widget,name=None, wdgtype=None):
        my.shadowbox.add(widget)

    def get_shadow_box(my):
        return my.shadowbox

class LayerWdg(HtmlElement):
    
    YPOS = 2
    def __init__(my, xpos=None, ypos=None, display=False):
        my.xpos = xpos
        my.ypos = ypos
        my.display = display
        super(LayerWdg, my).__init__("div")

    def init(my):

        # Set up the base div
        my.add_class('full')
        
        # add display setting
        if my.display:
            my.add_style("display: block")
        else:
            my.add_style("display: none")
        
        my.add_style("z-index: 1000")

        # add positioning settings
        if my.xpos == None:
            my.add_style("left", "0px")
        else:
            my.add_style("left", my.xpos)
        
        if my.ypos == None:
            my.add_style("top", str(LayerWdg.YPOS) + 'px')
        else:    
            my.add_style("top", my.ypos)
         
        name = "layer%s" % (my.generate_unique_id())
        my.set_id(name)
        
        my.onscript = "toggle_display('%s');" % (name)
        my.offscript = "toggle_display('%s');" % (name)

    def get_on_script(my):
        return my.onscript

    def get_off_script(my):
        return my.offscript
        

class OverlayWdg(ModalBoxWdg):
    pass


class IframeWdg(HtmlElement):
    # units in em
    WIDTH = 45 
    HEIGHT = 80 
    
    def __init__(my, width=WIDTH, height=HEIGHT):
        my.src = None
        my.width = width
        my.height = height
        super(IframeWdg, my).__init__("div")

    def init(my):
        my.name = "iframe%s" % (my.generate_unique_id())
        my.img_span_name = '%s_loading' %my.name
        my.iframe = HtmlElement.iframe()
        my.iframe.set_id(my.name)
        my.iframe.set_attr('name',my.name)
        # To adjust the real-time size of the overlay box, do it in get_on_script
        
        my.overlay = OverlayWdg(name='%s_shadowbox'%my.name, \
            width=my.width * 1.0, display=False, iframe_name=my.name )

        
        my.overlay.add(my.iframe)
        
        my.shadowbox = my.overlay.get_shadow_box()

        


        tall_control = IconButtonWdg(name='taller', icon='/context/icons/common/dn_button.png')
        tall_control.add_style("float: right")
        
       
        tall_control.add_event("onclick", my.get_taller_script(my.name, my.shadowbox.name) )
       
        short_control = IconButtonWdg(name='shorter', icon='/context/icons/common/up_button.png')
        short_control.add_style("float: right")
        short_control.add_style("padding-bottom: 4px")
        
        short_control.add_event("onclick", my.get_shorter_script(my.name, my.shadowbox.name) )
        
        control = DivWdg()
        control.add_style('margin-top: -30px')
        control.add(short_control)
        control.add(tall_control)
        
        if not WebContainer.get_web().is_IE():
            my.shadowbox.set_control(control)
        my.overlay.add(my._get_loading_span()) 
        my.add(my.overlay)

    
    def _get_loading_span(my):
        span = SpanWdg()
        span.add_style("display","none")
        img = HtmlElement.img('/context/icons/common/loading.gif')
        img.add_style("height","10px")
        msg_span = SpanWdg('loading')
        msg_span.set_class('small')
        span.add(msg_span)
        span.add(img) 
        span.set_id(my.img_span_name)
        return span



    
    def get_on_script(my, src, dynamic_element=[]):
        '''A script to display the iframe. this is not called on init'''
        scripts = []
        shadow_on_script = my.overlay.get_on_script()
   
        iframe_script = "IframeLoader_display('%s','%s','%s','%s')" % \
            (my.img_span_name, my.name, src, '||'.join(dynamic_element))
        
        scripts.append(iframe_script)
        scripts.append(shadow_on_script)
        resize_iframe = IframeWdg.get_resize_script(my.name, my.width)
        resize_shadow = IframeWdg.get_resize_script(my.shadowbox\
            .get_name(), my.width * 0.9)
            
        
        scripts.append(resize_shadow)
        scripts.append(resize_iframe)

        return ";".join(scripts)

    def get_off_script(my):
        shadow_off_script = my.overlay.get_off_script()
        return shadow_off_script 

    def get_display(my):
        my.iframe.center()
        my.iframe.add_style("max-width", "950px")
        my.iframe.add_style("max-height", "750px")
        my.iframe.add_style("height", str(my.height) + 'em')
        my.iframe.add_style("width", str(my.width) + 'em')
        my.iframe.add("WARNING: iframes are not supported")
        my.iframe.set_attr("scrolling", "auto")
       
        return super(IframeWdg, my).get_display()

    def set_width(my, width):
        my.width = width

    
    def get_taller_script(my, iframe_name, shad_name):
        taller_script = "Overlay.taller('%s','%s')"% (iframe_name, shad_name) 
        return taller_script
    
    def get_shorter_script(my, iframe_name, shad_name):
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
    
    def init(my):
        my.img_span_name = my.generate_unique_id('loadingplain')
        my.name = "iframeplain_%s" % (my.generate_unique_id())
        my.iframe = HtmlElement.iframe()
        my.iframe.set_id(my.name)
        my.iframe.set_attr('name',my.name)
        my.div = DivWdg(css='iframe_plain')
        my.div.add_style('display','none')
        my.div.set_id("iframeplain_cont_%s" % (my.generate_unique_id()))
        my.div.add(my.iframe)
        my.add(my.div)
        my.add(my._get_loading_span())
        
    def get_on_script(my, src, dynamic_element=[]):
        '''A script to display the iframe. this is not called on init'''
        scripts = []
        
        cont_on_script = "toggle_display('%s')" %my.div.get_id()
        iframe_script = "IframeLoader_display('%s','%s','%s','%s')" % \
            (my.img_span_name, my.name, src, '||'.join(dynamic_element))
        
        scripts.append(iframe_script)
        scripts.append(cont_on_script)
        
        resize_iframe = IframeWdg.get_resize_script(my.name, my.width)
     
        scripts.append(resize_iframe)
        return ";".join(scripts)

    def get_off_script(my):
        return "toggle_display('%s')" %my.div.get_id()

class PopupWindowWdg(Widget):

    def get_on_script( src, dynamic_element):
        script = "PopupWindow_display('%s','%s')" \
            % (src, '||'.join(dynamic_element) )
        return script
    get_on_script = staticmethod(get_on_script)
    
