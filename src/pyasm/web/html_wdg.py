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
        'SpanWdg', 'ButtonWdg', 'StyleWdg', 'Tbody', 'Table', 'Canvas', 'Video']

import os
import re
import string
import types
import locale
import sys
import hashlib

from dateutil import parser


from pyasm.common import Container, jsondumps, jsonloads, Common, FormatValue, Environment
from pyasm.search import Search, SObject, SearchType
from pyasm.biz import PrefSetting
from pyasm.common import SPTDate

from .event_container import *
from .widget import Widget
from .web_container import WebContainer

import six
basestring = six.string_types

IS_Pv3 = sys.version_info[0] > 2


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

    def _get_my_attrs(self):
        if self._attrs == None:
            self._attrs = {}
        return self._attrs
    def _set_my_attrs(self, attrs):
        self._attrs = attrs
    attrs = property(_get_my_attrs, _set_my_attrs)



    #def _get_my_behaviors(self):
    #    if self._behaviors == None:
    #        self._behaviors = []
    #    return self._behaviors
    #def _set_my_behaviors(self, behaviors):
    #    self._behaviors = behaviors
    #behaviors = property(_get_my_behaviors, _set_my_behaviors)



    def __init__(self, type=None, child=None, css=None, id=None):

        if not type or type == "None":
            type = "div"
            #raise Exception("No type defined in HTML widget")


        self._attrs = None
        self.events = None
        self.type = type
        self.classes = None
        self.styles = None
        self.relay_styles = None
        self.behaviors = None
        self.updates = None

        if css:
            self.set_class(css)    

        if id:
            self.set_id(id)

        super(HtmlElement,self).__init__()

        if child:
            self.add(child)


    """
        HtmlElement.count += 1
        #print("create: ", HtmlElement.count)
        search_key = self.type
        count = HtmlElement.track.get(search_key)
        if count == None:
            HtmlElement.track[search_key] = 1
        else:
            HtmlElement.track[search_key] = count + 1

    count = 0
    track = {}
    def __del__(self):
        self.del_ref()

    def del_ref(self):
        HtmlElement.count -= 1

        search_key = self.type
        print("search_key: ", search_key)
        count = HtmlElement.track[search_key]
        #print("delete: ", HtmlElement.count, search_key, count)

        if count == 1:
            del(HtmlElement.track[search_key])
        elif count == 0:
            sdfsfdafsd
        else:
            HtmlElement.track[search_key] = count - 1

        #print(HtmlElement.track)
        self.data = None
        self.update_data = None

        total = 0
        for key, x in HtmlElement.track.items():
            if x > 1:
                print(key, x)
            total += x
        print("total: ", total)

        self.clear()
    """



    def clear(self):

        #self.type = None
        #self.classes = None
        self.attrs = None
        self.events = None
        self.styles = None
        self.behaviors = None
        self.updates = None

        self._widgets = None
        self.named_widgets = None
        self.typed_widgets = None

    def set_type(self, type):
        '''Set the type of html element.  This constitutes all of the elements
        that define html. For example: p, hr, br, img, a ...
        '''
        assert(type)
        self.type = type


    def get_attr(self, name):
        '''Get the value of an attribute of the html element'''
        if name not in self.attrs:
            return None
        return self.attrs[name]

    def set_attr(self, name, value):
        '''Set an attribute of the html element'''

        if isinstance(value, basestring):
            self.attrs[name] = value
        # This is never called because of the above
        #elif isinstance(value, unicode):
        #    self.attrs[name] = value.encode('utf-8')
        else:
            self.attrs[name] = str(value)


    def add_attr(self, name, value):
        '''Set an attribute of the html element'''
        self.set_attr(name, value)

    def add_attribute(self, name, value):
        '''Set an attribute of the html element'''
        self.set_attr(name, value)

    def set_attribute(self, name, value):
        '''Set an attribute of the html element'''
        self.set_attr(name, value)


    def set_json_attr(self, name, value):
        value = jsondumps(value).replace('"', "&quot;")
        self.set_attr(name, value)


    def set_class(self, value):
        '''Set the class attribute of the html element for css styling'''
        #self.classes = {}
        self.add_class(value)
   
    def has_class(self, value):
        if not self.classes:
            return False
        if value in self.classes:
            return True
        return False

    def add_class(self, value):
        '''Adds a class attribute of the html element for css styling'''
        assert value
        if not self.classes:
            self.classes = {}
        self.classes[value] = value

    def remove_class(self, value):
        '''Adds a class attribute of the html element for css styling'''
        assert value
        if value in self.classes:
            self.classes.pop(value)

        
    def set_id(self, id):
        '''Sets the id attribute of the html element'''
        self.attrs['id'] = id

    def set_unique_id(self,prefix=None, force=False):
        if force:
            unique_id = 0
        else:
            unique_id = self.get_id()
        if not unique_id:
            unique_id = self.generate_unique_id(is_random=True)
            if prefix:
                unique_id = prefix + '_' + unique_id
            self.set_id(unique_id)
        return unique_id

    def get_id(self):
        '''Returns the id attribute of the html element'''
        return self.attrs.get('id')


    def get_unique_event(self, prefix='event'):
        unique_id = self.generate_unique_id(is_random=True)
        unique_id = prefix + '_' + unique_id
        return unique_id


    def add_looks(self, look_palette_names_str):
        if look_palette_names_str.find(" ") != -1:
            pals = look_palette_names_str.split(" ")
        else:
            pals = [ look_palette_names_str ]

        for pal_name in pals:
            pal_name = pal_name.strip()
            if pal_name:
                self.add_class( "look_%s" % pal_name )


    def set_style(self, style):
        '''sets a style attribute. set_style() overrides add_style() calls'''
        style = style.rstrip(";")
        if not self.styles:
            self.styles = {}
        self.attrs['style'] = style


    def add_style(self, name, value=None, override=True, bs=True):
        '''add a style attribute

        bs refers to compatibility with updated Bootstrap
        UI. If bs is False and the Bootstrap UI is used,
        the style will not be added.'''

        if not bs and self._use_bootstrap():
            return

        if not name:
            return
        if value == None:
            if name.find(";") != -1:
                name = name.split(";")[0]
            name, value = name.split(": ")
        if not self.styles:
            self.styles = {}

        elif not override and name in self.styles:
            return
        self.styles[name] = value


    def get_style(self, name):
        if self.styles:
            return self.styles.get(name) or ""
        else:
            return ""


    def add_styles(self, styles):
        if type(styles) == str:
            styles_list = styles.split(";")
            for s in styles_list:
                self.add_style( s.strip() )
        elif type(styles) == dict:
            for s_name,s_value in styles.iteritems():
                self.add_style( s_name, str(s_value) )


    def add_smart_style(self, class_name, name, value):
        style = HtmlElement.style()
        element_id = self.get_id()
        assert element_id
        style.add("#%s .%s { %s: %s; }" % (element_id, class_name, name, value))
        if self.relay_styles == None:
            self.relay_styles = []
        self.relay_styles.append(style)

    def add_smart_styles(self, class_name, data):
        for name, value in data.items():
            self.add_smart_style(class_name, name, value)


    def add_relay_style(self, class_name, name, value):
        return self.add_smart_style(class_name, name, value)

    def add_relay_styles(self, class_name, data):
        for name, value in data.items():
            self.add_smart_style(class_name, name, value)




    def get_palette(self):
        from .palette import Palette
        palette = Palette.get()
        return palette


    def get_theme(self):
        from .palette import Palette
        palette = Palette.get()
        return palette.get_theme()


    def get_color(self, palette_key, modifier=0, default=None):
        from .palette import Palette
        palette = Palette.get()
        color = palette.color(palette_key, modifier, default=default)
        return color

    def add_color(self, name, palette_key, modifier=0, default=None):
        from .palette import Palette
        palette = Palette.get()
        color = palette.color(palette_key, modifier, default=default)
        self.add_style("%s: %s" % (name, color) )
        #self.add_style("%s: var(spt_palette_%s)" % (name, color) )
        return color



    def get_gradient(self, palette_key, modifier=0, range=-20, reverse=False, default=None,angle=180):

        from .palette import Palette
        from .web_container import WebContainer
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
            if web.get_browser() == 'Qt':
                gradient = "-webkit-gradient(linear, 0%% 0%%, 0%% 100%%, from(%s), to(%s))" % (color1, color2)
            else:
                gradient = "linear-gradient(%sdeg, %s, %s)" % (angle, color1, color2)
            return gradient


    def add_gradient(self, name, palette_key, modifier=0, range=-20, reverse=False, default=None):
        gradient = self.get_gradient(palette_key, modifier=modifier, range=range, reverse=reverse, default=default)

        self.add_style("%s: %s" % (name,gradient) )
        return gradient




    def add_border(self, modifier=None, style="solid", direction=None, color="border", size="1px"):
        '''@params: direction can be top left bottom right, default to None''' 
        # border is a palette color; color argument may take a color name or a hex value also
        border_direction = 'border'
        if direction:
            border_direction = 'border-%s'% direction

        if size and border_direction == "border":
            self.add_style("border-style: %s" % style)
            self.add_style("border-width: %s" % size)
            self.add_style("border-color: %s" % self.get_color(color,modifier=modifier))
        else:
            self.add_style("%s: %s %s %s" % (border_direction, style, size, self.get_color(color, modifier=modifier) ))
        

    def add_hover(self, palette_key='background', modifier=-10):
        '''convenience function to add a standard hover'''
        hover_color = self.get_color(palette_key, modifier)
        self.add_behavior( {
            'type': 'hover',
            'hover': hover_color,
            'cbjs_action_over': '''
            bvr.src_el.setStyle("background", bvr.hover);
            ''',
            'cbjs_action_out': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )
        self.add_class("hand")


    # convenience method for z-sorting mechanism ...
    def set_z_start(self, z_start):
        self.add_class("SPT_Z")
        self.set_attr("spt_z_start",str(z_start))


    def get_children(self):
        '''returns a list of the children widgets of the html element'''
        return self.widgets

    def get_dom_path(self):
        '''returns the javascript dom path of the html element'''
        id = self.get_id()
        assert id

        return "document.form.%s" %id


    # NOTE: both add_named_listener and set_named_listener both only accept a 'cbjs_' based call-back string
    #       ... 'cbfn_' is not supported for this. I don't think 'cbfn_' format is really needed anymore.
    #
    def add_named_listener(self, event_name, cbjs_action_str, extra_bvr=None):
        self.add_behavior( self._get_named_listener_bvr(event_name, cbjs_action_str, extra_bvr) )


    def set_named_listener(self, event_name, cbjs_action_str, extra_bvr=None):
        self.set_behavior( self._get_named_listener_bvr(event_name, cbjs_action_str, extra_bvr) )


    def _get_named_listener_bvr(self, event_name, cbjs_action_str, extra_bvr):
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
    def force_default_context_menu(self):
        self.add_event( "oncontextmenu", "spt.force_default_context_menu = true;" )

    def add_behavior(self, bvr_spec):
        '''adds an individual behavior specification to the HTML based widget'''
        #print("bvr: ", str(bvr_spec).replace(r"\n", "\n"))
        #print("---")
        if self.behaviors == None:
            self.behaviors = []

        #if type(bvr_spec) == types.DictType:
        if isinstance(bvr_spec, dict):
            # handle any cbjs string value that has newlines (e.g. ones specified using triple single quote block
            # quotes in order to have the javascript code readable as indented multi-line code) ...
            regex = re.compile( r'\n\s*' )

            if not bvr_spec.get('type'):
                bvr_spec['type'] = 'click'

            if self.__class__.__name__.find('CheckboxWdg') != -1:
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
                    

            #for k,v in bvr_spec.iteritems():
            for k,v in bvr_spec.items():
                if 'cbjs' in k and '\n' in v:
                    bvr_spec[k] = regex.sub( '\n', v )
            self.behaviors.append( bvr_spec )
        elif isinstance(bvr_spec, six.string_types):
            # legacy support for any '.add_behavior' calls that provide a bvr_spec argument that is a string
            # representation of a behavior specification dictionary
            self.behaviors.append( self.convert_behavior_str(bvr_spec) )
        else:
            raise Exception( "Behavior specification should be a dictionary, %s spec is not supported." %
                             type(bvr_spec) )

        count = Container.get("Widget:bvr_count")
        if not count:
            count = 1
        else:
            count += 1
        Container.put("Widget:bvr_count", count)


    def add_relay_behavior(self, behavior):
        # should really build this in so that we're not creating an event
        # in a behavior (seems like an extra step)
        match_class = behavior.get('bvr_match_class')
        relay_behavior = {
        'type': 'load',
        'bvr': behavior,
        'bvr_match_class': match_class,
        'cbjs_action': r'''
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
                bvr.bvr_match_class = match;
                bvr.src_el = src_el;
                eval( "var f = function() {\n"+bvr.cbjs_action+"\n};" )
                f();
            };
            bvr.src_el.addEvent(event_key, func);

            // find all of the PUW
            setTimeout( function() {
                var stubs = bvr.src_el.getElements(".SPT_PUW_STUB");
                stubs.forEach( function(stub) {
                    var puw =  stub.spt_puw_el;
                    puw.addEvent(event_key, func);
                } );

            }, 0 );

        '''
        }
        self.add_behavior(relay_behavior)
 




    def set_behavior(self, new_bvr):
        # NOTE: new_bvr MUST be a dictionary! Not supporting string behavior spec when setting to override
        if self.behaviors == None:
            self.behaviors = []

        if not isinstance(new_bvr, dict):
            raise Exception( "Behavior specification should be a dictionary, %s spec is not supported." %
                             type(new_bvr) )
        if self.behaviors:
            t = new_bvr.get('type')
            idx_list = range(len(self.behaviors))
            idx_list.reverse()
            for i in idx_list:
                bvr = self.behaviors[i]
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
                        self.behaviors.remove( bvr )
        self.add_behavior( new_bvr )


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
            exec(stmt)
        return bvr_spec

    convert_behavior_str = classmethod(convert_behavior_str)


    def add_event(self, event, function, idx=None):
        '''adds a function to call on a particular event'''
        if not self.events:
            self.events = {}

        if event not in self.events:
            self.events[event] = []
        if idx == None:
            self.events[event].append(function)
        else:
            self.events[event].insert(idx, function)

    def set_event(self, event, function):
        if not self.events:
            self.events = {}
        self.events[event] = [function]

    def remove_event(self, event):
        if not self.events:
            return
        if event in self.events:
            self.events.pop(event)
        
    def get_event_attr(self, event):
        ''' get all the functions already added to this particular event'''
        if not self.events:
            return ''

        functions = self.events.get(event)
        if functions:
            return ';'.join(functions)
        else:
            return ''

    def add_event_caller(self, event, event_name):
        '''calls a registered event which in turn calls all of its
        listeners'''
        event_container = WebContainer.get_event_container()
        function = event_container.get_event_caller(event_name)
        self.add_event(event, function)


    def set_post_ajax_script(self, script):
        '''sets a post ajax script to be executed after the current AjaxCmd 
        is run'''
        self.set_attr('post_ajax', script)

    def add_tip(self, message, title='', cls='tactic_tip'):
        '''add a tool tip to this html element'''
        #self.set_attr('rel', message)

        message = '%s::%s' %(title, message)
        self.set_attr('title', message)
        self.add_class(cls)
    
    def set_dynamic(self):
        self.set_attr('mode','dynamic')


    def center(self):
        # this adds "margin-left: auto; margin-right: auto;" ...
        self.add_class("center")

    def push_left(self):
        self.add_styles("margin-left: 0px; margin-left: auto;")

    def push_right(self):
        self.add_styles("margin-left: auto; margin-left: 0px;")


    def get_display(self):
        '''override the get display function of Widget.  This is the function
        that actually draws the html element to the buffer'''
        html = WebContainer.get_buffer()
        buffer = html.get_buffer()

        if not self.type:
            #raise Exception("No type defined in HTML widget [%s]" % self)
            self.type = "div"
      
        buffer.write("<%s" % self.type)

        attrs = []
        if self.attrs:
            for x,y in self.attrs.items():
                if not IS_Pv3:
                    #if type(x) == types.UnicodeType:
                    x = Common.process_unicode_string(x)
                    y = Common.process_unicode_string(y)
                attrs.append( ' %s="%s"' % (x,y) )


            attr = " ".join( attrs )
            """
            attr = " ".join( [' %s="%s"' % (x,y) for x,y in self.attrs.items()] )
            if type(attr) == types.UnicodeType:
                attr = Common.process_unicode_string(attr)
            """
            buffer.write(attr)
            attr = None

        # now process behaviors and, if there are any, construct the SPT_BVR_LIST attribute and write it out.
        # also add the SPT_BVR class to the element if it does have behaviors.
        if self.behaviors:
            self.add_class('SPT_BVR')
            bvr_str_list = [ ' SPT_BVR_LIST="[' ]
            bvr_type_list = [ ' SPT_BVR_TYPE_LIST="[' ]
            #for c in range(len(self.behaviors)):
            for c, behavior in enumerate(self.behaviors):
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
        if self.styles:
            styles = []
            for name, value in self.styles.items():
                styles.append( "%s: %s" % (name,value) )
            buffer.write( " style='%s'" % ";".join(styles) )
            styles = None


        # handle relay styles
        if self.relay_styles:
            for relay_style in self.relay_styles:
                self.add(relay_style)
        
        # handle the class
        if self.classes:
            classes = self.classes.keys()
            buffer.write(" class='%s'" % " ".join(classes))
            classes = None

        # handle events
        if self.events:
            for key in self.events.keys():
                functions = self.events.get(key)
                function = "javascript:%s" % ";".join(functions)
                buffer.write( ' %s="%s"' % (key,function) )
                functions = None


        self_close = False
        if self.type in ["img", "br"] or (self.type == "input" and not self.widgets):
            self_close = True
        else:
            buffer.write(">")

        super(HtmlElement,self).get_display()

        # add the closing tag
        if self_close:
            buffer.write(" />")
        elif self.type == "span":
            buffer.write("</%s>" % self.type)
        elif self.type != 'br':
            #buffer.write("</%s>\n" % self.type)
            buffer.write("</%s>" % self.type)

        # clean up the widget
        self.clear()



    ###################
    # Dynamic Updates
    ###################

    def add_update(self, update):
        if self.updates == None:
            self.updates = [] 

        self.set_unique_id("SPT")
        self.updates.append(update)

        self.add_class("spt_update")
        self.add_behavior( {
            'type': 'load',
            'update': update,
            'cbjs_action': '''
            var id = bvr.src_el.getAttribute("id");
            var update = {};
            update[id] = bvr.update;
            bvr.src_el.spt_update = update;
            '''
        } )


    # TODO: still needs work
    """
    def add_update_text(self, update, value=None):
        if self.updates == None:
            self.updates = [] 

        self.set_unique_id("SPT")
        self.updates.append(update)


        if value:
            self.add(value)
        else:
            self.add( self.eval_update(update) )

        self.add_class("spt_update")
        self.add_behavior( {
            'type': 'load',
            'update': update,
            'cbjs_action': '''
            var id = bvr.src_el.getAttribute("id");
            var update = {};
            update[id] = bvr.update;
            bvr.src_el.spt_update = update;
            '''
        } )




    def add_update_attr(self, attr, update):
        if self.updates == None:
            self.updates = []

        update['attr'] = attr

        self.set_unique_id("SPT")
        self.updates.append(update)

        # evaluate
        self.add_attr(attr, self.eval_update(update) )
    """



    def add_update_expression(self, expr):
        value = Search.eval(expr)
        self.add(value)
        self.add_update( {
            'expression': expr
        } )


    def get_timezone_value(cls, value, format="%b %d, %Y - %H:%M"):
        '''given a datetime value, use the My Preferences time zone'''
        timezone = PrefSetting.get_value_by_key('timezone')

        if timezone in ["local", '']:
            value = SPTDate.convert_to_local(value)
        else:
            value = SPTDate.convert_to_timezone(value, timezone)
       
        try:
            encoding = locale.getlocale()[1]		
            value = value.strftime(format).decode(encoding)
        except:
            value = value.strftime(format)

        return value
    
    get_timezone_value = classmethod(get_timezone_value)


    def eval_update(cls, update):
        handler = update.get("handler")
        if handler:
            handler = Common.create_from_class_path(handler, kwargs={'update': update})

            value = handler.get_value()
            if value != None:
                return value

            column = handler.get_column()
            expression = handler.get_expression()
            compare = handler.get_compare()
            search_key = handler.get_search_key()
            expr_key = handler.get_expr_key()
            site = handler.get_site()


        else:

            search_type = update.get("search_type")
            column = update.get("column")
            expression = update.get("expression")
            compare = update.get("compare")
            return_type = update.get("return")


            #print("expression: ", expression)

            # search key is used to determine whether a change has occured.
            # when it is None, the expression is always evaluated ... however,
            # sometimes a search key is needed for the expression. In this case,
            # use "expr_key".
            search_key = update.get("search_key")
            expr_key = update.get("expr_key")



            # NOTE: this is explicitly not supported.  This would allow a client
            # to set the site which is forbidden
            #site = update.get("site")
            site = None


        from pyasm.security import Site
        try:
            if site:
                Site.set_site(site)


            value = update.get("value")
            if value != None:
                return value

            # get the sobject

            if search_type:
                return True
            elif search_key:
                sobject = Search.get_by_search_key(search_key)
            elif expr_key:
                sobject = Search.get_by_search_key(expr_key)
            else:
                sobject = None

            if not sobject and not expression:
                return


            if column:
                value = sobject.get_value(column)

                data_type = SearchType.get_column_type(sobject.get_search_type(), column)
                if data_type in ["timestamp","time"]: 
                    # convert to user timezone
                    if not SObject.is_day_column(column) and value:
                        # This date is assumed to be GMT
                        date = parser.parse(value)
                        value = cls.get_timezone_value(date)
                    else:
                        pass


            elif compare:
                value = Search.eval(compare, sobject, single=True)
                print("compare: ", compare)
                print("value: ", value)

            elif expression:
                value = Search.eval(expression, sobject, single=True)
                #print("sobject: ", sobject.get_search_key())
                #print("expression: ", expression)
                #print("value: ", value)
                #print("\n")

            format_str = update.get("format")
            if format_str:
                format = FormatValue()
                value = format.get_format_value( value, format_str )


        finally:
            if site:
                Site.pop_site()

        if return_type == "sobject":
            return sobject.get_sobject_dict()
        else:
            return value
    eval_update = classmethod(eval_update)


    def get_updates(self):
        return {self.get_id(): self.updates}



    #
    # Command key generation
    #
    def generate_command_key(self, cmd, kwargs={}, ticket=None):
        if ticket and not ticket.isalnum():
            raise Exception("No valid ticket")

        tmp_dir = Environment.get_tmp_dir(include_ticket=True)

        login = Environment.get_user_name()

        # use a non-random key
        seed = jsondumps(kwargs)
        key = "%s%s%s" % (ticket, cmd, seed)
        hash_object = hashlib.sha512(key.encode())
        key = "$%s" % hash_object.hexdigest()[:12]
        #key = "$"+Common.generate_random_key()

        self.add_attr("SPT_CMD_KEY", key)

        filename = "key_" + key.lstrip("$") + ".txt"
        path = "%s/%s" % (tmp_dir, filename)
        if os.path.exists(path):
            return key

        f = open(path, "w")
        data = {
            "class_name": cmd,
            "login": login,
            "ticket": ticket,
            "kwargs": kwargs,
        }
        f.write(jsondumps(data))
        f.close()

        return key


    def generate_api_key(self, api_name, inputs={}, ticket=None, attr=""):
        if ticket and not ticket.isalnum():
            raise Exception("No valid ticket")

        if not ticket:
            ticket = Environment.get_ticket()
        
        tmp_dir = Environment.get_tmp_dir(include_ticket=True)

        if not tmp_dir:
            raise Exception("TMP_DIR config not defined")
        
        if api_name.startswith("p_"):
            api_name = api_name.lstrip("p_")

        login = Environment.get_user_name()

        # use a non-random key
        seed = jsondumps(inputs)
        key = "%s%s%s" % (ticket, api_name, seed)
        hash_object = hashlib.sha512(key.encode())
        key = "$%s" % hash_object.hexdigest()[:12]
        #key = "$"+Common.generate_random_key()

        if attr:
            self.add_attr("SPT_%s_API_KEY" % attr.capitalize(), key)
        else:
            self.add_attr("SPT_API_KEY", key)


        filename = "api_key_" + key.lstrip("$") + ".txt"
        path = "%s/%s" % (tmp_dir, filename)
        if os.path.exists(path):
            return key

        f = open(path, 'w')
        args = {
            "method": api_name,
            "login": login,
            "ticket": ticket,
            "inputs": inputs
        }
        f.write(jsondumps(args))
        f.close()

        return key
    

    def generate_widget_key(self, class_name, inputs={}, ticket=None, attr="", unique=False):

        if ticket and not ticket.isalnum():
            raise Exception("No valid ticket")

        if not ticket:
            ticket = Environment.get_ticket()
        
        tmp_dir = Environment.get_tmp_dir(include_ticket=True)
        
        if not tmp_dir:
            raise Exception("TMP_DIR config not defined")
        
        if class_name.startswith("$"):
            raise Exception("Wrong class name")

        login = Environment.get_user_name()

        #unique = True
        if unique:
            key = "$"+Common.generate_random_key()
        else:
            # use a non-random key
            seed = jsondumps(inputs)
            key = "%s%s%s" % (ticket, class_name, seed)

            hash_object = hashlib.sha512(key.encode())
            key = "$%s" % hash_object.hexdigest()[:12]

        if attr:
            self.add_attr("SPT_%s_WIDGET_KEY" % attr.capitalize(), key)
        else:
            self.add_attr("SPT_WIDGET_KEY", key)


        filename = "widget_key_" + key.lstrip("$") + ".txt"
        path = "%s/%s" % (tmp_dir, filename)
        if os.path.exists(path):
            return key

        f = open(path, "w")
        args = {
            "method": class_name,
            "login": login,
            "ticket": ticket,
            "inputs": inputs
        }
        f.write(jsondumps(args))
        f.close()

        return key





    ###################
    # Factory Methods
    ###################
    
    def body(widget=None):
        element = HtmlElement("body")
        element.add(widget)
        return element
    body = staticmethod(body)

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
        for i in range(count):
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
            except UnicodeDecodeError as e:
                if isinstance(dict, basestring):
                    dict = dict.decode('iso-8859-1')
                    dict_str = jsondumps(dict)

            dict_str = dict_str.replace('"', '&quot;')
            if use_cache:
                data[key] = dict_str

        return dict_str
    get_json_string = staticmethod(get_json_string)


    def set_round_corners(self, size=5, corners=[]):
        browser = WebContainer.get_web().get_browser()
        if browser == 'Mozilla':
            for corner in corners:
                if corner in ['TL']:
                    self.add_style("-moz-border-radius-topleft: %spx" % size)
                    self.add_style("border-top-left-radius: %spx" % size)
                elif corner in ['TR']:
                    self.add_style("-moz-border-radius-topright: %spx" % size)
                    self.add_style("border-top-right-radius: %spx" % size)
                elif corner in ['BL']:
                    self.add_style("-moz-border-radius-bottomleft: %spx" % size)
                    self.add_style("border-bottom-left-radius: %spx" % size)
                elif corner in ['BR']:
                    self.add_style("-moz-border-radius-bottomright: %spx" % size)
                    self.add_style("border-bottom-right-radius: %spx" % size)
            if not corners:
                self.add_style("-moz-border-radius: %spx" % size)
                self.add_style("border-radius: %spx" % size)

        elif browser in ['Webkit','Qt']:
            for corner in corners:
                if corner in ['TL']:
                    self.add_style("border-top-left-radius: %spx" % size)
                elif corner in ['TR']:
                    self.add_style("border-top-right-radius: %spx" % size)
                elif corner in ['BL']:
                    self.add_style("border-bottom-left-radius: %spx" % size)
                elif corner in ['BR']:
                    self.add_style("border-bottom-right-radius: %spx" % size)
            if not corners:
                self.add_style("border-radius: %spx" % size)

        elif browser == 'IE':
            if not corners:
                corners = ['TL','TR','BL','BR']
            for corner in corners:
                if corner in ['TL']:
                    self.add_style("border-top-left-radius: %spx" % size)
                elif corner in ['TR']:
                    self.add_style("border-top-right-radius: %spx" % size)
                elif corner in ['BL']:
                    self.add_style("border-bottom-left-radius: %spx" % size)
                elif corner in ['BR']:
                    self.add_style("border-bottom-right-radius: %spx" % size)



    def set_box_shadow(self, value="0px 0px 15px", color=None):

        if not color:
            color = self.get_color("shadow")
        if not color:
            theme = self.get_theme()
            if theme == "dark":
                color = "#000000"
            else:
                color = "rgba(0,0,0,0.4)"

        browser = WebContainer.get_web().get_browser()
        if browser == 'Mozilla':
            self.add_style("-moz-box-shadow: %s %s" % (value, color))
            # This is needed for Mozilla 13
            self.add_style("box-shadow: %s %s" % (value, color))
        elif browser in ['Webkit', 'Qt']:
            self.add_style("-webkit-box-shadow: %s %s" % (value, color))
        else:
            self.add_style("box-shadow: %s %s" % (value, color))



class DivWdg(HtmlElement):
    '''Basic DIV element'''

    def get_args_keys(cls):
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)

    ARGS_KEYS = {
        'html': 'HTML code to add inside the div'
    }


    def __init__(self,html=None, css=None, id=None, **kwargs ):
        super(DivWdg,self).__init__("div", css=css, id=id)
        if html:
            self.add(html)



    def set_scale(self, scale):
        browser = WebContainer.get_web().get_browser()
        if browser == 'Mozilla':
            self.add_style("-moz-transform", "scale(%s)" % scale)
        elif browser == 'Webkit':
            self.add_style("-webkit-transform", "scale(%s)" % scale)




