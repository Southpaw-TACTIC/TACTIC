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


__all__ = ['HtmlException', 'HtmlElement', 'DivWdg', 'FloatDivWdg', 
        'SpanWdg', 'Tbody', 'Table', 'Canvas', 'Video']

import os
import re
import string
import types

from event_container import *

from pyasm.common import Container, jsondumps, jsonloads, Common
from pyasm.search import Search
from widget import Widget
from web_container import WebContainer




class HtmlException(Exception):
    pass



class HtmlElement(Widget):
    '''Define an html element.  Although these are real widgets, they
    are often not used as such and can be used by themselves.  This
    allows a simpler structure for the main widgets for the probagation
    of sobjects and searches without having to go through every html
    element in the hierarchy.  Most often, static convenience functions are
    used.  DivWdg and SpanWdg and TableWdg, which are most often used, have
    their own classes.

    Basic usage:

    p = HtmlElement.p()
    img = HtmlElement.img()
    img.set_attr("src", "/images/icon.png")
    p.add(img)
    '''

    def _get_my_attrs(my):
        if my._attrs == None:
            my._attrs = {}
        return my._attrs
    def _set_my_attrs(my, attrs):
        my._attrs = attrs
    attrs = property(_get_my_attrs, _set_my_attrs)



    #def _get_my_behaviors(my):
    #    if my._behaviors == None:
    #        my._behaviors = []
    #    return my._behaviors
    #def _set_my_behaviors(my, behaviors):
    #    my._behaviors = behaviors
    #behaviors = property(_get_my_behaviors, _set_my_behaviors)



    def __init__(my, type=None, child=None, css=None, id=None):
        my._attrs = None
        my.events = None
        my.type = type
        my.classes = None
        my.styles = None
        my.relay_styles = None
        my.behaviors = None

        if css:
            my.set_class(css)    

        if id:
            my.set_id(id)

        super(HtmlElement,my).__init__()

        if child:
            my.add(child)


    """
        HtmlElement.count += 1
        #print "create: ", HtmlElement.count
        search_key = my.type
        count = HtmlElement.track.get(search_key)
        if count == None:
            HtmlElement.track[search_key] = 1
        else:
            HtmlElement.track[search_key] = count + 1

    count = 0
    track = {}
    def __del__(my):
        my.del_ref()

    def del_ref(my):
        HtmlElement.count -= 1

        search_key = my.type
        print "search_key: ", search_key
        count = HtmlElement.track[search_key]
        #print "delete: ", HtmlElement.count, search_key, count

        if count == 1:
            del(HtmlElement.track[search_key])
        elif count == 0:
            sdfsfdafsd
        else:
            HtmlElement.track[search_key] = count - 1

        #print HtmlElement.track
        my.data = None
        my.update_data = None

        total = 0
        for key, x in HtmlElement.track.items():
            if x > 1:
                print key, x
            total += x
        print "total: ", total

        my.clear()
    """



    def clear(my):
        #print "clear: ", my
        my.attrs = None
        my.events = None
        my.type = None
        my.classes = None
        my.styles = None
        my.behaviors = None

        my._widgets = None
        my.named_widgets = None
        my.typed_widgets = None

    def set_type(my, type):
        '''Set the type of html element.  This constitutes all of the elements
        that define html. For example: p, hr, br, img, a ...
        '''
        my.type = type


    def get_attr(my, name):
        '''Get the value of an attribute of the html element'''
        if name not in my.attrs:
            return None
        return my.attrs[name]

    def set_attr(my, name, value):
        '''Set an attribute of the html element'''

        if type(value) in types.StringTypes:
            my.attrs[name] = value
        elif isinstance(value, unicode):
            my.attrs[name] = value.encode('utf-8')
        else:
            my.attrs[name] = str(value)


    def add_attr(my, name, value):
        '''Set an attribute of the html element'''
        my.set_attr(name, value)



    def set_class(my, value):
        '''Set the class attribute of the html element for css styling'''
        #my.classes = {}
        my.add_class(value)
   
    def has_class(my, value):
        if not my.classes:
            return False
        if value in my.classes:
            return True
        return False

    def add_class(my, value):
        '''Adds a class attribute of the html element for css styling'''
        assert value
        if not my.classes:
            my.classes = {}
        my.classes[value] = value

    def remove_class(my, value):
        '''Adds a class attribute of the html element for css styling'''
        assert value
        if my.classes.has_key(value):
            my.classes.pop(value)

        
    def set_id(my, id):
        '''Sets the id attribute of the html element'''
        my.attrs['id'] = id

    def set_unique_id(my,prefix=None):
        unique_id = my.generate_unique_id(is_random=True)
        if prefix:
            unique_id = prefix + '_' + unique_id
        my.set_id(unique_id)
        return unique_id

    def get_id(my):
        '''Returns the id attribute of the html element'''
        return my.attrs.get('id')


    def get_unique_event(my, prefix='event'):
        unique_id = my.generate_unique_id(is_random=True)
        unique_id = prefix + '_' + unique_id
        return unique_id


    def add_looks(my, look_palette_names_str):
        if look_palette_names_str.find(" ") != -1:
            pals = look_palette_names_str.split(" ")
        else:
            pals = [ look_palette_names_str ]

        for pal_name in pals:
            pal_name = pal_name.strip()
            if pal_name:
                my.add_class( "look_%s" % pal_name )


    def set_style(my, style):
        '''sets a style attribute. set_style() overrides add_style() calls'''
        style = style.rstrip(";")
        if not my.styles:
            my.styles = {}
        my.attrs['style'] = style


    def add_style(my, name, value=None, override=True):
        '''add a style attribute'''
        if not name:
            return
        if value == None:
            if name.find(";") != -1:
                name = name.split(";")[0]
            name, value = name.split(": ")
        if not my.styles:
            my.styles = {}

        elif not override and my.styles.has_key(name):
            return


        my.styles[name] = value


    def add_styles(my, styles):
        if type(styles) == str:
            styles_list = styles.split(";")
            for s in styles_list:
                my.add_style( s.strip() )
        elif type(styles) == dict:
            for s_name,s_value in styles.iteritems():
                my.add_style( s_name, str(s_value) )


    def add_smart_style(my, class_name, name, value):
        style = HtmlElement.style()
        element_id = my.get_id()
        assert element_id
        style.add("#%s .%s { %s: %s; }" % (element_id, class_name, name, value))
        if my.relay_styles == None:
            my.relay_styles = []
        my.relay_styles.append(style)

    def add_smart_styles(my, class_name, data):
        for name, value in data.items():
            my.add_smart_style(class_name, name, value)



    def get_palette(my):
        from palette import Palette
        palette = Palette.get()
        return palette


    def get_theme(my):
        from palette import Palette
        palette = Palette.get()
        return palette.get_theme()


    def get_color(my, palette_key, modifier=0, default=None):
        from palette import Palette
        palette = Palette.get()
        color = palette.color(palette_key, modifier, default=default)
        return color

    def add_color(my, name, palette_key, modifier=0, default=None):
        from palette import Palette
        palette = Palette.get()
        color = palette.color(palette_key, modifier, default=default)
        my.add_style("%s: %s" % (name, color) )
        return color



    def get_gradient(my, palette_key, modifier=0, range=-20, reverse=False, default=None,angle=180):

        from palette import Palette
        from web_container import WebContainer
        web = WebContainer.get_web()
        palette = Palette.get()
        if web.is_IE():
            color = palette.color(palette_key, (modifier+range)/2, default=default)
            return color
        else: 
            if not reverse:
                color1 = palette.color(palette_key, modifier, default=default)
                color2 = palette.color(palette_key, modifier+range, default=default)
            else:
                color2 = palette.color(palette_key, modifier, default=default)
                color1 = palette.color(palette_key, modifier+range, default=default)

            """
            if web.get_browser() == 'Mozilla':
                gradient = "-moz-linear-gradient(top, %s, %s)" % (color1, color2)
            else:
                gradient = "-webkit-gradient(linear, 0%% 0%%, 0%% 100%%, from(%s), to(%s))" % (color1, color2)
            """

            gradient = "linear-gradient(%sdeg, %s, %s)" % (angle, color1, color2)
            return gradient


    def add_gradient(my, name, palette_key, modifier=0, range=-20, reverse=False, default=None):
        gradient = my.get_gradient(palette_key, modifier=modifier, range=range, reverse=reverse, default=default)

        my.add_style("%s: %s" % (name,gradient) )
        return gradient




    def add_border(my, modifier=None, style=None, direction=None, color=None, size=None):
        '''@params: direction can be top left bottom right, default to None''' 
        if not style:
            style = "solid"
        style_name = 'border'
        if direction:
            style_name = 'border-%s'% direction
        if not color:
            color = "border"

        if size and style_name == "border":
            my.add_style("border-style: %s" % style)
            my.add_style("border-width: %s" % size)
            my.add_style("border-color: %s" % my.get_color(color,modifier=modifier))
        else:
            my.add_style("%s: %s 1px %s" % (style_name, style, my.get_color(color, modifier=modifier) ))
        

    def add_hover(my, palette_key='background', modifier=-10):
        '''convenience function to add a standard hover'''
        hover_color = my.get_color(palette_key, modifier)
        my.add_behavior( {
            'type': 'hover',
            'hover': hover_color,
            'cbjs_action_over': '''
            bvr.src_el.setStyle("background", bvr.hover);
            ''',
            'cbjs_action_out': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )
        my.add_class("hand")


    # convenience method for z-sorting mechanism ...
    def set_z_start(my, z_start):
        my.add_class("SPT_Z")
        my.set_attr("spt_z_start",str(z_start))


    def get_children(my):
        '''returns a list of the children widgets of the html element'''
        return my.widgets

    def get_dom_path(my):
        '''returns the javascript dom path of the html element'''
        id = my.get_id()
        assert id

        return "document.form.%s" %id


    # NOTE: both add_named_listener and set_named_listener both only accept a 'cbjs_' based call-back string
    #       ... 'cbfn_' is not supported for this. I don't think 'cbfn_' format is really needed anymore.
    #
    def add_named_listener(my, event_name, cbjs_action_str, extra_bvr=None):
        my.add_behavior( my._get_named_listener_bvr(event_name, cbjs_action_str, extra_bvr) )


    def set_named_listener(my, event_name, cbjs_action_str, extra_bvr=None):
        my.set_behavior( my._get_named_listener_bvr(event_name, cbjs_action_str, extra_bvr) )


    def _get_named_listener_bvr(my, event_name, cbjs_action_str, extra_bvr):
        bvr = {
            'type': 'listen',
            'event_name': event_name,
            'cbjs_action': cbjs_action_str
        }
        if extra_bvr:
            bvr.update( extra_bvr )
        return bvr


    # function to call if you want this HTML element to force the default right click context menu in
    # situations where a parent (or ancestor) element has a right click context menu override
    #
    def force_default_context_menu(my):
        my.add_event( "oncontextmenu", "spt.force_default_context_menu = true;" )

    def add_behavior(my, bvr_spec):
        '''adds an individual behavior specification to the HTML based widget'''
        #print "bvr: ", str(bvr_spec).replace(r"\n", "\n")
        #print "---"
        if my.behaviors == None:
            my.behaviors = []

        if type(bvr_spec) == types.DictType:
            # handle any cbjs string value that has newlines (e.g. ones specified using triple single quote block
            # quotes in order to have the javascript code readable as indented multi-line code) ...
            regex = re.compile( r'\n\s*' )

            if my.__class__.__name__.find('CheckboxWdg') != -1:
                if bvr_spec.get('propagate_evt') == None:
                    bvr_spec['propagate_evt'] = True

            script_path = bvr_spec.get('cbjs_script_path')
            if script_path:
                script_sobj = Container.get("HTML::custom_script")
                if script_sobj == None:
                    basename = os.path.basename(script_path)
                    dirname = os.path.dirname(script_path)
                    search = Search("config/custom_script")
                    search.add_filter("folder", dirname)
                    search.add_filter("title", basename)
                    script_sobj = search.get_sobject()
                if script_sobj:
                    Container.put("HTML::custom_script", script_sobj)
                    v = script_sobj.get_value("script")
                    bvr_spec['cbjs_action'] = regex.sub( '\n', v )

                else:
                    raise Exception( "Error: script path [%s] does not exist" % script_path )
                    

            for k,v in bvr_spec.iteritems():
                if 'cbjs' in k and '\n' in v:
                    bvr_spec[k] = regex.sub( '\n', v )
            my.behaviors.append( bvr_spec )
        elif type(bvr_spec) == types.StringType:
            # legacy support for any '.add_behavior' calls that provide a bvr_spec argument that is a string
            # representation of a behavior specification dictionary
            my.behaviors.append( my.convert_behavior_str(bvr_spec) )
        else:
            raise Exception( "Behavior specification should be a dictionary, %s spec is not supported." %
                             type(bvr_spec) )

        count = Container.get("Widget:bvr_count")
        if not count:
            count = 1
        else:
            count += 1
        Container.put("Widget:bvr_count", count)


    def add_relay_behavior(my, behavior):
        # should really build this in so that we're not creating an event
        # in a behavior (seems like an extra step)
        match_class = behavior.get('bvr_match_class')
        relay_behavior = {
        'type': 'load',
        'bvr': behavior,
        'bvr_match_class': match_class,
        'cbjs_action': '''
            var orig_bvr = bvr.bvr;
            var event = orig_bvr.type;
            var match = bvr.bvr_match_class;
            if (!match) {
                spt.alert("No match class defined for relay behavior");
                return;
            }
            var event_key = event + ":relay(." + match + ")";

            var func = function(evt, src_el) {
                var bvr = orig_bvr;
                bvr.src_el = src_el;
                eval(bvr.cbjs_action);
            };
            bvr.src_el.addEvent(event_key, func);
        '''
        }
        my.add_behavior(relay_behavior)
 




    def set_behavior(my, new_bvr):
        # NOTE: new_bvr MUST be a dictionary! Not supporting string behavior spec when setting to override
        if my.behaviors == None:
            my.behaviors = []

        if type(new_bvr) != types.DictType:
            raise Exception( "Behavior specification should be a dictionary, %s spec is not supported." %
                             type(new_bvr) )
        if my.behaviors:
            t = new_bvr.get('type')
            idx_list = range(len(my.behaviors))
            idx_list.reverse()
            for i in idx_list:
                bvr = my.behaviors[i]
                # if we have a match then just remove the bvr ...
                if t == bvr.get('type'):
                    match = True
                    if t in [ 'click', 'click_up', 'drag' ]:
                        # need to also match 'mouse_btn' ...
                        btn_match = False
                        if new_bvr.get('mouse_btn') in ['LMB',None] and bvr.get('mouse_btn') in ['LMB',None]:
                            btn_match = True
                        elif new_bvr.get('mouse_btn') == bvr.get('mouse_btn'):
                            btn_match = True
                        # need to also match 'modkeys' ...
                        mod_match = False
                        mk_list = []
                        if bvr.get('modkeys'):
                            mk_list = bvr.get('modkeys').replace(" ","").split("+")
                            mk_list.sort()
                        new_mk_list = []
                        if new_bvr.get('modkeys'):
                            new_mk_list = new_bvr.get('modkeys').replace(" ","").split("+")
                            new_mk_list.sort()
                        if mk_list == new_mk_list:
                            mod_match = True
                        match = (btn_match and mod_match)
                    if match:
                        my.behaviors.remove( bvr )
        my.add_behavior( new_bvr )


    def convert_behavior_str(cls, bvr_str):
        '''converts a legacy behavior spec string into a required behavior spec dictionary'''
        bvr_str = bvr_str.replace("{","").replace("}","")
        bvr_bits = bvr_str.split(",")
        bvr_spec = {}
        for bvr_kv in bvr_bits:
            idx = bvr_kv.find(':')
            k = bvr_kv[ : idx ].strip()
            if k[0] not in [ '"', "'" ]:
                k = "'%s'" % k
            v = bvr_kv[ idx+1 : ].strip()
            if v[0] not in [ '"', "'" ]:
                v = "'%s'" % v
            stmt = 'bvr_spec[%s] = %s' % (k, v)
            exec stmt
        return bvr_spec

    convert_behavior_str = classmethod(convert_behavior_str)


    def add_event(my, event, function, idx=None):
        '''adds a function to call on a particular event'''
        if not my.events:
            my.events = {}

        if not my.events.has_key(event):
            my.events[event] = []
        if idx == None:
            my.events[event].append(function)
        else:
            my.events[event].insert(idx, function)

    def set_event(my, event, function):
        if not my.events:
            my.events = {}
        my.events[event] = [function]

    def remove_event(my, event):
        if not my.events:
            return
        if my.events.has_key(event):
            my.events.pop(event)
        
    def get_event_attr(my, event):
        ''' get all the functions already added to this particular event'''
        if not my.events:
            return ''

        functions = my.events.get(event)
        if functions:
            return ';'.join(functions)
        else:
            return ''

    def add_event_caller(my, event, event_name):
        '''calls a registered event which in turn calls all of its
        listeners'''
        event_container = WebContainer.get_event_container()
        function = event_container.get_event_caller(event_name)
        my.add_event(event, function)


    def set_post_ajax_script(my, script):
        '''sets a post ajax script to be executed after the current AjaxCmd 
        is run'''
        my.set_attr('post_ajax', script)

    def add_tip(my, message, title='', cls='tactic_tip'):
        '''add a tool tip to this html element'''
        #my.set_attr('rel', message)

        message = '%s::%s' %(title, message)
        my.set_attr('title', message)
        my.add_class(cls)
    
    def set_dynamic(my):
        my.set_attr('mode','dynamic')


    def center(my):
        # this adds "margin-left: auto; margin-right: auto;" ...
        my.add_class("center")

    def push_left(my):
        my.add_styles("margin-left: 0px; margin-left: auto;")

    def push_right(my):
        my.add_styles("margin-left: auto; margin-left: 0px;")


    def get_display(my):
        '''override the get display function of Widget.  This is the function
        that actually draws the html element to the buffer'''
        html = WebContainer.get_buffer()
        buffer = html.get_buffer()
        
        buffer.write("<%s" % my.type)

        attrs = []
        if my.attrs:
            for x,y in my.attrs.items():
                if type(x) == types.UnicodeType:
                    x = Common.process_unicode_string(x)
                if type(y) == types.UnicodeType:
                    y = Common.process_unicode_string(y)
                attrs.append( ' %s="%s"' % (x,y) )


            attr = " ".join( attrs )
            """
            attr = " ".join( [' %s="%s"' % (x,y) for x,y in my.attrs.items()] )
            if type(attr) == types.UnicodeType:
                attr = Common.process_unicode_string(attr)
            """
            buffer.write(attr)
            attr = None

        # now process behaviors and, if there are any, construct the SPT_BVR_LIST attribute and write it out.
        # also add the SPT_BVR class to the element if it does have behaviors.
        if my.behaviors:
            my.add_class('SPT_BVR')
            bvr_str_list = [ ' SPT_BVR_LIST="[' ]
            bvr_type_list = [ ' SPT_BVR_TYPE_LIST="[' ]
            #for c in range(len(my.behaviors)):
            for c, behavior in enumerate(my.behaviors):
                if c:
                    bvr_str_list.append(',')
                    bvr_type_list.append(',')

                bvr_spec_str = HtmlElement.get_json_string(behavior)
                # NOTE: this is to make the HTML be XML compliant
                #bvr_spec_str = bvr_spec_str.replace("<", "&lt;")
                #bvr_spec_str = bvr_spec_str.replace(">", "&gt;")
                #bvr_spec_str = bvr_spec_str.replace("&", "&amp;")
                bvr_str_list.append( bvr_spec_str )

                bvr_info = {
                    'type': behavior.get("type"),
                }
                if behavior.get("_handoff_"):
                    bvr_info['_handoff_'] = behavior.get("_handoff_")

                bvr_info_str = HtmlElement.get_json_string(bvr_info)
                bvr_type_list.append( bvr_info_str )


            bvr_str_list.append( ']"' )
            bvr_type_list.append( ']"' )
            buffer.write( "".join( bvr_str_list ) )
            buffer.write( "".join( bvr_type_list ) )
            bvr_str_list = None
            bvr_type_list = None

        # handle the style
        if my.styles:
            styles = []
            for name, value in my.styles.items():
                styles.append( "%s: %s" % (name,value) )
            buffer.write( " style='%s'" % ";".join(styles) )
            styles = None


        # handle relay styles
        if my.relay_styles:
            for relay_style in my.relay_styles:
                my.add(relay_style)
        
        # handle the class
        if my.classes:
            classes = my.classes.keys()
            buffer.write(" class='%s'" % " ".join(classes))
            classes = None

        # handle events
        if my.events:
            for key in my.events.keys():
                functions = my.events.get(key)
                function = "javascript:%s" % ";".join(functions)
                buffer.write( ' %s="%s"' % (key,function) )
                functions = None


        self_close = False
        if my.type in ["img", "br"] or (my.type == "input" and not my.widgets):
            self_close = True
        else:
            buffer.write(">")

        super(HtmlElement,my).get_display()

        # add the closing tag
        if self_close:
            buffer.write(" />")
        elif my.type == "span":
            buffer.write("</%s>" % my.type)
        elif my.type != 'br':
            #buffer.write("</%s>\n" % my.type)
            buffer.write("</%s>" % my.type)

        my.clear()



    ###################
    # Factory Methods
    ###################

    def p(widget=None):
        element = HtmlElement("p")
        element.add(widget)
        return element
    p = staticmethod(p)

    def b(widget=None):
        element = HtmlElement("b")
        element.add(widget)
        return element
    b = staticmethod(b)
   
    def i(widget=None):
        element = HtmlElement("i")
        element.add(widget)
        return element
    i = staticmethod(i)

    def blockquote(widget=None):
        element = HtmlElement("blockquote")
        element.add(widget)
        return element
    blockquote = staticmethod(blockquote)
   
    def hr(widget=None):
        element = HtmlElement("hr")
        element.set_attr("size", "2")
        return element
    hr = staticmethod(hr)
    
    def br(count=1, clear=None):
        widget = Widget()
        for i in xrange(count):
            element = HtmlElement("br")
            widget.add(element)
            if clear:
                element.set_attr("clear", clear)
            if count==1:
                return element
        return widget
    br = staticmethod(br)

    def h2(widget=None):
        element = HtmlElement("h2")
        element.add(widget)
        return element
    h2 = staticmethod(h2)    

    def h3(widget=None):
        element = HtmlElement("h3")
        element.add(widget)
        return element
    h3 = staticmethod(h3) 

    def h4(widget=None):
        element = HtmlElement("h4")
        element.add(widget)
        return element
    h4 = staticmethod(h4) 

    def style(widget=None):
        element = HtmlElement("style")
        element.add(widget)
        return element
    style = staticmethod(style) 
    
    def href(data=None,ref=None,target=None):
        element = HtmlElement("a")
        element.set_attr("href", ref)
        if target != None:
            element.set_attr("target", target)
        if data != None:
            element.add(data)
        return element
    href = staticmethod(href)

    def js_href(script, data=None,ref='#',target=None):
        href = HtmlElement.href(data, ref, target)
        href.add_event('onclick', '%s; return false;'%script)
        return href
    js_href = staticmethod(js_href)

    def label(widget=None):
        element = HtmlElement("label")
        element.add(widget)
        return element
    label = staticmethod(label)

    def div(widget=None):
        element = HtmlElement("div")
        element.add(widget)
        return element
    div = staticmethod(div)

    def span(widget=None):
        element = HtmlElement("span")
        element.add(widget)
        return element
    span = staticmethod(span)

    def pre(widget=None):
        element = HtmlElement("pre")
        element.add(widget)
        return element
    pre = staticmethod(pre)

    def blink(widget=None):
        element = HtmlElement("blink")
        element.add(widget)
        return element
    blink = staticmethod(blink)

    def table():
        return Table()
    table = staticmethod(table)

    def col():
        return HtmlElement("col")
    col = staticmethod(col)

    def tbody():
        return HtmlElement("tbody")
    tbody = staticmethod(tbody)

    def tr():
        return HtmlElement("tr")
    tr = staticmethod(tr)


    def th(data=None):
        return HtmlElement("th",data)
    th = staticmethod(th)

    def td(data=None):
        return HtmlElement("td",data)
    td = staticmethod(td)


    def ul(data=None):
        return HtmlElement("ul",data)
    ul = staticmethod(ul)

    def ol(data=None):
        return HtmlElement("ol",data)
    ol = staticmethod(ol)



    def li(data=None):
        return HtmlElement("li",data)
    li = staticmethod(li)







    def form(method="POST",enctype="multipart/form-data"):
        form = HtmlElement("form")
        form.set_attr("method", method)
        form.set_attr("enctype", enctype)
        return form
    form = staticmethod(form)


    def input():
        return HtmlElement("input")
    input = staticmethod(input)


    def button(value="button"):
        element = HtmlElement("input")
        element.add_attr("value", value)
        element.add_attr("type", "button")
        return element
    button = staticmethod(button)


    def text(value=""):
        element = HtmlElement("input")
        if value:
            element.add_attr("value", value)
        element.set_attr("type", "text")
        return element
    text = staticmethod(text)

    def textarea(rows=1,cols=10,widget=None):
        element = HtmlElement("textarea")
        element.set_attr("rows", rows)
        element.set_attr("cols", cols)
        if widget:
            element.add(widget)
        return element
    textarea = staticmethod(textarea)


    def select():
        return HtmlElement("select")
    select = staticmethod(select)

    def img(src=None):
        img = HtmlElement("img")
        img.set_attr("border","0")
        if src != None:
            img.set_attr("src", src)
        return img
    img = staticmethod(img)


    def spacer_div(width=1,height=1):
        div = DivWdg()
        img = HtmlElement("img")
        img.add_styles("border: 0px; text-decoration: none; padding: none; width: %spx; height: %spx;" % (width,height) )
        img.set_attr("src", "/context/icons/common/transparent_pixel.gif")
        div.add(img)
        return div
    spacer_div = staticmethod(spacer_div)


    def script(script_text=None):
        script = HtmlElement("script")
        if script_text != None:
            script.add(script_text)
        return script
    script = staticmethod(script)


    def function(function_name, script_text):
        function = "function %s() {\n%s\n}\n" % (function_name, script_text)
        script = HtmlElement.script(function)
        return script
    function = staticmethod(function)


    def iframe():
        iframe = HtmlElement("iframe")
        return iframe
    iframe = staticmethod(iframe)


    def embed(src=None):
        embed = HtmlElement("embed")
        if src:
            embed.add_attr("src", src)
        return embed
    embed = staticmethod(embed)




    def upload(name=None):
        upload = HtmlElement.input()
        upload.set_attr("type","file")
        if name:
            upload.set_attr("name",name)
        return upload
    upload = staticmethod(upload)


    def get_json_string(dict, use_cache=True):
        '''given a dictionary, return a javascript friendly json string as a js string'''
        dict_str = None
        if use_cache:
            data = Container.get("Html:json_str")
            if not data:
                data = {}
                Container.put("Html:json_str", data)

            key = str(dict)
            dict_str = data.get(key)
    
        if dict_str == None:
            try:
                dict_str = jsondumps(dict)
            except UnicodeDecodeError, e:
                if isinstance(dict, basestring):
                    dict = dict.decode('iso-8859-1')
                    dict_str = jsondumps(dict)

            dict_str = dict_str.replace('"', '&quot;')
            if use_cache:
                data[key] = dict_str

        return dict_str
    get_json_string = staticmethod(get_json_string)


    def set_round_corners(my, size=5, corners=[]):
        browser = WebContainer.get_web().get_browser()
        if browser == 'Mozilla':
            for corner in corners:
                if corner in ['TL']:
                    my.add_style("-moz-border-radius-topleft: %spx" % size)
                    my.add_style("border-top-left-radius: %spx" % size)
                elif corner in ['TR']:
                    my.add_style("-moz-border-radius-topright: %spx" % size)
                    my.add_style("border-top-right-radius: %spx" % size)
                elif corner in ['BL']:
                    my.add_style("-moz-border-radius-bottomleft: %spx" % size)
                    my.add_style("border-bottom-left-radius: %spx" % size)
                elif corner in ['BR']:
                    my.add_style("-moz-border-radius-bottomright: %spx" % size)
                    my.add_style("border-bottom-right-radius: %spx" % size)
            if not corners:
                my.add_style("-moz-border-radius: %spx" % size)
                my.add_style("border-radius: %spx" % size)

        elif browser in ['Webkit','Qt']:
            for corner in corners:
                if corner in ['TL']:
                    my.add_style("border-top-left-radius: %spx" % size)
                elif corner in ['TR']:
                    my.add_style("border-top-right-radius: %spx" % size)
                elif corner in ['BL']:
                    my.add_style("border-bottom-left-radius: %spx" % size)
                elif corner in ['BR']:
                    my.add_style("border-bottom-right-radius: %spx" % size)
            if not corners:
                my.add_style("border-radius: %spx" % size)

        elif browser == 'IE':
            if not corners:
                corners = ['TL','TR','BL','BR']
            for corner in corners:
                if corner in ['TL']:
                    my.add_style("border-top-left-radius: %spx" % size)
                elif corner in ['TR']:
                    my.add_style("border-top-right-radius: %spx" % size)
                elif corner in ['BL']:
                    my.add_style("border-bottom-left-radius: %spx" % size)
                elif corner in ['BR']:
                    my.add_style("border-bottom-right-radius: %spx" % size)



    def set_box_shadow(my, value="0px 0px 15px", color=None):

        if not color:
            color = my.get_color("shadow")
        if not color:
            theme = my.get_theme()
            if theme == "dark":
                color = "#000000"
            else:
                color = "rgba(0,0,0,0.4)"

        browser = WebContainer.get_web().get_browser()
        if browser == 'Mozilla':
            my.add_style("-moz-box-shadow: %s %s" % (value, color))
            # This is needed for Mozilla 13
            my.add_style("box-shadow: %s %s" % (value, color))
        elif browser in ['Webkit', 'Qt']:
            my.add_style("-webkit-box-shadow: %s %s" % (value, color))
        else:
            my.add_style("box-shadow: %s %s" % (value, color))



class DivWdg(HtmlElement):
    '''Basic DIV element'''

    def get_args_keys(cls):
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)

    ARGS_KEYS = {
        'html': 'HTML code to add inside the div'
    }


    def __init__(my,html=None, css=None, id=None, **kwargs ):
        super(DivWdg,my).__init__("div", css=css, id=id)
        if html:
            my.add(html)



    def set_scale(my, scale):
        browser = WebContainer.get_web().get_browser()
        if browser == 'Mozilla':
            my.add_style("-moz-transform", "scale(%s)" % scale)
        elif browser == 'Webkit':
            my.add_style("-webkit-transform", "scale(%s)" % scale)




