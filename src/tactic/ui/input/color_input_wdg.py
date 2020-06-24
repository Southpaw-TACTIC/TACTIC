###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

# Color wheel input


__all__ = ['ColorWdg', 'ColorInputWdg', 'ColorContainerWdg', 'ColorSelectorWdg']

from pyasm.common import Date, Common
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer, Widget, HtmlElement
from pyasm.widget import IconWdg, IconButtonWdg, BaseInputWdg, TextWdg
from tactic.ui.common import BaseRefreshWdg

from .text_input_wdg import TextInputWdg


class ColorWdg(Widget):
    # DEPRECATED: because the browsers have a sufficiently good one built-in
    '''This is drawn once in the page to reuse by repositioning it'''
    def get_display(self):

        top = DivWdg()

        inner = DivWdg()
        top.add(inner)

        inner.add_style('position: absolute')
        inner.add_style('top: 100')
        inner.add_style('left: 100')
        inner.add_style("z-index: 1000")
        number = Common.randint(1, 1000)
        rainbow_id = "rainbow_%s" % number
        inner.set_id(rainbow_id);

        #top.add('''
        #<img id="%s" src="/context/spt_js/mooRainbow/rainbow.png" alt="[r]" width="16" height="16" />
        #''' % rainbow_id)


        inner.add_behavior( { 
            "type": "load",
            'rainbow_id': rainbow_id,
            "cbjs_action": '''

            spt.color = {};
            spt.color.top = bvr.src_el;

            spt.color.init = function() {
                var js_file = "mooRainbow/Source/mooRainbow.js";
                var url = "/context/spt_js/" + js_file;
                var js_el = document.createElement("script");
                js_el.setAttribute("type", "text/javascript");
                js_el.setAttribute("src", url);
                var head = document.getElementsByTagName("head")[0];
                head.appendChild(js_el);

                setTimeout( function() {

                spt.color.rainbow = new MooRainbow(bvr.rainbow_id, {
                    id: bvr.rainbow_id,
                    startColor: [58, 142, 246],
                    imgPath:    '/context/spt_js/mooRainbow/Assets/images/',
                    onComplete: function(color) {
                        if (spt.color.rainbow){
                            var cbk = spt.color.rainbow.cbk;
                            cbk(color);
                        }
                    }
                });
                //make it rise above the Edit popup
                spt.color.rainbow.layout.setStyle('z-index','10000');
                spt.color.rainbow.spt_id = bvr.rainbow_id;

                }, 300 );

            }

            spt.color.get = function() {
                if (! spt.color.rainbow ) {
                    spt.color.init();
                }

                return spt.color.rainbow;
            }

            '''
        } )


        return inner


#
# Use this for input
#