class FloatDivWdg(DivWdg):
    '''DivWdg defined with a float style and width'''
    def __init__(self,string=None, float='left', width=None, css=None, id=None):
        super(FloatDivWdg,self).__init__(string, css, id)
        self.add_style('float', float)
        if width:
            self.add_style('width', width)
        
            

class SpanWdg(HtmlElement):
    '''Basic SPAN element'''
    def __init__(self,string=None, css=None, id=None):
        super(SpanWdg,self).__init__("span", css=css, id=id)
        if string:
            self.add(string)


            

class ButtonWdg(HtmlElement):
    '''Basic Button element'''
    def __init__(self,string=None, css=None, id=None):
        super(ButtonWdg,self).__init__("button", css=css, id=id)
        if string:
            self.add(string)

      

class StyleWdg(HtmlElement):
    '''Basic Style element'''
    def __init__(self,string=None, css=None, id=None):
        super(StyleWdg,self).__init__("style", css=css, id=id)
        if string:
            self.add(string)






class Table(HtmlElement):

    def __init__(self, name=None, css=None):
        super(Table,self).__init__("table")
        self.add_style("border-collapse","collapse")
        self.name = name
        if css:
            self.set_class(css)    
        self.rows = []
        self.tbodies = []
        self.current_tbody = None
        self.current_row = None
        self.current_cell = None
        self.hidden_row_wdgs = []
       
        # keep track of the number of columns
        self.num_cols = 0
        self.max_cols = 0

        self.is_dynamic_flag = False
        self.dynamic_row = None

    def is_dynamic(self, flag):
        '''determines whether to make the table dynamic'''
        self.is_dynamic_flag = flag
    
        if self.is_dynamic_flag:
            self.dynamic_row = self.add_row()


    def get_current_row(self):
        return self.current_row

    def get_current_cell(self):
        return self.current_cell

    def add_col(self, css=None):
        col = HtmlElement.col()
        if css:
            col.set_class(css)
        self.add(col)
        return col

    def add_tbody(self):
        tbody = HtmlElement.tbody()
        #tbody.add_style('display','table-row-group')
        # each tbody can have a list of rows
        tbody.rows = []
        self.current_tbody = tbody
        self.tbodies.append(tbody)
        self.add(tbody)
        return self.current_tbody

    def close_tbody(self):
        self.current_tbody = None


    def get_current_tbody(self):
        return self.current_tbody


    def add_row(self, css=None, tr=None):

        # add hidden rows if hidden_row_wdgs is not empty 
        self.handle_hidden_rows()
        
        self.num_cols = 0
        if not tr:
            tr = HtmlElement.tr()

        if css:
            tr.set_class(css)
        
        
        if self.current_tbody:
            self.current_tbody.rows.append(tr)
            self.current_tbody.add(tr)
            
        else: 
            # some tr's may not be contained in a tbody even though 
            # the browser may draw it implicitly
            self.add(tr)
            #self.current_tbody = self.add_tbody() 

        self.rows.append(tr)
        self.current_row = tr
        return tr



    def handle_hidden_rows(self):
        '''handle hidden rows clear self.hidden_row_wdgs'''
        wdgs = self.hidden_row_wdgs
        self.hidden_row_wdgs = []
    
        Table.add_hidden_row(self, wdgs)

    def add_hidden_row(self, hidden_row_wdgs):
        elements = []
        for wdg in hidden_row_wdgs:
            tr,td = self.add_row_cell(wdg.get_hidden_row_wdg()) 
            tr.set_id("hidden_row_%s" % wdg.get_toggle_id())
            tr.add_styles("display: none;")

            elements.append([tr, td])
        return elements
    

    def add_header(self,data=None, css=None, row=None):
        self.num_cols += 1
        if self.num_cols > self.max_cols: self.max_cols = self.num_cols

        th = HtmlElement.th(data)
        if css:
            th.set_class(css)

        if row:
            current_row = row
        else:
            current_row = self.current_row

        if self.is_dynamic_flag and len(current_row.widgets) == 0:
            th_sep = HtmlElement.th('&nbsp;')
            current_row.add(th_sep)
            if css:
                th_sep.set_class(css)


        self.current_cell = th
        current_row.add(th)

        if self.is_dynamic_flag:
            th_sep = HtmlElement.th('&nbsp;')
            current_row.add(th_sep)
            if css:
                th_sep.set_class(css)

        return th


    def add_blank_header(self):
        return self.add_header('&nbsp;')

    def add_cell(self,data=None, css=None, add_hidden_wdg=False, row=None):
        self.num_cols += 1
        if self.num_cols > self.max_cols: self.max_cols = self.num_cols

        td = HtmlElement.td(data)
        if css:
            td.set_class(css)
        self.current_cell = td

        # make sure there is a row
        if self.current_row == None:
            self.add_row()


        if not row:
            row = self.current_row


        if self.is_dynamic_flag and self.num_cols == 1:
            # add a separator
            td_sep = HtmlElement.td("&nbsp;")
            row.add(td_sep)
            if css:
                td_sep.set_class(css)
       
        row.add(td)

        if add_hidden_wdg:
            self.add_hidden_row_wdg(data)


        if self.is_dynamic_flag:
            # add a separator
            td_sep = HtmlElement.td("&nbsp;")
            row.add(td_sep)
            if css:
                td_sep.set_class(css)
       
        return td
    
    def add_click_cell(self, input, event_name=None, data=None, css=None, add_hidden_wdg=False):
        ''' add a clickable cell which will toggle the checked state
        of the input '''
        td = self.add_cell(data, css, add_hidden_wdg)
        function = "a=get_element('%s');a.toggle_me()" % input.get_id()
        td.add_event('onClick', function)
        # attach the event if found
        if event_name:
            event = Event(event_name)
            input_func = event.get_caller()
            td.add_event('onClick', input_func)
            
        td.add_class('hand')
        return td

    def add_blank_cell(self):
        return self.add_cell('&nbsp;')


    def add_row_cell(self,data=None, css=None):
        '''adds a single cell that occupies an entire row'''
        tr = self.add_row(css)
        td = self.add_cell(data)

        if self.is_dynamic_flag:
            td.set_attr("colspan",self.max_cols*2)
        else:
            #td.set_attr("colspan",self.max_cols)
            td.set_attr("colspan","100%")
            #td.set_attr("colspan","50000")
            td.set_attr("colspan", self.max_cols)
        return (tr,td)


    def add_row_header(self,data=None):
        '''adds a single cell that occupies an entire row'''
        tr = self.add_row()
        th = self.add_header(data)
        if self.is_dynamic_flag:
            th.set_attr("colspan",self.max_cols*2)
        else:
            th.set_attr("colspan",self.max_cols)
        return (tr,th)


    def add_data(self,data):
        self.current_cell.add(data)

    def add_hidden_row_wdg(self, hidden_wdg):
        self.hidden_row_wdgs.append(hidden_wdg)

    def _get_col_index(self):
        return self.num_cols
    
    def get_next_col_name(self):
        '''get a default column name based on table name and col index'''
        table_name = self.name
        if table_name == None:
            table_name = self.generate_unique_id('table')
        return "%s_col%d" % (table_name, self._get_col_index())     
   
    def set_max_width(self, use_css=False):
        if use_css:
            if WebContainer.get_web().is_IE():
                self.add_style("width", "95%")
            else:
                self.add_style("width", "100%")
        else:
            # dynamic resizing doesn't work with css setting with %.
            self.set_attr("width", "100%")


    def add_dynamic_header(self,data=None, css=None, row=None):
        if row:
            current_row = row
        else:
            current_row = self.current_row

        # the first column
        if self.is_dynamic_flag and len(current_row.widgets) == 0:
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
        if self.is_dynamic_flag:
            div = DivWdg()
            img = HtmlElement.img("/context/icons/common/table/square_grey.png")
            div.add(img)

            th_sep = HtmlElement.th(div)
            current_row.add(th_sep)
            if css:
                th_sep.set_class(css)

        return th


            
   
    def get_display(self):
        if self.is_dynamic_flag and self.get_id():
            for i in range(0, self.max_cols):
                self.add_dynamic_header(row=self.dynamic_row)
            self.add("<script>new DynamicTable('%s')</script>" % self.get_id() )

        self.handle_hidden_rows()
        for row in self.rows:
            if len(row.widgets) == 1 and len(row.widgets ) < self.max_cols:
                row.widgets[0].set_attr("colspan", self.max_cols)
        return super(Table,self).get_display()