class FloatDivWdg(DivWdg):
    '''DivWdg defined with a float style and width'''
    def __init__(my,string=None, float='left', width=None, css=None, id=None):
        super(FloatDivWdg,my).__init__(string, css, id)
        my.add_style('float', float)
        if width:
            my.add_style('width', width)
        
            

class SpanWdg(HtmlElement):
    '''Basic SPAN element'''
    def __init__(my,string=None, css=None, id=None):
        super(SpanWdg,my).__init__("span", css=css, id=id)
        if string:
            my.add(string)





class Table(HtmlElement):

    def __init__(my, name=None, css=None):
        super(Table,my).__init__("table")
        my.add_style("border-collapse","collapse")
        my.name = name
        if css:
            my.set_class(css)    
        my.rows = []
        my.tbodies = []
        my.current_tbody = None
        my.current_row = None
        my.current_cell = None
        my.hidden_row_wdgs = []
       
        # keep track of the number of columns
        my.num_cols = 0
        my.max_cols = 0

        my.is_dynamic_flag = False
        my.dynamic_row = None

    def is_dynamic(my, flag):
        '''determines whether to make the table dynamic'''
        my.is_dynamic_flag = flag
    
        if my.is_dynamic_flag:
            my.dynamic_row = my.add_row()


    def get_current_cell(my):
        return my.current_cell

    def add_col(my, css=None):
        col = HtmlElement.col()
        if css:
            col.set_class(css)
        my.add(col)
        return col

    def add_tbody(my):
        tbody = HtmlElement.tbody()
        #tbody.add_style('display','table-row-group')
        # each tbody can have a list of rows
        tbody.rows = []
        my.current_tbody = tbody
        my.tbodies.append(tbody)
        my.add(tbody)
        return my.current_tbody

    def close_tbody(my):
        my.current_tbody = None


    def get_current_tbody(my):
        return my.current_tbody


    def add_row(my, css=None, tr=None):

        # add hidden rows if hidden_row_wdgs is not empty 
        my.handle_hidden_rows()
        
        my.num_cols = 0
        if not tr:
            tr = HtmlElement.tr()

        if css:
            tr.set_class(css)
        
        
        if my.current_tbody:
            my.current_tbody.rows.append(tr)
            my.current_tbody.add(tr)
            
        else: 
            # some tr's may not be contained in a tbody even though 
            # the browser may draw it implicitly
            my.add(tr)
            #my.current_tbody = my.add_tbody() 

        my.rows.append(tr)
        my.current_row = tr
        return tr



    def handle_hidden_rows(my):
        '''handle hidden rows clear my.hidden_row_wdgs'''
        wdgs = my.hidden_row_wdgs
        my.hidden_row_wdgs = []
    
        Table.add_hidden_row(my, wdgs)

    def add_hidden_row(my, hidden_row_wdgs):
        elements = []
        for wdg in hidden_row_wdgs:
            tr,td = my.add_row_cell(wdg.get_hidden_row_wdg()) 
            tr.set_id("hidden_row_%s" % wdg.get_toggle_id())
            tr.add_styles("display: none;")

            elements.append([tr, td])
        return elements
    

    def add_header(my,data=None, css=None, row=None):
        my.num_cols += 1
        if my.num_cols > my.max_cols: my.max_cols = my.num_cols

        th = HtmlElement.th(data)
        if css:
            th.set_class(css)

        if row:
            current_row = row
        else:
            current_row = my.current_row

        if my.is_dynamic_flag and len(current_row.widgets) == 0:
            th_sep = HtmlElement.th('&nbsp;')
            current_row.add(th_sep)
            if css:
                th_sep.set_class(css)


        my.current_cell = th
        current_row.add(th)

        if my.is_dynamic_flag:
            th_sep = HtmlElement.th('&nbsp;')
            current_row.add(th_sep)
            if css:
                th_sep.set_class(css)

        return th


    def add_blank_header(my):
        return my.add_header('&nbsp;')

    def add_cell(my,data=None, css=None, add_hidden_wdg=False, row=None):
        my.num_cols += 1
        if my.num_cols > my.max_cols: my.max_cols = my.num_cols

        td = HtmlElement.td(data)
        if css:
            td.set_class(css)
        my.current_cell = td

        # make sure there is a row
        if my.current_row == None:
            my.add_row()


        if not row:
            row = my.current_row


        if my.is_dynamic_flag and my.num_cols == 1:
            # add a separator
            td_sep = HtmlElement.td("&nbsp;")
            row.add(td_sep)
            if css:
                td_sep.set_class(css)
       
        row.add(td)

        if add_hidden_wdg:
            my.add_hidden_row_wdg(data)


        if my.is_dynamic_flag:
            # add a separator
            td_sep = HtmlElement.td("&nbsp;")
            row.add(td_sep)
            if css:
                td_sep.set_class(css)
       
        return td
    
    def add_click_cell(my, input, event_name=None, data=None, css=None, add_hidden_wdg=False):
        ''' add a clickable cell which will toggle the checked state
        of the input '''
        td = my.add_cell(data, css, add_hidden_wdg)
        function = "a=get_element('%s');a.toggle_me()" % input.get_id()
        td.add_event('onClick', function)
        # attach the event if found
        if event_name:
            event = Event(event_name)
            input_func = event.get_caller()
            td.add_event('onClick', input_func)
            
        td.add_class('hand')
        return td

    def add_blank_cell(my):
        return my.add_cell('&nbsp;')


    def add_row_cell(my,data=None, css=None):
        '''adds a single cell that occupies an entire row'''
        tr = my.add_row(css)
        td = my.add_cell(data)

        if my.is_dynamic_flag:
            td.set_attr("colspan",my.max_cols*2)
            #td.set_attr("colspan","100%")
        else:
            #td.set_attr("colspan",my.max_cols)
            td.set_attr("colspan","100%")
            td.set_attr("colspan","50000")
        return (tr,td)


    def add_row_header(my,data=None):
        '''adds a single cell that occupies an entire row'''
        tr = my.add_row()
        th = my.add_header(data)
        if my.is_dynamic_flag:
            th.set_attr("colspan",my.max_cols*2)
        else:
            th.set_attr("colspan",my.max_cols)
        return (tr,th)


    def add_data(my,data):
        my.current_cell.add(data)

    def add_hidden_row_wdg(my, hidden_wdg):
        my.hidden_row_wdgs.append(hidden_wdg)

    def _get_col_index(my):
        return my.num_cols
    
    def get_next_col_name(my):
        '''get a default column name based on table name and col index'''
        table_name = my.name
        if table_name == None:
            table_name = my.generate_unique_id('table')
        return "%s_col%d" % (table_name, my._get_col_index())     
   
    def set_max_width(my, use_css=False):
        if use_css:
            if WebContainer.get_web().is_IE():
                my.add_style("width", "95%")
            else:
                my.add_style("width", "100%")
        else:
            # dynamic resizing doesn't work with css setting with %.
            my.set_attr("width", "100%")


    def add_dynamic_header(my,data=None, css=None, row=None):
        if row:
            current_row = row
        else:
            current_row = my.current_row

        # the first column
        if my.is_dynamic_flag and len(current_row.widgets) == 0:
            div = DivWdg()
            img = HtmlElement.img("/context/icons/common/table/square_grey.png")
            div.add(img)

            th_sep = HtmlElement.th(div)
            current_row.add(th_sep)
            if css:
                th_sep.set_class(css)

        # add the moving header
        img = HtmlElement.img("/context/icons/common/table/square_grey.png")
        img.add_style("width: 100%")
        img.add_style("height: 10px")
        data = DivWdg(img)

        th = HtmlElement.th(data)

        current_row.add(th)

        # add the resize header
        if my.is_dynamic_flag:
            div = DivWdg()
            img = HtmlElement.img("/context/icons/common/table/square_grey.png")
            div.add(img)

            th_sep = HtmlElement.th(div)
            current_row.add(th_sep)
            if css:
                th_sep.set_class(css)

        return th


            
   
    def get_display(my):
        if my.is_dynamic_flag and my.get_id():
            for i in range(0, my.max_cols):
                my.add_dynamic_header(row=my.dynamic_row)
            my.add("<script>new DynamicTable('%s')</script>" % my.get_id() )

        my.handle_hidden_rows()
        for row in my.rows:
            if len(row.widgets) == 1 and len(row.widgets ) < my.max_cols:
                row.widgets[0].set_attr("colspan", my.max_cols)
        return super(Table,my).get_display()