class ColorInputWdg(BaseInputWdg):

    ARGS_KEYS = {
    }


    def __init__(self, name=None, **kwargs):
        if not name:
            name = kwargs.get("name")
        self.top = DivWdg()
        self.input = None
        self.kwargs = kwargs
        super(ColorInputWdg, self).__init__(name)

        if not self.input:
            self.input = TextInputWdg(name=self.get_input_name(), type="color", width="60")


    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def set_input(self, input):
        self.input = input
        self.input.set_name(self.get_input_name() )

    def get_input(self):
        return self.input


    def add(self, widget):
        self.top.add(widget)


    def add_behavior(self, behavior):
        return self.input.add_behavior(behavior)



    def get_display(self):
        top = self.top
        top.add_style("display: flex")
        top.add_style("align-items: center")
        top.add_class("spt_color_top")


        value = self.get_value()

        top.add(self.input)

        text = TextInputWdg(name=self.get_input_name())
        top.add(text)
        text.add_class("spt_color_text")
        text.add_style("margin-left: 15px")
        text.add_style("width: 100%")

        self.input.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_color_top");
            var el = top.getElement(".spt_color_text");
            el.value = bvr.src_el.value;
            '''
        } )


        text.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_color_top");
            var el = top.getElement(".spt_color_input");
            el.value = bvr.src_el.value;
            '''
        } )

        text.add_behavior( {
            'type': 'clickX',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_color_top");
            var el = top.getElement(".spt_color_input");
            el.click();
            '''
        } )





        if value:
            self.input.set_value(value)
            text.set_value(value)


        start_color = self.kwargs.get("start_color")

        if not value:
            if start_color and start_color.find(","):
                colors = start_color.split(",")

            elif not start_color or start_color == "random":
                #'rgba(188, 207, 215, 1.0)',
                colors = [
                    '#bccfd7',
                    '#bcd7cf',
                    '#d7bccf',
                    '#d7cfbc',
                    '#cfbcd7',
                    '#cfd7bc',
                ]

            num = Common.randint(0,len(colors)-1)
            start_color = colors[num]
            #start_color = top.get_color(start_color, -10)


        if start_color:
            self.input.set_value(start_color)
            text.set_value(start_color)

        self.input.add_class("spt_color_input")
     
        if not start_color:
            start_color = [0, 0, 255]
        elif start_color.startswith("#"):
            start_color = start_color.replace("#", "")
            r, g, b = start_color[:2], start_color[2:4], start_color[4:]
            r, g, b = [int(n, 16) for n in (r, g, b)]

            start_color = [r, g, b]

        return top



class ColorContainerWdg(BaseInputWdg):

    def __init__(self, **kwargs):
        super(ColorContainerWdg,self).__init__(**kwargs)

        from pyasm.widget import ColorWdg
        self.color_wdg = ColorWdg(**kwargs)

        self.color_wdg.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            bvr.src_el.lightOrDark = function(color) {
                // Variables for red, green, blue values
                var r, g, b, hsp;
                
                // Check the format of the color, HEX or RGB?
                if (color.match(/^rgb/)) {

                    // If HEX --> store the red, green, blue values in separate variables
                    color = color.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+(?:\.\d+)?))?\)$/);
                    
                    r = color[1];
                    g = color[2];
                    b = color[3];
                } 
                else {
                    
                    // If RGB --> Convert it to HEX: http://gist.github.com/983661
                    color = +("0x" + color.slice(1).replace( 
                    color.length < 5 && /./g, '$&$&'));

                    r = color >> 16;
                    g = color >> 8 & 255;
                    b = color & 255;
                }
                
                // HSP (Highly Sensitive Poo) equation from http://alienryderflex.com/hsp.html
                hsp = Math.sqrt(
                0.299 * (r * r) +
                0.587 * (g * g) +
                0.114 * (b * b)
                );

                // Using the HSP value, determine whether the color is light or dark
                if (hsp>127.5) {

                    return 'light';
                } 
                else {

                    return 'dark';
                }
            }

            bvr.src_el.oldValue = bvr.src_el.value;
            var top = bvr.src_el.getParent(".spt_color_container");
            var label = top.getElement(".spt_color_label");
            
            // init
            var isLight = bvr.src_el.lightOrDark(bvr.src_el.value) == 'light';
            var textColor = isLight ? '#000000' : '#ffffff';

            label.innerText = bvr.src_el.value;
            label.setStyle("color", textColor);


            // update
            var update = function() {
                var oldHex = bvr.src_el.oldValue;
                var hex = bvr.src_el.value;

                if (hex == oldHex) return;

                bvr.src_el.oldValue = hex;
                //var complimentary = hexToComplimentary(hex);
                var isLight = bvr.src_el.lightOrDark(hex) == 'light';
                var textColor = isLight ? '#000000' : '#ffffff';

                label.innerText = hex;
                label.setStyle("color", textColor);
            }

            setInterval(update, 200);

            '''
        })


    def get_color_wdg(self):
        return self.color_wdg


    def get_styles(self):

        styles = HtmlElement.style('''

            .spt_color_container {
                height: 40px;
                width: 84;
                position: relative;
            }

            .spt_color_value {
                height: 100%;
                width: 100%;
                cursor: pointer;
            }

            .spt_color_label {
                position: absolute;
                top: 12px;
                left: 12px;
                font-size: 14px;
                color: white;
                pointer-events: none;
            }

            ''')

        return styles


    def get_display(self):

        top = DivWdg()
        top.add_class("spt_color_container")

        top.add(self.color_wdg)
        self.color_wdg.add_class("spt_color_value")

        #color = self.color_wdg.get_value() or "#000000"
        color_label = DivWdg("#000000")
        top.add(color_label)
        color_label.add_class("spt_color_label")

        top.add(self.get_styles())

        return top


class ColorSelectorWdg(ColorContainerWdg):

    

    def get_display(self):


        top = DivWdg()
        top.add_class("spt_color_container")

        top.add(self.color_wdg)
        self.color_wdg.add_class("spt_color_value")
        self.color_wdg.add_behavior({
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.setAttribute("name", "edit|color");
        '''
        })

        color_label = DivWdg("#000000")
        top.add(color_label)
        color_label.add_class("spt_color_label")

        top.add(self.get_styles())

        return top