class Tbody(Table):
    ''' a collection of tr's without the parent <tbody>'''
    def __init__(self, name=None, css=None):
        HtmlElement.__init__(self, name)
        self.rows = []
        self.current_row = None
        self.current_cell = None
        self.hidden_row_wdgs = []
       
        # keep track of the number of columns
        self.num_cols = 0
        self.max_cols = 0
        self.is_dynamic_flag = False

    def add_row(self, css=None):

        # add hidden rows if hidden_row_wdgs is not empty 
        self.handle_hidden_rows()
        
        self.num_cols = 0
        tr = HtmlElement.tr()
        if css:
            tr.set_class(css)
        self.rows.append(tr)
        self.current_row = tr
        self.add(tr)
        return tr

    
            
    def get_display(self):
        self.handle_hidden_rows()
        
        for row in self.rows:
            if len(row.widgets) == 1 and len(row.widgets ) < self.max_cols:
                row.widgets[0].set_attr("colspan", self.max_cols)
        return Widget.get_display(self)




#
# HTML 5 support
#

class Canvas(HtmlElement):
    '''Basic Canvas element'''
    def __init__(self, css=None, id=None ):
        super(Canvas,self).__init__("canvas", css=css, id=id)



class Video(HtmlElement):
    '''Basic Video element'''
    def __init__(self, css=None, id=None ):
        super(Video,self).__init__("video", css=css, id=id)




# use psyco if present
try:
    import psyco
    psyco.bind(HtmlElement.get_display)
except ImportError:
    pass