class Tbody(Table):
    ''' a collection of tr's without the parent <tbody>'''
    def __init__(my, name=None, css=None):
        HtmlElement.__init__(my, name)
        my.rows = []
        my.current_row = None
        my.current_cell = None
        my.hidden_row_wdgs = []
       
        # keep track of the number of columns
        my.num_cols = 0
        my.max_cols = 0
        my.is_dynamic_flag = False

    def add_row(my, css=None):

        # add hidden rows if hidden_row_wdgs is not empty 
        my.handle_hidden_rows()
        
        my.num_cols = 0
        tr = HtmlElement.tr()
        if css:
            tr.set_class(css)
        my.rows.append(tr)
        my.current_row = tr
        my.add(tr)
        return tr

    
            
    def get_display(my):
        my.handle_hidden_rows()
        
        for row in my.rows:
            if len(row.widgets) == 1 and len(row.widgets ) < my.max_cols:
                row.widgets[0].set_attr("colspan", my.max_cols)
        return Widget.get_display(my)




#
# HTML 5 support
#

class Canvas(HtmlElement):
    '''Basic Canvas element'''
    def __init__(my, css=None, id=None ):
        super(Canvas,my).__init__("canvas", css=css, id=id)



class Video(HtmlElement):
    '''Basic Video element'''
    def __init__(my, css=None, id=None ):
        super(Video,my).__init__("video", css=css, id=id)




# use psyco if present
try:
    import psyco
    psyco.bind(HtmlElement.get_display)
except ImportError:
    pass



